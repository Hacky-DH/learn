// benchmark on oneapi::tbb::task_group
// total edge number: 13566
// MAX_QUEUE_SIZE = 8192
// 1. ConcurrentAddEdgesMoreOneQueue use MAX_QUEUE_NUMBER=10 queues, avg time 0.0301236 s
// 2. ConcurrentAddEdgesOneQueue use 1 queue, time 0.031908 s
// 3. ConcurrentAddEdgesNoQueue no use queue, avg time 0.01677 s

#include <oneapi/tbb/concurrent_queue.h>
#include <oneapi/tbb/concurrent_vector.h>
#include <oneapi/tbb/task_group.h>

struct LoadInfo {
  std::vector<Edge*>; edge_vec;
};
bool AddEdge(Edge*);

bool ConcurrentAddEdgesMoreOneQueue(
    const std::vector<LoadInfo>& load_infos) {
  // use more than one queue
  // avg time 0.0301236 s
  oneapi::tbb::task_group task_group;
  oneapi::tbb::concurrent_vector<Edge*> invalid_edges;
  int max_queue_number = GetEnv("MAX_QUEUE_NUMBER", (int)load_infos.size());
  max_queue_number = std::max(max_queue_number, (int)load_infos.size());
  std::vector<oneapi::tbb::concurrent_bounded_queue<Edge*>> queues(
      max_queue_number);
  int max_queue_size = GetEnv("MAX_QUEUE_SIZE", 8192);
  for (int i = 0; i < max_queue_number; ++i) {
    auto& queue = queues[i];
    queue.set_capacity(max_queue_size);
    for (auto& e : load_infos[i].edge_vec) {
      task_group.run([&queue, &e] { queue.push(e); });
    }
    task_group.run([&queue, &invalid_edges] {
      Edge* edge = nullptr;
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
      while (!queue.empty()) {
        queue.pop(edge);
        if (unlikely(!AddEdge(edge))) {
          invalid_edges.emplace_back(edge);
        }
      }
    });
  }
  if (unlikely(!invalid_edges.empty())) {
    LOG(WARNING) << "[Engine] " << invalid_edges.size() << " edges(one is "
                 << invalid_edges.at(0)->DebugStr() << ") have been ignored!";
    for (auto it : invalid_edges) {
      if (it) delete it;
    }
    invalid_edges.clear();
  }
  return oneapi::tbb::task_group_status::complete == task_group.wait();
}

bool ConcurrentAddEdgesOneQueue(
    const std::vector<LoadInfo>& load_infos) {
  // time 0.031908 s
  oneapi::tbb::task_group task_group;
  oneapi::tbb::concurrent_vector<Edge*> invalid_edges;
  oneapi::tbb::concurrent_bounded_queue<Edge*> queue;
  int max_queue_size = GetEnv("MAX_QUEUE_SIZE", 8192);
  queue.set_capacity(max_queue_size);

  for (auto& load_info : load_infos) {
    for (auto& e : load_info.edge_vec) {
      task_group.run([&queue, &e] { queue.push(e); });
    }
  }

  int consumer_num = GetEnv("BUILD_GRAPH_CONSUMER_NUM", 4);
  for (int i = 0; i < consumer_num; ++i) {
    task_group.run([&queue, &invalid_edges] {
      Edge* edge = nullptr;
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
      while (!queue.empty()) {
        queue.pop(edge);
        if (unlikely(!AddEdge(edge))) {
          invalid_edges.emplace_back(edge);
        }
      }
    });
  }

  if (unlikely(!invalid_edges.empty())) {
    LOG(WARNING) << "[Engine] " << invalid_edges.size() << " edges(one is "
                 << invalid_edges.at(0)->DebugStr() << ") have been ignored!";
    for (auto it : invalid_edges) {
      if (it) delete it;
    }
    invalid_edges.clear();
  }
  return oneapi::tbb::task_group_status::complete == task_group.wait();
}

bool ConcurrentAddEdgesNoQueue(const std::vector<LoadInfo>& load_infos) {
  // avg time 0.01677 s
  oneapi::tbb::task_group task_group;
  oneapi::tbb::concurrent_vector<Edge*> invalid_edges;

  for (auto& load_info : load_infos) {
    for (auto& e : load_info.edge_vec) {
      task_group.run([&invalid_edges, e] {
        if (unlikely(!AddEdge(e))) {
          invalid_edges.emplace_back(e);
        }
      });
    }
  }
  if (unlikely(!invalid_edges.empty())) {
    LOG(WARNING) << "[Engine] " << invalid_edges.size() << " edges(one is "
                 << invalid_edges.at(0)->DebugStr() << ") have been ignored!";
    for (auto it : invalid_edges) {
      if (it) delete it;
    }
    invalid_edges.clear();
  }
  return oneapi::tbb::task_group_status::complete == task_group.wait();
}
