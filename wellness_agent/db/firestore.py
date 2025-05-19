"""Firestore database client for the Wellness Agent."""

import os
import json
import uuid
import datetime
from typing import Dict, List, Optional, Any, Union
from google.cloud import firestore

class FirestoreClient:
    """Client for interacting with Firestore database."""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize the Firestore client.
        
        Args:
            project_id: Google Cloud project ID. If None, will use the
                GOOGLE_CLOUD_PROJECT environment variable.
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("Project ID must be provided or set as GOOGLE_CLOUD_PROJECT environment variable")
        
        self.db = firestore.Client(project=self.project_id)
    
    # ----- User Management ----- #
    
    def create_user(self, email: str, name: str, role: str) -> Dict[str, Any]:
        """Create a new user in the database.
        
        Args:
            email: User's email address
            name: User's full name
            role: User's role (employee, hr, employer)
            
        Returns:
            The created user document
        """
        user_ref = self.db.collection("users").document()
        user_data = {
            "user_id": user_ref.id,
            "email": email,
            "name": name,
            "role": role,
            "preferences": {},
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        user_ref.set(user_data)
        return user_data
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user document or None if not found
        """
        user_ref = self.db.collection("users").document(user_id)
        user = user_ref.get()
        return user.to_dict() if user.exists else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email.
        
        Args:
            email: The user's email
            
        Returns:
            The user document or None if not found
        """
        users = self.db.collection("users").where("email", "==", email).limit(1).stream()
        for user in users:
            return user.to_dict()
        return None
    
    # ----- Employee Profiles ----- #
    
    def create_employee_profile(self, user_id: str, privacy_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create an employee profile for a user.
        
        Args:
            user_id: User ID the profile belongs to
            privacy_settings: Privacy preferences
            
        Returns:
            The created profile document
        """
        profile_ref = self.db.collection("employee_profiles").document()
        profile_data = {
            "profile_id": profile_ref.id,
            "user_id": user_id,
            "privacy_settings": privacy_settings,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        profile_ref.set(profile_data)
        return profile_data
    
    def get_employee_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get an employee profile by ID.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            The profile document or None if not found
        """
        profile_ref = self.db.collection("employee_profiles").document(profile_id)
        profile = profile_ref.get()
        return profile.to_dict() if profile.exists else None
    
    def get_employee_profile_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get an employee profile by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            The profile document or None if not found
        """
        profiles = self.db.collection("employee_profiles").where("user_id", "==", user_id).limit(1).stream()
        for profile in profiles:
            return profile.to_dict()
        return None
    
    # ----- Symptom Tracking ----- #
    
    def log_symptom(self, profile_id: str, symptom_data: Dict[str, Any], 
                   severity_level: int, notes: Optional[str] = None) -> Dict[str, Any]:
        """Log a symptom for an employee.
        
        Args:
            profile_id: Employee profile ID
            symptom_data: Symptom information
            severity_level: Severity from 1-10
            notes: Optional notes
            
        Returns:
            The created symptom log document
        """
        log_ref = self.db.collection("symptom_logs").document()
        log_data = {
            "log_id": log_ref.id,
            "profile_id": profile_id,
            "date": firestore.SERVER_TIMESTAMP,
            "symptom_data": symptom_data,
            "severity_level": severity_level,
            "notes": notes or ""
        }
        
        log_ref.set(log_data)
        return log_data
    
    def get_symptom_history(self, profile_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get symptom history for an employee.
        
        Args:
            profile_id: Employee profile ID
            days: Number of days to look back
            
        Returns:
            List of symptom log documents
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        logs = self.db.collection("symptom_logs") \
            .where("profile_id", "==", profile_id) \
            .where("date", ">=", cutoff_date) \
            .order_by("date", direction=firestore.Query.DESCENDING) \
            .stream()
        
        return [log.to_dict() for log in logs]
    
    # ----- Accommodation Requests ----- #
    
    def create_accommodation_request(
        self, profile_id: str, request_type: str, start_date: str,
        end_date: Optional[str] = None, notes: Optional[str] = None,
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
        request_ref = self.db.collection("accommodation_requests").document()
        request_data = {
            "request_id": request_ref.id,
            "profile_id": profile_id,
            "type": request_type,
            "status": "pending",
            "request_date": firestore.SERVER_TIMESTAMP,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes or "",
            "anonymity_level": anonymity_level
        }
        
        request_ref.set(request_data)
        return request_data
    
    def update_accommodation_status(self, request_id: str, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update the status of an accommodation request.
        
        Args:
            request_id: Request ID
            status: New status (pending, approved, denied)
            notes: Optional notes
            
        Returns:
            The updated request document
        """
        request_ref = self.db.collection("accommodation_requests").document(request_id)
        request = request_ref.get()
        
        if not request.exists:
            raise ValueError(f"Accommodation request {request_id} not found")
        
        update_data = {
            "status": status,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        if notes:
            update_data["status_notes"] = notes
        
        request_ref.update(update_data)
        
        # Get the updated document
        updated_request = request_ref.get()
        return updated_request.to_dict()
    
    def get_pending_accommodation_requests(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all pending accommodation requests for an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            List of pending request documents
        """
        # This requires the employee profiles to be linked to organizations
        # For now, we'll get all pending requests and filter them later
        requests = self.db.collection("accommodation_requests") \
            .where("status", "==", "pending") \
            .order_by("request_date") \
            .stream()
        
        return [request.to_dict() for request in requests]
    
    # ----- Organizations and Policies ----- #
    
    def create_organization(self, name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization.
        
        Args:
            name: Organization name
            settings: Organization settings
            
        Returns:
            The created organization document
        """
        org_ref = self.db.collection("organizations").document()
        org_data = {
            "organization_id": org_ref.id,
            "name": name,
            "settings": settings,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        org_ref.set(org_data)
        return org_data
    
    def create_policy(
        self, organization_id: str, name: str, description: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new company policy.
        
        Args:
            organization_id: Organization ID
            name: Policy name
            description: Policy description
            details: Policy details
            
        Returns:
            The created policy document
        """
        policy_ref = self.db.collection("company_policies").document()
        policy_data = {
            "policy_id": policy_ref.id,
            "organization_id": organization_id,
            "name": name,
            "description": description,
            "details": details,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        policy_ref.set(policy_data)
        return policy_data
    
    def get_organization_policies(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all policies for an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            List of policy documents
        """
        policies = self.db.collection("company_policies") \
            .where("organization_id", "==", organization_id) \
            .order_by("updated_at", direction=firestore.Query.DESCENDING) \
            .stream()
        
        return [policy.to_dict() for policy in policies] 