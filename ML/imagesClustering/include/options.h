#pragma once
#include <iostream>
#include <string>
#include <exception>
#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>

namespace ic {

using std::cout;
using std::wcout;
using std::cerr;
using std::wcerr;
using std::endl;
namespace fs = boost::filesystem;
namespace po = boost::program_options;

extern const std::string version;

// Used to exit the program if the help/version option is set
class OptionsExitsProgram : public std::exception {};

class Options {
public:
    Options();

    std::string data_config();
    std::string data_root();
    std::string model_dir();
    size_t batch_size();
    size_t log_per_steps();
    size_t checkpoint_per_epoch();
    size_t start_epoch();
    size_t num_epochs();

    void parse(int argc, char* argv[]);
private:
    po::options_description _options;
    po::variables_map _results;
};

}
