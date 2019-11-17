#pragma once
#include <string>
#include <vector>
#include <list>

#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

#include <boost/filesystem.hpp>

#include <torch/torch.h>

#include "utils.h"

namespace ic {
namespace fs = boost::filesystem;
namespace td = torch::data::datasets;

void display_image(const std::string& path);

// first to check config path
// second to check in env
// check: dir exist
std::vector<fs::path> find_possible_paths(
    const std::string& config_path = "",
    const std::string& env = ""
);

// load mnist from possible paths or env MNIST_ROOT
//mnist dataset filenames:
//train-images-idx3-ubyte train-labels-idx1-ubyte
//t10k-images-idx3-ubyte t10k-labels-idx1-ubyte
std::vector<td::MNIST> load_mnist(const std::string& path);
}
