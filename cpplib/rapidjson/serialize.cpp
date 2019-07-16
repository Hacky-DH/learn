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
#include <functional>
#include <rapidjson/document.h>
#include <rapidjson/pointer.h>
#include <rapidjson/writer.h>
#include <rapidjson/istreamwrapper.h>
#include <rapidjson/ostreamwrapper.h>
#include <rapidjson/error/en.h>

namespace serialize {
using std::vector;
using std::map;
using std::string;
using std::ifstream;
using std::ofstream;
using std::stringstream;
using std::cerr;
using std::cout;
using std::endl;
using std::to_string;
using rapidjson::Document;
using rapidjson::Value;
using rapidjson::Pointer;
using rapidjson::IStreamWrapper;
using rapidjson::OStreamWrapper;
using rapidjson::Writer;
using rapidjson::GetParseError_En;
using rapidjson::kObjectType;
using rapidjson::kArrayType;
using rapidjson::kStringType;

// json demo from https://github.com/alibaba/euler/wiki/Preparing-Data

class Edge {
	int64_t src_id = 0;
	int64_t dst_id = 0;
	int edge_type = 0;
	double weight = 0;
	map<int, vector<int64_t>> uint64_feature;
	map<int, vector<double>> float_feature;
	map<int, string> binary_feature;
public:
	template <typename V>
	void serialize(V& doc, int index=0) const {
		stringstream ss;
		ss<<"/edge/"<<index;
		auto& root = Pointer(ss.str().c_str()).Create(doc).SetObject();
		root.AddMember("src_id", src_id, doc.GetAllocator());
		root.AddMember("dst_id", dst_id, doc.GetAllocator());
		root.AddMember("edge_type", edge_type, doc.GetAllocator());
		root.AddMember("weight", weight, doc.GetAllocator());
		Value name(kStringType);
		{
			Value obj(kObjectType);
			for (auto const& [id, val] : uint64_feature) {
				Value arr(kArrayType);
				for (auto const& b : val) {
					arr.PushBack(b, doc.GetAllocator());
				}
				name.SetString(to_string(id).c_str(), doc.GetAllocator());
				obj.AddMember(name.Move(), arr.Move(), doc.GetAllocator());
			}
			root.AddMember("uint64_feature", obj, doc.GetAllocator());
		}
		{
			Value obj(kObjectType);
			for (auto const& [id, val] : float_feature) {
				Value arr(kArrayType);
				for (auto const& b : val) {
					arr.PushBack(b, doc.GetAllocator());
				}
				name.SetString(to_string(id).c_str(), doc.GetAllocator());
				obj.AddMember(name.Move(), arr.Move(), doc.GetAllocator());
			}
			root.AddMember("float_feature", obj, doc.GetAllocator());
		}
		{
			Value obj(kObjectType);
			Value value(kStringType);
			for (auto const& [id, val] : binary_feature) {
				name.SetString(to_string(id).c_str(), doc.GetAllocator());
				value.SetString(val.c_str(), doc.GetAllocator());
				obj.AddMember(name.Move(), value.Move(), doc.GetAllocator());
			}
			root.AddMember("binary_feature", obj, doc.GetAllocator());
		}
	}

	void deserialize(Document& doc, int index=0) {
		stringstream ss;
		ss<<"/edge/"<<index;
		Value* v = Pointer(ss.str().c_str()).Get(doc);
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
	int64_t node_id = 0;
	int node_type = 0;
	double node_weight = 0;
	map<int, NeighborId> neighbor;
	map<int, vector<int64_t>> uint64_feature;
	map<int, vector<double>> float_feature;
	map<int, string> binary_feature;
	vector<Edge> edge;
public:
	template <typename V>
	void serialize(V& doc) const {
		Pointer("/node_id").Set(doc, node_id);
		doc.AddMember("node_type", node_type, doc.GetAllocator());
		doc.AddMember("node_weight", node_weight, doc.GetAllocator());
		Value name(kStringType);
		{
			Value obj(kObjectType);
			for (auto const& [type, nb] : neighbor) {
				Value nb_obj(kObjectType);
				for (auto const& [id, weight] : nb) {
					name.SetString(to_string(id).c_str(), doc.GetAllocator());
					nb_obj.AddMember(name.Move(), Value(weight).Move(), doc.GetAllocator());
				}
				name.SetString(to_string(type).c_str(), doc.GetAllocator());
				obj.AddMember(name.Move(), nb_obj, doc.GetAllocator());
			}
			doc.AddMember("neighbor", obj, doc.GetAllocator());
		}
		{
			Value obj(kObjectType);
			for (auto const& [id, val] : uint64_feature) {
				Value arr(kArrayType);
				for (auto const& b : val) {
					arr.PushBack(b, doc.GetAllocator());
				}
				name.SetString(to_string(id).c_str(), doc.GetAllocator());
				obj.AddMember(name.Move(), arr.Move(), doc.GetAllocator());
			}
			doc.AddMember("uint64_feature", obj, doc.GetAllocator());
		}
		{
			Value obj(kObjectType);
			for (auto const& [id, val] : float_feature) {
				Value arr(kArrayType);
				for (auto const& b : val) {
					arr.PushBack(b, doc.GetAllocator());
				}
				name.SetString(to_string(id).c_str(), doc.GetAllocator());
				obj.AddMember(name.Move(), arr.Move(), doc.GetAllocator());
			}
			doc.AddMember("float_feature", obj, doc.GetAllocator());
		}
		{
			Value obj(kObjectType);
			Value value(kStringType);
			for (auto const& [id, val] : binary_feature) {
				name.SetString(to_string(id).c_str(), doc.GetAllocator());
				value.SetString(val.c_str(), doc.GetAllocator());
				obj.AddMember(name.Move(), value.Move(), doc.GetAllocator());
			}
			doc.AddMember("binary_feature", obj, doc.GetAllocator());
		}
		for (int i=0; i < edge.size(); ++i) {
			edge[i].serialize(doc, i);
		}
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

	vector<Edge>& get_edges() {
		return edge;
	}

	Block& add_edge(const Edge& e) {
		edge.push_back(e);
		return *this;
	}
};


int test(const string& input, const string& output) {
	ifstream stream(input);
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
	// dump
	if(!output.empty()) {
		ofstream of(output);
		OStreamWrapper osw(of);
		Writer<OStreamWrapper> writer(osw);
		Document doc;
		block.serialize(doc);
		doc.Accept(writer);
		of.close();
	}
	return 0;
}

int dump(const string& file_name) {
}

void lambda() {
	std::vector<int> v={1,4,8};
	std::for_each(std::begin(v), std::end(v),
		[](const auto& i){std::cout<<i<<" ";});
}

} // end of namespace


int main() {
	return serialize::test("data.json", "output.json");
}
