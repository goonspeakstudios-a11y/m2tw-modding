# m2tw-modding

Versions and hotfixes for EUREX (Divide and Conquer EUR on the M2EX engine).

## Layout

| Path | Purpose |
|------|---------|
| `hotfixes/eurex-1.5-hotfix-1/` | Fix set for EUREX 1.5: six file patches, pack builder, player-facing README, provenance |

## EUREX 1.5 hotfix 1

Stdlib-only Python 3.10+ (tested on 3.13; the rig runs 3.14). No dependencies to install.

Apply to an installed mod folder (writes `.bak_eurex15_hotfix1` backups, idempotent):

```
python hotfixes/eurex-1.5-hotfix-1/apply_hotfix.py "D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR"
```

Dry run / undo:

```
python hotfixes/eurex-1.5-hotfix-1/apply_hotfix.py <mod folder> --check
python hotfixes/eurex-1.5-hotfix-1/apply_hotfix.py <mod folder> --revert
```

Build the drop-in zip for the EUREX thread from a patched mod folder:

```
python hotfixes/eurex-1.5-hotfix-1/build_pack.py <mod folder> --out "C:/Users/BigBoss1/Desktop/EUR_1.5_FixPack_upload"
```

Tests:

```
python -m unittest discover -s hotfixes/eurex-1.5-hotfix-1/tests -v
```

What each patch fixes and why: `hotfixes/eurex-1.5-hotfix-1/CHANGES.md`.
Player-facing bug list that ships inside the zip: `hotfixes/eurex-1.5-hotfix-1/README.txt`.

## Failure modes of apply_hotfix.py

| Trigger | Behaviour |
|---------|-----------|
| Mod folder missing or has no `script/eur` | exit 2, nothing written |
| `.EUREX1.5/manifest.json` absent | warning, hunks still matched exactly |
| `data/descr_caps_ex.txt` present in the mod | warning: engine package was unpacked into the mod folder |
| A hunk's "before" text absent and "after" text absent (file edited or wrong version) | that file is skipped unchanged, exit 1; other files still patched |
| All hunks of a file already present | reported `already-applied`, file untouched |
| Brace/paren balance of a `.nut` breaks after patching | file left untouched, exit 1 |
| Write fails mid-way | temp file written first then renamed; original stays intact |
| `--revert` with backup present | backup restored and removed |
| `--revert` without backup | inverse text replacement, refused if a replacement is ambiguous |
