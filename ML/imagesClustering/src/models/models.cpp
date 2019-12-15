#include "models.h"

namespace ic {

std::shared_ptr<BaseModel> get_model(const std::string& model) {
    if (model == "fnn") {
        return std::make_shared<FNN>();
    } else if (model == "dnn") {
        return std::make_shared<DNN>();
    } else if (model == "dcn") {
        return std::make_shared<DCN>();
    } else if (model == "vgg") {
        return std::make_shared<VGG>();
    } else if (model == "rnn") {
        return std::make_shared<RNN>();
    } else {
        throw std::runtime_error("unexpected model");
    }
}

}
