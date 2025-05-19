"""Organization service for the Wellness Agent."""

from typing import Dict, List, Any, Optional

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.privacy.anonymizer import Anonymizer

class OrganizationService:
    """Service for organization management."""
    
    def __init__(self, firestore_client=None, anonymizer=None):
        """Initialize the organization service.
        
        Args:
            firestore_client: Optional Firestore client instance
            anonymizer: Optional anonymizer instance
        """
        self.firestore = firestore_client or FirestoreClient()
        self.anonymizer = anonymizer or Anonymizer()
    
    def create_organization(self, name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization.
        
        Args:
            name: Organization name
            settings: Organization settings
            
        Returns:
            Created organization data
        """
        return self.firestore.create_organization(name, settings)
    
    def create_policy(self, organization_id: str, name: str, description: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a wellness policy for an organization.
        
        Args:
            organization_id: Organization ID
            name: Policy name
            description: Policy description
            details: Policy details
            
        Returns:
            Created policy data
        """
        return self.firestore.create_policy(organization_id, name, description, details)
    
    def get_organization_policies(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all policies for an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            List of policy documents
        """
        return self.firestore.get_organization_policies(organization_id) 