# PC5 repository reuse audit

Date: 24 October 2026

Candidate: https://github.com/bornaradusin/PC5

## Decision

**Use PC5 as a platform implementation reference; do not make it the Tekken runtime.** PC5 is a launcher for Windows PE programs through `prospero-win` (Wine, DXVK, VKD3D-Proton and RADV). It does not execute Xbox 360 XEX/ISO code and cannot replace the ReXGlue-generated Tekken 6 runtime or PS5X360.

## Relevant source paths verified in PC5

- `title/pc5_game_ps5.c`: direct PS5 APIs for DualSense light-bar and adaptive-trigger effects, video-out cursor overlay, CPU/SOC temperature and memory telemetry. This is useful when adding platform-specific feedback/diagnostics; its ABI declarations and memory assumptions must be checked against our pinned SDK before any reuse.
- `title/pc5_controls.c` and the corresponding `title/pc5_controls.h`: maps controller choices and button/key bindings for PC5's Windows-game use case. The policy/configuration model is useful, but it is not a native Tekken gameplay input adapter.
- `title/pc5_game.c` / `title/pc5_game.h`: PC5's process-launch, monitoring and close/return-to-launcher flow is a reference for lifecycle design. Tekken's native title has a different process model, so don't transplant the launcher process orchestration.
- `title/pc5_logs.c` / `title/pc5_logs.h`: classifies session logs and retains logs for failures. Adapt the diagnostic principles to the native title rather than importing Wine-specific log parsing.
- `title/pc5_console.c`, `title/pc5_draw.c`, `title/pc5_ui.c`: examples of a PS5-native shell, drawing and controller-driven UI. The existing probe is a smaller, verified starting point; the game's render path should not depend on the PC5 launcher UI.
- `patches/prospero-win/`: patches to Wine/compatibility-runtime behavior. These only matter if we later test a Windows build of Tekken (which is not the Xbox 360 release); they are not a substitute for porting ReXGlue or running Xbox 360 code.

## Integration plan

1. Keep the existing native PS5 Vulkan probe and its successful CI path as the baseline.
2. Compare PC5's PS5-specific calls and lifecycle/logging patterns against the exact PS5 SDK/template revision already pinned in this repository.
3. Prefer implementing a small platform adapter in our project (pad sample, exit request, log sink, optional light-bar/trigger effects) behind the existing game/runtime interface. Keep it independent of PC5 UI and Wine.
4. Test the adapter in the native probe first. Only use APIs confirmed by the pinned SDK/import validation; do not guess function signatures or copy ABI structures without verification.
5. Continue the separate main port path: compile the pinned ReXGlue runtime's existing Xenos Vulkan backend for Prospero, then integrate the user's locally generated Tekken code and game-specific adaptations.
6. Treat PC5 as an optional console-side test harness/reference only. Do not make the final game depend on PC5 being installed.

## Licensing and distribution

PC5's `NOTICE.md` says its own `title/`, `tools/`, `tests/`, `art/` and `patches/` code is LGPL-2.1-or-later, while its assembled app also includes other components under their own terms. If we copy or adapt source, preserve file-level copyright/SPDX notices and comply with the relevant license; audit the resulting project's distribution license before merging code. For now, this audit adds no PC5 source code to this repository.

## Limits / evidence

- Repository description and README identify PC5 as a Windows-game launcher on top of prospero-win.
- The inspected source confirms concrete PS5 APIs for DualSense effects, overlay/telemetry, and PC5-specific controller and logging logic.
- These findings identify reusable platform techniques, not a tested Tekken integration. No PC5 code has been compiled into the Tekken project, and no Xbox 360 game code/assets are in CI.
- PC5 itself cannot transform the Xbox 360 ISO into native PS5 code. The remaining game-specific gate is still ReXGlue/Xenos Vulkan + generated Tekken code, followed by console testing.
