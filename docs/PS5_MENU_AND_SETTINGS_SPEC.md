# PS5 in-game menu and settings plan

This is the UI specification for the native Tekken 6 Native Online port. It is not yet an implemented or runnable menu. The first black-screen diagnostic only proves the title process can stay alive.

## Design direction

Use a controller-first, 16:9 interface with a dark charcoal background, Tekken-red accent, high-contrast text, a clear selected-row highlight, and consistent spacing. Avoid tiny PC-style controls. Every menu must be navigable with DualSense and usable from a TV viewing distance.

## Main menu

1. **Play** — launch the locally built game when the native game runtime is integrated.
2. **Online** — connection status, ranked/casual search, lobby browser, create/join room, invite/join flow where supported by the upstream service.
3. **Practice** — local practice launch, frame-data/HUD options when the corresponding upstream features are integrated.
4. **Settings** — video, audio, controls, gameplay, network, and interface.
5. **Diagnostics** — build/version, runtime compatibility, controller test, network test, logs, and copy/export log.
6. **Credits & licenses** — attribution and open-source license notices.

## Settings pages

### Video
- Display mode / resolution choices supported by the PS5 renderer.
- Internal resolution: Original / Lower / Lowest, only where the port can honor those modes.
- V-sync and frame pacing options only if the renderer exposes safe controls.
- HUD scale and safe-area adjustment.
- Show FPS / frame-time overlay.

### Audio
- Master, music, effects, and voice volume where independent buses exist.
- Output device and latency settings only if supported by the native audio layer.
- Audio test.

### Controls
- DualSense mapping to Tekken's logical gamepad state.
- Button remapping, dead-zone only if analog input is used, vibration toggle if supported.
- Input test page and reset-to-defaults.

### Gameplay
- Practice HUD and frame-data options from upstream where available.
- Training/reset shortcuts.
- Determinism/rollback diagnostics kept separate from normal play.

### Online
- Status and ping display, connection test, input delay display.
- Rollback/network diagnostics and log export.
- Lobby/matchmaking features only after service configuration and protocol compatibility are verified.
- Do not invent server addresses or disable TLS/certificate checks to make a connection appear to work.

### Interface
- UI scale, menu sound, confirm/cancel button convention, reduced motion, and reset settings.
- Persist settings in a writable user-data location, with safe defaults if the save file is missing or invalid.

## Implementation gates

1. Establish a supported native PS5 rendering and controller-input path on the user's firmware 13.60 setup.
2. Implement a small interactive menu shell and prove D-pad/stick navigation, confirm/back, and settings persistence.
3. Connect menu actions to a real game launch only after the ReXGlue-generated game runtime is building and rendering.
4. Integrate upstream GGPO/session code behind platform abstractions; keep online UI disabled or clearly marked unavailable until service configuration is legitimate and verified.
5. Test each setting on console before showing it as supported.

## Current hard blockers

- The existing diagnostic has no renderer or controller input and therefore cannot display this menu yet.
- Upstream uses Windows networking/timing libraries, a Xenos GPU plugin, and a Qt/Win32 launcher; none can be assumed to work natively on PS5.
- The public upstream repository excludes game code/data. The user's own compatible Tekken 6 Xbox 360 USA/Europe Rev 1 disc dump is required for the ReXGlue build.
- Official matchmaking endpoint and pinned certificate configuration are not included in the public source.

## Acceptance standard

Do not ship placeholder buttons that do nothing. Each visible menu item must either perform its action or be clearly marked unavailable. Do not call the port playable until the game renders, DualSense works, and offline gameplay has been tested; do not call online functional until rollback and actual matchmaking/session tests pass.
