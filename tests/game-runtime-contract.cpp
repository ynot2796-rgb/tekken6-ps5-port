#include "t6_game_runtime.h"
#include "t6_input_adapter.h"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace {
struct FakeGame {
  std::uint32_t frames = 0;
  std::uint32_t buttons = 0;
};
int init(void*) { return 0; }
void shutdown(void*) {}
int advance(void* user, const t6::runtime::FrameInput* inputs, std::size_t count) {
  if (!user || !inputs || count != 1) return -1;
  auto& game = *static_cast<FakeGame*>(user);
  ++game.frames;
  game.buttons = inputs[0].buttons;
  return 0;
}
std::size_t state_size(void*) { return sizeof(FakeGame); }
int save(void* user, void* dst, std::size_t size) {
  if (!user || !dst || size != sizeof(FakeGame)) return -1;
  const auto& game = *static_cast<FakeGame*>(user);
  std::memcpy(dst, &game, sizeof(game));
  return 0;
}
int load(void* user, const void* src, std::size_t size) {
  if (!user || !src || size != sizeof(FakeGame)) return -1;
  std::memcpy(user, src, sizeof(FakeGame));
  return 0;
}
}  // namespace

int main() {
  using namespace t6::runtime;
  FakeGame game;
  GameCallbacks callbacks{&game, init, shutdown, advance, state_size, save, load};
  assert(callbacks_complete(callbacks));

  // Input capture is stable and normalized before simulation/rollback.
  PadSample pad{};
  pad.connected = true;
  pad.game_buttons = 0x1234;
  pad.left_x = 0;
  pad.left_y = 128;
  pad.right_x = 255;
  pad.right_y = 128;
  pad.left_trigger = 42;
  pad.right_trigger = 200;
  const FrameInput captured = capture_frame_input(pad, 1);
  assert(captured.buttons == 0x1234 && captured.player == 1);
  assert(captured.left_x == -32768 && captured.left_y == 0);
  assert(captured.right_x == 32767 && captured.right_y == 0);
  assert(captured.left_trigger == 42 && captured.right_trigger == 200);

  // Values immediately around center remain signed and deterministic.
  assert(normalize_axis(127) == -256);
  assert(normalize_axis(128) == 0);
  assert(normalize_axis(129) == 258);

  // Once captured, frame input is a value snapshot; later hardware changes
  // must not mutate it. Rollback reuses this value instead of polling again.
  pad.game_buttons = 0;
  pad.left_x = 128;
  assert(captured.buttons == 0x1234 && captured.left_x == -32768);

  // Disconnection must neutralize every gameplay control, not just buttons.
  pad.connected = false;
  pad.left_x = 0;
  pad.left_y = 255;
  pad.right_x = 0;
  pad.right_y = 255;
  pad.left_trigger = 255;
  pad.right_trigger = 255;
  const FrameInput disconnected = capture_frame_input(pad, 0);
  assert(disconnected.buttons == 0 && disconnected.left_x == 0 &&
         disconnected.left_y == 0 && disconnected.right_x == 0 &&
         disconnected.right_y == 0 && disconnected.left_trigger == 0 &&
         disconnected.right_trigger == 0 && disconnected.player == 0);

  // Missing mandatory callbacks must fail closed before the runtime starts.
  auto incomplete = callbacks;
  incomplete.load_state = nullptr;
  assert(!callbacks_complete(incomplete));

  assert(callbacks.initialize(callbacks.user) == 0);
  FrameInput input{};
  input.buttons = 0x25;
  assert(callbacks.advance_frame(callbacks.user, &input, 1) == 0);
  assert(game.frames == 1 && game.buttons == 0x25);

  // A rollback snapshot must restore the exact simulation state.
  std::array<std::byte, sizeof(FakeGame)> snapshot{};
  assert(callbacks.state_size(callbacks.user) == snapshot.size());
  assert(callbacks.save_state(callbacks.user, snapshot.data(), snapshot.size()) == 0);

  input.buttons = 0;
  assert(callbacks.advance_frame(callbacks.user, &input, 1) == 0);
  assert(game.frames == 2 && game.buttons == 0);

  // Rewind, replay the identical captured input, and compare the result.
  const FakeGame expected = game;
  assert(callbacks.load_state(callbacks.user, snapshot.data(), snapshot.size()) == 0);
  assert(game.frames == 1 && game.buttons == 0x25);
  assert(callbacks.advance_frame(callbacks.user, &input, 1) == 0);
  assert(std::memcmp(&game, &expected, sizeof(game)) == 0);

  // Invalid snapshot sizes and missing buffers must be rejected.
  assert(callbacks.save_state(callbacks.user, snapshot.data(), snapshot.size() - 1) != 0);
  assert(callbacks.load_state(callbacks.user, snapshot.data(), snapshot.size() - 1) != 0);
  assert(callbacks.save_state(callbacks.user, nullptr, snapshot.size()) != 0);
  assert(callbacks.load_state(callbacks.user, nullptr, snapshot.size()) != 0);

  callbacks.shutdown(callbacks.user);
  return 0;
}
