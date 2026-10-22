"""For every unique battle map NOT assigned by tile, work out which town it is for and whether the
engine's own matching (plan faction + settlement level) can ever pick it. ASCII only. Read-only."""
import glob
import os
import re
import struct

MOD = r"D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR"


def rd(p):
    b = open(p, "rb").read()
    return b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("latin1")


# display names
disp = {}
for m in re.finditer(r"^\{([A-Za-z_0-9]+)\}\s*(.+?)\s*$", rd(MOD + "/data/text/imperial_campaign_regions_and_settlement_names.txt"), re.M):
    disp[m.group(1)] = m.group(2)

# faction -> culture
fac_cult = {}
cur = None
for line in rd(MOD + "/data/descr_sm_factions.txt").splitlines():
    m = re.match(r"^faction\s+(\S+)", line)
    if m:
        cur = m.group(1).strip(",")
    m = re.match(r"^culture\s+(\S+)", line)
    if m and cur:
        fac_cult[cur] = m.group(1)

# towns: name -> owner, plan, level, castle
strat = rd(MOD + "/data/world/maps/campaign/imperial_campaign/descr_strat.txt")
reg_lines = rd(MOD + "/data/world/maps/base/descr_regions.txt").splitlines()
r2s = {}
i = 0
while i < len(reg_lines):
    l = reg_lines[i].strip()
    if l.endswith("_Province") and not l.startswith(";"):
        j = i + 1
        if reg_lines[j].strip().startswith("legion:"):
            j += 1
        r2s[l] = reg_lines[j].strip()
        i = j
    i += 1
towns = {}
for m in re.finditer(r"^faction\s+(\S+).*?(?=^faction\s|\Z)", strat, re.M | re.S):
    owner = m.group(1).strip(",")
    for s in re.finditer(r"^settlement(\s+castle)?[^\n{]*\n\s*\{(.*?)\n\}", m.group(0), re.M | re.S):
        castle = bool(s.group(1))
        b = s.group(2)
        region = re.search(r"region\s+(\S+)", b).group(1)
        level = re.search(r"level\s+(\S+)", b).group(1)
        plan = re.search(r"faction_creator\s+(\S+)", b)
        plan = plan.group(1) if plan else owner
        name = r2s.get(region, region)
        towns[name] = dict(owner=owner, plan=plan, level=level, castle=castle, region=region)

CITY_LEVELS = ["village", "town", "large_town", "city", "large_city", "huge_city"]
# engine battle-map names sit one step below the building names:
# motte_and_bailey->wooden_castle, wooden_castle->stone_keep, castle->castle, fortress->large_castle, citadel->fortress
CASTLE_TYPES = {"village": "wooden_castle", "town": "stone_keep", "large_town": "castle",
                "city": "large_castle", "large_city": "fortress", "huge_city": "fortress"}
TOWN_TYPES = {"town": "small_town"}


def pkg_type_of(t):
    """battle-map 'type' word a town resolves to."""
    return CASTLE_TYPES[t["level"]] if t["castle"] else TOWN_TYPES.get(t["level"], t["level"])


# packages
pkgs = {}
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
    txt = re.sub(rb"[^\x20-\x7e]+", b" ", d[k:]).decode()
    fld = dict(re.findall(r"(culture|faction|fortificationlevel|type)\s+(\S+)", txt))
    rel = os.path.relpath(f, MOD + "/data/settlements").replace("\\", "/")
    pkgs.setdefault(name, []).append((rel, fld))

helpers = rd(MOD + "/script/eur/eru/eurMapHelpers.nut")
casload = rd(MOD + "/script/eur/loaded/eurCasLoad.nut")
used = set(re.findall(r'\["\d+,\d+"\]\s*=\s*"([^"]+)"', helpers)) | set(re.findall(r'custom_maps\["[\d,]+"\]\s*(?:<-|=)\s*"([^"]+)"', casload))

# fuzzy: pkg name -> town by display name
def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())

disp_norm = {norm(v): k for k, v in disp.items() if k in towns}
DIRECT = {"annuminas": "Lake_Evendim", "annuminasrebuilt": "Lake_Evendim", "fornost": "Arthedain", "fornostrebuilt": "Arthedain", "azanulimbardum": "Azanulimbar_Dum",
          "baraddur": "Gorgoroth", "barrowdowns": "Haudh_Nogbenn", "burzakul": "Burzakul", "carndum": "Carn_Dum",
          "dainshall": "Iron_Hills", "fornost": "Arthedain", "fornostrebuilt": "Arthedain", "gundabad": "Mt_Gundabad",
          "hornburg": "Helms_Deep", "moriaeast": "East_Moria", "moriawest": "West_Moria", "orocarnilargecity": "Withered",
          "rivendell": "Imladris", "tolfalas": "Tolfalas", "fangorn": "Fangorn", "ostinedhil": "Eregion"}
ALIASES = {"hornburg": "Helm's Deep", "lorien": "Caras Galadhon", "moriaeast": "East Moria", "moriawest": "West Moria",
           "gram": "Mount Gram", "beorn": "Beorn's Hall", "thorinshalls": "Thorin's Halls", "thranduilshalls": "Thranduil's Halls",
           "dainshall": "Dain's Hall", "ostinedhil": "Ost-in-Edhil", "undertowerssettlement": "Undertowers",
           "barrowdownssettlement": "Barrow-downs", "orocarnilargecity": "Withered Heath", "goblintown": "Goblin-town",
           "blackgate": "Morannon", "rathteraig": "Rath Teraig", "azanulimbardum": "Azanulimbar-dum", "zaghkala": "Zagh Kala"}

print("%-26s %-22s %-24s %-15s %-15s %s" % ("package", "wants faction/type", "town (display)", "plan faction", "town type", "VERDICT"))
unmatched = []
for n, v in sorted(pkgs.items(), key=lambda kv: kv[0].lower()):
    if n in used or not any("nique" in r or "noldor" in r for r, _ in v):
        continue
    rel, fld = v[0]
    base = re.sub(r"_(a|b|c|d|A|B|C|D)$", "", n)
    base = re.sub(r"_(rebuilt|repaired|settlement)$", "", base, flags=re.I)
    key = norm(base)
    if key in ALIASES:
        key = norm(ALIASES[key])
    town = disp_norm.get(key)
    if key in DIRECT:
        cand = DIRECT[key]
        town = cand if cand in towns else None
    if town is None:
        # try prefix / contains
        cands = [k for k in disp_norm if key and (k.startswith(key) or key.startswith(k)) and len(k) > 3]
        town = disp_norm[cands[0]] if len(cands) == 1 else None
    want = "%s/%s" % (fld.get("faction", "?"), fld.get("type", "?"))
    if town is None:
        unmatched.append((n, want, rel))
        continue
    t = towns[town]
    tt = pkg_type_of(t)
    fac_ok = fld.get("faction") == t["plan"]
    type_ok = fld.get("type") == tt
    if fac_ok and type_ok:
        verdict = "should load"
    else:
        parts = []
        if not fac_ok:
            parts.append("plan is %s not %s" % (t["plan"], fld.get("faction")))
        if not type_ok:
            parts.append("town is %s not %s" % (tt, fld.get("type")))
        verdict = "WILL NOT LOAD: " + "; ".join(parts)
    print("%-26s %-22s %-24s %-15s %-15s %s" % (n, want, "%s (%s)" % (town, disp.get(town, "")), t["plan"], tt, verdict))
print()
print("--- generic-culture packs / could not tie to one town (engine picks by culture+faction+type) ---")
for n, want, rel in unmatched:
    print("  %-26s %-22s %s" % (n, want, rel))
