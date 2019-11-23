#pragma once
#include <torch/torch.h>

namespace ic {
namespace nn = torch::nn;

// DCN deep conv network
struct DCN : nn::Module {
    DCN();
    torch::Tensor forward(torch::Tensor x);
    nn::Conv2d conv1;
    nn::Conv2d conv2;
    nn::FeatureDropout conv2_drop;
    nn::Linear fc1;
    nn::Linear fc2;
};
}
