cmake_minimum_required(VERSION 3.12)

project(diffvg VERSION 0.0.1 DESCRIPTION "Differentiable Vector Graphics")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

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

# ✅ CUDA 配置
option(DIFFVG_CUDA "Build diffvg with GPU code path?" ON)

if(DIFFVG_CUDA)
    message(STATUS "✅ Build with CUDA support")
    find_package(CUDA 10 REQUIRED)
    set(CMAKE_CUDA_STANDARD 11)
    if(NOT WIN32)
        set(CUDA_NVCC_FLAGS "${CUDA_NVCC_FLAGS} -std=c++11")
    endif()
else()
    message(STATUS "⚠️ Build without CUDA support")
    set(THRUST_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/thrust")
    include_directories(${THRUST_INCLUDE_DIR})
endif()

