#include <atomic>
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

// print A B in turn by multi threads for 10 times
// g++ printABMThread.cpp -pthread -std=c++11

namespace C1 {
// using atomic is wrong way
// only print <10 times
std::atomic<bool> flag(true);

void wrongA() {
  for (int i = 0; i < 10; ++i) {
    if (flag) {
      std::cout << "A ";
      flag = false;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  }
}

void wrongB() {
  for (int i = 0; i < 10; ++i) {
    if (!flag) {
      std::cout << "B ";
      flag = true;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  }
}

void run() {
  std::cout << "using atomic is wrong way(<10 times)" << std::endl;
  std::thread a(wrongA), b(wrongB);
  a.join();
  b.join();
  std::cout << std::endl;
}

}  // namespace C1

namespace C2 {
// use condition_variable by two threads

std::mutex m;
std::condition_variable cv;
bool turn = false;

void rightA() {
  std::unique_lock<std::mutex> lk(m);
  for (int i = 0; i < 10; ++i) {
    cv.wait(lk, [] { return !turn; });
    std::cout << "A ";
    turn = true;
    cv.notify_one();
  }
}

void rightB() {
  std::unique_lock<std::mutex> lk(m);
  for (int i = 0; i < 10; ++i) {
    cv.wait(lk, [] { return turn; });
    std::cout << "B ";
    turn = false;
    cv.notify_one();
  }
}

void run() {
  std::cout << "using condition_variable by two threads" << std::endl;
  std::thread a(rightA), b(rightB);
  a.join();
  b.join();
  std::cout << std::endl;
}
}  // namespace C2

namespace C3 {
// use condition_variable by multi threads

std::mutex m;
std::condition_variable cv;
int threads = 5;
int flag = 0;

void mthread(int index) {
  std::unique_lock<std::mutex> lk(m);
  for (int i = 0; i < 10; ++i) {
    cv.wait(lk, [=] { return flag == index; });
    std::cout << char('A' + index) << " ";
    flag = (flag + 1) % threads;
    cv.notify_all();
  }
}

void run() {
  std::cout << "using condition_variable by 5 threads" << std::endl;
  std::vector<std::thread> tv;
  for (int i = 0; i < threads; ++i) {
    tv.emplace_back(mthread, i);
  }
  for (int i = 0; i < threads; ++i) {
    tv[i].join();
  }
  std::cout << std::endl;
}
}  // namespace C3

int main(int argc, char const *argv[]) {
  C1::run();
  C2::run();
  C3::run();
  return 0;
}

/*
output:
using atomic is wrong way(<10 times)
A B A B A B A B A B A B A B
using condition_variable by two threads
A B A B A B A B A B A B A B A B A B A B
using condition_variable by 5 threads
A B C D E A B C D E A B C D E A B C D E A B C D E A B C D E A B C D E A B C D E A B C D E A B C D E
*/
