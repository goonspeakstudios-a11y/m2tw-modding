# EUREX 1.5 hotfix 1 - what it changes and where it came from

Target: EUREX 1.5 overlay on Divide and Conquer EUR, M2EX engine build of 2026-10-15. Seven file patches.
Source: fixes made on BB1's rig on 2026-10-14 (city-model stamp, Amon Hen and Hobbiton keys, battle-map hook; first made for 1.4.2), 2026-10-16 (crest) and 2026-10-18 (re-port onto 1.5, Moria route, monster outlines, diagnostics); hardened 2026-10-22 for the 1.5.2 pack
(Claude Code sessions "Mtw2 not starting with euec launcher", "REX/M2eX mods in develop",
"Amon Hen, upgrade icon, pathfinding"). None of this was in a git repository before;
the drop-in zip lived at `C:\Users\BigBoss1\Desktop\EUR_1.5_FixPack_upload\`.

## File patches (applied by `apply_hotfix.py`)

| # | File | Bug | Root cause | Takes effect |
|---|------|-----|------------|--------------|
| 1 | `script/helper/eurCampaignTriggers.nut` | Custom city models (Bree, Amon Hen, every custom-look town) go generic in the second campaign loaded or started in one game session. | The M2EX script VM survives leaving a campaign. `campaignBoot` stamped the strat CAS models only once per process (`cas_standalone_set_already` guard), so every later campaign in the session kept the engine defaults. Now `setCasStandalone()` runs on every `campaignMapLoaded` (engine doc: that event fires every time the strat map opens, including the return from a battle, and anything stamped onto a model has to be restamped there); `loadStratCAS()` is retried inside try/catch. 1.5.2: `Amon_Hen` = 11 and the Hobbiton 133,385 / Bree 166,380 battle-map keys are re-forced right after the stock Carn Dum / Skarhald re-force, because `helper/eurSaveLoadValues.nut` saves both tables and replaces the defaults wholesale on load, so saves made before patch 2 would never get it. Diagnostics: `[EUR boot]` lines for campaignMapLoaded, campaignBoot start/done and newGameLoaded. The 1.5.1 pack also logged exitToMenu, unloadCampaign and newGameStart; those run before `::game` exists and wrote `[script.phase] [error] out of phase: '?.log'` lines, so 1.5.2 drops them. | Restart game |
| 2 | `script/eur/eru/eurMapHelpers.nut` | Amon Hen shows the generic round town; Hobbiton and Bree custom battle maps never trigger. | The 1.5 map renamed `eursett_15` to `Amon_Hen` and moved Hobbiton to tile 133,385; the custom-map table still keyed the old name and tile, and Bree (166,380) had no entry. `["Amon_Hen"] = 11` added, `eursett_15` kept as alias for older saves. The team's own `Eru/Mistrand/amon_hen.cas` model (square stone platform) now loads. On its own this table only reaches campaigns started after installing; patch 1 carries the three keys into older saves (1.5.2). `bree_a` may still be ignored by the engine: its package is tagged for the normans plan while Bree runs on the Bree_Folk plan, and no Bree siege has been logged yet. | Restart game |
| 3 | `script/eur/upgrades/eurGeneralBGSwap.nut` | Unit-upgrade / bodyguard-swap crest (faction card on the HUD when a unit is selected) disappears for the rest of the session. | `checkcard()` throws "index 'record' does not exist" on a stale `::EUR.temp_fort_char` after a battle or reload; M2EX then drops the onFrame handler ("handler raised 10 ticks in a row - dropped"). `render()` now wraps `syncLeftWindows()` + `checkcard()` in try/catch, clears the stale selection and hides the buttons. | Restart game |
| 4 | `data/world/maps/campaign/imperial_campaign/campaign_script.txt` | Reclaiming Moria quest (Durin's Folk, Mirkwood southern route): arrow target shows "Restricted area". | The 1.5 map added `Emyn_Nu_Fuin_Province` in the Mountains of Mirkwood. The quest's step-2 pointer (327,392) lies inside it and legs 2-3 and 3-4 cross it, but the three `restrict_clickable_area` whitelists never named it. Province added to all three lines (one also gains `Elven_Mirkwood_Province`). | NEW campaign only |
| 5 | `script/eur/battle/monsterAbilityConfig.nut` | Monster area attacks (trolls, Balrog, Mumakil) draw green shapes on the battlefield. | `debugAoeOutline = true` shipped in 1.5. Set to `false`. Drawing only, no damage or geometry change. | Restart game |
| 6 | `script/eur/loaded/eurCasLoad.nut` | Map props (stone trolls, Stone of Erech, Smaug and the rest of `strat_cas_standalone`) would be drawn again after every battle once patch 1 runs on every campaign-map load. | Engine doc for `drawAt`: calling it again with the same number draws the model in both places. 1.5.2 calls `::game.models.stopDrawing(modelID)` for every prop first (engine doc: take down every model drawn under this number, at every tile), inside try/catch so a missing call falls back to the old behaviour. Prop model numbers (1, 3-7, 10, 12) never overlap the settlement model numbers. Diagnostics: `[EUR cas] <town> tile x,y model N` per custom town and `[EUR cas] not found: <name>` when a table entry has no settlement. | Restart game |
| 7 | `script/eur/battle/eursetBattleMapPKG.nut` | No EUR custom settlement battle map ever loads (Tharbad, Weathertop, Hobbiton, Bree, Minas Ithil, Osgiliath, Isengard...): every siege plays on a generic engine map. | EUR defines the picker `::EUR.onSelectWorldpkgdesc` (keyed by defender tile "x,y" in `::EUR.custom_maps`) but never registered it with the M2EX engine event `selectWorldpkgdesc`. A wrapper now registers it, returns null when the engine's choice stands, and logs `[EUR maps] tile x,y engine=... -> ...` to `system.log.txt`. The fix dates from 2026-10-14 (EUREX 1.4.2), survived the 1.5 overlay because 1.5 does not ship this file, and was left out of the 10-18 pack and the first repo commit by mistake. Confirmed firing on the Oct-15 engine on 2026-10-16 (tile 188,333 -> South Tharbad). | Restart game |

## Install-level fix (not a file patch; see README.txt)

`EUREX1.5M2EX.7z` is the engine package in game-root layout (M2EX.exe Oct-15 build, dlls,
`data/`, `script/main.nut`, `mods/americas`...). It goes into `Medieval II Total War\`, never
into the mod folder. Unpacked into the mod it overwrote 99 mod files (main.nut, descr_strat,
EDB, 83 baseline files) and dropped a stray `data/descr_caps_ex.txt` in the mod scope, which
set `model_battle_source = text`; the engine then read the stray vanilla
`descr_model_battle.txt` instead of `battle_models.modeldb` and every mod unit failed with
"Could not find soldier battle model" (fatal in unit_db). The Oct-15 engine is required
regardless: the Oct-7 build caps factions at 31 and 1.5 ships 34 ("Too many factions").
`apply_hotfix.py` warns when `data/descr_caps_ex.txt` is present in the mod folder.

The same trap hit a second user in the EUREX Discord thread (game starts, no presets, no EUR
menu options, empty Missions button = EUR scripts not loading because the engine's
`script/main.nut` replaced the mod's).

## Verification without the rig

The rig was unreachable when this repo was built, so the hunks were checked against the
`diff` outputs the rig sessions recorded right after each patch (backup vs patched file,
2026-10-16 21:14 and 2026-10-19 01:58, 05:15, 05:35). Every added and removed line in those
diffs matches the hunks in `apply_hotfix.py` line for line, for all six files (the seventh, the battle-map hook, was added on the rig on 2026-10-22). Encodings on
the rig: eurMapHelpers.nut, eurCampaignTriggers.nut, campaign_script.txt and
monsterAbilityConfig.nut are CRLF (campaign_script and eurMapHelpers UTF-8 without BOM in
`file` output), eurGeneralBGSwap.nut is LF; the patcher preserves whichever it finds.
`apply_hotfix.py --check` on the rig reported `already-applied` for all seven on 2026-10-22, and applying
the patcher to a fresh copy of the stock 1.5 files reproduced the rig's seven files byte for byte.

## 1.5.2 hardening (2026-10-22)

A seven-agent review of the 1.5.1 files against stock 1.5 found no syntax or logic errors in the seven patches and three things to fix before a stable post:

- Three diagnostic `::game.log` calls (exitToMenu, unloadCampaign, newGameStart) run in the DataBuild phase and wrote an `out of phase` error line on every return to the menu and every new campaign (seen in `system.log.txt` on 2026-10-22 at 14:38, 14:44, 14:49 and 15:04). Removed.
- Patch 2 never reached saves made before it, because the save carries its own copy of the two tables. Patch 1 now re-forces the three keys.
- Patch 1 re-draws the map props after every battle; patch 6 now takes them down first.

Checks: 11 unit tests pass; `apply_hotfix.py` on a clean copy of the stock 1.5 files reproduces the seven 1.5.2 files byte for byte and a second run reports all seven already applied. Not yet seen in game: the re-force on an older save, the prop take-down, the absence of the out-of-phase lines. On an install that already carries the 1.5.1 pack the patcher reports `mismatch` for eurCampaignTriggers.nut and `pending` for eurCasLoad.nut; the drop-in zip overwrites both, so use the zip there.

## Not included

- Tharbad: BB1's own choice of the original Tharbad map for both river banks (2026-10-13, three scripts; map loading confirmed in the log on 2026-10-14, the east/west deployment test never reported). A taste change, not a bug fix. Also the
  Aragorn journey hotfix `eurAragornJourneyFix.nut` (2026-10-12): both pre-date 1.5, which
  ships its own `eur.campaign.aragornQuest`; the 1.5 overlay wiped them and they were not
  re-ported.
- Culture-conversion fix from 1.4.2: obsolete, 1.5 sets `automaticCultureConversionEnabled = false`.
- `descr_sounds_accents.txt` "32 vs 34 factions" warning: file lists all 34, the number comes
  from the baked sound cache (`data/sounds/*.dat/idx`); harmless, untouched.
- Known 1.5 load failure `eur.battle.warbandSwordShield` ("attackDirection: unsupported
  field" on the Oct-15 engine): the loader skips the module; harmless.

## Reported, triaged, not bugs or not reproducible from files

- Blue-Crag leader "with wolves": a Wolf Pack unit in his starting army in descr_strat.
- Kheledul dwarf-skinned rebel town, Celondim owned by Lindon: design choices for the new 1.5
  provinces (Celondim, Kheledul, Gondamon, Sarnur carved from Mithlond and Nan-i-Naugrim).
- Blue-Crag ports and walls: same `port_orc` models as Gundabad's culture. Real leftover: crags
  `huge_city` still points at `northmen_t6_huge_city` (Bree) and `faction_variants/normans/`
  holds Bree and Hobbit models from the slot's old use. Only visible at top-tier goblin cities.
- Sarnur "uncapturable": reachable only through a one-tile-wide low-mountain corridor 27 tiles
  north of Thorin's Halls, single approach tile 67,407; nothing in the files forbids capture.
- Wrong portraits on ordinary generals: all nine cultures ship 201 general portraits and the
  EUR scripts never touch generic portraits. Needs a concrete example.

## Backups the rig still carries

`.bak_15fix`, `.bak_moriaroute`, `.bak_before_upgradefix`, `.bak_aoe`, `.bak_casdiag` next to
the patched files; game root before the engine swap in `E:\M2TW_backup_2026-10-15\`.
