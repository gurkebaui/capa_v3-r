# affective/logger.py

import logging
import uuid
from datetime import datetime

class ActionLogger:
    """
    Records actions taken by cognitive layers and links them to subsequent feedback.
    This is the core of the 'Credit Assignment' mechanism.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.action_history = []
        self.feedback_log = []
        self.logger.info("Action Logger initialized.")

    def log_action(self, layer_index: int, model_name: str, system_prompt: str, result: dict) -> str:
        """Logs a cognitive action, including the system prompt used."""
        action_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        record = {
            "action_id": action_id,
            "timestamp": timestamp,
            "layer": f"Layer {layer_index}",
            "model": model_name,
            "system_prompt_used": system_prompt, # <-- NEUES FELD
            "output": result
        }
        self.action_history.append(record)
        self.logger.info(f"Logged action {action_id} from Layer {layer_index}.")
        return action_id
    

    def get_action_by_id(self, action_id: str) -> dict | None:
        """Finds and returns a specific action record from the history."""
        for action in self.action_history:
            if action["action_id"] == action_id:
                return action
        return None
    
    def clear_logs(self):
        """Clears all action and feedback history after a learning cycle."""
        self.action_history.clear()
        self.feedback_log.clear()
        self.logger.info("Action and feedback logs have been cleared for the next session.")

    def assign_feedback(self, value: float, feedback_type: str, reason: str = ""):
        """
        Links incoming feedback, including an optional reason, to the most recent action.
        """
        if not self.action_history:
            self.logger.warning("Received feedback, but no action history to assign it to.")
            return

        last_action = self.action_history[-1]
        action_id = last_action["action_id"]
        
        feedback_record = {
            "feedback_for": action_id,
            "feedback_type": feedback_type,
            "value": value,
            "reason": reason, # <-- NEUES FELD
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_log.append(feedback_record)
        self.logger.info(f"Assigned {feedback_type} (value: {value}, reason: '{reason}') to action {action_id}.")

    def get_logs(self) -> dict:
        """Returns all recorded logs for inspection."""
        return {
            "action_history": self.action_history,
            "feedback_log": self.feedback_log
        }