#include <functional>
#include <iostream>

// implement an incrementer using closure
// https://leimao.github.io/blog/CPP-Closure/

// not answer
std::function<int(int)> f1(int n) {
  return [&](int i) { return n += i; };
}

// not answer
std::function<int(int)> f2(int n) {
  int m = n;
  return [&](int i) { return m += i; };
}

struct lam {
  int m;
  lam(int m) : m(m) {}
  int operator()(int i) { return m += i; }
};

// answer using functor, but not closure
lam f3(int n) { return lam(n); }

// answer using mutable lambda
std::function<int(int)> f4(int n) {
  return [=](int i) mutable { return n += i; };
}

int main(int argc, char const* argv[]) {
  int c = 10;
  std::cout << "f1: ";
  auto r1 = f1(10);
  for (int i = 0; i < c; ++i) {
    // auto a = r1(i);
    // std::cout << a << ",";
    std::cout << r1(i) << ",";
  }
  std::cout << std::endl;

  std::cout << "f2: ";
  auto r2 = f2(20);
  for (int i = 0; i < c; ++i) {
    // auto b = r2(i);
    // std::cout << b << ",";
    std::cout << r2(i) << ",";
  }
  std::cout << std::endl;

  std::cout << "f3: ";
  auto r3 = f3(30);
  for (int i = 0; i < c; ++i) {
    std::cout << r3(i) << ",";
  }
  std::cout << std::endl;

  std::cout << "f4: ";
  auto r4 = f4(40);
  for (int i = 0; i < c; ++i) {
    std::cout << r4(i) << ",";
  }
  std::cout << std::endl;

  // answer using lambda
  std::cout << "f5: ";
  int init = 50;
  // Function object is not closure.
  // follow code will compile error:
  // use of local variable with automatic storage from containing function init
  /*
  struct lam_error {
    int operator()(int i) { return init += i; }
  };
  */
  // lambda is a closure, lambda as closure like class as instance
  auto f5 = [&](int i) { return init += i; };
  for (int i = 0; i < c; ++i) {
    std::cout << f5(i) << ",";
  }
  std::cout << std::endl;

  return 0;
}
/*
ouput:
f1: 10,1,2,3,4,5,6,7,8,9,
f2: 0,1,3,6,10,15,21,28,36,45,
f3: 30,31,33,36,40,45,51,58,66,75,
f4: 40,41,43,46,50,55,61,68,76,85,
f5: 50,51,53,56,60,65,71,78,86,95,
*/
