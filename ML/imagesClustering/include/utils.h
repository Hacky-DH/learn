#pragma once

#include <cstdlib>
#include <string>
#include <chrono>
#include <thread>
#include <random>
#include <fstream>
#include <sstream>
#include <iomanip>

#ifdef WIN32
#include <windows.h>
#include <psapi.h>
#endif

template<typename T>
struct convert;

template<>
struct convert<std::string> {
    static std::string action(const std::string& str) {
        return str;
    }
};

template<>
struct convert<int> {
    static int action(const std::string& str) {
        return std::stoi(str);
    }
};

template<>
struct convert<long> {
    static long action(const std::string& str) {
        return std::stol(str);
    }
};

template<>
struct convert<float> {
    static float action(const std::string& str) {
        return std::stof(str);
    }
};

template<typename T>
bool get_env(const std::string& key, T& value) {
    std::string _value;
    // _dupenv_s is safe then std::getenv on windows
#ifdef WIN32
    char *buf = nullptr;
    size_t sz;
    if (0 == _dupenv_s(&buf, &sz, key.c_str()) && buf != nullptr) {
        _value = std::string(buf);
        free(buf);
    } else {
        return false;
    }
#else
    auto ptr = std::getenv(key.c_str());
    if (ptr == nullptr) {
        return false;
    }
    _value = ptr;
#endif
    value = convert<T>::action(_value);
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
    int64_t elapsed() {
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
        generator.seed(static_cast<uint32_t>(seed));
    }
    template<typename T>
    T next(T lower, T upper) {
        std::uniform_int_distribution<T> distribution(lower, upper);
        return distribution(generator);
    }
};

/*
 * get memory usage of current process
*/
class MemUsage {
    size_t rss, peak; // in bytes
    void get() {
        rss = peak = 0;
#ifdef WIN32
        PROCESS_MEMORY_COUNTERS info;
        info.cb = sizeof(info);
        if (GetProcessMemoryInfo(GetCurrentProcess(),
            &info, sizeof(info))) {
            rss = info.WorkingSetSize;
            peak = info.PeakWorkingSetSize;
        }
#else
        std::ifstream status("/proc/self/status");
        if (status.is_open()) {
            std::string line, name;
            while (getline(status, line)) {
                std::istringstream iss(line);
                iss >> name;
                if (name == "VmPeak:") {
                    iss >> peak;
                    peak *= 1024;
                }
                if (name == "VmRSS:") {
                    iss >> rss;
                    rss *= 1024;
                }
            }
            status.close();
        }
#endif
    }
public:
    static std::string bytes2str(size_t bytes) {
        static size_t units[] = {
            1024,
            1024 * 1024,
            1024 * 1024 * 1024,
            1024 * 1024 * 1024 * 1024,
            1024 * 1024 * 1024 * 1024 * 1024,
        };
        static std::string ustr[] = { "Bytes", "KB", "MB",
            "GB", "TB", "PB" };
        for (size_t i = 0; i < sizeof(units) /
            sizeof(units[0]); ++i) {
            if (bytes < units[i]) {
                std::ostringstream oss;
                if (i == 0) {
                    oss << bytes;
                } else {
                    oss << std::setprecision(2)<<std::fixed
                        << (double)bytes / units[i - 1];
                }
                oss << " " << ustr[i];
                return oss.str();
            }
        }
        return "too large bytes " + std::to_string(bytes);
    }

    std::string str() {
        get();
        std::ostringstream oss;
        oss << "memory usage: RSS " << bytes2str(rss) <<
            ", Peak RSS " << bytes2str(peak);
        return oss.str();
    }
};
