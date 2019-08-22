#include "alias_sample.h"
#include <iostream>
#include <torch/torch.h>

// mkdir build && cd build
// cmake -DCMAKE_PREFIX_PATH=/usr/local/anaconda3/lib/python3.6/site-packages/torch ..
// make
int main() {
        auto row = torch::rand(10);
        row = row/row.sum();
        std::cout<<row<<std::endl;
        AliasSample as(row);
        for (int i=0; i<10; ++i) {
                std::cout<<as()<<",";
        }
        std::cout<<std::endl;
}
