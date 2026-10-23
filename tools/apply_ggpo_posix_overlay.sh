#!/usr/bin/env bash
# Apply the reviewed POSIX platform overlay to the pinned upstream GGPO tree.
# The upstream checkout is disposable; this script never changes upstream Git history.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${1:-$ROOT/.work/reference-sources/tekken6-native-online-source}"
GGPO="$SOURCE/third_party/ggpo/src/lib/ggpo"
test -f "$GGPO/types.h" || { echo "Missing pinned GGPO source at $GGPO" >&2; exit 2; }
cp "$ROOT/include/t6_socket_compat.h" "$GGPO/t6_socket_compat.h"
cp "$ROOT/ports/ggpo-posix/platform_linux.h" "$GGPO/platform_linux.h"
cp "$ROOT/ports/ggpo-posix/platform_linux.cpp" "$GGPO/platform_linux.cpp"
cp "$ROOT/ports/ggpo-posix/poll.cpp" "$GGPO/poll.cpp"
grep -q 'class Platform' "$GGPO/platform_linux.h"
grep -q '::poll(' "$GGPO/poll.cpp"
# Patch the upstream public header's Windows calling-convention annotation for POSIX.
python3 - "$SOURCE" <<'PY'
from pathlib import Path
import re, sys
source = Path(sys.argv[1])
header = source / "third_party/ggpo/src/include/ggponet.h"
text = header.read_text()
guard = "#ifndef __cdecl\n#  define __cdecl\n#endif\n"
if "#ifndef __cdecl" not in text:
    marker = "#define _GGPONET_H_\n"
    if marker not in text:
        raise SystemExit("Could not find ggponet.h include guard")
    text = text.replace(marker, marker + "\n" + guard, 1)
header.write_text(text)

main = source / "third_party/ggpo/src/lib/ggpo/main.cpp"
text = main.read_text()
pattern = r"BOOL WINAPI\s+DllMain\(.*?return TRUE;\s*\}"
match = re.search(pattern, text, flags=re.S)
if match and "#ifdef _WIN32\n" + match.group(0) not in text:
    text = text[:match.start()] + "#ifdef _WIN32\n" + match.group(0) + "\n#endif" + text[match.end():]
main.write_text(text)
PY

echo "Applied POSIX GGPO platform, public-header, and poll overlay to $GGPO"
