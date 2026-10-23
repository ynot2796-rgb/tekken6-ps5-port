#pragma once
/*
 * POSIX platform shim for the pinned Tekken 6 Native Online GGPO fork.
 * Intended for Linux CI and the FreeBSD-derived PS5 userland; it does not
 * emulate the Windows launcher or the game's DirectX renderer.
 */
#include "t6_socket_compat.h"
#include <cstdio>
#include <cstdarg>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <strings.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>

using DWORD = unsigned long;
using HANDLE = int;
#ifndef INFINITE
#  define INFINITE 0x7fffffff
#endif

class Platform {
public:
    using ProcessID = pid_t;
    static ProcessID GetProcessID() { return ::getpid(); }
    static void AssertFailed(char *msg) {
        ::fprintf(stderr, "%s\n", msg ? msg : "GGPO assertion failed");
        ::fflush(stderr);
    }
    static uint32 GetCurrentTimeMS() {
        struct timespec ts{};
        if (::clock_gettime(CLOCK_MONOTONIC, &ts) != 0) return 0;
        return static_cast<uint32>(ts.tv_sec * 1000u + ts.tv_nsec / 1000000u);
    }
    static int GetConfigInt(const char *name);
    static bool GetConfigBool(const char *name);
};


inline int t6_recvfrom_compat(SOCKET socket, char *buffer, int length, int flags,
                              struct sockaddr *address, int *address_length) {
    if (!address_length) { errno = EINVAL; return SOCKET_ERROR; }
    socklen_t native_length = static_cast<socklen_t>(*address_length);
    const ssize_t result = ::recvfrom(socket, buffer, static_cast<size_t>(length),
                                      flags, address, &native_length);
    *address_length = static_cast<int>(native_length);
    return static_cast<int>(result);
}
#define recvfrom t6_recvfrom_compat

/* The fork uses MSVC secure-CRT helpers. Keep equivalent bounded POSIX calls. */
#ifndef _MSC_VER
#  define sprintf_s(buffer, size, ...) std::snprintf((buffer), (size), __VA_ARGS__)
#  define vsprintf_s(buffer, size, fmt, args) std::vsnprintf((buffer), (size), (fmt), (args))
#  define strcpy_s(dst, src) std::snprintf((dst), sizeof(dst), "%s", (src))
#  define fopen_s(out, path, mode) ((*(out) = std::fopen((path), (mode))) == nullptr ? errno : 0)
#  define strncat_s(dst, dstsz, src, count) t6_strncat_s((dst), (dstsz), (src), (count))
inline int t6_strncat_s(char *dst, size_t dstsz, const char *src, size_t count) {
    if (!dst || !src || dstsz == 0) return EINVAL;
    const size_t used = std::strlen(dst);
    if (used >= dstsz) { dst[dstsz - 1] = '\0'; return ERANGE; }
    const size_t available = dstsz - used - 1;
    const size_t copied = count < available ? count : available;
    std::strncat(dst, src, copied);
    dst[used + copied] = '\0';
    return copied == count ? 0 : ERANGE;
}
#endif
#ifndef FALSE
#  define Sleep(milliseconds) ::usleep(static_cast<useconds_t>(milliseconds) * 1000u)
#  define FALSE 0
#endif
#ifndef TRUE
#  define TRUE 1
#endif
