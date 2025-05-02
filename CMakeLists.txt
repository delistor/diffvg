cmake_minimum_required(VERSION 3.12)

project(diffvg VERSION 0.0.1 LANGUAGES CXX CUDA)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 14)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)

# ✅ Python3 ≥ 3.7
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
include_directories(${Python3_INCLUDE_DIRS})

# ✅ 使用系统 pybind11
find_path(PYBIND11_INCLUDE_DIR pybind11/pybind11.h)
if(NOT PYBIND11_INCLUDE_DIR)
    message(FATAL_ERROR "❌ Cannot find pybind11 installed via pip.")
endif()
message(STATUS "✅ Found pybind11 at: ${PYBIND11_INCLUDE_DIR}")
include_directories(${PYBIND11_INCLUDE_DIR})

# ✅ CUDA 选项
option(DIFFVG_CUDA "Build diffvg with GPU code path?" ON)

if(DIFFVG_CUDA)
    message(STATUS "✅ Build with CUDA support")
    enable_language(CUDA)
    add_definitions(-DCOMPILE_WITH_CUDA)
else()
    message(STATUS "⚠️ Build without CUDA support")
    set(THRUST_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/thrust")
    include_directories(${THRUST_INCLUDE_DIR})
endif()

# ✅ 源文件列表（可根据情况使用 .cu 替换 diffvg.cpp）
set(SRCS
    atomic.cpp
    color.cpp
    diffvg.cu  # ⚠️ 关键！必须改名才能使用 nvcc 正确编译 CUDA
    parallel.cpp
    scene.cpp
    shape.cpp
)

# ✅ 编译目标
add_library(diffvg MODULE ${SRCS})

# ✅ 设置输出为 Python 模块（无前缀）
set_target_properties(diffvg PROPERTIES PREFIX "")

# ✅ 设置 RPATH（允许 Python 找到动态库）
set_target_properties(diffvg PROPERTIES
    SKIP_BUILD_RPATH FALSE
    BUILD_WITH_INSTALL_RPATH TRUE
    INSTALL_RPATH "$ORIGIN"
)

# ✅ Mac 特殊处理
if(APPLE)
    set_target_properties(diffvg PROPERTIES INSTALL_RPATH "@loader_path")
endif()

