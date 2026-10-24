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


## Reuse implementation added

Rather than inventing a renderer or guessing at controller APIs, the repository now
has `.github/workflows/native-ps5-render-input-probe.yml`. It checks out
[Mihawk's PS5 Vulkan Template](https://github.com/mihawk-99/PS5_VulkanTemplate)
at fixed commit `91179df760df1e6c6f2d4d172bc435319d79ff3c`, bootstraps its matching
PS5_Vulkan / Mesa / PayloadSDK stack, generates a separate `PPSA99873` title named
`Tekken 6 Port Probe` from the upstream 3D starter, and packages the result as a
GitHub Actions artifact. This reuses the upstream title lifecycle, RADV/Vulkan
rendering, DualSense platform layer, and build/package scripts instead of copying
unverified API snippets into the old black-screen diagnostic.

The workflow is intentionally a **probe**, not Tekken gameplay: its purpose is to
produce a visible, controller-responsive native title that can be installed and
tested on the target console before ReXGlue game integration. It does not replace
the current diagnostic until the artifact builds successfully and the user verifies
visible output and controller response on firmware 13.60. The workflow is manually
runnable and also runs when this workflow or this audit document changes.

The upstream template's foundation is MIT-licensed; its optional UI kit is
GPL-3.0-or-later. This probe is generated without the optional UI kit. Its stack
still contains separately licensed dependencies, which must remain attributed in
any redistributed source or binary package. The pinned source revision is
recorded in the workflow so future upstream changes do not silently alter this
build.
