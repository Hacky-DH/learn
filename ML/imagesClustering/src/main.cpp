#include <iostream>
#include <chrono>
#include <thread>
#include <locale>

#include <torch/torch.h>

#include "options.h"
#include "wallpaper.h"
#include "dataset.h"

using std::cout;
using std::wcout;
using std::cerr;
using std::wcerr;
using std::endl;
using namespace std::chrono_literals;
using namespace ic;
namespace dt = std::chrono;



// DCN deep clustering network using PyTorch C++ API

struct Net : torch::nn::Module {
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
