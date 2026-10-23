cmake_minimum_required(VERSION 3.20)
project(ggpo_posix_compile_test LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT DEFINED T6_REFERENCE_SOURCE)
  message(FATAL_ERROR "Set T6_REFERENCE_SOURCE to the pinned Native Online source checkout")
endif()
set(GGPO_SOURCE "${T6_REFERENCE_SOURCE}/third_party/ggpo/src")
include("${GGPO_SOURCE}/CMakeSources.cmake")
list(TRANSFORM GGPO_LIB_SRC PREPEND "${GGPO_SOURCE}/")
add_library(ggpo_posix STATIC ${GGPO_LIB_SRC})
target_include_directories(ggpo_posix PUBLIC
  "${GGPO_SOURCE}/include"
  "${GGPO_SOURCE}/lib/ggpo"
)
target_compile_options(ggpo_posix PRIVATE -Wno-unknown-pragmas)
option(T6_GGPO_BUILD_SMOKE "Build and run host-side GGPO poll smoke test" ON)
if(T6_GGPO_BUILD_SMOKE)
  enable_testing()
  add_executable(ggpo_posix_smoke smoke.cpp)
  target_include_directories(ggpo_posix_smoke PRIVATE "${GGPO_SOURCE}/include" "${GGPO_SOURCE}/lib/ggpo")
  target_link_libraries(ggpo_posix_smoke PRIVATE ggpo_posix)
  add_test(NAME ggpo_posix_poll_smoke COMMAND ggpo_posix_smoke)
endif()

option(T6_PS5_COMPAT_HEADER_CHECK "Compile PS5 host compatibility headers without linking an executable" OFF)
if(T6_PS5_COMPAT_HEADER_CHECK)
  if(NOT DEFINED T6_PS5_PORT_ROOT)
    message(FATAL_ERROR "Set T6_PS5_PORT_ROOT to the port repository root")
  endif()
  add_library(ps5_compat_header_check OBJECT "${T6_PS5_PORT_ROOT}/tests/ps5-compat-smoke.cpp")
  target_include_directories(ps5_compat_header_check PRIVATE
    "${T6_PS5_PORT_ROOT}/include/ps5_compat"
    "${T6_PS5_PORT_ROOT}/include"
  )
  add_library(t6_common_header_check OBJECT "${T6_PS5_PORT_ROOT}/tests/t6-common-header-smoke.cpp")
  target_include_directories(t6_common_header_check PRIVATE
    "${T6_PS5_PORT_ROOT}/include/ps5_compat"
    "${T6_PS5_PORT_ROOT}/include"
    "${T6_REFERENCE_SOURCE}/src"
  )
  add_library(t6_netplay_header_check OBJECT "${T6_PS5_PORT_ROOT}/tests/t6-netplay-header-smoke.cpp")
  target_include_directories(t6_netplay_header_check PRIVATE
    "${T6_PS5_PORT_ROOT}/include/ps5_compat"
    "${T6_PS5_PORT_ROOT}/include"
    "${T6_REFERENCE_SOURCE}/src"
    "${T6_REFERENCE_SOURCE}/third_party/ggpo/src/include"
    "${T6_REFERENCE_SOURCE}/third_party/ggpo/src/lib/ggpo"
    "${T6_REFERENCE_SOURCE}/../rexglue-sdk/include"
    "${T6_REFERENCE_SOURCE}/../fmt/include"
    "${T6_REFERENCE_SOURCE}/../simde"
    "${T6_REFERENCE_SOURCE}/../spdlog/include"
  )
endif()
