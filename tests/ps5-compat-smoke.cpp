#include "windows.h"
#include "winsock2.h"
#include "mmsystem.h"
#include "intrin.h"

#include <cstdio>
#include <string>

int main() {
    LARGE_INTEGER frequency{}, before{}, after{};
    if (!QueryPerformanceFrequency(&frequency) || frequency.QuadPart != 1000000000LL) {
        std::fprintf(stderr, "performance-counter frequency shim failed\n");
        return 1;
    }
    if (!QueryPerformanceCounter(&before) || !QueryPerformanceCounter(&after) ||
        after.QuadPart < before.QuadPart) {
        std::fprintf(stderr, "monotonic performance-counter shim failed\n");
        return 2;
    }
    WSADATA data{};
    if (WSAStartup(MAKEWORD(2, 2), &data) != 0 || data.version != 0x0202) {
        std::fprintf(stderr, "POSIX Winsock startup shim failed\n");
        return 3;
    }
    if (GetCurrentProcessId() == 0 || GetTickCount64() < GetTickCount()) {
        std::fprintf(stderr, "process ID or millisecond clock shim failed\n");
        return 4;
    }
    if (_byteswap_ushort(0x1234u) != 0x3412u) {
        std::fprintf(stderr, "16-bit byte-swap shim failed\n");
        return 5;
    }
    if (_byteswap_uint64(0x0102030405060708ULL) != 0x0807060504030201ULL) {
        std::fprintf(stderr, "intrinsic byte-swap shim failed\n");
        return 6;
    }
    FILE *file = nullptr;
    if (fopen_s(&file, "/tmp/t6-ps5-compat-smoke.tmp", "w") != 0 || !file) {
        std::fprintf(stderr, "secure file-open shim failed\n");
        return 7;
    }
    std::fputs("ok", file);
    std::fclose(file);
    if (!MoveFileExA("/tmp/t6-ps5-compat-smoke.tmp", "/tmp/t6-ps5-compat-smoke.out", MOVEFILE_REPLACE_EXISTING)) {
        std::fprintf(stderr, "atomic file-replace shim failed\n");
        return 8;
    }
    std::remove("/tmp/t6-ps5-compat-smoke.out");
    Sleep(0);
    if (!SwitchToThread()) {
        std::fprintf(stderr, "thread-yield shim failed\n");
        return 9;
    }
    const char *copy_source = "/tmp/t6-ps5-copy-source.tmp";
    const char *copy_destination = "/tmp/t6-ps5-copy-destination.tmp";
    FILE *copy_file = std::fopen(copy_source, "w");
    if (!copy_file) return 10;
    std::fputs("copy-test", copy_file);
    std::fclose(copy_file);
    std::remove(copy_destination);
    if (!CopyFileA(copy_source, copy_destination, TRUE)) {
        std::fprintf(stderr, "POSIX CopyFileA shim failed\n");
        std::remove(copy_source);
        return 11;
    }
    if (CopyFileA(copy_source, copy_destination, TRUE)) {
        std::fprintf(stderr, "CopyFileA fail-if-exists contract failed\n");
        std::remove(copy_source);
        std::remove(copy_destination);
        return 12;
    }
    FILE *copied = std::fopen(copy_destination, "r");
    char copied_text[16]{};
    if (!copied || !std::fgets(copied_text, sizeof(copied_text), copied) ||
        std::string(copied_text) != "copy-test") {
        std::fprintf(stderr, "copied file content mismatch\n");
        if (copied) std::fclose(copied);
        std::remove(copy_source);
        std::remove(copy_destination);
        return 13;
    }
    std::fclose(copied);
    std::remove(copy_source);
    std::remove(copy_destination);
    std::puts("PS5 host-API compatibility smoke test passed");
    return 0;
}
