"""SymptomsLog model for the Wellness Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class SymptomsLog:
    """
    Model for tracking employee symptoms over time.
    
    This model enables privacy-respecting symptom tracking for employees,
    with various input options (emoji, scale, text) to make daily check-ins
    quick and non-judgmental.
    """
    log_id: str
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Employee symptom tracking
    symptom_rating: Optional[int] = None  # 1-10 scale
    symptom_emoji: Optional[str] = None  # Emoji representation
    symptom_text: Optional[str] = None  # Free text description
    
    # Additional health metrics
    energy_level: Optional[int] = None  # 1-10 scale
    stress_level: Optional[int] = None  # 1-10 scale
    sleep_quality: Optional[int] = None  # 1-10 scale
    
    # Work impact tracking
    productivity_impact: Optional[int] = None  # 1-10 scale
    needs_accommodation: Optional[bool] = None
    accommodation_type: Optional[str] = None  # "remote", "flexible", "break", etc.
    
    # Privacy controls
    privacy_level: str = "standard"  # Inherited from user settings
    share_with_hr: bool = False  # Whether this log can be shared with HR
    is_anonymous: bool = True  # Whether to anonymize this data in reports
    
    # Contextual information
    tags: List[str] = field(default_factory=list)  # Tags for categorization
    notes: Optional[str] = None  # Additional notes
    location: Optional[str] = None  # Work location ("office", "home", etc.)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the symptoms log to a dictionary for storage."""
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "symptom_rating": self.symptom_rating,
            "symptom_emoji": self.symptom_emoji,
            "symptom_text": self.symptom_text,
            "energy_level": self.energy_level,
            "stress_level": self.stress_level,
            "sleep_quality": self.sleep_quality,
            "productivity_impact": self.productivity_impact,
            "needs_accommodation": self.needs_accommodation,
            "accommodation_type": self.accommodation_type,
            "privacy_level": self.privacy_level,
            "share_with_hr": self.share_with_hr,
            "is_anonymous": self.is_anonymous,
            "tags": self.tags,
            "notes": self.notes,
            "location": self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymptomsLog':
        """Create a SymptomsLog instance from a dictionary."""
        # Convert ISO date string to datetime object
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            
        return cls(**data)
    
    def anonymize(self) -> 'SymptomsLog':
        """
        Create an anonymized copy of this log for reporting.
        
        Returns:
            An anonymized copy of this symptoms log
        """
        # Create a copy of the log
        anon_log = SymptomsLog(
            log_id=f"anon_{self.log_id}",
            user_id="anonymous",
            timestamp=self.timestamp,
            symptom_rating=self.symptom_rating,
            symptom_emoji=self.symptom_emoji,
            energy_level=self.energy_level,
            stress_level=self.stress_level,
            sleep_quality=self.sleep_quality,
            productivity_impact=self.productivity_impact,
            needs_accommodation=self.needs_accommodation,
            accommodation_type=self.accommodation_type,
            privacy_level="anonymous",
            share_with_hr=True,
            is_anonymous=True,
            tags=self.tags.copy(),
            location=self.location
        )
        
        # Remove any potentially identifying information
        anon_log.symptom_text = None
        anon_log.notes = None
        
        return anon_log 