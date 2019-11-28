#pragma once
#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/sinks/text_file_backend.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <boost/log/utility/setup/console.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/sources/record_ostream.hpp>
#include <boost/log/sources/global_logger_storage.hpp>
#include <boost/log/support/date_time.hpp>

namespace ic {
using namespace boost::log::trivial;
namespace log {
namespace logging = boost::log;
namespace src = boost::log::sources;
namespace sinks = boost::log::sinks;
namespace keywords = boost::log::keywords;
namespace expr = boost::log::expressions;

// trivial example:
//BOOST_LOG_TRIVIAL(info)

// global logger
BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(ic_logger,
    log::src::severity_logger_mt<severity_level>);

using lg_t = src::severity_logger<severity_level>;

void init(bool log_to_console=true);
}
}
