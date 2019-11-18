#define BOOST_TEST_MODULE "Test for ic"
#include <boost/test/included/unit_test.hpp>
#include "utils.h"

BOOST_AUTO_TEST_SUITE(utils)
BOOST_AUTO_TEST_CASE(utils_str) {
    _putenv("TEST_ENV=a simple string");
    std::string str;
    get_env<std::string>("TEST_ENV", str);
    BOOST_TEST(str == "a simple string");
}

BOOST_AUTO_TEST_CASE(utils_int) {
    _putenv("TEST_ENV=86");
    int i;
    get_env<int>("TEST_ENV", i);
    BOOST_TEST(i == 86);
}

BOOST_AUTO_TEST_CASE(utils_float) {
    namespace tt = boost::test_tools;
    _putenv("TEST_ENV=86.68");
    float f;
    get_env<float>("TEST_ENV", f);
    BOOST_TEST(f == 86.68, tt::tolerance(0.001));
}
BOOST_AUTO_TEST_SUITE_END()
