cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
set(proj alias)
project(${proj})

set(CMAKE_PREFIX_PATH /usr/local/anaconda3/lib/python3.6/site-packages/torch)
find_package(Torch REQUIRED)

add_executable(${proj} main.cpp)
target_link_libraries(${proj} "${TORCH_LIBRARIES}")
target_include_directories(${proj} PRIVATE "/usr/local/anaconda3/include/python3.6m")
set_property(TARGET ${proj} PROPERTY CXX_STANDARD 11)
