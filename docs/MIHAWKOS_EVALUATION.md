# MihawkOS evaluation for Tekken 6 Native Online

**First compatibility target: MihawkOS, with Prospero Win as a secondary comparison.** This is a test plan, not a claim that Tekken currently runs on PS5.

Project: https://github.com/mihawk-99/PS5_MihawkOS  
Releases: https://github.com/mihawk-99/PS5_MihawkOS/releases  
Native Online source: https://github.com/Ekspym/tekken6-native-online-source

## Why test MihawkOS first

The MihawkOS project documents a Wine/Proton compatibility stack with DXVK for Direct3D 8–11 and VKD3D-Proton for Direct3D 12, plus networking, XInput/DualSense input and audio. Its current repository documents payload acceptance through firmware 13.60, but console validation has been reported on a standard PS5 at 13.40 and a PS5 Pro at 10.01; firmware 13.60 and this specific game remain unverified.

This makes MihawkOS a promising compatibility experiment because the Native Online project targets Windows. It does not guarantee that its custom Xenos graphics backend, Qt launcher, runtime dependencies, or game builder will work under Wine.

## Critical build limitation

The public Native Online repository requires a compatible copy of Tekken 6 Xbox 360 (USA/Europe, Rev 1) to generate the game's native code. This port project must not package game data or copyrighted generated files. The published build steps use Windows-oriented scripts ("build_x360.cmd" / "build_mingw.cmd") and the launcher uses Qt 6. The source-only repository is not a ready-to-run Windows executable.

The user's Android phone can transfer files, but cannot be assumed to provide the full host toolchain or the Linux/Windows environment required by the build. Do not claim the game can be built on the PS5 or phone until that path is tested. A cloud CI build may help with open-source launcher/probe components, but cannot produce the user's game without their own input files.

## Test order

1. Inspect the current upstream source and exact graphics API/backend dependencies.
2. Establish a reproducible Windows/Linux build of the public launcher and non-game components, without adding game data or secrets.
3. Build the actual game only from the user's own legally obtained compatible game files in a suitable host environment.
4. Add the resulting Windows program to MihawkOS using its official instructions; test offline startup before online.
5. Record runtime version, PS5 firmware, exact error text, and logs for each failure.
6. Test controller, audio, rendering, frame pacing and networking separately.
7. Attempt cross-play only after the official service configuration is available and service access is authorized.

## Online compatibility blocker

The Native Online source README says the official server endpoint, release API configuration, pinned TLS certificate and official launcher resources are not published. The GGPO fork is present in source, but preserving GGPO alone does not ensure matchmaking or cross-play: the client must also use the correct protocol, server configuration and certificate. Do not guess endpoints or disable TLS validation.

## Pass criteria

- Launches on the user's actual firmware and runtime build.
- Renders gameplay and accepts controller input.
- Audio and timing are stable.
- Network connection validates TLS normally.
- A real match succeeds with an unmodified PC Native Online player on the same supported release.

Until these checks pass, classify the work as feasibility testing, not a completed PS5 port.
