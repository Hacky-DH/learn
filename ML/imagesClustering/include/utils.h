#pragma once

#include <cstdlib>
#include <string>

template<typename T>
struct convert;

template<>
struct convert<std::string> {
    static std::string action(const char* str) {
        return std::string(str);
    }
};

template<>
struct convert<int> {
    static int action(const char* str) {
        return std::stoi(str);
    }
};

template<>
struct convert<long> {
    static long action(const char* str) {
        return std::stol(str);
    }
};

template<>
struct convert<float> {
    static float action(const char* str) {
        return std::stof(str);
    }
};

template<typename T>
bool get_env(const std::string& key, T& value) {
    auto ptr = std::getenv(key.c_str());
    if (ptr == nullptr) {
        return false;
    }
    value = convert<T>::action(ptr);
    return true;
}
