# Online Functions: PS5 Portability Notes

This document records source-level findings only. It does not claim online play works on PS5.

## Existing game-side integration

Files inspected in upstream `Ekspym/tekken6-native-online-source`:

- `src/t6_netplay.cpp`: shared state and memory/snapshot-related integration for the recompiled game.
- `src/t6_session.cpp`: GGPO session configuration, callbacks, input synchronization, frame boundaries, rollback/resimulation coordination, and session state.
- `src/t6_pads.cpp`: game controller/pad input hooks and input test/replay paths.

These are promising reuse points: the PS5 port should preserve the game-side deterministic frame flow and online session logic rather than implement a separate netcode from scratch.

## Port-specific issues visible in the source

- The session code uses environment-variable configuration such as `T6_NET`, `T6_NET_PLAYER`, `T6_NET_LOCAL_PORT`, `T6_NET_REMOTE`, `T6_NET_DELAY`, and `T6_NET_SEED`. These are development/runtime controls, not proof that the official matchmaking service is configured.
- The session integration calls the recompiled game's `XamInputGetState` path. The pad layer comments also reference `XInputGetState`. A native PS5 implementation must map DualSense/PS5 controller input into the game's expected logical input state while preserving deterministic input sampling.
- The top-level CMake currently links GGPO with `ws2_32` and `winmm`, so socket and timing dependencies need platform adapters or compatible implementations.
- The source contains rollback snapshot/resimulation machinery. Porting must preserve state capture/restore correctness; simply compiling GGPO without correct game-state rollback is not enough.

## Online feature preservation plan

1. Keep the upstream GGPO fork and game-side session/snapshot code as the initial reference implementation.
2. Define a small platform boundary for UDP/socket I/O, high-resolution monotonic timing, threads/synchronization, controller input, and logging.
3. Add PS5 implementations behind that boundary; avoid changing packet formats or timing semantics unless cross-platform testing proves it is necessary.
4. Keep matchmaking/lobby UI and service access separate from the in-match rollback transport. The public upstream README explicitly notes that official lobby endpoint and pinned-certificate configuration are not included.
5. Test in stages: two local builds on a controlled network, then two PS5 clients if possible, then PS5-to-PC cross-play against the matching upstream release. Only mark a feature supported after the test passes.

## Important limitation

Group lobbies, spectating, ranked/casual matchmaking, and other launcher/server features may depend on private service configuration or server behavior in addition to game-side code. Porting the game-side source alone cannot recreate missing server settings or guarantee that the service accepts a PS5 client.
