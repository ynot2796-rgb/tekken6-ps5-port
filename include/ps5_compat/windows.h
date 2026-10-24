#pragma once
/*
 * Minimal Win32 compatibility surface for Native Online's host-side helpers.
 * This is for the PS5/FreeBSD port only; it is not a Windows API emulator.
 * Window-focus and keyboard APIs deliberately report console-native defaults.
 */
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <dlfcn.h>
#include <functional>
#include <pthread.h>
#include <sched.h>
#include <signal.h>
#include <time.h>
#include <unistd.h>
#include <sys/types.h>

using BOOL = int;
using BYTE = uint8_t;
using WORD = uint16_t;
using SHORT = int16_t;
using DWORD = uint32_t;
using LONG = int32_t;
using ULONG = uint32_t;
using ULONGLONG = uint64_t;
using ULONG_PTR = uintptr_t;
using HANDLE = void *;
using HMODULE = void *;
using HINSTANCE = void *;
using HWND = void *;
using LPVOID = void *;
using LPCVOID = const void *;
using LPCWSTR = const wchar_t *;
using LPCSTR = const char *;
using FARPROC = void (*)();

struct LARGE_INTEGER { int64_t QuadPart = 0; };
struct FILETIME { DWORD dwLowDateTime = 0; DWORD dwHighDateTime = 0; };
struct CONTEXT {
    DWORD ContextFlags = 0;
    uint64_t Rip = 0;
    uint32_t Eip = 0;
};

#ifndef TRUE
#  define TRUE 1
#endif
#ifndef FALSE
#  define FALSE 0
#endif
#ifndef WINAPI
#  define WINAPI
#endif
#ifndef __cdecl
#  define __cdecl
#endif
#ifndef MAX_PATH
#  define MAX_PATH 4096
#endif
#ifndef CONTEXT_CONTROL
#  define CONTEXT_CONTROL 0x00100001
#endif
#ifndef THREAD_SUSPEND_RESUME
#  define THREAD_SUSPEND_RESUME 0x0002
#  define THREAD_GET_CONTEXT 0x0008
#  define THREAD_QUERY_INFORMATION 0x0040
#endif
#ifndef DUPLICATE_SAME_ACCESS
#  define DUPLICATE_SAME_ACCESS 0x00000002
#endif
#ifndef GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS
#  define GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS 0x00000004
#  define GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT 0x00000002
#endif

inline BOOL QueryPerformanceCounter(LARGE_INTEGER *value) {
    if (!value) { errno = EINVAL; return FALSE; }
    timespec ts{};
    if (::clock_gettime(CLOCK_MONOTONIC, &ts) != 0) return FALSE;
    value->QuadPart = static_cast<int64_t>(ts.tv_sec) * 1000000000LL + ts.tv_nsec;
    return TRUE;
}
inline BOOL QueryPerformanceFrequency(LARGE_INTEGER *value) {
    if (!value) { errno = EINVAL; return FALSE; }
    value->QuadPart = 1000000000LL;
    return TRUE;
}
inline DWORD GetTickCount() {
    LARGE_INTEGER t{};
    QueryPerformanceCounter(&t);
    return static_cast<DWORD>(static_cast<uint64_t>(t.QuadPart / 1000000LL));
}
inline ULONGLONG GetTickCount64() {
    LARGE_INTEGER t{};
    QueryPerformanceCounter(&t);
    return static_cast<uint64_t>(t.QuadPart / 1000000LL);
}
inline void Sleep(DWORD milliseconds) {
    if (milliseconds == 0) { ::sched_yield(); return; }
    timespec req{static_cast<time_t>(milliseconds / 1000),
                 static_cast<long>((milliseconds % 1000) * 1000000UL)};
    while (::nanosleep(&req, &req) != 0 && errno == EINTR) {}
}


inline void *_aligned_malloc(size_t size, size_t alignment) {
    void *memory = nullptr;
    if (::posix_memalign(&memory, alignment, size) != 0) return nullptr;
    return memory;
}
inline void _aligned_free(void *memory) { std::free(memory); }

inline int fopen_s(FILE **file, const char *path, const char *mode) {
    if (!file || !path || !mode) { errno = EINVAL; return EINVAL; }
    *file = std::fopen(path, mode);
    return *file ? 0 : (errno ? errno : 1);
}

inline DWORD GetLastError() { return static_cast<DWORD>(errno); }
inline DWORD GetCurrentProcessId() { return static_cast<DWORD>(::getpid()); }

inline DWORD GetCurrentThreadId() {
    return static_cast<DWORD>(std::hash<pthread_t>{}(::pthread_self()));
}
[[noreturn]] inline void ExitProcess(DWORD exit_code) {
    std::exit(static_cast<int>(exit_code));
}

inline HANDLE GetCurrentProcess() { return reinterpret_cast<HANDLE>(static_cast<uintptr_t>(-1)); }
inline HANDLE GetCurrentThread() { return nullptr; }

/* Remote-thread sampling is a Windows-only optional profiling feature. */
inline BOOL DuplicateHandle(HANDLE, HANDLE, HANDLE, HANDLE *target, DWORD, BOOL, DWORD) {
    if (target) *target = nullptr;
    return FALSE;
}
inline BOOL GetThreadContext(HANDLE, CONTEXT *) { return FALSE; }

/* Optional symbol lookup uses the process image on PS5 rather than DLL handles. */
inline HMODULE GetModuleHandleW(LPCWSTR) { return RTLD_DEFAULT; }
inline BOOL GetModuleHandleExW(DWORD, LPCWSTR, HMODULE *module) {
    if (module) *module = RTLD_DEFAULT;
    return module != nullptr;
}
inline BOOL GetModuleHandleExA(DWORD, LPCSTR, HMODULE *module) {
    if (module) *module = RTLD_DEFAULT;
    return module != nullptr;
}
inline FARPROC GetProcAddress(HMODULE, LPCSTR name) {
    return name ? reinterpret_cast<FARPROC>(::dlsym(RTLD_DEFAULT, name)) : nullptr;
}

/* Console focus is always the foreground; host keyboard input is not available. */
inline HWND GetForegroundWindow() { return reinterpret_cast<HWND>(static_cast<uintptr_t>(1)); }
inline DWORD GetWindowThreadProcessId(HWND, DWORD *process_id) {
    if (process_id) *process_id = GetCurrentProcessId();
    return 1;
}
inline SHORT GetAsyncKeyState(int) { return 0; }

#ifndef MOVEFILE_REPLACE_EXISTING
#  define MOVEFILE_REPLACE_EXISTING 0x00000001
#endif
inline BOOL MoveFileExA(LPCSTR existing, LPCSTR destination, DWORD flags) {
    if (!existing || !destination) { errno = EINVAL; return FALSE; }
    if (!(flags & MOVEFILE_REPLACE_EXISTING) && ::access(destination, F_OK) == 0) {
        errno = EEXIST;
        return FALSE;
    }
    return ::rename(existing, destination) == 0 ? TRUE : FALSE;
}

inline void OutputDebugStringA(const char *message) {
    if (message) { ::fputs(message, stderr); ::fflush(stderr); }
}
inline void DebugBreak() { ::raise(SIGTRAP); }
