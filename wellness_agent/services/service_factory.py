"""Service factory for the Wellness Agent."""

import os
from typing import Dict, Any, Optional, Union

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.db.bigquery import BigQueryClient
from wellness_agent.privacy.anonymizer import Anonymizer
from wellness_agent.services.symptom_service import SymptomService
from wellness_agent.services.db_service import DatabaseService
from wellness_agent.services.db.leave_request_service import LeaveRequestService
from wellness_agent.services.db.accommodation_plan_service import AccommodationPlanService

class ServiceFactory:
    """
    Factory for creating service instances.
    
    This helps manage service dependencies and configuration,
    and ensures services are properly initialized.
    """
    
    def __init__(self):
        """Initialize the service factory."""
        self._services = {}
        self._use_mock = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
        self.firestore_client = None
        self.bigquery_client = None
        self.anonymizer = None
        
        # Try to initialize shared clients
        try:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            if project_id:
                self.firestore_client = FirestoreClient(project_id)
                self.bigquery_client = BigQueryClient(project_id)
                self.anonymizer = Anonymizer()
        except Exception as e:
            print(f"Warning: Failed to initialize shared clients: {e}")
            # Will use default initialization in services
    
    def get_leave_request_service(self) -> LeaveRequestService:
        """
        Get or create a LeaveRequestService instance.
        
        Returns:
            An initialized LeaveRequestService
        """
        if "leave_request_service" not in self._services:
            self._services["leave_request_service"] = LeaveRequestService()
        return self._services["leave_request_service"]
    
    def get_accommodation_plan_service(self) -> AccommodationPlanService:
        """
        Get or create an AccommodationPlanService instance.
        
        Returns:
            An initialized AccommodationPlanService
        """
        if "accommodation_plan_service" not in self._services:
            self._services["accommodation_plan_service"] = AccommodationPlanService()
        return self._services["accommodation_plan_service"]
    
    def get_symptom_service(self):
        """
        Get or create a SymptomService instance.
        
        This is a placeholder for a service that would be implemented in a real system.
        
        Returns:
            A mock SymptomService with placeholder methods
        """
        if "symptom_service" not in self._services:
            # This would be a real service in a full implementation
            # For now, return a simple mock object with the expected methods
            self._services["symptom_service"] = type('MockSymptomService', (), {
                'track_symptom': lambda **kwargs: {
                    "status": "success",
                    "message": f"Your {kwargs.get('symptom_type')} symptom has been logged.",
                    "data": kwargs
                },
                'get_wellness_tips': lambda **kwargs: {
                    "status": "success", 
                    "message": f"Here are some tips for {kwargs.get('symptom_type')}:",
                    "tips": [
                        "Take regular breaks throughout your workday",
                        "Stay hydrated with water",
                        "Practice deep breathing when feeling stressed",
                        "Consider speaking with your healthcare provider about persistent symptoms",
                        "Remember to maintain good posture at your workstation"
                    ]
                },
                'get_symptom_history': lambda **kwargs: {
                    "status": "success",
                    "message": f"Here's your symptom history:",
                    "data": {
                        "symptom_counts": {"headache": 5, "fatigue": 3},
                        "severity_trends": []
                    }
                }
            })()
        return self._services["symptom_service"]
    
    def get_database_service(self) -> DatabaseService:
        """Get the database service instance.
        
        Returns:
            DatabaseService instance
        """
        if "db_service" not in self._services:
            self._services["db_service"] = DatabaseService(os.getenv("GOOGLE_CLOUD_PROJECT"))
        return self._services["db_service"]
    
    def reset_services(self):
        """Reset all cached service instances."""
        self._services = {}
    
    # Add similar methods for other services 