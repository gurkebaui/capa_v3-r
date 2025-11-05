# memory/man.py

import logging
from memory.subsystem import MemorySubsystem

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