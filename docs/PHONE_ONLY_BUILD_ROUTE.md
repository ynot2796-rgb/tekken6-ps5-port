# Phone-only, zero-budget build route

## What we can do now

This repository includes a GitHub Actions Windows workflow that checks whether the public Native Online launcher source compiles and packages its Qt runtime. Standard GitHub-hosted runners are free for public repositories. This workflow intentionally builds the launcher only; it does not contain or build the game, and its placeholder launcher is not expected to connect to official matchmaking.

Workflow: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/workflows/windows-launcher-build.yml

## Why the actual game build is different

The game build requires the user's own compatible Xbox 360 Tekken 6 Rev 1 files and the upstream ReXGlue/toolchain setup. Neither the ISO nor extracted game data may be committed to this public repository or included in public artifacts. A public CI runner must never receive a private game ISO through a public URL, print its contents in logs, or upload generated game code as an artifact.

The upstream scripts reference a local toolchain directory and a Visual Studio installation. The public source tree does not itself guarantee that all required toolchain binaries are available in a clean cloud runner. The actual build needs a private, reproducible environment and enough disk space for the ISO, extraction, generated sources, and build output.

## Free cloud options and limits

- **GitHub Actions on this public repo:** good for source audits, compile checks, and building public launcher/test components. Standard hosted runners are free for public repositories. Do not put game files or secrets into this workflow.
- **GitHub Codespaces:** personal Free accounts include a monthly quota of 120 core-hours and 15 GB-month storage. Usage stops when the free quota is exhausted if no payment method is set. Codespaces are Linux-based by default, so a Windows-only build script will not run unchanged. The source/toolchain and ISO may also exceed available disk space.
- **Android phone:** suitable for managing GitHub, transferring files, and using a remote browser-based development environment, but not a proven replacement for the Windows/LLVM build toolchain.

## Next technical milestones

1. Get a green CI build of the public launcher and record any environment-specific failures.
2. Inspect upstream release assets/toolchain distribution to determine whether the game compiler can be installed in a clean environment without relying on files absent from the public repository.
3. Test whether a Linux-based Codespace can run the necessary code generation and Windows cross-compilation tools, without uploading the ISO to this public repo. Treat this as an experiment, not a guaranteed solution.
4. Only if the toolchain and storage requirements are satisfied, design a private workflow that accepts the user's own game files without logging, retaining, or publishing them. Do not implement a public ISO-upload workflow.
5. Build and validate on a Windows host if the Linux route fails; then test in MihawkOS on the user's PS5 firmware 13.60.

## Status terminology

- **Launcher CI:** checks the open-source Qt launcher only.
- **Game build:** requires user's own game data and the ReXGlue build toolchain.
- **PS5 compatibility:** requires testing the generated Windows executable on the actual PS5 runtime.
- **Online cross-play:** requires valid official server configuration/certificate and a real match against a PC client.

A successful launcher CI run does not imply that the game has been built, runs on PS5, or can connect online.
