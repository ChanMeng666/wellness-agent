"""Anonymizer for the Wellness Agent."""

import json
import copy
import datetime
import hashlib
import random
from typing import Dict, List, Any, Optional, Set, Union, Tuple

class Anonymizer:
    """Handles anonymization of sensitive data for the Wellness Agent."""
    
    def __init__(self, min_group_size: int = 5, salt: Optional[str] = None):
        """Initialize the anonymizer.
        
        Args:
            min_group_size: Minimum size of a group for k-anonymity
            salt: Optional salt for hashing (will generate randomly if not provided)
        """
        self.min_group_size = min_group_size
        self.salt = salt or self._generate_salt()
        
    def _generate_salt(self) -> str:
        """Generate a random salt for hashing."""
        return hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
    
    def _hash_identifier(self, identifier: str) -> str:
        """Hash an identifier with the salt.
        
        Args:
            identifier: The identifier to hash
            
        Returns:
            A salted hash of the identifier
        """
        return hashlib.sha256(f"{identifier}{self.salt}".encode()).hexdigest()
    
    def anonymize_symptom_data(
        self, 
        data: List[Dict[str, Any]], 
        user_privacy_settings: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Anonymize symptom tracking data.
        
        Args:
            data: List of symptom records
            user_privacy_settings: User's privacy preferences
            
        Returns:
            Tuple of (personal_data, anonymized_data)
        """
        # Copy data to avoid modifying original
        personal_data = copy.deepcopy(data)
        anonymized_data = []
        
        # Apply privacy settings
        privacy_level = user_privacy_settings.get("symptom_privacy", "high")
        
        # Process all records
        for record in data:
            anon_record = copy.deepcopy(record)
            
            # Always remove or hash identifiers
            if "user_id" in anon_record:
                anon_record["user_id"] = self._hash_identifier(anon_record["user_id"])
            if "profile_id" in anon_record:
                anon_record["profile_id"] = self._hash_identifier(anon_record["profile_id"])
                
            # Remove identifying notes in all cases
            if "notes" in anon_record:
                if privacy_level == "high":
                    # Remove notes completely
                    del anon_record["notes"]
                else:
                    # Replace with generic text
                    anon_record["notes"] = "Details redacted for privacy"
            
            # Handle different privacy levels
            if privacy_level == "high":
                # Generalize data further by bucketing severity
                if "severity_level" in anon_record:
                    severity = anon_record["severity_level"]
                    # Convert to low/medium/high
                    if severity <= 3:
                        anon_record["severity_category"] = "low"
                    elif severity <= 7:
                        anon_record["severity_category"] = "medium"
                    else:
                        anon_record["severity_category"] = "high"
                    del anon_record["severity_level"]
                
                # Generalize timestamp to just the week
                if "date" in anon_record and isinstance(anon_record["date"], (str, datetime.datetime)):
                    date = anon_record["date"]
                    if isinstance(date, str):
                        date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                    
                    # Get the start of the week
                    start_of_week = date - datetime.timedelta(days=date.weekday())
                    anon_record["week"] = start_of_week.strftime("%Y-%m-%d")
                    del anon_record["date"]
            
            # Medium privacy - less generalization
            elif privacy_level == "medium":
                # Keep severity but round to nearest integer
                if "severity_level" in anon_record:
                    anon_record["severity_level"] = round(anon_record["severity_level"])
                
                # Generalize timestamp to just the day
                if "date" in anon_record and isinstance(anon_record["date"], (str, datetime.datetime)):
                    date = anon_record["date"]
                    if isinstance(date, str):
                        date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                    
                    anon_record["date"] = date.strftime("%Y-%m-%d")
            
            # Low privacy - minimal changes
            else:
                # Just round time to the hour
                if "date" in anon_record and isinstance(anon_record["date"], (str, datetime.datetime)):
                    date = anon_record["date"]
                    if isinstance(date, str):
                        date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                    
                    anon_record["date"] = date.replace(minute=0, second=0, microsecond=0).isoformat()
            
            anonymized_data.append(anon_record)
        
        # Calculate aggregated data
        aggregated = self._aggregate_symptom_data(anonymized_data)
        
        return personal_data, {"records": anonymized_data, "aggregated": aggregated}
    
    def _aggregate_symptom_data(self, anonymized_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate anonymized symptom data.
        
        Args:
            anonymized_data: Anonymized symptom records
            
        Returns:
            Aggregated statistics
        """
        # Count by symptom type
        symptom_counts = {}
        severity_sums = {}
        severity_counts = {}
        
        time_field = "week" if "week" in anonymized_data[0] else "date"
        
        for record in anonymized_data:
            symptom_type = record.get("symptom_data", {}).get("type", "unknown")
            
            # Count symptoms by type
            symptom_counts[symptom_type] = symptom_counts.get(symptom_type, 0) + 1
            
            # Track severity for averaging
            if "severity_level" in record:
                if symptom_type not in severity_sums:
                    severity_sums[symptom_type] = 0
                    severity_counts[symptom_type] = 0
                
                severity_sums[symptom_type] += record["severity_level"]
                severity_counts[symptom_type] += 1
            elif "severity_category" in record:
                # Convert category back to number for aggregation
                category_map = {"low": 2, "medium": 5, "high": 8}
                severity = category_map.get(record["severity_category"], 5)
                
                if symptom_type not in severity_sums:
                    severity_sums[symptom_type] = 0
                    severity_counts[symptom_type] = 0
                
                severity_sums[symptom_type] += severity
                severity_counts[symptom_type] += 1
        
        # Calculate averages
        avg_severity = {}
        for symptom_type in severity_sums:
            if severity_counts[symptom_type] > 0:
                avg_severity[symptom_type] = round(
                    severity_sums[symptom_type] / severity_counts[symptom_type], 1
                )
        
        # Apply k-anonymity: remove any with less than min_group_size
        for symptom_type in list(symptom_counts.keys()):
            if symptom_counts[symptom_type] < self.min_group_size:
                del symptom_counts[symptom_type]
                if symptom_type in avg_severity:
                    del avg_severity[symptom_type]
        
        return {
            "symptom_counts": symptom_counts,
            "average_severity": avg_severity,
            "total_records": len(anonymized_data)
        }
    
    def anonymize_accommodation_data(
        self, 
        data: List[Dict[str, Any]],
        user_privacy_settings: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Anonymize accommodation request data.
        
        Args:
            data: List of accommodation request records
            user_privacy_settings: User's privacy preferences
            
        Returns:
            Tuple of (personal_data, anonymized_data)
        """
        # Copy data to avoid modifying original
        personal_data = copy.deepcopy(data)
        anonymized_data = []
        
        # Apply privacy settings
        privacy_level = user_privacy_settings.get("accommodation_privacy", "high")
        
        for record in data:
            anon_record = copy.deepcopy(record)
            
            # Always remove or hash identifiers
            if "user_id" in anon_record:
                anon_record["user_id"] = self._hash_identifier(anon_record["user_id"])
            if "profile_id" in anon_record:
                anon_record["profile_id"] = self._hash_identifier(anon_record["profile_id"])
            
            # Handle notes based on privacy level
            if "notes" in anon_record:
                if privacy_level == "high":
                    del anon_record["notes"]
                else:
                    anon_record["notes"] = "Details redacted for privacy"
            
            # For high privacy
            if privacy_level == "high":
                # Generalize dates to month
                for date_field in ["request_date", "start_date", "end_date"]:
                    if date_field in anon_record and anon_record[date_field]:
                        date = anon_record[date_field]
                        if isinstance(date, str):
                            try:
                                date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                            except ValueError:
                                # Handle date strings in different format
                                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                        
                        # Get just the month
                        anon_record[date_field] = date.strftime("%Y-%m")
            
            # For medium privacy
            elif privacy_level == "medium":
                # Keep dates but remove times
                for date_field in ["request_date", "start_date", "end_date"]:
                    if date_field in anon_record and anon_record[date_field]:
                        date = anon_record[date_field]
                        if isinstance(date, str):
                            try:
                                date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                            except ValueError:
                                # Handle date strings in different format
                                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                        
                        # Get just the date
                        anon_record[date_field] = date.strftime("%Y-%m-%d")
            
            anonymized_data.append(anon_record)
        
        # Calculate aggregated data
        aggregated = self._aggregate_accommodation_data(anonymized_data)
        
        return personal_data, {"records": anonymized_data, "aggregated": aggregated}
    
    def _aggregate_accommodation_data(self, anonymized_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate anonymized accommodation data.
        
        Args:
            anonymized_data: Anonymized accommodation records
            
        Returns:
            Aggregated statistics
        """
        # Count by request type and status
        type_counts = {}
        status_counts = {"pending": 0, "approved": 0, "denied": 0}
        
        for record in anonymized_data:
            req_type = record.get("type", "unknown")
            status = record.get("status", "pending")
            
            type_counts[req_type] = type_counts.get(req_type, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Apply k-anonymity
        for req_type in list(type_counts.keys()):
            if type_counts[req_type] < self.min_group_size:
                del type_counts[req_type]
        
        return {
            "request_type_counts": type_counts,
            "status_counts": status_counts,
            "total_requests": len(anonymized_data)
        }
    
    def anonymize_wellbeing_data(
        self, 
        data: List[Dict[str, Any]],
        user_privacy_settings: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Anonymize wellbeing check-in data.
        
        Args:
            data: List of wellbeing check-in records
            user_privacy_settings: User's privacy preferences
            
        Returns:
            Tuple of (personal_data, anonymized_data)
        """
        # Copy data to avoid modifying original
        personal_data = copy.deepcopy(data)
        anonymized_data = []
        
        # Apply privacy settings
        privacy_level = user_privacy_settings.get("wellbeing_privacy", "high")
        
        for record in data:
            anon_record = copy.deepcopy(record)
            
            # Always remove or hash identifiers
            if "user_id" in anon_record:
                anon_record["user_id"] = self._hash_identifier(anon_record["user_id"])
            if "profile_id" in anon_record:
                anon_record["profile_id"] = self._hash_identifier(anon_record["profile_id"])
            
            # Handle privacy levels
            if privacy_level == "high":
                # Group wellbeing into categories
                if "overall_wellbeing" in anon_record:
                    wellbeing = anon_record["overall_wellbeing"]
                    if wellbeing in ["great", "good"]:
                        anon_record["wellbeing_category"] = "high"
                    elif wellbeing == "okay":
                        anon_record["wellbeing_category"] = "medium"
                    else:
                        anon_record["wellbeing_category"] = "low"
                    del anon_record["overall_wellbeing"]
                
                # Remove emoji data entirely
                if "emoji_mood" in anon_record:
                    del anon_record["emoji_mood"]
                
                # Generalize timestamp to week
                if "timestamp" in anon_record:
                    date = anon_record["timestamp"]
                    if isinstance(date, str):
                        date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                    
                    # Get the start of the week
                    start_of_week = date - datetime.timedelta(days=date.weekday())
                    anon_record["week"] = start_of_week.strftime("%Y-%m-%d")
                    del anon_record["timestamp"]
            
            elif privacy_level == "medium":
                # Keep wellbeing category but generalize timestamp to day
                if "timestamp" in anon_record:
                    date = anon_record["timestamp"]
                    if isinstance(date, str):
                        date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                    
                    anon_record["date"] = date.strftime("%Y-%m-%d")
                    del anon_record["timestamp"]
            
            anonymized_data.append(anon_record)
        
        # Calculate aggregated data
        aggregated = self._aggregate_wellbeing_data(anonymized_data)
        
        return personal_data, {"records": anonymized_data, "aggregated": aggregated}
    
    def _aggregate_wellbeing_data(self, anonymized_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate anonymized wellbeing data.
        
        Args:
            anonymized_data: Anonymized wellbeing records
            
        Returns:
            Aggregated statistics
        """
        # Count by wellbeing category
        mood_counts = {}
        
        # Map for converting values to numeric scores
        wellbeing_map = {
            "great": 5, "good": 4, "okay": 3, "struggling": 2, "poor": 1,
            "high": 4.5, "medium": 3, "low": 1.5  # Categories
        }
        
        total_score = 0
        count = 0
        
        for record in anonymized_data:
            # Check if we have raw wellbeing or category
            if "overall_wellbeing" in record:
                mood = record["overall_wellbeing"]
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
                total_score += wellbeing_map.get(mood, 3)
                count += 1
            elif "wellbeing_category" in record:
                category = record["wellbeing_category"]
                mood_counts[category] = mood_counts.get(category, 0) + 1
                total_score += wellbeing_map.get(category, 3)
                count += 1
        
        # Calculate average score
        avg_score = round(total_score / count, 1) if count > 0 else 0
        
        # Apply k-anonymity
        for mood in list(mood_counts.keys()):
            if mood_counts[mood] < self.min_group_size:
                del mood_counts[mood]
        
        # If we don't have enough data after k-anonymity, simplify further
        if sum(mood_counts.values()) < self.min_group_size:
            # Convert to just high/medium/low
            simplified = {
                "high": 0,
                "medium": 0,
                "low": 0
            }
            
            # Map original categories to simplified
            mapping = {
                "great": "high", "good": "high",
                "okay": "medium",
                "struggling": "low", "poor": "low",
                # Categories are already mapped
                "high": "high", "medium": "medium", "low": "low"
            }
            
            # Rebuild counts
            for record in anonymized_data:
                if "overall_wellbeing" in record:
                    mood = record["overall_wellbeing"]
                    category = mapping.get(mood, "medium")
                    simplified[category] = simplified.get(category, 0) + 1
                elif "wellbeing_category" in record:
                    category = record["wellbeing_category"]
                    simplified[category] = simplified.get(category, 0) + 1
            
            # Apply k-anonymity again
            for category in list(simplified.keys()):
                if simplified[category] < self.min_group_size:
                    del simplified[category]
            
            return {
                "simplified_mood_counts": simplified,
                "average_score": avg_score,
                "total_checkins": len(anonymized_data)
            }
        
        return {
            "mood_counts": mood_counts,
            "average_score": avg_score,
            "total_checkins": len(anonymized_data)
        } 