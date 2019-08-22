#include "alias_sample.h"
#include <iostream>
#include <torch/torch.h>

using std::cout;
using std::endl;

// build steps:
// mkdir build && cd build
// cmake ..
// make

int main() {
        auto row = torch::rand(10);
        row = row/row.sum();
        cout<<"dist: "<<row<<endl;
        AliasSample as(row);
        cout<<as.Str()<<"samples: ";
        for (int i=0; i<10; ++i) {
                cout<<as()<<",";
        }
        cout<<endl;
}
