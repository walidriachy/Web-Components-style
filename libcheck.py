#!/usr/bin/env python3
"""Component contract validation, shared by build-lib.py and check-batch.py.

A component is {id, name, cat, tags, note, html, css, js}. `id` is also the CSS
class prefix; `js` is a function body taking `root`. Everything below exists so
a component can be pasted into any project without leaking styles, reaching the
network, or depending on anything outside its own three strings.
"""
import io, json, os, re, subprocess, sys, tempfile

def strip_at_blocks(css):
    """Remove @keyframes bodies; unwrap @media/@supports so inner selectors are checked."""
    out, i, kf_names = [], 0, []
    while i < len(css):
        m = re.compile(r'@(keyframes|media|supports|layer)[^{]*\{', re.I).search(css, i)
        if not m:
            out.append(css[i:]); break
        out.append(css[i:m.start()])
        head = css[m.start():m.end()]
        depth, j = 1, m.end()
        while j < len(css) and depth:
            if css[j] == '{': depth += 1
            elif css[j] == '}': depth -= 1
            j += 1
        body = css[m.end():j-1]
        if m.group(1).lower() == "keyframes":
            nm = re.search(r'@keyframes\s+([\w-]+)', head, re.I)
            if nm: kf_names.append(nm.group(1))
        else:
            out.append(body)
        i = j
    return "".join(out), kf_names

UNESC = [("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"), ("&amp;", "&")]
def unescape_markup(h):
    """Agents sometimes entity-escape their markup. If it has no real tags but has
       escaped ones, decode it — otherwise it renders as literal text."""
    if "<" in h and "&lt;" not in h:
        return h
    if "&lt;" not in h:
        return h
    for a, b in UNESC:
        h = h.replace(a, b)
    return h

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

# Components legitimately show API keys, tokens and secrets as UI — a masked key row,
# a connected-integration list. Invented sample values sometimes land on a real
# provider's format, which makes every secret scanner treat the library as a leak and
# blocks anyone who copies the component. These are rewritten to values that still read
# as credentials but cannot match a provider pattern.
SECRET_PATS = [
    (re.compile(r'\b(sk|pk|rk)_(live|test)_[A-Za-z0-9]{10,}'),
     lambda m: m.group(1) + "_demo_EXAMPLEkey00NOTAREAL"),
    (re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}'), lambda m: "ghdemo_EXAMPLEtoken00NOTAREAL"),
    (re.compile(r'\bAKIA[0-9A-Z]{16}\b'),         lambda m: "AKIAEXAMPLE000NOTREAL"),
    (re.compile(r'\bsk-[A-Za-z0-9]{20,}'),         lambda m: "sk-demoEXAMPLEkey00NOTAREAL"),
    (re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}'), lambda m: "xoxdemo-EXAMPLE00NOTAREAL"),
    (re.compile(r'\bAIza[0-9A-Za-z_\-]{35}'),      lambda m: "AIzaDEMOexampleKEY00NOTAREAL"),
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY'),  lambda m: "-----BEGIN EXAMPLE NOT A KEY"),
]

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

def validate(c):
    """Return a list of contract problems. Empty list == component is shippable."""
    p = []
    cid = c.get("id", "")
    if not re.fullmatch(r'[a-z][a-z0-9-]{2,58}', cid): return ["bad id"]
    for k in ("name", "cat", "html", "css"):
        if not str(c.get(k, "")).strip(): p.append("empty " + k)
    html, css, js = c.get("html", ""), c.get("css", ""), c.get("js", "") or ""
    if ("class=\"" + cid) not in html and ("class='" + cid) not in html:
        p.append("root element missing class=" + cid)
    if css.count("{") != css.count("}"): p.append("unbalanced css braces")
    body, kf = strip_at_blocks(css)
    c["_kf"] = kf
    for sel in re.findall(r'(?m)^\s*([^@{}\n][^{}\n]*)\{', body):
        for part in sel.split(","):
            part = part.strip()
            if not part or part.startswith("%") or part in ("from", "to"): continue
            if ("." + cid) not in part:
                p.append("unscoped selector: " + part[:48]); break
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
    """Validate a list. Returns (clean, problems) where problems is {id: [reasons]}.

    strict adds two rules that only apply to newly written batches:
      * every @keyframes name must start with the component id
      * any animation loop must stop itself once the component is unmounted
    The shipped library predates both — it uses names that are unprefixed but
    provably non-colliding, and its loops are cleaned up inconsistently."""
    problems, ids = {}, {}
    for c in components:
        cid = c.get("id", "<missing id>")
        c["html"] = unescape_markup(c.get("html", "") or "")
        pr = validate(c)
        if strict:
            for name in strip_at_blocks(c.get("css", "") or "")[1]:
                if not name.startswith(cid):
                    pr.append("@keyframes '%s' must start with the component id "
                              "'%s' (all components share one stylesheet)" % (name, cid))
            js = c.get("js", "") or ""
            # The harness unmounts by clearing innerHTML, which cannot reach into a
            # running loop. A loop that does not check whether it is still in the
            # document keeps burning frames on detached nodes for the rest of the
            # session, and the library mounts hundreds of components while scrolling.
            if ("requestAnimationFrame" in js or "setInterval" in js) \
               and "isConnected" not in js:
                pr.append("animation loop never stops: add `if (!root.isConnected) return;` "
                          "at the top of the rAF/interval callback so the component "
                          "self-terminates when unmounted")
        if not js_ok(c.get("js", "") or ""): pr.append("js syntax error")
        if cid in ids: pr.append("duplicate id within this batch")
        ids[cid] = 1
        if pr: problems[cid] = pr
    return [c for c in components if c.get("id") not in problems], problems

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: libcheck.py <batch.json>"); sys.exit(2)
    data = json.load(io.open(sys.argv[1], encoding="utf-8"))
    if isinstance(data, dict): data = data.get("components", [])
    for c in data:
        for note in sanitize(c):
            print("sanitised %s — %s" % (c.get("id", "?"), note))
    clean, problems = check(data, strict=True)
    # A keyframes name colliding with one already in the library would silently
    # hijack that component's animation, so check against the shipped set too.
    libf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "components.js")
    if os.path.exists(libf):
        src = io.open(libf, encoding="utf-8").read()
        try:
            existing = json.loads(src[src.index("["):src.rindex("]") + 1])
        except Exception:
            existing = []
        taken_ids = set(x["id"] for x in existing)
        taken_kf = set()
        for x in existing:
            taken_kf |= set(strip_at_blocks(x.get("css", ""))[1])
        for c in data:
            hits = []
            if c.get("id") in taken_ids: hits.append("id already exists in the library")
            for n in strip_at_blocks(c.get("css", ""))[1]:
                if n in taken_kf: hits.append("@keyframes '%s' already exists in the library" % n)
            if hits: problems.setdefault(c.get("id", "?"), []).extend(hits)
    # summary is printed after the library cross-checks so it can never say
    # "clean" on a line above a list of failures
    print("checked %d | clean %d | problems %d" % (len(data), len(data) - len(problems), len(problems)))
    for cid, pr in problems.items():
        print("\nFAIL %s" % cid)
        for x in pr: print("   - " + x)
    print("\nOK - every component satisfies the contract" if not problems
          else "\nNOT SHIPPABLE - fix the above and re-run")
    sys.exit(1 if problems else 0)
