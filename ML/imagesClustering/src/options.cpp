#include "options.h"

namespace ic {

const std::string version("1.0.0");

// class Options
Options::Options() :_options("Options") {
    // set all options
    fs::path default_data_config;
    default_data_config = default_data_config / ".local" /
        "data.config";
    _options.add_options()
        ("help,h", "help message")
        ("version,v", "show program version")
        ("data-config,c", po::value<std::string>()->
            default_value(default_data_config.string()),
            "The root path of dataset");
    _options.add_options()
        ("data-root,d", po::value<std::string>(),
            "The root path of dataset");
    _options.add_options()
        ("batch-size,b", po::value<size_t>()->
            default_value(64), "batch size");
    _options.add_options()
        ("log-per-steps", po::value<size_t>()->
            default_value(100), "log per steps");
    _options.add_options()
        ("checkpoint-per-epoch", po::value<size_t>()->
            default_value(10), "checkpoint per epoch");
    _options.add_options()
        ("model-dir", po::value<std::string>()->
            default_value("model"), "model dir");
    _options.add_options()
        ("start-epoch", po::value<size_t>()->
            default_value(0), "start epoch");
    _options.add_options()
        ("num-epochs", po::value<size_t>()->
            default_value(10), "num epochs");
}

std::string Options::data_config() {
    return _results["data-config"].as<std::string>();
}

std::string Options::data_root() {
    if (_results.count("data-root")) {
        return _results["data-root"].as<std::string>();
    }
    return "";
}

size_t Options::batch_size() {
    return _results["batch-size"].as<size_t>();
}

size_t Options::log_per_steps() {
    return _results["log-per-steps"].as<size_t>();
}

size_t Options::checkpoint_per_epoch() {
    return _results["checkpoint-per-epoch"].as<size_t>();
}

std::string Options::model_dir() {
    return _results["model-dir"].as<std::string>();
}

size_t Options::start_epoch() {
    return _results["start-epoch"].as<size_t>();
}

size_t Options::num_epochs() {
    return _results["num-epochs"].as<size_t>();
}

void Options::parse(int argc, char* argv[]) {
    po::store(po::parse_command_line(argc, argv, _options),
        _results);
    po::notify(_results);
    if (_results.count("help")) {
        cout << _options << "\n";
        throw OptionsExitsProgram();
    }
    if (_results.count("version")) {
        cout << "version " << version << "\n";
        throw OptionsExitsProgram();
    }
}

}
