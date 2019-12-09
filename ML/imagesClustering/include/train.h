#pragma once
#include "utils.h"
#include "log.h"

namespace ic {
namespace fs = boost::filesystem;
namespace nn = torch::nn;

template <typename Module, typename DataLoader>
void train(
    size_t epoch,
    Module model,
    torch::optim::Optimizer &optimizer,
    DataLoader &data_loader,
    size_t log_per_steps = 100) {
    auto &lg = log::ic_logger::get();
    model->train();
    size_t step = 0;
    for (auto& batch : *data_loader) {
        optimizer.zero_grad();
        // Execute the model on the input data.
        torch::Tensor prediction = model->forward(batch.data);
        torch::Tensor loss = torch::nll_loss(prediction, batch.target);
        loss.backward();
        optimizer.step();
        if (++step % log_per_steps == 0) {
            BOOST_LOG_SEV(lg, info) << "Epoch: [" << epoch + 1 << "] Batch: ["
                << step << "] Loss: " << loss.item<float>();
        }
    }
}

template <typename Module, typename DataLoader>
void test(
    Module model,
    DataLoader& data_loader,
    size_t dataset_size) {
    auto &lg = log::ic_logger::get();
    torch::NoGradGuard no_grad;
    model->eval();
    double test_loss = 0;
    int32_t correct = 0;
    for (const auto& batch : *data_loader) {
        auto output = model->forward(batch.data);
        // no at::Reduction::Sum?
        test_loss += torch::nll_loss(output, batch.target,
            /*weight=*/{}, /*reduction=sum*/2)
            .template item<float>();
        auto pred = output.argmax(1);
        correct += pred.eq(batch.target).sum().template item<int64_t>();
    }
    test_loss /= dataset_size;
    BOOST_LOG_SEV(lg, info) << "Test set: Average loss: " << test_loss
        << " | Accuracy: " << static_cast<double>(correct) / dataset_size;
}
} //namespace ic
