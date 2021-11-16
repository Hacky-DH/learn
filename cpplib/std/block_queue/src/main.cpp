#include <iostream>
#include <thread>

#include "block_queue.h"

int main() {
  BlockQueue<int> bq(5);
  std::thread t([&] {
    std::this_thread::sleep_for(std::chrono::seconds(2));
    bq.put(5);
  });
  if (!bq.poll()) {
    std::cout << *bq.take() << std::endl;
  }
  t.join();
  return 0;
}
