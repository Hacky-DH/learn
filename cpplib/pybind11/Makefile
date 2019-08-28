target=cls`python3-config --extension-suffix`
${target} : main.cpp
	c++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` main.cpp -o ${target}
clean:
	\rm -fr ${target}
