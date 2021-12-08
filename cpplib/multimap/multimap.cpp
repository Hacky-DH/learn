/*
compare concurrent_unordered_multimap of TBB and unordered_multimap
https://github.com/oneapi-src/oneTBB

compile with
g++ -I include/ -Wl,-rpath,lib64/ lib64/libtbb.so multimap.cpp
*/

#include <oneapi/tbb/concurrent_unordered_map.h>
#include <string>
#include <iostream>
#include <unordered_map>


int main() {
	oneapi::tbb::concurrent_unordered_multimap<std::string,int> hm;
	//std::unordered_multimap<std::string,int> hm;
	hm.insert({"abc",4});
	hm.insert({"a",65});
	hm.insert({"c",3});
	hm.insert({"abc",8});
	hm.insert({"b",8});
	hm.insert({"abc",6});

	std::cout << "for key abc" << std::endl;
	auto rg = hm.equal_range("abc");
	while(rg.first != rg.second){
		std::cout << "abc" << " is " << rg.first->second << std::endl;
		++rg.first;
	}

	std::cout << "for all" << std::endl;
	for (auto& i : hm){
		std::cout << i.first << " is " << i.second << std::endl;
	}
}
/*
output:
for key abc
abc is 6
abc is 8
abc is 4
for all
abc is 6
abc is 8
abc is 4
c is 3
b is 8
a is 65
*/
