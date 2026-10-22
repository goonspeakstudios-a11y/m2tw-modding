# Changelog - EUR fix packs for Divide and Conquer EUR on the M2EX engine

Every entry is a change made on BB1's machine to the mod folder
`mods\Divide_and_Conquer_EUR` (or the game root) and verified there. Dates are the day the
change was made. "Pack" means the drop-in zip a player extracts into `mods\` and overwrites.
Technical detail per fix (root cause, exact hunks, encodings) lives in
`hotfixes/eurex-1.5-hotfix-1/CHANGES.md`; the exact diffs are in `eurex-1.5/diffs/`.

## 1.5.1 - 2026-10-22 - stable pack for EUREX 1.5 (`EUR_1.5.1_FixPack.zip`)

Requires: Divide and Conquer EUR 2.08 with the EUREX 1.5 overlay and the M2EX engine build of
2026-10-15. Does not apply to EUREX 1.4.2 (use the 1.4.2 pack under `history/`).

Seven files. Install: extract the zip into `mods\`, overwrite, restart the game.

| # | Fix (what a player sees) | File | Since | Needs |
|---|---|---|---|---|
| 1 | Custom city models (Bree, Amon Hen, every custom-look town) no longer go generic in the second campaign loaded or started in one game session. | `script/helper/eurCampaignTriggers.nut` | 2026-10-14, re-done for 1.5 on 2026-10-18 | restart |
| 2 | Amon Hen shows its own stone-platform model again; Hobbiton and Bree custom battle maps are keyed to the tiles the 1.5 map actually uses. | `script/eur/eru/eurMapHelpers.nut` | 2026-10-14, re-done for 1.5 on 2026-10-18 | restart |
| 3 | The unit-upgrade / bodyguard crest no longer disappears for the rest of the session after a battle or reload. | `script/eur/upgrades/eurGeneralBGSwap.nut` | 2026-10-16 | restart |
| 4 | Reclaiming Moria quest (Durin's Folk, Mirkwood route): the arrow target no longer says "Restricted area". | `data/world/maps/campaign/imperial_campaign/campaign_script.txt` | 2026-10-18 | NEW campaign |
| 5 | No more green debug shapes under monster area attacks (trolls, Balrog, Mumakil). | `script/eur/battle/monsterAbilityConfig.nut` | 2026-10-18 | restart |
| 6 | Diagnostic only: `[EUR cas]` lines in `system.log.txt` name every custom town model that is applied, so a missing model can be traced. | `script/eur/loaded/eurCasLoad.nut` | 2026-10-18 | restart |
| 7 | Custom settlement battle maps (Tharbad, Weathertop, Hobbiton, Bree, Minas Ithil, Osgiliath, Isengard and the rest) load again. EUR had the picker but never switched it on, so every siege used a generic engine map. **New in this pack: it was in the 1.4.2 pack but missing from the 2026-10-18 pack and from the first GitHub commit.** | `script/eur/battle/eursetBattleMapPKG.nut` | 2026-10-14 | restart |

Verification on 2026-10-22: `apply_hotfix.py --check` reports every file already applied on
BB1's install, and applying the patcher to a fresh copy of the stock 1.5 files reproduces his
seven files byte for byte. Fixes 1, 2 (Amon Hen model), 3 and 7 were seen working in-game or
in the game log (`[EUR cas]`, `[EUR maps]` lines). Fix 4 waits for a new Durin's Folk campaign.
Fix 5 is a one-line switch the mod's own comment describes as drawing-only.

### Install notes that belong with the pack

- `EUREX1.5M2EX.7z` is the ENGINE package in game-root layout (M2EX.exe of 2026-10-15, dlls,
  `data/`, `script/main.nut`, `mods/americas`...). Extract it into `Medieval II Total War\`,
  never into the mod folder. Unpacked into the mod it overwrites the mod's `main.nut` (no EUR
  menus, no presets, empty Missions button) and leaves a stray `data\descr_caps_ex.txt` that
  switches unit models to a text source the mod does not have: every unit fails to load and
  the game will not start. The 2026-10-15 engine is required anyway; the 2026-10-07 build caps
  factions at 31 and 1.5 has 34 ("Too many factions").
- `EUREX1.5.zip` is the mod overlay: extract INTO `mods\Divide_and_Conquer_EUR`. Its
  `.EUREX1.5\manifest.json` holds a sha256 for every mod file; `tools/manifest_diff.py` lists
  every file that differs from the release.
- EUREX README step 4: delete the 16 `data\text\*.txt.strings.bin` caches once after
  installing, so the new text files are rebuilt.
- Harmless log lines on this engine: `eur.battle.warbandSwordShield` fails to load
  ("attackDirection: unsupported field"), 75 `BuildingRegistry` duplicate-building asserts
  from `export_descr_buildings.txt`, `accent_types: wrong number of factions (32 vs 34)`
  from the baked sound cache.

### Known deviations on BB1's install that are NOT part of the pack

- `data/ui/battle.sd` differs from the 1.5 manifest: the engine rebuilt it from
  `battle.sd.xml` after that file was recovered on 2026-10-15. Harmless.
- Three `eopData/eopScripts/*.lua` files are the official EUR 2.08_5 hotfix (installed
  2026-10-11), unused by the M2EX engine.
- `eur_options.dat` and `script/eur/options/eurPresetDraft_legendary.nut` are BB1's own
  settings and saved Legendary preset.
- `script/eur/campaign/eurAragornJourneyFix.nut` still sits in the mod but 1.5 does not load
  it (1.5 ships its own `eur.campaign.aragornQuest`). Leftover, harmless.

### Reported in the EUREX Discord thread, triaged, not fixable from files

- Blue-Crag leader "with wolves": a Wolf Pack unit in his starting army (descr_strat).
- Kheledul dwarf-skinned rebel town and Celondim owned by Lindon: design of the new 1.5
  provinces (Celondim, Kheledul, Gondamon, Sarnur).
- Blue-Crag ports and walls: the `crags` culture reuses Gundabad's port models; its
  `huge_city` entry still points at the Bree model and `faction_variants/normans/` holds Bree
  and Hobbit models from the slot's old use. Only visible at top-tier goblin cities.
- Sarnur "uncapturable": one-tile-wide low-mountain corridor, single approach tile 67,407;
  nothing in the files forbids capture. Needs the reporter's exact symptom.
- Wrong portraits on ordinary generals: all nine cultures ship 201 portraits and EUR scripts
  never touch them. Needs a concrete example.

## 2026-10-18 - EUR_1.5_FixPack (superseded by 1.5.1)

Six files: fixes 1 to 6 above. The battle-map hook (fix 7) was left out by mistake.
Same day: Amon Hen custom model confirmed in-game (before/after composite on the Desktop);
monster debug outlines found and switched off; `[EUR cas]` per-town diagnostics added.

## 2026-10-16 - upgrade crest fix (`EUR_upgrade_crest_fix.zip`, one file)

`eurGeneralBGSwap.nut`: `checkcard()` threw on a stale remembered general after a battle or
reload and the engine dropped the frame handler for the session ("handler raised 10 ticks in a
row - dropped"). `render()` now guards the call and clears the stale selection. Also that day:
read the EUREX Discord thread; a second user had the same engine-in-mod-folder install trap.

## 2026-10-15 - EUREX 1.5 installed; recovery from the engine-package mistake

The engine 7z had been unpacked into the mod folder: 1748 engine files landed there, 99 of
them overwrote mod files. Done that night (log: `tools/mod_folder_cleanup_log_2026-10-15.txt`):

- Game root backed up to `E:\M2TW_backup_2026-10-15\game_root_before_1.5_engine` (1747
  files), then the 2026-10-15 engine installed into the root.
- 1649 stray engine files moved out of the mod to
  `E:\M2TW_backup_2026-10-15\engine_files_moved_out_of_mod_folder`; 171 emptied folders removed.
- 14 clobbered files restored from `EUREX1.5.zip` (main.nut, descr_strat, EDB, sound descr,
  shared/strategy .sd.xml, menu lnt...) and `script/manifest.nut` from `EUREX1.4.2.zip`.
- 83 clobbered baseline files that neither zip carries (sound descr files, aerial-map ground
  textures, radar_map2, weather_db, battle.sd.xml, descr_shortcuts...) extracted straight out of
  the EUR 2.08 Inno Setup installer with `tools/inno_extract83.py`, sha256-verified
  (list: `tools/recovered_83_baseline_files.txt`).
- The 16 `.strings.bin` text caches deleted per the EUREX README; `TATW.cfg` log level back to
  `* error` after diagnosis.

Result: game starts, 133 script modules load, only `warbandSwordShield` fails (engine side).
The 1.5 overlay wiped every 1.4.2 fix except the crest fix and the battle-map hook (1.5 does
not ship that file); the city-model and Amon Hen/Hobbiton fixes were re-done on 2026-10-18.
Obsolete after 1.5: the culture-conversion fix (1.5 disables automatic culture conversion),
the `descr_sounds_accents.txt` and `descr_flaming_projectiles.txt` edits (1.5 ships its own
versions), the Tharbad map swap (never tested, BB1's preference), the Aragorn journey hotfix
(1.5 has its own port).

## 2026-10-14 - EUR_M2EX_1.4.2_FixPack (`history/eurex-1.4.2/`, EUREX 1.4.2 only)

Eight files, drop-in, every original verified byte-identical to `EUREX1.4.2.zip` first:

- `main.nut` + `eurAragornJourneyFix.nut`: Aragorn journey hotfix (see 2026-10-12).
- `eursetBattleMapPKG.nut`: battle-map picker registered with the engine (fix 7 above). First
  confirmed via `[EUR maps]` log lines that day (Tharbad x2, Weathertop).
- `eurMapHelpers.nut`: Hobbiton key 134,386 -> 133,385, Bree 166,380 -> bree_a, Amon Hen ->
  model 11 (table only had a dead alias). Found by `tools/audit_assets.py` /
  `audit_unique_maps.py`, which read every town's real tile from `map_regions.tga`.
- `eurOptionsCustomization.nut`: "cities revert to generic" root cause under M2EX. BB1's saved
  Legendary preset turned on Automatic culture conversion; on M2EX that write re-stamps the
  strat model, and 23+ towns deliberately run on a foreign plan for their unique look. Rule
  added: never convert a custom-look town while its starting owner holds it; after conquest
  only the nine good/evil swap towns convert. Obsolete in 1.5.
- `eurCampaignTriggers.nut`: model stamp re-run on every campaign load (fix 1).
- `descr_sounds_accents.txt`: barrow_wights added to the English accent line (removed a
  "31 vs 33 factions" warning). Obsolete in 1.5.
- Left out on purpose: Tharbad map swap, `#flame_wheel` texture change (could not be proven a
  mod bug), AI garrison doubling for the Barrow Wights (design choice, options offered, nothing
  changed). An installer-script version of this pack was rejected by BB1 ("insane install
  directions") and deleted; packs are plain drop-in zips from then on.

## 2026-10-12 - Aragorn journey hotfix (`history/aragorn-journey-fix-2026-10-12/`)

Under M2EX the EDCT region triggers never advanced the "Aragorn" trait, so the RPG chain stuck
at level 1 and only the turn-5 "go to Bree" popup fired. `eurAragornJourneyFix.nut` re-implements
the six region steps on CharacterTurnStart (covers the split Bree regions) and `main.nut` loads
it. Verified by BB1 on 2026-10-12 ("it seems to be working now normally"); removed and reinstated
on 2026-10-14 at his request. Superseded by 1.5's own `eur.campaign.aragornQuest`.
