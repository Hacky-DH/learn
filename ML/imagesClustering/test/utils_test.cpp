#define BOOST_TEST_MODULE "Test for utils"
#include <boost/test/included/unit_test.hpp>
#include "utils.h"

BOOST_AUTO_TEST_CASE(utils) {
    putenv("TEST_ENV=a simple string");
    std::string str;
    get_env<std::string>("TEST_ENV", str);
    BOOST_TEST(str == "a simple string");
}
