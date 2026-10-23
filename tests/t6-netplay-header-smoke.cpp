#include "intrin.h"
#include "t6_netplay_internal.h"

void t6_netplay_header_compile_smoke() {
    LARGE_INTEGER counter{};
    QueryPerformanceCounter(&counter);
    (void)counter.QuadPart;
}
