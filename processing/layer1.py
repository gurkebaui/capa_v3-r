# processing/layer1.py (KOMPLETT ÜBERARBEITET)

import logging
import ollama
import re

class ContextEnricher:
    def __init__(self, man):
        self.man = man
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = ollama.Client()
        self.model_name = "granite4:3b"
        self.logger.info(f"Context Enricher (Layer 1) initialized with LLM: {self.model_name}.")

    def _extract_query_from_response(self, text: str) -> str:
        """Extracts the core search query from a potentially chatty LLM response."""
        # Versucht, Text in ```-Blöcken zu finden
        code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks.strip()
        
        # Fallback: Nimmt die letzte nicht-leere Zeile
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            return lines[-1]
        
        return text # Absoluter Fallback

    def _generate_emotional_query(self, input_text: str) -> str:
        """Uses an LLM to transform user input into an emotion-focused search query."""
        prompt = f"""
        Your job is to transform a user's statement into a search query for finding similar past experiences and emotions (your emotions).
        User statement: "{input_text}"
        Your output MUST be only the search query string, nothing else.

        Example 1:
        User statement: "I finally solved that difficult bug!"
        Output:
        past experiences of success and overcoming challenges (you are happy because the user is happy)

        Example 2:
        User statement: "I don't understand how this works."
        Output:
        memories related to confusion or learning something new (again you feel stressed because the user is stressed)
        """
        self.logger.info("Generating emotion-focused query with LLM...")
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            raw_response = response['message']['content']
            # --- KORREKTUR HIER ---
            query = self._extract_query_from_response(raw_response)
            self.logger.info(f"Generated emotional query: '{query}'")
            return query
        except Exception as e:
            self.logger.error(f"Failed to generate emotional query: {e}")
            return input_text # Fallback auf den Originaltext

    def process(self, input_text: str) -> dict:
        """
        Processes raw text to create an "enriched data packet" with emotional context.
        """
        self.logger.info(f"Processing input: '{input_text}'")

        # 1. Intelligente Query an das MAN formulieren
        emotional_query = self._generate_emotional_query(input_text)
        
        # 2. LTM nach emotional relevanten Erinnerungen durchsuchen
        self.logger.info(f"Querying MAN with emotional query: '{emotional_query}'")
        context_result = self.man.request(emotional_query, search_type='quick')
        
        # 3. "Gefühlsvektor" extrahieren (simuliert)
        emotion_context = "neutral" # Default
        if context_result and context_result.get('metadatas') and context_result['metadatas'][0]:
            metadata = context_result['metadatas'][0][0]
            if "emotion" in metadata:
                emotion_context = metadata["emotion"]
                self.logger.info(f"Extracted emotional context from memory: '{emotion_context}'")

        # 4. Angereichertes Datenpaket erstellen
        enriched_packet = {
            "original_input": input_text,
            "emotion_context": emotion_context
        }
        self.logger.info(f"Created enriched data packet: {enriched_packet}")
        return enriched_packet