#!/usr/bin/env python3
"""Build the drop-in zip (EUR_1.5_FixPack.zip) from an already patched mod folder.

The zip holds Divide_and_Conquer_EUR/<the six patched files> plus README.txt, so a player
extracts it into their "mods" folder and overwrites. Every file is verified to carry the
hotfix text before it is packed; a file that is unpatched or mismatched aborts the build.

Exit codes: 0 = zip written, 1 = a file is not patched or cannot be read, 2 = bad arguments.

Run:
    python build_pack.py "D:/SteamLibrary/steamapps/common/Medieval II Total War/mods/Divide_and_Conquer_EUR" --out "C:/Users/BigBoss1/Desktop/EUR_1.5_FixPack_upload"
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import zipfile

import apply_hotfix as hf

MOD_FOLDER_NAME = "Divide_and_Conquer_EUR"
ZIP_NAME = "EUR_1.5_FixPack.zip"
README_NAME = "README.txt"

log = logging.getLogger("eurex15.pack")


def readme_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), README_NAME)


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


def build(mod_dir: str, out_dir: str) -> int:
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
    if bad is not None:
        log.error("zip integrity check failed on %s", bad)
        return 1
    log.info("wrote %s (%d bytes) and %s", zip_path, os.path.getsize(zip_path), os.path.join(out_dir, README_NAME))
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
