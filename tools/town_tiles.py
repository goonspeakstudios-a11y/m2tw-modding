"""Find each named town's tile on the 1.5 map: black pixel in map_regions.tga touching the region colour. ASCII. Read-only."""
import re, struct, sys
MOD = r"D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR"
want = sys.argv[1:]
txt = open(MOD + "/data/world/maps/base/descr_regions.txt", "rb").read().decode("latin1").splitlines()
cols = {}
i = 0
while i < len(txt):
    l = txt[i].strip()
    if l.endswith("_Province") and not l.startswith(";"):
        j = i + 1; town = None
        while j < len(txt) and j < i + 8:
            s = txt[j].strip()
            if town is None and s and not s.startswith(";") and not s.startswith("legion"):
                town = s
            m = re.match(r"^(\d+)\s+(\d+)\s+(\d+)\s*$", s)
            if m:
                cols[town] = tuple(int(x) for x in m.groups()); break
            j += 1
    i += 1
b = open(MOD + "/data/world/maps/base/map_regions.tga", "rb").read()
idl, cmt, it = b[0], b[1], b[2]
w, h = struct.unpack_from("<HH", b, 12); bpp = b[16]; desc = b[17]
off = 18 + idl; n = bpp // 8
px = bytearray(w * h * n)
if it == 2:
    px[:] = b[off:off + w * h * n]
elif it == 10:
    p = 0; o = off
    while p < w * h * n:
        hdr = b[o]; o += 1; cnt = (hdr & 127) + 1
        if hdr & 128:
            px[p:p + cnt * n] = b[o:o + n] * cnt; o += n
        else:
            px[p:p + cnt * n] = b[o:o + cnt * n]; o += cnt * n
        p += cnt * n
top = bool(desc & 32)
def rgb(x, row):
    k = (row * w + x) * n
    return (px[k + 2], px[k + 1], px[k])
for t in want:
    c = cols.get(t)
    if not c: print(t, "no colour"); continue
    hits = []
    for row in range(h):
        for x in range(w):
            if rgb(x, row) == (0, 0, 0):
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    xx, rr = x+dx, row+dy
                    if 0 <= xx < w and 0 <= rr < h and rgb(xx, rr) == c:
                        y = row if top else (h - 1 - row)
                        hits.append((x, y)); break
    print("%-14s colour=%s tile(s)=%s" % (t, c, hits))
