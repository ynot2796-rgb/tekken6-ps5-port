#!/usr/bin/env python3
"""Verify the pinned PS5X360 source contracts used by the Tekken port.

This is a source audit, not a native title build. It deliberately fails closed if
the pinned upstream structure changes, so the integration plan cannot silently
drift to a different runtime or link recipe.
"""
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "PS5X360")
CHECKS = {
    "native entry point": (
        "src/native_game_main.cpp",
        [
            'xe::Emulator emulator(',
            "scePadReadState",
            "xbox360ps5::NativeAudioSystem",
            "xe::gpu::vulkan::VulkanGraphicsSystem",
            'sceSystemServiceHideSplashScreen()',
        ],
    ),
    "PS5 memory adapter": (
        "platform/ps5/native_memory_calls.cpp",
        [
            "sceKernelMmap",
            "sceKernelMprotect",
            "sceKernelMunmap",
            "__wrap_mmap",
            "__wrap_mprotect",
            "__wrap_munmap",
        ],
    ),
    "native title linker recipe": (
        "tools/build-native-game.sh",
        [
            "prospero-lld",
            "radv_link_recipe",
            "--wrap=mmap",
            "--version-script",
            "native_app_builder.cpp",
            "package-game.py",
        ],
    ),
    "PS5 platform patch": (
        "patches/canary/xbox360ps5.patch",
        [
            "XE_PLATFORM_PS5",
            "CLOCK_MONOTONIC_RAW",
            'return "/download0"',
            "memory_posix",
        ],
    ),
}

failed = False
for label, (relative, markers) in CHECKS.items():
    path = ROOT / relative
    if not path.is_file():
        print(f"FAIL {label}: missing {relative}")
        failed = True
        continue
    data = path.read_text(encoding="utf-8", errors="replace")
    missing = [marker for marker in markers if marker not in data]
    if missing:
        print(f"FAIL {label}: {relative} missing markers: {missing}")
        failed = True
    else:
        print(f"PASS {label}: {relative} ({len(markers)} contract markers)")
if failed:
    raise SystemExit(1)
print("PASS pinned PS5X360 source contracts; this does not prove a Tekken build or console boot.")
