# build

set env Torch_DIR to libtorch

```
mkdir build
cd build
cmake ..
make
```

or use ```cmake -DCMAKE_PREFIX_PATH=/absolute/path/to/libtorch ..```

on Windows use ```cmake -G "Visual Studio 15 2017 Win64" ..```
