#include <iostream>
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
    int batch_size = options.batch_size();
    try {
        auto mnist = load_mnist(options.data_root());
        if (mnist.empty()) {
            cerr << "ERROR: no paths to load mnist" << endl;
            return 1;
        }
        cout << "load mnist train size " << mnist[0].size().value()
            << ", test size " << mnist[1].size().value() << endl;

        namespace tt = torch::data::transforms;
        auto train_data = mnist[0].map(tt::Normalize<>(0.13707, 0.3081)).
            map(torch::data::transforms::Stack<>());
        auto data_loader = torch::data::make_data_loader(std::move(train_data), 64);

        auto net = std::make_shared<Net>();
        torch::optim::SGD optimizer(net->parameters(), 0.01);

        for (auto& batch : *data_loader) {
            cout << batch.data.size(0) << endl;
            break;
        }
    }
    catch (const std::exception& e) {
        cerr << e.what() << endl;
        return 1;
    }
}
