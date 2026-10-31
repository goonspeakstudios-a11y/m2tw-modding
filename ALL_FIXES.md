# All fixes: EUR fix pack and GSO

This is every fix made for Divide and Conquer EUR on the M2EX engine, as of 2026-10-31. It covers two
projects:

- **EUR fix pack.** Fixes to EUR itself. The repo is `m2tw-modding`.
- **GSO (Grand Strategy Overhaul).** The 40-unit overhaul. The repo is `eur-40-units`, which is private.

Sources: the commits in both repos, `CHANGELOG.md`, `fix_registry.json`, `docs/KNOWN_BUGS.md`,
`tools/build_052.py`, and the Claude Code session logs from BB1, Oct 12 to Oct 30.

Status key:
- **Released** means the fix is in a pack that has been handed out.
- **Built** means the fix is in a finished zip on BB1 that has not been released.
- **Code only** means the fix is pushed but no pack has been built from it.
- **Retired** means the fix was dropped on purpose, with the reason given.

---

## Part 1 - EUR fix pack (`m2tw-modding`)

The current release is **1.5.2**. It is tagged `eur-1.5.2` on `main` and was staged on BB1 in
`Desktop\EUR_1.5.2_for_Google_Drive`. No session log confirms that it was uploaded.

### Fixes in 1.5.2 (released)

