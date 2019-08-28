#include <pybind11/pybind11.h>

// https://pybind11.readthedocs.io/en/stable/classes.html

class Demo {
public:
    Demo(const std::string &name, int a, float b) : name(name),a(a),b(b) { }
    void set_name(const std::string &name_) { name = name_; }
    const std::string &get_name() const { return name; }

    std::string to_str() {
        std::string res = "Demo[name=" + name;
        res += ",a=" + std::to_string(a);
        res += ",b=" + std::to_string(b);
        res += "]";
        return res;
    }

    float operator()() const {
        return a * 8 + b;
    }

private:
    std::string name;
    int a;
    float b;
};

int add(int i, int j) {
    return i + j;
}

using pybind11::class_;
using pybind11::init;

PYBIND11_MODULE(cls, m) {
    m.doc() = "pybind11 class example plugin";
    // bindings for a class type
    // Operator overloading
    class_<Demo>(m, "Demo", "Demo class")
        .def(init<const std::string &, int, float>())
        .def_property("name", &Demo::get_name, &Demo::set_name)
        .def("__repr__", &Demo::to_str)
        .def("__call__", &Demo::operator());
    // bindings for a simple function
    m.def("add", &add, "A function which adds two numbers");
}
