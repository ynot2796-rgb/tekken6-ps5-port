#include "t6_game_runtime.h"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>

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
  *static_cast<FakeGame*>(user);
  auto& game = *static_cast<FakeGame*>(user);
  __builtin_memcpy(dst, &game, sizeof(game));
  return 0;
}
int load(void* user, const void* src, std::size_t size) {
  if (!user || !src || size != sizeof(FakeGame)) return -1;
  __builtin_memcpy(user, src, sizeof(FakeGame));
  return 0;
}
}  // namespace

int main() {
  using namespace t6::runtime;
  FakeGame game;
  GameCallbacks callbacks{&game, init, shutdown, advance, state_size, save, load};
  assert(callbacks_complete(callbacks));
  assert(callbacks.initialize(callbacks.user) == 0);

  FrameInput input{};
  input.buttons = 0x25;
  assert(callbacks.advance_frame(callbacks.user, &input, 1) == 0);
  assert(game.frames == 1 && game.buttons == 0x25);

  std::array<std::byte, sizeof(FakeGame)> snapshot{};
  assert(callbacks.state_size(callbacks.user) == snapshot.size());
  assert(callbacks.save_state(callbacks.user, snapshot.data(), snapshot.size()) == 0);
  input.buttons = 0;
  assert(callbacks.advance_frame(callbacks.user, &input, 1) == 0);
  assert(game.frames == 2 && game.buttons == 0);
  assert(callbacks.load_state(callbacks.user, snapshot.data(), snapshot.size()) == 0);
  assert(game.frames == 1 && game.buttons == 0x25);

  callbacks.shutdown(callbacks.user);
  return 0;
}
