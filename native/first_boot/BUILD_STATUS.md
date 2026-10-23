# First-boot diagnostic build record

**Build result: CI package build passed. Console launch: not yet tested.**

- Workflow run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40034527509
- Workflow commit: `95faddb89d028968faf2857098e7b099c6ce7b72`
- Artifact name: `T6-PS5-native-diagnostic-95faddb89d028968faf2857098e7b099c6ce7b72`
- Artifact expiry: 2026-11-22
- Install ZIP: `PPSA99873.zip`
- SHA-256: `3b4b2eaa6ce4358fe8ef408bd8c43c5da64434804e7dec8a5b5db68b49c7fc74`

## What's inside

- `PPSA99873/eboot.bin`: signed native diagnostic executable.
- `PPSA99873/sce_sys/param.json`: title metadata.
- `PPSA99873/sce_sys/icon0.png`: generated 512x512 icon.
- `PPSA99873/sce_module/libc.prx`: checksum-verified clean-room runtime module used by the pinned public build tooling.

The ZIP has the expected title-folder root and no extra Lapy helper. The build job checks for the executable, runtime module, metadata and absence of the unused helper before publishing the artifact.

## What the diagnostic does

When launched, it sends a PS5 system notification saying the native title booted, waits 15 seconds, then exits. It is only a toolchain/packaging check. It is not Tekken 6 and does not test rendering, controller support, audio, rollback, matchmaking or cross-play.

## Install test

1. Download the ZIP and extract it once. The result must be a folder named `PPSA99873`, not a nested `PPSA99873/PPSA99873` folder.
2. Copy that folder into a directory ShadowMountPlus scans, commonly `/data/homebrew/PPSA99873`.
3. Confirm `eboot.bin` is directly inside `PPSA99873` and the folder/files are readable by the console. If your file-transfer app preserves restrictive permissions, set the folder tree to 777.
4. Wait for ShadowMountPlus to register the title, then launch **T6 Native Port Test** from the home screen.
5. Success means the notification appears and the app exits after about 15 seconds.

The title ID `PPSA99873` is a proposed development ID. Check for a conflict with an existing title on your console before copying it.

## Firmware limitation

The CI build passed, but the package has **not been run on a physical PS5**. In particular, firmware 13.60 compatibility is not yet confirmed. If it fails to register or launch, capture the exact error and, if available, the ShadowMountPlus/kernel log. Do not treat the build passing as proof of console compatibility.
