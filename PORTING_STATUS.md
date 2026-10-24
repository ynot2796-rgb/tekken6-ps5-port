# Porting status

## Confirmed from upstream source

- Native Online is a native Windows PC project, not an emulator package.
- It recompiles Xbox 360 game code through ReXGlue.
- It includes rollback networking based on a GGPO fork and game-side netplay/session/input integration.
- The public source does not include game code/data.
- The public source README says the official server address, release API, pinned server certificate, and launcher artwork are not published.
- The upstream CMake configuration links GGPO with Windows-specific libraries (`ws2_32`, `winmm`), uses a Xenos GPU plugin, applies x86-specific compiler flags, and configures Windows GUI entry points. This is not currently a PS5 build configuration.
- The public source repository is pinned at commit `24db272e03ab0e6c35f22abea519e76b22ecf450` (source release 2.3.5, dated 21 October 2026). The separate Native Online release repository has since published v2.4.0, v2.4.1 and v2.4.2 on 22–23 October 2026. Their release notes describe group lobbies/live spectating, rollback-related crash fixes, and a performance fix, but those later patch implementations are not present in the public source commit. Do not claim the native port includes the 2.4.x patches until matching source or a legitimate, testable implementation is available. References: https://github.com/Ekspym/tekken6-native-online-source/commit/24db272e03ab0e6c35f22abea519e76b22ecf450 and https://github.com/Ekspym/Tekken6-native-online/releases/latest.

## Route selection

**Primary route: native PS5 homebrew title.** The deliverable must be a real title folder registered by ShadowMountPlus, not a Windows executable or a payload-only demo.

The target is the updated Native Online experience—not merely offline Tekken 6. The currently available source includes the 2.3.5-era rollback/session integration and practice tools. The 2.4.x release notes advertise group lobbies/live spectating and additional rollback/performance fixes, but these later changes are not present in the pinned public source. They remain explicit porting targets, not implemented features; porting them requires the corresponding public source changes or a lawful, technically verifiable implementation, plus compatible service protocol access.

## Work recorded

- `docs/NATIVE_PS5_HOMEBREW_PORT.md`: native-port strategy and phased milestones.
- `docs/NATIVE_PS5_SOURCE_AUDIT.md`: source-level portability findings.
- `docs/ONLINE_PORTABILITY_NOTES.md`: session, rollback and input reuse points.
- `docs/PS5_MENU_AND_SETTINGS_SPEC.md`: controller-first menu, settings and UI acceptance criteria.
- `docs/PS5_TITLE_PACKAGING_AND_BOOT.md`: native title folder, runtime, signing, ShadowMountPlus and firmware-specific validation requirements.
- `native/first_boot/main.c`: first-boot notification diagnostic source, explicitly not the game.
- `native/first_boot/sce_sys/param.json`: proposed title metadata for the diagnostic.
- `native/first_boot/make_icon.py`: deterministic icon generator.
- `native/first_boot/BUILD_STATUS.md`: build record and console test results.
- `ports/ggpo-posix/`: POSIX implementation of GGPO platform timing and polling plus compatibility helpers.
- `include/ps5_compat/`: initial host-side Win32/Winsock compatibility headers for game helper code.
- `tools/prepare_ps5_game_source.sh`: applies the POSIX GGPO overlay and adjusts the upstream CMake target/link setup for a PS5/FreeBSD cross-build.
- `.github/workflows/ggpo-posix-compile.yml`: compiles, links, and executes a host-side GGPO polling/clock smoke test.
- `.github/workflows/ggpo-ps5-cross-compile.yml`: builds the actual upstream GGPO static library using the pinned PS5 SDK/toolchain, compiles the initial deterministic/netplay game-side modules against the PS5 compatibility layer, and uploads the GGPO archive.
- `.github/workflows/ps5-compat-smoke.yml`: compiles and exercises the first Win32/Winsock compatibility headers.
- `.github/workflows/native-ps5-diagnostic.yml`: CI build/package route using the public ProsperoStore native-app build tooling pinned to commit `3290ee0d43c5e8ac49870e7c7e84639374a56bf1`.

## Current status — do not overstate

Two native diagnostic builds were produced by CI. The first crashed on the user's PS5 with SIGSYS. The second build (`5363436d28564d56f03e89c76a34391b0d2e4621`) has now been tested by the user: it remains on a black screen without an immediate crash. This confirms the diagnostic process can stay running in the user's current setup; it does **not** confirm rendering, controller support, audio, game integration, or firmware-wide compatibility.

