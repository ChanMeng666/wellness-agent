"""Accommodation plan service for the Wellness Agent."""

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from google.cloud import firestore

from wellness_agent.db.models.accommodation_plan import AccommodationPlan


class AccommodationPlanService:
    """
    Service for managing accommodation plans in the database.
    
    This service handles CRUD operations for accommodation plans, using
    Firestore as the backend database.
    """
    
    def __init__(self):
        """Initialize the accommodation plan service with a Firestore client."""
        self.use_mock = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
        
        if not self.use_mock:
            try:
                self.db = firestore.Client()
                self.collection = self.db.collection('accommodation_plans')
            except Exception as e:
                print(f"Error initializing Firestore client, falling back to mock: {e}")
                self.use_mock = True
    
    def create_accommodation_plan(
        self,
        employee_id: str,
        accommodation_types: List[str],
        duration: str,
        frequency: str,
        specific_days: Optional[List[str]] = None,
        functional_limitations: Optional[List[str]] = None,
        privacy_level: str = "minimum",
        manager_notes: Optional[str] = None
    ) -> AccommodationPlan:
        """
        Create a new accommodation plan in the database.
        
        Args:
            employee_id: ID of the employee the plan is for
            accommodation_types: Types of accommodations requested
            duration: How long the accommodations are needed
            frequency: How often the accommodations are needed
            specific_days: Days of the week for the accommodation
            functional_limitations: Descriptions of work-related limitations
            privacy_level: Level of privacy for the plan
            manager_notes: Notes visible to the manager
            
        Returns:
            The created AccommodationPlan object
        """
        if self.use_mock:
            return self._mock_create_accommodation_plan(
                employee_id=employee_id,
                accommodation_types=accommodation_types,
                duration=duration,
                frequency=frequency,
                specific_days=specific_days,
                functional_limitations=functional_limitations,
                privacy_level=privacy_level,
                manager_notes=manager_notes
            )
            
        # Generate a unique plan ID
        today = datetime.now().strftime("%Y%m%d")
        plan_id = f"AP-{today}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate review date (default to 90 days from now)
        review_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        
        # Create the accommodation plan object
        plan = AccommodationPlan(
            plan_id=plan_id,
            employee_id=employee_id,
            accommodation_types=accommodation_types,
            duration=duration,
            frequency=frequency,
            specific_days=specific_days,
            functional_limitations=functional_limitations,
            privacy_level=privacy_level,
            manager_notes=manager_notes,
            status="pending",
            created_at=datetime.now().isoformat(),
            review_date=review_date
        )
        
        # Save to Firestore
        try:
            self.collection.document(plan_id).set(plan.to_dict())
            return plan
        except Exception as e:
            print(f"Error creating accommodation plan: {e}")
            # Fall back to mock implementation
            return self._mock_create_accommodation_plan(
                employee_id=employee_id,
                accommodation_types=accommodation_types,
                duration=duration,
                frequency=frequency,
                specific_days=specific_days,
                functional_limitations=functional_limitations,
                privacy_level=privacy_level,
                manager_notes=manager_notes
            )
    
    def get_accommodation_plan(self, plan_id: str) -> Optional[AccommodationPlan]:
        """
        Get an accommodation plan by ID.
        
        Args:
            plan_id: ID of the plan to retrieve
            
        Returns:
            AccommodationPlan object if found, None otherwise
        """
        if self.use_mock:
            return self._mock_get_accommodation_plan(plan_id)
            
        try:
            doc = self.collection.document(plan_id).get()
            if doc.exists:
                return AccommodationPlan.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error retrieving accommodation plan: {e}")
            # Fall back to mock implementation
            return self._mock_get_accommodation_plan(plan_id)
    
    def get_accommodation_plans_by_employee(
        self, 
        employee_id: str,
        active_only: bool = True
    ) -> List[AccommodationPlan]:
        """
        Get all accommodation plans for an employee.
        
        Args:
            employee_id: ID of the employee
            active_only: Whether to include only active plans
            
        Returns:
            List of AccommodationPlan objects
        """
        if self.use_mock:
            return self._mock_get_accommodation_plans_by_employee(
                employee_id=employee_id,
                active_only=active_only
            )
            
        try:
            query = self.collection.where('employee_id', '==', employee_id)
            
            if active_only:
                query = query.where('status', 'in', ['pending', 'approved'])
                
            docs = query.stream()
            
            return [AccommodationPlan.from_dict(doc.to_dict()) for doc in docs]
        except Exception as e:
            print(f"Error retrieving accommodation plans: {e}")
            # Fall back to mock implementation
            return self._mock_get_accommodation_plans_by_employee(
                employee_id=employee_id,
                active_only=active_only
            )
    
    def update_accommodation_plan_status(
        self, 
        plan_id: str, 
        status: str,
        approved_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update the status of an accommodation plan.
        
        Args:
            plan_id: ID of the plan to update
            status: New status (approved, denied, completed)
            approved_by: ID of the person approving the plan
            notes: Optional notes about the status change
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_mock:
            return self._mock_update_accommodation_plan_status(
                plan_id=plan_id,
                status=status,
                approved_by=approved_by,
                notes=notes
            )
            
        try:
            updates = {
                'status': status
            }
            
            if status == "approved":
                updates['approved_at'] = datetime.now().isoformat()
                if approved_by:
                    updates['approved_by'] = approved_by
                
            if notes:
                updates['notes'] = notes
                
            self.collection.document(plan_id).update(updates)
            return True
        except Exception as e:
            print(f"Error updating accommodation plan status: {e}")
            # Fall back to mock implementation
            return self._mock_update_accommodation_plan_status(
                plan_id=plan_id,
                status=status,
                approved_by=approved_by,
                notes=notes
            )
            
    def delete_accommodation_plan(self, plan_id: str) -> bool:
        """
        Delete an accommodation plan.
        
        Args:
            plan_id: ID of the plan to delete
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_mock:
            return self._mock_delete_accommodation_plan(plan_id)
            
        try:
            self.collection.document(plan_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting accommodation plan: {e}")
            # Fall back to mock implementation
            return self._mock_delete_accommodation_plan(plan_id)
    
    # Mock implementations for local testing without Firestore
    def _mock_create_accommodation_plan(
        self,
        employee_id: str,
        accommodation_types: List[str],
        duration: str,
        frequency: str,
        specific_days: Optional[List[str]] = None,
        functional_limitations: Optional[List[str]] = None,
        privacy_level: str = "minimum",
        manager_notes: Optional[str] = None
    ) -> AccommodationPlan:
        """Mock implementation for local testing."""
        # Generate a unique plan ID
        today = datetime.now().strftime("%Y%m%d")
        plan_id = f"AP-{today}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate review date (default to 90 days from now)
        review_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        
        # Create the accommodation plan object
        plan = AccommodationPlan(
            plan_id=plan_id,
            employee_id=employee_id,
            accommodation_types=accommodation_types,
            duration=duration,
            frequency=frequency,
            specific_days=specific_days,
            functional_limitations=functional_limitations,
            privacy_level=privacy_level,
            manager_notes=manager_notes,
            status="pending",
            created_at=datetime.now().isoformat(),
            review_date=review_date
        )
        
        # Save to local JSON file for testing
        self._save_to_mock_db(plan)
        return plan
    
    def _mock_get_accommodation_plan(self, plan_id: str) -> Optional[AccommodationPlan]:
        """Mock implementation to get an accommodation plan."""
        mock_data = self._load_from_mock_db()
        if plan_id in mock_data:
            return AccommodationPlan.from_dict(mock_data[plan_id])
        return None
    
    def _mock_get_accommodation_plans_by_employee(
        self, 
        employee_id: str,
        active_only: bool = True
    ) -> List[AccommodationPlan]:
        """Mock implementation to get accommodation plans by employee."""
        mock_data = self._load_from_mock_db()
        
        # Filter by employee ID
        filtered_data = [
            AccommodationPlan.from_dict(data) 
            for data in mock_data.values() 
            if data.get('employee_id') == employee_id
        ]
        
        # Filter by status if needed
        if active_only:
            filtered_data = [
                plan for plan in filtered_data 
                if plan.status in ['pending', 'approved']
            ]
            
        return filtered_data
    
    def _mock_update_accommodation_plan_status(
        self, 
        plan_id: str, 
        status: str,
        approved_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Mock implementation to update accommodation plan status."""
        mock_data = self._load_from_mock_db()
        
        if plan_id not in mock_data:
            return False
            
        # Update the plan
        plan_data = mock_data[plan_id]
        plan_data['status'] = status
        
        if status == "approved":
            plan_data['approved_at'] = datetime.now().isoformat()
            if approved_by:
                plan_data['approved_by'] = approved_by
            
        if notes:
            plan_data['notes'] = notes
            
        # Save back to file
        mock_data[plan_id] = plan_data
        with open(self._get_mock_db_path(), 'w') as f:
            json.dump(mock_data, f, indent=2)
            
        return True
    
    def _mock_delete_accommodation_plan(self, plan_id: str) -> bool:
        """Mock implementation to delete an accommodation plan."""
        mock_data = self._load_from_mock_db()
        
        if plan_id not in mock_data:
            return False
            
        # Delete the plan
        del mock_data[plan_id]
        
        # Save back to file
        with open(self._get_mock_db_path(), 'w') as f:
            json.dump(mock_data, f, indent=2)
            
        return True
    
    def _save_to_mock_db(self, plan: AccommodationPlan) -> None:
        """Save to a local JSON file for mock testing."""
        mock_db_path = self._get_mock_db_path()
        
        # Load existing data
        existing_data = self._load_from_mock_db()
        
        # Add or update the accommodation plan
        existing_data[plan.plan_id] = plan.to_dict()
        
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
        
        return os.path.join(mock_db_dir, 'accommodation_plans.json') 