| # | What the player sees | Root cause | File | First fixed | Seen working in game |
|---|---|---|---|---|---|
| 1 | In the second campaign of a session, custom city models (Bree, Amon Hen and every custom-look town) show as generic towns | The M2EX script machine stays alive between campaigns, so a stamp-once guard skipped every campaign after the first. The models are now stamped on every campaign load. | `script/helper/eurCampaignTriggers.nut` | Oct 14. Redone for 1.5 on Oct 18 and hardened Oct 22 | Yes |
| 2 | Amon Hen shows the generic round town. The Hobbiton and Bree custom battle maps never load | The 1.5 map renamed `eursett_15` to `Amon_Hen` and moved Hobbiton to tile 133,385. Bree had no entry. From 1.5.2 the keys are re-applied after a save loads, so older saves get the fix too. | `script/eur/eru/eurMapHelpers.nut` and `eurCampaignTriggers.nut` | Oct 14, redone Oct 18, older saves Oct 22 | Amon Hen yes. Hobbiton and Bree not yet seen in a siege |
| 3 | The unit-upgrade and bodyguard crest disappears for the rest of the session | `checkcard()` threw an error on a general who was no longer valid, and the engine then dropped the frame handler. The call is now guarded and the stale selection is cleared. | `script/eur/upgrades/eurGeneralBGSwap.nut` | Oct 16 | Yes. Dunedain Wardens were upgraded to Armsmen |
| 4 | Reclaiming Moria quest (Durin's Folk, Mirkwood route): the arrow target says "Restricted area" | The new 1.5 province `Emyn_Nu_Fuin_Province` was missing from three `restrict_clickable_area` lists | `data/world/maps/campaign/imperial_campaign/campaign_script.txt` | Oct 18 | Not yet. It needs a new Durin's Folk campaign |
| 5 | Green shapes appear under monster area attacks (trolls, Balrog, Mumakil) | 1.5 shipped with `debugAoeOutline = true` | `script/eur/battle/monsterAbilityConfig.nut` | Oct 18 | One-line switch. The mod's own comment says it only affects drawing |
| 6 | Map props such as stone trolls, the Stone of Erech and Smaug pile up after every battle. The log does not name the town models it applies | The models are re-applied each time the campaign map opens, which happens after every battle. Each prop is now taken down before it is drawn again, and the log names each model. | `script/eur/loaded/eurCasLoad.nut` | Log lines Oct 18, prop fix Oct 22 | Log lines yes. Prop take-down not yet |
| 7 | Custom settlement siege maps (Tharbad, Weathertop, Hobbiton, Minas Ithil, Osgiliath, Isengard and others) never load | EUR defined the map picker but never registered it with the engine | `script/eur/battle/eursetBattleMapPKG.nut` | Oct 14. It was missing from 1.5.1 by mistake | Yes, at Tharbad and Weathertop |

Three more 1.5.2 changes have no number of their own:

- Three diagnostic log calls ran before the game was ready, and each wrote an "out of phase" error line.
  They were removed.
- The registry rule is now enforced: no fix can drop out of a later pack. `build_pack.py` refuses to
  build when a fix from any earlier pack is missing without a written reason.
- The install note is the fix for the Oct 15 "game won't start" problem. `EUREX1.5M2EX.7z` goes in the
  game root, never in the mod folder. A stray `data\descr_caps_ex.txt` inside the mod folder stops every
  unit model from loading.

### Fixes in 1.5.3 (code only, branch `eur40-caps`, pack not built)

| # | What the player sees | File |
|---|---|---|
| 8 | AI free garrisons, global recruitment deliveries, unit upgrades, leader and heir bodyguard swaps, and spawned generals stop at the campaign's real army limit instead of a fixed 20. A 20-unit campaign behaves the same. | `eurGarrisons.nut`, `eurGlobalRecruitment.nut`, `eurGeneralBGSwap.nut`, `eurLeaderHeirSwap.nut`, `eurSpawnGeneral.nut`, plus army-limit helpers in `main.nut` |
| 9 | `main.nut` loads optional add-on modules from `script/eur40/` when that folder exists, with `eur40Core` loaded first | `script/main.nut` |

To build the pack, run `apply_hotfix.py` against the live mod on BB1 first.

### Retired fixes (dropped on purpose)

| Fix | Was in | Reason |
|---|---|---|
| Aragorn journey hotfix (`eurAragornJourneyFix.nut` and its loader in `main.nut`), Oct 12 | Aragorn pack, 1.4.2 | EUREX 1.5 ships its own `eur.campaign.aragornQuest` |
| Culture-conversion guard (`eurOptionsCustomization.nut`) | 1.4.2 | 1.5 turns automatic culture conversion off, so the bug cannot happen |
| Barrow Wights accents line (`descr_sounds_accents.txt`) | 1.4.2 | The 1.5 file lists all 34 factions |

### Install-level fixes on BB1 (not shipped in the pack)

- **Oct 15, game would not start.** The engine 7z had been unpacked into the mod folder, which
  overwrote 99 mod files and left the stray `descr_caps_ex.txt`. The fix:
  - The Oct 15 engine was installed in the game root, with a backup on `E:\M2TW_backup_2026-10-15`.
  - 1,649 stray files were moved out and 15 files were restored from the zips.
  - 83 clobbered baseline files were pulled out of the Inno Setup installer and checked by SHA-256.
- **Oct 13, Tharbad east and west.** Both were set to use the original Tharbad map. It was never tested,
  and the 1.5 overlay wiped it.

---

## Part 2 - GSO / EUR 40 units (`eur-40-units`)

Release history:

| Version | Date | Where it is |
|---|---|---|
| 0.4.0-test | Oct 23 | Tag `v0.4.0-test` |
| 1.0.0 build | Oct 28 | Commit 7494e8c. This is the base the current zip is built from |
| 0.5.1 | before Oct 29 | ModDB, `gso-051-for-eurex-15` |
| 0.5.2 | Oct 29 | Branch `hud-any-resolution` holds the code and `tools/build_052.py`. The zip itself was built on BB1 in `E:\GSO_052` |

On Oct 30 the ModDB page carried the 0.5.2 title. The live file was still the 2.38 GB bundle that
includes Suber's engine. A slim, GSO-only zip is on hold because it has not been tested on EUREX 1.4.2.

### Fixes in the GSO 0.5.2 build (built, ModDB file not yet replaced)

| What the player sees | Known-bug # | How |
|---|---|---|
| No difficulty menu at campaign start, Bree invisible or untextured, buildings missing in settlements | 1, 2, 3 | The 98 EUR files that EUREX 1.5 expects from 1.4.2 (helpers, options, difficulty menu, upgrades, forts, AI) now ship in the zip. Players no longer need EUREX 1.4.2. |
| Bree, Hobbiton and Amon Hen problems, generic city models, the Moria route, siege maps | 2 | The EUR 1.5.2 fix pack (Part 1) is folded into the zip |
| Unit cards drawn over the minimap, and the battle UI squeezed on 16:10 and screens narrower than 1920 | 8, 9 | `eur40HudGeo.nut`: the campaign card rack fits between the side panels, and battle cards are centred and never outgrow their row. 1920x1080 is unchanged pixel for pixel, and 14 resolutions are tested. |
| Ten log warnings for every player from leftover multirun and editor lines in TATW.cfg | 7 | Those lines are removed from the shipped `TATW.cfg` |
| "Unknown escape \T" log error | 20 | EUR's typo `\n\The` in the Orthanc Guard text is corrected in GSO's copy of `export_units.txt` |
| Aragorn's quest counts only Bree | - | The Bree steps now count all four Breeland regions: Bree, Staddle, Combe and Trestlebridge |
| The uninstaller leaves banners and weather files behind | - | `GSO_Uninstall.bat` restores `descr_standards.txt` and the Aragorn quest, and removes the weather sounds and banner art |

The 0.5.2 build also adds new features: campaign weather (clouds, rain, snow, mist, mountain caps and
sound, which `NO_WEATHER=1` leaves out) and new army and town banners.

### Fixes in GSO 1.0.0 and earlier (in the 0.5.x zips)

| Fix | Commit | Date |
|---|---|---|
| Mordor's towns show the evil faith's pip, not the engine's Christian cross for "catholic" | 74fe288 | Oct 28 |
| Fair refill price. EUR priced a refill at recruit cost divided by the men left, so a worn-down unit paid several times the fair rate. It is now recruit cost divided by full strength, per man gained. | 96c60c3 | Oct 28 |
| Garrison window tooltips are shorter and plainer, in EUR's style | 48e5604 | Oct 28 |
| The battle bar's hourglass and speed slider are back on the 40-card HD battle HUD, which was missing its art | c95a900, f58ffe0 | Oct 28 |
| GSO switches on 40-unit armies and the HD interface itself, so players need no settings step | b21162e | Oct 28 |
| A garrison's first unit is on foot, except for horse peoples (Rohan) or a town with no foot unit | 10d31b6 | Oct 25 |
| EUR's paid replenishment no longer refills and bills Town Guard units before they stand down | 1d72a62 | Oct 25 |
| The siege that is ending is still counted when the endSiege event fires, so the merge reconcile runs on time | 84879e0 | Oct 25 |
| Garrison merges are handled. When the engine folds garrison and recruited men together, the men are sorted back at the siege's end, and only real garrison dead come off the town's people. In game, 77 men were sent home and 38 returned. | 884d1bb | Oct 25 |
| Garrison units are named "<Town> Town Guard - <Unit>". The older " Garrison " tag clashed with EUR's own units. | 5190d53, 9c24b74 | Oct 24 to 25 |
| The upkeep refund follows the engine's free-slot rule and is capped, so the refund can no longer pay out free gold. Before this, Belfalas was refunded 385, Forochel 680 and Cerin Amroth 300. | f30da8b | Oct 24 |
| The town watch uses the faction's own militia, and no muster opens with a lone war machine. Forochel raises Iron Hills Mattocks, not a lone Dwarven Ballista. | f30da8b | Oct 24 |
| EUR's hand-written garrison lists are blocked at the functions, not at the option | e8a5044 | Oct 24 |
| The 0.4.2 garrison module failed to compile because Quirrel forbids `delete`. The lint now rejects it. | e05ef65 | Oct 24 |
| Garrison units are gated on ownership and the live recruit capabilities, and only upkeep that was actually billed is refunded | d8f761d | Oct 24 |
| Quirrel compile fixes (regexp, reserved words, `find` to `indexof`), with lint checks over every module | 2a99285 | Oct 23 |
| On defeat the dead levy is not refunded, and nothing else is taken | 5c0bd6a | Oct 23 |
| No Mumak garrisons. The beast table keeps trolls only. | 22a4bef | Oct 23 |

### Still open in GSO (from `KNOWN_BUGS.md`, Oct 29, updated for 0.5.2)

| # | Bug | Status |
|---|---|---|
| 6 | GSO's `TATW.cfg` overwrites the player's video settings | Open |
| 10 | Stray textures left of the faction icon | Open, cause unknown |
| 11 | Free-upkeep garrison units lost their blue cards | Open. It is display only, and the money is correct |
| 12 | No description on buildings that feed the garrison | Open. Branch `garrison-tooltips` |
| 13 | Kingsfell fort is present with upkeep 1470 | Open. It is a leftover from Suber's test |
| 14 | The Dunedain fort economy does nothing | Work in progress |
| 15 | Several AI armies besiege one city | Open question |
| 16 | Low FPS zoomed in on detailed units in big battles | Open. The multicore "Fast Sim" research is on branch `banners-test` |
| 17 | `warbandSwordShield` attackDirection warning | Open and harmless |
| 18 | Out-of-phase `?.campaign` and `?.log` log errors | Open in GSO. EUR fix pack 1.5.2 removed its own three |
| 19 | "no general unit for faction(scripts)" | Open |
| 21 | 75 unit-ownership mismatches in `export_descr_buildings` | Open and harmless |
| 22 | accent_types count 32 vs 34 | Open and harmless. It comes from the baked sound cache |
| - | Treasury fell from -7,643 to -17,199 in one turn (Oct 25) | Open. The economy check has not been done |
| - | The garrison window shows 152 men on a 150-man unit | Open |

### Not fixed, triaged as design or unconfirmed (EUREX Discord, Oct 18)

- **Blue-Crag leader "with wolves".** A Wolf Pack unit is in his starting army.
- **Kheledul and Celondim.** Their skin and ownership are the design of the new 1.5 provinces.
- **Blue-Crag ports and walls.** The ports reuse Gundabad's orc ports, and `huge_city` still points
  at the Bree model.
- **Sarnur "uncapturable".** Nothing in the files forbids capturing it. The reporter's exact symptom is
  needed.
- **Wrong portraits on generic generals.** EUR scripts never touch them. A concrete example is needed.

---

## Where each piece lives

| Repo / place | Branch or path | Contents |
|---|---|---|
| `m2tw-modding` | `main`, tag `eur-1.5.2` | EUR fix pack 1.5.2, patcher, registry, overlay, diffs, history, tools |
| `m2tw-modding` | `eur40-caps` | 1.5.3 code (fixes 8 and 9) |
| `m2tw-modding` | `ccr-6ca53ed6-qs2g86` | Hotseat quick-pass tool |
| `eur-40-units` | `foundation` | Garrison and HUD work through Oct 25 |
| `eur-40-units` | `main` | GSO up to the 1.0.0 build and the Oct 28 fixes |
| `eur-40-units` | `hud-any-resolution` | GSO 0.5.2: any-resolution HUD, Aragorn Breeland and the build script |
| `eur-40-units` | `known-bugs-2026-10-29` | `docs/KNOWN_BUGS.md` |
| `eur-40-units` | `garrison-tooltips`, `grouped-card-bar`, `banners-test` | Unfinished work |
| BB1 | `E:\GSO_052` | The built GSO 0.5.2 zips: the full bundle and the slim GSO-only zip |
| BB1 | `Desktop\EUR_1.5.2_for_Google_Drive` | The EUR 1.5.2 fix pack zip, README and full change list |
