# Build plan from source (game files remain private)

## Current starting point

The user currently has the public Native Online source only and can transfer files to the PS5 from Android. No Windows game executable has been built yet.

Upstream build documentation: https://github.com/Ekspym/tekken6-native-online-source

## Required host environment

The upstream project documents a Windows 10/11 64-bit host with a DirectX 12-capable GPU for the normal release experience. The source build uses Git submodules, Python, clang plus MSVC ABI (or llvm-mingw for the game package), and Qt 6 with MSVC for the launcher. The exact required tool versions must be checked against the current upstream source and build scripts before attempting a build.

The user's own compatible Tekken 6 Xbox 360 USA/Europe Rev 1 ISO (or extracted disc folder) is required. The builder checks the version, extracts game data, translates Default.xex to C++, applies netplay patches, and compiles it. The game data and generated files must remain private and must not be committed to this repository.

## Steps when a suitable host is available

1. Download/clone the official source repository and initialize all submodules:
   `git submodule update --init --recursive`
2. Apply the project's ReXGlue patches:
   `python tools/apply_rexglue_patches.py`
3. Put the user's own compatible ISO in a private local location and use the upstream launcher builder or documented build scripts. Do not upload the ISO or generated game code to a public repository.
4. Build the game using the upstream documented path (`build_x360.cmd` for clang/MSVC ABI or `build_mingw.cmd` for llvm-mingw); build the launcher separately using `launcher\build.bat` and Qt 6/MSVC.
5. Save the full build log and generated Windows executable/package. Test it on a Windows host first to separate ordinary build errors from PS5 compatibility issues.
6. Test the built program in MihawkOS on PS5 firmware 13.60. If it fails, capture the exact message and logs; do not immediately modify GGPO or the graphics backend.
7. Only after offline launch/rendering/input/audio pass, test network access. Official server configuration and the pinned certificate are absent from the public source, so online cross-play remains blocked until the authorized configuration is obtained.

## Phone-only limitation

Android can transfer source and build artifacts but should not be treated as a proven environment for this Windows-oriented toolchain. GitHub-hosted CI may be useful for testing open-source components, but the actual game build needs the user's ISO and may be impractical to run as an ordinary public CI job. Do not store the ISO, game data, generated code, credentials, or private server configuration in a public repository or workflow log.

## Immediate decision

Before setting up a host, determine whether the user can access any Windows 10/11 PC temporarily (friend/family/workshop/library where permitted). If not, investigate a temporary remote Windows build host and its cost, GPU/DirectX availability, upload limits, privacy, and whether the user can transfer the large ISO securely. Do not promise a free cloud build until a viable provider and environment are verified.
