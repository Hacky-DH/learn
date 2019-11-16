add_executable(${PROJECT_NAME} main.cpp wallpaper.cpp dataset.cpp)

target_link_libraries(${PROJECT_NAME}
                      ${TORCH_LIBRARIES}
                      ${OpenCV_LIBS})

if(MSVC AND COPYDLL)
  file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
  add_custom_command(TARGET ${PROJECT_NAME}
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     ${TORCH_DLLS}
                     $<TARGET_FILE_DIR:${PROJECT_NAME}>)
endif()
