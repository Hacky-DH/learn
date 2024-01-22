macro(copy_target target target_directory)
    if(NOT EXISTS ${target_directory})
        execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory 
        ${target_directory})
    endif()
    set(target_file $<TARGET_FILE:${target}>)
    add_custom_target(copy_target_${target} ALL
        COMMAND ${CMAKE_COMMAND} -E copy ${target_file} 
        ${target_directory}
        COMMAND ${CMAKE_COMMAND} -E echo "Copy target ${target_file} \
            to ${target_directory}"
        DEPENDS ${target}
        COMMENT "Copying target to directory"
    )
endmacro()


set(libs_dir_tmp ${CMAKE_SOURCE_DIR}/../libs)
cmake_path(SET libs_dir NORMALIZE "${libs_dir_tmp}")

macro(copy_libs target)
    copy_target(${target} ${libs_dir})
endmacro()

if(NOT TARGET cleanall)
    add_custom_target(cleanall
        COMMAND ${CMAKE_MAKE_PROGRAM} clean
        COMMAND ${CMAKE_COMMAND} -E remove ${libs_dir}/*.so
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Cleaning all build outputs"
    )
endif()
