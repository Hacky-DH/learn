#include "options.h"

namespace ic {

const std::string version("1.0.0");

// class Options
Options::Options() :_options("Options") {
    // set all options
    fs::path default_data_root;
    default_data_root = default_data_root / ".." / ".." /
        "dataset" / ".local" / "mnist";
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
        ("data-root,d", po::value<std::string>()->
            default_value(default_data_root.string()),
            "The root path of dataset");
    _options.add_options()
        ("batch-size,b", po::value<int>()->
            default_value(1), "batch size");
}

std::string Options::data_config() {
    return _results["data-config"].as<std::string>();
}

std::string Options::data_root() {
    return _results["data-root"].as<std::string>();
}

int Options::batch_size() {
    return _results["batch-size"].as<int>();
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