#!/usr/bin/env python3
"""Generate a simple 512x512 PNG title icon using only the Python standard library."""
import struct
import sys
import zlib

SIZE = 512
pixels = bytearray()
glyphs = {
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
}
scale = 34
glyph_gap = 18
glyph_width = 5 * scale
total_width = glyph_width * 2 + glyph_gap
start_x = (SIZE - total_width) // 2
start_y = (SIZE - 7 * scale) // 2

for y in range(SIZE):
    pixels.append(0)
    for x in range(SIZE):
        t = (x + y) / (2 * (SIZE - 1))
        r = int(10 + 24 * t)
        g = int(18 + 18 * t)
        b = int(42 + 54 * t)
        if 72 <= y < 82 and 84 <= x < 428:
            r, g, b = 244, 184, 82
        for glyph_index, glyph_name in enumerate(("T", "6")):
            gx = start_x + glyph_index * (glyph_width + glyph_gap)
            if gx <= x < gx + glyph_width and start_y <= y < start_y + 7 * scale:
                col = (x - gx) // scale
                row = (y - start_y) // scale
                if glyphs[glyph_name][row][col] == "1":
                    r, g, b = 244, 247, 255
        pixels.extend((r, g, b, 255))

def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(bytes(pixels), 9))
png += chunk(b"IEND", b"")
path = sys.argv[1] if len(sys.argv) > 1 else "native/first_boot/sce_sys/icon0.png"
with open(path, "wb") as out:
    out.write(png)
print(f"Wrote {path} ({SIZE}x{SIZE})")
