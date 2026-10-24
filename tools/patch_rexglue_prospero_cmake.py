#!/usr/bin/env python3
"""Patch the pinned ReXGlue SDK's CMake platform selection for an explicit Prospero target."""
from __future__ import annotations

import argparse
from pathlib import Path

PLATFORM_NEEDLE = '''if(WIN32)
    if(REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")
        set(REX_PLATFORM "win-amd64")
'''
PLATFORM_REPLACEMENT = '''option(REX_PLATFORM_PROSPERO "Build the ReXGlue SDK for PlayStation 5 Prospero" OFF)

if(REX_PLATFORM_PROSPERO)
    if(NOT REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")
        message(FATAL_ERROR "Prospero builds require the 64-bit x86 target")
    endif()
    set(REX_PLATFORM "prospero-amd64")
    add_compile_definitions(REX_PLATFORM_PROSPERO=1)
elseif(WIN32)
    if(REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")
        set(REX_PLATFORM "win-amd64")
'''
RPATH_NEEDLE = "if(UNIX AND NOT APPLE)\n    # Keep installed binaries self-contained by resolving shared libs relative"
RPATH_REPLACEMENT = "if(UNIX AND NOT APPLE AND NOT REX_PLATFORM_PROSPERO)\n    # Keep installed binaries self-contained by resolving shared libs relative"
OPTION_LINE = 'option(REX_PLATFORM_PROSPERO "Build the ReXGlue SDK for PlayStation 5 Prospero" OFF)'


def patch_cmake(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    changed = False

    if OPTION_LINE not in source:
        if source.count(PLATFORM_NEEDLE) != 1:
            raise ValueError("Expected exactly one pinned ReXGlue platform-selection block")
        source = source.replace(PLATFORM_NEEDLE, PLATFORM_REPLACEMENT, 1)
        changed = True
    elif source.count('set(REX_PLATFORM "prospero-amd64")') != 1:
        raise ValueError("Prospero option exists but its platform-selection block is incomplete")

    if RPATH_NEEDLE in source:
        if source.count(RPATH_NEEDLE) != 1:
            raise ValueError("Expected exactly one ELF RPATH block")
        source = source.replace(RPATH_NEEDLE, RPATH_REPLACEMENT, 1)
        changed = True
    elif RPATH_REPLACEMENT not in source:
        raise ValueError("Could not locate the pinned ReXGlue ELF RPATH block")

    if changed:
        path.write_text(source, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sdk_root", type=Path, help="ReXGlue SDK checkout root")
    args = parser.parse_args()
    target = args.sdk_root / "CMakeLists.txt"
    try:
        changed = patch_cmake(target)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print("Patched ReXGlue CMake for explicit Prospero selection." if changed else "Prospero CMake patch already present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
