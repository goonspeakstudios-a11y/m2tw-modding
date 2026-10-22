"""Audit every EUR custom settlement asset against the CURRENT campaign map.
ASCII-only output. Read-only."""
import glob
import os
import re
import struct
import sys

MOD = r"D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR"
BASE = MOD + "/data/world/maps/base"
SCR = MOD + "/script"


def rd(p):
    b = open(p, "rb").read()
    return b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("latin1")


# ---------- 1. regions: name, settlement, colour ----------
def parse_regions():
    lines = [l.rstrip("\r") for l in rd(BASE + "/descr_regions.txt").splitlines()]
    regions = []
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        if l.endswith("_Province") and not l.startswith(";"):
            j = i + 1
            if lines[j].strip().startswith("legion:"):
                j += 1
            sett = lines[j].strip()
            # colour line: three ints
            k = j
            rgb = None
            while k < min(j + 6, len(lines)):
                m = re.match(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s*$", lines[k])
                if m:
                    rgb = tuple(int(x) for x in m.groups())
                    break
                k += 1
            regions.append((l, sett, rgb))
            i = k
        i += 1
    return regions


# ---------- 2. TGA (type 2/10, 24/32 bpp) ----------
def decode_tga(path):
    d = open(path, "rb").read()
    idlen, imgtype = d[0], d[2]
    w, h = struct.unpack("<HH", d[12:16])
    bpp, desc = d[16], d[17]
    bpx = bpp // 8
    off = 18 + idlen
    px = []
    if imgtype == 2:
        for i in range(w * h):
            b, g, r = d[off + i * bpx: off + i * bpx + 3]
            px.append((r, g, b))
    elif imgtype == 10:
        p = off
        while len(px) < w * h:
            hdr = d[p]; p += 1
            n = (hdr & 0x7F) + 1
            if hdr & 0x80:
                b, g, r = d[p:p + 3]; p += bpx
                px.extend([(r, g, b)] * n)
            else:
                for _ in range(n):
                    b, g, r = d[p:p + 3]; p += bpx
                    px.append((r, g, b))
    else:
        raise SystemExit("unsupported tga type %d" % imgtype)
    top_origin = bool(desc & 0x20)
    rows = [px[r * w:(r + 1) * w] for r in range(h)]
    if top_origin:
        rows = rows[::-1]  # make row 0 = bottom
    return w, h, rows  # rows[y][x], y=0 is the SOUTH edge


def settlement_tiles(regions):
    w, h, rows = decode_tga(BASE + "/map_regions.tga")
    col2reg = {rgb: (name, sett) for name, sett, rgb in regions if rgb}
    tiles = {}
    for y in range(h):
        for x in range(w):
            if rows[y][x] == (0, 0, 0):
                # region colour from neighbours
                found = None
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and rows[ny][nx] in col2reg:
                        found = col2reg[rows[ny][nx]]
                        break
                if found:
                    tiles[found[1]] = (x, y, found[0])
    return tiles, (w, h)


# ---------- 3. EUR script tables ----------
def nut_table(src, head):
    i = src.find(head)
    if i < 0:
        return ""
    j = src.find("\n}", i)
    return src[i:j]


def parse_models(src):
    blk = nut_table(src, "::EUR.strat_models <-")
    out = {}
    for m in re.finditer(r'^\s*\[(\d+)\]\s*=\s*"([^"]*)"\s*,?\s*(//.*)?$', blk, re.M):
        out[int(m.group(1))] = (m.group(2), (m.group(3) or "").strip("/ \t"))
    return out


def parse_cas_setts(src):
    blk = nut_table(src, "::EUR.strat_cas_setts <-")
    active, commented = {}, []
    for line in blk.splitlines():
        s = line.strip()
        m = re.match(r'^\["([A-Za-z_0-9]+)"\]\s*=\s*(\d+)\s*,?\s*(//.*)?$', s)
        if m:
            active[m.group(1)] = (int(m.group(2)), (m.group(3) or "").strip("/ \t"))
            continue
        m = re.match(r'^//\s*\["([A-Za-z_0-9]+)"\]\s*=\s*(\w+)\s*,?\s*(//.*)?$', s)
        if m:
            commented.append((m.group(1), m.group(2), (m.group(3) or "").strip("/ \t")))
    return active, commented


def parse_custom_maps(src):
    blk = nut_table(src, "::EUR.custom_maps <-")
    out = {}
    for line in blk.splitlines():
        s = line.strip()
        m = re.match(r'^\["(\d+),(\d+)"\]\s*=\s*"([^"]+)"\s*,?\s*(//.*)?$', s)
        if m:
            out[(int(m.group(1)), int(m.group(2)))] = (m.group(3), (m.group(4) or "").strip("/ \t"))
    return out


def parse_swap_tiles(src):
    out = []
    for m in re.finditer(r'setOnTile\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)\s*(//.*)?', src):
        out.append(((int(m.group(1)), int(m.group(2))), int(m.group(3)), (m.group(5) or "").strip("/ \t")))
    for m in re.finditer(r'custom_maps\["(\d+),(\d+)"\]\s*(?:<-|=)\s*"([^"]+)"', src):
        out.append(((int(m.group(1)), int(m.group(2))), "map:" + m.group(3), ""))
    return out


def battle_packages():
    names = {}
    for f in glob.glob(MOD + "/data/settlements/**/*.worldpkgdesc", recursive=True):
        d = open(f, "rb").read()
        k = d.find(b"\x0a\x00\x00\x00settlement")
        if k < 0:
            continue
        name = None
        for p in range(k - 5, max(0, k - 300), -1):
            if struct.unpack("<I", d[p:p + 4])[0] == k - (p + 4):
                name = d[p + 4:k].decode("latin1")
                break
        m = re.search(rb"(settlements/[^\x00]+?\.world)", d[k:], re.I)
        world = m.group(1).decode() if m else ""
        names.setdefault(name, []).append((os.path.relpath(f, MOD + "/data/settlements"), os.path.exists(MOD + "/data/" + world)))
    return names


def main():
    regions = parse_regions()
    tiles, (w, h) = settlement_tiles(regions)
    sett_names = {s for _, s, _ in regions}
    tile2sett = {(x, y): s for s, (x, y, r) in tiles.items()}
    helpers = rd(SCR + "/eur/eru/eurMapHelpers.nut")
    casload = rd(SCR + "/eur/loaded/eurCasLoad.nut")
    saveload = rd(SCR + "/helper/eurSaveLoadValues.nut")
    models = parse_models(helpers)
    cas, cas_commented = parse_cas_setts(helpers)
    cmaps = parse_custom_maps(helpers)
    pkgs = battle_packages()

    print("map %dx%d, regions %d, settlement tiles found %d" % (w, h, len(regions), len(tiles)))
    print()

    # ---- A. campaign-map model table ----
    print("=== A. CAMPAIGN-MAP CITY MODELS (strat_cas_setts) ===")
    bad = 0
    for name, (mid, cmt) in sorted(cas.items()):
        exists = name in sett_names
        path = models.get(mid, ("?", ""))[0]
        file_ok = os.path.exists(MOD + "/data/models_strat/residences/" + path) if path != "?" else False
        flag = "OK" if exists and file_ok else ("NO SUCH TOWN" if not exists else "MODEL FILE MISSING")
        if flag != "OK":
            bad += 1
        print("  %-18s -> model %2d %-55s %s %s" % (name, mid, path, flag, ("(" + cmt + ")") if cmt else ""))
    print("  problems: %d" % bad)
    print()
    print("--- models with a town in their comment but NOT assigned to any current town ---")
    assigned_ids = {mid for mid, _ in cas.values()}
    # also ids used by swap code
    swap_ids = {int(x) for x in re.findall(r"setOnTile\(\d+,\s*\d+,\s*(\d+)", casload)}
    swap_ids |= {int(x) for x in re.findall(r'strat_cas_setts\["[A-Za-z_]+"\]\s*=\s*(\d+)', casload)}
    for mid, (path, cmt) in sorted(models.items()):
        if mid in assigned_ids or mid in swap_ids:
            continue
        print("  model %2d %-55s %s" % (mid, path, cmt))
    print()
    print("--- commented-out table entries (towns intentionally left to the swap scripts?) ---")
    for name, val, cmt in cas_commented:
        print("  %-18s = %s  %s  [town exists: %s]" % (name, val, cmt, name in sett_names))
    print()

    # ---- B. battle maps by coordinate ----
    print("=== B. CUSTOM BATTLE MAPS (custom_maps, keyed by tile) ===")
    bad = 0
    for (x, y), (mapname, cmt) in sorted(cmaps.items(), key=lambda kv: kv[1][0]):
        here = tile2sett.get((x, y))
        pk = pkgs.get(mapname)
        pk_ok = bool(pk) and any(ok for _, ok in pk)
        if here is None:
            # nearest settlement
            near = min(tiles.items(), key=lambda kv: abs(kv[1][0] - x) + abs(kv[1][1] - y))
            flag = "NO TOWN ON THIS TILE (nearest %s at %d,%d)" % (near[0], near[1][0], near[1][1])
            bad += 1
        else:
            flag = "OK -> " + here
        if not pk_ok:
            flag += " | MAP PACKAGE MISSING"
            bad += 1
        print("  %3d,%-3d %-26s %s   %s" % (x, y, mapname, flag, ("(" + cmt + ")") if cmt else ""))
    print("  problems: %d" % bad)
    print()

    # ---- C. hard-coded swap tiles ----
    print("=== C. HARD-CODED SWAP TILES (eurCasLoad / eurSaveLoadValues) ===")
    seen = set()
    bad = 0
    for (x, y), what, cmt in parse_swap_tiles(casload) + parse_swap_tiles(saveload):
        key = ((x, y), str(what))
        if key in seen:
            continue
        seen.add(key)
        here = tile2sett.get((x, y))
        flag = ("OK -> " + here) if here else "NO TOWN ON THIS TILE"
        if not here:
            bad += 1
        print("  %3d,%-3d %-32s %s %s" % (x, y, str(what), flag, ("(" + cmt + ")") if cmt else ""))
    print("  problems: %d" % bad)
    print()

    # ---- D. unique battle maps installed but never assigned ----
    print("=== D. UNIQUE BATTLE MAPS INSTALLED BUT NOT ASSIGNED TO ANY TILE ===")
    used = {m for m, _ in cmaps.values()} | set(re.findall(r'custom_maps\["[\d,]+"\]\s*(?:<-|=)\s*"([^"]+)"', casload + saveload))
    for n, v in sorted(pkgs.items(), key=lambda kv: kv[0].lower()):
        if n in used:
            continue
        if any("nique" in p for p, _ in v):
            print("  %-28s %s" % (n, v[0][0].replace("\\", "/").rsplit("/", 1)[0]))
    print()

    # ---- E. towns table for reference ----
    if "--tiles" in sys.argv:
        print("=== TILES ===")
        for s, (x, y, r) in sorted(tiles.items()):
            print("  %-26s %3d,%-3d %s" % (s, x, y, r))


main()
