#include <atomic>
#include <iostream>
#include <utility>

// for reducing the number of the same logs
// true only count is 2^n
template <typename T>
bool ShouldLog(T& count) {
  ++count;
  return (count & (count - 1)) == 0;
}

// for atomic
template <typename T>
std::pair<T, bool> ShouldLog(std::atomic<T>& count) {
  auto value = count.fetch_add(1, std::memory_order_relaxed);
  ++value;
  auto should = ((value & (value - 1)) == 0);
  return std::make_pair(value, should);
}

void test_int() {
  static int i = 0;
  if (ShouldLog(i)) {
    std::cout << "test_int " << i << std::endl;
  }
}

void test_atomic_int() {
  static std::atomic<int> i(0);
  auto sl = ShouldLog(i);
  if (sl.second) {
    std::cout << "test_atomic_int " << sl.first << std::endl;
  }
}

int main(int argc, char const* argv[]) {
  int c = 100;
  for (int i = 0; i < c; ++i) {
    test_int();
    test_atomic_int();
  }
  return 0;
}

/*
output:
test_int 1
test_atomic_int 1
test_int 2
test_atomic_int 2
test_int 4
test_atomic_int 4
test_int 8
test_atomic_int 8
test_int 16
test_atomic_int 16
test_int 32
test_atomic_int 32
test_int 64
test_atomic_int 64
*/
