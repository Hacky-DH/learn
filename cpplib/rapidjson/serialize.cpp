// rapidjson doc http://rapidjson.org/zh-cn/index.html
#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <fstream>
#include <rapidjson/document.h>
#include <rapidjson/pointer.h>
#include <rapidjson/writer.h>
#include <rapidjson/istreamwrapper.h>
#include <rapidjson/error/en.h>

namespace serialize {
using std::vector;
using std::map;
using std::string;
using std::ifstream;
using std::cerr;
using std::cout;
using std::endl;
using rapidjson::Document;
using rapidjson::Value;
using rapidjson::Pointer;
using rapidjson::IStreamWrapper;
using rapidjson::GetParseError_En;

// json demo from https://github.com/alibaba/euler/wiki/Preparing-Data

class Edge {
	long src_id;
	long dst_id;
	int edge_type;
	float weight;
	map<int, vector<long>> uint64_feature;
	map<int, vector<float>> float_feature;
	map<int, string> binary_feature;
protected:
	template <typename Writer>
    void serialize(Writer& writer) const {
    }
    void deserialize(Document& doc) {
    }
};


class Block {
private:
	long node_id;
	int node_type;
	float node_weight;
	map<int, map<long, float>> neighbor;
	map<int, vector<long>> uint64_feature;
	map<int, vector<float>> float_feature;
	map<int, string> binary_feature;
	vector<Edge> edge;
protected:
	template <typename Writer>
    void serialize(Writer& writer) const {
    }
    void deserialize(Document& doc) {
    }
};

int test(const string& file_name) {
	ifstream stream(file_name);
	IStreamWrapper wrap(stream);
	Document doc;
	if(doc.ParseStream(wrap).HasParseError()) {
		cerr<<"parse error: "<<GetParseError_En(doc.GetParseError())<<endl;
		return 1;
	}
    assert(doc.IsObject());
    stream.close();
    return 0;
}


void lambda() {
	std::vector<int> v={1,4,8};
	std::for_each(std::begin(v), std::end(v),
		[](const auto& i){std::cout<<i<<" ";});
}

} // end of namespace


int main() {
	return serialize::test("data.json");
}

//serialize/deserialize
