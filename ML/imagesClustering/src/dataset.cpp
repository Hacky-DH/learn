#include "dataset.h"
namespace ic {
void display_image(const std::string& path) {
    cv::Mat image = cv::imread(path);
    if (image.empty()) {
        throw std::runtime_error("Could not open the image");
    }
    cv::namedWindow("Display image");
    cv::imshow("Display image", image);
    cv::waitKey(0);
}
}
