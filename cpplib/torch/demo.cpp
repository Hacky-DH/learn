#include <iostream>
#include <torch/torch.h>

using std::cout;
using std::endl;

int main() {
    // random 10x1 tensor in range [0,100)
    auto rd = torch::randint(100, 10);
    cout << "random: " << rd << endl;
}
