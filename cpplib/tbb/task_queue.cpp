/*
 * test task_group and concurrent_bounded_queue
 * https://github.com/oneapi-src/oneTBB
 *
 * compile with
 * g++ -I include/ -Wl,-rpath,lib64/ lib64/libtbb.so task_queue.cpp
 */

#include <oneapi/tbb/concurrent_queue.h>
#include <oneapi/tbb/task_group.h>

#include <chrono>
#include <thread>
#include <iostream>

int main() {
  oneapi::tbb::task_group task_group;
  oneapi::tbb::concurrent_bounded_queue<int> queue;
  queue.set_capacity(50);

  // producers
  for (int i = 0; i < 100; ++i) {
    task_group.run([&queue, i] { queue.push(i); });
  }

  // consumers
  for (int i = 0; i < 10; ++i) {
    task_group.run([&queue, i] {
      int res = -1;
      std::cout << " recv task start " << i << std::endl;
      //sleep a while
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
      while (!queue.empty()) {
        queue.pop(res);
        std::cout << " task " << i << " recv " << res << std::endl;
      }
      std::cout << " recv task end " << i << std::endl;
    });
  }
  if (oneapi::tbb::task_group_status::complete == task_group.wait()) {
    std::cout << "done";
  }
}
