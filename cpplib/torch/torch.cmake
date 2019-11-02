# set env Torch_DIR to libtorch
if (DEFINED ENV{Torch_DIR})
	set(TORCH_INSTALL_PREFIX $ENV{Torch_DIR})
	if(EXISTS ${TORCH_INSTALL_PREFIX})
		message(STATUS "find torch in dir: " ${TORCH_INSTALL_PREFIX})
		set(TORCH_INCLUDE_DIRS
			${TORCH_INSTALL_PREFIX}/include
			${TORCH_INSTALL_PREFIX}/include/torch/csrc/api/include)
		set(TORCH_LIBRARIES ${TORCH_INSTALL_PREFIX}/lib)
		return()
	endif()
endif()
message(FATAL_ERROR "NOT set env Torch_DIR")
