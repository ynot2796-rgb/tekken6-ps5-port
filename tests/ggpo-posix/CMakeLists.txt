cmake_minimum_required(VERSION 3.20)
project(ggpo_posix_compile_test LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT DEFINED T6_REFERENCE_SOURCE)
  message(FATAL_ERROR "Set T6_REFERENCE_SOURCE to the pinned Native Online source checkout")
endif()
set(GGPO_SOURCE "${T6_REFERENCE_SOURCE}/third_party/ggpo/src")
include("${GGPO_SOURCE}/CMakeSources.cmake")
add_library(ggpo_posix_compile OBJECT ${GGPO_LIB_SRC})
target_include_directories(ggpo_posix_compile PRIVATE
  "${GGPO_SOURCE}/include"
  "${GGPO_SOURCE}/lib/ggpo"
)
target_compile_options(ggpo_posix_compile PRIVATE -Wno-unknown-pragmas)
