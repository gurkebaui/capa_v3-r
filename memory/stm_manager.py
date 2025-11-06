# memory/stm_manager.py (FINAL KORRIGIERT)

import logging
import ollama
import json

class STMManager:
    """
    The intelligent storyteller for the STM. It analyzes the STM graph, identifies
    significant events (input -> output -> feedback), and summarizes them into
    'learned lessons' for the Long-Term Memory.
    """
    def __init__(self, memory_subsystem):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = ollama.Client()
        self.model_name = "granite4:3b"
        self.memory_subsystem = memory_subsystem
        self.system_prompt = """
        You are an AI Analyst summarizing a cognitive cycle. You will receive a snapshot of memories. Your task is to identify the core event and summarize it into a single, concise 'Learned Lesson'.
        The format MUST be: "INPUT: [user's core request] | OUTPUT: [agent's final response] | RESULT: [summary of feedback, e.g., 'Positive feedback', 'Negative feedback: was nonsensical', or 'Neutral'] | EMOTION: [internal emotion after feedback, e.g., 'very positive', 'negative']"

        - Focus on the most important nodes: the user's direct input, the agent's final external response, and any FEEDBACK nodes.
        - Ignore intermediate thoughts ('L_THOUGHT', 'RECURSIVE_THOUGHT').
        - If there is no feedback, the RESULT is 'Neutral'.

        Example Input:
        - "Node(0, 'was ist 2+2', salience=1.0)"
        - "Node(1, 'RECURSIVE_THOUGHT: I should calculate this.', salience=0.8)"
        - "Node(2, 'The answer is 4.', salience=1.0)"
        - "Node(3, 'FEEDBACK: Received reward of value 1.0. Reason: 'correct answer'', salience=0.8)"

        Example Output:
        "INPUT: was ist 2+2 | OUTPUT: The answer is 4. | RESULT: Positive feedback: 'correct answer' | EMOTION: positive"
        """
        self.logger.info(f"STM Manager (Storyteller) initialized with LLM: {self.model_name}.")

    def summarize_and_archive(self, stm_nodes: list, final_emotion_text: str):
        """
        Summarizes the key event from the STM nodes into a 'learned lesson' and archives it.
        """
        if not stm_nodes:
            self.logger.info("STM is empty. Nothing to summarize.")
            return

        # Formatiere die Knoten für den Prompt
        formatted_nodes = "\n- ".join([f"Node({n[0]}, '{n[1]}', salience={n[2]})" for n in stm_nodes])
        prompt_input = f"STM Snapshot:\n- {formatted_nodes}\n\nFinal Internal Emotion State: '{final_emotion_text}'"

        self.logger.info(f"STM Manager summarizing {len(stm_nodes)} nodes into a lesson...")
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt_input}
                ],
            )
            # Wir nehmen die Antwort direkt, da sie bereits das korrekte Format haben sollte
            learned_lesson = response['message']['content'].strip()
            
            self.logger.info(f"Generated Learned Lesson: '{learned_lesson}'")
            
            # Die zusammengefasste Lektion ins LTM speichern
            self.memory_subsystem.add_experience(
                text=learned_lesson,
                metadata={"source": "learned_lesson"}
            )
            self.logger.info("Successfully archived the learned lesson to LTM.")

        except Exception as e:
            self.logger.error(f"STM Manager failed to create a learned lesson: {e}.")