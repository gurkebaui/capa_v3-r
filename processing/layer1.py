# processing/layer1.py

import logging
from memory.man import MemoryAccessNetwork

class ContextEnricher:
    """
    Layer 1: The intelligent pre-filter.
    Its job is to take raw input and enrich it with relevant context from long-term memory.
    """
    def __init__(self, man: MemoryAccessNetwork):
        self.man = man
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Context Enricher (Layer 1) initialized.")

    def process(self, input_text: str) -> dict:
        """
        Processes the raw input text to create an "enriched data packet".

        Args:
            input_text: The raw text from Layer 2.

        Returns:
            A dictionary containing the original input and retrieved context.
        """
        self.logger.info(f"Processing input: '{input_text}'")

        # 1. Summarize (Bridge Mode)
        # In the future, a small LLM would summarize the input.
        # For now, we just use the original text.
        summary = input_text
        self.logger.info("Summarization (Bridge Mode): Using original text as summary.")

        # 2. Contextualize by querying the MAN
        self.logger.info("Querying MAN for relevant context...")
        context_result = self.man.request(summary, search_type='quick')
        
        # Extract the most relevant memory, if any
        found_memory = ""
        if context_result and context_result.get('documents') and context_result['documents'][0]:
            found_memory = context_result['documents'][0][0]
            self.logger.info(f"MAN returned context: '{found_memory}'")
        else:
            self.logger.warning("MAN returned no relevant context.")

        # 3. Create the enriched data packet
        enriched_packet = {
            "original_input": input_text,
            "context_memory": found_memory
        }
        self.logger.info(f"Created enriched data packet: {enriched_packet}")

        return enriched_packet