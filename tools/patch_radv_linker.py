#!/usr/bin/env python3
"""Apply the documented LLVM 18 workaround to the pinned PS5 RADV title linker."""
from __future__ import annotations

import argparse
from pathlib import Path

NEEDLE = '"$sdk_root/bin/prospero-lld" "${radv_linker_script[@]}"'
REPLACEMENT = '"$sdk_root/bin/prospero-lld" --no-dynamic-linker "${radv_linker_script[@]}"'


def patch_linker_script(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    old_count = source.count(NEEDLE)
    new_count = source.count(REPLACEMENT)

    if old_count == 1 and new_count == 0:
        path.write_text(source.replace(NEEDLE, REPLACEMENT), encoding="utf-8")
        return True
    if old_count == 0 and new_count == 1:
        return False  # Already patched; make retries safe.
    raise ValueError(
        "Expected exactly one unpatched RADV link command, or exactly one "
        f"already-patched command; found unpatched={old_count}, patched={new_count}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("linker_script", type=Path)
    args = parser.parse_args()
    try:
        changed = patch_linker_script(args.linker_script)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print("Applied RADV LLVM 18 linker workaround." if changed else "RADV linker workaround already present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
