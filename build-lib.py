#!/usr/bin/env python3
"""components-src/*.json -> components.js -> library.html, with hard validation.

components-src/ is the source of truth: one JSON array per category, built in
filename order. Add components by writing a batch and installing it with
`python3 libcheck.py batch.json --install components-src/NNNN-name.json`,
then run this script.
"""
import io, json, os, glob
from libcheck import unescape_markup, validate, js_ok, sanitize, KEYS

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "components-src")


def collect():
    rows = []
    files = sorted(glob.glob(os.path.join(SRC, "*.json")))
    if not files:
        raise SystemExit("components-src/ is empty — refusing to overwrite components.js "
                         "with an empty library")
    for f in files:
        try:
            data = json.load(io.open(f, encoding="utf-8"))
        except Exception as e:
            print("SKIPPED %s — not valid JSON (%s)" % (os.path.basename(f), e))
            continue
        rows.extend(data if isinstance(data, list) else data.get("components", []))
    return rows, len(files)


# Components proven broken at runtime in the browser. Syntax checking cannot
# catch these, so anything that fails to mount during verification is recorded
# here with its reason rather than shipped as a broken card.
BLOCK = {
    "t213-aggr-ratio": "TypeError at mount: 'f is not a function'",
}

raw, nfiles = collect()
print("collected %d components from %d files in components-src/" % (len(raw), nfiles))
seen, good, rejected, renamed, redacted = set(), [], {}, [0], [0]
for c in raw:
    cid = c.get("id", "")
    if cid in BLOCK:
        rejected["runtime failure"] = rejected.get("runtime failure", 0) + 1
        continue
    c["html"] = unescape_markup(c.get("html", "") or "")
    # never ship a string shaped like a real provider credential, even an invented one
    for note in sanitize(c):
        redacted[0] += 1
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
        print("REJECTED %s — %s" % (cid, probs[0]))
        rejected[probs[0].split(":")[0]] = rejected.get(probs[0].split(":")[0], 0) + 1
        continue
    seen.add(cid)
    c["_id"] = cid
    good.append(c)

# @keyframes and @property registrations are document-global, so a name used by
# two components silently hijacks one of them. Reject genuine collisions only.
for field, what in (("_kf", "@keyframes"), ("_props", "@property")):
    owner, clash = {}, set()
    for c in good:
        for n in c.get(field, []):
            if n in owner and owner[n] != c["_id"]: clash.add(n)
            owner.setdefault(n, c["_id"])
    if clash:
        before = len(good)
        good = [c for c in good if not (set(c.get(field, [])) & clash)]
        print("dropped %d for colliding %s names: %s" % (before - len(good), what, sorted(clash)[:6]))

good = [{k: c[k] for k in KEYS if k in c and (k == "js" or c[k] not in (None, ""))} for c in good]

print("accepted %d | rejected %d | renamed variants %d | credential-shaped strings redacted %d"
      % (len(good), len(raw) - len(good), renamed[0], redacted[0]))
if rejected: print("rejection reasons:", dict(sorted(rejected.items(), key=lambda x: -x[1])))
cats = {}
for c in good: cats[c["cat"]] = cats.get(c["cat"], 0) + 1
print("categories: %d" % len(cats))

body = ",\n".join(json.dumps(c, ensure_ascii=False) for c in good)
io.open(os.path.join(BASE, "components.js"), "w", encoding="utf-8").write(
    "/* Component library — %d self-contained components. Built from components-src/.\n"
    "   Each: id (also the CSS class prefix), html, css, js (function body taking `root`),\n"
    "   optional span (\"full\" = takes a whole row). */\n"
    "window.COMPONENTS = [\n%s\n];\n" % (len(good), body))

# library.html references components.js rather than inlining it: the data was
# being stored twice in the repo, and every rebuild doubled the diff.
shell = io.open(os.path.join(BASE, "_lib_shell.html"), encoding="utf-8").read()
app   = io.open(os.path.join(BASE, "_lib_app.html"), encoding="utf-8").read()
nav = ''
navf = os.path.join(BASE, "_lib_nav.html")
if os.path.exists(navf): nav = io.open(navf, encoding="utf-8").read()
io.open(os.path.join(BASE, "library.html"), "w", encoding="utf-8").write(
    shell + nav + '<script src="components.js"></script>\n' + app)
print("components.js %d KB · library.html %d KB" % (
    os.path.getsize(os.path.join(BASE, "components.js")) // 1024,
    os.path.getsize(os.path.join(BASE, "library.html")) // 1024))
