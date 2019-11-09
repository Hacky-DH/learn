#include <iostream>
#include <chrono>
#include <thread>
#include <locale>

#include <torch/torch.h>

#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>
#include <boost/locale.hpp>

#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

#ifdef WIN32
#include <windows.h>
#include <wininet.h>
#include <ShlObj.h>
#endif

using std::cout;
using std::wcout;
using std::cerr;
using std::wcerr;
using std::endl;
using namespace std::chrono_literals;
namespace dt = std::chrono;
namespace fs = boost::filesystem;
namespace po = boost::program_options;

const std::string version("1.0.0");

// DCN deep clustering network using PyTorch C++ API

struct Net : torch::nn::Module {
};

// Used to exit the program if the help/version option is set
class OptionsExitsProgram : public std::exception {};

class Options {
public:
    Options() :_options("Options") {
        // set all options
        fs::path default_data_root;
        default_data_root = default_data_root / ".." / ".." /
            "dataset" / ".local" / "mnist";
        _options.add_options()
            ("help,h", "help message")
            ("version,v", "show program version")
            ("data-root,d", po::value<std::string>()->
                default_value(default_data_root.string()),
                "The root path of dataset");
        _options.add_options()
            ("batch-size,b", po::value<int>()->
                default_value(1), "batch size");
    }

    fs::path data_root() {
        return _results["data-root"].as<std::string>();
    }

    int batch_size() {
        return _results["batch-size"].as<int>();
    }

    void parse(int argc, char* argv[]) {
        po::store(po::parse_command_line(argc, argv, _options),
            _results);
        po::notify(_results);
        if (_results.count("help")) {
            cout << _options << "\n";
            throw OptionsExitsProgram();
        }
        if (_results.count("version")) {
            cout << "version " << version << "\n";
            throw OptionsExitsProgram();
        }
    }
private:
    po::options_description _options;
    po::variables_map _results;
};


#ifdef WIN32
class WallPaper {
    IActiveDesktop *ptr;
    WALLPAPEROPT last_opt;
    std::wstring last_wallpaper;
public:
    WallPaper() :ptr(nullptr) {
        CoInitialize(nullptr);
        std::locale::global(std::locale(""));
        last_opt.dwSize = sizeof(last_opt);
    }

    ~WallPaper() {
        if (ptr != nullptr) {
            ptr->Release();
        }
        CoUninitialize();
    }

    //set the wallpaper and style
    // make sure enable the active desktop(default is enable)
    // SetDesktopItemOptions
    //WPSTYLE_CENTER 0
    //WPSTYLE_TILE 1
    //WPSTYLE_STRETCH 2
    //WPSTYLE_KEEPASPECT 3
    //WPSTYLE_CROPTOFIT 4
    //WPSTYLE_SPAN 5
    bool apply(const std::wstring& wallpaper, uint32_t style) {
        HRESULT hr = CoCreateInstance(CLSID_ActiveDesktop,
            NULL, CLSCTX_INPROC_SERVER,
            IID_IActiveDesktop, (void**)&ptr);
        if (FAILED(hr)) {
            ptr = nullptr;
            return false;
        }
        WCHAR path[MAX_PATH];
        hr = ptr->GetWallpaper(path, MAX_PATH, 0);
        if (FAILED(hr)) {
            return false;
        }
        last_wallpaper = path;
        std::wcout << "last wallpaper path " <<
            last_wallpaper << endl;
        hr = ptr->SetWallpaper(wallpaper.c_str(), 0);
        if (FAILED(hr)) {
            return false;
        }
        hr = ptr->GetWallpaperOptions(&last_opt, 0);
        if (FAILED(hr)) {
            return false;
        }
        cout << "last opt is " << last_opt.dwStyle << endl;
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

    bool apply(const std::string& wallpaper, uint32_t style) {
        std::wstring _wallpaper = boost::locale::conv::
            to_utf<wchar_t>(wallpaper, "GBK");
        return apply(_wallpaper, style);
    }

    bool restore() {
        return apply(last_wallpaper, last_opt.dwStyle);
    }
};
#else
class WallPaper {
public:
    bool apply(const std::string& wallpaper, uint32_t style) {
        return true;
    }
    bool apply(const std::wstring& wallpaper, uint32_t style) {
        return true;
    }
    bool restore() {
        return true;
    }
};
#endif


int main(int argc, char* argv[]) {
    Options options;
    try {
        options.parse(argc, argv);
    }
    catch (po::error& e) {
        cerr << "error: " << e.what() << "\n";
        return 1;
    }
    catch (OptionsExitsProgram) {
        return 0;
    }

    auto pwd = fs::current_path();
    cout << "current path is " << pwd << endl;
    auto data_root = options.data_root();
    int batch_size = options.batch_size();
    if (!fs::is_directory(data_root)) {
        cerr << "dataset root dir " << data_root << " don't exist" << endl;
        return 1;
    }
    cout << "load mnist from " << data_root << endl;
    //auto dataset = torch::data::datasets::MNIST(data_root);
    //auto dataset = torch::data::datasets::MNIST(data_root.string()).
    //    map(torch::data::transforms::Normalize<>(0.13707, 0.3081)).
    //    map(torch::data::transforms::Stack<>());
    //cout << dataset.size().value() << endl;
    //auto data_loader = torch::data::make_data_loader(std::move(dataset), 64);

    auto net = std::make_shared<Net>();
    torch::optim::SGD optimizer(net->parameters(), 0.01);

    WallPaper p;
    std::string path = "";
    p.apply(path, WPSTYLE_CENTER);
    std::this_thread::sleep_for(1s);
    p.apply(path, WPSTYLE_TILE);
    std::this_thread::sleep_for(1s);
    p.apply(path, WPSTYLE_STRETCH);
    std::this_thread::sleep_for(1s);
    p.apply(path, WPSTYLE_KEEPASPECT);
    std::this_thread::sleep_for(1s);
    p.apply(path, WPSTYLE_CROPTOFIT);
    std::this_thread::sleep_for(1s);
    p.apply(path, WPSTYLE_SPAN);
}