The second diagnostic deliberately avoids sleep and returning from `main`, using a busy loop to isolate the earlier crash. Close it with the PS button; do not leave it running. Artifact run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40035488841

**The full Tekken 6 Native Online game has not been built or booted yet. Progress since the previous status: the full upstream GGPO source set compiles and links on Linux with the POSIX overlay; its poll/clock smoke test passes; the same GGPO static library cross-compiles for the PS5 target using the pinned public PayloadSDK/toolchain; and the initial deterministic/session/netplay/resimulation/snapshot game-side modules now pass the PS5-target compile check. The compatibility-header, socket, POSIX GGPO, source-audit, and PS5 cross-compile workflows all pass on commit `3015eb22b753031dee9984c77c77a221bd09c7d6`. Evidence: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055627819, https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055627840, https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055632108, and https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40055627849.

The next engineering phase is no longer the initial netplay compile: it is the native title's graphics/runtime boundary and the ReXGlue-generated game target. The green CI compile is only a compile check, not a linked game executable. First prove a visible PS5 graphics/input loop; then integrate the generated ReXGlue game target and native platform services, and only then build and boot the full title. The pinned public source checkout contains no generated Tekken game code or assets; those must be generated from a compatible user-owned USA/Europe Rev 1 Xbox 360 ISO. Preserve the upstream GGPO rollback/session code and port it rather than replacing it with a separate netcode implementation.

## Latest graphics/input build checkpoint

- Latest attempted native graphics/input workflow before the current retry: [run 40060776596](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40060776596), commit `e4bfc76f0ba688fa36a348fb40e9186b2693a299`. It passed host dependency installation, then RADV's Meson configuration failed because the host LLVM/SPIR-V translator development package was missing: `Dependency "LLVMSPIRVLib" not found`.
- Corrective commit: `7627239f20e0850dbd0a6c55b469b2ff5565211c` ("Install LLVM SPIR-V development dependency for RADV build"). The native graphics/input workflow now installs Ubuntu 24.04's `libllvmspirvlib-18-dev` and `llvm-spirv-18`, matching the LLVM 18 host toolchain.
- Current retry: [run 40061787706](https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40061787706), on the corrective commit. Last checked: job still in progress during "Install host dependencies"; no result yet. Do not treat this fix as verified until RADV config/build passes.
- The workflow will then generate a separate `PPSA99874` title from the pinned PS5 Vulkan starter, build it, package it with SHA-256, and upload an artifact. The starter is a real Vulkan 3D sample with model animation, a settings overlay, and camera movement via the controller, but the generated title has not yet been built or tested on the user's console.
- This build retry is a graphics/input foundation only. The full Tekken 6 executable is still unbuilt; actual game-code generation requires the user's compatible game image locally, and console rendering/controller behavior must be physically verified.

## Unknown / blockers

- ReXGlue runtime and generated-game integration with the native app runtime is unverified; the game source has not yet been generated from the required user-owned ISO.
- Current successful PS5 CI builds compile the GGPO archive and selected game-side objects, but do not link a complete game executable or include a renderer. The next missing proof is a visible native graphics/input loop and then a renderer path that can replace/adapt the Xenos backend.
- The PS5 GGPO static library is cross-compiled, but the full Tekken executable and ReXGlue Xenos GPU plugin have not been built together or booted.
- Initial timer, WinSock startup, and debug/profiling compatibility shims exist; full game-side API coverage and controller/audio behavior are not yet validated. Console keyboard focus is intentionally treated as always focused and host keyboard input is disabled in the initial shim.
- The public source does not contain official lobby endpoint and pinned certificate configuration. Do not invent endpoints or bypass authentication/certificate checks.
- Official server/operator compatibility with a PS5 client is unverified.
- Source/release gap: the latest public source commit is 2.3.5, while the release page is at 2.4.2. The 2.4.0 group-lobby/spectating feature and 2.4.1/2.4.2 fixes cannot be assumed to exist in the source currently being cross-compiled.
- Cross-play with PC Native Online must be tested against the same compatible release/protocol; it cannot be promised from a successful build alone.

## Acceptance criteria

- Diagnostic title builds and launches from the home screen on the user's firmware 13.60 setup.
- Reproducible native PS5 build and launch instructions.
- No game image, extracted assets, generated game code, credentials, private certificates, or proprietary Sony modules bundled in the public repository.
- Correct controller input, audio, rendering, and stable gameplay timing.
- Existing rollback netplay preserved and tested.
- Updated online features implemented where their code and service protocol permit.
- Official matchmaking access only with legitimate configuration and verified compatibility.
- A cross-play test against the matching PC Native Online client passes before cross-play is described as working.
