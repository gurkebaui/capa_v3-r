# affective/engine.py

import logging

class AffectiveEngine:
    """
    Manages the agent's internal emotional state using a Valence-Arousal model.
    - Valence: How pleasant (-1.0) or unpleasant (+1.0) the feeling is.
    - Arousal: The intensity or energy level of the feeling (0.0 to 1.0).
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Start in a neutral state: [valence, arousal]
        self.state = [0.0, 0.0]
        self.logger.info(f"Affective Engine initialized with neutral state: {self.state}")

    def apply_reward(self, value: float):
        """Applies a positive feedback, increasing valence and arousal."""
        valence, arousal = self.state
        valence = min(100.0, valence + abs(value))
        arousal = min(100.0, arousal + abs(value) * 0.5) # Arousal increases less sharply
        self.state = [valence, arousal]
        self.logger.info(f"REWARD applied. New state: {self.state}")

    def apply_punishment(self, value: float):
        """Applies a negative feedback, decreasing valence and increasing arousal."""
        valence, arousal = self.state
        valence = max(-100.0, valence - abs(value))
        arousal = min(100.0, arousal + abs(value) * 0.5)
        self.state = [valence, arousal]
        self.logger.warning(f"PUNISHMENT applied. New state: {self.state}")

    def get_state_as_text(self) -> str:
        """Translates the [valence, arousal] vector into a human-readable string for the LLM."""
        valence, arousal = self.state
        
        # Valence description
        if valence > 50.5: v_text = "very positive"
        elif valence > 30.1: v_text = "positive"
        elif valence < -50.5: v_text = "very negative"
        elif valence < -30.1: v_text = "negative"
        else: v_text = "neutral"

        # Arousal description
        if arousal > 60.7: a_text = "high arousal (intense)"
        elif arousal > 30.3: a_text = "moderate arousal"
        else: a_text = "low arousal (calm)"
        
        return f"{v_text}, {a_text}"