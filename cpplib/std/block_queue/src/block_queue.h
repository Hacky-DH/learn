#include <chrono>
#include <condition_variable>
#include <exception>
#include <memory>
#include <mutex>
#include <queue>

class TimeoutException : public std::exception {
 public:
  const char* what() const throw() { return "time out"; }
};

/**
 * thread safe block queue
 */
template <typename T>
class BlockQueue {
 private:
  mutable std::queue<T> m_queue;
  std::mutex m_mutex;
  std::condition_variable not_empty, not_full;
  size_t max_capacity;

 public:
  explicit BlockQueue(size_t capacity) : max_capacity(capacity) {}
  BlockQueue(const BlockQueue& bq) {
    std::lock_guard<std::mutex> lk(m_mutex);
    m_queue = bq.m_queue;
  }

  BlockQueue(const BlockQueue&& bq) = delete;
  BlockQueue& operator=(const BlockQueue&) = delete;

  /**
   * not wait push
   * @param push value
   * @return false if queue is full
   */
  bool try_push(T new_value) {
    std::lock_guard<std::mutex> lk(m_mutex);
    if (m_queue.size() >= max_capacity) return false;
    m_queue.push(new_value);
    not_empty.notify_all();
    return true;
  }

  void wait_and_push(T new_value) {
    std::unique_lock<std::mutex> lk(m_mutex);
    not_full.wait(lk, [this] { return m_queue.size() < max_capacity; });
    m_queue.push(new_value);
    not_empty.notify_all();
  }

  template <class Rep, class Period>
  void wait_for_and_push(T new_value,
                         const std::chrono::duration<Rep, Period>& time) {
    std::unique_lock<std::mutex> lk(m_mutex);
    if (!not_full.wait(lk, time,
                       [this] { return m_queue.size() < max_capacity; }))
      throw TimeoutException();
    m_queue.push(new_value);
    not_empty.notify_all();
  }

  /**
   * not wait pop
   * @param pop value
   * @return false if queue is empty
   */
  bool try_pop(T& value) {
    std::lock_guard<std::mutex> lk(m_mutex);
    if (m_queue.empty()) return false;
    value = m_queue.front();
    m_queue.pop();
    not_full.notify_all();
    return true;
  }

  /**
   * not wait pop
   * return shared_ptr
   */
  std::shared_ptr<T> try_pop() {
    std::lock_guard<std::mutex> lk(m_mutex);
    if (m_queue.empty()) return std::shared_ptr<T>();
    auto value = std::make_shared<T>(m_queue.front());
    m_queue.pop();
    not_full.notify_all();
    return value;
  }

  /**
   * wait pop
   * @param pop value
   */
  void wait_and_pop(T& value) {
    std::unique_lock<std::mutex> lk(m_mutex);
    not_empty.wait(lk, [this] { return !m_queue.empty(); });
    value = m_queue.front();
    m_queue.pop();
    not_full.notify_all();
  }

  /**
   * wait pop
   * return shared_ptr
   */
  std::shared_ptr<T> wait_and_pop() {
    std::unique_lock<std::mutex> lk(m_mutex);
    not_empty.wait(lk, [this] { return !m_queue.empty(); });
    auto value = std::make_shared<T>(m_queue.front());
    m_queue.pop();
    not_full.notify_all();
    return value;
  }

  /**
   * wait pop with timeout
   * return shared_ptr
   */
  template <class Rep, class Period>
  std::shared_ptr<T> wait_for_and_pop(
      const std::chrono::duration<Rep, Period>& time) {
    std::unique_lock<std::mutex> lk(m_mutex);
    if (!not_empty.wait(lk, time, [this] { return !m_queue.empty(); }))
      throw TimeoutException();
    auto value = std::make_shared<T>(m_queue.front());
    m_queue.pop();
    not_full.notify_all();
    return value;
  }

  /**
   * empty still lock
   */
  bool empty() const {
    std::lock_guard<std::mutex> lk(m_mutex);
    return m_queue.empty();
  }

  size_t size() const {
    std::lock_guard<std::mutex> lk(m_mutex);
    return m_queue.size();
  }

  /*
     the following is java interface for BlockingQueue
   */

  void put(T new_value) { wait_and_push(new_value); }

  std::shared_ptr<T> take() { return wait_and_pop(); }

  bool offer(T& value) { return try_push(value); }

  bool poll() {
    T res;
    return try_pop(res);
  }

  template <class Rep, class Period>
  void offer(T new_value, const std::chrono::duration<Rep, Period>& time) {
    wait_for_and_push(new_value, time);
  }

  template <class Rep, class Period>
  std::shared_ptr<T> poll(const std::chrono::duration<Rep, Period>& time) {
    return wait_for_and_pop(time);
  }
};