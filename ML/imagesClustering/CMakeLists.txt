cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
# if in msys2 use `cmake -G "MSYS Makefiles" ..`, tried, but make failed
# if in vs use `cmake -G "Visual Studio 15 2017 Win64" ..`, success
project(imagesClustering)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_BUILD_TYPE Release)

if (DEFINED ENV{BOOST_DIR})
	set(BOOST_DIR $ENV{BOOST_DIR})
	include_directories(${BOOST_DIR})
	link_directories(${BOOST_DIR}/stage/lib)
endif()

# set env OpenCV_DIR
find_package(OpenCV REQUIRED)

# set env Torch_DIR or CMAKE_PREFIX_PATH to libtorch
find_package(Torch REQUIRED)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

option(COPYDLL "copy dlls" OFF)

add_subdirectory(src)
