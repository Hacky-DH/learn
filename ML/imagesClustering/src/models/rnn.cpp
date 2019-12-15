#include "models.h"

namespace ic {

RNN::RNN(size_t input_size,
    size_t hidden_size,
    size_t num_layers,
    size_t num_classes,
    size_t sequence_length) :
    BaseModel("Recurrent Neural Network"),
    rnn(nn::RNNOptions(input_size, hidden_size).layers(num_layers)),
    fc(nn::Linear(hidden_size, num_classes)),
    input_size(input_size),
    sequence_length(sequence_length){
    register_module("rnn", rnn);
    register_module("fc", fc);
}

// still didn't work
torch::Tensor RNN::forward(torch::Tensor x) {
    x = x.view({ -1, static_cast<int64_t>(sequence_length),
        static_cast<int64_t>(input_size) });
    x = fc(rnn(x).output);
    return torch::log_softmax(x, /*dim=*/1);
}
}
