#pragma once
#include <cstdint>
#ifndef _byteswap_uint64
#  define _byteswap_uint64(value) __builtin_bswap64(static_cast<uint64_t>(value))
#endif
#ifndef _byteswap_ulong
#  define _byteswap_ulong(value) __builtin_bswap32(static_cast<uint32_t>(value))
#endif

#ifndef _byteswap_ushort
#  define _byteswap_ushort(value) __builtin_bswap16(static_cast<uint16_t>(value))
#endif
