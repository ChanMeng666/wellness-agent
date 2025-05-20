"""Memory database service for the Wellness Agent."""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from google.cloud import firestore

from wellness_agent.db.models import (
    User,
    Session,
    SymptomsLog,
    WellnessTip,
    LeaveRequest
)


class MemoryService:
    """
    Service for managing memory persistence in the Wellness Agent.
    
    This service handles database operations for the memory system,
    including storing and retrieving user profiles, sessions, and logs.
    It supports both Firestore and a mock implementation.
    """
    
    def __init__(self):
        """Initialize the memory service."""
        self.use_mock = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
        
        if not self.use_mock:
            # Initialize Firestore client
            self.db = firestore.Client()
        else:
            # Initialize mock storage
            self.mock_data = {
                "users": {},
                "sessions": {},
                "symptom_logs": {},
                "wellness_tips": {},
                "leave_requests": {}
            }
            self._load_mock_data()
    
    def _load_mock_data(self) -> None:
        """Initialize the mock data store with empty collections."""
        import uuid
        from datetime import datetime
        from wellness_agent.db.models.user import User
        from wellness_agent.db.models.session import Session
        from wellness_agent.db.models.symptoms_log import SymptomsLog
        from wellness_agent.db.models.wellness_tip import WellnessTip
        
        # Initialize collections
        self.mock_data = {
            "users": {},
            "sessions": {},
            "symptom_logs": {},
            "wellness_tips": {}
        }
        
        try:
            # Create a demo user for the default employee role
            demo_employee = User(
                user_id="demo_profile_123",
                role="employee",
                email="demo.employee@example.com",
                organization_id="demo_org_456",
                privacy_level="standard"
            )
            
            # Create a demo user for the HR manager role
            demo_hr_manager = User(
                user_id="demo_hr_manager_789",
                role="hr_manager",
                email="hr.manager@example.com",
                organization_id="demo_org_456",
                privacy_level="standard"
            )
            
            # Create a demo user for the employer role
            demo_employer = User(
                user_id="demo_employer_101",
                role="employer",
                email="employer.admin@example.com",
                organization_id="demo_org_456",
                privacy_level="standard"
            )
            
            # Store users with their user_id as the key
            self.mock_data["users"][demo_employee.user_id] = demo_employee.to_dict()
            self.mock_data["users"][demo_hr_manager.user_id] = demo_hr_manager.to_dict()
            self.mock_data["users"][demo_employer.user_id] = demo_employer.to_dict()
            
            # Create a sample session (as a dictionary, not as a Session object)
            sample_session = Session(
                session_id=str(uuid.uuid4()),
                user_id=demo_employee.user_id,
                user_role=demo_employee.role,
                is_active=True
            )
            self.mock_data["sessions"][sample_session.session_id] = sample_session.to_dict()
            
            # Create a sample symptom log (as a dictionary)
            sample_log = SymptomsLog(
                log_id=str(uuid.uuid4()),
                user_id=demo_employee.user_id,
                timestamp=datetime.now(),
                symptom_rating=3,
                symptom_text="Mild headache",
                energy_level=4,
                stress_level=3,
                privacy_level="standard"
            )
            self.mock_data["symptom_logs"][sample_log.log_id] = sample_log.to_dict()
        except Exception as e:
            print(f"Error initializing mock data: {str(e)}")
    
    # User methods
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            The user if found, None otherwise
        """
        if self.use_mock:
            user_dict = self.mock_data["users"].get(user_id)
            return User.from_dict(user_dict) if user_dict else None
        else:
            doc_ref = self.db.collection("users").document(user_id)
            doc = doc_ref.get()
            return User.from_dict(doc.to_dict()) if doc.exists else None
    
    def save_user(self, user: User) -> bool:
        """
        Save a user to the database.
        
        Args:
            user: The user to save
            
        Returns:
            True if successful, False otherwise
        """
        user_dict = user.to_dict()
        
        try:
            if self.use_mock:
                self.mock_data["users"][user.user_id] = user
                return True
            else:
                self.db.collection("users").document(user.user_id).set(user_dict)
                return True
        except Exception as e:
            print(f"Error saving user: {str(e)}")
            return False
    
    # Session methods
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The session if found, None otherwise
        """
        if self.use_mock:
            session = self.mock_data["sessions"].get(session_id)
            # Check if the object is already a Session instance
            if isinstance(session, Session):
                return session
            # Otherwise convert from dictionary
            return Session.from_dict(session) if session else None
        else:
            doc_ref = self.db.collection("sessions").document(session_id)
            doc = doc_ref.get()
            return Session.from_dict(doc.to_dict()) if doc.exists else None
    
    def save_session(self, session: Session) -> bool:
        """
        Save a session to the database.
        
        Args:
            session: The session to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_mock:
                # Store the session object directly
                self.mock_data["sessions"][session.session_id] = session
                return True
            else:
                # Convert to dictionary for Firestore
                session_dict = session.to_dict()
                self.db.collection("sessions").document(session.session_id).set(session_dict)
                return True
        except Exception as e:
            print(f"Error saving session: {str(e)}")
            return False
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[Session]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: The ID of the user
            active_only: Whether to only return active sessions
            
        Returns:
            A list of sessions for the user
        """
        if self.use_mock:
            sessions = []
            for session_id, session in self.mock_data["sessions"].items():
                # Check if it's already a Session object
                if isinstance(session, Session):
                    if session.user_id == user_id:
                        if not active_only or session.is_active:
                            sessions.append(session)
                else:
                    # It's a dictionary
                    if session.get('user_id') == user_id:
                        if not active_only or session.get('is_active', True):
                            sessions.append(Session.from_dict(session))
            return sessions
        else:
            query = self.db.collection("sessions").where("user_id", "==", user_id)
            if active_only:
                query = query.where("is_active", "==", True)
            
            sessions = []
            for doc in query.stream():
                sessions.append(Session.from_dict(doc.to_dict()))
            return sessions
    
    # Symptom Log methods
    def save_symptom_log(self, log: SymptomsLog) -> bool:
        """
        Save a symptom log to the database.
        
        Args:
            log: The symptom log to save
            
        Returns:
            True if successful, False otherwise
        """
        log_dict = log.to_dict()
        
        try:
            if self.use_mock:
                self.mock_data["symptom_logs"][log.log_id] = log
                return True
            else:
                self.db.collection("symptom_logs").document(log.log_id).set(log_dict)
                return True
        except Exception as e:
            print(f"Error saving symptom log: {str(e)}")
            return False
    
    def get_user_symptom_logs(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SymptomsLog]:
        """
        Get symptom logs for a user.
        
        Args:
            user_id: The ID of the user
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of logs to return
            
        Returns:
            A list of symptom logs for the user
        """
        if self.use_mock:
            logs = []
            for log in self.mock_data["symptom_logs"].values():
                if log.user_id == user_id:
                    if start_date and log.timestamp < start_date:
                        continue
                    if end_date and log.timestamp > end_date:
                        continue
                    logs.append(log)
                    if len(logs) >= limit:
                        break
            return logs
        else:
            query = self.db.collection("symptom_logs").where("user_id", "==", user_id)
            
            if start_date:
                query = query.where("timestamp", ">=", start_date.isoformat())
            if end_date:
                query = query.where("timestamp", "<=", end_date.isoformat())
            
            query = query.limit(limit)
            
            logs = []
            for doc in query.stream():
                logs.append(SymptomsLog.from_dict(doc.to_dict()))
            return logs
    
    # Wellness Tip methods
    def get_wellness_tip(self, tip_id: str) -> Optional[WellnessTip]:
        """
        Get a wellness tip by ID.
        
        Args:
            tip_id: The ID of the tip to retrieve
            
        Returns:
            The wellness tip if found, None otherwise
        """
        if self.use_mock:
            tip_dict = self.mock_data["wellness_tips"].get(tip_id)
            return WellnessTip.from_dict(tip_dict) if tip_dict else None
        else:
            doc_ref = self.db.collection("wellness_tips").document(tip_id)
            doc = doc_ref.get()
            return WellnessTip.from_dict(doc.to_dict()) if doc.exists else None
    
    def get_wellness_tips_by_category(
        self, 
        categories: List[str],
        symptom_tags: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[WellnessTip]:
        """
        Get wellness tips by category and optional symptom tags.
        
        Args:
            categories: List of categories to filter by
            symptom_tags: Optional list of symptom tags to filter by
            limit: Maximum number of tips to return
            
        Returns:
            A list of matching wellness tips
        """
        if self.use_mock:
            tips = []
            for tip in self.mock_data["wellness_tips"].values():
                # Check if any category matches
                if not any(category in tip.categories for category in categories):
                    continue
                
                # Check symptom tags if provided
                if symptom_tags and not any(tag in tip.symptom_tags for tag in symptom_tags):
                    continue
                
                tips.append(tip)
                if len(tips) >= limit:
                    break
            return tips
        else:
            # Firestore doesn't support OR queries across fields directly
            # For simplicity, we'll query by the first category and filter in code
            query = self.db.collection("wellness_tips").where("categories", "array_contains", categories[0])
            query = query.limit(limit * 2)  # Fetch extra to allow for filtering
            
            tips = []
            for doc in query.stream():
                tip = WellnessTip.from_dict(doc.to_dict())
                
                # Check if any category matches
                if not any(category in tip.categories for category in categories):
                    continue
                
                # Check symptom tags if provided
                if symptom_tags and not any(tag in tip.symptom_tags for tag in symptom_tags):
                    continue
                
                tips.append(tip)
                if len(tips) >= limit:
                    break
            
            return tips
    
    def save_wellness_tip(self, tip: WellnessTip) -> bool:
        """
        Save a wellness tip to the database.
        
        Args:
            tip: The wellness tip to save
            
        Returns:
            True if successful, False otherwise
        """
        tip_dict = tip.to_dict()
        
        try:
            if self.use_mock:
                self.mock_data["wellness_tips"][tip.tip_id] = tip
                return True
            else:
                self.db.collection("wellness_tips").document(tip.tip_id).set(tip_dict)
                return True
        except Exception as e:
            print(f"Error saving wellness tip: {str(e)}")
            return False
    
    # Helper methods
    def create_new_session(self, user_id: str, user_role: str) -> Session:
        """
        Create a new session for a user.
        
        Args:
            user_id: The ID of the user
            user_role: The role of the user
            
        Returns:
            A new session instance
        """
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            is_active=True
        )
        
        # Initialize empty state
        session.state = {
            "user_id": user_id,
            "user_role": user_role,
            "system_time": datetime.now().isoformat()
        }
        
        # Save the session
        self.save_session(session)
        
        return session
    
    def create_symptom_log_from_state(self, state: Dict[str, Any]) -> Optional[SymptomsLog]:
        """
        Create a symptom log from the current session state.
        
        Args:
            state: The current session state
            
        Returns:
            A new symptom log instance, or None if required data is missing
        """
        user_id = state.get("user_id")
        if not user_id:
            return None
        
        log_id = str(uuid.uuid4())
        log = SymptomsLog(
            log_id=log_id,
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        # Set symptom data from state
        log.symptom_rating = state.get("symptom_rating")
        log.symptom_emoji = state.get("symptom_emoji")
        log.symptom_text = state.get("symptom_text")
        
        # Set additional metrics if available
        log.energy_level = state.get("energy_level")
        log.stress_level = state.get("stress_level")
        log.sleep_quality = state.get("sleep_quality")
        
        # Set work impact data if available
        log.productivity_impact = state.get("productivity_impact")
        log.needs_accommodation = state.get("needs_accommodation")
        log.accommodation_type = state.get("accommodation_type")
        
        # Set privacy controls from user settings
        log.privacy_level = state.get("privacy_level", "standard")
        log.share_with_hr = state.get("share_with_hr", False)
        log.is_anonymous = state.get("is_anonymous", True)
        
        # Set contextual information
        log.tags = state.get("symptom_tags", [])
        log.notes = state.get("symptom_notes")
        log.location = state.get("location")
        
        # Save the log
        self.save_symptom_log(log)
        
        return log
    
    def sync_state_to_database(self, state: Dict[str, Any]) -> bool:
        """
        Synchronize the current session state to the database.
        
        Args:
            state: The current session state
            
        Returns:
            True if successful, False otherwise
        """
        session_id = state.get("session_id")
        if not session_id:
            return False
        
        try:
            # Get the current session
            session = self.get_session(session_id)
            if not session:
                return False
            
            # Update the session state
            session.state = state
            session.updated_at = datetime.now()
            session.last_interaction_time = datetime.now()
            
            # Save the updated session
            return self.save_session(session)
        except Exception as e:
            print(f"Error syncing state to database: {str(e)}")
            return False 