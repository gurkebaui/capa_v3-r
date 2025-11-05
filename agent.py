# agent.py

import logging
from cognitive.layers import ThinkingLayer3, ThinkingLayer4, ThinkingLayer5
from processing.layer1 import ContextEnricher
from memory.man import MemoryAccessNetwork
try:
    from capa_core import CPPCore # type: ignore
except ImportError:
    CPPCore = None

class Agent:
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork, context_enricher: ContextEnricher):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cpp_core = cpp_core
        self.man = man
        self.context_enricher = context_enricher

        self.logger.info("Initializing Cognitive Layers for Agent...")
        self.layer3 = ThinkingLayer3(cpp_core=self.cpp_core)
        self.layer4 = ThinkingLayer4(cpp_core=self.cpp_core, man=self.man)
        self.layer5 = ThinkingLayer5(cpp_core=self.cpp_core, man=self.man)
        self.layers = {3: self.layer3, 4: self.layer4, 5: self.layer5}
        self.logger.info("Agent initialized successfully.")

    def _run_cognitive_process(self, initial_graph_snapshot: bytes) -> dict:
        """
        Manages the dynamic thinking process, including escalation and recursion.
        """
        current_graph = initial_graph_snapshot
        current_layer_index = 3
        recursion_counter = 0
        max_recursions = 30 # Limitiere die Rekursion

        while True:
            active_layer = self.layers[current_layer_index]
            self.logger.info(f"--- Passing control to Layer {current_layer_index} ({active_layer.model_name}) ---")
            
            result = active_layer.think(current_graph)
            confidence = result.get('confidence_score', 0)
            internal_monologue = result.get('internal_monologue', '')

            # 1. Fall: Hohe Konfidenz -> Prozess beenden
            if confidence > 90:
                self.logger.info(f"Layer {current_layer_index} has high confidence ({confidence}%). Finalizing thought process.")
                return result

            # 2. Fall: Niedrige Konfidenz -> Eskalation
            elif confidence < 40:
                self.logger.warning(f"Layer {current_layer_index} has low confidence ({confidence}%).")
                if current_layer_index < 5:
                    self.logger.info(f"Escalating from Layer {current_layer_index} to Layer {current_layer_index + 1}.")
                    # Füge den Monolog als Kontext für den nächsten Layer hinzu
                    self.cpp_core.add_node(f"L{current_layer_index}_THOUGHT: {internal_monologue}")
                    current_graph = self.cpp_core.serialize_graph()
                    current_layer_index += 1
                    continue # Nächste Schleifeniteration mit dem höheren Layer
                else:
                    self.logger.warning("Reached highest layer (5) with low confidence. Returning best effort.")
                    return result
            
            # 3. Fall: Mittlere Konfidenz -> Rekursive Denk-Schleife
            else: # 40 <= confidence <= 90
                self.logger.info(f"Layer {current_layer_index} has medium confidence ({confidence}%). Initiating recursive thought.")
                if recursion_counter >= max_recursions:
                    self.logger.warning("Max recursion depth reached. Finalizing thought process.")
                    return result
                
                recursion_counter += 1
                self.logger.info(f"Recursion cycle {recursion_counter}/{max_recursions}.")
                # Füge den Monolog als rekursiven Gedanken hinzu und starte bei Layer 3 neu
                self.cpp_core.add_node(f"RECURSIVE_THOUGHT: {internal_monologue}")
                current_graph = self.cpp_core.serialize_graph()
                current_layer_index = 3 # Reset zur Reflex-Ebene
                continue
    
    def process_input(self, text: str) -> dict:
        """
        Handles the full end-to-end process for a given text input.
        """
        self.logger.info(f"--- New Input Received: '{text}' ---")
        
        # 1. Kontext anreichern
        enriched_packet = self.context_enricher.process(text)
        
        # 2. Im STM speichern (wenn relevant)
        label = enriched_packet['original_input']
        metadata = {"context": enriched_packet['context_memory']}
        
        if self.cpp_core.should_store_in_stm(label, metadata):
            self.logger.info("STM Gatekeeper approved storage.")
            id1 = self.cpp_core.add_node(label)
            if enriched_packet['context_memory']:
                id2 = self.cpp_core.add_node(enriched_packet['context_memory'])
                self.cpp_core.add_edge(id1, id2, 0.8)
            
            # 3. Kognitiven Prozess starten
            initial_graph = self.cpp_core.serialize_graph()
            final_result = self._run_cognitive_process(initial_graph)
            return final_result
        else:
            self.logger.info("STM Gatekeeper denied storage. Discarding input.")
            return {
                "internal_monologue": "Input was deemed irrelevant and not processed further.",
                "external_response": "I have noted your input, but did not deem it necessary for deep thought.",
                "confidence_score": 100
            }