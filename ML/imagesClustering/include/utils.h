#pragma once

#include <cstdlib>
#include <string>
#include <chrono>
#include <thread>
#include <random>

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

namespace dt = std::chrono;
/**
* @bref timer
* @example
* @code
*   Timer t;
*   long e = t.elapsed();
*/
class Timer {
    dt::time_point<dt::system_clock> start;
public:
    Timer() {
        start = dt::system_clock::now();
        //dt::high_resolution_clock::now()
    }

    static void sleep(long seconds) {
        std::this_thread::sleep_for(dt::seconds(seconds));
    }

    void reset() {
        start = dt::system_clock::now();
    }

    /*
    * milliseconds
    */
    long elapsed() {
        auto end = dt::system_clock::now();
        auto elp = dt::duration_cast<dt::milliseconds>(end - start);
        return elp.count();
    }

    bool reach(dt::seconds duration) {
        return dt::system_clock::now() - start >= duration;
    }
};

/**
* @bref int random generator
* @example
* @code
*   random_generator rg;
*   size_t rand = rg.next<size_t>(1,5);
*/
class random_generator {
    std::default_random_engine generator;
public:
    random_generator() {
        auto seed = std::chrono::system_clock::now().time_since_epoch().count();
        generator.seed(seed);
    }
    template<typename T>
    T next(T lower, T upper) {
        std::uniform_int_distribution<T> distribution(lower, upper);
        return distribution(generator);
    }
};
