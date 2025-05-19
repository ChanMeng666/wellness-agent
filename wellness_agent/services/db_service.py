"""Database service for the Wellness Agent."""

import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.db.bigquery import BigQueryClient
from wellness_agent.privacy.anonymizer import Anonymizer

class DatabaseService:
    """Service to handle all database operations."""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize the database service.
        
        Args:
            project_id: Google Cloud project ID.
        """
        self.firestore = FirestoreClient(project_id)
        self.bigquery = BigQueryClient(project_id)
        self.anonymizer = Anonymizer()
        
    # ---- User Management ----
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID."""
        return self.firestore.get_user(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email."""
        return self.firestore.get_user_by_email(email)
    
    def create_user(self, email: str, name: str, role: str) -> Dict[str, Any]:
        """Create a new user."""
        return self.firestore.create_user(email, name, role)
    
    # ---- Employee Profiles ----
    
    def get_employee_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get an employee profile by ID."""
        return self.firestore.get_employee_profile(profile_id)
    
    def get_employee_profile_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get an employee profile by user ID."""
        return self.firestore.get_employee_profile_by_user(user_id)
    
    def create_employee_profile(self, user_id: str, privacy_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create an employee profile."""
        return self.firestore.create_employee_profile(user_id, privacy_settings)
    
    # ---- Symptom Tracking ----
    
    def log_symptom(self, profile_id: str, symptom_data: Dict[str, Any], 
                    severity_level: int, notes: Optional[str] = None) -> Dict[str, Any]:
        """Log a symptom for an employee."""
        return self.firestore.log_symptom(profile_id, symptom_data, severity_level, notes)
    
    def get_symptom_history(self, profile_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get symptom history for an employee."""
        return self.firestore.get_symptom_history(profile_id, days)
    
    # ---- Accommodation Requests ----
    
    def create_accommodation_request(
        self, profile_id: str, request_type: str, start_date: str,
        end_date: Optional[str] = None, notes: Optional[str] = None,
        anonymity_level: str = "anonymous_only"
    ) -> Dict[str, Any]:
        """Create an accommodation request."""
        return self.firestore.create_accommodation_request(
            profile_id, request_type, start_date, end_date, notes, anonymity_level
        )
    
    def update_accommodation_status(self, request_id: str, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update the status of an accommodation request."""
        return self.firestore.update_accommodation_status(request_id, status, notes)
    
    def get_pending_accommodation_requests(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all pending accommodation requests for an organization."""
        return self.firestore.get_pending_accommodation_requests(organization_id)
    
    # ---- Organization Management ----
    
    def create_organization(self, name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization."""
        return self.firestore.create_organization(name, settings)
    
    def create_policy(self, organization_id: str, name: str, description: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a wellness policy for an organization."""
        return self.firestore.create_policy(organization_id, name, description, details)
    
    def get_organization_policies(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all policies for an organization."""
        return self.firestore.get_organization_policies(organization_id)
    
    # ---- Analytics ----
    
    def generate_symptom_metrics(
        self, organization_id: str, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> Dict[str, Any]:
        """Generate anonymized symptom metrics for an organization.
        
        This method:
        1. Retrieves raw symptom data from Firestore
        2. Anonymizes the data using privacy rules
        3. Stores the anonymized metrics in BigQuery
        4. Returns the aggregated metrics
        """
        # Get all users in the organization (in a real implementation, we'd have a more efficient way)
        # For now, we'll simulate this with sample data
        raw_data = []  # This would come from Firestore in a real implementation
        
        # Count employees
        employee_count = len(set(item.get("profile_id") for item in raw_data))
        
        # Only proceed if we have enough data for privacy
        if employee_count < 5:
            return {"error": "Not enough data for privacy-preserving analysis"}
        
        # Generate anonymized metrics
        return self.bigquery.generate_anonymized_metric(
            organization_id=organization_id,
            metric_type="symptom_frequency",
            raw_data=raw_data,
            employee_count=employee_count,
            period_start=start_date,
            period_end=end_date
        )
    
    def generate_accommodation_metrics(
        self, organization_id: str, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> Dict[str, Any]:
        """Generate anonymized accommodation request metrics for an organization."""
        # Similar to symptom metrics, but for accommodation requests
        raw_data = []  # This would come from Firestore in a real implementation
        
        # Count employees
        employee_count = len(set(item.get("profile_id") for item in raw_data))
        
        # Only proceed if we have enough data for privacy
        if employee_count < 5:
            return {"error": "Not enough data for privacy-preserving analysis"}
        
        # Generate anonymized metrics
        return self.bigquery.generate_anonymized_metric(
            organization_id=organization_id,
            metric_type="accommodation_requests",
            raw_data=raw_data,
            employee_count=employee_count,
            period_start=start_date,
            period_end=end_date
        )
    
    def get_wellness_trend(
        self, organization_id: str, metric_type: str, 
        start_date: datetime.datetime, end_date: Optional[datetime.datetime] = None,
        min_employee_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Get trend data for an organization with privacy protections."""
        return self.bigquery.get_trend_data(
            organization_id=organization_id,
            metric_type=metric_type,
            start_date=start_date,
            end_date=end_date,
            min_employee_count=min_employee_count
        )
    
    # ---- Privacy Functions ----
    
    def anonymize_data_for_hr(self, data: List[Dict[str, Any]], data_type: str, user_privacy_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize data for HR viewing."""
        if data_type == "symptoms":
            _, anonymized = self.anonymizer.anonymize_symptom_data(data, user_privacy_settings)
            return anonymized
        elif data_type == "accommodations":
            _, anonymized = self.anonymizer.anonymize_accommodation_data(data, user_privacy_settings)
            return anonymized
        elif data_type == "wellbeing":
            _, anonymized = self.anonymizer.anonymize_wellbeing_data(data, user_privacy_settings)
            return anonymized
        else:
            raise ValueError(f"Unknown data type: {data_type}") 