# Native PS5 + PC cross-play implementation plan

Status: engineering plan, not a claim of implementation or compatibility.

## Goal

Run the Xbox 360-based Tekken 6 Native Online game on a jailbroken PS5 and match PC players running the same Native Online release. Preserve the PC project's deterministic simulation and online wire protocol wherever technically possible.

## Critical compatibility rule

Cross-play is not achieved by merely using GGPO on both platforms. The clients must agree on the game build/protocol version, session handshake, input serialization, frame numbering, rollback behavior, and match lifecycle. The PS5 renderer and input device may differ, but those differences must not alter deterministic simulation or the packets exchanged with PC.

## Recommended architecture

Keep the upstream project as the source of truth and isolate console-specific work behind a platform layer.

- `game_core`: ReXGlue-generated game code and the upstream netplay patches; do not fork game logic unless a PS5 blocker requires a documented change.
- `platform_ps5`: PS5 process lifecycle, filesystem, monotonic clock, controller mapping, audio output, threads/synchronization, and network sockets.
- `render_ps5`: replace or adapt the upstream Xenos/DirectX 12 rendering path. Do not assume a DirectX 12 API shim exists on PS5; first identify the actual graphics abstraction boundary and the GPU commands/resources emitted by the current renderer.
- `netplay_common`: upstream GGPO fork and game-side protocol code, compiled with a portable socket/timer abstraction. Keep packet layouts and protocol constants byte-for-byte compatible.
- `launcher_ps5`: native 16:9 controller-first menu for game build status, diagnostics, display/audio/control settings, and online status. No fake buttons or invented server addresses.
- `game_data`: user-provided compatible USA/Europe Rev 1 Xbox 360 image/extracted data; never bundle proprietary game content.

## Build order / acceptance gates

### Gate 0 — freeze and audit the target
- Pin an exact upstream Native Online release/source commit.
- Record submodule revisions, ReXGlue patch set, compiler assumptions, game build/version identifiers, and all Windows-only dependencies.
- Identify licenses and whether each dependency can be rebuilt for the target ABI.
- Deliverable: dependency map and a reproducible source manifest.

### Gate 1 — portable netplay compile target
- Make the GGPO fork and game-side netplay compile for a non-Windows target independently of the renderer.
- Replace WinSock calls with a narrow socket adapter; replace Windows timing and synchronization with monotonic-clock/thread adapters.
- Keep serialized packet layouts unchanged; add unit tests/golden byte vectors for packet encode/decode and handshake/version checks.
- Acceptance: host-side tests pass and the PC build remains unchanged.

### Gate 2 — native title shell
- Replace the current busy-loop diagnostic with a real PS5 render loop and DualSense input polling.
- Show a visible menu, diagnostics, build/version and runtime status; support clean exit/suspend behavior.
- Acceptance: repeatedly launches on the target firmware, renders at stable cadence, controller navigates, no busy loop, no SIGSYS.

### Gate 3 — game runtime and graphics
- Build generated game code for the target ABI only after auditing ReXGlue's x86/Windows ABI assumptions and generated code.
- Implement the minimum renderer required for a complete training/fight scene; map textures, shaders, render targets, depth/stencil, synchronization, and presentation correctly.
- Port audio, filesystem, timing and input. Use deterministic frame/tick control.
- Acceptance: local training/fight boots, character controls work, sound works, stable simulation and no platform-specific crash.

### Gate 4 — offline deterministic parity
- Add repeatable input recordings and state/checksum diagnostics on PC and PS5.
- Compare per-frame simulation checksums for identical inputs; fix sources of nondeterminism (floating-point flags, FMA, rounding, thread order, timers, uninitialized state).
- Acceptance: deterministic simulation parity for a defined test suite. Renderer pixels need not match exactly.

### Gate 5 — PC cross-play
- First test a PS5 client against the exact same official PC release and version, using authorized server configuration.
- Verify session handshake, input delay, rollback window, packet encoding, disconnect and reconnect behavior, NAT traversal, and match-end reporting.
- Run loss/latency tests and verify that both clients produce the same result.
- Acceptance: repeated full matches between PS5 and PC, logs proving same protocol/version and no desync.

### Gate 6 — newer online features
- Add group lobbies, spectating and practice tooling only after base matches and deterministic parity pass.
- Features requiring launcher/server support must be tested against the actual server protocol; do not assume a feature is client-only.

## Server constraints and fallback

The public source does not publish the official server endpoint/release API/pinned certificate configuration. Do not guess the address, disable certificate checks, spoof an identity, or claim official matchmaking works without authorization.

Preferred order:
1. Determine whether official server operators allow a PS5 client and obtain legitimate configuration.
2. If not, investigate a separately operated compatible server only if the protocol and applicable licenses permit it.
3. A private compatible server is not automatically cross-play: PC users must have a supported route to that same server, and protocol/version compatibility must be verified.

## Immediate next task

Audit the pinned upstream source and list the exact portability blockers by source file and dependency. Do not attempt to package the current diagnostic as a game. The next binary should be a visible PS5 menu/input/render test, followed by a portable GGPO/netplay compile target; neither should be represented as playable Tekken until it passes its acceptance gate.
