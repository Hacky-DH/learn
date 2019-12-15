add_executable(${PROJECT_NAME}
  main.cpp
  wallpaper.cpp
  dataset.cpp
  options.cpp
  log.cpp
  models/models.cpp
  models/fnn.cpp
  models/dcn.cpp
  models/dnn.cpp
  models/vgg.cpp
  models/rnn.cpp
)

set(libs ${TORCH_LIBRARIES} ${OpenCV_LIBS})
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
set(libs ${libs} boost_system
  boost_program_options
  boost_filesystem)
endif()

target_link_libraries(${PROJECT_NAME} ${libs})

if(MSVC AND COPYDLL)
  file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
  add_custom_command(TARGET ${PROJECT_NAME}
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     ${TORCH_DLLS}
                     $<TARGET_FILE_DIR:${PROJECT_NAME}>)
endif()
