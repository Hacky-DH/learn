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

add_executable(${PROJECT_NAME} main.cpp)

# set env Torch_DIR or CMAKE_PREFIX_PATH to libtorch
find_package(Torch REQUIRED)

target_link_libraries(${PROJECT_NAME}
                      ${TORCH_LIBRARIES}
                      ${OpenCV_LIBS})

if(MSVC)
  file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
  add_custom_command(TARGET ${PROJECT_NAME}
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     ${TORCH_DLLS}
                     $<TARGET_FILE_DIR:${PROJECT_NAME}>)
endif(MSVC)
