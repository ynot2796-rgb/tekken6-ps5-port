#include "intrin.h"
#include "t6_common.h"
#include "t6_game_runtime.h"

static_assert(sizeof(t6::runtime::FrameInput) == 16);
static_assert(t6::runtime::callbacks_complete(t6::runtime::GameCallbacks{} ) == false);

void t6_common_header_compile_smoke() {
    LARGE_INTEGER counter{};
    QueryPerformanceCounter(&counter);
    (void)T6NowMs();
    (void)T6Open("/tmp/t6-port-smoke.log", "a");
}
