"""Leave request model for the database."""

from datetime import datetime
from typing import Optional, Dict, Any, List


class LeaveRequest:
    """
    Model representing a leave request in the database.
    
    Attributes:
        request_id: Unique identifier for the request
        employee_id: ID of the employee making the request
        request_type: Type of leave (sick_day, remote_work, flexible_hours, etc.)
        start_date: When the leave starts
        end_date: When the leave ends (optional)
        disclosure_level: How much health information is shared
        work_impact_notes: Optional notes about work impact
        status: Current status of the request (pending, approved, denied, completed)
        submitted_at: When the request was submitted
        processed_at: When the request was processed (optional)
        processed_by: Who processed the request (optional)
        notes: Additional notes or comments
    """
    
    def __init__(
        self,
        request_id: str,
        employee_id: str,
        request_type: str,
        start_date: str,
        status: str = "pending",
        end_date: Optional[str] = None,
        disclosure_level: str = "no_reason",
        work_impact_notes: Optional[str] = None,
        submitted_at: Optional[str] = None,
        processed_at: Optional[str] = None,
        processed_by: Optional[str] = None,
        notes: Optional[str] = None
    ):
        self.request_id = request_id
        self.employee_id = employee_id
        self.request_type = request_type
        self.start_date = start_date
        self.end_date = end_date
        self.disclosure_level = disclosure_level
        self.work_impact_notes = work_impact_notes
        self.status = status
        self.submitted_at = submitted_at or datetime.now().isoformat()
        self.processed_at = processed_at
        self.processed_by = processed_by
        self.notes = notes
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeaveRequest':
        """Create a LeaveRequest instance from a dictionary."""
        return cls(
            request_id=data.get('request_id'),
            employee_id=data.get('employee_id'),
            request_type=data.get('request_type'),
            start_date=data.get('start_date'),
            status=data.get('status', 'pending'),
            end_date=data.get('end_date'),
            disclosure_level=data.get('disclosure_level', 'no_reason'),
            work_impact_notes=data.get('work_impact_notes'),
            submitted_at=data.get('submitted_at'),
            processed_at=data.get('processed_at'),
            processed_by=data.get('processed_by'),
            notes=data.get('notes')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the LeaveRequest instance to a dictionary."""
        return {
            'request_id': self.request_id,
            'employee_id': self.employee_id,
            'request_type': self.request_type,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'disclosure_level': self.disclosure_level,
            'work_impact_notes': self.work_impact_notes,
            'status': self.status,
            'submitted_at': self.submitted_at,
            'processed_at': self.processed_at,
            'processed_by': self.processed_by,
            'notes': self.notes
        } 