"""Symptom tracking service for the Wellness Agent."""

import datetime
from typing import Dict, List, Optional, Any, Union

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.db.bigquery import BigQueryClient
from wellness_agent.privacy.anonymizer import Anonymizer

class SymptomService:
    """Service for managing symptom tracking."""
    
    def __init__(
        self,
        firestore_client: Optional[FirestoreClient] = None,
        bigquery_client: Optional[BigQueryClient] = None,
        anonymizer: Optional[Anonymizer] = None
    ):
        """Initialize the symptom service.
        
        Args:
            firestore_client: Firestore client for data storage
            bigquery_client: BigQuery client for analytics
            anonymizer: Data anonymizer
        """
        self.db = firestore_client or FirestoreClient()
        self.analytics_db = bigquery_client or BigQueryClient()
        self.anonymizer = anonymizer or Anonymizer()
    
    def track_symptom(
        self,
        profile_id: str,
        symptom_type: str,
        severity: int,
        privacy_level: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track a symptom for an employee.
        
        Args:
            profile_id: Employee profile ID
            symptom_type: Type of symptom
            severity: Severity level (1-10)
            privacy_level: Privacy setting for this symptom
            notes: Optional notes
            
        Returns:
            The saved symptom data
        """
        # Get the employee profile to check privacy settings
        profile = self.db.get_employee_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        # Prepare symptom data
        symptom_data = {
            "type": symptom_type,
            "privacy_level": privacy_level
        }
        
        # Store the symptom log in Firestore
        log_data = self.db.log_symptom(
            profile_id=profile_id,
            symptom_data=symptom_data,
            severity_level=severity,
            notes=notes
        )
        
        # If privacy level allows anonymous analytics, add to aggregated data
        if privacy_level in ["anonymous_only", "shareable"]:
            try:
                # Get organization ID from the profile
                # In a real implementation, this would be stored in the profile
                organization_id = profile.get("organization_id", "unknown")
                
                # Queue the symptom for aggregation (in real implementation)
                # This would be done in a background process to avoid blocking
                print(f"Queued symptom data for anonymized analytics for org {organization_id}")
            except Exception as e:
                # Log but don't block the user experience
                print(f"Error queueing for analytics: {e}")
        
        return {
            "status": "success",
            "message": f"Your {symptom_type} symptom (severity {severity}) has been logged with {privacy_level} privacy level.",
            "data": log_data
        }
    
    def get_symptom_history(
        self,
        profile_id: str,
        time_period: str = "month",
        symptom_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get symptom history for an employee.
        
        Args:
            profile_id: Employee profile ID
            time_period: Time period to retrieve
            symptom_types: Optional list of symptom types to filter by
            
        Returns:
            Symptom history data
        """
        # Convert time period to days
        days_map = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365
        }
        days = days_map.get(time_period, 30)
        
        # Get symptom logs from Firestore
        logs = self.db.get_symptom_history(profile_id, days)
        
        # Filter by symptom type if specified
        if symptom_types:
            logs = [
                log for log in logs
                if log.get("symptom_data", {}).get("type") in symptom_types
            ]
        
        # Process the data for visualization
        symptom_counts = {}
        severity_trends = {}
        dates = []
        
        for log in logs:
            symptom_type = log.get("symptom_data", {}).get("type", "unknown")
            severity = log.get("severity_level", 0)
            date = log.get("date")
            
            # Convert firestore timestamp to string
            if hasattr(date, "isoformat"):
                date_str = date.strftime("%Y-%m-%d")
            else:
                # Handle string dates or other formats
                date_str = str(date).split("T")[0] if "T" in str(date) else str(date)
            
            # Count symptoms by type
            symptom_counts[symptom_type] = symptom_counts.get(symptom_type, 0) + 1
            
            # Track severity by date for trending
            if date_str not in severity_trends:
                severity_trends[date_str] = {}
                dates.append(date_str)
            
            severity_trends[date_str][symptom_type] = severity
        
        # Sort dates for consistent display
        dates.sort()
        
        # Format severity trends for charting
        trend_data = []
        for date_str in dates:
            data_point = {"date": date_str}
            for symptom_type in symptom_counts.keys():
                data_point[symptom_type] = severity_trends.get(date_str, {}).get(symptom_type, None)
            trend_data.append(data_point)
        
        return {
            "status": "success",
            "message": f"Retrieved symptom history for the past {time_period}.",
            "data": {
                "logs": logs,
                "symptom_counts": symptom_counts,
                "severity_trends": trend_data,
                "time_period": time_period
            }
        }
    
    def get_wellness_tips(
        self,
        symptom_type: str,
        environment: str = "office"
    ) -> Dict[str, Any]:
        """Get personalized wellness tips based on reported symptoms.
        
        Args:
            symptom_type: Type of symptom to get tips for
            environment: Work environment context
            
        Returns:
            List of wellness tips
        """
        # In a real implementation, this would draw from a database of evidence-based recommendations
        tips_by_symptom = {
            "headache": [
                "Take a 5-minute screen break every hour to reduce eye strain",
                "Ensure proper lighting in your workspace to reduce eye strain",
                "Stay hydrated by keeping a water bottle at your desk",
                "Try gentle neck stretches at your desk",
                "Adjust your monitor height to be at eye level"
            ],
            "fatigue": [
                "Take a brief walk outside or around the office when possible",
                "Consider a standing desk or alternating between sitting and standing",
                "Schedule complex tasks during your natural high-energy periods",
                "Take a proper lunch break away from your workstation",
                "Try a brief mindfulness exercise between meetings"
            ],
            "cramps": [
                "Use a heating pad or hot water bottle discreetly at your desk",
                "Try seated stretching exercises for relief",
                "Consider an ergonomic chair cushion for support",
                "Take brief movement breaks to reduce discomfort",
                "Stay hydrated throughout the day"
            ],
            "mood": [
                "Practice a 2-minute breathing exercise between tasks",
                "Keep a gratitude or accomplishment list for tough days",
                "Schedule short breaks for mood reset activities",
                "Try the 'Pomodoro technique' (25 min work, 5 min break) for focus",
                "Consider noise-cancelling headphones for a calmer environment"
            ],
            "focus": [
                "Break large tasks into smaller, manageable segments",
                "Use the 'brain dump' technique to clear mental distractions",
                "Try time-blocking your calendar for focused work periods",
                "Reduce notifications during concentration periods",
                "Consider a white noise app to mask distracting sounds"
            ]
        }
        
        # Default tips if the specific symptom isn't in our database
        default_tips = [
            "Take regular breaks throughout your workday",
            "Stay hydrated with water",
            "Practice deep breathing when feeling stressed",
            "Consider speaking with your healthcare provider about persistent symptoms",
            "Remember to maintain good posture at your workstation"
        ]
        
        # Retrieve tips for the specific symptom, or use defaults
        tips = tips_by_symptom.get(symptom_type.lower(), default_tips)
        
        # Add environment-specific tips
        if environment == "remote":
            tips.append("Set clear boundaries between work and home spaces")
            tips.append("Schedule virtual coffee breaks with colleagues to reduce isolation")
        elif environment == "office":
            tips.append("Find a quiet space for brief relaxation periods when needed")
            tips.append("Consider noise-cancelling headphones during high-symptom periods")
        elif environment == "hybrid":
            tips.append("Plan office days around your symptom patterns when possible")
            tips.append("Create consistent wellness routines that work in both environments")
        
        # In a full implementation, we would log which tips were provided to improve recommendations
        
        return {
            "status": "success",
            "message": f"Here are some workplace-appropriate tips for managing {symptom_type}:",
            "tips": tips
        }
    
    def anonymize_and_aggregate_symptoms(
        self,
        organization_id: str,
        time_period: str = "month"
    ) -> Dict[str, Any]:
        """Anonymize and aggregate symptom data for an organization.
        
        Args:
            organization_id: Organization ID
            time_period: Time period to aggregate
            
        Returns:
            Anonymized aggregated data
        """
        # In a real implementation, this would:
        # 1. Fetch all symptom logs for the organization with proper privacy filters
        # 2. Use the anonymizer to properly anonymize the data
        # 3. Store the aggregated data in BigQuery
        
        # For demonstration, we'll return simulated data
        
        period_days = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365
        }.get(time_period, 30)
        
        # Calculate date range
        now = datetime.datetime.now()
        start_date = now - datetime.timedelta(days=period_days)
        
        # Simulated aggregated data that would come from anonymization
        aggregated_data = {
            "symptom_counts": {
                "headache": 23,
                "fatigue": 18,
                "focus": 12,
                "mood": 15
            },
            "average_severity": {
                "headache": 6.2,
                "fatigue": 5.8,
                "focus": 4.3,
                "mood": 4.9
            },
            "time_trends": {
                "weekly": [
                    {"week": "2023-01-01", "headache": 5, "fatigue": 4, "focus": 3, "mood": 4},
                    {"week": "2023-01-08", "headache": 6, "fatigue": 5, "focus": 2, "mood": 3},
                    {"week": "2023-01-15", "headache": 4, "fatigue": 3, "focus": 4, "mood": 5},
                    {"week": "2023-01-22", "headache": 8, "fatigue": 6, "focus": 3, "mood": 3}
                ]
            },
            "employee_count": 42,  # Important for k-anonymity
            "min_group_size": 5    # Minimum group size for k-anonymity
        }
        
        # In a real implementation, we would store this in BigQuery
        # metric_id = self.analytics_db.store_anonymized_metrics(
        #     organization_id=organization_id,
        #     metric_type="symptom_frequency",
        #     period_start=start_date,
        #     period_end=now,
        #     employee_count=aggregated_data["employee_count"],
        #     aggregated_data=aggregated_data
        # )
        
        return {
            "status": "success",
            "message": f"Generated anonymized symptom trends for {time_period}",
            "data": aggregated_data
        } 