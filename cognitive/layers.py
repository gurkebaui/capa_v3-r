# cognitive/layers.py (KORRIGIERT)

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
        node_str = ", ".join([f"Node({n[0]}, '{n[1]}')" for n in nodes])
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

    def think(self, graph_snapshot: bytes, active_plans: list[str]) -> dict:
        """This method will now be overridden by each subclass."""
        raise NotImplementedError("Each layer must implement its own think method.")

# --- KORREKTUR HIER: Die __init__ Methoden müssen die Argumente an super() weitergeben ---

class ThinkingLayer3(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="gemma:2b", cpp_core=cpp_core, man=None)

    def think(self, graph_snapshot: bytes, active_plans: list[str]) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        
        # --- KORREKTUR: Verbesserter Prompt für Layer 3 ---
        prompt = f"""
        You are the 'Reflex' layer (Model: gemma:2b). Your job is to handle simple, direct questions.
        
        **CRITICAL RECURSION RULE:** If you see nodes labeled 'RECURSIVE_THOUGHT' in the STM, it means your previous attempt was not good enough. You MUST analyze that thought and try a DIFFERENT approach. Do not repeat yourself.

        **Active Plans (for context only):** {"".join(active_plans) if active_plans else "None"}
        **Current STM state:** {formatted_graph}

        Provide your analysis as a valid JSON object with keys "internal_monologue", "external_response", and "confidence_score". Be brutally honest about your confidence. it is not a failiure to admit low confidence; it shows self-awareness.
        Lower your confidence if you see 'RECURSIVE_THOUGHT' nodes and explain why in your monologue. Lower your confidence  below 40% if the task seems complex or future-oriented. Your output must be a valid JSON.
        """
        return self._execute_llm_call(prompt)


class ThinkingLayer4(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="qwen:7b", cpp_core=cpp_core, man=man)
    
    def think(self, graph_snapshot: bytes, active_plans: list[str]) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        
        # --- KORREKTUR: Deutlich strengerer Prompt für Layer 4 ---
        prompt = f"""
        You are the 'Tactical' layer (Model: qwen:7b). You break down problems that can be solved *immediately* into short-term plans.

        **CRITICAL RULE:** If the user's request involves a future deadline or action (e.g., 'tomorrow', 'next week', 'summarize later'), you are NOT the correct layer to handle it. Your confidence in this case MUST be low (< 40) to ensure the problem is escalated to the strategic Layer 5. Do not try to solve future-oriented tasks.

        **Active Plans:** {"".join(active_plans) if active_plans else "None"}
        **Current STM state:** {formatted_graph}

        Analyze the situation. If it's an immediate task, create a "short_term" plan. If it's a future task, state that in your monologue and set a low confidence score.
        Your output must be a valid JSON.
        """
        return self._execute_llm_call(prompt)


class ThinkingLayer5(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="llama3:8b", cpp_core=cpp_core, man=man)

    def think(self, graph_snapshot: bytes, active_plans: list[str]) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        prompt = f"""
        You are the 'Strategic' layer (Model: llama3:8b). You create long-term, strategic plans for complex, future-oriented tasks.
        If the user asks for something that cannot be done in one step (e.g., "research X and summarize tomorrow"), you MUST create a "long_term" plan.

        Active Plans: {"".join(active_plans) if active_plans else "None"}
        Current STM state: {formatted_graph}

        Analyze the situation. If you create a long-term plan, your JSON output MUST include:
        - "internal_monologue": Your reasoning for creating the plan.
        - "external_response": A confirmation to the user that you have created a plan.
        - "confidence_score": 100 (since you are creating a plan, not answering).
        - "plan": A list of strings representing the steps.
        - "plan_type": "long_term"
        """
        return self._execute_llm_call(prompt)