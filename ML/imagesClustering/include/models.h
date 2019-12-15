#pragma once
#include <torch/torch.h>

namespace ic {
namespace nn = torch::nn;

struct BaseModel: nn::Module {
    BaseModel(const std::string& name) :nn::Module(name) {}
    virtual torch::Tensor forward(torch::Tensor x) = 0;
};

// Feedforward Neural Network
struct FNN: BaseModel {
    FNN(size_t input_size=784,
        size_t hidden_size=500,
        size_t num_classes=10);
    torch::Tensor forward(torch::Tensor x);
    size_t input_size;
    torch::nn::Linear fc1{nullptr}, fc2{nullptr};
};

struct DNN: BaseModel {
    DNN(size_t input_size=784, size_t num_classes=10,
        size_t h1=64, size_t h2=32);
    torch::Tensor forward(torch::Tensor x);
    size_t input_size;
    torch::nn::Linear fc1{nullptr}, fc2{nullptr}, fc3{nullptr};
};

// DCN deep conv network
struct DCN : BaseModel {
    DCN();
    torch::Tensor forward(torch::Tensor x);
    nn::Conv2d conv1;
    nn::Conv2d conv2;
    nn::FeatureDropout conv2_drop;
    nn::Linear fc1;
    nn::Linear fc2;
};

std::shared_ptr<BaseModel> get_model(const std::string& model);
}
