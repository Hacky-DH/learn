#pragma once
#include <iostream>
#include "utils.h"
namespace nn = torch::nn;

template <typename Module, typename DataLoader>
void train(
    Module model,
    torch::optim::Optimizer &optimizer,
    DataLoader &data_loader,
    size_t start_epoch = 0,
    size_t num_epochs = 10,
    size_t log_per_steps = 50,
    size_t checkpoint_per_epoch = 5,
    std::string model_dir = "model") {
    for (size_t epoch = start_epoch; epoch <= num_epochs; ++epoch) {
        size_t step = 0;
        for (auto& batch : *data_loader) {
            optimizer.zero_grad();
            // Execute the model on the input data.
            torch::Tensor prediction = model->forward(batch.data);
            torch::Tensor loss = torch::nll_loss(prediction, batch.target);
            loss.backward();
            optimizer.step();
            if (++step % log_per_steps == 0) {
                std::cout << "Epoch: [" << epoch + 1 << "] Batch: [" << step
                    << "] Loss: " << loss.item<float>() << std::endl;
            }
        }
        if ((epoch + 1) % checkpoint_per_epoch == 0) {
            fs::create_directory(model_dir);
            fs::path file = fs::path(model_dir) / "checkpoint.pt";
            torch::save(model, file.string());
        }
    }
}
