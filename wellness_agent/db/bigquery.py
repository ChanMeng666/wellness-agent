"""BigQuery database client for anonymized analytics in the Wellness Agent."""

import os
import json
import datetime
from typing import Dict, List, Optional, Any, Union
from google.cloud import bigquery

class BigQueryClient:
    """Client for interacting with BigQuery for anonymized analytics."""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize the BigQuery client.
        
        Args:
            project_id: Google Cloud project ID. If None, will use the
                GOOGLE_CLOUD_PROJECT environment variable.
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("Project ID must be provided or set as GOOGLE_CLOUD_PROJECT environment variable")
        
        self.client = bigquery.Client(project=self.project_id)
        self.dataset_id = "wellness_analytics"
        self.metrics_table = "anonymized_metrics"
        
    def _ensure_dataset_exists(self):
        """Ensure the analytics dataset exists."""
        dataset_ref = self.client.dataset(self.dataset_id)
        
        try:
            self.client.get_dataset(dataset_ref)
        except Exception:
            # Dataset doesn't exist, create it
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset = self.client.create_dataset(dataset)
            
    def _ensure_metrics_table_exists(self):
        """Ensure the anonymized metrics table exists."""
        self._ensure_dataset_exists()
        
        table_ref = self.client.dataset(self.dataset_id).table(self.metrics_table)
        
        try:
            self.client.get_table(table_ref)
        except Exception:
            # Table doesn't exist, create it
            schema = [
                bigquery.SchemaField("metric_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("organization_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("period_start", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("period_end", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("metric_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("employee_count", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("aggregated_data", "JSON", mode="REQUIRED"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
    
    def store_anonymized_metrics(
        self,
        organization_id: str,
        metric_type: str,
        period_start: datetime.datetime,
        period_end: datetime.datetime,
        employee_count: int,
        aggregated_data: Dict[str, Any]
    ) -> str:
        """Store anonymized metrics in BigQuery.
        
        Args:
            organization_id: Organization ID
            metric_type: Type of metric (e.g., symptom_frequency, accommodation_requests)
            period_start: Start of the period
            period_end: End of the period
            employee_count: Number of employees in the data
            aggregated_data: Anonymized aggregated data
            
        Returns:
            The ID of the stored metric record
        """
        self._ensure_metrics_table_exists()
        
        metric_id = f"{organization_id}_{metric_type}_{int(period_start.timestamp())}"
        
        # Prepare the row data
        row = {
            "metric_id": metric_id,
            "organization_id": organization_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "metric_type": metric_type,
            "employee_count": employee_count,
            "aggregated_data": json.dumps(aggregated_data),
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Insert the row
        table_ref = self.client.dataset(self.dataset_id).table(self.metrics_table)
        errors = self.client.insert_rows_json(table_ref, [row])
        
        if errors:
            raise RuntimeError(f"Error inserting row: {errors}")
        
        return metric_id
    
    def get_trend_data(
        self,
        organization_id: str,
        metric_type: str,
        start_date: datetime.datetime,
        end_date: Optional[datetime.datetime] = None,
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
        if not end_date:
            end_date = datetime.datetime.now()
            
        query = f"""
        SELECT
            metric_id,
            organization_id,
            period_start,
            period_end,
            metric_type,
            employee_count,
            aggregated_data
        FROM
            `{self.project_id}.{self.dataset_id}.{self.metrics_table}`
        WHERE
            organization_id = @organization_id
            AND metric_type = @metric_type
            AND period_end >= @start_date
            AND period_start <= @end_date
            AND employee_count >= @min_employee_count
        ORDER BY
            period_start ASC
        """
        
        query_params = [
            bigquery.ScalarQueryParameter("organization_id", "STRING", organization_id),
            bigquery.ScalarQueryParameter("metric_type", "STRING", metric_type),
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date.isoformat()),
            bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date.isoformat()),
            bigquery.ScalarQueryParameter("min_employee_count", "INTEGER", min_employee_count)
        ]
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = self.client.query(query, job_config=job_config)
        
        results = []
        for row in query_job:
            result = {
                "metric_id": row.metric_id,
                "organization_id": row.organization_id,
                "period_start": row.period_start,
                "period_end": row.period_end,
                "metric_type": row.metric_type,
                "employee_count": row.employee_count,
                "aggregated_data": json.loads(row.aggregated_data)
            }
            results.append(result)
            
        return results
        
    def generate_anonymized_metric(
        self,
        organization_id: str,
        metric_type: str,
        raw_data: List[Dict[str, Any]],
        employee_count: int,
        period_start: datetime.datetime,
        period_end: datetime.datetime
    ) -> Dict[str, Any]:
        """Generate an anonymized metric from raw data.
        
        This function applies privacy-preserving techniques before storing data.
        
        Args:
            organization_id: Organization ID
            metric_type: Type of metric
            raw_data: Raw data to anonymize
            employee_count: Number of employees in the data
            period_start: Start of the period
            period_end: End of the period
            
        Returns:
            The stored metric record ID
        """
        # Skip if there are too few data points for privacy
        if employee_count < 5:
            raise ValueError("Cannot anonymize data with fewer than 5 employees")
        
        # Apply anonymization techniques based on metric type
        if metric_type == "symptom_frequency":
            aggregated_data = self._anonymize_symptom_data(raw_data)
        elif metric_type == "accommodation_requests":
            aggregated_data = self._anonymize_accommodation_data(raw_data)
        elif metric_type == "wellbeing_scores":
            aggregated_data = self._anonymize_wellbeing_data(raw_data)
        else:
            # Generic anonymization
            aggregated_data = self._anonymize_generic_data(raw_data)
        
        # Store the anonymized metrics
        metric_id = self.store_anonymized_metrics(
            organization_id=organization_id,
            metric_type=metric_type,
            period_start=period_start,
            period_end=period_end,
            employee_count=employee_count,
            aggregated_data=aggregated_data
        )
        
        return {"metric_id": metric_id, "aggregated_data": aggregated_data}
    
    def _anonymize_symptom_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Anonymize symptom data.
        
        Args:
            raw_data: List of symptom records
            
        Returns:
            Anonymized aggregated data
        """
        # Count frequency of each symptom type
        symptom_counts = {}
        symptom_severities = {}
        
        for record in raw_data:
            symptom_type = record.get("symptom_data", {}).get("type", "unknown")
            severity = record.get("severity_level", 0)
            
            symptom_counts[symptom_type] = symptom_counts.get(symptom_type, 0) + 1
            
            # Track total severity for calculating averages
            if symptom_type not in symptom_severities:
                symptom_severities[symptom_type] = {"total": 0, "count": 0}
            
            symptom_severities[symptom_type]["total"] += severity
            symptom_severities[symptom_type]["count"] += 1
        
        # Calculate average severity for each symptom
        avg_severities = {}
        for symptom_type, data in symptom_severities.items():
            avg_severities[symptom_type] = round(data["total"] / data["count"], 1)
        
        # Apply k-anonymity: remove any symptom with fewer than 3 occurrences
        for symptom_type in list(symptom_counts.keys()):
            if symptom_counts[symptom_type] < 3:
                del symptom_counts[symptom_type]
                if symptom_type in avg_severities:
                    del avg_severities[symptom_type]
        
        return {
            "symptom_counts": symptom_counts,
            "average_severities": avg_severities
        }
    
    def _anonymize_accommodation_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Anonymize accommodation request data.
        
        Args:
            raw_data: List of accommodation request records
            
        Returns:
            Anonymized aggregated data
        """
        # Count frequency of each request type
        request_counts = {}
        status_counts = {"pending": 0, "approved": 0, "denied": 0}
        
        for record in raw_data:
            req_type = record.get("type", "unknown")
            status = record.get("status", "pending")
            
            request_counts[req_type] = request_counts.get(req_type, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Apply k-anonymity: remove any request type with fewer than 3 occurrences
        for req_type in list(request_counts.keys()):
            if request_counts[req_type] < 3:
                del request_counts[req_type]
        
        return {
            "request_type_counts": request_counts,
            "status_counts": status_counts,
            "total_requests": len(raw_data)
        }
    
    def _anonymize_wellbeing_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Anonymize wellbeing score data.
        
        Args:
            raw_data: List of wellbeing check-in records
            
        Returns:
            Anonymized aggregated data
        """
        # Map text ratings to numeric values for averaging
        wellbeing_map = {
            "great": 5,
            "good": 4,
            "okay": 3,
            "struggling": 2,
            "poor": 1
        }
        
        # Count occurrences and calculate averages
        mood_counts = {}
        total_score = 0
        
        for record in raw_data:
            mood = record.get("overall_wellbeing", "okay")
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            total_score += wellbeing_map.get(mood, 3)
        
        avg_score = round(total_score / len(raw_data), 1) if raw_data else 0
        
        # Apply k-anonymity: bucket data if needed
        if len(raw_data) < 10:
            # Simplify to just high/medium/low
            simplified_counts = {
                "high": mood_counts.get("great", 0) + mood_counts.get("good", 0),
                "medium": mood_counts.get("okay", 0),
                "low": mood_counts.get("struggling", 0) + mood_counts.get("poor", 0)
            }
            
            # Remove any with fewer than 3
            for level in list(simplified_counts.keys()):
                if simplified_counts[level] < 3:
                    del simplified_counts[level]
                    
            return {
                "simplified_mood_counts": simplified_counts,
                "average_score": avg_score,
                "total_checkins": len(raw_data)
            }
        else:
            # We have enough data to show more detail
            return {
                "mood_counts": mood_counts,
                "average_score": avg_score,
                "total_checkins": len(raw_data)
            }
    
    def _anonymize_generic_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generic anonymization for any type of data.
        
        Args:
            raw_data: List of records to anonymize
            
        Returns:
            Anonymized aggregated data
        """
        # Just return count information
        return {
            "total_records": len(raw_data),
            "time_period": "custom"
        } 