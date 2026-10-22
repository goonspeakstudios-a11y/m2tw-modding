#!/usr/bin/env python3
"""Build the drop-in zip (EUR_<version>_FixPack.zip) from an already patched mod folder.

The zip holds Divide_and_Conquer_EUR/<every shipped fix file> plus README.txt, so a player
extracts it into their "mods" folder and overwrites.

Rule: every fix that was ever in a pack is in every later pack, unless it is retired on
purpose with a written reason. fix_registry.json next to this script is the list. The build
stops (exit 1, no zip) when:
  - a fix from ANY earlier pack is neither shipped nor retired with a reason;
  - the registry and apply_hotfix.py disagree about which files are fixed;
  - this pack's version is not recorded in the registry with exactly the shipped files;
  - the install differs from the EUREX 1.5 release in a file nobody listed (a fix made on the
    rig but never added to the pack), or has a new script module nobody listed;
  - a shipped file is unpatched, mismatched, or missing from the finished zip.
Without .EUREX1.5/manifest.json in the mod folder the install scan is skipped with a warning;
the registry checks still run.

Exit codes: 0 = zip written, 1 = a check failed or a file cannot be read, 2 = bad arguments.

Run:
    python build_pack.py "D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR" --out "C:/Users/BigBoss1/Desktop/EUR_1.5_FixPack_upload"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import zipfile

import apply_hotfix as hf

MOD_FOLDER_NAME = "Divide_and_Conquer_EUR"
ZIP_NAME = "EUR_1.5.2_FixPack.zip"
README_NAME = "README.txt"
REGISTRY_NAME = "fix_registry.json"

# Install scan: release files under these roots (or at the mod root) with these extensions are
# compared against the manifest. Fixes live in scripts and text data; textures and models are
# skipped to keep the scan to seconds.
SCAN_ROOTS = ("script/", "data/", "eopdata/")
SCAN_EXT = (".nut", ".txt", ".lua", ".xml", ".cfg", ".json", ".dat", ".sd", ".lnt", ".ini")

log = logging.getLogger("eurex15.pack")


def here(name: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)


def readme_path() -> str:
    return here(README_NAME)


def pack_version() -> str:
    match = re.search(r"EUR_(\d+(?:\.\d+)+)_FixPack\.zip$", ZIP_NAME)
    if match is None:
        raise ValueError(f"ZIP_NAME {ZIP_NAME!r} does not carry a version")
    return match.group(1)


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_registry(path: str | None = None) -> dict | None:
    path = path or here(REGISTRY_NAME)
    try:
        with open(path, encoding="utf-8") as fh:
            registry = json.load(fh)
    except (OSError, ValueError) as exc:
        log.error("cannot read the fix registry %s: %s", path, exc)
        return None
    if not isinstance(registry, dict):
        log.error("fix registry %s is not a JSON object", path)
        return None
    return registry


def _files(registry: dict, key: str) -> list[str]:
    return [entry.get("file", "") for entry in registry.get(key, [])]


def registry_problems(registry: dict) -> list[str]:
    """Every reason the registry does not guarantee 'no fix dropped'. Empty list = consistent."""
    problems: list[str] = []
    shipped = set(_files(registry, "shipped"))
    retired = set(_files(registry, "retired"))
    not_shipped = set(_files(registry, "not_shipped"))
    patched = {patch.rel_path for patch in hf.PATCHES}

    for f in sorted(patched - shipped):
        problems.append(f"{f}: apply_hotfix.py patches it but it is not listed under 'shipped'")
    for f in sorted(shipped - patched):
        problems.append(f"{f}: listed under 'shipped' but apply_hotfix.py has no patch for it, so the pack would leave this fix out")
    for f in sorted(shipped & retired):
        problems.append(f"{f}: listed as both 'shipped' and 'retired'")
    for f in sorted(shipped & not_shipped):
        problems.append(f"{f}: listed as both 'shipped' and 'not_shipped'")
    for key in ("shipped", "retired", "not_shipped"):
        names = _files(registry, key)
        for f in sorted({n for n in names if names.count(n) > 1}):
            problems.append(f"{f}: listed twice under '{key}'")
        for f in names:
            if not f:
                problems.append(f"an entry under '{key}' has no 'file'")
    for key in ("retired", "not_shipped"):
        for entry in registry.get(key, []):
            if not str(entry.get("reason", "")).strip():
                problems.append(f"{entry.get('file', '?')}: listed under '{key}' without a reason")

    packs = registry.get("packs", {})
    for version in sorted(packs):
        for f in packs[version]:
            if f not in shipped and f not in retired:
                problems.append(f"{f}: was in the {version} pack but is neither shipped nor retired with a reason - this pack would drop that fix")
    version = pack_version()
    if version not in packs:
        problems.append(f"pack {version} is not recorded under 'packs'; add it with the shipped files before building")
    elif set(packs[version]) != shipped:
        problems.append(f"pack {version} under 'packs' does not list exactly the shipped files")
    return problems


def unlisted_changes(mod_dir: str, registry: dict) -> list[str] | None:
    """Files on this install that differ from the EUREX 1.5 release, or new script modules, that
    the registry neither ships nor excuses. None when there is no usable manifest."""
    manifest_path = os.path.join(mod_dir, hf.MANIFEST_REL)
    try:
        with open(manifest_path, encoding="utf-8-sig") as fh:
            manifest = json.load(fh)
    except (OSError, ValueError):
        return None
    entries = manifest.get("files") if isinstance(manifest, dict) else None
    if not entries:
        return None

    listed = {f.lower() for key in ("shipped", "not_shipped") for f in _files(registry, key)}
    in_release: set[str] = set()
    found: set[str] = set()
    for entry in entries:
        rel = str(entry.get("path", "")).replace("\\", "/")
        low = rel.lower()
        in_release.add(low)
        source = entry.get("source")
        if not source or entry.get("status") == "deleted":
            continue
        if "/" in low and not low.startswith(SCAN_ROOTS):
            continue
        if not low.endswith(SCAN_EXT) or low in listed:
            continue
        path = os.path.join(mod_dir, *rel.split("/"))
        try:
            st = os.stat(path)
        except OSError:
            continue  # absent files are not something a pack ships
        if st.st_size == source.get("size") and st.st_mtime_ns == source.get("mtime_ns"):
            continue
        try:
            if sha256_file(path) != str(source.get("sha256", "")).lower():
                found.add(rel)
        except OSError as exc:
            log.warning("%s: cannot read for the install scan: %s", rel, exc)

    for root, _dirs, names in os.walk(os.path.join(mod_dir, "script")):
        for name in names:
            if not name.lower().endswith(".nut"):
                continue  # .bak_* backups and other leftovers are never loaded
            rel = os.path.relpath(os.path.join(root, name), mod_dir).replace(os.sep, "/")
            if rel.lower() not in in_release and rel.lower() not in listed:
                found.add(rel)
    return sorted(found)


def verify_patched(mod_dir: str) -> bool:
    ok = True
    for patch in hf.PATCHES:
        status, _ = hf.file_status(mod_dir, patch)
        if status != hf.STATUS_ALREADY:
            log.error("%s: %s (run apply_hotfix.py first)", patch.rel_path, status)
            ok = False
        else:
            log.info("%s: patched", patch.rel_path)
    return ok


def check_no_fix_dropped(mod_dir: str, registry: dict) -> bool:
    problems = registry_problems(registry)
    for problem in problems:
        log.error("fix registry: %s", problem)
    if problems:
        log.error("build stopped: fix %s in hotfixes/eurex-1.5-hotfix-1/%s first", "these" if len(problems) > 1 else "this", REGISTRY_NAME)
        return False
    unlisted = unlisted_changes(mod_dir, registry)
    if unlisted is None:
        log.warning("no EUREX 1.5 manifest in the mod folder: cannot check this install for fixes missing from the pack")
        return True
    for rel in unlisted:
        log.error("changed on this install but not in the pack: %s - add a patch for it, or list it under 'not_shipped' with the reason", rel)
    if unlisted:
        log.error("build stopped: %d changed file(s) are neither shipped nor excused", len(unlisted))
        return False
    log.info("install scan: every file that differs from EUREX 1.5 is shipped or excused")
    return True


def build(mod_dir: str, out_dir: str, registry: dict | None = None) -> int:
    if registry is None:
        registry = load_registry()
        if registry is None:
            return 1
    if not check_no_fix_dropped(mod_dir, registry):
        return 1
    if not verify_patched(mod_dir):
        return 1
    readme = readme_path()
    if not os.path.isfile(readme):
        log.error("README.txt missing next to build_pack.py: %s", readme)
        return 1
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        log.error("cannot create output folder %s: %s", out_dir, exc)
        return 1

    zip_path = os.path.join(out_dir, ZIP_NAME)
    tmp_path = zip_path + ".tmp"
    try:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for patch in hf.PATCHES:
                src = os.path.join(mod_dir, *patch.rel_path.split("/"))
                arc = MOD_FOLDER_NAME + "/" + patch.rel_path
                zf.write(src, arc)
                log.info("packed %s", arc)
            zf.write(readme, README_NAME)
        os.replace(tmp_path, zip_path)
        with open(readme, "rb") as src, open(os.path.join(out_dir, README_NAME), "wb") as dst:
            dst.write(src.read())
    except OSError as exc:
        log.error("zip build failed: %s", exc)
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return 1

    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        names = set(zf.namelist())
    if bad is not None:
        log.error("zip integrity check failed on %s", bad)
        return 1
    missing = sorted(f for f in _files(registry, "shipped") if MOD_FOLDER_NAME + "/" + f not in names)
    if missing:
        for f in missing:
            log.error("finished zip is missing shipped fix %s", f)
        try:
            os.remove(zip_path)
        except OSError:
            pass
        return 1
    log.info("wrote %s (%d bytes, all %d shipped fixes) and %s", zip_path, os.path.getsize(zip_path),
             len(_files(registry, "shipped")), os.path.join(out_dir, README_NAME))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mod_dir", help="path to the patched mods/Divide_and_Conquer_EUR")
    parser.add_argument("--out", required=True, help="output folder for the zip and README.txt")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(message)s", stream=sys.stderr)
    mod_dir = os.path.abspath(args.mod_dir)
    if not hf.validate_mod_dir(mod_dir):
        return 2
    return build(mod_dir, os.path.abspath(args.out))


if __name__ == "__main__":
    sys.exit(main())
