#!/usr/bin/env python3
"""Combine XDVDFS root inspection and safe default.xex metadata parsing.

The selected ISO is read-only. The executable is copied to a temporary file
only so the existing XEX parser can inspect it; the temporary file is removed
when the command exits. This reports metadata but does not certify Tekken 6 or
Rev 1 without a trusted game-specific reference.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from xdvdfs_root import DirectoryError, list_root
from xex_metadata import XexError, inspect_xex

MAX_XEX_BYTES = 1024 * 1024 * 1024
COPY_CHUNK = 1024 * 1024


class GameImageError(ValueError):
    pass


def inspect_game_image(path: str | Path) -> dict[str, object]:
    image = Path(path)
    root = list_root(image)
    executable = next(
        (entry for entry in root["root_entries"]
         if str(entry["name"]).casefold() == "default.xex"
         and not bool(entry["directory"])),
        None,
    )
    if executable is None:
        raise GameImageError(
            "No root-level default.xex file was found. This image is not yet "
            "eligible for the Tekken 6 import path."
        )

    xex_size = int(executable["size_bytes"])
    if xex_size < 24 or xex_size > MAX_XEX_BYTES:
        raise GameImageError(
            f"default.xex size ({xex_size} bytes) is outside the supported "
            "metadata-inspection limit."
        )

    with tempfile.TemporaryDirectory(prefix="t6-xex-inspect-") as temp_dir:
        temp_xex = Path(temp_dir) / "default.xex"
        remaining = xex_size
        with image.open("rb") as source, temp_xex.open("wb") as target:
            source.seek(int(executable["data_offset"]))
            while remaining:
                block = source.read(min(COPY_CHUNK, remaining))
                if not block:
                    raise GameImageError("Image ended while reading default.xex.")
                target.write(block)
                remaining -= len(block)
        metadata = inspect_xex(temp_xex)

    return {
        "valid_xdvdfs_structure": True,
        "default_xex_present": True,
        "default_xex_size_bytes": xex_size,
        "xex_metadata": metadata,
        "game_identity_verified": False,
        "revision_verified": False,
        "import_ready": False,
        "note": (
            "XDVDFS structure and XEX execution metadata were read. This does "
            "not prove the image is Tekken 6 USA/Europe Rev 1. Import remains "
            "blocked until game-specific title/media IDs and a trusted revision "
            "reference are validated."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="path to a user-owned Xbox 360 ISO/XISO")
    args = parser.parse_args()
    try:
        result = inspect_game_image(args.image)
    except (OSError, DirectoryError, XexError, GameImageError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
