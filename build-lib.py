#!/usr/bin/env python3
"""Merge component workflow output -> components.js -> library.html, with hard validation."""
import io, json, os, re, subprocess, sys, glob

BASE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.expanduser("~/.claude/projects/-Users-walid-Created-Apps-in-claude-Page-Style/"
                        "4fb716f4-74bc-4069-9276-4332c2e894c8/subagents/workflows")

def collect():
    rows = []
    for j in glob.glob(os.path.join(WF, "*", "journal.jsonl")):
        for line in io.open(j, encoding="utf-8"):
            try: rec = json.loads(line)
            except Exception: continue
            res = rec.get("result")
            if isinstance(res, dict) and isinstance(res.get("components"), list):
                rows.extend(res["components"])
    return rows

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

def validate(c):
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
    # These are presentational components. Nothing here needs network access,
    # storage, dynamic evaluation or navigation — so any of it is disqualifying.
    # Two batches shipped without a completed safety review, so this is checked
    # mechanically for every component rather than trusted.
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
    blob = js + " " + html
    for token, why in BANNED:
        if token in blob:
            p.append("disallowed capability (%s)" % why)
            break
    for pat, why in ((r'<\s*script[\s>/]', "nested script tag"),
                     (r'<\s*iframe[\s>/]', "embedded frame"),
                     (r'<\s*object[\s>/]', "embedded object"),
                     (r'<\s*embed[\s>/]',  "embedded object")):
        if re.search(pat, blob, re.I):
            p.append("disallowed capability (%s)" % why)
            break
    return p

def js_ok(js):
    if not js.strip(): return True
    src = "(function(root){\n" + js + "\n});"
    f = os.path.join(BASE, "_jscheck.js")
    io.open(f, "w", encoding="utf-8").write(src)
    r = subprocess.run(["node", "--check", f], capture_output=True)
    os.remove(f)
    return r.returncode == 0

# Components proven broken at runtime in the browser. Syntax checking cannot
# catch these, so anything that fails to mount during verification is recorded
# here with its reason rather than shipped as a broken card.
BLOCK = {
    "t213-aggr-ratio": "TypeError at mount: 'f is not a function'",
}

raw = collect()
# hand-written components live alongside agent output and go through the same validation
for hm in sorted(glob.glob(os.path.join(BASE, "_handmade*.json"))):
    extra = json.load(io.open(hm, encoding="utf-8"))
    raw = extra + raw
    print("including %d hand-written from %s" % (len(extra), os.path.basename(hm)))
print("collected %d component records" % len(raw))
seen, good, rejected, renamed = set(), [], {}, [0]
for c in raw:
    cid = c.get("id", "")
    if cid in BLOCK:
        rejected["runtime failure"] = rejected.get("runtime failure", 0) + 1
        continue
    c["html"] = unescape_markup(c.get("html", "") or "")
    # A colliding id is a regenerated variant, not waste. The id IS the class
    # prefix, so renaming it consistently across html/css/js yields a clean,
    # independent component instead of a dropped one.
    if cid in seen:
        base, n = cid, 2
        while cid in seen and n < 9:
            cid = "%s-v%d" % (base, n); n += 1
        if cid in seen:
            rejected["duplicate id"] = rejected.get("duplicate id", 0) + 1; continue
        for f in ("html", "css", "js"):
            c[f] = (c.get(f, "") or "").replace(base, cid)
        c["id"] = cid
        c["name"] = c.get("name", "") + " II"
        renamed[0] += 1
    probs = validate(c)
    if not js_ok(c.get("js", "") or ""): probs.append("js syntax error")
    if probs:
        for p in probs[:1]: rejected[p.split(":")[0]] = rejected.get(p.split(":")[0], 0) + 1
        continue
    seen.add(cid)
    c["_id"] = cid
    good.append(c)

# @keyframes live in one shared stylesheet, so a duplicated name would silently
# hijack another component's animation. Reject only genuine collisions.
owner, clash = {}, set()
for c in good:
    for n in c.get("_kf", []):
        if n in owner and owner[n] != c["_id"]: clash.add(n)
        owner.setdefault(n, c["_id"])
if clash:
    before = len(good)
    good = [c for c in good if not (set(c.get("_kf", [])) & clash)]
    print("dropped %d for colliding @keyframes names: %s" % (before - len(good), sorted(clash)[:6]))
good = [{k: c[k] for k in ("id", "name", "cat", "tags", "note", "html", "css", "js")} for c in good]

print("accepted %d | rejected %d | renamed variants %d" % (len(good), len(raw) - len(good), renamed[0]))
if rejected: print("rejection reasons:", dict(sorted(rejected.items(), key=lambda x: -x[1])))
cats = {}
for c in good: cats[c["cat"]] = cats.get(c["cat"], 0) + 1
print("categories (%d): %s" % (len(cats), dict(sorted(cats.items(), key=lambda x: -x[1]))))

body = ",\n".join(json.dumps(c, ensure_ascii=False) for c in good)
io.open(os.path.join(BASE, "components.js"), "w", encoding="utf-8").write(
    "/* Component library — %d self-contained components.\n"
    "   Each: id (also the CSS class prefix), html, css, js (function body taking `root`). */\n"
    "window.COMPONENTS = [\n%s\n];\n" % (len(good), body))

shell = io.open(os.path.join(BASE, "_lib_shell.html"), encoding="utf-8").read()
app   = io.open(os.path.join(BASE, "_lib_app.html"), encoding="utf-8").read()
comps = io.open(os.path.join(BASE, "components.js"), encoding="utf-8").read()
nav = ''
navf = os.path.join(BASE, "_lib_nav.html")
if os.path.exists(navf): nav = io.open(navf, encoding="utf-8").read()
io.open(os.path.join(BASE, "library.html"), "w", encoding="utf-8").write(
    shell + nav + "<script>\n" + comps + "</script>\n" + app)
print("library.html written (%d KB)" % (os.path.getsize(os.path.join(BASE, "library.html")) // 1024))
