#include <rapidjson/document.h>
#include <rapidjson/error/en.h>
#include <iostream>

// g++ rj.cc -std=c++17 -o rj -O0 -g
// g++ rj.cc -std=c++17 -o rj -O2 -DNDEBUG

constexpr const char* schema_str = R"raw(
{
  "vertexes":
  [
    {
      "vtype" : 0, "entity" : "DT_INT64", "weight" : "DT_FLOAT",
      "attrs" : [
        {"name" : "cid", "dtype" : "DT_INT16"},
        {"name" : "price", "dtype" : "DT_FLOAT"},
        {"name" : "attr", "dtype" : "DT_STRING"}
      ]
    },{
      "vtype" : 1, "entity" : "DT_INT64", "weight" : "DT_FLOAT",
      "attrs" : [
        {"name" : "age", "dtype" : "DT_UINT8"},
        {"name" : "edu", "dtype" : "DT_ARRAY_INT64"},
        {"name" : "addr", "dtype" : "DT_FLOAT"},
        {"name" : "test", "dtype" : "DT_ARRAY_INT32"}
      ]
    }
  ]
}
)raw";

constexpr const char* SCM_VERTEX = "vertexes";
constexpr const char* SCM_VTYPE = "vtype";
constexpr const char* SCM_ENTITY = "entity";
constexpr const char* SCM_WEIGHT = "weight";
constexpr const char* SCM_ATTRS = "attrs";
constexpr const char* SCM_ATTR_NAME = "name";
constexpr const char* SCM_ATTR_TYPE = "dtype";

bool parse() {
  rapidjson::Document doc;
  rapidjson::ParseResult pr = doc.Parse(schema_str);
  if (!pr) {
    std::cerr << "[Schema] JSON parse error:"
              << rapidjson::GetParseError_En(pr.Code()) << "(" << pr.Offset()
              << ")";

    return false;
  }
  std::cout << "[Schema] root size: " << doc.MemberCount() << std::endl;
  rapidjson::Value::ConstMemberIterator maybe_vertexes =
      doc.FindMember(SCM_VERTEX);
  if (maybe_vertexes == doc.MemberEnd()) {
    std::cerr << "[Schema] " << SCM_VERTEX << " is not in schema!";
    return false;
  }
  const rapidjson::Value& vertexes = maybe_vertexes->value;
  if (!vertexes.IsArray()) {
    std::cerr << "[Schema] " << SCM_VERTEX << " must be an array!";
    return false;
  }
  const auto& vertex_array = vertexes.GetArray();
  size_t vtype_num = vertex_array.Size();
  std::cout << "[Schema] vertex type size: " << vtype_num << std::endl;
  for (size_t vtype_index = 0; vtype_index < vtype_num; ++vtype_index) {
    const auto& v_obj = vertex_array[vtype_index];
    std::cout << "[Schema] vertex type " << vtype_index
              << " size: " << v_obj.MemberCount() << std::endl;
    auto maybe_vtype = v_obj.FindMember(SCM_VTYPE);
    if (maybe_vtype != v_obj.MemberEnd()) {
      if (!maybe_vtype->value.IsNumber()) {
        std::cerr << "[Schema] " << SCM_VTYPE << " must be a number";
        return false;
      }
      std::cout << "[Schema] vertex type " << vtype_index
                << ",vtype:" << v_obj[SCM_VTYPE].GetInt() << std::endl;
    }
    auto maybe_entity = v_obj.FindMember(SCM_ENTITY);
    if (maybe_entity == v_obj.MemberEnd()) {
      std::cerr << "[Schema] "
                << " no entity";
      return false;
    }
    std::cout << "[Schema] vertex type " << vtype_index
              << ",entity:" << v_obj[SCM_ENTITY].GetString() << std::endl;
    auto maybe_weight = v_obj.FindMember(SCM_WEIGHT);
    if (maybe_weight == v_obj.MemberEnd()) {
      std::cerr << "[Schema] "
                << " no weight";
      return false;
    }
    std::cout << "[Schema] vertex type " << vtype_index
              << ",weight:" << v_obj[SCM_WEIGHT].GetString() << std::endl;
    auto maybe_attrs = v_obj.FindMember(SCM_ATTRS);
    if (maybe_attrs == v_obj.MemberEnd()) {
      std::cerr << "[Schema] "
                << " no attrs";
      return false;
    }
    std::cout << "[Schema] vertex attrs type " << vtype_index
              << ",attrs size:" << v_obj[SCM_ATTRS].Size() << std::endl;
    for (auto& v : v_obj.GetObject()) {
      if (v.value.IsArray()) {
        std::cout << "\t[Schema] vertex attrs name " << v.name.GetString()
                  << ", size=" << v.value.Size() << std::endl;
        for (auto& a : v.value.GetArray()) {
          const auto& nv = a.GetObject();
          std::cout << "\t\t[Schema] vertex attrs name "
                    << nv[SCM_ATTR_NAME].GetString() << "="
                    << nv[SCM_ATTR_TYPE].GetString() << std::endl;
        }
      } else {
        std::cout << "\t[Schema] vertex attrs name " << v.name.GetString()
                  << "=" << v.value.GetType() << std::endl;
      }
    }
  }
  std::cout << "Done\n";
  return true;
}

int main() { parse(); }
