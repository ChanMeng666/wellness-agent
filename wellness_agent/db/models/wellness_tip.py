"""WellnessTip model for the Wellness Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class WellnessTip:
    """
    Model for wellness recommendations in the Wellness Agent.
    
    This model stores wellness tips and recommendations that can be
    provided to employees based on their symptoms and workplace context.
    Tips are categorized to enable relevant, workplace-appropriate suggestions.
    """
    tip_id: str
    title: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Tip content
    short_description: Optional[str] = None
    
    # Categorization
    categories: List[str] = field(default_factory=list)  # E.g., "ergonomics", "stress", "energy"
    symptom_tags: List[str] = field(default_factory=list)  # Related symptoms
    difficulty_level: str = "easy"  # "easy", "medium", "advanced"
    time_required: str = "quick"  # "quick", "short", "extended"
    location_types: List[str] = field(default_factory=lambda: ["office", "home"])
    
    # Usage tracking
    times_suggested: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    
    # Additional information
    source: Optional[str] = None
    external_links: List[str] = field(default_factory=list)
    is_verified: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the wellness tip to a dictionary for storage."""
        return {
            "tip_id": self.tip_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "title": self.title,
            "description": self.description,
            "short_description": self.short_description,
            "categories": self.categories,
            "symptom_tags": self.symptom_tags,
            "difficulty_level": self.difficulty_level,
            "time_required": self.time_required,
            "location_types": self.location_types,
            "times_suggested": self.times_suggested,
            "positive_feedback": self.positive_feedback,
            "negative_feedback": self.negative_feedback,
            "source": self.source,
            "external_links": self.external_links,
            "is_verified": self.is_verified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WellnessTip':
        """Create a WellnessTip instance from a dictionary."""
        # Convert ISO date strings to datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            
        return cls(**data)
    
    def record_suggestion(self) -> None:
        """Record that this tip has been suggested to a user."""
        self.times_suggested += 1
        self.updated_at = datetime.now()
    
    def add_feedback(self, positive: bool) -> None:
        """
        Record user feedback on this tip.
        
        Args:
            positive: Whether the feedback was positive (True) or negative (False)
        """
        if positive:
            self.positive_feedback += 1
        else:
            self.negative_feedback += 1
        self.updated_at = datetime.now()
    
    @property
    def effectiveness_score(self) -> float:
        """
        Calculate an effectiveness score based on user feedback.
        
        Returns:
            A score from 0.0 to 1.0 representing the tip's effectiveness
        """
        if self.times_suggested == 0:
            return 0.0
        
        total_feedback = self.positive_feedback + self.negative_feedback
        if total_feedback == 0:
            return 0.5  # Neutral score with no feedback
        
        return self.positive_feedback / total_feedback 