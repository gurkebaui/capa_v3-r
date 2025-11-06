# cognitive/layers.py (VOLLSTÄNDIG & KORRIGIERT)

import logging
import json
import msgpack
import ollama
from memory.man import MemoryAccessNetwork
try:
    from capa_core import CPPCore # type: ignore
except ImportError:
    CPPCore = None

def _extract_json_from_response(response_text: str) -> str:
    """Finds and extracts the first valid JSON object."""
    try:
        start_index = response_text.index('{')
        end_index = response_text.rindex('}') + 1
        return response_text[start_index:end_index]
    except ValueError:
        logging.error(f"Could not find a JSON object in the LLM response: {response_text}")
        raise

class BaseThinkingLayer:
    """A base class for all thinking layers, centralizing LLM interaction."""
    def __init__(self, model_name: str, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name
        self.cpp_core = cpp_core
        self.man = man
        self.client = ollama.Client()
        self.logger.info(f"Initialized with dedicated LLM Model: {self.model_name}. MAN Access: {'Yes' if self.man else 'No'}")

    def _format_graph_for_prompt(self, nodes: list, edges: list) -> str:
        """Converts the graph data into a simple string for the LLM prompt."""
        if not nodes:
            return "The short-term memory is currently empty."
        node_str = ", ".join([f"Node({n[0]}, '{n[1]}', salience={n[2]})" for n in nodes])
        edge_str = ", ".join([f"Edge({e[0]}->{e[1]}, w={e[2]})" for e in edges])
        return f"Current STM State: Nodes=[{node_str}], Edges=[{edge_str}]"

    def _execute_llm_call(self, prompt: str) -> dict:
        """Helper to centralize the actual Ollama call and error handling."""
        try:
            self.logger.info(f"Sending request to dedicated LLM ({self.model_name})...")
            response = self.client.chat(model=self.model_name, messages=[{'role': 'user', 'content': prompt}], format='json')
            response_content = response['message']['content']
            cleaned_json = _extract_json_from_response(response_content)
            result = json.loads(cleaned_json)
            self.logger.info(f"LLM ({self.model_name}) generated: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error during LLM ({self.model_name}) interaction: {e}", exc_info=True)
            return {"internal_monologue": "Error processing response.", "external_response": "Error.", "confidence_score": 0, "plan": None}

    def think(self, graph_snapshot: bytes, active_plans: list[str], emotion_context: str) -> dict:
        raise NotImplementedError("Each layer must implement its own think method.")


class ThinkingLayer3(BaseThinkingLayer):
    # --- KORREKTUR: Fehlende __init__ Methode wieder hinzugefügt ---
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="gemma:2b", cpp_core=cpp_core, man=None)

    def think(self, graph_snapshot: bytes, active_plans: list[str], emotion_context: str) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        prompt = f"""
        You are the 'Reflex' layer (Model: gemma:2b), a helpful assistant.
        **CRITICAL RULE 1: The user's most recent input (highest salience) has absolute priority.**
        **CRITICAL RULE 2: Your memories and plans are context ONLY.** Do NOT talk about them unless the user's input is directly related to them.

        Current Emotional Context: {emotion_context}
        Active Plans: {"".join(active_plans) if active_plans else "None"}
        Current STM state: {formatted_graph}

        Based *primarily* on the user's latest input, provide a valid JSON with "internal_monologue", "external_response", and "confidence_score". be brutally honest about your confidence.
        if confidence is below 40, indicate that you need to escalate to the next layer for deeper analysis. If the user's input is simple and direct, you can handle it here with high confidence. If the input involves complex reasoning or future planning, you MUST have low confidence (< 40) to escalate.
        """
        return self._execute_llm_call(prompt)

class ThinkingLayer4(BaseThinkingLayer):
    # --- KORREKTUR: Fehlende __init__ Methode wieder hinzugefügt ---
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="qwen:7b", cpp_core=cpp_core, man=man)

    def think(self, graph_snapshot: bytes, active_plans: list[str], emotion_context: str) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        prompt = f"""
        You are the 'Tactical' layer (Model: qwen:7b), a helpful assistant.
        **CRITICAL RULE 1: The user's most recent input (highest salience) has absolute priority.**
        **CRITICAL RULE 2: Your memories and plans are context ONLY.** Do NOT talk about them unless the user's input is directly related to them.
        **YOUR TASK:** Handle immediate, multi-step problems. If a task has a future deadline, you MUST have low confidence (< 40) to escalate.

        Current Emotional Context: {emotion_context}
        Active Plans: {"".join(active_plans) if active_plans else "None"}
        Current STM state: {formatted_graph}

        Based *primarily* on the user's latest input, respond with a valid JSON.
        """
        return self._execute_llm_call(prompt)


class ThinkingLayer5(BaseThinkingLayer):
    # --- KORREKTUR: Fehlende __init__ Methode wieder hinzugefügt ---
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="llama3:8b", cpp_core=cpp_core, man=man)

    def think(self, graph_snapshot: bytes, active_plans: list[str], emotion_context: str) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        prompt = f"""
        You are the 'Strategic' layer (Model: llama3:8b), a helpful assistant.
        **CRITICAL RULE 1: The user's most recent input (highest salience) has absolute priority.**
        **CRITICAL RULE 2: Your memories and plans are context ONLY.** Do NOT talk about them unless the user's input is directly related to them.
        **YOUR TASK:** Create long-term, strategic plans for complex, future-oriented tasks.
        **YOUR OTHER TASK (most important)** If the user's input poses a complex problem without a clear future deadline, create a short-term plan to address it immediately(only if a hard reasonong problem). Or handle it directly if possible (appreciated).

        Current Emotional Context: {emotion_context}
        Active Plans: {"".join(active_plans) if active_plans else "None"}
        Current STM state: {formatted_graph}

        Based *primarily* on the user's latest input, respond with a valid JSON.
        """
        return self._execute_llm_call(prompt)

    def create_training_data_for_layer1(self):
        self.logger.warning("BRIDGE MODE: Would analyze recent Layer 1 performance and generate a fine-tuning dataset (LoRAs).")