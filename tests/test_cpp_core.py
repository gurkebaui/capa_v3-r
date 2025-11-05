# tests/test_cpp_core.py (KORRIGIERT)

import sys
import os
import msgpack

# Add root directory to path to allow importing capa_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import capa_core # type: ignore
except ImportError:
    print("Error: Could not import 'capa_core'.")
    print("Please make sure you have run the build.bat script and copied the .pyd file to the root directory.")
    sys.exit(1)

def test_core_functionality():
    print("--- Testing C++ Core Functionality ---")
    
    core = capa_core.CPPCore()
    print("Successfully instantiated CPPCore.")

    id1 = core.add_node("concept_A")
    id2 = core.add_node("concept_B")
    core.add_edge(id1, id2, 0.75)
    print(f"Added nodes (ID: {id1}, {id2}) and an edge between them.")
    
    core.update_node_salience(id1, 1.5)
    print(f"Updated salience for node {id1}.")

    print("Serializing graph...")
    serialized_bytes = core.serialize_graph()
    assert isinstance(serialized_bytes, bytes)
    print(f"Serialization successful. Received {len(serialized_bytes)} bytes.")

    # In Python 3, msgpack.unpackb is preferred for a single object
    unpacked_data = msgpack.unpackb(serialized_bytes)
    
    nodes, edges = unpacked_data
    
    print("Deserialization successful. Validating data...")
    assert len(nodes) == 2
    assert len(edges) == 1
    
    # --- KORREKTUR HIER ---
    # Wir greifen per Index auf das Tuple zu: (id, label, salience) -> (0, 1, 2)
    node_a = nodes[0] if nodes[0][0] == id1 else nodes[1]
    edge = edges[0]

    assert node_a[1] == 'concept_A' # Index 1 ist 'label'
    assert node_a[2] == 1.5         # Index 2 ist 'salience'
    assert edge[0] == id1 and edge[1] == id2 # from_id, to_id
    
    print("--- C++ Core Test Passed! ---")

if __name__ == "__main__":
    test_core_functionality()