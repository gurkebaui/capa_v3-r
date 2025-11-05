// cpp_core/src/short_term_memory.h

#ifndef SHORT_TERM_MEMORY_H
#define SHORT_TERM_MEMORY_H

#include <string>
#include <vector>
#include <unordered_map>
#include <msgpack.hpp>

struct Node {
    int id;
    std::string label;
    float salience;

    MSGPACK_DEFINE(id, label, salience);
};

struct Edge {
    int from_id;
    int to_id;
    float weight;

    MSGPACK_DEFINE(from_id, to_id, weight);
};

class ShortTermMemory {
public:
    ShortTermMemory();
    int add_node(const std::string& label);
    void add_edge(int from_id, int to_id, float weight);
    void update_node_salience(int id, float salience);
    
    // Serialisiert den Graphen zu einem Byte-Vektor
    std::vector<char> serialize_graph();

    // Schreibt einen JSON-String in die Journal-Datei (Aufgabe 2)
    void log_to_ltm(const std::string& json_data);

private:
    std::unordered_map<int, Node> nodes;
    std::vector<Edge> edges;
    int next_node_id;
};

#endif // SHORT_TERM_MEMORY_H