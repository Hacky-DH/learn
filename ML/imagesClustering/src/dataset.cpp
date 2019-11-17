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


std::vector<fs::path> find_possible_paths(
    const std::string& config_path,
    const std::string& env) {
    auto cwd = fs::current_path();
    static std::list<fs::path> all_possible_paths{
        cwd / ".." / ".." / ".." / ".." / "dataset" / ".local" / "mnist",
        cwd / ".." / ".." / ".." / "dataset" / ".local" / "mnist",
        cwd / ".." / ".." / "dataset" / ".local" / "mnist",
        cwd / ".." / "dataset" / ".local" / "mnist",
        cwd / "dataset" / ".local" / "mnist",
        cwd / ".local" / "mnist",
        cwd / "dataset" / "mnist",
        cwd / "dataset",
        cwd / "data" / "mnist",
        cwd / "data",
    };
    std::string _env;
    if (!env.empty()) {
        get_env<std::string>(env, _env);
    }
    if (!_env.empty()) {
        all_possible_paths.push_front(_env);
    }
    if (!config_path.empty()) {
        fs::path path = config_path;
        if (!path.is_absolute()) {
            path = cwd / path;
        }
        all_possible_paths.push_front(path);
    }
    std::vector<fs::path> paths;
    for (auto path : all_possible_paths) {
        if (fs::is_directory(path)) {
            paths.push_back(fs::canonical(path.make_preferred()));
        }
    }
    return paths;
}


std::vector<td::MNIST> load_mnist(const std::string& path) {
    auto paths = find_possible_paths(path, "MNIST_ROOT");
    for (auto p : paths) {
        auto train_data = td::MNIST(p.string());
        auto test_data = td::MNIST(p.string(), td::MNIST::Mode::kTest);
        return {train_data, test_data};
    }
    return {};
}

}
