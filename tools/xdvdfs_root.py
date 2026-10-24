#!/usr/bin/env python3
"""Read the XDVDFS root directory of a user-owned Xbox 360 ISO/XISO.

This is structural discovery only. It does not extract files, decrypt XEX,
or establish Tekken 6 region/revision compatibility.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

from iso_preflight import ImageError, inspect_image

ENTRY_FIXED_BYTES = 14
DIRECTORY_ATTRIBUTE = 0x10
MAX_ENTRIES = 100_000


class DirectoryError(ValueError):
    pass


def list_root(path: str | Path) -> dict[str, object]:
    image = Path(path)
    info = inspect_image(image)
    start = int(info["root_directory_offset"])
    length = int(info["root_directory_bytes"])
    entries: list[dict[str, object]] = []
    with image.open("rb") as stream:
        stream.seek(start)
        data = stream.read(length)
    if len(data) != length:
        raise DirectoryError("Root directory could not be read completely.")

    pos = 0
    while pos < len(data):
        # Remaining zero padding is allowed; a partial nonzero record is not.
        if data[pos:] and all(byte == 0 for byte in data[pos:]):
            break
        if len(entries) >= MAX_ENTRIES:
            raise DirectoryError("Root directory exceeds the entry safety limit.")
        if len(data) - pos < ENTRY_FIXED_BYTES:
            raise DirectoryError("Truncated XDVDFS directory entry header.")
        left, right, sector, size = struct.unpack_from("<HHII", data, pos)
        attributes = data[pos + 12]
        name_length = data[pos + 13]
        record_end = pos + ENTRY_FIXED_BYTES + name_length
        if name_length == 0 or record_end > len(data):
            raise DirectoryError("Invalid XDVDFS directory entry name length.")
        raw_name = data[pos + ENTRY_FIXED_BYTES:record_end]
        try:
            name = raw_name.decode("ascii")
        except UnicodeDecodeError as exc:
            raise DirectoryError("Root directory contains a non-ASCII entry name.") from exc
        if any(ord(ch) < 0x20 or ch in "/\\:" for ch in name):
            raise DirectoryError("Root directory contains an unsafe entry name.")
        next_pos = (record_end + 3) & ~3
        if next_pos <= pos or next_pos > len(data):
            raise DirectoryError("Directory entry alignment points outside root directory.")
        absolute_offset = int(info["partition_offset"]) + sector * 2048
        if absolute_offset < int(info["partition_offset"]) or absolute_offset + size > image.stat().st_size:
            raise DirectoryError(f"Entry {name!r} points outside the image.")
        entries.append({
            "name": name,
            "directory": bool(attributes & DIRECTORY_ATTRIBUTE),
            "size_bytes": size,
            "data_offset": absolute_offset,
            "left_sibling_offset": left,
            "right_sibling_offset": right,
        })
        pos = next_pos

    names = [str(entry["name"]).casefold() for entry in entries]
    return {
        "valid_xdvdfs_structure": True,
        "root_entry_count": len(entries),
        "root_entries": entries,
        "default_xex_present": "default.xex" in names,
        "game_identity_verified": False,
        "revision_verified": False,
        "note": "Root directory listed only. Presence of default.xex does not prove Tekken 6 identity or Rev 1.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="path to a user-owned Xbox 360 ISO/XISO")
    args = parser.parse_args()
    try:
        result = list_root(args.image)
    except (OSError, ImageError, DirectoryError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
