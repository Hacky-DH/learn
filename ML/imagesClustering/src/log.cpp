#include "log.h"

namespace ic {
namespace log {

void init(bool log_to_console) {
    if (log_to_console) {
        logging::add_console_log();
    }
    logging::add_file_log
    (
        keywords::file_name = "ic_log_%N.log",
        keywords::open_mode = std::ios_base::out | std::ios_base::app,
        keywords::rotation_size = 10 << 20,
        keywords::time_based_rotation = sinks::file::rotation_at_time_point(0, 0, 0),
        // This makes the sink to write log records that look like this:
        // YYYY-MM-DD HH:MI:SS [info] A normal severity message
        keywords::format =
        (
            expr::stream
            << expr::format_date_time< boost::posix_time::ptime >
            ("TimeStamp", "%Y-%m-%d %H:%M:%S")
            << " [" << logging::trivial::severity
            << "] " << expr::smessage
        ),
        keywords::auto_flush = true
    );

    logging::core::get()->set_filter
    (
        logging::trivial::severity >= logging::trivial::info
    );
    logging::add_common_attributes();
}
}
}
