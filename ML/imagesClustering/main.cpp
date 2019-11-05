#include <iostream>
#include <torch/torch.h>

using std::cout;
using std::endl;

// DCN deep clustering network using PyTorch C++ API

struct Net: torch::nn::Module {
};

int main() {
    // random 10x1 tensor in range [0,100)
    auto rd = torch::randint(100, 10);
    cout << "random: " << rd << endl;
    //range [0,10)
    auto rg = torch::arange(10);
    cout << "range: " << rg << endl;

    //find
    auto eight = (rg == 8).nonzero();
    cout << "eight: " << eight << endl;
    auto none = (rg == 25).nonzero();
    cout << "none: " << none << endl;

    rd[8] = 88;
    cout << "index: " << rd[8] << "," << rd[5].item<int>() << endl;

    //float type
    auto one = torch::ones(10, torch::kFloat64);
    cout << "float: " << one << endl;

    // matrix
    auto mat = torch::zeros({ 4,5 }, torch::kInt64);
    mat[3][1] = 56;
    cout << "matirx: " << mat << endl;

    //index
    auto src = torch::tensor({ 0, 1, 1, 1, 2, 2, 3, 3, 4, 4 }, torch::kInt64);
    auto dst = torch::tensor({ 1, 0, 2, 3, 1, 4, 1, 4, 2, 3 }, torch::kInt64);
    // find the index of dst == 1
    auto index = (dst == 1).nonzero();
    cout << index << endl;  // 0,4,6
    // operation index to index the tensor by index
    cout << src.index(index) << endl;  // 0,2,3
}
