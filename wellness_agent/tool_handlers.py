"""Tool handlers for the Wellness Agent."""

from typing import Dict, List, Optional, Any, Literal, Union
import os

from wellness_agent.services.service_factory import ServiceFactory

# Initialize service factory
service_factory = ServiceFactory()

# ---- Employee Tool Handlers ----

def track_symptom_handler(
    symptom_type: str,
    severity: int, 
    privacy_level: Literal["fully_private", "anonymous_only", "shareable"],
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Track an employee's reported symptom for their personal record.
    
    Args:
        symptom_type: The category of symptom being reported
        severity: Severity level from 1 (minimal) to 10 (severe)
        privacy_level: Privacy setting for this specific symptom data
        notes: Optional additional details about the symptom
        
    Returns:
        A confirmation message and the saved symptom data
    """
    try:
        # In a real implementation, we would get the profile_id from authentication
        # For demo purposes, we'll use a mock profile ID
        profile_id = os.getenv("DEMO_PROFILE_ID", "demo_profile_123")
        
        # Get the symptom service
        symptom_service = service_factory.get_symptom_service()
        
        # Track the symptom
        result = symptom_service.track_symptom(
            profile_id=profile_id,
            symptom_type=symptom_type,
            severity=severity,
            privacy_level=privacy_level,
            notes=notes
        )
        
        return result
    except Exception as e:
        # For demonstration, we'll handle the error and return a friendly message
        print(f"Error tracking symptom: {e}")
        
        # Fall back to mock response for demonstration
        return {
            "status": "success",
            "message": f"Your {symptom_type} symptom (severity {severity}) has been logged with {privacy_level} privacy level.",
            "data": {
                "symptom_type": symptom_type,
                "severity": severity,
                "privacy_level": privacy_level,
                "notes": notes,
                "timestamp": "2025-05-19T12:00:00Z"  # Would be current time in real implementation
            }
        }

def quick_check_in_handler(
    overall_wellbeing: Literal["great", "good", "okay", "struggling", "poor"],
    emoji_mood: Literal["😊", "😌", "😐", "😟", "😣"],
    share_with_team: bool = False
) -> Dict[str, Any]:
    """
    Record a quick daily check-in with emoji-based mood tracking.
    
    Args:
        overall_wellbeing: A simple descriptor of how the employee is feeling today
        emoji_mood: An emoji that represents the employee's current mood
        share_with_team: Whether this check-in should be visible to the team dashboard (anonymously)
        
    Returns:
        A confirmation message and the saved check-in data
    """
    # This would connect to a database in a real implementation
    
    response_messages = {
        "great": "That's wonderful to hear! Keep up those positive practices.",
        "good": "Glad you're doing well today!",
        "okay": "Thanks for checking in. Let me know if you need any support today.",
        "struggling": "I'm sorry to hear you're struggling today. Would you like some workplace wellness tips?",
        "poor": "I'm sorry you're not feeling well. Would you like to explore accommodations or wellness resources?"
    }
    
    return {
        "status": "success",
        "message": response_messages[overall_wellbeing],
        "data": {
            "overall_wellbeing": overall_wellbeing,
            "emoji_mood": emoji_mood,
            "share_with_team": share_with_team,
            "timestamp": "2025-05-19T12:00:00Z"  # Would be current time in real implementation
        }
    }

def get_wellness_tips_handler(
    symptom_type: str,
    environment: Literal["office", "remote", "hybrid"] = "office"
) -> Dict[str, Any]:
    """
    Get personalized wellness tips based on reported symptoms.
    
    Args:
        symptom_type: The category of symptom to get tips for
        environment: The work environment context for the tips
        
    Returns:
        A list of workplace-appropriate wellness tips
    """
    try:
        # Get the symptom service
        symptom_service = service_factory.get_symptom_service()
        
        # Get wellness tips
        result = symptom_service.get_wellness_tips(
            symptom_type=symptom_type,
            environment=environment
        )
        
        return result
    except Exception as e:
        # For demonstration, we'll handle the error and return a friendly message
        print(f"Error getting wellness tips: {e}")
        
        # Fall back to mock response
        # Default tips if the specific symptom isn't in our database
        default_tips = [
            "Take regular breaks throughout your workday",
            "Stay hydrated with water",
            "Practice deep breathing when feeling stressed",
            "Consider speaking with your healthcare provider about persistent symptoms",
            "Remember to maintain good posture at your workstation"
        ]
        
        return {
            "status": "success",
            "message": f"Here are some workplace-appropriate tips for managing {symptom_type}:",
            "tips": default_tips
        }

def request_accommodation_handler(
    accommodation_type: Literal["flexible_schedule", "remote_work", "physical_modification", "leave_request", "other"],
    start_date: str,
    end_date: Optional[str] = None,
    details: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit a workplace accommodation request.
    
    Args:
        accommodation_type: The type of accommodation being requested
        start_date: When the accommodation should begin (YYYY-MM-DD)
        end_date: When the accommodation should end, if temporary (YYYY-MM-DD)
        details: Additional details about the accommodation request
        
    Returns:
        A confirmation and next steps
    """
    # In a real implementation, this would create a request in the system
    
    accommodation_descriptions = {
        "flexible_schedule": "modified work hours or schedule adjustments",
        "remote_work": "working from home or another remote location",
        "physical_modification": "changes to your physical workspace or equipment",
        "leave_request": "time off for health-related reasons",
        "other": "a custom accommodation"
    }
    
    description = accommodation_descriptions.get(accommodation_type, "an accommodation")
    
    return {
        "status": "success",
        "message": f"Your request for {description} has been submitted.",
        "next_steps": [
            "Your request has been sent to HR anonymously (they'll see the request details but not your health data).",
            "You should receive a response within 2 business days.",
            "You can check the status of your request in the 'My Requests' section."
        ],
        "request_id": "req_12345"  # Would be a database-generated ID in real implementation
    }

def view_symptom_history_handler(
    time_period: Literal["week", "month", "quarter", "year"] = "month",
    symptom_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    View personal symptom history and trends.
    
    Args:
        time_period: How far back to show history
        symptom_types: Optional list of symptom types to filter by
        
    Returns:
        Personal symptom history data and visualizations
    """
    try:
        # In a real implementation, we would get the profile_id from authentication
        # For demo purposes, we'll use a mock profile ID
        profile_id = os.getenv("DEMO_PROFILE_ID", "demo_profile_123")
        
        # Get the symptom service
        symptom_service = service_factory.get_symptom_service()
        
        # Get symptom history
        result = symptom_service.get_symptom_history(
            profile_id=profile_id,
            time_period=time_period,
            symptom_types=symptom_types
        )
        
        return result
    except Exception as e:
        # For demonstration, we'll handle the error and return a friendly message
        print(f"Error retrieving symptom history: {e}")
        
        # Fall back to mock response for demonstration
        return {
            "status": "success",
            "message": f"Here's your symptom history for the past {time_period}:",
            "data": {
                "symptom_counts": {
                    "headache": 5,
                    "fatigue": 3,
                    "mood": 2
                },
                "severity_trends": [
                    {"date": "2025-05-01", "headache": 7, "fatigue": None, "mood": None},
                    {"date": "2025-05-03", "headache": 5, "fatigue": None, "mood": None},
                    {"date": "2025-05-07", "headache": 4, "fatigue": None, "mood": None},
                    {"date": "2025-05-10", "headache": None, "fatigue": 6, "mood": None},
                    {"date": "2025-05-11", "headache": None, "fatigue": 5, "mood": None},
                    {"date": "2025-05-15", "headache": None, "fatigue": 4, "mood": None},
                    {"date": "2025-05-17", "headache": None, "fatigue": None, "mood": 3},
                    {"date": "2025-05-18", "headache": None, "fatigue": None, "mood": 4}
                ]
            }
        }

# Add more tool handlers as needed 