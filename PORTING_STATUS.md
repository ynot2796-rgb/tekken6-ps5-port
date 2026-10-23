# Porting status

## Confirmed from upstream source

- Native Online is a native Windows PC project, not an emulator package.
- It recompiles Xbox 360 game code through ReXGlue.
- It includes rollback networking based on a GGPO fork and game-side netplay/session/input integration.
- The public source does not include game code/data.
- The public source README says the official server address, release API, pinned server certificate, and launcher artwork are not published.
- The upstream CMake configuration links GGPO with Windows-specific libraries (`ws2_32`, `winmm`), uses a Xenos GPU plugin, applies x86-specific compiler flags, and configures Windows GUI entry points. This is not currently a PS5 build configuration.
- Upstream releases currently list Native Online v2.4.0, published 22 October 2026. The selected target must track the current public source/features, not an older demo.

## Route selection

**Primary route: native PS5 homebrew title.** The deliverable must be a real title folder registered by ShadowMountPlus, not a Windows executable or a payload-only demo.

The target is the updated Native Online experience—not merely offline Tekken 6. Desired retained functionality includes rollback netplay, online sessions/lobbies and matchmaking, and newer features such as practice-mode tools, group lobbies/spectating where their code and compatible service protocol permit.

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
- `.github/workflows/ggpo-ps5-cross-compile.yml`: builds the actual upstream GGPO static library using the pinned PS5 SDK/toolchain and uploads the archive.
- `.github/workflows/ps5-compat-smoke.yml`: compiles and exercises the first Win32/Winsock compatibility headers.
- `.github/workflows/native-ps5-diagnostic.yml`: CI build/package route using the public ProsperoStore native-app build tooling pinned to commit `3290ee0d43c5e8ac49870e7c7e84639374a56bf1`.

## Current status — do not overstate

Two native diagnostic builds were produced by CI. The first crashed on the user's PS5 with SIGSYS. The second build (`5363436d28564d56f03e89c76a34391b0d2e4621`) has now been tested by the user: it remains on a black screen without an immediate crash. This confirms the diagnostic process can stay running in the user's current setup; it does **not** confirm rendering, controller support, audio, game integration, or firmware-wide compatibility.

The second diagnostic deliberately avoids sleep and returning from `main`, using a busy loop to isolate the earlier crash. Close it with the PS button; do not leave it running. Artifact run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40035488841

**The full Tekken 6 Native Online game has not been built or booted yet.** Progress since the previous status: the full upstream GGPO source set now compiles and links on Linux with the POSIX overlay; its poll/clock smoke test passes; the same GGPO static library cross-compiles successfully for the PS5 target using the pinned public PayloadSDK/toolchain. The POSIX polling replacement and initial Win32/Winsock host compatibility headers are in the repository. Successful checks: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40040675791 and https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40040675801.

The next engineering phase is to integrate the game-side host API shims and generated ReXGlue game target, then build and boot the full title. The pinned public source checkout contains no generated Tekken game code or assets; those must be generated from a compatible user-owned USA/Europe Rev 1 Xbox 360 ISO. Preserve the upstream GGPO rollback/session code and port it rather than replacing it with a separate netcode implementation.

## Unknown / blockers

- ReXGlue runtime and generated-game integration with the native app runtime is unverified; the game source has not yet been generated from the required user-owned ISO.
- The PS5 GGPO static library is cross-compiled, but the full Tekken executable and ReXGlue Xenos GPU plugin have not been built together or booted.
- Initial timer, WinSock startup, and debug/profiling compatibility shims exist; full game-side API coverage and controller/audio behavior are not yet validated. Console keyboard focus is intentionally treated as always focused and host keyboard input is disabled in the initial shim.
- The public source does not contain official lobby endpoint and pinned certificate configuration. Do not invent endpoints or bypass authentication/certificate checks.
- Official server/operator compatibility with a PS5 client is unverified.
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
