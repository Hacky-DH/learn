#pragma once
#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <locale>

#include <boost/locale.hpp>

#ifdef WIN32
#include <windows.h>
#include <wininet.h>
#include <ShlObj.h>
#endif

namespace ic {

using std::cout;
using std::wcout;
using std::cerr;
using std::wcerr;
using std::endl;
using namespace std::chrono_literals;
namespace dt = std::chrono;


#ifdef WIN32
extern std::string WPSTYLES[];

class WallPaper {
    IActiveDesktop *ptr;
    WALLPAPEROPT last_opt;
    std::wstring last_wallpaper;
public:
    WallPaper();

    ~WallPaper();

    //set the wallpaper and style
    // make sure enable the active desktop(default is enable)
    // SetDesktopItemOptions
    //WPSTYLE_CENTER 0
    //WPSTYLE_TILE 1
    //WPSTYLE_STRETCH 2
    //WPSTYLE_KEEPASPECT 3
    //WPSTYLE_CROPTOFIT 4
    //WPSTYLE_SPAN 5
    bool apply(const std::wstring& wallpaper, uint32_t style);

    bool apply(const std::string& wallpaper, uint32_t style);

    // set wallpaper styles round, one by one
    bool round();

    bool restore() {
        return apply(last_wallpaper, last_opt.dwStyle);
    }
};

void test_wallpaper(const std::string& path);
void set_style_or_round(const std::string& style);
#else
class WallPaper {
public:
    bool apply(const std::string&, uint32_t) {
        throw std::runtime_error("Not Implemented");
    }
    bool apply(const std::wstring&, uint32_t) {
        throw std::runtime_error("Not Implemented");
    }
    bool restore() {
        throw std::runtime_error("Not Implemented");
    }
};
#endif

}