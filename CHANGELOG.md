# Changelog - EUR fix packs for Divide and Conquer EUR on the M2EX engine

Every entry is a change made on BB1's machine to the mod folder
`mods\Divide_and_Conquer_EUR` (or the game root). Dates are the day the change was made.
"Pack" means the drop-in zip a player extracts into `mods\` and overwrites.
Technical detail per fix (root cause, exact hunks) lives in
`hotfixes/eurex-1.5-hotfix-1/CHANGES.md`; the exact diffs against stock 1.5 are in
`eurex-1.5/diffs/`.

## 1.5.3 - 2026-10-22 - caps follow the engine army limit (`EUR_1.5.3_FixPack.zip`, NOT YET BUILT)

Everything from 1.5.2 plus five more files. No change in a normal 20-unit campaign: every edited
line reads the engine's live army limit, which is 20 unless the campaign was started in M2EX's
40-unit army mode. This is the groundwork the separate "EUR 40 units" add-on builds on, so the
two packs can be installed in either order.

| # | What a player sees | File | Since | Needs |
|---|---|---|---|---|
| 8 | AI free garrisons, global recruitment deliveries, unit upgrades, leader/heir bodyguard swaps and spawned generals stop at the campaign's real army limit instead of a hard 20. | `script/eur/garrisons/eurGarrisons.nut`, `script/eur/global_recruitment/eurGlobalRecruitment.nut`, `script/eur/upgrades/eurGeneralBGSwap.nut`, `script/eur/upgrades/eurLeaderHeirSwap.nut`, `script/eur/campaign/eurSpawnGeneral.nut`, helpers in `script/helper/eurCampaignTriggers.nut` | 2026-10-22 | restart |
| 9 | `script/main.nut` gains one block that loads optional add-on modules from `script/eur40/` when that folder exists. Hunk patch on the mod's own 1.5 file; the module list is untouched. | `script/main.nut` | 2026-10-22 | restart |

## 1.5.2 - 2026-10-22 - stable pack for EUREX 1.5 (`EUR_1.5.2_FixPack.zip`)

Requires Divide and Conquer EUR 2.08 with the EUREX 1.5 overlay and the M2EX engine build of
2026-10-15. Does not apply to EUREX 1.4.2 (that pack is under `history/`).

Seven files. Install: extract the zip into `mods\`, overwrite, restart the game. It replaces
the 1.5.1 pack; extract it over the top.

| # | What a player sees | File | Since | Needs |
|---|---|---|---|---|
| 1 | Custom city models (Bree, Amon Hen, every custom-look town) keep their look in the second campaign loaded or started in one game session. | `script/helper/eurCampaignTriggers.nut` | 2026-10-14, re-done for 1.5 on 2026-10-18, hardened 2026-10-22 | restart |
| 2 | Amon Hen shows its own stone-platform model again. Hobbiton's battle map is keyed to the tile the 1.5 map uses. Bree gets its own map entry, though the engine may still choose the generic one. **New in 1.5.2: this now reaches saves made before the fix.** | `script/eur/eru/eurMapHelpers.nut` + `eurCampaignTriggers.nut` | 2026-10-14, re-done 2026-10-18, save support 2026-10-22 | restart |
| 3 | The unit-upgrade / bodyguard crest no longer disappears for the rest of the session after a battle or reload. | `script/eur/upgrades/eurGeneralBGSwap.nut` | 2026-10-16 | restart |
| 4 | Reclaiming Moria quest (Durin's Folk, Mirkwood route): the arrow target no longer says "Restricted area". | `data/world/maps/campaign/imperial_campaign/campaign_script.txt` | 2026-10-18 | new campaign to be sure |
| 5 | No more green debug shapes under monster area attacks (trolls, Balrog, Mumakil). | `script/eur/battle/monsterAbilityConfig.nut` | 2026-10-18 | restart |
| 6 | Map props (stone trolls, Stone of Erech, Smaug...) are taken down before being drawn again, so they no longer pile up after every battle. The game log also names every custom town model it applies. | `script/eur/loaded/eurCasLoad.nut` | diagnostics 2026-10-18, prop fix 2026-10-22 | restart |
| 7 | Custom settlement battle maps (Tharbad, Weathertop, Hobbiton, Minas Ithil, Osgiliath, Isengard and the rest) load again. EUR had the picker but never switched it on, so every siege used a generic engine map. **Missing from the 1.5.1 pack by mistake.** | `script/eur/battle/eursetBattleMapPKG.nut` | 2026-10-14 | restart |

### What changed from 1.5.1 to 1.5.2

- **Battle-map picker added.** It was in the 1.4.2 pack and live on BB1's install the whole
  time, because 1.5 does not ship that file. Players on stock 1.5 never had it.
- **Error lines removed.** Three diagnostic log calls ran before the game was ready and wrote
  an "out of phase" error line on every return to the menu and every new campaign. They were
  seen in `system.log.txt` on 2026-10-22.
- **Fix 2 now reaches older saves.** The save carries its own copy of the town tables and
  replaced the fixed defaults on load. The three keys are now re-applied after loading, the same
  way the mod already does for Carn Dum and Skarhald.
- **Map props cannot stack.** Fix 1 re-applies models every time the campaign map opens, and
  the engine opens it after every battle. Each prop is now taken down before it is drawn again.

- **No fix can be dropped again.** BB1's rule from 2026-10-22: every hotfix always includes
  every fix. The pack builder now checks a fix list that records every pack ever made. It refuses
  to build when a fix from an earlier pack is missing and was not retired with a reason. It also
  refuses when the install has a changed file nobody put in the pack or excused. Run against BB1's
  real install, it flags exactly the 14 files that differ from the 1.5 release, the siege-map file
  among them, so it would have stopped the 1.5.1 mistake. The four retired fixes (Aragorn loader,
  Aragorn module, culture-conversion guard, Barrow Wights accents) each carry their reason.

### Verification on 2026-10-22

- Seven independent reviews found no syntax or logic error in the 1.5.1 changes. Their findings
  are the four items above.
- The 21 unit tests pass. Ten of them cover the never-drop rule, including a replay of the 1.5.1
  mistake.
- Applying the patcher to a clean copy of the stock 1.5 files reproduces the seven 1.5.2 files
  byte for byte. A second run reports every file already applied.
- Seen working in-game or in the game log before today: fix 1 (second campaign re-stamped), the
  Amon Hen model, fix 3 (BB1 upgraded Dunedain Wardens to Armsmen) and fix 7 (Tharbad, Weathertop).
- **Not yet seen in game:** the 1.5.2 additions (older-save re-apply, prop take-down, no more
  out-of-phase lines), fix 4 (needs a Durin's Folk campaign), the Hobbiton and Bree maps in a
  siege. Fix 5 is a one-line switch that the mod's own comment calls drawing-only.

### Install notes that belong with the pack

- **Base first.** Use EUR 2.08 with the official EUR 2.08_5 hotfix (2026-10-11). That hotfix
  zip also drops a stray `eopData\eopScripts\eur\campaign\eurOverrides (8).lua` that is never
  loaded; it can be deleted.
- **Folder name.** The mod folder must be named exactly `Divide_and_Conquer_EUR`.
- **Two downloads, two places.** `EUREX1.5.zip` is the mod overlay; extract it INTO
  `mods\Divide_and_Conquer_EUR`. `EUREX1.5M2EX.7z` is the ENGINE (M2EX.exe of 2026-10-15,
  dlls, `data\`, `script\main.nut`, `mods\americas`...); extract it into
  `Medieval II Total War\`, never into the mod folder. Unpacked into the mod it replaces the
  mod's `main.nut` (no EUR menus, no presets, empty Missions button). It also leaves a stray
  `data\descr_caps_ex.txt` that switches unit models to a text source, so every unit fails and
  the game will not start. The 2026-10-15 engine is needed anyway, because the 2026-10-07 build
  caps factions at 31 and 1.5 has 34.
- **EUREX README step 4.** Delete the files listed in `.EUREX1.5\deleted_files.txt`: seven
  `data\text\*.txt.strings.bin` caches and two old AI scripts. The game rebuilds the caches.
  BB1's install is also missing 16 other `.strings.bin` caches for an unrecorded reason, which
  is harmless.
- **Keep the Moria fix.** Do not copy a `campaign_script.txt` from `Activate\KD_SKIP`,
  `Activate\SPEED` or `Activate\NORMAL` over the live one afterwards; those still carry the
  old Moria lists.
- **No Steam "Verify" needed.** The fire and smoke textures live inside the base game's
  `packs\data_*.pack` files.
- **Harmless log lines.** `eur.battle.warbandSwordShield` fails to load ("attackDirection:
  unsupported field"). There are 75 duplicate-building asserts from
  `export_descr_buildings.txt`. "accent_types: wrong number of factions (32 vs 34)" comes from
  the baked sound cache.

### On BB1's install but not part of the pack

- `data/ui/battle.sd` differs from the 1.5 manifest. The engine rebuilt it from `battle.sd.xml`
  after that file was recovered on 2026-10-15.
- Three `eopData/eopScripts/*.lua` files are the official EUR 2.08_5 hotfix, unused by M2EX.
- `eur_options.dat` and `script/eur/options/eurPresetDraft_legendary.nut` are BB1's own
  settings and saved Legendary preset.
- `script/eur/campaign/eurAragornJourneyFix.nut` is still in the mod, but 1.5 loads its own
  `eur.campaign.aragornQuest` instead. Leftover and harmless.
- About 24 `.bak*` backups sit next to patched files. The 1.5 undo set is `.bak_15fix`,
  `.bak_moriaroute`, `.bak_before_upgradefix`, `.bak_aoe` and `.bak_casdiag`. The 1.4.2-era ones
  (`.bak_tharbad`, `.bak_cas`, `.bak_culture`, `.bak_amonhen`, `.bak_wheel`, `.bak_wights`,
  `.bak_hook`, `main.nut.bak_aragorn2`) are stale restore points.

### Reported in the EUREX Discord thread, triaged, not fixable from files

- **Blue-Crag leader "with wolves".** A Wolf Pack unit is in his starting army.
- **Kheledul dwarf-skinned rebel town, Celondim owned by Lindon.** Both are the design of the
  new 1.5 provinces.
- **Blue-Crag ports and walls.** The `crags` culture reuses Gundabad's port models. Its
  `huge_city` entry still points at the Bree model. Only visible at top-tier goblin cities.
- **Sarnur "uncapturable".** It sits behind a one-tile-wide mountain corridor and nothing in
  the files forbids capture. The reporter's exact symptom is needed.
- **Wrong portraits on ordinary generals.** EUR scripts never touch generic portraits. A
  concrete example is needed.

## 1.5.1 - 2026-10-18 - `EUR_1.5.1_FixPack.zip` (superseded by 1.5.2)

Six files: fixes 1 to 6 in their 2026-10-18 form. Fix 7 was left out by mistake. The
diagnostics in fix 1 wrote out-of-phase error lines. Same day: Amon Hen custom model confirmed
in-game (before/after picture on the Desktop), monster debug outlines found and switched off,
per-town `[EUR cas]` log lines added.

## 2026-10-16 - upgrade crest fix (`EUR_upgrade_crest_fix.zip`, one file)

`checkcard()` in `eurGeneralBGSwap.nut` threw on a stale remembered general after a battle or
reload. The engine then dropped the frame handler for the session ("handler raised 10 ticks in a
row - dropped"). `render()` now guards the call and clears the stale selection. BB1 confirmed it
by upgrading a unit. Also that day: read the EUREX Discord thread, where a second user had the
same engine-in-mod-folder install trap.

## 2026-10-15 - EUREX 1.5 installed; recovery from the engine-package mistake

The engine 7z had been unpacked into the mod folder: 1748 engine files landed there and 99 of
them overwrote mod files. That night (log: `tools/mod_folder_cleanup_log_2026-10-15.txt`):

- The game root was backed up to `E:\M2TW_backup_2026-10-15\game_root_before_1.5_engine` (1747
  files). Then the 2026-10-15 engine was installed into the root.
- 1649 stray engine files were moved out of the mod to
  `E:\M2TW_backup_2026-10-15\engine_files_moved_out_of_mod_folder`, and 171 emptied folders
  were removed.
- 14 overwritten files were restored from `EUREX1.5.zip`: main.nut, descr_strat, EDB, sound
  files, shared/strategy .sd.xml, the menu lnt and others. `script/manifest.nut` came from
  `EUREX1.4.2.zip`.
- 83 overwritten base files that neither zip carries were pulled straight out of the EUR 2.08
  installer with `tools/inno_extract83.py` and checked by hash. They are sound files, aerial-map
  ground textures, radar_map2, weather_db, battle.sd.xml and descr_shortcuts
  (`tools/recovered_83_baseline_files.txt`).
- Two old `.strings.bin` caches were moved out. Trace logging was switched on in `TATW.cfg` for
  the diagnosis and back to `* error` once the game ran.

Result: the game starts and 133 script modules load. Only `warbandSwordShield` fails, on the
engine side. The 1.5 overlay wiped every 1.4.2 fix except the battle-map picker (1.5 does not
ship that file). The city-model and Amon Hen/Hobbiton fixes were re-done on 2026-10-18.

## 2026-10-14 - `EUR_M2EX_1.4.2_FixPack.zip` (`history/eurex-1.4.2/`, EUREX 1.4.2 only)

Eight files, drop-in. Every original was checked byte-identical to `EUREX1.4.2.zip` first.

- **Aragorn journey hotfix.** `main.nut` + `eurAragornJourneyFix.nut`; see 2026-10-12.
- **Battle-map picker.** `eursetBattleMapPKG.nut` registers the picker with the engine (fix 7
  above). First confirmed by log lines that day for Tharbad and Weathertop.
- **Town keys.** `eurMapHelpers.nut`: Hobbiton key 134,386 to 133,385, Bree 166,380 to bree_a,
  and Amon Hen to model 11 (the table only had a dead alias). Found with
  `tools/audit_assets.py` and `audit_unique_maps.py`, which read every town's real tile from
  `map_regions.tga`.
- **Culture conversion.** `eurOptionsCustomization.nut`: BB1's saved Legendary preset turned on
  Automatic culture conversion, which re-stamps the town model on M2EX. Rule added: never
  convert a custom-look town while its starting owner holds it. Obsolete in 1.5, which disables
  the option.
- **Re-stamp every load.** `eurCampaignTriggers.nut`: the model stamp re-runs on every campaign
  load (fix 1).
- **Barrow Wights voices.** `descr_sounds_accents.txt`: barrow_wights added to the English
  accent line. 1.5 ships its own file.
- **Kept off the pack but applied on BB1's install, all wiped by 1.5:**
  - Tharbad: BB1's choice of the original map for both river banks. Map loading was confirmed
    in the log; the east/west deployment test was never reported. It is a taste change, not a
    bug.
  - The `#flame_wheel` fire-texture swap. The original texture is inside the base-game packs,
    so this was never a bug.
- **Looked at, nothing changed.** Barrow Wights AI garrison doubling is the mod team's design.
- **Packaging rule.** An installer-script version of this pack was rejected by BB1 ("insane
  install directions"). Packs are plain drop-in zips from then on.

## 2026-10-12 - Aragorn journey hotfix (`history/aragorn-journey-fix-2026-10-12/`)

Under M2EX the trait triggers tied to regions never advanced the "Aragorn" trait. The RPG chain
stuck at level 1 and only the turn-5 "go to Bree" popup fired.

- First try: the Bree step's region list in `export_descr_character_traits.txt` was widened to
  the new Combe/Archet/Trestlebridge regions. It had no effect, because those triggers never fire
  on M2EX. It was kept out of the pack and wiped by 1.5.
- The fix: `eurAragornJourneyFix.nut` re-implements the six region steps when a character
  starts a turn, and `main.nut` loads it. BB1 confirmed it the same day ("it seems to be
  working now normally").
- A free-movement test switch for Aragorn was on in BB1's copy until 2026-10-14.
- The fix was removed and reinstated on 2026-10-14 at BB1's request. It is superseded by 1.5's
  own `eur.campaign.aragornQuest`.
