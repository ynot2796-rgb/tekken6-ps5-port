# Native diagnostic build and console test record

## Current test result

**Second diagnostic build: CI passed; user reports black screen with no immediate crash on the PS5.** This is a better result than the first build, which crashed with SIGSYS. It is still only a process-liveness test; it does not prove that graphics, input, audio, or the Tekken 6 game runtime works.

- Workflow run: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40035488841
- Workflow commit: `5363436d28564d56f03e89c76a34391b0d2e4621`
- Artifact name: `T6-PS5-native-diagnostic-5363436d28564d56f03e89c76a34391b0d2e4621`
- Artifact ID: `12535894417`
- Install ZIP: `PPSA99873.zip`
- SHA-256: `2f18884c7e2e9412e96f90db90c65b4a04bfb7849ef52284ed6a7c7a6d66631c`

## What this diagnostic does

This build sends a notification and then remains in a busy loop. It intentionally avoids the sleep call and returning from `main` to isolate the earlier SIGSYS. The black screen is expected. Close the app with the PS button; do not leave the busy loop running.

## Install/test notes

1. Extract the ZIP once. The result must be a folder named `PPSA99873`, not a nested `PPSA99873/PPSA99873` folder.
2. Copy that folder into a directory ShadowMountPlus scans, commonly `/data/homebrew/PPSA99873`.
3. Confirm `eboot.bin` is directly inside `PPSA99873` and the folder/files are readable by the console. If the file-transfer app preserves restrictive permissions, set the folder tree to 777.
4. Wait for ShadowMountPlus to register the title, then launch **T6 Native Port Test** from the home screen.

## Important limitation

This package is **not Tekken 6**. It contains no game code or game data and does not test rendering, controller support, audio, rollback, matchmaking, or cross-play. Do not treat this diagnostic as the actual port or as proof the game is ready.
