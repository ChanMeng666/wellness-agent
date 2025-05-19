"""Leave request service for the Wellness Agent."""

import os
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from google.cloud import firestore

from wellness_agent.db.models.leave_request import LeaveRequest


class LeaveRequestService:
    """
    Service for managing leave requests in the database.
    
    This service handles CRUD operations for leave requests, using
    Firestore as the backend database.
    """
    
    def __init__(self):
        """Initialize the leave request service with a Firestore client."""
        self.use_mock = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
        
        if not self.use_mock:
            try:
                self.db = firestore.Client()
                self.collection = self.db.collection('leave_requests')
            except Exception as e:
                print(f"Error initializing Firestore client, falling back to mock: {e}")
                self.use_mock = True
    
    def create_leave_request(
        self,
        employee_id: str,
        request_type: str,
        start_date: str,
        end_date: Optional[str] = None,
        disclosure_level: str = "no_reason",
        work_impact_notes: Optional[str] = None
    ) -> LeaveRequest:
        """
        Create a new leave request in the database.
        
        Args:
            employee_id: ID of the employee making the request
            request_type: Type of leave (sick_day, remote_work, etc.)
            start_date: When the leave starts (YYYY-MM-DD)
            end_date: When the leave ends (YYYY-MM-DD, optional)
            disclosure_level: How much health information to share
            work_impact_notes: Optional notes about work impact
            
        Returns:
            The created LeaveRequest object
        """
        if self.use_mock:
            return self._mock_create_leave_request(
                employee_id=employee_id,
                request_type=request_type,
                start_date=start_date,
                end_date=end_date,
                disclosure_level=disclosure_level,
                work_impact_notes=work_impact_notes
            )
            
        # Generate a unique request ID
        today = datetime.now().strftime("%Y%m%d")
        request_id = f"LR-{today}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create the leave request object
        leave_request = LeaveRequest(
            request_id=request_id,
            employee_id=employee_id,
            request_type=request_type,
            start_date=start_date,
            end_date=end_date,
            disclosure_level=disclosure_level,
            work_impact_notes=work_impact_notes,
            status="pending",
            submitted_at=datetime.now().isoformat()
        )
        
        # Save to Firestore
        try:
            self.collection.document(request_id).set(leave_request.to_dict())
            return leave_request
        except Exception as e:
            print(f"Error creating leave request: {e}")
            # Fall back to mock implementation
            return self._mock_create_leave_request(
                employee_id=employee_id,
                request_type=request_type,
                start_date=start_date,
                end_date=end_date,
                disclosure_level=disclosure_level,
                work_impact_notes=work_impact_notes
            )
    
    def get_leave_request(self, request_id: str) -> Optional[LeaveRequest]:
        """
        Get a leave request by ID.
        
        Args:
            request_id: ID of the request to retrieve
            
        Returns:
            LeaveRequest object if found, None otherwise
        """
        if self.use_mock:
            return self._mock_get_leave_request(request_id)
            
        try:
            doc = self.collection.document(request_id).get()
            if doc.exists:
                return LeaveRequest.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error retrieving leave request: {e}")
            # Fall back to mock implementation
            return self._mock_get_leave_request(request_id)
    
    def get_leave_requests_by_employee(
        self, 
        employee_id: str, 
        include_completed: bool = False
    ) -> List[LeaveRequest]:
        """
        Get all leave requests for an employee.
        
        Args:
            employee_id: ID of the employee
            include_completed: Whether to include completed/past requests
            
        Returns:
            List of LeaveRequest objects
        """
        if self.use_mock:
            return self._mock_get_leave_requests_by_employee(
                employee_id=employee_id,
                include_completed=include_completed
            )
            
        try:
            query = self.collection.where('employee_id', '==', employee_id)
            
            if not include_completed:
                query = query.where('status', 'in', ['pending', 'approved'])
                
            docs = query.stream()
            
            return [LeaveRequest.from_dict(doc.to_dict()) for doc in docs]
        except Exception as e:
            print(f"Error retrieving leave requests: {e}")
            # Fall back to mock implementation
            return self._mock_get_leave_requests_by_employee(
                employee_id=employee_id,
                include_completed=include_completed
            )
    
    def update_leave_request_status(
        self, 
        request_id: str, 
        status: str,
        processed_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update the status of a leave request.
        
        Args:
            request_id: ID of the request to update
            status: New status (approved, denied, completed)
            processed_by: ID of the person processing the request
            notes: Optional notes about the status change
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_mock:
            return self._mock_update_leave_request_status(
                request_id=request_id,
                status=status,
                processed_by=processed_by,
                notes=notes
            )
            
        try:
            updates = {
                'status': status,
                'processed_at': datetime.now().isoformat()
            }
            
            if processed_by:
                updates['processed_by'] = processed_by
                
            if notes:
                updates['notes'] = notes
                
            self.collection.document(request_id).update(updates)
            return True
        except Exception as e:
            print(f"Error updating leave request status: {e}")
            # Fall back to mock implementation
            return self._mock_update_leave_request_status(
                request_id=request_id,
                status=status,
                processed_by=processed_by,
                notes=notes
            )
            
    def delete_leave_request(self, request_id: str) -> bool:
        """
        Delete a leave request.
        
        Args:
            request_id: ID of the request to delete
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_mock:
            return self._mock_delete_leave_request(request_id)
            
        try:
            self.collection.document(request_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting leave request: {e}")
            # Fall back to mock implementation
            return self._mock_delete_leave_request(request_id)
    
    # Mock implementations for local testing without Firestore
    def _mock_create_leave_request(
        self,
        employee_id: str,
        request_type: str,
        start_date: str,
        end_date: Optional[str] = None,
        disclosure_level: str = "no_reason",
        work_impact_notes: Optional[str] = None
    ) -> LeaveRequest:
        """Mock implementation for local testing."""
        # Generate a unique request ID
        today = datetime.now().strftime("%Y%m%d")
        request_id = f"LR-{today}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create the leave request object
        leave_request = LeaveRequest(
            request_id=request_id,
            employee_id=employee_id,
            request_type=request_type,
            start_date=start_date,
            end_date=end_date,
            disclosure_level=disclosure_level,
            work_impact_notes=work_impact_notes,
            status="pending",
            submitted_at=datetime.now().isoformat()
        )
        
        # Save to local JSON file for testing
        self._save_to_mock_db(leave_request)
        return leave_request
    
    def _mock_get_leave_request(self, request_id: str) -> Optional[LeaveRequest]:
        """Mock implementation to get a leave request."""
        mock_data = self._load_from_mock_db()
        if request_id in mock_data:
            return LeaveRequest.from_dict(mock_data[request_id])
        return None
    
    def _mock_get_leave_requests_by_employee(
        self, 
        employee_id: str, 
        include_completed: bool = False
    ) -> List[LeaveRequest]:
        """Mock implementation to get leave requests by employee."""
        mock_data = self._load_from_mock_db()
        
        # Filter by employee ID
        filtered_data = [
            LeaveRequest.from_dict(data) 
            for data in mock_data.values() 
            if data.get('employee_id') == employee_id
        ]
        
        # Filter by status if needed
        if not include_completed:
            filtered_data = [
                request for request in filtered_data 
                if request.status in ['pending', 'approved']
            ]
            
        return filtered_data
    
    def _mock_update_leave_request_status(
        self, 
        request_id: str, 
        status: str,
        processed_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Mock implementation to update leave request status."""
        mock_data = self._load_from_mock_db()
        
        if request_id not in mock_data:
            return False
            
        # Update the request
        request_data = mock_data[request_id]
        request_data['status'] = status
        request_data['processed_at'] = datetime.now().isoformat()
        
        if processed_by:
            request_data['processed_by'] = processed_by
            
        if notes:
            request_data['notes'] = notes
            
        # Save back to file
        mock_data[request_id] = request_data
        with open(self._get_mock_db_path(), 'w') as f:
            json.dump(mock_data, f, indent=2)
            
        return True
    
    def _mock_delete_leave_request(self, request_id: str) -> bool:
        """Mock implementation to delete a leave request."""
        mock_data = self._load_from_mock_db()
        
        if request_id not in mock_data:
            return False
            
        # Delete the request
        del mock_data[request_id]
        
        # Save back to file
        with open(self._get_mock_db_path(), 'w') as f:
            json.dump(mock_data, f, indent=2)
            
        return True
    
    def _save_to_mock_db(self, leave_request: LeaveRequest) -> None:
        """Save to a local JSON file for mock testing."""
        mock_db_path = self._get_mock_db_path()
        
        # Load existing data
        existing_data = self._load_from_mock_db()
        
        # Add or update the leave request
        existing_data[leave_request.request_id] = leave_request.to_dict()
        
        # Save back to file
        with open(mock_db_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def _load_from_mock_db(self) -> Dict[str, Any]:
        """Load data from the mock database."""
        mock_db_path = self._get_mock_db_path()
        
        if not os.path.exists(mock_db_path):
            return {}
            
        try:
            with open(mock_db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading mock database: {e}")
            return {}
    
    def _get_mock_db_path(self) -> str:
        """Get the path to the mock database file."""
        mock_db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'mock_db')
        os.makedirs(mock_db_dir, exist_ok=True)
        
        return os.path.join(mock_db_dir, 'leave_requests.json') 