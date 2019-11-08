#include <iostream>

#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

using std::cout;
using std::cerr;
using std::endl;


int main(int argc, char* argv[]) {
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) return -1;
    cv::Mat frame, edges;
    cv::namedWindow("edges", cv::WINDOW_AUTOSIZE);
    for (;;)
    {
        cap >> frame;
        cv::cvtColor(frame, edges, cv::COLOR_BGR2GRAY);
        cv::GaussianBlur(edges, edges, cv::Size(7, 7), 1.5, 1.5);
        cv::Canny(edges, edges, 0, 30, 3);
        cv::imshow("edges", edges);
        if (cv::waitKey(30) >= 0) break;
    }
}
