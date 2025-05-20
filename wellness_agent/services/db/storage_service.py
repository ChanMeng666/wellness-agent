"""
Cloud Storage service for accessing wellness resources.
"""

from google.cloud import storage
import logging
import json
import csv
import io
import os
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageService:
    """Service class for accessing Cloud Storage resources."""
    
    def __init__(self, bucket_name=None):
        """Initialize Storage client"""
        try:
            # Use environment variable if not specified
            if not bucket_name:
                bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "wellness-agent-resources")
            
            self.storage_client = storage.Client()
            self.bucket_name = bucket_name
            logger.info(f"Initializing Storage Service with bucket: {bucket_name}")
            
            # Check if the bucket exists
            try:
                self.bucket = self.storage_client.bucket(bucket_name)
                if not self.bucket.exists():
                    logger.warning(f"Bucket {bucket_name} does not exist. Will attempt to create it.")
                    self.bucket = self.storage_client.create_bucket(bucket_name)
                    logger.info(f"Created bucket {bucket_name}")
            except Exception as e:
                logger.error(f"Error accessing bucket {bucket_name}: {str(e)}")
                # Use default fallback behavior
                self.bucket = self.storage_client.bucket(bucket_name)
                
        except Exception as e:
            logger.error(f"Error initializing StorageService: {str(e)}")
            # Keep a reference to avoid attribute errors, but operations will fail
            self.storage_client = None
            self.bucket_name = bucket_name
            self.bucket = None
    
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
            if not self.storage_client or not self.bucket:
                logger.error("Storage client or bucket not initialized")
                return {"error": "Storage service not properly initialized", "suggestion": "Check your Cloud Storage configuration"}
                
            blob = self.bucket.blob(blob_name)
            logger.info(f"Attempting to retrieve resource: {blob_name}")
            
            # First check if the blob exists
            if not blob.exists():
                logger.warning(f"Resource not found: {blob_name}")
                return {
                    "error": f"Resource not found: {blob_name}",
                    "suggestion": "Check if the file exists in your Cloud Storage bucket or create it"
                }
            
            # Get blob metadata
            try:
                blob.reload()
                content_type = blob.content_type
                size = blob.size
                logger.info(f"Resource exists: {blob_name}, Type: {content_type}, Size: {size} bytes")
            except Exception as e:
                logger.warning(f"Could not get metadata for {blob_name}: {str(e)}")
                content_type = "unknown"
                size = "unknown"
            
            # Download as text
            try:
                content = blob.download_as_text()
                logger.info(f"Successfully downloaded content for {blob_name}")
            except Exception as e:
                logger.error(f"Error downloading content for {blob_name}: {str(e)}")
                return {
                    "error": f"Could not download resource content: {str(e)}",
                    "suggestion": "Check file permissions and file type"
                }
            
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
                except json.JSONDecodeError as json_error:
                    logger.error(f"Invalid JSON in {blob_name}: {str(json_error)}")
                    return {
                        "error": f"Invalid JSON in {blob_name}: {str(json_error)}",
                        "content_preview": content[:100] + "..." if len(content) > 100 else content,
                        "suggestion": "The file exists but contains invalid JSON format"
                    }
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
                    logger.error(f"Error parsing CSV in {blob_name}: {str(csv_error)}")
                    return {
                        "error": f"Error parsing CSV: {str(csv_error)}",
                        "content_preview": content[:100] + "..." if len(content) > 100 else content,
                        "suggestion": "The file exists but could not be parsed as CSV"
                    }
            else:
                # Default to text
                return {
                    "message": f"Retrieved {blob_name}",
                    "content_type": "text/plain",
                    "content": content
                }
                
        except Exception as e:
            logger.error(f"Error retrieving resource {blob_name}: {str(e)}")
            return {
                "error": f"Could not retrieve resource: {str(e)}",
                "resource": blob_name,
                "suggestion": "Check your Cloud Storage permissions and bucket configuration"
            }
    
    def find_policy_document(self, policy_type: str) -> Dict[str, Any]:
        """
        Find and retrieve a policy document by type.
        
        Args:
            policy_type: Type of policy (e.g., "leave", "remote_work", "accommodation")
            
        Returns:
            Dict with policy document content
        """
        try:
            if not self.storage_client or not self.bucket:
                logger.error("Storage client or bucket not initialized")
                return {"error": "Storage service not properly initialized", "suggestion": "Check your Cloud Storage configuration"}
                
            policy_prefix = "policy_documents/"
            logger.info(f"Looking for policy document with type: {policy_type}")
            
            # Try to list blobs to see if we have access
            try:
                blobs = list(self.bucket.list_blobs(prefix=policy_prefix, max_results=10))
                logger.info(f"Found {len(blobs)} policy document blobs")
            except Exception as e:
                logger.error(f"Error listing policy documents: {str(e)}")
                return {"error": f"Could not access policy documents: {str(e)}", "suggestion": "Check your Google Cloud credentials and permissions"}
            
            # Map of search terms to likely filenames - more comprehensive
            policy_mapping = {
                # General leave policies
                "leave": "leave_policy.md",
                "pto": "leave_policy.md",
                "vacation": "leave_policy.md",
                "time off": "leave_policy.md",
                
                # Specific leave types
                "sick": "sick_leave_policy.md",
                "illness": "sick_leave_policy.md",
                "menstruation": "menstruation_leave_policy.md",
                "period": "menstruation_leave_policy.md",
                "menstrual": "menstruation_leave_policy.md",
                "parental": "parental_leave_policy.md",
                "maternity": "parental_leave_policy.md",
                "paternity": "parental_leave_policy.md",
                "mental health": "mental_health_leave_policy.md",
                "mental health day": "mental_health_leave_policy.md", 
                "mental health days": "mental_health_leave_policy.md",
                "bereavement": "bereavement_leave_policy.md",
                
                # Other policy types
                "remote": "remote_work_policy.md",
                "work from home": "remote_work_policy.md",
                "wfh": "remote_work_policy.md",
                "accommodation": "accommodation_policy.md",
                "disability": "accommodation_policy.md",
                "ada": "accommodation_policy.md",
                "wellness": "wellness_policy.md",
                "health": "wellness_policy.md"
            }
            
            # Normalize the policy type
            policy_type_lower = policy_type.lower()
            
            # Look for an exact match in our mapping
            target_file = None
            for key, filename in policy_mapping.items():
                if key in policy_type_lower:
                    candidate_file = policy_prefix + filename
                    logger.info(f"Found potential policy match: {candidate_file}")
                    
                    # Check if this file actually exists
                    blob = self.bucket.blob(candidate_file)
                    if blob.exists():
                        target_file = candidate_file
                        logger.info(f"Verified policy file exists: {target_file}")
                        break
                    else:
                        logger.warning(f"Mapped policy file does not exist: {candidate_file}")
            
            # If no direct match found, try to find a policy document that contains the search term
            if not target_file:
                logger.info("No direct mapping found, searching for partial matches in blob names")
                for blob in blobs:
                    if policy_type_lower in blob.name.lower():
                        target_file = blob.name
                        logger.info(f"Found partial match: {target_file}")
                        break
            
            # If we found a matching file, get its content
            if target_file:
                logger.info(f"Retrieving content for policy document: {target_file}")
                return self.get_resource_content(target_file)
            else:
                # Fallback mechanism for specific policy types
                
                # If looking for mental health policy, try the general leave policy
                if "mental health" in policy_type_lower or "mental_health_leave" in policy_type_lower:
                    logger.info(f"No specific mental health policy found, checking general leave policy")
                    general_leave_policy = policy_prefix + "leave_policy.md"
                    blob = self.bucket.blob(general_leave_policy)
                    if blob.exists():
                        logger.info(f"Using general leave policy for mental health days query: {general_leave_policy}")
                        return self.get_resource_content(general_leave_policy)
                
                # If looking for specific leave type, fall back to the general leave policy
                elif "leave" in policy_type_lower or "time off" in policy_type_lower:
                    general_leave_policy = policy_prefix + "leave_policy.md"
                    blob = self.bucket.blob(general_leave_policy)
                    if blob.exists():
                        logger.info(f"No specific leave policy found, using general leave policy: {general_leave_policy}")
                        return self.get_resource_content(general_leave_policy)
                
                # List available policies for diagnostic purposes
                available_policies = [blob.name.replace(policy_prefix, "") for blob in blobs if not blob.name.endswith('.keep')]
                logger.warning(f"No policy document found for '{policy_type}'. Available policies: {available_policies}")
                
                return {
                    "message": f"No policy document found for '{policy_type}'",
                    "available_policies": available_policies,
                    "suggestion": "You could create a policy document with this name and upload it to the Cloud Storage bucket."
                }
                
        except Exception as e:
            logger.error(f"Error finding policy document: {str(e)}")
            return {"error": f"Could not find policy document: {str(e)}", 
                    "suggestion": "Check the logs for more details and ensure your Cloud Storage bucket is properly configured."}
    
    def get_wellness_guide(self, guide_type: str) -> Dict[str, Any]:
        """
        Find and retrieve a wellness guide by type.
        
        Args:
            guide_type: Type of guide (e.g., "mental_health", "work_life_balance", "remote_work")
            
        Returns:
            Dict with wellness guide content
        """
        try:
            if not self.storage_client or not self.bucket:
                logger.error("Storage client or bucket not initialized")
                return {"error": "Storage service not properly initialized", "suggestion": "Check your Cloud Storage configuration"}
                
            guides_prefix = "wellness_guides/"
            logger.info(f"Looking for wellness guide with type: {guide_type}")
            
            # Try to list blobs to see if we have access
            try:
                blobs = list(self.bucket.list_blobs(prefix=guides_prefix, max_results=10))
                logger.info(f"Found {len(blobs)} wellness guide blobs")
            except Exception as e:
                logger.error(f"Error listing wellness guides: {str(e)}")
                return {"error": f"Could not access wellness guides: {str(e)}", "suggestion": "Check your Google Cloud credentials and permissions"}
            
            # Map of search terms to likely filenames or directories - expanded
            guide_mapping = {
                # Mental health
                "mental health": "mental_health/mental_health_guide.md",
                "mental": "mental_health/mental_health_guide.md",
                "stress": "mental_health/stress_management_guide.md",
                "anxiety": "mental_health/anxiety_guide.md",
                "depression": "mental_health/depression_guide.md",
                
                # Work-life balance
                "work life balance": "work_life_balance/work_life_balance_guide.md",
                "balance": "work_life_balance/work_life_balance_guide.md",
                "burnout": "work_life_balance/burnout_prevention_guide.md",
                
                # Remote work
                "remote work": "remote_work_guide.md",
                "wfh": "remote_work_guide.md",
                "home office": "remote_work_guide.md",
                
                # Physical wellness
                "physical": "physical_wellness/physical_wellness_guide.md",
                "exercise": "physical_wellness/exercise_guide.md",
                "ergonomic": "physical_wellness/ergonomic_guide.md",
                
                # Other wellness areas
                "nutrition": "nutrition_guide.md",
                "sleep": "sleep_guide.md",
                "meditation": "meditation_guide.md",
                "mindfulness": "mindfulness_guide.md"
            }
            
            # Normalize the guide type
            guide_type_lower = guide_type.lower()
            
            # Look for an exact match in our mapping
            target_file = None
            for key, filename in guide_mapping.items():
                if key in guide_type_lower:
                    candidate_file = guides_prefix + filename
                    logger.info(f"Found potential guide match: {candidate_file}")
                    
                    # Check if this file actually exists
                    blob = self.bucket.blob(candidate_file)
                    if blob.exists():
                        target_file = candidate_file
                        logger.info(f"Verified guide file exists: {target_file}")
                        break
                    else:
                        logger.warning(f"Mapped guide file does not exist: {candidate_file}")
            
            # If no direct match found, try to find a guide that contains the search term
            if not target_file:
                logger.info("No direct mapping found, searching for partial matches in blob names")
                for blob in blobs:
                    if guide_type_lower in blob.name.lower() and not blob.name.endswith('.keep'):
                        target_file = blob.name
                        logger.info(f"Found partial match: {target_file}")
                        break
            
            # If we found a matching file, get its content
            if target_file:
                logger.info(f"Retrieving content for wellness guide: {target_file}")
                return self.get_resource_content(target_file)
            else:
                # If no specific match, try a generic stress guide as fallback for stress-related queries
                if "stress" in guide_type_lower or "anxiety" in guide_type_lower:
                    generic_stress_guide = guides_prefix + "mental_health/stress_management_guide.md"
                    blob = self.bucket.blob(generic_stress_guide)
                    if blob.exists():
                        logger.info(f"No specific guide found, using generic stress guide: {generic_stress_guide}")
                        return self.get_resource_content(generic_stress_guide)
                    
                    # Try even more generic mental health guide
                    generic_mental_guide = guides_prefix + "mental_health/mental_health_guide.md"
                    blob = self.bucket.blob(generic_mental_guide)
                    if blob.exists():
                        logger.info(f"No specific guide found, using generic mental health guide: {generic_mental_guide}")
                        return self.get_resource_content(generic_mental_guide)
                
                # List available guides for diagnostic purposes
                available_guides = [
                    blob.name.replace(guides_prefix, "") 
                    for blob in blobs 
                    if not blob.name.endswith('.keep') and blob.name != guides_prefix
                ]
                logger.warning(f"No wellness guide found for '{guide_type}'. Available guides: {available_guides}")
                
                return {
                    "message": f"No wellness guide found for '{guide_type}'",
                    "available_guides": available_guides,
                    "suggestion": "You could create a wellness guide with this name and upload it to the Cloud Storage bucket."
                }
                
        except Exception as e:
            logger.error(f"Error finding wellness guide: {str(e)}")
            return {"error": f"Could not find wellness guide: {str(e)}", 
                    "suggestion": "Check the logs for more details and ensure your Cloud Storage bucket is properly configured."}
    
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