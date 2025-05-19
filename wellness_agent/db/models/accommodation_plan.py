"""Accommodation plan model for the database."""

from datetime import datetime
from typing import Optional, Dict, Any, List


class AccommodationPlan:
    """
    Model representing an accommodation plan in the database.
    
    Attributes:
        plan_id: Unique identifier for the plan
        employee_id: ID of the employee the plan is for
        accommodation_types: Types of accommodations requested
        duration: How long the accommodations are needed
        frequency: How often the accommodations are needed
        specific_days: Days of the week for the accommodation (if applicable)
        functional_limitations: Descriptions of work-related limitations
        privacy_level: Level of privacy for the plan
        manager_notes: Notes visible to the manager
        status: Current status of the plan
        created_at: When the plan was created
        review_date: When the plan should be reviewed
        approved_at: When the plan was approved (if applicable)
        approved_by: Who approved the plan (if applicable)
        notes: Additional notes or comments
    """
    
    def __init__(
        self,
        plan_id: str,
        employee_id: str,
        accommodation_types: List[str],
        duration: str,
        frequency: str,
        status: str = "pending",
        specific_days: Optional[List[str]] = None,
        functional_limitations: Optional[List[str]] = None,
        privacy_level: str = "minimum",
        manager_notes: Optional[str] = None,
        created_at: Optional[str] = None,
        review_date: Optional[str] = None,
        approved_at: Optional[str] = None,
        approved_by: Optional[str] = None,
        notes: Optional[str] = None
    ):
        self.plan_id = plan_id
        self.employee_id = employee_id
        self.accommodation_types = accommodation_types
        self.duration = duration
        self.frequency = frequency
        self.specific_days = specific_days or []
        self.functional_limitations = functional_limitations or []
        self.privacy_level = privacy_level
        self.manager_notes = manager_notes
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.review_date = review_date
        self.approved_at = approved_at
        self.approved_by = approved_by
        self.notes = notes
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccommodationPlan':
        """Create an AccommodationPlan instance from a dictionary."""
        return cls(
            plan_id=data.get('plan_id'),
            employee_id=data.get('employee_id'),
            accommodation_types=data.get('accommodation_types', []),
            duration=data.get('duration'),
            frequency=data.get('frequency'),
            status=data.get('status', 'pending'),
            specific_days=data.get('specific_days'),
            functional_limitations=data.get('functional_limitations'),
            privacy_level=data.get('privacy_level', 'minimum'),
            manager_notes=data.get('manager_notes'),
            created_at=data.get('created_at'),
            review_date=data.get('review_date'),
            approved_at=data.get('approved_at'),
            approved_by=data.get('approved_by'),
            notes=data.get('notes')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AccommodationPlan instance to a dictionary."""
        return {
            'plan_id': self.plan_id,
            'employee_id': self.employee_id,
            'accommodation_types': self.accommodation_types,
            'duration': self.duration,
            'frequency': self.frequency,
            'specific_days': self.specific_days,
            'functional_limitations': self.functional_limitations,
            'privacy_level': self.privacy_level,
            'manager_notes': self.manager_notes,
            'status': self.status,
            'created_at': self.created_at,
            'review_date': self.review_date,
            'approved_at': self.approved_at,
            'approved_by': self.approved_by,
            'notes': self.notes
        } 