cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
set(proj learn)
project(${proj})

find_package(Torch REQUIRED)

add_executable(${proj} learn.cpp)
target_link_libraries(${proj} "${TORCH_LIBRARIES}")
set_property(TARGET ${proj} PROPERTY CXX_STANDARD 11)
