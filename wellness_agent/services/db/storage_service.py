"""
Cloud Storage service for accessing wellness resources.
"""

from google.cloud import storage
import logging
import json
import csv
import io
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageService:
    """Service class for accessing Cloud Storage resources."""
    
    def __init__(self, bucket_name="wellness-agent-resources"):
        """Initialize Storage client"""
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(bucket_name)
    
    def list_resources(self, prefix: str = "") -> Dict[str, Any]:
        """
        List resources in the bucket with the given prefix.
        
        Args:
            prefix: Optional prefix to filter by (e.g., "wellness_guides/")
            
        Returns:
            Dict with resource listing
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            resources = []
            for blob in blobs:
                # Skip directory marker objects
                if blob.name.endswith('.keep'):
                    continue
                
                resources.append({
                    "name": blob.name,
                    "size": blob.size,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "content_type": blob.content_type
                })
            
            # Organize by type/directory
            organized = {}
            for resource in resources:
                path_parts = resource["name"].split('/')
                
                # Skip files at the top level
                if len(path_parts) <= 1:
                    continue
                
                # Get the top-level directory
                top_dir = path_parts[0]
                
                if top_dir not in organized:
                    organized[top_dir] = []
                
                organized[top_dir].append(resource)
            
            return {
                "message": f"Retrieved {len(resources)} resources",
                "resources": resources,
                "organized": organized
            }
            
        except Exception as e:
            logger.error(f"Error listing resources: {str(e)}")
            return {"error": f"Could not list resources: {str(e)}"}
    
    def get_resource_content(self, blob_name: str) -> Dict[str, Any]:
        """
        Get the content of a resource.
        
        Args:
            blob_name: The name of the blob to retrieve
            
        Returns:
            Dict with resource content
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                return {"error": f"Resource not found: {blob_name}"}
            
            # Download as text
            content = blob.download_as_text()
            
            # Handle different file types
            if blob_name.endswith('.md'):
                # Return markdown directly
                return {
                    "message": f"Retrieved {blob_name}",
                    "content_type": "text/markdown",
                    "content": content
                }
            elif blob_name.endswith('.json'):
                # Parse JSON
                try:
                    data = json.loads(content)
                    return {
                        "message": f"Retrieved {blob_name}",
                        "content_type": "application/json",
                        "data": data
                    }
                except json.JSONDecodeError:
                    return {"error": f"Invalid JSON in {blob_name}"}
            elif blob_name.endswith('.csv'):
                # Parse CSV
                try:
                    csv_reader = csv.DictReader(io.StringIO(content))
                    rows = list(csv_reader)
                    return {
                        "message": f"Retrieved {blob_name}",
                        "content_type": "text/csv",
                        "headers": csv_reader.fieldnames,
                        "rows": rows
                    }
                except Exception as csv_error:
                    return {"error": f"Error parsing CSV: {str(csv_error)}"}
            else:
                # Default to text
                return {
                    "message": f"Retrieved {blob_name}",
                    "content_type": "text/plain",
                    "content": content
                }
                
        except Exception as e:
            logger.error(f"Error retrieving resource: {str(e)}")
            return {"error": f"Could not retrieve resource: {str(e)}"}
    
    def find_policy_document(self, policy_type: str) -> Dict[str, Any]:
        """
        Find and retrieve a policy document by type.
        
        Args:
            policy_type: Type of policy (e.g., "leave", "remote_work", "accommodation")
            
        Returns:
            Dict with policy document content
        """
        try:
            policy_prefix = "policy_documents/"
            blobs = self.bucket.list_blobs(prefix=policy_prefix)
            
            # Map of search terms to likely filenames
            policy_mapping = {
                "leave": "leave_policy.md",
                "pto": "leave_policy.md",
                "vacation": "leave_policy.md",
                "sick": "leave_policy.md",
                "remote": "remote_work_policy.md",
                "work from home": "remote_work_policy.md",
                "wfh": "remote_work_policy.md",
                "accommodation": "accommodation_policy.md",
                "disability": "accommodation_policy.md",
                "ada": "accommodation_policy.md"
            }
            
            # Normalize the policy type
            policy_type_lower = policy_type.lower()
            
            # Look for an exact match in our mapping
            target_file = None
            for key, filename in policy_mapping.items():
                if key in policy_type_lower:
                    target_file = policy_prefix + filename
                    break
            
            # If no match found, try to find a policy document that contains the search term
            if not target_file:
                for blob in blobs:
                    if policy_type_lower in blob.name.lower():
                        target_file = blob.name
                        break
            
            # If we found a matching file, get its content
            if target_file:
                return self.get_resource_content(target_file)
            else:
                # List available policies
                available_policies = [blob.name.replace(policy_prefix, "") for blob in blobs if not blob.name.endswith('.keep')]
                return {
                    "message": f"No policy document found for '{policy_type}'",
                    "available_policies": available_policies
                }
                
        except Exception as e:
            logger.error(f"Error finding policy document: {str(e)}")
            return {"error": f"Could not find policy document: {str(e)}"}
    
    def get_wellness_guide(self, guide_type: str) -> Dict[str, Any]:
        """
        Find and retrieve a wellness guide by type.
        
        Args:
            guide_type: Type of guide (e.g., "mental_health", "work_life_balance", "remote_work")
            
        Returns:
            Dict with wellness guide content
        """
        try:
            guides_prefix = "wellness_guides/"
            blobs = self.bucket.list_blobs(prefix=guides_prefix)
            
            # Map of search terms to likely filenames or directories
            guide_mapping = {
                "mental health": "mental_health/mental_health_guide.md",
                "mental": "mental_health/mental_health_guide.md",
                "stress": "mental_health/mental_health_guide.md",
                "anxiety": "mental_health/mental_health_guide.md",
                "depression": "mental_health/mental_health_guide.md",
                "work life balance": "work_life_balance/work_life_balance_guide.md",
                "balance": "work_life_balance/work_life_balance_guide.md",
                "remote work": "remote_work_guide.md",
                "wfh": "remote_work_guide.md",
                "home office": "remote_work_guide.md"
            }
            
            # Normalize the guide type
            guide_type_lower = guide_type.lower()
            
            # Look for an exact match in our mapping
            target_file = None
            for key, filename in guide_mapping.items():
                if key in guide_type_lower:
                    target_file = guides_prefix + filename
                    break
            
            # If no match found, try to find a guide that contains the search term
            if not target_file:
                for blob in blobs:
                    if guide_type_lower in blob.name.lower() and not blob.name.endswith('.keep'):
                        target_file = blob.name
                        break
            
            # If we found a matching file, get its content
            if target_file:
                return self.get_resource_content(target_file)
            else:
                # List available guides
                available_guides = [
                    blob.name.replace(guides_prefix, "") 
                    for blob in blobs 
                    if not blob.name.endswith('.keep') and blob.name != guides_prefix
                ]
                return {
                    "message": f"No wellness guide found for '{guide_type}'",
                    "available_guides": available_guides
                }
                
        except Exception as e:
            logger.error(f"Error finding wellness guide: {str(e)}")
            return {"error": f"Could not find wellness guide: {str(e)}"}
    
    def get_report(self, report_type: str) -> Dict[str, Any]:
        """
        Retrieve an aggregated report by type.
        
        Args:
            report_type: Type of report (e.g., "wellness", "leave_trends")
            
        Returns:
            Dict with report content
        """
        try:
            reports_prefix = "aggregated_reports/"
            
            # Map of search terms to filenames
            report_mapping = {
                "wellness": "annual_wellness_report.json",
                "annual": "annual_wellness_report.json",
                "leave": "leave_trends.csv",
                "absence": "leave_trends.csv",
                "time off": "leave_trends.csv",
                "department": "department_wellness_metrics.csv",
                "metrics": "department_wellness_metrics.csv",
                "stats": "department_wellness_metrics.csv"
            }
            
            # Normalize the report type
            report_type_lower = report_type.lower()
            
            # Look for a match in our mapping
            target_file = None
            for key, filename in report_mapping.items():
                if key in report_type_lower:
                    target_file = reports_prefix + filename
                    break
            
            # If no match found, list available reports
            if not target_file:
                blobs = self.bucket.list_blobs(prefix=reports_prefix)
                available_reports = [
                    blob.name.replace(reports_prefix, "") 
                    for blob in blobs 
                    if not blob.name.endswith('.keep')
                ]
                return {
                    "message": f"No report found for '{report_type}'",
                    "available_reports": available_reports
                }
            
            # Get the report content
            return self.get_resource_content(target_file)
                
        except Exception as e:
            logger.error(f"Error retrieving report: {str(e)}")
            return {"error": f"Could not retrieve report: {str(e)}"} 