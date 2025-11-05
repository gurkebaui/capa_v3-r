# tests/run_e2e_test.py

import sys
import os
import time
import json
import multiprocessing

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Must be imported after path setup
from memory.listener import run_ltm_listener
from memory.subsystem import MemorySubsystem
try:
    import capa_core
except ImportError:
    print("Error: Could not import 'capa_core'.")
    print("Please make sure you have run the build.bat script successfully.")
    sys.exit(1)


def e2e_test():
    print("--- Starting End-to-End Test ---")
    
    # 1. Start the LTM listener in a separate process
    print("Starting LTM listener in background...")
    listener_process = multiprocessing.Process(target=run_ltm_listener)
    listener_process.start()
    # Give it a moment to initialize
    time.sleep(5)

    try:
        # 2. Instantiate the C++ core in the main process
        print("Instantiating C++ core...")
        core = capa_core.CPPCore()
        
        # 3. Use the C++ core to log a new memory to the journal
        experience_text = "The quick brown fox jumps over the lazy dog."
        experience_metadata = {"source": "e2e_test", "timestamp": time.time()}
        
        log_entry = {
            "text": experience_text,
            "metadata": experience_metadata
        }
        json_string = json.dumps(log_entry)
        
        print(f"Logging to LTM via C++ core: {json_string}")
        core.log_to_ltm(json_string)

        # 4. Wait for the listener to process the entry
        print("Waiting for listener to process the journal entry...")
        time.sleep(5) 

        # 5. Validate the result by querying ChromaDB directly
        print("Querying LTM to verify the memory was stored...")
        memory_checker = MemorySubsystem()
        query_result = memory_checker.query_memories(query_text="A fast animal", n_results=1)
        
        assert query_result is not None
        assert len(query_result['documents'][0]) > 0
        
        retrieved_doc = query_result['documents'][0][0]
        retrieved_meta = query_result['metadatas'][0][0]
        
        print(f"Retrieved document: {retrieved_doc}")
        print(f"Retrieved metadata: {retrieved_meta}")
        
        assert retrieved_doc == experience_text
        assert retrieved_meta['source'] == "e2e_test"
        
        print("\n--- E2E TEST PASSED! ---")
        print("The memory was successfully written via C++ and processed by the Python listener.")

    finally:
        # 6. Clean up: terminate the listener process
        print("Terminating listener process...")
        listener_process.terminate()
        listener_process.join()
        print("Listener process stopped.")

if __name__ == "__main__":
    e2e_test()