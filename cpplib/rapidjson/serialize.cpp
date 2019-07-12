// rapidjson doc http://rapidjson.org/zh-cn/index.html
// demo of serialize/deserialize cpp object
// build g++ -std=c++1z serialize.cpp
#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <string>
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
using std::stringstream;
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
	int64_t src_id;
	int64_t dst_id;
	int edge_type;
	double weight;
	map<int, vector<int64_t>> uint64_feature;
	map<int, vector<double>> float_feature;
	map<int, string> binary_feature;
public:
	template <typename Writer>
	void serialize(Writer& writer) const {
	}

	void deserialize(Document& doc) {
	}
};


class Block {
private:
	int64_t node_id;
	int node_type;
	double node_weight;
	map<int, map<int64_t, double>> neighbor;
	map<int, vector<int64_t>> uint64_feature;
	map<int, vector<double>> float_feature;
	map<int, string> binary_feature;
	vector<Edge> edge;
public:
	template <typename Writer>
	void serialize(Writer& writer) const {
	}

	void deserialize(Document& doc) {
		Value* v = Pointer("/node_id").Get(doc);
		if(v) node_id = v->GetInt64();
		v = Pointer("/node_type").Get(doc);
		if(v) node_type = v->GetInt();
		v = Pointer("/node_weight").Get(doc);
		if(v) node_weight = v->GetDouble();
		v = Pointer("/neighbor").Get(doc);
		if(v) node_weight = v->GetDouble();
	}

	string str() const {
		stringstream ss;
		ss<<"Block: "<<endl;
		ss<<"node_id: "<<node_id<<endl;
		ss<<"node_type: "<<node_type<<endl;
		ss<<"node_weight: "<<node_weight<<endl;
		ss<<"neighbor: ";
		for (auto const& [type, nb] : neighbor) {
			ss<<type;
			for (auto const& [id, weight] : nb) {
				ss<<id<<weight<<" ";
			}
			ss<<";";
		}
		ss<<endl;
		ss<<"uint64_feature: ";
		for (auto const& [id, val] : uint64_feature) {
			ss<<id;
			for (auto const& v : val) {
				ss<<v<<" ";
			}
			ss<<";";
		}
		ss<<endl;
		ss<<"float_feature: ";
		for (auto const& [id, val] : float_feature) {
			ss<<id;
			for (auto const& v : val) {
				ss<<v<<" ";
			}
			ss<<";";
		}
		ss<<endl;
		ss<<"binary_feature: ";
		for (auto const& [id, val] : binary_feature) {
			ss<<id<<val<<" ";
		}
		ss<<endl;
		return ss.str();
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
	Block block;
	block.deserialize(doc);
	cout<<block.str()<<endl;
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
