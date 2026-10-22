# m2tw-modding

Fix packs for EUREX: Divide and Conquer EUR (Medieval II Total War) running on the M2EX engine.
Everything here was made and verified on one Windows install; the history of every change is in
`CHANGELOG.md`.

## Current release: EUR 1.5.2 fix pack (for EUREX 1.5)

Players: download `EUR_1.5.2_FixPack.zip` from the Releases page, extract it into your `mods`
folder, overwrite, restart the game. The Moria route fix needs a new campaign. Seven files;
what each one fixes is in the zip's `README.txt` and in `CHANGELOG.md`.

## Rule: every pack carries every fix

A fix that was in any earlier pack is in every later pack. It leaves only when it is moved to
`retired` in `hotfixes/eurex-1.5-hotfix-1/fix_registry.json` with a written reason.
`build_pack.py` enforces this and writes no zip when:

- a fix from any earlier pack (the `packs` history) is neither shipped nor retired;
- the fix list and `apply_hotfix.py` disagree about which files are fixed;
- the new pack's version is not recorded with exactly the shipped files;
- the install it builds from has a file that differs from the EUREX 1.5 release, or a new script
  module, that is neither shipped nor listed under `not_shipped` with a reason (this is how a
  fix made in-game but never added to the pack gets caught);
- a shipped file is unpatched, or missing from the finished zip.

To add a fix: patch it in `apply_hotfix.py`, list it under `shipped`, bump `ZIP_NAME` in
`build_pack.py`, record the new version under `packs`, add a `CHANGELOG.md` line.

## Layout

| Path | Purpose |
|------|---------|
| `CHANGELOG.md` | Every change ever made, by date, with what it fixes, what it superseded and what was left out |
| `eurex-1.5/overlay/Divide_and_Conquer_EUR/` | The seven fixed files exactly as they sit in the mod folder; this is the content of the release zip |
| `eurex-1.5/diffs/` | Unified diff of each fixed file against the stock EUREX 1.5 file |
| `hotfixes/eurex-1.5-hotfix-1/` | Patcher that applies the same seven fixes to any EUREX 1.5 install (`apply_hotfix.py`), pack builder, player README, technical notes (`CHANGES.md`), tests |
| `history/eurex-1.4.2/` | The 2026-10-14 fix pack for EUREX 1.4.2 (eight files) |
| `history/aragorn-journey-fix-2026-10-12/` | The first hotfix, Aragorn journey chain under M2EX |
| `tools/` | Scripts used along the way: manifest comparison, asset and tile audits, installer extraction, mod-folder cleanup, plus the 2026-10-15 cleanup log and the list of 83 recovered files |

## Using the patcher instead of the zip

Stdlib-only Python 3.10+. Writes `.bak_eurex15_hotfix1` backups next to each file; idempotent. It patches a STOCK 1.5 install; on an install that already has the older 1.5.1 pack, use the zip instead (it overwrites).

```
python hotfixes/eurex-1.5-hotfix-1/apply_hotfix.py "<game>/mods/Divide_and_Conquer_EUR"
python hotfixes/eurex-1.5-hotfix-1/apply_hotfix.py "<game>/mods/Divide_and_Conquer_EUR" --check
python hotfixes/eurex-1.5-hotfix-1/apply_hotfix.py "<game>/mods/Divide_and_Conquer_EUR" --revert
```

Build the release zip from a patched mod folder:

```
python hotfixes/eurex-1.5-hotfix-1/build_pack.py "<game>/mods/Divide_and_Conquer_EUR" --out <folder>
```

Tests:

```
python -m unittest discover -s hotfixes/eurex-1.5-hotfix-1/tests -v
```

List every file in an install that differs from the EUREX 1.5 release (reads
`.EUREX1.5/manifest.json`, hashes only files whose size or time changed):

```
python -I tools/manifest_diff.py "<game>/mods/Divide_and_Conquer_EUR"
```

## Install trap worth repeating

`EUREX1.5M2EX.7z` is the engine package in game-root layout. It goes into
`Medieval II Total War\`, never into the mod folder. Unpacked into the mod it replaces the
mod's `script/main.nut` (no EUR menus, no presets) and drops a `data/descr_caps_ex.txt` that
stops every unit model from loading. `apply_hotfix.py` warns when it sees that file.

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
