#include <iostream>
#include <torch/torch.h>
#include <boost/optional.hpp>
#include <boost/filesystem.hpp>

using std::cout;
using std::cerr;
using std::endl;
namespace fs = boost::filesystem;

// DCN deep clustering network using PyTorch C++ API

struct Net: torch::nn::Module {
};

int main() {
    auto pwd = fs::current_path();
    auto data_root = pwd / ".." / ".." / "dataset" / ".local" / "mnist";
    data_root = data_root.make_preferred();
    if (!fs::is_directory(data_root)) {
        cerr << "dataset root dir " << data_root << " don't exist" << endl;
        return 1;
    }
    cout << "load mnist from " << data_root << endl;
    //auto dataset = torch::data::datasets::MNIST(data_root.string());
    //auto dataset = torch::data::datasets::MNIST(data_root.string()).
    //    map(torch::data::transforms::Normalize<>(0.13707, 0.3081)).
    //    map(torch::data::transforms::Stack<>());
    //cout << dataset.size().value() << endl;
    //auto data_loader = torch::data::make_data_loader(std::move(dataset), 64);

    auto net = std::make_shared<Net>();
    torch::optim::SGD optimizer(net->parameters(), 0.01);
}
