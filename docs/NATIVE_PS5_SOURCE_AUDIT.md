# Native PS5 Port: Source Portability Audit

Status: source-level audit. A minimal diagnostic title has been built and launched, and the GGPO static library has cross-compiled for PS5; the Tekken 6 game executable has not been built.

## Target

Build a native PS5 homebrew application that reuses the public Tekken 6 Native Online code where technically possible, including the updated online gameplay features. MihawkOS / Prospero Win is not the primary target.

Upstream source: https://github.com/Ekspym/tekken6-native-online-source
Upstream project description and source layout: https://github.com/Ekspym/tekken6-native-online-source#readme

## Concrete findings from upstream CMakeLists.txt

1. The game target is C++23 and includes a long list of game integration files under `src/`, including `t6_netplay.cpp`, `t6_net_state.cpp`, `t6_snapshot.cpp`, `t6_session.cpp`, `t6_pads.cpp`, `t6_audio_step.cpp`, `t6_sound_boundary.cpp`, `t6_resim.cpp`, and `t6_resolution.cpp`.
2. The project links a GGPO fork, but its current build explicitly defines Windows macros and links `ws2_32` and `winmm`. These are not portable PS5 build settings; the networking/socket and timer/audio-adjacent dependencies need an abstraction or platform implementation.
3. The game build calls `rexglue_setup_target(tekken6 GPU_PLUGINS xenos)`. The Xenos GPU plugin is a major graphics dependency and cannot be assumed to work on PS5. A graphics backend or compatibility layer will be required.
4. The build applies `-mssse3` to the game target. CPU/compiler flags must be reviewed for the PS5's x86-64 target and the chosen SDK toolchain rather than copied blindly.
5. Windows-specific launch setup is explicit: MinGW uses `-municode -mwindows`; MSVC-ABI Windows builds set `WIN32_EXECUTABLE`. The current CMake configuration is not a native PS5 build recipe.
6. The game target links `rex::ui`, and the upstream launcher is a separate Qt 6 application. A PS5 homebrew should start with a console-native menu or minimal test harness rather than trying to port the Qt/Win32 launcher first.
7. The source README says the lobby server is not included in the public source and that official server address/release API/pinned certificate values are in unpublished launcher files. This is a concrete online integration blocker; do not invent endpoints or bypass authentication/certificate checks.

## Preserve the updated online functions

The port should aim to retain the upstream netplay/gameplay features—not replace them with a basic offline port:
- GGPO-style rollback and state/input synchronization.
- Match setup/session handling and controller input.
- Existing matchmaking/lobby integration and online settings where the required service configuration is legitimately available.
- Newer online features present in the selected upstream release, such as group lobbies and live spectating, only after the matching game-side code and server protocol dependencies are identified.

The PS5 build must match the PC version's protocol and deterministic game build before cross-play can be claimed. A successful compile alone does not prove online compatibility.

## Recommended engineering order

1. Freeze the intended upstream release/tag and inventory its actual online features and source dependencies.
2. Add a PS5 CMake/toolchain profile and compile a minimal homebrew ELF that launches on the user's supported setup. Keep this separate from the full game target.
3. Build a dependency map for socket APIs, timers, threads, atomics, file paths, memory allocation, controller input, audio, and renderer calls.
4. Isolate GGPO and the netplay logic behind platform interfaces; replace Windows socket/timer/input dependencies while preserving protocol behavior.
5. Prove a minimal render/input/audio loop on PS5 before attempting the Xenos renderer.
6. Integrate the game recompilation/runtime and assets locally supplied by the user; never commit game images, extracted assets, generated game code, server secrets, or private certificates.
7. Validate offline boot, stable 60 FPS timing, input/audio, rollback in a controlled test, lobby/matchmaking, and finally a cross-play match against the corresponding PC client.

## Current blockers

- No Tekken 6 game executable or package exists yet; the only console-tested package is a minimal process-liveness diagnostic.
- The PS5 toolchain has compiled the GGPO static library, but full game-target/toolchain integration remains unverified.
- Renderer/backend portability is unresolved.
- Official lobby endpoint and pinned certificate are absent from public source; online access cannot be promised until legitimate configuration and compatibility are established.
- The diagnostic has launched in the user's firmware 13.60 setup without an immediate crash, but graphics, input, audio, and game-runtime compatibility remain unverified.

## Honest status

This audit confirms that the existing source contains reusable netplay and gameplay integration code, but it is a Windows-oriented build with substantial platform and renderer dependencies. The next milestone is to get the deterministic/netplay game modules compiling against the PS5 target, then prove a native graphics/input loop. This is not a claim that Tekken 6 already runs on PS5.
