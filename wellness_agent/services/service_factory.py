"""Service factory for the Wellness Agent."""

import os
from typing import Dict, Any, Optional, Union

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.db.bigquery import BigQueryClient
from wellness_agent.privacy.anonymizer import Anonymizer
from wellness_agent.services.symptom_service import SymptomService

class ServiceFactory:
    """Factory for creating and caching service instances."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the factory and shared resources."""
        # Initialize database clients
        self.firestore_client = None
        self.bigquery_client = None
        self.anonymizer = None
        
        # Cache for services
        self.services = {}
        
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
    
    def get_symptom_service(self) -> SymptomService:
        """Get or create a SymptomService instance.
        
        Returns:
            A SymptomService instance
        """
        if "symptom_service" not in self.services:
            self.services["symptom_service"] = SymptomService(
                firestore_client=self.firestore_client,
                bigquery_client=self.bigquery_client,
                anonymizer=self.anonymizer
            )
        return self.services["symptom_service"]
    
    # Add similar methods for other services 