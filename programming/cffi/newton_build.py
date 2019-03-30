# -*- coding: utf-8 -*-
from cffi import FFI
import os

ffi = FFI()
ffi.cdef("double newton(double, int);")
# _newton is the name of the python extension module
ffi.set_source("_newton",'#include "newton.h"', sources=['newton.c'], libraries=[])

if __name__ == "__main__":
    ffi.compile(verbose=True)