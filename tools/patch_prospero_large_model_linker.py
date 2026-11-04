#!/usr/bin/env python3
"""Patch the pinned Prospero PIE script for ReXGlue large-code-model sections."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch_prospero_large_model_linker.py PROSPERO_REFERENCE_ROOT")

root = Path(sys.argv[1]).resolve()
linker = root / "tooling/native/ps5-pie.ld"
if not linker.is_file():
    raise SystemExit(f"missing pinned Prospero linker script: {linker}")

source = linker.read_text(encoding="utf-8")
replacements = (
    ("*(.text .text.*)", "*(.text .text.* .ltext .ltext.* __lcxx_override)"),
    ("*(.rodata .rodata.*)", "*(.rodata .rodata.* .lrodata .lrodata.* .note.dlopen)"),
    ("*(.data .data.*)", "*(.data .data.* .ldata .ldata.*)"),
    ("*(.bss .bss.*)", "*(.bss .bss.* .lbss .lbss.*)"),
)
for original, patched in replacements:
    if patched in source:
        continue
    if source.count(original) != 1:
        raise SystemExit(f"expected exactly one linker pattern {original!r}; refusing unsafe patch")
    source = source.replace(original, patched, 1)

if not all(patched in source for _, patched in replacements):
    raise SystemExit("large-model linker section validation failed")
linker.write_text(source, encoding="utf-8")
print("Prospero linker script maps large-model code/data sections and libc++ override into correct segments.")
