# tests/test_sprint2.py

import sys
import os
import time
import json
import logging

# Pfad-Setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Logging-Konfiguration für bessere Test-Ausgaben
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Modul-Importe
from memory.subsystem import MemorySubsystem
from memory.man import MemoryAccessNetwork
from memory.listener import DEFAULT_JOURNAL_PATH, run_ltm_listener
try:
    import capa_core # type: ignore
except ImportError:
    print("FATAL: Could not import 'capa_core'. Please build it first.")
    sys.exit(1)


def run_sprint2_tests():
    """
    Executes the integration tests for Sprint 2 features.
    """
    print("\n--- Running Sprint 2 Integration Tests ---")

    # --- SETUP: LTM mit Daten befüllen ---
    print("\n--- SETUP: Populating LTM with test memories ---")
    
    # Sicherstellen, dass die Journal-Datei für den Test leer ist
    if os.path.exists(DEFAULT_JOURNAL_PATH):
        os.remove(DEFAULT_JOURNAL_PATH)
    
    core = capa_core.CPPCore()
    
    memories_to_add = [
        {"text": "Die Sonne ist ein Stern im Zentrum unseres Sonnensystems.", "metadata": {"topic": "astronomy"}},
        {"text": "Photosynthese ist der Prozess, den Pflanzen zur Energiegewinnung nutzen.", "metadata": {"topic": "biology"}},
    ]
    
    for mem in memories_to_add:
        core.log_to_ltm(DEFAULT_JOURNAL_PATH, json.dumps(mem))
        print(f"Logged to LTM journal: '{mem['text']}'")

    print("Waiting for listener to process memories...")
    # Wir starten den Listener nicht, da wir das MemorySubsystem direkt instanziieren können.
    # Für einen echten Test würde man den Listener im Hintergrund laufen lassen.
    # Hier simulieren wir den Effekt, indem wir direkt die DB befüllen.
    # HINWEIS: Für einen sauberen Unit-Test befüllen wir die DB direkt.
    memory_system = MemorySubsystem()
    for mem in memories_to_add:
        memory_system.add_experience(mem['text'], mem['metadata'])


    # --- TEST A: Memory Access Network (MAN) ---
    print("\n--- TEST A: Validating MemoryAccessNetwork (MAN) ---")
    man = MemoryAccessNetwork(memory_system)

    # 1. Test Quick Search
    query_quick = "Was ist die Sonne?"
    results_quick = man.request(query_quick, search_type='quick')
    
    assert results_quick is not None, "MAN Quick Search returned None"
    assert "astronomy" in str(results_quick['metadatas']), "MAN Quick Search failed to retrieve correct memory"
    print("MAN Quick Search PASSED.")

    # 2. Test Slow Search (Platzhalter)
    query_slow = "Erzähl mir von Pflanzen."
    results_slow = man.request(query_slow, search_type='slow')

    assert results_slow is not None, "MAN Slow Search returned None"
    assert "biology" in str(results_slow['metadatas']), "MAN Slow Search failed to retrieve correct memory"
    print("MAN Slow Search (Placeholder) PASSED.")
    print("--- MAN Tests successful ---\n")


    # --- TEST B: STM Gatekeeper ---
    print("--- TEST B: Validating STM Gatekeeper (C++ Core) ---")
    
    # 1. Relevante Daten
    relevant_label = "Ein wichtiger Gedanke"
    relevant_metadata = {"source": "test"}
    should_store_relevant = core.should_store_in_stm(relevant_label, relevant_metadata)
    assert should_store_relevant is True, "Gatekeeper blocked relevant data."
    print("STM Gatekeeper correctly identified relevant data. PASSED.")

    # 2. Irrelevante Daten (Keyword im Label)
    irrelevant_label = "Dies ist nur unwichtiges Rauschen"
    irrelevant_metadata = {"source": "test"}
    should_store_irrelevant_label = core.should_store_in_stm(irrelevant_label, irrelevant_metadata)
    assert should_store_irrelevant_label is False, "Gatekeeper allowed irrelevant data (label)."
    print("STM Gatekeeper correctly blocked irrelevant data (label). PASSED.")
    
    # 3. Irrelevante Daten (Keyword in Metadaten)
    other_label = "Ein normaler Gedanke"
    irrelevant_metadata_val = {"details": "dieser test ist unwichtig"}
    should_store_irrelevant_meta = core.should_store_in_stm(other_label, irrelevant_metadata_val)
    assert should_store_irrelevant_meta is False, "Gatekeeper allowed irrelevant data (metadata)."
    print("STM Gatekeeper correctly blocked irrelevant data (metadata). PASSED.")
    print("--- STM Gatekeeper Tests successful ---")
    
    print("\n--- Sprint 2 Integration Tests Passed Successfully! ---\n")


if __name__ == "__main__":
    run_sprint2_tests()