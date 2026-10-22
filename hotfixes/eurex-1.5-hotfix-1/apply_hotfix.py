#!/usr/bin/env python3
"""EUREX 1.5 hotfix 1 - apply, check or revert the fix set on an installed mod folder.

Target: Medieval II Total War/mods/Divide_and_Conquer_EUR with the EUREX 1.5 overlay
(.EUREX1.5/manifest.json present) running on the M2EX engine build of 2026-10-15.

Every edit is an exact before/after text replacement. A file is written only when every
hunk for it either applies cleanly (old text found exactly once) or is already applied
(new text present, old text absent). Nothing is written in --check mode. Byte order mark
and line-ending style (CRLF or LF) of each file are preserved. The first run keeps a
backup next to each file as <name>.bak_eurex15_hotfix1; --revert restores from it.

Exit codes: 0 = every file applied or already applied, 1 = at least one file could not
be patched (details in the log), 2 = bad arguments or mod folder not found.

Run:
    python apply_hotfix.py "D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR"
    python apply_hotfix.py <mod folder> --check
    python apply_hotfix.py <mod folder> --revert
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from dataclasses import dataclass, field
from typing import Iterable

HOTFIX_ID = "eurex15_hotfix1"
BACKUP_SUFFIX = ".bak_" + HOTFIX_ID
MANIFEST_REL = os.path.join(".EUREX1.5", "manifest.json")
BOM = b"\xef\xbb\xbf"

log = logging.getLogger("eurex15.hotfix")


@dataclass(frozen=True)
class Hunk:
    old: str
    new: str


@dataclass(frozen=True)
class FilePatch:
    rel_path: str
    title: str
    hunks: tuple[Hunk, ...]
    check_braces: bool = True
    needs_new_campaign: bool = False


# ----------------------------------------------------------------------------------
# The fix set. Paths are relative to the mod folder and use forward slashes.
# ----------------------------------------------------------------------------------

PATCHES: tuple[FilePatch, ...] = (
    FilePatch(
        rel_path="script/helper/eurCampaignTriggers.nut",
        title="Custom city models going generic in the second campaign of a session",
        hunks=(
            Hunk(
                old=(
                    "    if (!::EUR.cas_standalone_set_already) {\n"
                    "        ::EUR.loadStratCAS()\n"
                    "        ::EUR.setCasStandalone()\n"
                    "        ::EUR.cas_standalone_set_already = true\n"
                    "    }\n"
                ),
                new=(
                    "    // The M2EX script VM survives leaving a campaign, so a once-per-process guard left every\n"
                    "    // campaign after the first (load or new) with the engine's default city models (Bree etc.).\n"
                    "    // Stamp on every campaign boot; the model re-add is harmless when the models already exist.\n"
                    "    if (!::EUR.cas_standalone_set_already) {\n"
                    "        ::EUR.loadStratCAS()\n"
                    "        ::EUR.cas_standalone_set_already = true\n"
                    "    } else {\n"
                    "        try { ::EUR.loadStratCAS() } catch (e) { ::game.log(\"[EUR cas] model re-add skipped: \" + e) }\n"
                    "    }\n"
                    "    ::EUR.setCasStandalone()\n"
                    "    try { ::game.log(\"[EUR cas] settlement models applied\") } catch (e) {}\n"
                ),
            ),
            Hunk(
                old=(
                    "    ::EUR.eur_numberOfFactions = ::game.factionCount()\n"
                    "    ::EUR.eur_playerFactionId = ::game.localFactionId()\n"
                    "    ::EUR.eur_player_faction = ::game.localFaction()\n"
                    "    // Before anything can build a widget"
                ),
                new=(
                    "    ::EUR.eur_numberOfFactions = ::game.factionCount()\n"
                    "    ::EUR.eur_playerFactionId = ::game.localFactionId()\n"
                    "    ::EUR.eur_player_faction = ::game.localFaction()\n"
                    "    try { ::game.log(\"[EUR boot] campaignBoot start, first_run=\" + ::EUR.options_first_run\n"
                    "        + \" show_options=\" + ::EUR.show_options_window + \" cas_done=\" + ::EUR.cas_standalone_set_already) } catch (e) {}\n"
                    "    // Before anything can build a widget"
                ),
            ),
            Hunk(
                old=(
                    "    ::events.on(\"campaignMapLoaded\", function() {\n"
                    "        ::EUR.campaignBoot()\n"
                    "    })\n"
                ),
                new=(
                    "    ::events.on(\"campaignMapLoaded\", function() {\n"
                    "        try { ::game.log(\"[EUR boot] campaignMapLoaded\") } catch (e) {}\n"
                    "        ::EUR.campaignBoot()\n"
                    "        try { ::game.log(\"[EUR boot] campaignBoot done, in_map=\" + ::EUR.in_campaign_map\n"
                    "            + \" first_run=\" + ::EUR.options_first_run + \" show_options=\" + ::EUR.show_options_window\n"
                    "            + \" presets=\" + ::EUR.campaignPresets.len()) } catch (e) {}\n"
                    "    })\n"
                ),
            ),
            Hunk(
                old=(
                    "    ::events.on(\"exitToMenu\", function() {\n"
                    "        ::EUR.in_campaign_map = false\n"
                    "    })\n"
                ),
                new=(
                    "    ::events.on(\"exitToMenu\", function() {\n"
                    "        try { ::game.log(\"[EUR boot] exitToMenu\") } catch (e) {}\n"
                    "        ::EUR.in_campaign_map = false\n"
                    "    })\n"
                ),
            ),
            Hunk(
                old=(
                    "    ::events.on(\"newGameStart\", function() {\n"
                    "        if (!::EUR.options_first_run) {\n"
                ),
                new=(
                    "    ::events.on(\"newGameStart\", function() {\n"
                    "        try { ::game.log(\"[EUR boot] newGameStart, first_run=\" + ::EUR.options_first_run) } catch (e) {}\n"
                    "        if (!::EUR.options_first_run) {\n"
                ),
            ),
            Hunk(
                old=(
                    "        ::EUR.preparePresetChoice()\n"
                    "        //::EUR.show_genenabled = true\n"
                ),
                new=(
                    "        ::EUR.preparePresetChoice()\n"
                    "        try { ::game.log(\"[EUR boot] newGameLoaded: preset choice prepared\") } catch (e) {}\n"
                    "        //::EUR.show_genenabled = true\n"
                ),
            ),
            Hunk(
                old=(
                    "    ::events.on(\"unloadCampaign\", function() {\n"
                    "        if (::EUR.to_log) { println(\"EUR SCRIPT: \" + \"onUnloadCampaign\") }\n"
                ),
                new=(
                    "    ::events.on(\"unloadCampaign\", function() {\n"
                    "        try { ::game.log(\"[EUR boot] unloadCampaign\") } catch (e) {}\n"
                    "        if (::EUR.to_log) { println(\"EUR SCRIPT: \" + \"onUnloadCampaign\") }\n"
                ),
            ),
        ),
    ),
    FilePatch(
        rel_path="script/eur/eru/eurMapHelpers.nut",
        title="Amon Hen campaign model under its current settlement name; Hobbiton and Bree custom battle maps keyed to the right tiles",
        hunks=(
            Hunk(
                old="\t[\"134,386\"] = \"hobbiton_a\",                //(Hobiton)\n",
                new=(
                    "\t[\"133,385\"] = \"hobbiton_a\",                //(Hobiton) tile on the current map (was 134,386)\n"
                    "\t[\"166,380\"] = \"bree_a\",                    //(Bree) package tagged normans; town runs on the Bree_Folk plan, engine may ignore\n"
                ),
            ),
            Hunk(
                old="\t[\"eursett_15\"] = 11,         //(Amon Hen)\n",
                new=(
                    "\t[\"Amon_Hen\"] = 11,           //(Amon Hen) current settlement name\n"
                    "\t[\"eursett_15\"] = 11,         //(Amon Hen) old alias for older saves\n"
                ),
            ),
        ),
    ),
    FilePatch(
        rel_path="script/eur/upgrades/eurGeneralBGSwap.nut",
        title="Unit-upgrade / bodyguard crest disappearing for the rest of the session",
        hunks=(
            Hunk(
                old=(
                    "    function render() {\n"
                    "        this.buildOnce()\n"
                    "        ::EUR.syncLeftWindows()\n"
                    "        this.checkcard()\n"
                ),
                new=(
                    "    function render() {\n"
                    "        this.buildOnce()\n"
                    "        try {\n"
                    "            ::EUR.syncLeftWindows()\n"
                    "            this.checkcard()\n"
                    "        } catch (e) {\n"
                    "            // The remembered selection can go stale (general died in battle, save reloaded,\n"
                    "            // army merged). Without this guard the engine drops this frame handler for the\n"
                    "            // rest of the session and the bodyguard/upgrade crest never draws again.\n"
                    "            println(\"EUR BGSwap: stale selection cleared after error: \" + e)\n"
                    "            ::EUR.temp_fort_char = null\n"
                    "            ::EUR.sel_unit = null\n"
                    "            ::EUR.can_bg_swap = false\n"
                    "            ::EUR.can_unit_upgrade = false\n"
                    "            if (this.cardBtn != 0) { ::UI.widgetVisible(this.cardBtn, false) }\n"
                    "            if (this.upgradeBtn != 0) { ::UI.widgetVisible(this.upgradeBtn, false) }\n"
                    "            ::EUR.set_active_left_window(\"\")\n"
                    "        }\n"
                ),
            ),
        ),
    ),
    FilePatch(
        rel_path="data/world/maps/campaign/imperial_campaign/campaign_script.txt",
        title="Reclaiming Moria quest (Durin's Folk, Mirkwood route): \"Restricted area\" on the arrow target",
        check_braces=False,
        needs_new_campaign=True,
        hunks=(
            Hunk(
                old="restrict_clickable_area Central_Mirkwood_Province Elven_Mirkwood_Province Esgaroth_Province\n",
                new="restrict_clickable_area Central_Mirkwood_Province Elven_Mirkwood_Province Esgaroth_Province Emyn_Nu_Fuin_Province\n",
            ),
            Hunk(
                old="restrict_clickable_area Central_Mirkwood_Province Middle_Mirkwood_Province Deep_Mirkwood_Province\n",
                new="restrict_clickable_area Central_Mirkwood_Province Middle_Mirkwood_Province Deep_Mirkwood_Province Emyn_Nu_Fuin_Province Elven_Mirkwood_Province\n",
            ),
            Hunk(
                old="restrict_clickable_area Middle_Mirkwood_Province Central_Mirkwood_Province Central_Vale_Province Woodsmen_Province Deep_Mirkwood_Province\n",
                new="restrict_clickable_area Middle_Mirkwood_Province Central_Mirkwood_Province Central_Vale_Province Woodsmen_Province Deep_Mirkwood_Province Emyn_Nu_Fuin_Province\n",
            ),
        ),
    ),
    FilePatch(
        rel_path="script/eur/battle/monsterAbilityConfig.nut",
        title="Green outlines under monster area attacks (debug switch left on in 1.5)",
        hunks=(
            Hunk(
                old="debugAoeOutline = true,",
                new="debugAoeOutline = false,   // was true in 1.5: drew green debug outlines under monster area attacks",
            ),
        ),
    ),
    FilePatch(
        rel_path="script/eur/loaded/eurCasLoad.nut",
        title="Per-town [EUR cas] log lines so a missing custom city model can be traced in system.log.txt",
        hunks=(
            Hunk(
                old=(
                    "        local sett = ::EUR.eur_sMap.findSettlement(name)\n"
                    "        if (sett != null) { ::EUR.setCasSett(sett) }\n"
                ),
                new=(
                    "        local sett = ::EUR.eur_sMap.findSettlement(name)\n"
                    "        if (sett != null) { ::EUR.setCasSett(sett) }\n"
                    "        else { try { ::game.log(\"[EUR cas] not found: \" + name) } catch (e) {} }\n"
                ),
            ),
            Hunk(
                old=(
                    "        local modelID = ::EUR.strat_cas_setts[sett.name]\n"
                    "        ::game.models.setOnTile(sett.tileX, sett.tileY, modelID, modelID)\n"
                ),
                new=(
                    "        local modelID = ::EUR.strat_cas_setts[sett.name]\n"
                    "        try { ::game.log(\"[EUR cas] \" + sett.name + \" tile \" + sett.tileX + \",\" + sett.tileY + \" model \" + modelID) } catch (e) {}\n"
                    "        ::game.models.setOnTile(sett.tileX, sett.tileY, modelID, modelID)\n"
                ),
            ),
        ),
    ),
    FilePatch(
        rel_path="script/eur/battle/eursetBattleMapPKG.nut",
        title="Custom settlement battle maps never loading (picker defined but never registered with the engine)",
        hunks=(
            Hunk(
                old=(
                    "// Picks a custom battle-map package by the defender tile's coordinates.\n"
                    '// custom_maps is populated in eurCasLoad (keyed "x,y").\n'
                    '::EUR.onSelectWorldpkgdesc <- function(selectedRecord, selectedRecordGroup) {\n'
                    '    local battle = ::battle.current()\n'
                    '    if (battle == null) { return selectedRecord }\n'
                    '\n'
                    '    local xCoord = battle.defenderX\n'
                    '    local yCoord = battle.defenderY\n'
                    '    if (xCoord == 0 || yCoord == 0) { return selectedRecord }\n'
                    '\n'
                    '    local coordKey = xCoord + "," + yCoord\n'
                    '    if (coordKey in ::EUR.custom_maps) {\n'
                    '        selectedRecord = ::EUR.custom_maps[coordKey]\n'
                    '    }\n'
                    '    return selectedRecord\n'
                    '}\n'
                ),
                new=(
                    "// Picks a custom battle-map package by the defender tile's coordinates.\n"
                    '// custom_maps is populated in eurCasLoad (keyed "x,y").\n'
                    '::EUR.onSelectWorldpkgdesc <- function(selectedRecord, selectedRecordGroup) {\n'
                    '    local battle = ::battle.current()\n'
                    '    if (battle == null) { return selectedRecord }\n'
                    '\n'
                    '    local xCoord = battle.defenderX\n'
                    '    local yCoord = battle.defenderY\n'
                    '    if (xCoord == 0 || yCoord == 0) { return selectedRecord }\n'
                    '\n'
                    '    local coordKey = xCoord + "," + yCoord\n'
                    '    if (coordKey in ::EUR.custom_maps) {\n'
                    '        selectedRecord = ::EUR.custom_maps[coordKey]\n'
                    '    }\n'
                    '    return selectedRecord\n'
                    '}\n'
                    '\n'
                    '// Hotfix: the picker above was never registered with M2EX, so no custom\n'
                    "// battle map ever loaded. Hook it to the engine's selectWorldpkgdesc event.\n"
                    '::events.on("selectWorldpkgdesc", function(...) {\n'
                    '    local rec = vargv.len() > 0 ? vargv[0] : null\n'
                    '    local grp = vargv.len() > 1 ? vargv[1] : null\n'
                    '    local picked = rec\n'
                    '    try {\n'
                    '        picked = ::EUR.onSelectWorldpkgdesc(rec, grp)\n'
                    '        local b = ::battle.current()\n'
                    '        local where = b == null ? "?" : (b.defenderX + "," + b.defenderY)\n'
                    '        ::game.log("[EUR maps] tile " + where + " engine=" + rec + " group=" + grp + " -> " + picked)\n'
                    '    } catch (e) {\n'
                    '        ::game.log("[EUR maps] error: " + e)\n'
                    '        return null\n'
                    '    }\n'
                    '    return picked == rec ? null : picked\n'
                    '})\n'
                ),
            ),
        ),
    ),
)


# ----------------------------------------------------------------------------------
# Text handling
# ----------------------------------------------------------------------------------

@dataclass
class TextFile:
    path: str
    text: str
    bom: bool
    crlf: bool
    original_bytes: bytes = field(repr=False)

    @classmethod
    def read(cls, path: str) -> "TextFile":
        with open(path, "rb") as fh:
            raw = fh.read()
        bom = raw.startswith(BOM)
        body = raw[len(BOM):] if bom else raw
        crlf = b"\r\n" in body
        text = body.decode("utf-8").replace("\r\n", "\n")
        return cls(path=path, text=text, bom=bom, crlf=crlf, original_bytes=raw)

    def encode(self) -> bytes:
        out = self.text.replace("\n", "\r\n") if self.crlf else self.text
        data = out.encode("utf-8")
        return (BOM + data) if self.bom else data

    def write(self) -> None:
        tmp = self.path + ".tmp_" + HOTFIX_ID
        with open(tmp, "wb") as fh:
            fh.write(self.encode())
        os.replace(tmp, self.path)


def braces_balanced(text: str) -> bool:
    return text.count("{") == text.count("}") and text.count("(") == text.count(")")


# ----------------------------------------------------------------------------------
# Patch status / apply / revert
# ----------------------------------------------------------------------------------

STATUS_APPLIED = "applied"
STATUS_ALREADY = "already-applied"
STATUS_PENDING = "pending"
STATUS_MISSING = "file-missing"
STATUS_MISMATCH = "mismatch"
STATUS_ERROR = "error"
STATUS_REVERTED = "reverted"
STATUS_NOT_APPLIED = "not-applied"


def hunk_state(text: str, hunk: Hunk) -> str:
    """Classify one hunk. Occurrences of the old text that sit inside an occurrence of the
    new text do not count, so an additive hunk (new = old + extra lines) reads as already
    applied instead of being applied twice."""
    new_n = text.count(hunk.new)
    outside = text.replace(hunk.new, "") if new_n else text
    old_n = outside.count(hunk.old)
    if old_n == 1 and new_n == 0:
        return STATUS_PENDING
    if old_n == 0 and new_n >= 1:
        return STATUS_ALREADY
    return STATUS_MISMATCH


def file_status(mod_dir: str, patch: FilePatch) -> tuple[str, list[str]]:
    """Return (status, per-hunk states) without writing anything."""
    path = os.path.join(mod_dir, *patch.rel_path.split("/"))
    if not os.path.isfile(path):
        return STATUS_MISSING, []
    try:
        tf = TextFile.read(path)
    except (OSError, UnicodeDecodeError) as exc:
        log.error("%s: cannot read: %s", patch.rel_path, exc)
        return STATUS_ERROR, []
    states = [hunk_state(tf.text, h) for h in patch.hunks]
    if any(s == STATUS_MISMATCH for s in states):
        return STATUS_MISMATCH, states
    if all(s == STATUS_ALREADY for s in states):
        return STATUS_ALREADY, states
    return STATUS_PENDING, states


def apply_file(mod_dir: str, patch: FilePatch, dry_run: bool) -> str:
    path = os.path.join(mod_dir, *patch.rel_path.split("/"))
    status, states = file_status(mod_dir, patch)
    if status == STATUS_MISSING:
        log.error("%s: file not found", patch.rel_path)
        return status
    if status == STATUS_ERROR:
        return status
    if status == STATUS_MISMATCH:
        for i, s in enumerate(states):
            if s == STATUS_MISMATCH:
                log.error("%s: hunk %d does not match the EUREX 1.5 text (file modified or wrong version)",
                          patch.rel_path, i + 1)
        return status
    if status == STATUS_ALREADY:
        log.info("%s: already applied", patch.rel_path)
        return status
    if dry_run:
        log.info("%s: would apply %d hunk(s)", patch.rel_path,
                 sum(1 for s in states if s == STATUS_PENDING))
        return STATUS_PENDING

    tf = TextFile.read(path)
    before_balanced = braces_balanced(tf.text)
    for i, (hunk, state) in enumerate(zip(patch.hunks, states)):
        if state == STATUS_PENDING:
            tf.text = tf.text.replace(hunk.old, hunk.new, 1)
            log.debug("%s: hunk %d replaced", patch.rel_path, i + 1)
    if patch.check_braces and before_balanced and not braces_balanced(tf.text):
        log.error("%s: brace/paren balance broke after patching; file left untouched", patch.rel_path)
        return STATUS_ERROR

    backup = path + BACKUP_SUFFIX
    try:
        if not os.path.exists(backup):
            shutil.copy2(path, backup)
            log.info("%s: backup written -> %s", patch.rel_path, os.path.basename(backup))
        tf.write()
    except OSError as exc:
        log.error("%s: write failed: %s", patch.rel_path, exc)
        return STATUS_ERROR
    log.info("%s: applied (%s)", patch.rel_path, patch.title)
    if patch.needs_new_campaign:
        log.warning("%s: takes effect only in a NEW campaign", patch.rel_path)
    return STATUS_APPLIED


def revert_file(mod_dir: str, patch: FilePatch, dry_run: bool) -> str:
    path = os.path.join(mod_dir, *patch.rel_path.split("/"))
    backup = path + BACKUP_SUFFIX
    if not os.path.isfile(path):
        log.error("%s: file not found", patch.rel_path)
        return STATUS_MISSING
    if os.path.isfile(backup):
        if dry_run:
            log.info("%s: would restore from %s", patch.rel_path, os.path.basename(backup))
            return STATUS_PENDING
        try:
            shutil.copy2(backup, path)
            os.remove(backup)
        except OSError as exc:
            log.error("%s: restore failed: %s", patch.rel_path, exc)
            return STATUS_ERROR
        log.info("%s: restored from backup", patch.rel_path)
        return STATUS_REVERTED

    # No backup (patched by hand or packed file): undo by inverse replacement.
    try:
        tf = TextFile.read(path)
    except (OSError, UnicodeDecodeError) as exc:
        log.error("%s: cannot read: %s", patch.rel_path, exc)
        return STATUS_ERROR
    if all(tf.text.count(h.new) == 0 for h in patch.hunks):
        log.info("%s: not applied, nothing to revert", patch.rel_path)
        return STATUS_NOT_APPLIED
    for i, h in enumerate(patch.hunks):
        if tf.text.count(h.new) > 1:
            log.error("%s: hunk %d replacement text occurs more than once; cannot revert safely", patch.rel_path, i + 1)
            return STATUS_MISMATCH
    if dry_run:
        log.info("%s: would revert by inverse replacement (no backup present)", patch.rel_path)
        return STATUS_PENDING
    for h in patch.hunks:
        if tf.text.count(h.new) == 1:
            tf.text = tf.text.replace(h.new, h.old, 1)
    try:
        tf.write()
    except OSError as exc:
        log.error("%s: write failed: %s", patch.rel_path, exc)
        return STATUS_ERROR
    log.info("%s: reverted by inverse replacement", patch.rel_path)
    return STATUS_REVERTED


# ----------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------

def validate_mod_dir(mod_dir: str) -> bool:
    if not os.path.isdir(mod_dir):
        log.error("mod folder not found: %s", mod_dir)
        return False
    if not os.path.isdir(os.path.join(mod_dir, "script", "eur")):
        log.error("%s does not look like Divide_and_Conquer_EUR (no script/eur folder)", mod_dir)
        return False
    if not os.path.isfile(os.path.join(mod_dir, MANIFEST_REL)):
        log.warning("%s not found: this may not be an EUREX 1.5 install; hunks will be checked exactly anyway",
                    MANIFEST_REL)
    stray_caps = os.path.join(mod_dir, "data", "descr_caps_ex.txt")
    if os.path.isfile(stray_caps):
        log.warning("data/descr_caps_ex.txt is present in the mod folder. The engine package belongs in the game "
                    "root; a stray copy here switches model_battle_source and no unit model loads. Remove it.")
    return True


def configure_logging(verbose: bool, log_file: str | None) -> None:
    fmt = "%(asctime)s %(levelname)-7s %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        try:
            handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
        except OSError as exc:
            print(f"cannot open log file {log_file}: {exc}", file=sys.stderr)
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format=fmt, handlers=handlers)


def run(mod_dir: str, mode: str, patches: Iterable[FilePatch] = PATCHES) -> int:
    results: dict[str, str] = {}
    for patch in patches:
        if mode == "revert":
            results[patch.rel_path] = revert_file(mod_dir, patch, dry_run=False)
        elif mode == "check":
            results[patch.rel_path] = apply_file(mod_dir, patch, dry_run=True)
        else:
            results[patch.rel_path] = apply_file(mod_dir, patch, dry_run=False)

    ok_states = {STATUS_APPLIED, STATUS_ALREADY, STATUS_REVERTED, STATUS_NOT_APPLIED}
    if mode == "check":
        ok_states = {STATUS_PENDING, STATUS_ALREADY}
    failures = {p: s for p, s in results.items() if s not in ok_states}

    log.info("---- summary (%s) ----", mode)
    for rel, state in results.items():
        log.info("%-62s %s", rel, state)
    if failures:
        log.error("%d file(s) not %s", len(failures), "patchable" if mode != "revert" else "reverted")
        return 1
    if mode == "apply" and any(s == STATUS_APPLIED for s in results.values()):
        log.info("restart Medieval II for the script changes to load; the Moria route fix needs a new campaign")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mod_dir", help="path to mods/Divide_and_Conquer_EUR")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="report what would change; write nothing")
    group.add_argument("--revert", action="store_true", help="restore the pre-hotfix files")
    parser.add_argument("--log-file", default=None, help="also write the log to this file")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    configure_logging(args.verbose, args.log_file)
    mod_dir = os.path.abspath(args.mod_dir)
    if not validate_mod_dir(mod_dir):
        return 2
    mode = "revert" if args.revert else ("check" if args.check else "apply")
    log.info("EUREX 1.5 hotfix 1: %s on %s", mode, mod_dir)
    return run(mod_dir, mode)


if __name__ == "__main__":
    sys.exit(main())
