#!/usr/bin/env python3
"""Merge component workflow output -> components.js -> library.html, with hard validation."""
import io, json, os, re, subprocess, sys, glob
from libcheck import strip_at_blocks, unescape_markup, validate, js_ok

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
