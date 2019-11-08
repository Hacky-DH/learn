cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(opencv2lib)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_BUILD_TYPE Release)

if (DEFINED ENV{BOOST_DIR})
	set(BOOST_DIR $ENV{BOOST_DIR})
	include_directories(${BOOST_DIR})
	link_directories(${BOOST_DIR}/stage/lib)
endif()

# set env OpenCV_DIR
find_package(OpenCV REQUIRED)

add_executable(canny canny.cpp)

target_link_libraries(canny ${OpenCV_LIBS})
