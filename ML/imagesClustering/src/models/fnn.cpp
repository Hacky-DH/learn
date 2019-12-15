#include "models.h"

namespace ic {

std::shared_ptr<BaseModel> get_model(const std::string& model) {
    if (model == "fnn") {
        return std::make_shared<FNN>();
    } else if (model == "dnn") {
        return std::make_shared<DNN>();
    } else if (model == "dcn") {
        return std::make_shared<DCN>();
    } else {
        throw std::runtime_error("unexpected model");
    }
}

// Feedforward Neural Network
FNN::FNN(size_t input_size, size_t hidden_size,
    size_t num_classes):
    BaseModel("Feedforward neural network"),
    input_size(input_size),
    fc1(input_size, hidden_size),
    fc2(hidden_size, num_classes) {
    register_module("fc1", fc1);
    register_module("fc2", fc2);
}

torch::Tensor FNN::forward(torch::Tensor x) {
    x = torch::relu(fc1->forward(x.view({ x.size(0),
        static_cast<int64_t>(input_size) })));
    return fc2(x);
}
}
