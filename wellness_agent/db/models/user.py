"""User model for the Wellness Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class User:
    """
    Model for user data in the Wellness Agent.
    
    This model stores user profiles with role-specific properties.
    Personal health data is only stored for employee users and is
    subject to privacy controls.
    """
    # Common fields for all users
    user_id: str
    role: str  # "employee", "hr_manager", or "employer"
    email: str
    organization_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Privacy settings
    privacy_level: str = "standard"  # "minimal", "standard", "detailed"
    data_sharing_consent: Dict[str, bool] = field(default_factory=lambda: {
        "anonymous_trends": True,
        "hr_notifications": False,
        "manager_access": False
    })
    
    # Role-specific fields
    # For employees only
    symptom_tracking_enabled: Optional[bool] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    last_checkin_date: Optional[datetime] = None
    
    # For HR managers only
    managed_teams: Optional[List[str]] = None
    hr_access_level: Optional[str] = None
    
    # For employers only
    leadership_level: Optional[str] = None
    dashboard_access: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the user model to a dictionary for storage."""
        result = {
            "user_id": self.user_id,
            "role": self.role,
            "email": self.email,
            "organization_id": self.organization_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "preferences": self.preferences,
            "privacy_level": self.privacy_level,
            "data_sharing_consent": self.data_sharing_consent
        }
        
        # Add role-specific fields if they exist
        if self.role == "employee":
            result.update({
                "symptom_tracking_enabled": self.symptom_tracking_enabled,
                "notification_preferences": self.notification_preferences,
                "last_checkin_date": self.last_checkin_date.isoformat() if self.last_checkin_date else None
            })
        elif self.role == "hr_manager":
            result.update({
                "managed_teams": self.managed_teams,
                "hr_access_level": self.hr_access_level
            })
        elif self.role == "employer":
            result.update({
                "leadership_level": self.leadership_level,
                "dashboard_access": self.dashboard_access
            })
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from a dictionary."""
        # Convert ISO date strings to datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if "last_checkin_date" in data and isinstance(data["last_checkin_date"], str):
            data["last_checkin_date"] = datetime.fromisoformat(data["last_checkin_date"])
            
        return cls(**data) 