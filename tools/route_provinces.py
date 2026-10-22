"""Which province owns each quest pointer tile, and which provinces a straight walk between pointers crosses. ASCII. Read-only."""
import re, struct
MOD = r"D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR"
def regions(path):
    txt = open(path, "rb").read().decode("latin1").splitlines()
    col2prov = {}
    i = 0
    while i < len(txt):
        l = txt[i].strip()
        if l.endswith("_Province") and not l.startswith(";") and not l.startswith("legion"):
            for j in range(i + 1, min(i + 9, len(txt))):
                m = re.match(r"^(\d+)\s+(\d+)\s+(\d+)\s*$", txt[j].strip())
                if m:
                    col2prov[tuple(int(x) for x in m.groups())] = l; break
        i += 1
    return col2prov
cur = regions(MOD + "/data/world/maps/base/descr_regions.txt")
try:
    old = regions(MOD + "/data/world/maps/base/descr_regions.txt.bak")
    print("provinces NEW since the .bak:", sorted(set(cur.values()) - set(old.values())))
    print("provinces GONE since the .bak:", sorted(set(old.values()) - set(cur.values())))
except OSError:
    print("no .bak")
b = open(MOD + "/data/world/maps/base/map_regions.tga", "rb").read()
idl, it = b[0], b[2]; w, h = struct.unpack_from("<HH", b, 12); n = b[16] // 8; desc = b[17]
off = 18 + idl; px = bytearray(w * h * n)
if it == 2: px[:] = b[off:off + w * h * n]
else:
    p = 0; o = off
    while p < w * h * n:
        hdr = b[o]; o += 1; cnt = (hdr & 127) + 1
        if hdr & 128: px[p:p + cnt * n] = b[o:o + n] * cnt; o += n
        else: px[p:p + cnt * n] = b[o:o + cnt * n]; o += cnt * n
        p += cnt * n
top = bool(desc & 32)
def prov(x, y):
    row = y
    k = (row * w + x) * n
    c = (px[k + 2], px[k + 1], px[k])
    if c == (0, 0, 0): return "TOWN"
    if c == (255, 255, 255): return "PORT"
    return cur.get(c, "?%s" % (c,))
print("map", w, "x", h)
pts = [(338,416),(338,399),(327,392),(316,392),(305,391),(289,393),(289,387),(270,364),(249,337)]
for (x, y) in pts: print("pointer %3d,%3d -> %s" % (x, y, prov(x, y)))
for (a, bb) in zip(pts, pts[1:]):
    seen = []
    steps = max(abs(bb[0]-a[0]), abs(bb[1]-a[1]))
    for s in range(steps + 1):
        x = round(a[0] + (bb[0]-a[0]) * s / steps); y = round(a[1] + (bb[1]-a[1]) * s / steps)
        p = prov(x, y)
        if not seen or seen[-1] != p: seen.append(p)
    print("walk %s -> %s crosses: %s" % (a, bb, " | ".join(seen)))

print()
print("=== corridor provinces (within 4 tiles of each leg) vs the script's whitelist ===")
lists = {
 "status1 (accepted)  leg 338,416->338,399": ("Dale_Province Esgaroth_Province Elven_Mirkwood_Province", [(338,416),(338,399)]),
 "status1->2 leg 338,399->327,392": ("Central_Mirkwood_Province Elven_Mirkwood_Province Esgaroth_Province", [(338,399),(327,392)]),
 "status2->3 leg 327,392->316,392": ("Central_Mirkwood_Province Middle_Mirkwood_Province Deep_Mirkwood_Province", [(327,392),(316,392)]),
 "status3->4 leg 316,392->305,391": ("Middle_Mirkwood_Province Central_Mirkwood_Province Central_Vale_Province Woodsmen_Province Deep_Mirkwood_Province", [(316,392),(305,391)]),
 "status4->5 leg 305,391->289,393": ("Central_Mirkwood_Province Lower_Anduin_Vale_Province Middle_Mirkwood_Province", [(305,391),(289,393)]),
 "status5->6 leg 289,393->270,364": ("Central_Vale_Province Lower_Anduin_Vale_Province Gladden_Fields_Province Middle_Mirkwood_Province Woodsmen_Province Pezarsan_Province West_Mirkwood_Province", [(289,393),(289,387),(270,364)]),
 "status6->7 leg 270,364->249,337": ("Gladden_Fields_Province Celebrant_Province East_Moria_Province Pezarsan_Province West_Mirkwood_Province", [(270,364),(249,337)]),
 "status7->8 at 249,337": ("East_Moria_Province West_Mirkwood_Province", [(249,337),(245,341)]),
}
for label, (wl, pts) in lists.items():
    allowed = set(wl.split())
    found = set()
    for a, bb in zip(pts, pts[1:]):
        steps = max(abs(bb[0]-a[0]), abs(bb[1]-a[1]), 1)
        for s in range(steps + 1):
            cx = round(a[0] + (bb[0]-a[0]) * s / steps); cy = round(a[1] + (bb[1]-a[1]) * s / steps)
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < w and 0 <= y < h:
                        p = prov(x, y)
                        if p.endswith("_Province"): found.add(p)
    print(label)
    print("   corridor:", sorted(found))
    print("   MISSING from whitelist:", sorted(found - allowed))
