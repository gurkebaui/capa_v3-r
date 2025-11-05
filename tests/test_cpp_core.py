# tests/test_cpp_core.py

import sys
import os
import msgpack

# Add root directory to path to allow importing capa_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import capa_core
except ImportError:
    print("Error: Could not import 'capa_core'.")
    print("Please make sure you have run the build.bat script successfully.")
    sys.exit(1)

def test_core_functionality():
    print("--- Testing C++ Core Functionality ---")
    
    # 1. Instantiate the core
    core = capa_core.CPPCore()
    print("Successfully instantiated CPPCore.")

    # 2. Add nodes and edges
    id1 = core.add_node("concept_A")
    id2 = core.add_node("concept_B")
    core.add_edge(id1, id2, 0.75)
    print(f"Added nodes (ID: {id1}, {id2}) and an edge between them.")
    
    # 3. Update salience
    core.update_node_salience(id1, 1.5)
    print(f"Updated salience for node {id1}.")

    # 4. Serialize and deserialize
    print("Serializing graph...")
    serialized_bytes = core.serialize_graph()
    assert isinstance(serialized_bytes, bytes)
    print(f"Serialization successful. Received {len(serialized_bytes)} bytes.")

    unpacker = msgpack.Unpacker(raw=False)
    unpacker.feed(serialized_bytes)
    unpacked_data = unpacker.unpack()
    
    nodes, edges = unpacked_data
    
    print("Deserialization successful. Validating data...")
    assert len(nodes) == 2
    assert len(edges) == 1
    assert nodes[0]['label'] == 'concept_A'
    assert nodes[0]['salience'] == 1.5
    assert edges[0]['from_id'] == id1 and edges[0]['to_id'] == id2
    
    print("--- C++ Core Test Passed! ---")

if __name__ == "__main__":
    test_core_functionality()