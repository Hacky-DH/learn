#include "models.h"

namespace ic {

// VGG-16 Visual Geometry Group
VGG::VGG() : BaseModel("VGG-16 network"),
conv1_1(nn::Conv2d(nn::Conv2dOptions(1, 10, 3).padding(1))),
conv1_2(nn::Conv2d(nn::Conv2dOptions(10, 20, 3).padding(1))),
conv2_1(nn::Conv2d(nn::Conv2dOptions(20, 30, 3).padding(1))),
conv2_2(nn::Conv2d(nn::Conv2dOptions(30, 40, 3).padding(1))),
conv3_1(nn::Conv2d(nn::Conv2dOptions(40, 50, 3).padding(1))),
conv3_2(nn::Conv2d(nn::Conv2dOptions(50, 60, 3).padding(1))),
conv3_3(nn::Conv2d(nn::Conv2dOptions(60, 70, 3).padding(1))),
conv4_1(nn::Conv2d(nn::Conv2dOptions(70, 80, 3).padding(1))),
conv4_2(nn::Conv2d(nn::Conv2dOptions(80, 90, 3).padding(1))),
conv4_3(nn::Conv2d(nn::Conv2dOptions(90, 100, 3).padding(1))),
conv5_1(nn::Conv2d(nn::Conv2dOptions(100, 110, 3).padding(1))),
conv5_2(nn::Conv2d(nn::Conv2dOptions(110, 120, 3).padding(1))),
conv5_3(nn::Conv2d(nn::Conv2dOptions(120, 130, 3).padding(1))),
fc1(nn::Linear(130, 50)),
fc2(nn::Linear(50, 20)),
fc3(nn::Linear(20, 10)) {
    register_module("conv1_1", conv1_1);
    register_module("conv1_2", conv1_2);
    register_module("conv2_1", conv2_1);
    register_module("conv2_2", conv2_2);
    register_module("conv3_1", conv3_1);
    register_module("conv3_2", conv3_2);
    register_module("conv3_3", conv3_3);
    register_module("conv4_1", conv4_1);
    register_module("conv4_2", conv4_2);
    register_module("conv4_3", conv4_3);
    register_module("conv5_1", conv5_1);
    register_module("conv5_2", conv5_2);
    register_module("conv5_3", conv5_3);
    register_module("fc1", fc1);
    register_module("fc2", fc2);
    register_module("fc3", fc3);
}

torch::Tensor VGG::forward(torch::Tensor x) {
    x = torch::relu(conv1_1(x));
    x = torch::relu(conv1_2(x));
    x = torch::max_pool2d(x, 2);

    x = torch::relu(conv2_1(x));
    x = torch::relu(conv2_2(x));
    x = torch::max_pool2d(x, 2);

    x = torch::relu(conv3_1(x));
    x = torch::relu(conv3_2(x));
    x = torch::relu(conv3_3(x));
    x = torch::max_pool2d(x, 2);

    x = torch::relu(conv4_1(x));
    x = torch::relu(conv4_2(x));
    x = torch::relu(conv4_3(x));
    x = torch::max_pool2d(x, 2);

    x = torch::relu(conv5_1(x));
    x = torch::relu(conv5_2(x));
    x = torch::relu(conv5_3(x));
    x = x.view({ -1, 130 });

    x = torch::relu(fc1(x));
    x = torch::relu(fc2(x));
    x = fc3(x);

    return torch::log_softmax(x, 1);
}
}
