"""Move the 1,649 stray engine files out of mods/Divide_and_Conquer_EUR into the E: backup
folder and put back the 15 mod files they overwrote. Nothing is deleted; everything moved
lands in E:\\M2TW_backup_2026-10-15\\engine_files_moved_out_of_mod_folder\\ and is logged."""
import os, json, zipfile, hashlib, shutil, collections

GAME = r"D:\SteamLibrary\steamapps\common\Medieval II Total War"
os.chdir(GAME)
dac = "mods/Divide_and_Conquer_EUR/"
e15 = "mods/EUREX1.5/"
quarantine = "E:/M2TW_backup_2026-10-15/engine_files_moved_out_of_mod_folder/"
plan = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mod_fix_plan.json")))
man = json.load(open(e15 + ".EUREX1.5/manifest.json", encoding="utf-8"))
rec = {r["path"].replace("\\", "/").lower(): r for r in man["files"]}
z = zipfile.ZipFile("mods/EUREX1.4.2.zip")
zn = {n.lower(): n for n in z.namelist()}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


log = open("E:/M2TW_backup_2026-10-15/mod_folder_cleanup_log.txt", "w")
c = collections.Counter()
for act, p in plan:
    t = dac + p
    if not os.path.isfile(t):
        c["already gone"] += 1
        continue
    if act == "delete":
        d = quarantine + p
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.move(t, d)
        c["moved out to E:"] += 1
        log.write(f"moved\t{p}\n")
    elif act == "from15":
        shutil.copy2(e15 + p, t)
        c["restored from 1.5"] += 1
        log.write(f"restored-1.5\t{p}\n")
    elif act == "from142":
        open(t, "wb").write(z.read(zn[p.lower()]))
        c["restored from 1.4.2"] += 1
        log.write(f"restored-1.4.2\t{p}\n")
    if act != "delete":
        assert sha(open(t, "rb").read()) == rec[p.lower()]["source"]["sha256"], p

# README step 4: the two stale text caches 1.5 says to remove (only if they are the exact baseline files)
for r in man["files"]:
    if r["status"] != "deleted":
        continue
    p = r["baseline"]["path"].replace("\\", "/")
    t = dac + p
    if os.path.isfile(t) and sha(open(t, "rb").read()) == r["baseline"]["sha256"]:
        d = quarantine + "_obsolete_1.4.2_files/" + p
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.move(t, d)
        c["obsolete 1.4.2 file moved out"] += 1
        log.write(f"moved-obsolete\t{p}\n")

removed = 0
for root, dirs, files in os.walk(dac, topdown=False):
    for d in dirs:
        q = os.path.join(root, d)
        if not os.listdir(q):
            os.rmdir(q)
            removed += 1
            log.write(f"rmdir-empty\t{q}\n")
print(dict(c), "empty folders removed:", removed)
print("main.nut is the 1.5 one:", sha(open(dac + "script/main.nut", "rb").read()) == sha(open(e15 + "script/main.nut", "rb").read()))
print("mod folder top level now:", sorted(os.listdir(dac)))
for p in ("data/descr_caps_ex.txt", "data/descr_model_battle.txt", "Americas.bat", "packs/voices.pack"):
    print(f"  {p}: {'STILL THERE - cleanup incomplete' if os.path.exists(dac + p) else 'gone (good)'}")
