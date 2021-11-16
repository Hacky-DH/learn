#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>

using namespace std;
mutex m;
condition_variable cond;
int flag = 0;

void producer() {
  this_thread::sleep_for(chrono::seconds(1));
  lock_guard<mutex> guard(m);
  flag = 100;
  cond.notify_one();
  cout << "notify..." << endl;
}

void customer() {
  unique_lock<mutex> lk(m);
  if (m.try_lock())
    cout << "mutex unlocked after unique_lock" << endl;
  else
    cout << "mutex locked after unique_lock" << endl;
  while (flag == 0) {
    cout << "wait..." << endl;
    cond.wait(lk);
  }
  if (m.try_lock())
    cout << "mutex unlocked after wait" << endl;
  else
    cout << "mutex locked after wait" << endl;
  cout << "flag==100? " << flag << endl;
}

int main() {
  thread one(producer);
  thread two(customer);
  one.join();
  two.join();
  return 0;
}
