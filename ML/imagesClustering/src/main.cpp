#include <iostream>
#include <locale>

#include <torch/torch.h>

#include "options.h"
#include "wallpaper.h"
#include "dataset.h"
#include "train.h"
#include "models.h"
#include "utils.h"
#include "log.h"

using namespace ic;
namespace nn = torch::nn;
namespace tt = torch::data::transforms;

// PyTorch C++ API

int main(int argc, char* argv[]) {
    log::init();
    auto &lg = log::ic_logger::get();
    Options options;
    try {
        options.parse(argc, argv);
    } catch (po::error& e) {
        BOOST_LOG_SEV(lg, error)<< e.what();
        return 1;
    } catch (OptionsExitsProgram) {
        return 0;
    }
    try {
        auto mnist = load_mnist(options.data_root());
        if (mnist.empty()) {
            BOOST_LOG_SEV(lg, error) << "no paths to load mnist";
            return 1;
        }
        BOOST_LOG_SEV(lg, info) << "load mnist train size "
            << mnist[0].size().value() << ", test size "
            << mnist[1].size().value();

        auto train_data = mnist[0].map(tt::Normalize<>(0.13707, 0.3081))
            .map(tt::Stack<>());
        auto batch_size = options.batch_size();
        auto train_data_loader = torch::data::make_data_loader(
            std::move(train_data), batch_size);

        auto test_data = mnist[1].map(tt::Normalize<>(0.1307, 0.3081))
            .map(tt::Stack<>());
        const size_t test_data_size = test_data.size().value();
        auto test_data_loader = torch::data::make_data_loader(
                std::move(test_data), 1024);

        auto model = get_model(options.model());
        torch::optim::SGD optimizer(model->parameters(),
            torch::optim::SGDOptions(0.01).momentum(0.5));

        // train and test
        BOOST_LOG_SEV(lg, info) << "Start train " << model->name();
        size_t start_epoch = options.start_epoch(),
            num_epochs = options.num_epochs(),
            checkpoint_per_epoch = options.checkpoint_per_epoch();
        std::string model_dir = options.model_dir();
        fs::create_directory(model_dir);
        for (size_t epoch = start_epoch; epoch < num_epochs; ++epoch) {
            train(epoch, model, optimizer, train_data_loader,
                options.log_per_steps());
            test(model, test_data_loader, test_data_size);
            if ((epoch + 1) % checkpoint_per_epoch == 0) {
                fs::path file = fs::path(model_dir) / "checkpoint.pt";
                torch::save(model, file.string());
            }
        }
    } catch (const std::exception& e) {
        BOOST_LOG_SEV(lg, error)<< e.what();
        return 1;
    }
}
