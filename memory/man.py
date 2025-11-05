# memory/man.py

import logging
from memory.subsystem import MemorySubsystem
from chromadb.api.types import QueryResult


class MemoryAccessNetwork:
    """
    The Memory Access Network (MAN) acts as an intelligent interface 
    to the long-term memory (LTM).
    """
    def __init__(self, memory_subsystem: MemorySubsystem):
        """
        Initializes the MAN with a reference to the core memory subsystem.
        """
        self.memory_subsystem = memory_subsystem
        logging.info("Memory Access Network (MAN) initialized.")

    def request(self, query_text: str, search_type: str = 'quick') -> dict:
        """
        Processes a memory request.

        Args:
            query_text: The natural language query.
            search_type: 'quick' for a direct vector search, 
                         'slow' for a (future) more complex analysis.

        Returns:
            A dictionary containing the query results from ChromaDB.
        """
        if search_type == 'slow':
            # Platzhalter-Logik für Slow Search
            logging.warning(
                "MAN: 'Slow Search' requested. "
                "BRIDGE-MODE: Executing 'Quick Search' logic as a placeholder."
            )
            # Führt die gleiche Logik wie Quick Search aus
            return self.memory_subsystem.query_memories(query_text)
        
        # Logik für Quick Search
        logging.info(f"MAN: Executing Quick Search for: '{query_text}'")
        return self.memory_subsystem.query_memories(query_text)
    
    def find_active_plans(self) -> list[str]:
        """
        Specifically queries the LTM for documents flagged as an active future plan.
        """
        logging.info("MAN: Searching for active future plans in LTM...")
        try:
            # --- KORREKTUR: Korrekte 'where' Syntax mit $and Operator ---
            results = self.memory_subsystem.collection.get(
                where={
                    "$and": [
                        {"type": "future_plan"},
                        {"status": "active"}
                    ]
                }
            )
            plans = results.get('documents', [])
            if plans:
                logging.info(f"Found {len(plans)} active plan(s): {plans}")
            else:
                logging.info("No active plans found.")
            return plans
        except Exception as e:
            logging.error(f"Error while querying for plans in LTM: {e}")
            return []