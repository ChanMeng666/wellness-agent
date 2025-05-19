"""Accommodation service for the Wellness Agent."""

import datetime
from typing import Dict, List, Optional, Any, Union

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.db.bigquery import BigQueryClient
from wellness_agent.privacy.anonymizer import Anonymizer

class AccommodationService:
    """Service for managing accommodation requests."""
    
    def __init__(
        self,
        firestore_client: Optional[FirestoreClient] = None,
        bigquery_client: Optional[BigQueryClient] = None,
        anonymizer: Optional[Anonymizer] = None
    ):
        """Initialize the accommodation service.
        
        Args:
            firestore_client: Firestore client for data storage
            bigquery_client: BigQuery client for analytics
            anonymizer: Data anonymizer
        """
        self.db = firestore_client or FirestoreClient()
        self.analytics_db = bigquery_client or BigQueryClient()
        self.anonymizer = anonymizer or Anonymizer()
    
    def create_accommodation_request(
        self,
        profile_id: str,
        request_type: str,
        start_date: str,
        end_date: Optional[str] = None,
        notes: Optional[str] = None,
        anonymity_level: str = "anonymous_only"
    ) -> Dict[str, Any]:
        """Create an accommodation request.
        
        Args:
            profile_id: Employee profile ID
            request_type: Type of accommodation
            start_date: Start date for accommodation
            end_date: Optional end date
            notes: Optional notes
            anonymity_level: Privacy level for the request
            
        Returns:
            The created request document
        """
        # Get the employee profile to check privacy settings
        profile = self.db.get_employee_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        # Create the accommodation request in Firestore
        request_data = self.db.create_accommodation_request(
            profile_id=profile_id,
            request_type=request_type,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            anonymity_level=anonymity_level
        )
        
        return {
            "status": "success",
            "message": f"Your accommodation request has been submitted with {anonymity_level} privacy level.",
            "data": request_data
        }
    
    def update_accommodation_status(
        self,
        request_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update the status of an accommodation request.
        
        Args:
            request_id: Request ID
            status: New status (pending, approved, denied)
            notes: Optional notes
            
        Returns:
            The updated request document
        """
        try:
            # Update the status in Firestore
            updated_data = self.db.update_accommodation_status(
                request_id=request_id,
                status=status,
                notes=notes
            )
            
            return {
                "status": "success",
                "message": f"Accommodation request status updated to {status}.",
                "data": updated_data
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_pending_accommodation_requests(
        self,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get all pending accommodation requests for an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            List of pending request documents
        """
        # Get pending requests from Firestore
        requests = self.db.get_pending_accommodation_requests(organization_id)
        
        # Apply privacy filters based on anonymity levels
        for request in requests:
            anonymity_level = request.get("anonymity_level", "anonymous_only")
            
            if anonymity_level == "anonymous_only":
                # Remove identifying information
                if "profile_id" in request:
                    request["profile_id"] = "anonymous"
                if "notes" in request:
                    request["notes"] = "Details redacted for privacy"
        
        return {
            "status": "success",
            "message": f"Retrieved {len(requests)} pending accommodation requests.",
            "data": requests
        }
    
    def get_accommodation_trends(
        self,
        organization_id: str,
        time_period: str = "month"
    ) -> Dict[str, Any]:
        """Get anonymized accommodation request trends for an organization.
        
        Args:
            organization_id: Organization ID
            time_period: Time period to analyze
            
        Returns:
            Anonymized trend data
        """
        # Convert time period to days
        days_map = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365
        }
        days = days_map.get(time_period, 30)
        
        # In a real implementation, this would:
        # 1. Fetch raw data from Firestore
        # 2. Apply anonymization
        # 3. Store in BigQuery for analytics
        
        # For demonstration, we'll return simulated data
        
        return {
            "status": "success",
            "message": f"Generated anonymized accommodation trends for {time_period}",
            "data": {
                "request_type_counts": {
                    "flexible_schedule": 12,
                    "remote_work": 18,
                    "physical_modification": 5,
                    "leave_request": 8
                },
                "status_counts": {
                    "pending": 14,
                    "approved": 22,
                    "denied": 7
                },
                "time_trends": {
                    "weekly": [
                        {"week": "2023-01-01", "count": 8},
                        {"week": "2023-01-08", "count": 11},
                        {"week": "2023-01-15", "count": 9},
                        {"week": "2023-01-22", "count": 15}
                    ]
                },
                "employee_count": 42,
                "time_period": time_period
            }
        } 