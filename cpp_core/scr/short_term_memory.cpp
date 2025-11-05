// cpp_core/src/short_term_memory.cpp

#include "short_term_memory.h"
#include <fstream>
#include <stdexcept>
#include <sstream>

ShortTermMemory::ShortTermMemory() : next_node_id(0) {}

int ShortTermMemory::add_node(const std::string& label) {
    int id = next_node_id++;
    nodes[id] = {id, label, 1.0f}; // Default salience
    return id;
}

void ShortTermMemory::add_edge(int from_id, int to_id, float weight) {
    if (nodes.find(from_id) == nodes.end() || nodes.find(to_id) == nodes.end()) {
        throw std::runtime_error("Node ID not found.");
    }
    edges.push_back({from_id, to_id, weight});
}

void ShortTermMemory::update_node_salience(int id, float salience) {
    if (nodes.find(id) == nodes.end()) {
        throw std::runtime_error("Node ID not found.");
    }
    nodes[id].salience = salience;
}

std::vector<char> ShortTermMemory::serialize_graph() {
    std::vector<Node> node_list;
    for (const auto& pair : nodes) {
        node_list.push_back(pair.second);
    }

    std::tuple<std::vector<Node>, std::vector<Edge>> graph_data = {node_list, edges};
    
    std::stringstream buffer;
    msgpack::pack(buffer, graph_data);

    const std::string& str = buffer.str();
    return std::vector<char>(str.begin(), str.end());
}

void ShortTermMemory::log_to_ltm(const std::string& json_data) {
    // Open file in append mode. std::ios::out is default for ofstream.
    std::ofstream journal_file("../journals/ltm_journal.wal", std::ios::app);
    if (!journal_file.is_open()) {
        throw std::runtime_error("Could not open LTM journal file.");
    }
    journal_file << json_data << std::endl; // Append data and a newline
}