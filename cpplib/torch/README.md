# build

set env Torch_DIR to libtorch

```
mkdir build
cd build
cmake ..
make
```

or use ```cmake -DCMAKE_PREFIX_PATH=/absolute/path/to/libtorch ..```

on msys2 use ```cmake -G "MSYS Makefiles" ..```
