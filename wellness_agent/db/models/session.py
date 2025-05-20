"""Session model for the Wellness Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class Session:
    """
    Model for conversation sessions in the Wellness Agent.
    
    This model stores conversation history and session state to enable
    continuity between interactions. It respects privacy settings and
    data retention policies.
    """
    session_id: str
    user_id: str
    user_role: str  # Employee, HR, or Employer
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    # State information
    last_interaction_time: datetime = field(default_factory=datetime.now)
    current_sub_agent: Optional[str] = None  # Which sub-agent is active
    privacy_level: str = "standard"  # Inherited from user settings
    
    # Session data
    state: Dict[str, Any] = field(default_factory=dict)  # For ADK session state
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the session model to a dictionary for storage."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "user_role": self.user_role,
            "last_interaction_time": self.last_interaction_time.isoformat(),
            "current_sub_agent": self.current_sub_agent,
            "privacy_level": self.privacy_level,
            "state": self.state,
            "conversation_history": self.conversation_history,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create a Session instance from a dictionary."""
        # Convert ISO date strings to datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if "last_interaction_time" in data and isinstance(data["last_interaction_time"], str):
            data["last_interaction_time"] = datetime.fromisoformat(data["last_interaction_time"])
            
        return cls(**data)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender (user, assistant)
            content: The content of the message
            metadata: Optional metadata about the message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
        self.last_interaction_time = datetime.now()
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """
        Update the session state.
        
        Args:
            new_state: New state information to merge with existing state
        """
        self.state.update(new_state)
        self.updated_at = datetime.now()
        
    def mark_inactive(self) -> None:
        """Mark the session as inactive."""
        self.is_active = False
        self.updated_at = datetime.now() 