#include <string>

// get rss(Resident Set Size) of current process
// return Bytes
uint64_t GetRSS();

// return human string
std::string GetRSSStr();


uint64_t GetRSS() {
  std::fstream stat("/proc/self/stat");
  if (!stat.is_open()) {
    return 0;
  }
  std::string str;
  uint64_t size;
  // i=22 VSZ Byte
  for (size_t i = 0; i < 25; ++i) {
    if (i == 23) {
      // i=23, rss is page size
      stat >> size;
    } else {
      stat >> str;
    }
  }
  return size * 4;
}

// return human string
std::string GetRSSStr() {
  uint64_t rss = GetRSS();
  double result = 1.;
  std::string fotmat("%.3f");
  char buff[64];
  if (rss >= (1ULL << 30)) {
    fotmat.append("TiB");
    result = (1ULL << 30);
  } else if (rss >= (1ULL << 20)) {
    fotmat.append("GiB");
    result = (1ULL << 20);
  } else if (rss >= (1ULL << 10)) {
    fotmat.append("MiB");
    result = (1ULL << 10);
  } else {
    fotmat.append("KiB");
    result = 1.;
  }
  std::snprintf(buff, 64, fotmat.c_str(), static_cast<double>(rss) / result);
  return buff;
}
