"""Second pass: only references that matter (used by a defined unit/character/building), with each
missing file classified as VANILLA (exists in another stock mod folder = came from the deleted base packs)
or MOD-ONLY (the mod itself never shipped it). ASCII only. Read-only."""
import os
import re
import glob
from collections import defaultdict

G = r"D:/SteamLibrary/steamapps/common/Medieval II Total War"
MOD = G + "/mods/Divide_and_Conquer_EUR"
DATA = MOD + "/data"


def rd(p):
    b = open(p, "rb").read()
    return b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("latin1")


def norm(p):
    p = p.replace("\\", "/").strip().strip('"').lower()
    return p[5:] if p.startswith("data/") else p


# vanilla proxy index: stock Kingdoms folders + TES (ships vanilla-derived assets) + base data
vanilla = set()
for root in [G + "/mods/" + m + "/data" for m in ["americas", "british_isles", "crusades", "teutonic", "The_Elder_Scrolls"]] + [G + "/data"]:
    for dp, dn, fn in os.walk(root):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), root).replace("\\", "/").lower()
            vanilla.add(rel)
            vanilla.add(os.path.splitext(rel)[0])


def exists(rel):
    rel = norm(rel)
    base = os.path.splitext(rel)[0]
    for c in [rel, base + ".texture", rel + ".dds", base + ".tga", base + ".tga.dds", base + ".dds", base + ".cas"]:
        if os.path.exists(DATA + "/" + c) or os.path.exists(G + "/data/" + c):
            return True
    return False


def cls(rel):
    rel = norm(rel)
    base = os.path.splitext(rel)[0]
    return "VANILLA" if (rel in vanilla or base in vanilla) else "MOD-ONLY"


def report(title, missing):
    v = sorted(p for p in missing if cls(p) == "VANILLA")
    m = sorted(p for p in missing if cls(p) == "MOD-ONLY")
    print("=== %s: %d missing files -> %d VANILLA (lost with the base packs), %d MOD-ONLY" % (title, len(missing), len(v), len(m)))
    for p in m[:25]:
        print("   MOD-ONLY  %s   <- %s" % (p, missing[p][0]))
    if len(m) > 25:
        print("   ... %d more mod-only" % (len(m) - 25))
    for p in v[:6]:
        print("   vanilla   %s" % p)
    if len(v) > 6:
        print("   ... %d more vanilla" % (len(v) - 6))
    print()


# ---- modeldb, EDU-used entries only
txt = rd(DATA + "/unit_models/battle_models.modeldb")
entries = {}
cur = None
names = set()
for mm in re.finditer(r"(\d+) ([^\r\n\t]{1,400}?)(?=\s)", txt):
    n = int(mm.group(1))
    s = mm.group(2)
    if len(s) < n or n < 2:
        continue
    s = s[-n:]
    if re.search(r"\.(mesh|texture|cas)$", s, re.I):
        if cur:
            entries.setdefault(cur, []).append(s)
    elif re.fullmatch(r"[A-Za-z0-9_\-\.]+", s) and not s[0].isdigit():
        cur = s
        names.add(s)
edu = rd(DATA + "/export_descr_unit.txt")
used = set()
badnames = []
units = 0
for blk in re.split(r"\n(?=type\s)", edu):
    t = re.match(r"type\s+(.+)", blk)
    if not t:
        continue
    units += 1
    for key in ("soldier", "officer"):
        for mm in re.finditer(r"^%s\s+([^,\s]+)" % key, blk, re.M):
            used.add(mm.group(1))
            if mm.group(1) not in names:
                badnames.append((t.group(1).strip(), mm.group(1)))
dm = rd(DATA + "/descr_mount.txt")
for mm in re.finditer(r"^\s*model\s+(\S+)", dm, re.M):
    used.add(mm.group(1))
print("modeldb entries parsed: %d | EDU units: %d | model names used: %d | used names NOT in modeldb: %d %s" % (len(names), units, len(used), len(badnames), badnames[:8]))
missing = defaultdict(list)
for e in used:
    for f in entries.get(e, []):
        if not exists(f):
            missing[norm(f)].append(e)
report("Battle models/textures of units actually defined (modeldb, used entries)", missing)

# ---- descr_model_strat, used by descr_character
dms = rd(DATA + "/descr_model_strat.txt")
dc = re.sub(r";.*", "", rd(DATA + "/descr_character.txt"))
usedt = set()
for mm in re.finditer(r"^\s*strat_model\s+(.+)$", dc, re.M):
    usedt |= {x.strip() for x in mm.group(1).split(",") if x.strip()}
types = {}
cur = None
for line in dms.splitlines():
    l = re.sub(r";.*", "", line).strip()
    mm = re.match(r"type\s+(\S+)", l)
    if mm:
        cur = mm.group(1)
        types[cur] = []
        continue
    mm = re.match(r"model_flexi(?:_m)?\s+([^,\s]+\.cas)", l, re.I)
    if mm and cur:
        types[cur].append(mm.group(1))
    mm = re.match(r"texture\s+(?:\w+\s*,\s*)?([^\s,]+\.(?:tga|texture))", l, re.I)
    if mm and cur:
        types[cur].append(mm.group(1))
undefined = sorted(usedt - set(types))
print("descr_character strat_model names: %d used, %d NOT defined in descr_model_strat %s" % (len(usedt), len(undefined), undefined[:8]))
missing = defaultdict(list)
for tname in usedt & set(types):
    for f in types[tname]:
        if not exists(f):
            missing[norm(f)].append(tname)
