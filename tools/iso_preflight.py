#!/usr/bin/env python3
"""Fail-closed structural preflight for Xbox 360 XDVDFS/XISO images.

This is an early import-pipeline component, not a Tekken 6 region/revision
validator and not the final PS5 in-app importer. It never modifies the input.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from pathlib import Path

SECTOR = 2048
DESCRIPTOR_SECTOR = 32
MAGIC = b"MICROSOFT*XBOX*MEDIA"
PARTITION_CANDIDATES = (0, 0x0FD90000, 0x02080000, 0x18300000)
MAX_DIRECTORY_BYTES = 16 * 1024 * 1024


class ImageError(ValueError):
    pass


def inspect_image(path: str | os.PathLike[str]) -> dict[str, object]:
    image = Path(path)
    if not image.is_file():
        raise ImageError("Selected path is not a regular file.")
    size = image.stat().st_size
    if size < 0x10000 + SECTOR:
        raise ImageError("Image is too small to contain an Xbox XDVDFS descriptor.")

    with image.open("rb") as stream:
        for partition in PARTITION_CANDIDATES:
            offset = partition + DESCRIPTOR_SECTOR * SECTOR
            if offset + SECTOR > size:
                continue
            stream.seek(offset)
            descriptor = stream.read(SECTOR)
            if len(descriptor) != SECTOR:
                continue
            # XDVDFS descriptors carry the signature at both ends.
            if descriptor[:len(MAGIC)] != MAGIC or descriptor[-len(MAGIC):] != MAGIC:
                continue
            root_sector, root_bytes = struct.unpack_from("<II", descriptor, 20)
            root_offset = partition + root_sector * SECTOR
            if root_bytes == 0 or root_bytes > MAX_DIRECTORY_BYTES:
                raise ImageError("Xbox descriptor has an invalid root-directory size.")
            if root_offset < partition or root_offset + root_bytes > size:
                raise ImageError("Xbox descriptor points outside the selected image.")
            return {
                "valid_xdvdfs_structure": True,
                "format": "xbox360-xdvdfs-xiso",
                "image_bytes": size,
                "partition_offset": partition,
                "root_directory_offset": root_offset,
                "root_directory_bytes": root_bytes,
                "game_identity_verified": False,
                "note": "Structure recognized only; Tekken 6 title ID, region, and Rev 1 are not yet verified.",
            }

    raise ImageError("No valid Xbox XDVDFS descriptor found in supported partition locations.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="path to a user-owned Xbox 360 ISO/XISO")
    args = parser.parse_args()
    try:
        result = inspect_image(args.image)
    except (OSError, ImageError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
