# memory/stm_manager.py (FINAL KORRIGIERT)

import logging
import ollama
import json

class STMManager:
    """
    The intelligent "Memory Consolidator". It analyzes the entire content of the STM
    at the end of a session, identifies distinct learning events (ending with feedback),
    summarizes each into a 'Learned Lesson', and archives them to LTM.
    """
    def __init__(self, memory_subsystem):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = ollama.Client()
        self.model_name = "granite4:3b"
        self.memory_subsystem = memory_subsystem
        
        # --- KORREKTUR: Die Prompt-Variablen werden hier korrekt definiert ---
        self.lesson_prompt = """
        You are an AI Analyst summarizing an AI's cognitive session into a series of 'Learned Lessons'.
        You will receive a list of raw memories from the Short-Term Memory.
        A 'learning cycle' is a sequence of memories that ends with a 'FEEDBACK' node.
        
        Your task is to:
        1. Identify each complete learning cycle in the list.
        2. For EACH cycle, create a single, concise 'Learned Lesson' string.
        3. Ignore all memories that are not part of a completed feedback cycle.
        
        The format for each lesson MUST be:
        "INPUT: [The user's core request that started the cycle] | OUTPUT: [The agent's final response that was judged] | RESULT: [A summary of the feedback] | EMOTION: [The agent's internal emotion during the summary]"

        You MUST respond with a valid JSON object containing a single key "learned_lessons", which is a list of the lesson strings you generated.
        """
        self.day_summary_prompt = """
        You are an AI Psychologist analyzing a list of 'Learned Lessons' from an AI's session.
        Your task is to synthesize these individual experiences into a single, overarching 'Lesson of the Day'.
        This meta-lesson should capture the most important learning or pattern from the session.
        Your output must be a single string.
        """
        self.logger.info(f"STM Manager (Consolidator) initialized with LLM: {self.model_name}.")

    def consolidate_and_learn(self, stm_nodes: list, final_emotion_text: str):
        """
        Analyzes all STM nodes, generates a list of learned lessons, and archives them.
        """
        if not any("FEEDBACK:" in node[1] for node in stm_nodes):
            self.logger.info("No feedback nodes found in STM. No new lessons to learn.")
            return

        formatted_nodes = "\n- ".join([f"Node({n[0]}, '{n[1]}', salience={n[2]})" for n in stm_nodes])
        prompt_input = f"STM Snapshot:\n- {formatted_nodes}\n\nAgent's final Internal Emotion State for this session: '{final_emotion_text}'"

        self.logger.info(f"STM Manager consolidating {len(stm_nodes)} nodes into lessons...")
        try:
            # --- KORREKTUR: Die korrekte Prompt-Variable wird hier verwendet ---
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': self.lesson_prompt},
                    {'role': 'user', 'content': prompt_input}
                ],
                format='json'
            )
            data = json.loads(response['message']['content'])
            learned_lessons = data.get("learned_lessons", [])
            
            if not learned_lessons:
                self.logger.warning("Consolidator did not generate any lessons from the STM content.")
                return

            self.logger.info(f"Generated {len(learned_lessons)} new individual Learned Lesson(s).")
            
            for lesson in learned_lessons:
                self.memory_subsystem.add_experience(
                    text=lesson,
                    metadata={"source": "learned_lesson"}
                )
            self.logger.info("Successfully archived all individual lessons to LTM.")

            if len(learned_lessons) > 1:
                self.logger.info("Synthesizing the 'Lesson of the Day'...")
                day_summary_input = "\n- ".join(learned_lessons)
                summary_response = self.client.chat(
                    model=self.model_name,
                    messages=[
                        {'role': 'system', 'content': self.day_summary_prompt},
                        {'role': 'user', 'content': f"Here are the lessons from the session:\n- {day_summary_input}"}
                    ]
                )
                lesson_of_the_day = summary_response['message']['content'].strip()
                self.logger.info(f"Generated Lesson of the Day: '{lesson_of_the_day}'")
                
                self.memory_subsystem.add_experience(
                    text=lesson_of_the_day,
                    metadata={"source": "lesson_of_the_day"}
                )
                self.logger.info("Successfully archived the Lesson of the Day to LTM.")

        except Exception as e:
            self.logger.error(f"STM Manager failed during consolidation: {e}", exc_info=True)