report("Campaign-map character models actually used (descr_model_strat)", missing)

# ---- building pics with culture prefix
edb = rd(DATA + "/export_descr_buildings.txt")
levels = []
for mm in re.finditer(r"^building\s+(\S+).*?^\s*levels\s+(.+?)$", edb, re.M | re.S):
    levels += mm.group(2).split()
cultures = [d for d in os.listdir(DATA + "/ui") if os.path.isdir(os.path.join(DATA, "ui", d, "buildings"))]
nowhere = [l for l in levels if not any(exists("ui/%s/buildings/#%s_%s.tga" % (c, c, l)) for c in cultures)]
print("=== Building pictures (#<culture>_<level>.tga): %d levels, %d with no picture in any culture folder" % (len(levels), len(nowhere)))
vn = [l for l in nowhere if any(("ui/%s/buildings/#%s_%s" % (c, c, l)) in vanilla for c in cultures)]
print("   of which vanilla-stock building names (pics were in the base packs): %d %s" % (len(vn), vn[:10]))
print("   mod-specific with no picture at all: %d %s" % (len(nowhere) - len(vn), [l for l in nowhere if l not in vn][:20]))
print()

# ---- eventpics with none anywhere
names_ev = set()
for f in glob.glob(DATA + "/world/maps/campaign/**/campaign_script.txt", recursive=True):
    names_ev |= set(re.findall(r"historic_event\s+(\w+)", rd(f)))
for f in glob.glob(MOD + "/script/**/*.nut", recursive=True):
    names_ev |= set(re.findall(r'showHistoricEvent\("(\w+)"', rd(f)))
ecult = [d for d in os.listdir(DATA + "/ui") if os.path.isdir(os.path.join(DATA, "ui", d, "eventpics"))]
none = sorted(n for n in names_ev if not any(exists("ui/%s/eventpics/%s.tga" % (c, n)) for c in ecult))
print("=== Event pictures: %d events, %d with no picture anywhere: %s" % (len(names_ev), len(none), none))
print()

# ---- faction logos
sm = rd(DATA + "/descr_sm_factions.txt")
missing = defaultdict(list)
for key in ("symbol", "rebel_symbol", "loading_logo"):
    for mm in re.finditer(r"^%s\s+(\S+)" % key, sm, re.M):
        if not exists(mm.group(1)):
            missing[norm(mm.group(1))].append(key)
report("Faction symbols / loading logos", missing)

# ---- effects
missing = defaultdict(list)
for fn in ["descr_arrow_trail_effects.txt", "descr_flaming_projectiles.txt", "descr_burning_men_effect.txt",
           "descr_burning_oil_effect.txt", "descr_burning_building.txt", "descr_campfires_brasiers.txt",
           "descr_projectile.txt", "descr_engines.txt", "descr_ship.txt"]:
    p = DATA + "/" + fn
    if not os.path.exists(p):
        continue
    t = re.sub(r";.*", "", rd(p))
    for mm in re.finditer(r"^\s*(?:texture|model|model_flexi|flexi_model)\s+([^\s,]+\.(?:tga|texture|cas|mesh))", t, re.M | re.I):
        if not exists(mm.group(1)):
            missing[norm(mm.group(1))].append(fn)
report("Effects / projectiles / engines / ships", missing)

# ---- battle-map packages: missing .world, with twin check
byname = defaultdict(list)
noworld = []
for f in glob.glob(DATA + "/settlements/**/*.worldpkgdesc", recursive=True):
    d = open(f, "rb").read()
    k = d.find(b"\x0a\x00\x00\x00settlement")
    if k < 0:
        continue
    mm = re.search(rb"(settlements/[^\x00]+?)\.world\b", d, re.I)
    if not mm:
        continue
    world = mm.group(1).decode()
    nm = os.path.basename(world).lower()
    ok = os.path.exists(DATA + "/" + world + ".world")
    rel = os.path.relpath(f, DATA + "/settlements").replace("\\", "/")
    byname[nm].append((rel, ok))
    if not ok:
        noworld.append((rel, nm))
print("=== Battle-map packages pointing at a .world that does not exist: %d" % len(noworld))
for p, nm in noworld:
    twin = [q for q, ok in byname[nm] if ok]
    print("   %-75s %s" % (p, ("twin OK: " + twin[0]) if twin else "NO WORKING COPY"))
print()

# ---- units with missing cards: are they recruitable?
strat = rd(DATA + "/world/maps/campaign/imperial_campaign/descr_strat.txt")
for u in ["Lego Rohirrim", "Lego Spearmen", "Desert Uruks", "Lego Uruk-hai Infantry"]:
    print("   %-26s recruit lines in EDB: %d | descr_strat: %d" % (u, len(re.findall(re.escape(u), edb)), len(re.findall(re.escape(u), strat))))
print()

# ---- unit_info layout
cnt = defaultdict(int)
for dp, dn, fn in os.walk(DATA + "/ui"):
    for f in fn:
        if f.lower().endswith("_info.tga"):
            cnt[os.path.relpath(dp, DATA).replace("\\", "/")] += 1
top = sorted(cnt.items(), key=lambda kv: -kv[1])[:8]
print("=== where *_info.tga unit pictures live (top folders):", top)
