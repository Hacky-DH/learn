cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
# if in msys2 use `cmake -G "MSYS Makefiles" ..`, tried, but make failed
# if in vs use `cmake -G "Visual Studio 15 2017 Win64" ..`, success
project(learn)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_BUILD_TYPE Release)

option(MYTORCH "use mytorch cmake config" OFF)

# find_package(OpenCV REQUIRED)

set(learn learn)
add_executable(${learn} learn.cpp)
set(demo demo)
add_executable(${demo} demo.cpp)
add_executable(dataset dataset.cpp)

if(MYTORCH)
	# search for torch
	set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})
	include(torch)
	find_package(PythonLibs REQUIRED)

	target_include_directories(${learn} PRIVATE
		${TORCH_INCLUDE_DIRS}
		${PYTHON_INCLUDE_PATH})
else()
	# set env Torch_DIR or CMAKE_PREFIX_PATH to libtorch
	find_package(Torch REQUIRED)
	target_link_libraries(${learn} ${TORCH_LIBRARIES})
	target_link_libraries(${demo} ${TORCH_LIBRARIES})
	target_link_libraries(dataset ${TORCH_LIBRARIES})
endif(MYTORCH)

if(MSVC)
  file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
  add_custom_command(TARGET ${learn}
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     ${TORCH_DLLS}
                     $<TARGET_FILE_DIR:${learn}>)
endif(MSVC)
