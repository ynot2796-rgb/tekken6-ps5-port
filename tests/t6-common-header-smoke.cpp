#include "intrin.h"
#include "t6_common.h"

void t6_common_header_compile_smoke() {
    LARGE_INTEGER counter{};
    QueryPerformanceCounter(&counter);
    (void)T6NowMs();
    (void)T6Open("/tmp/t6-port-smoke.log", "a");
}
