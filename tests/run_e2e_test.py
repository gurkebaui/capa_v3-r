# tests/run_e2e_test.py (FINAL VERSION)

import sys
import os
import time
import json
import multiprocessing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We import the canonical path that the listener will use
from memory.listener import run_ltm_listener, DEFAULT_JOURNAL_PATH
from memory.subsystem import MemorySubsystem
try:
    import capa_core # type: ignore
except ImportError:
    print("Error: Could not import 'capa_core'. Build it first.")
    sys.exit(1)


def e2e_test():
    print("--- Starting End-to-End Test ---")
    
    # Ensure the journal file and its directory exist before starting
    os.makedirs(os.path.dirname(DEFAULT_JOURNAL_PATH), exist_ok=True)
    if os.path.exists(DEFAULT_JOURNAL_PATH):
        os.remove(DEFAULT_JOURNAL_PATH) # Clean slate for the test

    listener_process = multiprocessing.Process(target=run_ltm_listener, daemon=True)
    listener_process.start()
    print("LTM listener started in background...")
    time.sleep(15) # Give listener time to initialize fully

    try:
        core = capa_core.CPPCore()
        
        experience_text = "The quick brown fox jumps over the lazy dog."
        experience_metadata = {"source": "e2e_test", "timestamp": time.time()}
        
        log_entry = {"text": experience_text, "metadata": experience_metadata}
        json_string = json.dumps(log_entry)
        
        # MODIFIED: Pass the absolute path to the C++ function
        print(f"Logging to LTM via C++ core into file: {DEFAULT_JOURNAL_PATH}")
        core.log_to_ltm(DEFAULT_JOURNAL_PATH, json_string)

        print("Waiting for listener to process...")
        time.sleep(15)

        print("Querying LTM to verify...")
        memory_checker = MemorySubsystem()
        query_result = memory_checker.query_memories(query_text="A quick brown fox", n_results=1)
        
        assert query_result is not None, "Query returned None"
        documents = query_result.get('documents') 
        assert documents is not None and len(documents) > 0, "Query result has no 'documents'"
        first_doc_list = documents[0]
        assert len(first_doc_list) > 0, "No documents found for the query"
        retrieved_doc = first_doc_list[0]
        
        print(f"Retrieved document: {retrieved_doc}")
        assert retrieved_doc == experience_text
        
        print("\n--- E2E TEST PASSED! ---")

    finally:
        print("Terminating listener process...")
        listener_process.terminate()
        listener_process.join(timeout=2)
        print("Listener process stopped.")

if __name__ == "__main__":
    e2e_test()