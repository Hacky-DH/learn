#include <torch/extension.h>

using torch::Tensor;

Tensor multinomial(const Tensor& probs, int64_t n_samples) {
#if PYTORCH_VERSION >= (1<<16) + (2<<8)
    // alias method, both on CPU and GPU
    // just works in pytorch 1.2
    auto as = torch::_multinomial_alias_setup(probs);
    return torch::_multinomial_alias_draw(std::get<1>(as), std::get<0>(as), n_samples);
#else
    return torch::multinomial(probs, n_samples, true);
#endif
}
