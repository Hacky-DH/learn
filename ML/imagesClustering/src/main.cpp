#include <iostream>
#include <locale>

#include <torch/torch.h>

#include "options.h"
#include "wallpaper.h"
#include "dataset.h"
#include "train.h"

using std::cout;
using std::wcout;
using std::cerr;
using std::wcerr;
using std::endl;
using namespace std::chrono_literals;
using namespace ic;
namespace nn = torch::nn;
namespace tt = torch::data::transforms;


// DCN deep clustering network using PyTorch C++ API

struct Net : nn::Module {
    Net():
        conv1(torch::nn::Conv2dOptions(1, 10, /*kernel_size=*/5)),
        conv2(torch::nn::Conv2dOptions(10, 20, /*kernel_size=*/5)),
        fc1(320, 50),
        fc2(50, 10) {
        register_module("conv1", conv1);
        register_module("conv2", conv2);
        register_module("conv2_drop", conv2_drop);
        register_module("fc1", fc1);
        register_module("fc2", fc2);
    }
    torch::Tensor forward(torch::Tensor x) {
        x = torch::relu(torch::max_pool2d(conv1->forward(x), 2));
        x = torch::relu(
            torch::max_pool2d(conv2_drop->forward(conv2->forward(x)), 2));
        x = x.view({-1, 320});
        x = torch::relu(fc1->forward(x));
        x = torch::dropout(x, /*p=*/0.5, /*training=*/is_training());
        x = fc2->forward(x);
        return torch::log_softmax(x, /*dim=*/1);
    }
    nn::Conv2d conv1;
    nn::Conv2d conv2;
    nn::FeatureDropout conv2_drop;
    nn::Linear fc1;
    nn::Linear fc2;
};


int main(int argc, char* argv[]) {
    Options options;
    try {
        options.parse(argc, argv);
    } catch (po::error& e) {
        cerr << "error: " << e.what() << "\n";
        return 1;
    } catch (OptionsExitsProgram) {
        return 0;
    }
    try {
        auto mnist = load_mnist(options.data_root());
        if (mnist.empty()) {
            cerr << "ERROR: no paths to load mnist" << endl;
            return 1;
        }
        cout << "load mnist train size " << mnist[0].size().value()
            << ", test size " << mnist[1].size().value() << endl;

        auto train_data = mnist[0].map(tt::Normalize<>(0.13707, 0.3081))
            .map(tt::Stack<>());
        int batch_size = options.batch_size();
        auto train_data_loader = torch::data::make_data_loader(
            std::move(train_data), batch_size);

        auto test_data = mnist[1].map(tt::Normalize<>(0.1307, 0.3081))
            .map(tt::Stack<>());
        const size_t test_data_size = test_data.size().value();
        auto test_data_loader = torch::data::make_data_loader(
                std::move(test_data), 1024);

        auto model = std::make_shared<Net>();
        torch::optim::SGD optimizer(model->parameters(),
            torch::optim::SGDOptions(0.01).momentum(0.5));

        // train and test
        size_t start_epoch = 0, num_epochs = 10;
        for (size_t epoch = start_epoch; epoch < num_epochs; ++epoch) {
            train(epoch, model, optimizer, train_data_loader);
            test(model, test_data_loader, test_data_size);
        }
    } catch (const std::exception& e) {
        cerr << e.what() << endl;
        return 1;
    }
}
