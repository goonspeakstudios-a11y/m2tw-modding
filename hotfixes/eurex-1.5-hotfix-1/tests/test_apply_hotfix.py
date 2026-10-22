"""Fixture-based tests for apply_hotfix.py and build_pack.py.

A fake mod tree is built from the EUREX 1.5 "before" text of every hunk, wrapped in filler
lines, with a mix of BOM/CRLF and plain LF files. No real mod files are needed.

Run from the repository root:
    python -m unittest discover -s hotfixes/eurex-1.5-hotfix-1/tests -v
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import apply_hotfix as hf  # noqa: E402
import build_pack  # noqa: E402

logging.disable(logging.CRITICAL)

STYLE = {
    "script/helper/eurCampaignTriggers.nut": (True, True),
    "script/eur/eru/eurMapHelpers.nut": (False, True),
    "script/eur/upgrades/eurGeneralBGSwap.nut": (False, False),
    "data/world/maps/campaign/imperial_campaign/campaign_script.txt": (True, True),
    "script/eur/battle/monsterAbilityConfig.nut": (True, False),
    "script/eur/loaded/eurCasLoad.nut": (False, True),
    "script/eur/battle/eursetBattleMapPKG.nut": (False, False),
}


def encode(text: str, bom: bool, crlf: bool) -> bytes:
    data = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
    return (hf.BOM + data) if bom else data


def baseline_text(patch: hf.FilePatch) -> str:
    parts = ["// filler header line\nfunction keep() { return (1) }\n"]
    for i, h in enumerate(patch.hunks):
        parts.append(f"// --- block {i} ---\n")
        parts.append(h.old if h.old.endswith("\n") else h.old + "\n")
        parts.append("}\n" if h.old.count("{") > h.old.count("}") else "")
    parts.append("// filler footer\n")
    return "".join(parts)


def make_mod_tree(root: str) -> None:
    os.makedirs(os.path.join(root, "script", "eur"), exist_ok=True)
    os.makedirs(os.path.join(root, ".EUREX1.5"), exist_ok=True)
    with open(os.path.join(root, ".EUREX1.5", "manifest.json"), "w", encoding="utf-8") as fh:
        fh.write("{}")
    for patch in hf.PATCHES:
        bom, crlf = STYLE[patch.rel_path]
        path = os.path.join(root, *patch.rel_path.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(encode(baseline_text(patch), bom, crlf))


class ApplyHotfixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="eurex15_")
        self.mod = os.path.join(self.tmp, "Divide_and_Conquer_EUR")
        make_mod_tree(self.mod)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read_bytes(self, rel: str) -> bytes:
        with open(os.path.join(self.mod, *rel.split("/")), "rb") as fh:
            return fh.read()

    def test_baseline_is_pending(self) -> None:
        for patch in hf.PATCHES:
            status, states = hf.file_status(self.mod, patch)
            self.assertEqual(status, hf.STATUS_PENDING, patch.rel_path)
            self.assertTrue(all(s == hf.STATUS_PENDING for s in states), patch.rel_path)

    def test_check_writes_nothing(self) -> None:
        before = {p.rel_path: self.read_bytes(p.rel_path) for p in hf.PATCHES}
        self.assertEqual(hf.run(self.mod, "check"), 0)
        for rel, data in before.items():
            self.assertEqual(self.read_bytes(rel), data, rel)
            self.assertFalse(os.path.exists(os.path.join(self.mod, *rel.split("/")) + hf.BACKUP_SUFFIX))

    def test_apply_then_idempotent_then_revert(self) -> None:
        originals = {p.rel_path: self.read_bytes(p.rel_path) for p in hf.PATCHES}
        self.assertEqual(hf.run(self.mod, "apply"), 0)
        for patch in hf.PATCHES:
            status, _ = hf.file_status(self.mod, patch)
            self.assertEqual(status, hf.STATUS_ALREADY, patch.rel_path)
            data = self.read_bytes(patch.rel_path)
            bom, crlf = STYLE[patch.rel_path]
            self.assertEqual(data.startswith(hf.BOM), bom, patch.rel_path)
            body = data[len(hf.BOM):] if bom else data
            self.assertEqual(b"\r\n" in body, crlf, patch.rel_path)
            if crlf:
                self.assertNotIn(b"\r\r\n", body, patch.rel_path)
                self.assertNotRegex(body.decode("utf-8"), r"(?<!\r)\n", patch.rel_path)
            text = body.decode("utf-8").replace("\r\n", "\n")
            for hunk in patch.hunks:
                self.assertEqual(text.count(hunk.new), 1, patch.rel_path)
                self.assertEqual(text.replace(hunk.new, "").count(hunk.old), 0, patch.rel_path)
            backup = os.path.join(self.mod, *patch.rel_path.split("/")) + hf.BACKUP_SUFFIX
            with open(backup, "rb") as fh:
                self.assertEqual(fh.read(), originals[patch.rel_path], patch.rel_path)
        patched = {p.rel_path: self.read_bytes(p.rel_path) for p in hf.PATCHES}

        self.assertEqual(hf.run(self.mod, "apply"), 0)
        for rel, data in patched.items():
            self.assertEqual(self.read_bytes(rel), data, rel)

        self.assertEqual(hf.run(self.mod, "revert"), 0)
        for rel, data in originals.items():
            self.assertEqual(self.read_bytes(rel), data, rel)
            self.assertFalse(os.path.exists(os.path.join(self.mod, *rel.split("/")) + hf.BACKUP_SUFFIX))

    def test_revert_without_backup_uses_inverse_replacement(self) -> None:
        originals = {p.rel_path: self.read_bytes(p.rel_path) for p in hf.PATCHES}
        self.assertEqual(hf.run(self.mod, "apply"), 0)
        for patch in hf.PATCHES:
            os.remove(os.path.join(self.mod, *patch.rel_path.split("/")) + hf.BACKUP_SUFFIX)
        self.assertEqual(hf.run(self.mod, "revert"), 0)
        for rel, data in originals.items():
            self.assertEqual(self.read_bytes(rel), data, rel)

    def test_mismatched_file_is_left_alone_and_fails(self) -> None:
        rel = "script/eur/upgrades/eurGeneralBGSwap.nut"
        path = os.path.join(self.mod, *rel.split("/"))
        with open(path, "wb") as fh:
            fh.write(b"function render() { somethingElse() }\n")
        before = self.read_bytes(rel)
        self.assertEqual(hf.run(self.mod, "apply"), 1)
        self.assertEqual(self.read_bytes(rel), before)
        self.assertFalse(os.path.exists(path + hf.BACKUP_SUFFIX))
        for patch in hf.PATCHES:
            if patch.rel_path != rel:
                status, _ = hf.file_status(self.mod, patch)
                self.assertEqual(status, hf.STATUS_ALREADY, patch.rel_path)

    def test_missing_file_fails(self) -> None:
        os.remove(os.path.join(self.mod, "script", "eur", "loaded", "eurCasLoad.nut"))
        self.assertEqual(hf.run(self.mod, "apply"), 1)

    def test_hunk_old_text_is_unique_per_file(self) -> None:
        for patch in hf.PATCHES:
            text = baseline_text(patch)
            for i, hunk in enumerate(patch.hunks):
                self.assertEqual(text.count(hunk.old), 1, f"{patch.rel_path} hunk {i + 1}")
                self.assertNotEqual(hunk.old, hunk.new)

    def test_hunk_state_classification(self) -> None:
        additive = hf.Hunk(old="a()\n", new="a()\nb()\n")
        self.assertEqual(hf.hunk_state("x\na()\ny\n", additive), hf.STATUS_PENDING)
        self.assertEqual(hf.hunk_state("x\na()\nb()\ny\n", additive), hf.STATUS_ALREADY)
        self.assertEqual(hf.hunk_state("x\na()\nb()\ny\na()\n", additive), hf.STATUS_MISMATCH)
        self.assertEqual(hf.hunk_state("x\na()\ny\na()\n", additive), hf.STATUS_MISMATCH)
        self.assertEqual(hf.hunk_state("nothing here\n", additive), hf.STATUS_MISMATCH)
        for patch in hf.PATCHES:
            for i, hunk in enumerate(patch.hunks):
                applied = baseline_text(patch).replace(hunk.old, hunk.new, 1)
                self.assertEqual(hf.hunk_state(applied, hunk), hf.STATUS_ALREADY, f"{patch.rel_path} hunk {i + 1}")

    def test_nut_hunks_keep_brace_balance(self) -> None:
        for patch in hf.PATCHES:
            if not patch.check_braces:
                continue
            for i, hunk in enumerate(patch.hunks):
                delta_old = (hunk.old.count("{") - hunk.old.count("}"), hunk.old.count("(") - hunk.old.count(")"))
                delta_new = (hunk.new.count("{") - hunk.new.count("}"), hunk.new.count("(") - hunk.new.count(")"))
                self.assertEqual(delta_old, delta_new, f"{patch.rel_path} hunk {i + 1}")

    def test_main_cli(self) -> None:
        self.assertEqual(hf.main([self.mod, "--check"]), 0)
        self.assertEqual(hf.main([self.mod]), 0)
        self.assertEqual(hf.main([self.mod, "--revert"]), 0)
        self.assertEqual(hf.main([os.path.join(self.tmp, "nope")]), 2)

    def test_build_pack(self) -> None:
        out = os.path.join(self.tmp, "upload")
        self.assertEqual(build_pack.build(self.mod, out), 1)
        self.assertFalse(os.path.exists(os.path.join(out, build_pack.ZIP_NAME)))
        self.assertEqual(hf.run(self.mod, "apply"), 0)
        self.assertEqual(build_pack.build(self.mod, out), 0)
        zip_path = os.path.join(out, build_pack.ZIP_NAME)
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
            self.assertIsNone(zf.testzip())
        expected = {build_pack.MOD_FOLDER_NAME + "/" + p.rel_path for p in hf.PATCHES} | {build_pack.README_NAME}
        self.assertEqual(names, expected)
        self.assertTrue(os.path.isfile(os.path.join(out, build_pack.README_NAME)))


if __name__ == "__main__":
    unittest.main()
