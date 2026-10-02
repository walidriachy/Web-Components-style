#!/usr/bin/env python3
"""Component contract validation, shared by build-lib.py and the batch checker.

A component is {id, name, cat, tags, note, html, css, js} plus an optional
span ("full" for dashboards, app shells and page sections that need a whole
row). `id` is also the CSS class prefix; `js` is a function body taking `root`.
Everything below exists so a component can be pasted into any project without
leaking styles, reaching the network, or depending on anything outside its own
three strings.

Usage:
    python3 libcheck.py batch.json                     check a batch
    python3 libcheck.py batch.json --install DEST      check, and write DEST only if clean
"""
import io, json, os, re, subprocess, sys, tempfile, glob

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "components-src")
KEYS = ("id", "name", "cat", "tags", "note", "span", "html", "css", "js")
SPANS = ("full",)

# ---------------------------------------------------------------------------
# CSS scanning
# ---------------------------------------------------------------------------

# At-rules whose block contains ordinary style rules: scoping passes straight through.
AT_TRANSPARENT = {"media", "supports", "layer", "container", "starting-style", "document"}
# At-rules whose block holds descriptors or frames, never selectors.
AT_OPAQUE = {"keyframes", "-webkit-keyframes", "property", "font-face", "counter-style",
             "page", "font-feature-values", "font-palette-values", "view-transition"}


def _skip_string(css, i):
    q = css[i]; i += 1
    while i < len(css):
        if css[i] == "\\": i += 2; continue
        if css[i] == q: return i + 1
        i += 1
    return i


def _match_brace(css, i):
    """css[i] == '{'. Return the index just past its matching '}'."""
    depth = 0
    while i < len(css):
        ch = css[i]
        if ch in "\"'": i = _skip_string(css, i); continue
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    return i


