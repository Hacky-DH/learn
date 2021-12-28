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

int main(int argc, char const* argv[]) {
  int c = 10;
  auto r1 = f1(10);
  auto r2 = f2(20);
  for (int i = 0; i < c; ++i) {
    auto a = r1(i);
    std::cout << "f1 " << a << std::endl;
  }
  for (int i = 0; i < c; ++i) {
    auto b = r2(i);
    std::cout << "f2 " << b << std::endl;
  }
  auto r3 = f3(30);
  for (int i = 0; i < c; ++i) {
    std::cout << "f3 " << r3(i) << std::endl;
  }
  
  double pi = 3.1415926;
  double r = 2.0;

  // Function object is not closure.
  // follow code will compile error:
  // use of local variable with automatic storage from containing function pi
  /*
  class CircleArea {
   public:
    CircleArea() {}
    double operator()(double r) const { return pi * r * r; }
  };
  CircleArea circleArea;
  */

  // lambda is a closure
  // lambda as closure like class as instance
  auto circleArea = [=](double r) { return pi * r * r; };
  double area = circleArea(r);
  std::cout << area << std::endl;

  return 0;
}
/*
output:
f1 10
f1 32767
f1 32768
f1 32769
f1 32770
f1 32771
f1 32772
f1 32773
f1 32774
f1 32775
f2 0
f2 1
f2 3
f2 6
f2 10
f2 15
f2 21
f2 28
f2 36
f2 45
f3 30
f3 31
f3 33
f3 36
f3 40
f3 45
f3 51
f3 58
f3 66
f3 75
12.5664
*/
