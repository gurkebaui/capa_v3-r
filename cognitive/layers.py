# cognitive/layers.py (KORRIGIERT & ROBUSTER)

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
    """
    Finds and extracts the first valid JSON object (from '{' to '}') from a string.
    This makes the parsing robust against chatty LLMs.
    """
    try:
        # Finde den ersten Start des JSON-Objekts
        start_index = response_text.index('{')
        # Finde das letzte Ende des JSON-Objekts
        end_index = response_text.rindex('}') + 1
        # Extrahiere den reinen JSON-String
        return response_text[start_index:end_index]
    except ValueError:
        # Tritt auf, wenn '{' oder '}' nicht gefunden werden
        logging.error(f"Could not find a JSON object in the LLM response: {response_text}")
        raise

class BaseThinkingLayer:
    """
    A base class for all thinking layers, centralizing LLM interaction.
    """
    def __init__(self, model_name: str, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name
        self.cpp_core = cpp_core
        self.man = man
        self.client = ollama.Client()
        self.logger.info(f"Initialized with dedicated LLM Model: {self.model_name}. MAN Access: {'Yes' if self.man else 'No'}")

    # ... _format_graph_for_prompt bleibt unverändert ...
    def _format_graph_for_prompt(self, nodes: list, edges: list) -> str:
        if not nodes: return "The short-term memory is currently empty."
        node_str = ", ".join([f"Node({n[0]}, '{n[1]}')" for n in nodes])
        edge_str = ", ".join([f"Edge({e[0]}->{e[1]}, w={e[2]})" for e in edges])
        return f"Current STM State: Nodes=[{node_str}], Edges=[{edge_str}]"

    def think(self, graph_snapshot: bytes) -> dict:
        """
        The core thinking process for a layer.
        """
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        self.logger.info(f"Analyzing STM snapshot: {formatted_graph}")

        # --- ANGEPASSTER PROMPT ---
        prompt = f"""
        You are a cognitive layer in an AI with the model '{self.model_name}'. Your task is to analyze the user's input, if it helps, use the current Short-Term Memory (STM) state .

        **CRITICAL INSTRUCTION: You must honestly self-assess your confidence.**
        - **High Confidence (> 90):** Use for simple, factual questions you are certain about (e.g., "What is the capital of France?") or simple dialog.
        - **Medium Confidence (40-90):** Use if you understand the question but need to "think step-by-step" to be sure of the answer or complex dialog.
        - **Low Confidence (< 40):** Use for complex logic puzzles, ambiguous questions, or topics you know little about or very compplex dialog. This is NOT a failure; it signals that a more powerful AI layer needs to take over.

        **Current STM state:**
        {formatted_graph}

        Based on this, provide your analysis as a valid JSON object with three keys:
        1. "internal_monologue": Your brief, step-by-step reasoning or your assessment of the question's nature. (only if needed)
        2. "external_response": The direct answer or response for the user. (only if confident)
        3. "confidence_score": Your honest confidence score (0-100) based on the rules above.

        **Example for a complex riddle:**
        {{
            "internal_monologue": "This is a logic puzzle, not a simple fact. It requires careful step-by-step deduction. My initial analysis is incomplete.",
            "external_response": "That's a tricky question. Let me think about that for a moment." or none,
            "confidence_score": 35
        }}

         **Example for a fast awnser:**
        {{
            "internal_monologue": none,
            "external_response": " That's Paris",
            "confidence_score": 90
        }}
        """

        try:
            self.logger.info(f"Sending request to dedicated LLM ({self.model_name})...")
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json'
            )
            
            response_content = response['message']['content']
            
            # --- NEUER, ROBUSTER SCHRITT ---
            # Bereinige den Output, bevor wir ihn parsen.
            cleaned_json = _extract_json_from_response(response_content)
            
            result = json.loads(cleaned_json)
            self.logger.info(f"LLM ({self.model_name}) generated: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error during LLM ({self.model_name}) interaction: {e}", exc_info=True)
            return {
                "internal_monologue": f"Error processing LLM response from {self.model_name}.",
                "external_response": "I encountered an error while thinking.",
                "confidence_score": 0
            }

# --- Die Layer-Klassen bleiben exakt gleich ---
class ThinkingLayer3(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore):
        super().__init__(model_name="gemma:2b", cpp_core=cpp_core, man=None)

class ThinkingLayer4(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork):
        super().__init__(model_name="qwen:7b", cpp_core=cpp_core, man=man)

class ThinkingLayer5(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork):
        super().__init__(model_name="llama3:8b", cpp_core=cpp_core, man=man)