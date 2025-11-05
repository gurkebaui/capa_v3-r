// cpp_core/src/short_term_memory.cpp (FINAL KORRIGIERT)

#include "short_term_memory.h"
#include <fstream>
#include <stdexcept>
#include <sstream>

ShortTermMemory::ShortTermMemory() : next_node_id(0) {}

int ShortTermMemory::add_node(const std::string& label) {
    int id = next_node_id++;
    nodes[id] = {id, label, 1.0f};
    return id;
}

bool ShortTermMemory::should_store_in_stm(const std::string& label, const pybind11::dict& metadata) {
    const std::vector<std::string> irrelevant_keywords = {"rauschen", "unwichtig", "irrelevant"};

    // Prüfe das Label
    for (const auto& keyword : irrelevant_keywords) {
        if (label.find(keyword) != std::string::npos) {
            return false; // Keyword im Label gefunden
        }
    }

    // Prüfe die Metadaten-Werte
    for (auto item : metadata) {
        // Wir prüfen nur Werte, die Strings sind
        if (pybind11::isinstance<pybind11::str>(item.second)) {
            std::string value = item.second.cast<std::string>();
            for (const auto& keyword : irrelevant_keywords) {
                if (value.find(keyword) != std::string::npos) {
                    return false; // Keyword in einem Metadaten-Wert gefunden
                }
            }
        }
    }

    return true; // Keine irrelevanten Keywords gefunden
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

void ShortTermMemory::log_to_ltm(const std::string& journal_path, const std::string& json_data) {
    // Open the exact path provided by the Python caller
    {
        std::ofstream journal_file(journal_path, std::ios::app);
        if (!journal_file.is_open()) {
            throw std::runtime_error("C++ Core: Could not open journal file at path: " + journal_path);
        }
    
    journal_file << json_data << std::endl; // std::endl flushes, but we'll be more explicit.
    
    // --- DIE KORREKTUR ---
    // Zwingt den Stream, seinen Puffer sofort auf die Festplatte zu schreiben.
    // Das ist der entscheidende Schritt, damit watchdog die Änderung bemerkt.
    journal_file.flush();
    }
    
    // Die Datei wird automatisch geschlossen, wenn journal_file am Ende der Funktion
    // zerstört wird (RAII-Prinzip).
}