#!/usr/bin/env python3
"""Regression tests for the Prospero large-code-model linker patch."""
from pathlib import Path
import subprocess
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "patch_prospero_large_model_linker.py"

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    linker = root / "tooling/native/ps5-pie.ld"
    linker.parent.mkdir(parents=True)
    linker.write_text("""
SECTIONS {
  .text : { *(.text .text.*) } : text
  .rodata : { *(.rodata .rodata.*) } : ro
  .data : { *(.data .data.*) } : data
  .bss : { *(.bss .bss.*) *(COMMON) } : data
}
""")
    first = subprocess.run(["python3", str(SCRIPT), str(root)], text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    patched = linker.read_text()
    assert "*(.text .text.* .ltext .ltext.* __lcxx_override)" in patched
    assert "*(.rodata .rodata.* .lrodata .lrodata.* .note.dlopen)" in patched
    assert "*(.data .data.* .ldata .ldata.*)" in patched
    assert "*(.bss .bss.* .lbss .lbss.*)" in patched
    second = subprocess.run(["python3", str(SCRIPT), str(root)], text=True, capture_output=True)
    assert second.returncode == 0, second.stderr
    assert linker.read_text() == patched

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "tooling/native").mkdir(parents=True)
    (root / "tooling/native/ps5-pie.ld").write_text("SECTIONS { .text : { *(.text) } }")
    result = subprocess.run(["python3", str(SCRIPT), str(root)], text=True, capture_output=True)
    assert result.returncode != 0
    assert "expected exactly one linker pattern" in result.stderr

print("Prospero large-model linker patch tests passed.")
