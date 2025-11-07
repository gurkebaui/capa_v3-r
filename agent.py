# agent.py (VOLLSTÄNDIG & FINAL KORRIGIERT)

import json
import logging
import msgpack
from cognitive.layers import  ThinkingLayer3, ThinkingLayer4, ThinkingLayer5
from affective.engine import AffectiveEngine
from processing.layer1 import ContextEnricher
from memory.man import MemoryAccessNetwork
from memory.subsystem import MemorySubsystem
from affective.logger import ActionLogger
from memory.stm_manager import STMManager 
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
        self.stm_manager = STMManager(memory_subsystem)
        self.layers = {
            3: ThinkingLayer3(cpp_core, man),
            4: ThinkingLayer4(cpp_core, man),
            5: ThinkingLayer5(cpp_core, man)
        }
        self.logger.info("Agent initialized successfully.")


    def process_input(self, text: str) -> dict:
        self.logger.info(f"--- New Input Received: '{text}' ---")
        enriched_packet = self.context_enricher.process(text)
        
        # --- ZURÜCK ZUR ALTEN LOGIK: Alles wird erstmal ins STM geschrieben ---
        label = enriched_packet['original_input']
        emotion = enriched_packet['emotion_context']
        
        self.logger.info("Storing input in STM.")
        self.cpp_core.add_node(label, salience=1.0)
        initial_graph = self.cpp_core.serialize_graph()
        
        max_recursions = 3
        return self._run_cognitive_process(initial_graph, emotion, max_recursions)
    

    def log_feedback_to_stm(self, feedback_type: str, value: float, reason: str):
        """Logs a feedback event directly into the STM to be archived later."""
        log_message = f"FEEDBACK: Received {feedback_type} of value {value}. Reason: '{reason}'"
        self.logger.info(f"Logging to STM: {log_message}")
        self.cpp_core.add_node(log_message, salience=0.8) # Feedback ist wichtig!


    def _run_cognitive_process(self, initial_graph_snapshot: bytes, emotion_context: str, max_recursions: int) -> dict:
        internal_emotion_text = self.affective_engine.get_state_as_text()
        active_plans = self.man.find_active_plans()

        # --- PHASE 1: REFLEX-SCHICHT (LAYER 3) ---
        self.logger.info("--- Passing control to Layer 3 (Reflex) ---")
        l3_result = self.layers[3].think(
            graph_snapshot=initial_graph_snapshot, 
            emotion_context=emotion_context, 
            internal_emotion_text=internal_emotion_text
        )
        _, _, l3_confidence = _parse_and_validate_llm_response(l3_result)
        
        if l3_confidence > 90:
            self.logger.info("Layer 3 has high confidence. Finalizing thought process.")
            return l3_result
        
        self.logger.warning(f"Layer 3 has low/medium confidence ({l3_confidence}%). Escalating to L4/L5 reasoning duo.")

        # --- PHASE 2: L4/L5 REASONING-SCHLEIFE ---
        recursion_counter = 0
        current_graph = initial_graph_snapshot # Starte mit dem sauberen Graphen
        last_l5_result = l3_result # Fallback-Antwort

        while recursion_counter < max_recursions:
            recursion_info = f"Reasoning cycle {recursion_counter + 1} of {max_recursions}."
            
            # 1. LAYER 4 (PLANNER)
            self.logger.info(f"--- Passing control to Layer 4 (Planner) | {recursion_info} ---")
            l4_result = self.layers[4].think(
                graph_snapshot=current_graph,
                active_plans=active_plans,
                emotion_context=emotion_context,
                internal_emotion_text=internal_emotion_text,
                recursion_info=recursion_info
            )
            l4_plan = l4_result.get("plan_for_layer5")

            if not l4_plan:
                self.logger.error("Layer 4 failed to produce a plan. Aborting reasoning loop.")
                return last_l5_result

            self.logger.info(f"Layer 4 produced a plan for Layer 5: {l4_plan}")

            # 2. LAYER 5 (EXECUTOR)
            # Füge den Plan und den L4-Monolog zum Graphen hinzu
            self.cpp_core.add_node(f"L4_PLAN: {l4_plan}")
            self.cpp_core.add_node(f"L4_THOUGHT: {l4_result.get('internal_monologue')}")
            current_graph = self.cpp_core.serialize_graph()

            self.logger.info(f"--- Passing control to Layer 5 (Executor) | {recursion_info} ---")
            l5_result = self.layers[5].think(
                graph_snapshot=current_graph,
                active_plans=active_plans,
                emotion_context=emotion_context,
                internal_emotion_text=internal_emotion_text,
                l4_plan=l4_plan,
                recursion_info=recursion_info
            )
            last_l5_result = l5_result # Speichere das Ergebnis für den Fall, dass die Schleife abbricht
            _, _, l5_confidence = _parse_and_validate_llm_response(l5_result)

            if l5_confidence > 90:
                self.logger.info("Layer 5 has high confidence. Finalizing reasoning loop.")
                return l5_result
            
            self.logger.warning(f"Layer 5 has low/medium confidence ({l5_confidence}%). Looping back to Layer 4 for a new plan.")
            self.cpp_core.add_node(f"L5_FAILED_ATTEMPT: {l5_result.get('internal_monologue')}")
            current_graph = self.cpp_core.serialize_graph()
            recursion_counter += 1
        
        self.logger.warning("Max recursion depth for L4/L5 loop reached. Returning best effort.")
        return last_l5_result
    
    
        
    def initiate_training(self):
        """Initiates the autonomous training cycle as per MAD Block 4."""
        self.logger.info("--- AUTONOMOUS TRAINING DEACTIVATED FOR NOW ---")

        """# 1. Initiierung (bereits geschehen)
        self.logger.info("Step 1: Initiation complete.")

        # 2. Selbst-Training von Layer 5 (Bridge Mode)
        self.logger.info("Step 2: Layer 5 Self-Training (Bridge Mode)...")
        # Hier würde L5 seine eigene Performance analysieren und ein neues Modell trainieren.
        # Wir simulieren dies, indem wir annehmen, dass es erfolgreich war.
        self.logger.info("...L5 Self-Training simulation complete.")
        
        # 3. Evaluation (Bridge Mode)
        self.logger.info("Step 3: Evaluation by L5_old and L4 (Bridge Mode)...")
        # Hier würden L5_old und L4 das neue L5_new-Modell testen.
        evaluation_passed = True # Wir nehmen Erfolg an.
        self.logger.info("...Evaluation simulation passed.")

        # 4. Promotion (Bridge Mode)
        if evaluation_passed:
            self.logger.info("Step 4: Promoting new model to active (Bridge Mode).")
        else:
            self.logger.error("Step 4: Promotion failed. Aborting training cycle.")
            return

        # 5. Trainingskaskade (Echte Implementierung!)
        self.logger.info("Step 5: Initiating Training Cascade (Teacher Mode)...")
        self._run_training_cascade()
        
        # 6. Abschluss
        self.logger.info("Step 6: Autonomous Training Cycle complete.") """

    def _run_training_cascade(self):
        self.logger.info("Training Cascade skipped for now (update needed)")
        """Layer 5 acts as the 'Teacher' to improve other layers."""
        """teacher_prompt = self.prompts.get('teacher', {}).get('system_prompt')
        if not teacher_prompt:
            self.logger.error("Teacher prompt not found in prompts.json. Aborting cascade.")
            return

        logs = self.action_logger.get_logs()
        punished_actions = [
            log for log in logs['action_history'] 
            if any(f['feedback_for'] == log['action_id'] and f['feedback_type'] == 'punishment' for f in logs['feedback_log'])
        ]

        if not punished_actions:
            self.logger.info("No punished actions found. No training needed.")
            return

        self.logger.info(f"Found {len(punished_actions)} punished actions to learn from.")
        
        # Den Lehrer (L5) bitten, neue Prompts zu generieren
        teacher_task_prompt = f""" 
        #{teacher_prompt}

       # **Performance Data:**
       # {json.dumps(logs, indent=2)}

       # Based on this data, generate the improved prompts.
        """
        
        try:
            teacher_layer = self.layers[5]
            self.logger.info("Requesting new prompts from the Teacher (L5)...")
            
            # Hier wird der Teacher-Prompt aus der JSON-Datei geladen
            teacher_task_prompt = self.prompts.get('teacher', {}).get('system_prompt', '')
            teacher_task_prompt += f"\n\n**Performance Data:**\n{json.dumps(logs, indent=2)}\n\nBased on this data, generate the improved prompts."

            response = teacher_layer._execute_llm_call(teacher_task_prompt)
            
            if response and isinstance(response, dict):
                updated = False
                # --- KORREKTUR: Mache den Key-Vergleich case-insensitive ---
                for layer_key_raw, new_prompt_text in response.items():
                    layer_key = layer_key_raw.lower() # z.B. 'Layer3' -> 'layer3'
                    if layer_key in self.prompts and 'system_prompt' in self.prompts[layer_key]:
                        self.logger.info(f"Updating prompt for '{layer_key}'...")
                        self.prompts[layer_key]['system_prompt'] = new_prompt_text
                        updated = True
                
                if updated:
                    with open('prompts.json', 'w', encoding='utf-8') as f:
                        json.dump(self.prompts, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"Successfully updated 'prompts.json'. The agent will use these new instructions on the next run.")
            else:
                self.logger.error("Teacher (L5) did not return a valid prompt update dictionary.")

        except Exception as e:
            self.logger.error(f"An error occurred during the training cascade: {e}", exc_info=True)"""
        

    def manage_short_term_memory(self):
        """
        Initiates the consolidation of the entire STM session:
        1. Summarizes feedback-driven events into 'Learned Lessons'.
        2. Archives them to LTM.
        3. Clears STM and ActionLogger for the next session.
        """
        self.logger.info("--- STM Management Cycle Initiated (Consolidate & Learn) ---")
        graph_snapshot = self.cpp_core.serialize_graph()
        nodes, _ = msgpack.unpackb(graph_snapshot)

        if not nodes:
            self.logger.info("STM is empty. Nothing to manage.")
            return
        
        # 1. Den Manager die Lektionen aus der Session erstellen lassen
        final_emotion = self.affective_engine.get_state_as_text()
        self.stm_manager.consolidate_and_learn(nodes, final_emotion)
            
        # 2. STM leeren
        self.logger.info("Consolidation complete. Clearing STM for the next session.")
        self.cpp_core.clear_graph()

        # 3. ActionLogger leeren
        self.action_logger.clear_logs()

        self.affective_engine.reset()
        
        self.logger.info("--- STM Management Cycle Complete ---")

    # --- `reward` und `punish` werden wieder vereinfacht ---
    # Ihre einzige Aufgabe ist es, das Feedback ins STM zu schreiben.
    def log_feedback_to_stm(self, feedback_type: str, value: float, reason: str):
        log_message = f"FEEDBACK: Received {feedback_type} of value {value}. Reason: '{reason}'"
        self.logger.info(f"Logging feedback to STM: {log_message}")
        self.cpp_core.add_node(log_message, salience=0.9)

    def reward(self, value: float, reason: str = ""):
        """Applies an external reward and logs the feedback assignment with a reason."""
        self.affective_engine.apply_reward(value)
        self.action_logger.assign_feedback(value, "reward", reason)
        self.log_feedback_to_stm("reward", value, reason)

    def punish(self, value: float, reason: str = ""):
        """Applies an external punishment and logs the feedback assignment with a reason."""
        self.affective_engine.apply_punishment(value)
        self.action_logger.assign_feedback(value, "punishment", reason)
        self.log_feedback_to_stm("punishment", value, reason)


    def get_status(self) -> str:
        """Returns the current internal status of the agent."""
        return f"Internal Emotion: {self.affective_engine.get_state_as_text()}"