#!/usr/bin/env python3
"""Apply the LLVM 18 weak-entrypoint workaround to a pinned PS5 RADV link script."""
from __future__ import annotations

import argparse
from pathlib import Path

NEEDLES = (
    '"$sdk_root/bin/prospero-lld" "${radv_linker_script[@]}"',
    '"$sdk/bin/prospero-lld" "${radv_linker_script[@]}"',
)
REPLACEMENTS = tuple(
    needle.replace('prospero-lld" "', 'prospero-lld" --no-dynamic-linker "')
    for needle in NEEDLES
)


def patch_linker_script(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    old_count = sum(source.count(needle) for needle in NEEDLES)
    new_count = sum(source.count(replacement) for replacement in REPLACEMENTS)

    if old_count == 1 and new_count == 0:
        for needle, replacement in zip(NEEDLES, REPLACEMENTS):
            if needle in source:
                path.write_text(source.replace(needle, replacement), encoding="utf-8")
                return True
        raise AssertionError("Link command count changed unexpectedly")
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
