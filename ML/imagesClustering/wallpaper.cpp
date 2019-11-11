#include "wallpaper.h"


#ifdef WIN32
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
    std::wcout << "last wallpaper path " <<
        last_wallpaper << endl;
    hr = ptr->GetWallpaperOptions(&last_opt, 0);
    if (FAILED(hr)) {
        return false;
    }
    cout << "last opt is " << last_opt.dwStyle << endl;
    if(wallpaper.empty()){
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
        wallpaper << ", style " << style << endl;
    return true;
}

bool WallPaper::apply(const std::string& wallpaper, uint32_t style) {
    std::wstring _wallpaper = boost::locale::conv::
        to_utf<wchar_t>(wallpaper, "GBK");
    return apply(_wallpaper, style);
}

void test_wallpaper(const std::string& path) {
    WallPaper p;
    for (int i = WPSTYLE_CENTER; i < WPSTYLE_MAX; ++i) {
        p.apply(path, i);
        std::this_thread::sleep_for(1s);
    }
}
#endif
