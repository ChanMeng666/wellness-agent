"""Emoji input helpers for the Wellness Agent."""

from typing import Dict, List, Tuple, Optional

# Define mood emoji mappings with corresponding descriptions and scores
MOOD_EMOJIS = {
    "😊": {"description": "Happy", "score": 5, "related_terms": ["happy", "great", "energetic"]},
    "😌": {"description": "Content", "score": 4, "related_terms": ["content", "good", "satisfied"]},
    "😐": {"description": "Neutral", "score": 3, "related_terms": ["okay", "fine", "neutral"]},
    "😟": {"description": "Concerned", "score": 2, "related_terms": ["worried", "stressed", "anxious"]},
    "😣": {"description": "Struggling", "score": 1, "related_terms": ["bad", "poor", "terrible", "struggling"]}
}

# Define symptom emoji mappings
SYMPTOM_EMOJIS = {
    "🤕": {"type": "headache", "description": "Headache", "related_terms": ["headache", "migraine", "head pain"]},
    "😴": {"type": "fatigue", "description": "Fatigue", "related_terms": ["tired", "exhausted", "low energy"]},
    "🌫️": {"type": "focus", "description": "Focus issues", "related_terms": ["brain fog", "distracted", "concentration"]},
    "😰": {"type": "anxiety", "description": "Anxiety", "related_terms": ["anxious", "stressed", "overwhelmed"]},
    "😥": {"type": "mood", "description": "Low mood", "related_terms": ["sad", "depressed", "down"]},
    "💪": {"type": "energy", "description": "Energy level", "related_terms": ["vitality", "stamina"]},
    "🧠": {"type": "cognitive", "description": "Cognitive function", "related_terms": ["memory", "thinking", "clarity"]},
    "💤": {"type": "sleep", "description": "Sleep quality", "related_terms": ["insomnia", "rest", "tired"]},
    "🤒": {"type": "fever", "description": "Fever", "related_terms": ["temperature", "hot", "cold"]},
    "🥴": {"type": "dizziness", "description": "Dizziness", "related_terms": ["vertigo", "lightheaded", "faint"]}
}

# Define emoji-based severity levels
SEVERITY_EMOJIS = {
    "⚪": {"level": 1, "description": "Minimal"},
    "🟡": {"level": 2, "description": "Mild"},
    "🟠": {"level": 3, "description": "Moderate"},
    "🔴": {"level": 4, "description": "Severe"}
}

def parse_emoji_mood(emoji: str) -> Dict:
    """
    Parse a mood emoji into its corresponding data.
    
    Args:
        emoji: The emoji character to parse
        
    Returns:
        Dictionary with mood information or default values if not recognized
    """
    return MOOD_EMOJIS.get(emoji, {"description": "Unknown", "score": 3, "related_terms": []})

def get_symptom_from_emoji(emoji: str) -> Dict:
    """
    Get symptom information from a symptom emoji.
    
    Args:
        emoji: The emoji character to parse
        
    Returns:
        Dictionary with symptom information or default values if not recognized
    """
    return SYMPTOM_EMOJIS.get(emoji, {"type": "unknown", "description": "Unknown symptom", "related_terms": []})

def get_severity_from_emoji(emoji: str) -> Dict:
    """
    Get severity information from a severity emoji.
    
    Args:
        emoji: The emoji character to parse
        
    Returns:
        Dictionary with severity information or default values if not recognized
    """
    return SEVERITY_EMOJIS.get(emoji, {"level": 2, "description": "Moderate"})

def emoji_to_wellbeing_score(emoji: str) -> int:
    """
    Convert a mood emoji to a numeric wellbeing score (1-5).
    
    Args:
        emoji: The emoji character to convert
        
    Returns:
        Numeric score from 1-5
    """
    mood_data = parse_emoji_mood(emoji)
    return mood_data["score"]

def get_emoji_keyboard(emoji_type: str = "mood") -> List[Dict]:
    """
    Get a formatted emoji keyboard for the specified type.
    
    Args:
        emoji_type: The type of emoji keyboard to return (mood, symptom, severity)
        
    Returns:
        List of emoji options with their descriptions for display in the UI
    """
    if emoji_type == "mood":
        return [{"emoji": k, **v} for k, v in MOOD_EMOJIS.items()]
    elif emoji_type == "symptom":
        return [{"emoji": k, **v} for k, v in SYMPTOM_EMOJIS.items()]
    elif emoji_type == "severity":
        return [{"emoji": k, **v} for k, v in SEVERITY_EMOJIS.items()]
    else:
        return []

def text_to_emoji_suggestion(text: str, emoji_type: str = "mood") -> Optional[str]:
    """
    Suggest an emoji based on text input.
    
    Args:
        text: The text to parse for emotion/symptom keywords
        emoji_type: The type of emoji to suggest
        
    Returns:
        Suggested emoji or None if no match found
    """
    text = text.lower()
    
    if emoji_type == "mood":
        for emoji, data in MOOD_EMOJIS.items():
            if any(term in text for term in data["related_terms"]):
                return emoji
    elif emoji_type == "symptom":
        for emoji, data in SYMPTOM_EMOJIS.items():
            if any(term in text for term in data["related_terms"]):
                return emoji
    elif emoji_type == "severity":
        severity_terms = {
            "minimal": "⚪",
            "mild": "🟡",
            "moderate": "🟠",
            "severe": "🔴",
            "light": "🟡",
            "medium": "🟠",
            "heavy": "🔴",
            "bad": "🔴",
            "worst": "🔴",
            "little": "🟡",
            "bit": "⚪",
            "slightly": "🟡",
            "very": "🔴"
        }
        
        for term, emoji in severity_terms.items():
            if term in text:
                return emoji
    
    return None 