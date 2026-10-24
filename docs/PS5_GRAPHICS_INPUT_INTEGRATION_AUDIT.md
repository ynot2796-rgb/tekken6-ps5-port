# PS5 graphics and controller integration audit

## Result of the next-step investigation

The current native diagnostic is not a graphics test: `native/first_boot/main.c`
sends a notification and then spins forever. Its black screen is expected. The
next milestone must replace that liveness-only loop with a bounded native
render/input probe before attempting to boot generated Tekken game code.

A public reference project, [TheSimpsonsGame-PS5-Builder](https://github.com/LoZazaMastro/TheSimpsonsGame-PS5-Builder),
documents a native Prospero runtime using Vulkan/RADV for rendering,
`scePad` for DualSense input, and `sceAudioOut` for audio. Its README pins a
specific PS5 Payload SDK and Mesa/RADV source revision and documents title
packaging. This establishes a plausible public implementation route, not
drop-in compatibility with Tekken 6.

Reference findings:
- `prospero/README.md`: pinned build environment, native title packaging,
  and separate user-supplied game-data staging.
- `tools/rexglue-sdk/src/input/prospero/prospero_input_driver.cpp`: maps
  native `scePad` state to the XInput-style state expected by recompiled games.
- `prospero/radv/README.md`: display integration is tied to a specific Mesa
  revision and PS5 SDK; host-side tests do not prove behavior on a real console.
- `prospero/tests/prospero_input_host.cpp`: extensive host-fixture tests cover
  input mapping and edge cases, but mocked native APIs are not a physical PS5
  controller test.

## Integration decision

Do not copy the reference runtime wholesale or mix arbitrary SDK/Mesa versions.
First inventory the reference project's license notices and build pins, then
create a small native graphics/input probe using a single consistent public
PayloadSDK + RADV/Vulkan dependency set. The probe should:
1. initialize the display/graphics API and render a changing, clearly visible
   frame (not just a notification or black clear);
2. poll DualSense input through `scePad` and visibly change a marker/state;
3. log initialization failures and exit/close cleanly where supported;
4. be packaged as a native title and tested on the user's firmware 13.60 console;
5. only after that, become the platform shell for the ReXGlue-generated game
   target and its Xenos graphics-backend replacement.

## Gate before game integration

The current port repository does not yet have a linked Vulkan renderer, native
input loop, generated Tekken game target, or a complete game executable. The
successful GGPO/compatibility builds remain component-level evidence only.
The graphics/input milestone is **not complete** until the probe visibly renders
on the actual PS5 and responds to the controller. Online service endpoints,
certificates, and PC cross-play must remain unclaimed until independently
verified.
