#include <iostream>
#include <chrono>
#include <thread>
#include <locale>

#include <torch/torch.h>

#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>

#include "wallpaper.h"
#include "dataset.h"

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
    Options();

    std::string data_config();
    std::string data_root();
    int batch_size();

    void parse(int argc, char* argv[]);
private:
    po::options_description _options;
    po::variables_map _results;
};


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
    fs::path data_root = options.data_root();
    int batch_size = options.batch_size();
    if (!fs::is_directory(data_root)) {
        cerr << "dataset root dir " << data_root << " don't exist" << endl;
        return 1;
    }
    try {
        //mnist dataset filenames:
        //train-images-idx3-ubyte train-labels-idx1-ubyte
        //t10k-images-idx3-ubyte t10k-labels-idx1-ubyte
        namespace td = torch::data::datasets;
        auto _train_data = td::MNIST(data_root.string());
        auto _test_data = td::MNIST(data_root.string(), td::MNIST::Mode::kTest);
        cout << "load mnist train size " << _train_data.size().value()
            << ", test size " << _test_data.size().value() << endl;

        namespace tt = torch::data::transforms;
        auto train_data = _train_data.map(tt::Normalize<>(0.13707, 0.3081)).
            map(torch::data::transforms::Stack<>());
        auto data_loader = torch::data::make_data_loader(std::move(train_data), 64);

        auto net = std::make_shared<Net>();
        torch::optim::SGD optimizer(net->parameters(), 0.01);

        for (auto& batch : *data_loader) {
            cout << batch.data.size(0) << endl;
        }
    }
    catch (const std::exception& e) {
        cerr << e.what() << endl;
        return 1;
    }
}

// class Options
Options::Options() :_options("Options") {
    // set all options
    fs::path default_data_root;
    default_data_root = default_data_root / ".." / ".." /
        "dataset" / ".local" / "mnist";
    fs::path default_data_config;
    default_data_config = default_data_config / ".local" /
        "data.config";
    _options.add_options()
        ("help,h", "help message")
        ("version,v", "show program version")
        ("data-config,c", po::value<std::string>()->
            default_value(default_data_config.string()),
            "The root path of dataset");
    _options.add_options()
        ("data-root,d", po::value<std::string>()->
            default_value(default_data_root.string()),
            "The root path of dataset");
    _options.add_options()
        ("batch-size,b", po::value<int>()->
            default_value(1), "batch size");
}

std::string Options::data_config() {
    return _results["data-config"].as<std::string>();
}

std::string Options::data_root() {
    return _results["data-root"].as<std::string>();
}

int Options::batch_size() {
    return _results["batch-size"].as<int>();
}

void Options::parse(int argc, char* argv[]) {
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
