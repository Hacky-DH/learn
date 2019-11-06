#include <iostream>
#include <torch/torch.h>
#include <boost/optional.hpp>
#include <boost/filesystem.hpp>

using std::cout;
using std::endl;

// DCN deep clustering network using PyTorch C++ API

struct Net: torch::nn::Module {
};

int main() {
    cout << boost::filesystem::current_path() << endl;
    boost::filesystem::path root("../dataset/.local/mnist");
    if (boost::filesystem::exists(root)) {
        cout << "exist" << endl;
    }
    auto dataset = torch::data::datasets::MNIST("../dataset/.local/mnist");
    //auto dataset = torch::data::datasets::MNIST("../dataset/.local/mnist").
    //    map(torch::data::transforms::Normalize<>(0.13707, 0.3081)).
    //    map(torch::data::transforms::Stack<>());
    //cout << dataset.size().value() << endl;
    //auto data_loader = torch::data::make_data_loader(std::move(dataset), 64);

    auto net = std::make_shared<Net>();
    torch::optim::SGD optimizer(net->parameters(), 0.01);
}
