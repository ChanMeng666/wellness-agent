"""Analytics service for the Wellness Agent."""

import datetime
from typing import Dict, List, Any, Optional

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.db.bigquery import BigQueryClient
from wellness_agent.privacy.anonymizer import Anonymizer

class AnalyticsService:
    """Service for analytics and data processing."""
    
    def __init__(self, firestore_client=None, bigquery_client=None, anonymizer=None):
        """Initialize the analytics service.
        
        Args:
            firestore_client: Optional Firestore client instance
            bigquery_client: Optional BigQuery client instance
            anonymizer: Optional anonymizer instance
        """
        self.firestore = firestore_client or FirestoreClient()
        self.bigquery = bigquery_client or BigQueryClient()
        self.anonymizer = anonymizer or Anonymizer()
    
    def get_wellness_trend(
        self, organization_id: str, metric_type: str, 
        start_date: datetime.datetime, end_date: Optional[datetime.datetime] = None,
        min_employee_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Get trend data for an organization with privacy protections.
        
        Args:
            organization_id: Organization ID
            metric_type: Type of metric to retrieve
            start_date: Start date for the query
            end_date: End date for the query (default: now)
            min_employee_count: Minimum number of employees required for privacy
            
        Returns:
            List of trend data records
        """
        return self.bigquery.get_trend_data(
            organization_id=organization_id,
            metric_type=metric_type,
            start_date=start_date,
            end_date=end_date,
            min_employee_count=min_employee_count
        )
    
    def generate_symptom_metrics(
        self, organization_id: str, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> Dict[str, Any]:
        """Generate anonymized symptom metrics for an organization.
        
        Args:
            organization_id: Organization ID
            start_date: Start date for metrics
            end_date: End date for metrics
            
        Returns:
            Generated metrics
        """
        # In a real implementation, this would fetch actual data from Firestore
        # For now, we'll simulate with empty data
        raw_data = []
        
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
        """Generate anonymized accommodation request metrics for an organization.
        
        Args:
            organization_id: Organization ID
            start_date: Start date for metrics
            end_date: End date for metrics
            
        Returns:
            Generated metrics
        """
        # Similar to symptom metrics, but for accommodation requests
        raw_data = []
        
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
    
    def calculate_roi(
        self, organization_id: str, 
        start_date: datetime.datetime, 
        end_date: datetime.datetime,
        program_costs: float,
        productivity_factor: float = 1.0
    ) -> Dict[str, Any]:
        """Calculate return on investment for wellness programs.
        
        Args:
            organization_id: Organization ID
            start_date: Start date for analysis
            end_date: End date for analysis
            program_costs: Costs of wellness programs
            productivity_factor: Factor to adjust productivity impact
            
        Returns:
            ROI analysis
        """
        # This would be a complex calculation in a real implementation
        # For now, we'll return a simulated result
        
        # Get wellness trends
        wellness_data = self.get_wellness_trend(
            organization_id=organization_id,
            metric_type="wellbeing_scores",
            start_date=start_date,
            end_date=end_date
        )
        
        # Get accommodation request trends
        accommodation_data = self.get_wellness_trend(
            organization_id=organization_id,
            metric_type="accommodation_requests",
            start_date=start_date,
            end_date=end_date
        )
        
        # Simulate benefit calculation
        # In a real implementation, this would use actual data and research-based formulas
        avg_wellness_improvement = 0.1  # 10% improvement assumption
        reduced_absence_hours = 24  # Assumption: 3 days per employee per year
        hourly_productivity_value = 50  # Assumption: $50 per hour productivity value
        
        # Calculate benefits
        estimated_employee_count = 100  # Assumption for demo
        productivity_benefit = (
            reduced_absence_hours * 
            hourly_productivity_value * 
            estimated_employee_count * 
            productivity_factor
        )
        
        # Calculate ROI
        roi = (productivity_benefit - program_costs) / program_costs if program_costs > 0 else 0
        
        return {
            "status": "success",
            "organization_id": organization_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "metrics": {
                "program_costs": program_costs,
                "productivity_benefit": productivity_benefit,
                "net_benefit": productivity_benefit - program_costs,
                "roi": roi,
                "roi_percentage": f"{roi * 100:.1f}%"
            },
            "assumptions": {
                "wellness_improvement": f"{avg_wellness_improvement * 100:.1f}%",
                "reduced_absence_hours": reduced_absence_hours,
                "hourly_productivity_value": hourly_productivity_value,
                "employee_count": estimated_employee_count,
                "productivity_factor": productivity_factor
            }
        } 