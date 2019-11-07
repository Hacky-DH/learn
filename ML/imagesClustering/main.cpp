#include <iostream>
#include <chrono>
#include <torch/torch.h>
#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>

using std::cout;
using std::cerr;
using std::endl;
namespace dt = std::chrono;
namespace fs = boost::filesystem;
namespace po = boost::program_options;

// DCN deep clustering network using PyTorch C++ API

struct Net : torch::nn::Module {
};

int main(int argc, char* argv[]) {
    auto pwd = fs::current_path();
    auto default_data_root = pwd / ".." / ".." / "dataset" / ".local" / "mnist";
    default_data_root = default_data_root.make_preferred();
    std::string data_root;
    int batch_size;
    try {
        po::options_description desc("Options");
        desc.add_options()
            ("help,h", "help message")
            ("data-root,d", po::value<std::string>(&data_root)->
                default_value(default_data_root.string()),
                "The root path of dataset")
                ("batch-size,b", po::value<int>(&batch_size)->
                    default_value(1), "batch size");
        po::variables_map vm;
        po::store(po::parse_command_line(argc, argv, desc), vm);
        po::notify(vm);
        if (vm.count("help")) {
            cout << desc << "\n";
            return 0;
        }
    }
    catch (po::error& e) {
        cerr << "error: " << e.what() << "\n";
        return 1;
    }
    catch (...) {
        cerr << "Exception of unknown type!\n";
        return 1;
    }
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
}
