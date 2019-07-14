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

	void deserialize(Document& doc, int index=0) {
		stringstream ss;
		ss<<"/edge/"<<index;
		Pointer pointer = Pointer(ss.str().c_str());
		Value* v = pointer.Get(doc);
		assert(v);
		auto ed = v->GetObject();
		src_id = ed["src_id"].GetInt64();
		dst_id = ed["dst_id"].GetInt64();
		edge_type = ed["edge_type"].GetInt();
		weight = ed["weight"].GetDouble();
		for (const auto& fid : ed["uint64_feature"].GetObject()) {
			vector<int64_t> ids;
			for(const auto& f : fid.value.GetArray()) {
				ids.push_back(f.GetInt64());
			}
			uint64_feature[std::stoi(fid.name.GetString())] = ids;
		}
		for (const auto& fid : ed["float_feature"].GetObject()) {
			vector<double> ids;
			for(const auto& f : fid.value.GetArray()) {
				ids.push_back(f.GetDouble());
			}
			float_feature[std::stoi(fid.name.GetString())] = ids;
		}
		for (const auto& fid : ed["binary_feature"].GetObject()) {
			binary_feature[std::stoi(fid.name.GetString())] = fid.value.GetString();
		}
	}

	string str() const {
		stringstream ss;
		ss<<"Edge: "<<endl;
		ss<<"src_id: "<<src_id<<endl;
		ss<<"dst_id: "<<dst_id<<endl;
		ss<<"edge_type: "<<edge_type<<endl;
		ss<<"weight: "<<weight<<endl;
		ss<<"uint64_feature: ";
		for (auto const& [id, val] : uint64_feature) {
			ss<<id<<"{";
			for (auto const& v : val) {
				ss<<v<<",";
			}
			ss<<"}";
		}
		ss<<endl;
		ss<<"float_feature: ";
		for (auto const& [id, val] : float_feature) {
			ss<<id<<"{";
			for (auto const& v : val) {
				ss<<v<<",";
			}
			ss<<"}";
		}
		ss<<endl;
		ss<<"binary_feature: ";
		for (auto const& [id, val] : binary_feature) {
			ss<<"("<<id<<","<<val<<")";
		}
		ss<<endl;
		return ss.str();
	}
};


class Block {
	typedef map<int64_t, double> NeighborId;
private:
	int64_t node_id;
	int node_type;
	double node_weight;
	map<int, NeighborId> neighbor;
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
		// object in object
		if(v) {
			for (const auto& nid : v->GetObject()) {
				NeighborId mid;
				for(const auto& w : nid.value.GetObject()) {
					mid[std::stol(w.name.GetString())] = w.value.GetDouble();
				}
				neighbor[std::stoi(nid.name.GetString())] = mid;
			}
		}
		// array in object
		v = Pointer("/uint64_feature").Get(doc);
		if(v) {
			for (const auto& fid : v->GetObject()) {
				vector<int64_t> ids;
				for(const auto& f : fid.value.GetArray()) {
					ids.push_back(f.GetInt64());
				}
				uint64_feature[std::stoi(fid.name.GetString())] = ids;
			}
		}
		v = Pointer("/float_feature").Get(doc);
		if(v) {
			for (const auto& fid : v->GetObject()) {
				vector<double> ids;
				for(const auto& f : fid.value.GetArray()) {
					ids.push_back(f.GetDouble());
				}
				float_feature[std::stoi(fid.name.GetString())] = ids;
			}
		}
		v = Pointer("/binary_feature").Get(doc);
		if(v) {
			for (const auto& fid : v->GetObject()) {
				binary_feature[std::stoi(fid.name.GetString())] = fid.value.GetString();
			}
		}
		// object in array
		v = Pointer("/edge").Get(doc);
		if(v) {
			Edge ed;
			for (int i=0; i < v->GetArray().Size(); ++i) {
				ed.deserialize(doc, i);
				edge.push_back(ed);
			}
		}
	}

	string str() const {
		stringstream ss;
		ss<<"Block: "<<endl;
		ss<<"node_id: "<<node_id<<endl;
		ss<<"node_type: "<<node_type<<endl;
		ss<<"node_weight: "<<node_weight<<endl;
		ss<<"neighbor: ";
		for (auto const& [type, nb] : neighbor) {
			ss<<type<<"{";
			for (auto const& [id, weight] : nb) {
				ss<<"("<<id<<","<<weight<<")";
			}
			ss<<"}";
		}
		ss<<endl;
		ss<<"uint64_feature: ";
		for (auto const& [id, val] : uint64_feature) {
			ss<<id<<"{";
			for (auto const& v : val) {
				ss<<v<<",";
			}
			ss<<"}";
		}
		ss<<endl;
		ss<<"float_feature: ";
		for (auto const& [id, val] : float_feature) {
			ss<<id<<"{";
			for (auto const& v : val) {
				ss<<v<<",";
			}
			ss<<"}";
		}
		ss<<endl;
		ss<<"binary_feature: ";
		for (auto const& [id, val] : binary_feature) {
			ss<<"("<<id<<","<<val<<")";
		}
		ss<<endl;
		ss<<"edges:"<<endl;
		for (const auto& e : edge) {
			ss<<"{"<<e.str()<<"}";
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
	//Edge e;
	//e.deserialize(doc);
	//cout<<e.str()<<endl;
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
