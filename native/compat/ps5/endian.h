#pragma once
// Minimal endian conversion compatibility for PS5 Payload SDK libc++.
// ReXGlue's bundled SHA-256 implementation includes <endian.h>, which the
// target SDK does not provide under that spelling.
#include <cstdint>

#if defined(__BYTE_ORDER__) && (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)
#define T6_PS5_BIG_ENDIAN 1
#else
#define T6_PS5_BIG_ENDIAN 0
#endif

#if T6_PS5_BIG_ENDIAN
#define htole16(x) __builtin_bswap16(static_cast<uint16_t>(x))
#define htole32(x) __builtin_bswap32(static_cast<uint32_t>(x))
#define htole64(x) __builtin_bswap64(static_cast<uint64_t>(x))
#define le16toh(x) __builtin_bswap16(static_cast<uint16_t>(x))
#define le32toh(x) __builtin_bswap32(static_cast<uint32_t>(x))
#define le64toh(x) __builtin_bswap64(static_cast<uint64_t>(x))
#define htobe16(x) static_cast<uint16_t>(x)
#define htobe32(x) static_cast<uint32_t>(x)
#define htobe64(x) static_cast<uint64_t>(x)
#define be16toh(x) static_cast<uint16_t>(x)
#define be32toh(x) static_cast<uint32_t>(x)
#define be64toh(x) static_cast<uint64_t>(x)
#else
#define htole16(x) static_cast<uint16_t>(x)
#define htole32(x) static_cast<uint32_t>(x)
#define htole64(x) static_cast<uint64_t>(x)
#define le16toh(x) static_cast<uint16_t>(x)
#define le32toh(x) static_cast<uint32_t>(x)
#define le64toh(x) static_cast<uint64_t>(x)
#define htobe16(x) __builtin_bswap16(static_cast<uint16_t>(x))
#define htobe32(x) __builtin_bswap32(static_cast<uint32_t>(x))
#define htobe64(x) __builtin_bswap64(static_cast<uint64_t>(x))
#define be16toh(x) __builtin_bswap16(static_cast<uint16_t>(x))
#define be32toh(x) __builtin_bswap32(static_cast<uint32_t>(x))
#define be64toh(x) __builtin_bswap64(static_cast<uint64_t>(x))
#endif

#undef T6_PS5_BIG_ENDIAN
