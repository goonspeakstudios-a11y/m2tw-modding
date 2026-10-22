import json, hashlib, os, sys, time
mod = sys.argv[1]
m = json.load(open(os.path.join(mod, ".EUREX1.5", "manifest.json"), encoding="utf-8-sig"))
entries = [e for e in m["files"] if e.get("status") != "deleted" and e.get("source")]
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()
def ts(p): return time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(p)))
changed, missing, hashed = [], [], 0
known = set()
for e in entries:
    rel = e["path"]; src = e["source"]; known.add(rel.lower())
    p = os.path.join(mod, rel)
    if not os.path.isfile(p): missing.append(rel); continue
    st = os.stat(p)
    if st.st_size == src["size"] and st.st_mtime_ns == src["mtime_ns"]:
        continue  # untouched since the 1.5 release tree was built
    hashed += 1
    if sha(p).lower() != src["sha256"].lower():
        changed.append((rel, st.st_size, src["size"], ts(p)))
print("manifest entries:", len(entries), " hashed (size/mtime differ):", hashed)
print("CHANGED vs 1.5 release:", len(changed))
for r in sorted(changed): print("  %-78s live=%8d stock=%8d  %s" % r)
print("MISSING:", len(missing))
for r in missing[:40]: print("  ", r)
extra = []
for root, _, fs in os.walk(mod):
    for f in fs:
        p = os.path.join(root, f); rel = os.path.relpath(p, mod).replace("\\", "/")
        if rel.lower() in known or rel.startswith((".EUREX", "logs/", "saves/")): continue
        if ".bak" in f or rel.startswith("script/") or rel.endswith((".txt", ".nut", ".lua", ".json", ".cfg", ".cas", ".tga")):
            extra.append((rel, os.path.getsize(p), ts(p)))
print("EXTRA (not in manifest; scripts/text/backups):", len(extra))
for r in sorted(extra, key=lambda x: x[2]): print("  %-78s %8d  %s" % r)
