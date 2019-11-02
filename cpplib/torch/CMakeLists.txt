cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
# cmake -G "MSYS Makefiles" .. in msys2
project(learn)

set(CMAKE_CXX_STANDARD 11)

add_executable(${PROJECT_NAME} learn.cpp)

message(${CMAKE_SYSTEM_NAME})
if(WIN32)
	# search for torch
	set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})
	include(torch)
	find_package(PythonLibs REQUIRED)

	target_include_directories(${PROJECT_NAME} PRIVATE
		${TORCH_INCLUDE_DIRS}
		${PYTHON_INCLUDE_PATH})
else()
	# set env Torch_DIR to libtorch
	find_package(Torch REQUIRED)
	target_link_libraries(${proj} ${TORCH_LIBRARIES})
endif()
