# EUREX 1.5 hotfix 1 - what it changes and where it came from

Target: EUREX 1.5 overlay on Divide and Conquer EUR, M2EX engine build of 2026-10-15.
Source: the fixes BB1 applied on the Windows rig between 2026-10-15 and 2026-10-19
(Claude Code sessions "Mtw2 not starting with euec launcher", "REX/M2eX mods in develop",
"Amon Hen, upgrade icon, pathfinding"). None of this was in a git repository before;
the drop-in zip lived at `C:\Users\BigBoss1\Desktop\EUR_1.5_FixPack_upload\`.

## File patches (applied by `apply_hotfix.py`)

| # | File | Bug | Root cause | Takes effect |
|---|------|-----|------------|--------------|
| 1 | `script/helper/eurCampaignTriggers.nut` | Custom city models (Bree, Amon Hen, every custom-look town) go generic in the second campaign loaded or started in one game session. Upgrade and mode windows looked absent in that campaign too. | The M2EX script VM survives leaving a campaign. `campaignBoot` stamped the strat CAS models only once per process (`cas_standalone_set_already` guard), so every later campaign in the session kept the engine defaults. Now `setCasStandalone()` runs on every `campaignMapLoaded`; `loadStratCAS()` is retried inside try/catch. Adds `[EUR boot]` log lines (newGameStart, newGameLoaded, campaignMapLoaded, campaignBoot start/done, exitToMenu, unloadCampaign) to `system.log.txt`. | Restart game |
| 2 | `script/eur/eru/eurMapHelpers.nut` | Amon Hen shows the generic round town; Hobbiton and Bree custom battle maps never trigger. | The 1.5 map renamed `eursett_15` to `Amon_Hen` and moved Hobbiton to tile 133,385; the custom-map table still keyed the old name and tile, and Bree (166,380) had no entry. `["Amon_Hen"] = 11` added, `eursett_15` kept as alias for older saves. The team's own `Eru/Mistrand/amon_hen.cas` model (square stone platform) now loads. | Restart game |
| 3 | `script/eur/upgrades/eurGeneralBGSwap.nut` | Unit-upgrade / bodyguard-swap crest (faction card on the HUD when a unit is selected) disappears for the rest of the session. | `checkcard()` throws "index 'record' does not exist" on a stale `::EUR.temp_fort_char` after a battle or reload; M2EX then drops the onFrame handler ("handler raised 10 ticks in a row - dropped"). `render()` now wraps `syncLeftWindows()` + `checkcard()` in try/catch, clears the stale selection and hides the buttons. | Restart game |
| 4 | `data/world/maps/campaign/imperial_campaign/campaign_script.txt` | Reclaiming Moria quest (Durin's Folk, Mirkwood southern route): arrow target shows "Restricted area". | The 1.5 map added `Emyn_Nu_Fuin_Province` in the Mountains of Mirkwood. The quest's step-2 pointer (327,392) lies inside it and legs 2-3 and 3-4 cross it, but the three `restrict_clickable_area` whitelists never named it. Province added to all three lines (one also gains `Elven_Mirkwood_Province`). | NEW campaign only |
| 5 | `script/eur/battle/monsterAbilityConfig.nut` | Monster area attacks (trolls, Balrog, Mumakil) draw green shapes on the battlefield. | `debugAoeOutline = true` shipped in 1.5. Set to `false`. Drawing only, no damage or geometry change. | Restart game |
| 6 | `script/eur/loaded/eurCasLoad.nut` | Diagnostic only. | Logs `[EUR cas] <town> tile x,y model N` per custom town and `[EUR cas] not found: <name>` when a table entry has no settlement, so a missing model can be traced from `system.log.txt`. | Restart game |

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

## Not included

- Tharbad east/west battle-map change (2026-10-13, three scripts, never tested) and the
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
