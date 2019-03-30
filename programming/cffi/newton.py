# -*- coding: utf-8 -*-
from cffi import FFI
import os

ffi = FFI()
ffi.cdef("double newton(double, int);")

# pass c source file to python
src_dir = os.path.abspath('.')
lib = ffi.verify("#include <newton.c>", include_dirs=[src_dir], libraries=[])

print(lib.newton(0, 30))

# or use so library
# gcc newton.c -shared -o newton.so
libso = ffi.verify("#include <newton.c>", include_dirs=[src_dir], library_dirs=[src_dir], libraries=['newton'])
print(libso.newton(0, 30))