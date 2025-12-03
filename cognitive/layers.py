# cognitive/layers.py (VOLLSTÄNDIG & KORRIGIERT)

import logging
import json

from psutil import users
import msgpack
import ollama
from memory.man import MemoryAccessNetwork
try:
    from capa_core import CPPCore
except ImportError:
    CPPCore = None

# Placeholder: In the future, these prompts will be loaded from an external file (e.g., prompts.json)
# to allow for autonomous evolution without changing the source code.

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
    def __init__(self, model_name: str, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name
        self.cpp_core = cpp_core
        self.man = man
        self.client = ollama.Client()
        self.system_prompt = "" # Wird in den Subklassen gesetzt
        self.logger.info(f"Initialized with dedicated LLM Model: {self.model_name}. MAN Access: {'Yes' if self.man else 'No'}")


    def _format_graph_for_prompt(self, nodes: list, edges: list) -> str:
        """Converts the graph data into a simple string for the LLM prompt."""
        if not nodes:
            return "The short-term memory is currently empty."
        node_str = ", ".join([f"Node({n[0]}, '{n[1]}', salience={n[2]})" for n in nodes])
        edge_str = ", ".join([f"Edge({e[0]}->{e[1]}, w={e[2]})" for e in edges])
        return f"Current STM State: Nodes=[{node_str}], Edges=[{edge_str}]"

    def _execute_llm_call(self, dynamic_prompt_content: str) -> dict:
        full_prompt = f"{self.system_prompt}\n\n{dynamic_prompt_content}"
        try:
            self.logger.info(f"Sending request to dedicated LLM ({self.model_name})...")
            response = self.client.chat(model=self.model_name, messages=[{'role': 'user', 'content': full_prompt}], format='json')
            response_content = response['message']['content']
            cleaned_json = _extract_json_from_response(response_content)
            result = json.loads(cleaned_json)
            self.logger.info(f"LLM ({self.model_name}) generated: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error during LLM ({self.model_name}) interaction: {e}", exc_info=True)
            return {"internal_monologue": "Error processing response.", "external_response": "Error.", "confidence_score": 0}

    def think(self, **kwargs) -> dict:
        raise NotImplementedError("Each layer must implement its own think method.")



class ThinkingLayer3(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="gemma3:4b", cpp_core=cpp_core, man=None)
        self.system_prompt = """
        You are the 'Reflex' layer. Your job is to answer simple, factual questions with high confidence.
        **CRITICAL RULE: The user's most recent input has absolute priority.**
        If the question is complex, a riddle, or requires multiple steps, you MUST have a low confidence score (e.g., 30) to escalate it. Do not attempt to solve it. Your job is speed and efficiency.
        """

    def think(self, graph_snapshot: bytes, emotion_context: str, internal_emotion_text: str, input_text: str) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        dynamic_content = f"""
        **Data Provided:**
        - Your Emotion: {internal_emotion_text} (behave accordingly, this is your current sate)
        - How the input makes you feel: {emotion_context}
        - Short-Term Memory State: {formatted_graph}
        -User's most recent input: {input_text}

        **Your Task:**
        Fill out the following JSON structure. Be brutally honest about your confidence level. Only awnser simple tasks directly. If there is a riddle or complex dialog or task, do NOT answer directly but reason it out in your internal monologue and lower your confidence below 40%.   
        {{
            "internal_monologue": "Your reasoning."(optional),
            "external_response": "Your direct response.(do not forget your emotion)" (only if confident),
            "confidence_score": Your confidence score (0-100) .
        }}
        """
        return self._execute_llm_call(dynamic_content)
    #for reasoning: Is this a simple fact? Yes/No, because...


class ThinkingLayer4(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, recursion_counter: int, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="dolphin3", cpp_core=cpp_core, man=man)
        self.system_prompt = f"You are the 'Tactical Planner' layer. Your ONLY job is to create a reasoning plan for Layer 5. You do not respond to the user. Analyze the users's request and the STM state. Create a clear, step-by-step plan that the final strategic layer should follow to solve the problem. " if recursion_counter < 2 else "Look at the Input result given to you by layer 5 and look at the Input by the user and determine if what Layer 5 did was correct or not. If it was correct, give a nice output sentence and tell layer 5 to have a high confidence score. If it was not correct, analyze what went wrong and try to solve the problem.  "
    
    def think(self, graph_snapshot: bytes,  active_plans: list[str], emotion_context: str, internal_emotion_text: str, recursion_info: str, recursion_counter: int, input_text: str) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        user_input_display = f"- User's most recent input: {input_text}" if recursion_counter < 2 else "- User's most recent input: {input_text} "

        dynamic_content = f"""
        **Data Provided:**
        - Your Internal Emotion: {internal_emotion_text}
        - How the input makes you feel: {emotion_context}
        - Active Plans: None
        - Reasoning Status: {recursion_info}
        {user_input_display}
        - Short-Term Memory State (for context): {formatted_graph}

        **Your Task:**
        Create a reasoning plan for Layer 5 to follow.
        {{
            "internal_monologue": "My analysis of the user's request and why this plan is necessary. The previous attempt failed because...",
            "plan_for_layer5": ["Step 1: ...", "Step 2: ...", "Step 3: ..., and so on"""if recursion_counter < 2 else "your new salution with a mistake analysis and a confidence of your own""]"
        "}}"
        """"""
        return self._execute_llm_call(dynamic_content)


class ThinkingLayer5(BaseThinkingLayer):
    def __init__(self, cpp_core: CPPCore, man: MemoryAccessNetwork | None = None):
        super().__init__(model_name="dolphin3", cpp_core=cpp_core, man=man)
        self.system_prompt = """
        You are the 'Strategic Executor' layer, a helpful assistant. Your job is to provide the final answer to the user by following a plan from Layer 4.
        **CRITICAL RULE: The user's most recent input has absolute priority.**
        """

    def think(self, graph_snapshot: bytes , active_plans: list[str], emotion_context: str, internal_emotion_text: str, l4_plan: list[str], recursion_info: str, recursion_counter: int, input_text: str) -> dict:
        nodes, edges = msgpack.unpackb(graph_snapshot)
        formatted_graph = self._format_graph_for_prompt(nodes, edges)
        dynamic_content = f"""
        **Data Provided:**
        - Your Internal Emotion: {internal_emotion_text} (behave accordingly, this is your current sate, do not hide it, it is part of you)
        - How the input makes you feel: {emotion_context}
        - **Reasoning plan from Layer 4:** {l4_plan}
        - Short-Term Memory State: {formatted_graph}
        - Active Plans: {"".join(active_plans) if active_plans else "None"}
        - Reasoning Status: {recursion_info}
        { "-Users's most recent input:" .join(input_text) if recursion_counter < 2  else ""}

        **Your Task:**
        Execute the provided reasoning plan in your internal monologue to formulate the final answer. If you are still not confident, give a low confidence score to get a new plan from Layer 4.
        {{
            "internal_monologue": "Executing plan: Step 1...",
            "external_response": "The final, comprehensive answer for the user.(do not forget your emotion)",
            "confidence_score": "Your confidence score for this answer (0-100)."
        }}
        """
        return self._execute_llm_call(dynamic_content)

    def create_training_data_for_layer1(self):
        self.logger.warning("BRIDGE MODE: Would analyze recent Layer 1 performance and generate a fine-tuning dataset (LoRAs).")