def _split_selectors(prelude):
    """Split a selector list on top-level commas (not inside :is(), :where(), [...])."""
    parts, depth, cur = [], 0, []
    for ch in prelude:
        if ch in "([": depth += 1
        elif ch in ")]": depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def scan_css(css, cid):
    """Walk the stylesheet with a brace stack, the way a browser parses it.

    Returns {problems, keyframes, properties}. A style rule is scoped when every
    selector in its list mentions .<cid>, or when it is nested inside a rule that
    already is (native CSS nesting). The previous checker matched selectors with a
    line-anchored regex, which never saw a rule that did not start a line — every
    rule after the first in minified CSS went unchecked, and nested rules were
    misread as top-level ones."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = {"problems": [], "keyframes": [], "properties": []}
    stack, i, start, n = [], 0, 0, len(css)
    needle = "." + cid
    while i < n:
        ch = css[i]
        if ch in "\"'":
            i = _skip_string(css, i); continue
        if ch == "{":
            prelude = css[start:i].strip()
            parent_scoped = stack[-1] if stack else False
            if prelude.startswith("@"):
                m = re.match(r"@([\w-]+)", prelude)
                name = m.group(1).lower() if m else ""
                if name in AT_OPAQUE:
                    if "keyframes" in name:
                        km = re.match(r"@[\w-]+\s+([\w-]+)", prelude)
                        if km: out["keyframes"].append(km.group(1))
                    elif name == "property":
                        pm = re.match(r"@property\s+(--[\w-]+)", prelude)
                        if pm: out["properties"].append(pm.group(1))
                    i = _match_brace(css, i); start = i; continue
                if name == "scope":
                    stack.append(parent_scoped or needle in prelude)
                else:
                    stack.append(parent_scoped)
            else:
                if parent_scoped:
                    stack.append(True)
                else:
                    bad = [p for p in _split_selectors(prelude) if needle not in p]
                    if bad and prelude:
                        out["problems"].append("unscoped selector: " + bad[0][:48])
                    # keep scanning children as scoped so one bad rule is reported once
                    stack.append(True)
            start = i + 1
        elif ch == "}":
            if stack: stack.pop()
            start = i + 1
        elif ch == ";":
            start = i + 1
        i += 1
    if stack:
        out["problems"].append("unbalanced css braces")
    return out


def strip_at_blocks(css):
    """Kept for callers that only need @keyframes names."""
    return css, scan_css(css, "\x00")["keyframes"]

# ---------------------------------------------------------------------------
# Markup and capability rules
# ---------------------------------------------------------------------------

UNESC = [("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"), ("&amp;", "&")]
def unescape_markup(h):
    """Agents sometimes entity-escape their markup. If it has no real tags but has
       escaped ones, decode it — otherwise it renders as literal text.

       Markup that already contains real tags is left alone: any &lt; in it is
       deliberate (a code sample, a "< OK >" button label), and decoding it would
       turn displayed code into live elements. The previous version only returned
       early when there was no &lt; at all, so it decoded exactly those."""
    if "<" in h or "&lt;" not in h:
        return h
    for a, b in UNESC:
        h = h.replace(a, b)
    return h

# Components legitimately show API keys, tokens and secrets as UI — a masked key row,
# a connected-integration list. Invented sample values sometimes land on a real
# provider's format, which makes every secret scanner treat the library as a leak and
# blocks anyone who copies the component. These are rewritten to values that still read
# as credentials but cannot match a provider pattern.
SECRET_PATS = [
    (re.compile(r'\b(sk|pk|rk)_(live|test)_[A-Za-z0-9]{10,}'),
     lambda m: m.group(1) + "_demo_EXAMPLEkey00NOTAREAL"),
    (re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}'), lambda m: "ghdemo_EXAMPLEtoken00NOTAREAL"),
    (re.compile(r'\bAKIA[0-9A-Z]{16}\b'),         lambda m: "AKIA_EXAMPLE_NOT_REAL"),
    (re.compile(r'\bsk-[A-Za-z0-9]{20,}'),         lambda m: "sk-demo_EXAMPLE_NOT_A_REAL_KEY"),
    (re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}'), lambda m: "xoxdemo-EXAMPLE00NOTAREAL"),
    (re.compile(r'\bAIza[0-9A-Za-z_\-]{35}'),      lambda m: "AIzaDEMOexampleKEY00NOTAREAL"),
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY'),  lambda m: "-----BEGIN EXAMPLE NOT A KEY"),
]

# A replacement must never itself look like a credential, or sanitised components would
# still trip every scanner (and this file would too). Checked whenever the module loads.
for _pat, _repl in SECRET_PATS:
    for _p2, _ in SECRET_PATS:
        _v = _repl(type("M", (), {"group": lambda self, i=0: "sk"})())
        assert not _p2.search(_v), "replacement %r matches a credential pattern" % _v

def sanitize(c):
    """Rewrite provider-shaped credential placeholders. Returns what was changed."""
    changed = []
    for f in ("html", "css", "js"):
        v = c.get(f) or ""
        for pat, repl in SECRET_PATS:
            hits = pat.findall(v)
            if hits:
                v = pat.sub(repl, v)
                changed.append("%s: %d credential-shaped string(s)" % (f, len(hits)))
        c[f] = v
    return changed

# These are presentational components. Nothing here needs network access,
# storage, dynamic evaluation or navigation — so any of it is disqualifying.
BANNED = [
    ("fetch(",            "network call"),
    ("XMLHttpRequest",    "network call"),
    ("sendBeacon",        "network call"),
    ("WebSocket",         "network call"),
    ("EventSource",       "network call"),
    ("eval(",             "dynamic evaluation"),
    ("new Function",      "dynamic evaluation"),
    ("document.cookie",   "cookie access"),
    ("localStorage",      "storage access"),
    ("sessionStorage",    "storage access"),
    ("indexedDB",         "storage access"),
    ("location.href",     "navigation"),
    ("location.replace",  "navigation"),
    ("location.assign",   "navigation"),
    ("window.open",       "navigation"),
    ("postMessage",       "cross-frame messaging"),
    ("import(",           "dynamic import"),
    # tags are matched by regex below, not substring — "i<script.length"
    # is ordinary code, not a nested script tag
    ("srcdoc",            "embedded frame"),
    ("javascript:",       "javascript: url"),
    ("onerror=",          "inline handler"),
]
TAG_PATS = ((r'<\s*script[\s>/]', "nested script tag"),
            (r'<\s*iframe[\s>/]', "embedded frame"),
            (r'<\s*object[\s>/]', "embedded object"),
            (r'<\s*embed[\s>/]',  "embedded object"))


def validate(c):
    """Return a list of contract problems. Empty list == component is shippable."""
    p = []
    cid = c.get("id", "")
    if not re.fullmatch(r'[a-z][a-z0-9-]{2,58}', cid): return ["bad id"]
    for k in ("name", "cat", "html", "css"):
        if not str(c.get(k, "")).strip(): p.append("empty " + k)
    if c.get("span") not in (None, "") and c.get("span") not in SPANS:
        p.append("span must be one of %s" % (SPANS,))
    html, css, js = c.get("html", ""), c.get("css", ""), c.get("js", "") or ""
    if ("class=\"" + cid) not in html and ("class='" + cid) not in html:
        p.append("root element missing class=" + cid)
    if css.count("{") != css.count("}"): p.append("unbalanced css braces")
    scan = scan_css(css, cid)
    c["_kf"], c["_props"] = scan["keyframes"], scan["properties"]
    p.extend(x for x in scan["problems"] if x not in p)
    for bad, why in ((r'(?m)^\s*\*\s*\{', "global * selector"),
                     (r':root\s*\{', ":root"),
                     (r'(?m)^\s*body\s*\{', "body selector"),
                     (r'(?m)^\s*html\s*\{', "html selector")):
        if re.search(bad, css): p.append(why)
    if re.search(r'@import|url\(\s*[\'"]?https?:', css): p.append("external resource")
    if "document.querySelector" in js and "root" not in js.split("document.querySelector")[0][-40:]:
        p.append("uses document.querySelector instead of root")
    blob = js + " " + html
    for token, why in BANNED:
        if token in blob:
            p.append("disallowed capability (%s)" % why); break
    for pat, why in TAG_PATS:
        if re.search(pat, blob, re.I):
            p.append("disallowed capability (%s)" % why); break
    return p


VIEWPORT_UNIT = re.compile(r'(?<![\w-])-?(?:\d+\.?\d*|\.\d+)(?:d|s|l)?(?:vh|vw|vmin|vmax|vi|vb)\b')

def strict_problems(c):
    """Rules for newly written components. The shipped library predates them."""
    cid = c.get("id", "")
    css, js, html = c.get("css", "") or "", c.get("js", "") or "", c.get("html", "") or ""
    p = []
    for name in c.get("_kf") or scan_css(css, cid)["keyframes"]:
        if not name.startswith(cid):
            p.append("@keyframes '%s' must start with the component id '%s' "
                     "(all components share one stylesheet)" % (name, cid))
    for name in c.get("_props") or scan_css(css, cid)["properties"]:
        if not name.startswith("--" + cid):
            p.append("@property '%s' must start with '--%s' — registered properties are "
                     "global, like @keyframes" % (name, cid))
    # The harness unmounts by clearing innerHTML, which cannot reach into a running
    # loop. A loop that does not check whether it is still in the document keeps
    # burning frames on detached nodes for the rest of the session.
    if ("requestAnimationFrame" in js or "setInterval" in js) and "isConnected" not in js:
        p.append("animation loop never stops: add `if (!root.isConnected) return;` at the "
                 "top of the rAF/interval callback so the component self-terminates")
    # Browsers keep roughly 16 live WebGL contexts and then silently kill the oldest.
    # A library page mounts dozens of components while scrolling.
    if re.search(r"getContext\(\s*['\"](?:webgl2?|experimental-webgl)", js) and "loseContext" not in js:
        p.append("WebGL context is never released: when !root.isConnected, call "
                 "gl.getExtension('WEBGL_lose_context').loseContext()")
    if re.search(r"\b(?:document|window)\.addEventListener\s*\(", js) and "removeEventListener" not in js:
        p.append("listener on document/window is never removed: remove it once "
                 "!root.isConnected, or listen on root instead")
    if re.search(r'position\s*:\s*fixed', css):
        p.append("position:fixed escapes the component and covers the host page — use "
                 "position:absolute inside the root")
    if re.search(r"\.showModal\s*\(|\.showPopover\s*\(|\bpopover\s*=|\spopover[\s>]|@view-transition", js + html + css):
        p.append("top-layer API (dialog.showModal / popover / @view-transition) escapes the "
                 "component — keep overlays inside the root with position:absolute")
    m = VIEWPORT_UNIT.search(css)
    if m:
        p.append("viewport unit '%s' sizes against the browser window, not the component — "
                 "set container-type on the root and use cqi/cqb units" % m.group(0))
    if c.get("span") == "full" and "container-type" not in css:
        p.append("full-span components must set container-type on the root and respond "
                 "with @container rules, so they collapse in narrow layouts")
    for m in re.finditer(r'view-transition-name\s*:\s*([\w-]+)', css):
        v = m.group(1)
        if v not in ("none", "auto", "match-element") and not v.startswith(cid):
            p.append("view-transition-name '%s' must start with '%s' — names are "
                     "document-global" % (v, cid))
    for m in re.finditer(r"viewTransitionName\s*=\s*['\"]([\w-]+)['\"]", js):
        if m.group(1) not in ("none", "auto") and not m.group(1).startswith(cid):
            p.append("viewTransitionName '%s' must start with '%s'" % (m.group(1), cid))
    for f in ("html", "css", "js"):
        for pat, _ in SECRET_PATS:
            hit = pat.search(c.get(f) or "")
            if hit:
                p.append("%s contains a string shaped like a real credential (%s…) — secret "
                         "scanners block the repo; use an obviously fake value" % (f, hit.group(0)[:14]))
                break
    return p


def js_ok(js):
    """Syntax-check the js as a function body taking `root`."""
    if not js.strip(): return True
    fd, f = tempfile.mkstemp(suffix=".js")
    try:
        with io.open(fd, "w", encoding="utf-8") as fh:
            fh.write("(function(root){\n" + js + "\n});")
        return subprocess.run(["node", "--check", f], capture_output=True).returncode == 0
    finally:
        os.remove(f)


def check(components, strict=False):
    """Validate a list. Returns (clean, problems) where problems is {id: [reasons]}."""
    problems, ids = {}, {}
    for c in components:
        cid = c.get("id", "<missing id>")
        c["html"] = unescape_markup(c.get("html", "") or "")
        pr = validate(c)
        if strict and pr != ["bad id"]:
            pr.extend(strict_problems(c))
        if not js_ok(c.get("js", "") or ""): pr.append("js syntax error")
        if cid in ids: pr.append("duplicate id within this batch")
        ids[cid] = 1
        if pr: problems[cid] = pr
    return [c for c in components if c.get("id") not in problems], problems


def load_library(exclude=()):
    """Every shipped component, from components-src (falling back to components.js).
    exclude: absolute paths of components-src files to leave out."""
    rows = []
    files = sorted(glob.glob(os.path.join(SRC, "*.json")))
    if files:
        for f in files:
            if os.path.abspath(f) in exclude: continue
            try:
                d = json.load(io.open(f, encoding="utf-8"))
            except Exception:
                continue
            rows.extend(d if isinstance(d, list) else d.get("components", []))
        return rows
    libf = os.path.join(BASE, "components.js")
    if os.path.exists(libf):
        s = io.open(libf, encoding="utf-8").read()
        try: return json.loads(s[s.index("["):s.rindex("]") + 1])
        except Exception: return []
    return []


def _dash_prefix(a, b):
    return b.startswith(a + "-")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    install = None
    if "--install" in args:
        k = args.index("--install")
        install = args[k + 1] if k + 1 < len(args) else None
        args = args[:k] + args[k + 2:]
        if not install:
            print("--install needs a destination path"); sys.exit(2)
    data = json.load(io.open(args[0], encoding="utf-8"))
    if isinstance(data, dict): data = data.get("components", [])
    clean, problems = check(data, strict=True)

    # Cross-check against everything already shipped. A duplicate id, a reused
    # @keyframes/@property name, or an id that is a dash-prefix of another (so
    # one component's class names can land on the other's elements) all leak.
    # Skip the batch's own file and the install target: re-checking a file that already
    # lives in components-src must not report it colliding with itself.
    skip = {os.path.abspath(args[0])}
    if install: skip.add(os.path.abspath(install))
    existing = load_library(exclude=skip)
    taken_ids = set(x["id"] for x in existing)
    taken_kf, taken_props = set(), set()
    for x in existing:
        sc = scan_css(x.get("css", ""), x["id"])
        taken_kf |= set(sc["keyframes"]); taken_props |= set(sc["properties"])
    all_ids = taken_ids | set(c.get("id", "") for c in data)
    for c in data:
        cid, hits = c.get("id", "?"), []
        if cid in taken_ids: hits.append("id already exists in the library")
        sc = scan_css(c.get("css", ""), cid)
        hits += ["@keyframes '%s' already exists in the library" % n for n in sc["keyframes"] if n in taken_kf]
        hits += ["@property '%s' already exists in the library" % n for n in sc["properties"] if n in taken_props]
        for other in all_ids:
            if other != cid and (_dash_prefix(cid, other) or _dash_prefix(other, cid)):
                hits.append("id '%s' and '%s' are dash-prefixes of each other, so their class "
                            "names can collide — rename one" % (cid, other)); break
        if hits: problems.setdefault(cid, []).extend(hits)

    # summary after the cross-checks so it never says "clean" above a list of failures
    print("checked %d | clean %d | problems %d" % (len(data), len(data) - len(problems), len(problems)))
    for cid, pr in problems.items():
        print("\nFAIL %s" % cid)
        for x in pr: print("   - " + x)
    if problems:
        print("\nNOT SHIPPABLE - fix the above and re-run" +
              (" (nothing was installed)" if install else ""))
        sys.exit(1)
    print("\nOK - every component satisfies the contract")
    if install:
        # js is kept even when empty (CSS-only components); span only when set
        rows = [{k: c[k] for k in KEYS if k in c and (k == "js" or c[k] not in (None, ""))}
                for c in data]
        os.makedirs(os.path.dirname(os.path.abspath(install)), exist_ok=True)
        with io.open(install, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1); f.write("\n")
        print("INSTALLED %d components -> %s" % (len(rows), install))
    sys.exit(0)
