#include <iostream>
#include <vector>
#include <torch/torch.h>

using std::cout;
using std::endl;

using torch::data::datasets::Dataset;
using torch::data::transforms::Lambda;
using torch::data::samplers::SequentialSampler;

struct DummyDataset : Dataset<DummyDataset, int> {
  explicit DummyDataset(size_t size = 100) : size_(size) {}

  int get(size_t index) override {
    return 1 + index;
  }
  torch::optional<size_t> size() const override {
    return size_;
  }

  size_t size_;
};

using NextFunc = std::function<std::vector<int>()>;

NextFunc data_loader(){
    auto dl = torch::data::make_data_loader<SequentialSampler>(
            DummyDataset().map(Lambda<int>([](int x) { return x + 1; })), 25);
    return [&dl]() -> std::vector<int> {
        // begin() will core dump, why?
        // at torch/data/dataloader/base.h:62 DataLoaderBase::reset
        static auto next = dl->begin();
        if (next == dl->end()) {
            next = dl->begin();
            std::vector<int> empty;
            return empty;
        }
        auto tmp = *next;
        ++next;
        return tmp;
    };
}

int main() {
    auto next = data_loader();
    while(true){
        auto batch = next();
        if(batch.empty()) break;
        cout<<next()[0]<<endl;
    }
}
