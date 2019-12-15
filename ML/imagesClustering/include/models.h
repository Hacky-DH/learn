#pragma once
#include <torch/torch.h>

namespace ic {
namespace nn = torch::nn;

struct BaseModel: nn::Module {
    BaseModel(const std::string& name) : nn::Module(name) {}
    virtual torch::Tensor forward(torch::Tensor x) = 0;
};

std::shared_ptr<BaseModel> get_model(const std::string& model);

// Feedforward Neural Network
struct FNN: BaseModel {
    FNN(size_t input_size=784,
        size_t hidden_size=500,
        size_t num_classes=10);
    torch::Tensor forward(torch::Tensor x);
    size_t input_size;
    nn::Linear fc1{nullptr}, fc2{nullptr};
};

struct DNN: BaseModel {
    DNN(size_t input_size=784, size_t num_classes=10,
        size_t h1=64, size_t h2=32);
    torch::Tensor forward(torch::Tensor x);
    size_t input_size;
    nn::Linear fc1{nullptr}, fc2{nullptr}, fc3{nullptr};
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

// VGG-16 Visual Geometry Group
// see https://krshrimali.github.io/PyTorch-C++-API/
// small kernel size 3x3 and deep layers
// conv1_1 - conv1_2 - pool 1 -
// conv2_1 - conv2_2 - pool 2 -
// conv3_1 - conv3_2 - conv3_3 - pool 3 -
// conv4_1 - conv4_2 - conv4_3 - pool 4 -
// conv5_1 - conv5_2 - conv5_3 - pool 5 -
// fc6 - fc7 - fc8
struct VGG : BaseModel {
    VGG();
    torch::Tensor forward(torch::Tensor x);

    nn::Conv2d conv1_1{nullptr}, conv1_2{nullptr};
    nn::Conv2d conv2_1{nullptr}, conv2_2{nullptr};
    nn::Conv2d conv3_1{nullptr}, conv3_2{nullptr}, conv3_3{nullptr};
    nn::Conv2d conv4_1{nullptr}, conv4_2{nullptr}, conv4_3{nullptr};
    nn::Conv2d conv5_1{nullptr}, conv5_2{nullptr}, conv5_3{nullptr};
    nn::Linear fc1{nullptr}, fc2{nullptr}, fc3{nullptr};
};

// Recurrent Neural Network
struct RNN : BaseModel {
    RNN(size_t input_size = 28,
        size_t hidden_size = 128,
        size_t num_layers = 2,
        size_t num_classes = 10,
        size_t sequence_length=28);
    torch::Tensor forward(torch::Tensor x);
    size_t input_size;
    size_t sequence_length;
    nn::RNN rnn{ nullptr };
    nn::Linear fc{ nullptr };
};

}
