#!/usr/bin/env python3
"""Read identity metadata from an extracted Xbox 360 XEX header.

This parser does not decrypt the executable, modify game files, or establish a
specific game revision. Revision verification needs a trusted reference hash or
additional validated game-specific metadata.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

XEX_MAGIC = b"XEX2"
EXECUTION_ID_HEADER = 0x00040006
XEX_HEADER_BYTES = 0x18
OPTIONAL_HEADER_BYTES = 8
EXECUTION_ID_BYTES = 24


class XexError(ValueError):
    pass


def inspect_xex(path: str | Path) -> dict[str, object]:
    source = Path(path)
    if not source.is_file():
        raise XexError("Selected path is not a regular file.")
    size = source.stat().st_size
    if size < XEX_HEADER_BYTES:
        raise XexError("File is too small to contain an XEX header.")

    with source.open("rb") as stream:
        header = stream.read(XEX_HEADER_BYTES)
        if header[:4] != XEX_MAGIC:
            raise XexError("Unsupported executable header; expected XEX2.")
        header_count = struct.unpack_from(">I", header, 20)[0]
        directory_end = XEX_HEADER_BYTES + header_count * OPTIONAL_HEADER_BYTES
        if directory_end > size or header_count > 0x10000:
            raise XexError("XEX optional-header directory is out of bounds.")

        execution_offset = None
        for index in range(header_count):
            stream.seek(XEX_HEADER_BYTES + index * OPTIONAL_HEADER_BYTES)
            entry = stream.read(OPTIONAL_HEADER_BYTES)
            if len(entry) != OPTIONAL_HEADER_BYTES:
                raise XexError("Truncated XEX optional-header directory.")
            key, value = struct.unpack(">II", entry)
            if key == EXECUTION_ID_HEADER:
                execution_offset = value
                break

        if execution_offset is None:
            raise XexError("XEX execution metadata (0x00040006) is missing.")
        if execution_offset > size or execution_offset + EXECUTION_ID_BYTES > size:
            raise XexError("XEX execution metadata points outside the file.")

        stream.seek(execution_offset)
        execution = stream.read(EXECUTION_ID_BYTES)
        if len(execution) != EXECUTION_ID_BYTES:
            raise XexError("Truncated XEX execution metadata.")

    media_id, version, base_version, title_id = struct.unpack_from(">IIII", execution, 0)
    platform, executable_type, disc_number, disc_count = execution[16:20]
    savegame_id = struct.unpack_from(">I", execution, 20)[0]
    return {
        "valid_xex2_header": True,
        "title_id": f"{title_id:08X}",
        "media_id": f"{media_id:08X}",
        "version": f"{version:08X}",
        "base_version": f"{base_version:08X}",
        "platform": platform,
        "executable_type": executable_type,
        "disc_number": disc_number,
        "disc_count": disc_count,
        "savegame_id": f"{savegame_id:08X}",
        "game_identity_verified": False,
        "revision_verified": False,
        "note": "XEX metadata parsed only. Compare title/media IDs and trusted hashes against a verified Tekken 6 Rev 1 reference before declaring compatibility.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xex", help="path to a user-owned extracted default.xex")
    args = parser.parse_args()
    try:
        result = inspect_xex(args.xex)
    except (OSError, XexError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
