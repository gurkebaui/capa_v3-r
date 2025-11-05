// cpp_core/src/main.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For automatic type conversion
#include "short_term_memory.h"

namespace py = pybind11;

PYBIND11_MODULE(capa_core, m) {
    m.doc() = "High-performance core module for CAPA v3-R";

    py::class_<ShortTermMemory>(m, "CPPCore")
        .def(py::init<>())
        .def("add_node", &ShortTermMemory::add_node, py::arg("label"), "Adds a node to the graph and returns its ID.")
        .def("add_edge", &ShortTermMemory::add_edge, py::arg("from_id"), py::arg("to_id"), py::arg("weight"), "Adds a directed edge between two nodes.")
        .def("update_node_salience", &ShortTermMemory::update_node_salience, py::arg("id"), py::arg("salience"), "Updates the salience of a specific node.")
        .def("serialize_graph", [](ShortTermMemory &self) {
            std::vector<char> result = self.serialize_graph();
            // Return as Python bytes
            return py::bytes(result.data(), result.size());
        }, "Serializes the entire graph using msgpack and returns it as bytes.")
        .def("log_to_ltm", &ShortTermMemory::log_to_ltm, py::arg("journal_path"), py::arg("data"), "Appends a JSON string to the specified journal file for asynchronous processing.")
        .def("should_store_in_stm", &ShortTermMemory::should_store_in_stm, 
             py::arg("label"), py::arg("metadata"),
             "Checks if a node should be stored in STM based on a simple keyword filter.");
}