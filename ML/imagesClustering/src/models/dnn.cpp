#include "models.h"

namespace ic {
namespace nn = torch::nn;


DNN::DNN(size_t input_size, size_t num_classes,
    size_t h1, size_t h2) : BaseModel("Deep neural network"),
    input_size(input_size) {
    // Construct and register two Linear submodules.
    fc1 = register_module("fc1", torch::nn::Linear(input_size, h1));
    fc2 = register_module("fc2", torch::nn::Linear(h1, h2));
    fc3 = register_module("fc3", torch::nn::Linear(h2, num_classes));
}

torch::Tensor DNN::forward(torch::Tensor x) {
    // Use one of many tensor manipulation functions.
    x = torch::relu(fc1->forward(x.view({ x.size(0),
        static_cast<int64_t>(input_size) })));
    x = torch::dropout(x, /*p=*/0.5, /*train=*/is_training());
    x = torch::relu(fc2->forward(x));
    x = torch::log_softmax(fc3->forward(x), /*dim=*/1);
    return x;
}
}
