# agent.py (VOLLSTÄNDIG & FINAL KORRIGIERT)

import logging
from cognitive.layers import ThinkingLayer3, ThinkingLayer4, ThinkingLayer5
from affective.engine import AffectiveEngine
from processing.layer1 import ContextEnricher
from memory.man import MemoryAccessNetwork
from memory.subsystem import MemorySubsystem
from affective.logger import ActionLogger
try:
    from capa_core import CPPCore
except ImportError:
    CPPCore = None

def _parse_and_validate_llm_response(response: dict) -> tuple[str, str, int]:
    """
    Robustly parses LLM responses, handling key variations and normalizing confidence.
    """
    internal_monologue = response.get('internal_monologue') or response.get('monologue', '')
    external_response = response.get('external_response', 'N/A')
    
    confidence_val = response.get('confidence_score') or response.get('confidence', 0)
    
    # --- FINALE KORREKTUR: Mache die Typ-Konvertierung absolut sicher ---
    try:
        # Versuche, den Wert in eine Fließkommazahl umzuwandeln (fängt "40" und 40.0 ab)
        confidence_float = float(confidence_val)
    except (ValueError, TypeError):
        # Wenn die Konvertierung fehlschlägt, setze die Konfidenz auf 0
        confidence_float = 0.0

    if 0 < confidence_float <= 1:
        confidence = int(confidence_float * 100)
    else:
        confidence = int(confidence_float)
        
    return internal_monologue, external_response, confidence

# --- Der Rest der Datei ist bereits korrekt und bleibt unverändert ---

class Agent:
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork, context_enricher: ContextEnricher, memory_subsystem: MemorySubsystem):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cpp_core = cpp_core
        self.man = man
        self.context_enricher = context_enricher
        self.memory_subsystem = memory_subsystem
        self.affective_engine = AffectiveEngine()
        self.action_logger = ActionLogger()
        self.layers = {
            3: ThinkingLayer3(cpp_core, man),
            4: ThinkingLayer4(cpp_core, man),
            5: ThinkingLayer5(cpp_core, man)
        }
        self.logger.info("Agent initialized successfully.")

    def _run_cognitive_process(self, initial_graph_snapshot: bytes, emotion_context: str) -> dict:
        current_graph = initial_graph_snapshot
        current_layer_index = 3
        recursion_counter = 0
        max_recursions = 20
        active_plans = self.man.find_active_plans()
        internal_emotion_text = self.affective_engine.get_state_as_text()

        while True:
            active_layer = self.layers[current_layer_index]
            self.logger.info(f"--- Passing control to Layer {current_layer_index} ({active_layer.model_name}) ---")
            
            # emotion_context wird nun an die think-Methode übergeben
            result = active_layer.think(current_graph, active_plans, emotion_context, internal_emotion_text)

            # Loggt Aktionen für feedback-Zuordnung (spionage)
            self.action_logger.log_action(current_layer_index, active_layer.model_name, result)
            
            if result.get("plan") and result.get("plan_type"):
                plan_type = result["plan_type"]
                plan_steps = result["plan"]
                self.logger.info(f"Layer {current_layer_index} created a {plan_type} plan.")
                if plan_type == "long_term":
                    plan_text = "Plan: " + " | ".join(plan_steps)
                    self.memory_subsystem.add_experience(text=plan_text, metadata={"type": "future_plan", "status": "active"})
                    self.logger.info("Long-term plan STORED in LTM.")
                elif plan_type == "short_term":
                    for step in plan_steps: self.cpp_core.add_node(f"PLAN_STEP: {step}")
                    self.logger.info("Short-term plan noted in STM.")
                return result

            internal_monologue, external_response, confidence = _parse_and_validate_llm_response(result)

            if confidence > 90:
                self.logger.info(f"Layer {current_layer_index} has high confidence ({confidence}%). Finalizing.")
                self.affective_engine.apply_reward(0.1)
                return result
            elif confidence < 40:
                self.logger.warning(f"Layer {current_layer_index} has low confidence ({confidence}%).")
                if current_layer_index < 5:
                    self.logger.info(f"Escalating to Layer {current_layer_index + 1}.")
                    self.cpp_core.add_node(f"L{current_layer_index}_THOUGHT: {internal_monologue}")
                    current_graph = self.cpp_core.serialize_graph()
                    current_layer_index += 1
                    self.affective_engine.apply_punishment(0.1)
                    continue
                else:
                    self.logger.error("Reached highest layer (5) with low confidence.")
                    self.cpp_core.add_node(f"L{current_layer_index}_THOUGHT: {internal_monologue}")
                    current_graph = self.cpp_core.serialize_graph()
                    current_layer_index = 3
                    self.affective_engine.apply_punishment(0.1)
                    continue
            else:
                self.logger.info(f"Layer {current_layer_index} has medium confidence ({confidence}%). Initiating recursion.")
                if recursion_counter >= max_recursions:
                    self.logger.warning("Max recursion depth reached. Finalizing.")
                    return result
                recursion_counter += 1
                self.logger.info(f"Recursion cycle {recursion_counter}/{max_recursions}.")
                self.cpp_core.add_node(f"RECURSIVE_THOUGHT: {internal_monologue}")
                current_graph = self.cpp_core.serialize_graph()
                current_layer_index = 3
                continue
    
    def process_input(self, text: str) -> dict:
        self.logger.info(f"--- New Input Received: '{text}' ---")
        enriched_packet = self.context_enricher.process(text)
        label = enriched_packet['original_input']
        emotion = enriched_packet['emotion_context']
        
        if self.cpp_core.should_store_in_stm(label, {"emotion": emotion}):
            self.logger.info("STM Gatekeeper approved storage.")
            self.cpp_core.add_node(label, salience=1.0)
            initial_graph = self.cpp_core.serialize_graph()
            # Der Aufruf hier war bereits korrekt
            return self._run_cognitive_process(initial_graph, emotion)
        else:
            self.logger.info("STM Gatekeeper denied storage.")
            return {"external_response": "I have noted your input, but did not deem it necessary for deep thought."}
        
    def initiate_training(self):
        """Initiates the autonomous training cycle (Bridge Mode)."""
        self.logger.info("--- AUTONOMOUS TRAINING CYCLE INITIATED (BRIDGE MODE) ---")
        self.layers[5].create_training_data_for_layer1()
        self.logger.info("--- TRAINING CYCLE COMPLETED (BRIDGE MODE) ---")


    def reward(self, value: float):
        """Applies an external reward to the agent."""
        self.affective_engine.apply_reward(value)
        self.action_logger.assign_feedback(value, "reward")

    def punish(self, value: float):
        """Applies an external punishment to the agent."""
        self.affective_engine.apply_punishment(value)
        self.action_logger.assign_feedback(value, "punishment")

    def get_status(self) -> str:
        """Returns the current internal status of the agent."""
        return f"Internal Emotion: {self.affective_engine.get_state_as_text()}"