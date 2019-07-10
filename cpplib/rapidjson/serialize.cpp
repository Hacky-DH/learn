#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <rapidjson/document.h>

using std::vector;
using std::map;
using std::string;
using rapidjson::Document;
using rapidjson::Value;


class Edge {
	long src_id;
	long dst_id;
	int edge_type;
	float weight;
	map<int, vector<long>> uint64_feature;
	map<int, vector<float>> float_feature;
	map<int, string> binary_feature;
};


class Block {
public:
    Block(){}
    ~Block(){}

protected:
    template <typename Writer>
    void Serialize(Writer& writer) const {
    }

private:
	long node_id;
	int node_type;
	float node_weight;
	map<int, map<long, float>> neighbor;
	map<int, vector<long>> uint64_feature;
	map<int, vector<float>> float_feature;
	map<int, string> binary_feature;
	vector<Edge> edge;
};


void lambda() {
	std::vector<int> v={1,4,8};
	std::for_each(std::begin(v), std::end(v),
		[](const auto& i){std::cout<<i<<" ";});
}


int main() {
	const char json[] = " { \"hello\" : \"world\", \"t\" : true , \"f\" : false, \"n\": null, \"i\":123, \"pi\": 3.1416, \"a\":[1, 2, 3, 4] } ";

    Document document;
    if (document.Parse(json).HasParseError())
        return 1;
    assert(document.IsObject());
    assert(document.HasMember("hello"));
    assert(document["hello"].IsString());
    printf("hello = %s\n", document["hello"].GetString());
    const Value& v = document["t"];
    assert(v.IsBool());
}

//serialize/deserialize
