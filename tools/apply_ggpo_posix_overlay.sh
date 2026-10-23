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
echo "Applied POSIX GGPO platform and poll overlay to $GGPO"
