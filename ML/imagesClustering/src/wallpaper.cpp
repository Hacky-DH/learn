#include "wallpaper.h"

namespace ic {

#ifdef WIN32
std::string WPSTYLES[] = {
    "center", "tile",
    "stretch", "keepaspect",
    "croptofit", "span", "max"
};

WallPaper::WallPaper() {
    CoInitialize(nullptr);
    CoCreateInstance(CLSID_ActiveDesktop,
        NULL, CLSCTX_INPROC_SERVER,
        IID_IActiveDesktop, (void**)&ptr);
    std::locale::global(std::locale(""));
    last_opt.dwSize = sizeof(last_opt);
}

WallPaper::~WallPaper() {
    if (ptr != nullptr) {
        ptr->Release();
    }
    CoUninitialize();
}
bool WallPaper::apply(const std::wstring& wallpaper, uint32_t style) {
    WCHAR path[MAX_PATH];
    HRESULT hr = ptr->GetWallpaper(path, MAX_PATH, 0);
    if (FAILED(hr)) {
        return false;
    }
    last_wallpaper = path;
    hr = ptr->GetWallpaperOptions(&last_opt, 0);
    if (FAILED(hr)) {
        return false;
    }
    if(wallpaper.empty()) {
        hr = ptr->SetWallpaper(path, 0);
    } else {
        hr = ptr->SetWallpaper(wallpaper.c_str(), 0);
    }
    if (FAILED(hr)) {
        return false;
    }
    auto opt = last_opt;
    opt.dwStyle = style;
    hr = ptr->SetWallpaperOptions(&opt, 0);
    if (FAILED(hr)) {
        return false;
    }
    hr = ptr->ApplyChanges(AD_APPLY_ALL);
    if (FAILED(hr)) {
        return false;
    }
    std::wcout << "set wallpaper path " <<
        (wallpaper.empty() ? path : wallpaper.c_str())
        << ", style " << WPSTYLES[style].c_str() << endl;
    return true;
}

bool WallPaper::apply(const std::string& wallpaper, uint32_t style) {
    std::wstring _wallpaper = boost::locale::conv::
        to_utf<wchar_t>(wallpaper, "GBK");
    return apply(_wallpaper, style);
}

bool WallPaper::round() {
    WCHAR path[MAX_PATH];
    HRESULT hr = ptr->GetWallpaper(path, MAX_PATH, 0);
    if (FAILED(hr)) {
        return false;
    }
    last_wallpaper = path;
    hr = ptr->GetWallpaperOptions(&last_opt, 0);
    if (FAILED(hr)) {
        return false;
    }
    hr = ptr->SetWallpaper(path, 0);
    if (FAILED(hr)) {
        return false;
    }
    auto opt = last_opt;
    opt.dwStyle = (last_opt.dwStyle + 1) % WPSTYLE_MAX;
    hr = ptr->SetWallpaperOptions(&opt, 0);
    if (FAILED(hr)) {
        return false;
    }
    hr = ptr->ApplyChanges(AD_APPLY_ALL);
    if (FAILED(hr)) {
        return false;
    }
    std::wcout << "set wallpaper path " << path <<
        ", style " << WPSTYLES[opt.dwStyle].c_str() << endl;
    return true;
}

void test_wallpaper(const std::string& path) {
    WallPaper p;
    for (int i = WPSTYLE_CENTER; i < WPSTYLE_MAX; ++i) {
        p.apply(path, i);
        std::this_thread::sleep_for(1s);
    }
}

// example: set_style_or_round(argc > 1 ? argv[1] : "8");
// #pragma comment(linker, "/subsystem:windows /entry:mainCRTStartup")
void set_style_or_round(const std::string& style) {
    uint32_t s = style[0] - '0';
    WallPaper p;
    if (s >= 0 && s < WPSTYLE_MAX) {
        p.apply("", s);
    } else {
        p.round();
    }
}
#endif
}
