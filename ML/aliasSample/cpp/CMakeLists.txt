cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(rw)

find_package(Torch REQUIRED)

add_executable(rw main.cpp)
target_link_libraries(rw "${TORCH_LIBRARIES}")
target_include_directories(rw PRIVATE "/usr/local/anaconda3/include/python3.6m")
set_property(TARGET rw PROPERTY CXX_STANDARD 11)
