"""
Cloud Storage service for accessing wellness resources.
"""

from google.cloud import storage
import logging
import json
import csv
import io
import os
import datetime
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
    
    def generate_signed_url(self, blob_name: str, expiration_minutes: int = 60) -> Dict[str, Any]:
        """
        Generate a signed URL for a Cloud Storage blob that allows temporary access.
        
        Args:
            blob_name: The name of the blob to generate a URL for
            expiration_minutes: Number of minutes the URL should be valid for (default: 60)
            
        Returns:
            Dict with signed URL information
        """
        try:
            if not self.storage_client or not self.bucket:
                logger.error("Storage client or bucket not initialized")
                return {"error": "Storage service not properly initialized", "suggestion": "Check your Cloud Storage configuration"}
                
            blob = self.bucket.blob(blob_name)
            logger.info(f"Generating signed URL for resource: {blob_name}")
            
            # First check if the blob exists
            if not blob.exists():
                logger.warning(f"Resource not found: {blob_name}")
                return {
                    "error": f"Resource not found: {blob_name}",
                    "suggestion": "Check if the file exists in your Cloud Storage bucket or create it"
                }
            
            # Generate a signed URL
            expiration = datetime.timedelta(minutes=expiration_minutes)
            try:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=expiration,
                    method="GET"
                )
                logger.info(f"Generated signed URL for {blob_name}, valid for {expiration_minutes} minutes")
                
                # Determine the content type for the response
                content_type = "application/octet-stream"  # Default
                if blob_name.endswith('.md'):
                    content_type = "text/markdown"
                elif blob_name.endswith('.json'):
                    content_type = "application/json"
                elif blob_name.endswith('.csv'):
                    content_type = "text/csv"
                elif blob_name.endswith('.pdf'):
                    content_type = "application/pdf"
                elif blob_name.endswith('.txt'):
                    content_type = "text/plain"
                
                return {
                    "message": f"Generated signed URL for {blob_name}",
                    "url": url,
                    "expires_in_minutes": expiration_minutes,
                    "content_type": content_type,
                    "file_name": blob_name.split('/')[-1]  # Extract filename from path
                }
            except Exception as e:
                logger.error(f"Error generating signed URL for {blob_name}: {str(e)}")
                return {
                    "error": f"Could not generate signed URL: {str(e)}",
                    "suggestion": "Check your Google Cloud permissions and service account configuration"
                }
                
        except Exception as e:
            logger.error(f"Error generating signed URL for {blob_name}: {str(e)}")
            return {
                "error": f"Could not generate signed URL: {str(e)}",
                "resource": blob_name,
                "suggestion": "Check your Cloud Storage permissions and bucket configuration"
            }
    
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
            
            # Generate a signed URL for the file
            signed_url_info = self.generate_signed_url(blob_name)
            has_url = "url" in signed_url_info
            
            # Handle different file types
            if blob_name.endswith('.md'):
                # Return markdown directly
                result = {
                    "message": f"Retrieved {blob_name}",
                    "content_type": "text/markdown",
                    "content": content
                }
                if has_url:
                    result["url"] = signed_url_info["url"]
                    result["expires_in_minutes"] = signed_url_info["expires_in_minutes"]
                return result
            elif blob_name.endswith('.json'):
                # Parse JSON
                try:
                    data = json.loads(content)
                    result = {
                        "message": f"Retrieved {blob_name}",
                        "content_type": "application/json",
                        "data": data
                    }
                    if has_url:
                        result["url"] = signed_url_info["url"]
                        result["expires_in_minutes"] = signed_url_info["expires_in_minutes"]
                    return result
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
                    result = {
                        "message": f"Retrieved {blob_name}",
                        "content_type": "text/csv",
                        "headers": csv_reader.fieldnames,
                        "rows": rows
                    }
                    if has_url:
                        result["url"] = signed_url_info["url"]
                        result["expires_in_minutes"] = signed_url_info["expires_in_minutes"]
                    return result
                except Exception as csv_error:
                    logger.error(f"Error parsing CSV in {blob_name}: {str(csv_error)}")
                    return {
                        "error": f"Error parsing CSV: {str(csv_error)}",
                        "content_preview": content[:100] + "..." if len(content) > 100 else content,
                        "suggestion": "The file exists but could not be parsed as CSV"
                    }
            else:
                # Default to text
                result = {
                    "message": f"Retrieved {blob_name}",
                    "content_type": "text/plain",
                    "content": content
                }
                if has_url:
                    result["url"] = signed_url_info["url"]
                    result["expires_in_minutes"] = signed_url_info["expires_in_minutes"]
                return result
                
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
            policy_type: Type of policy document (e.g., "leave", "remote_work")
            
        Returns:
            Dict with policy document content
        """
        try:
            if not self.storage_client or not self.bucket:
                logger.error("Storage client or bucket not initialized")
                return {"error": "Storage service not properly initialized", "suggestion": "Check your Cloud Storage configuration"}
                
            policies_prefix = "policy_documents/"
            logger.info(f"Looking for policy document with type: {policy_type}")
            
            # Try to list blobs to see if we have access
            try:
                blobs = list(self.bucket.list_blobs(prefix=policies_prefix, max_results=10))
                logger.info(f"Found {len(blobs)} policy document blobs")
            except Exception as e:
                logger.error(f"Error listing policy documents: {str(e)}")
                return {"error": f"Could not access policy documents: {str(e)}", "suggestion": "Check your Google Cloud credentials and permissions"}
                
            # Normalize policy type for searching
            policy_type_lower = policy_type.lower()
            
            # Look for any policy document that matches the type
            target_file = None
            
            # First try direct matching with policy type
            for blob in blobs:
                blob_name = blob.name.lower()
                if blob_name.endswith('.keep'):
                    continue
                
                # Check if policy type appears in the filename
                if policy_type_lower in blob_name:
                    target_file = blob.name
                    logger.info(f"Found direct policy match: {target_file}")
                    break
            
            # Try common policy synonyms if no direct match
            if not target_file:
                # Map of common policy terms to search
                policy_synonyms = {
                    "leave": ["leave", "absence", "time_off", "pto", "vacation"],
                    "remote_work": ["remote", "wfh", "telework", "work_from_home"],
                    "accommodation": ["accommodation", "disability", "ada", "accessibility"],
                    "wellness": ["wellness", "health", "wellbeing", "benefits"]
                }
                
                # See if our policy type matches any known categories
                search_terms = []
                for category, terms in policy_synonyms.items():
                    if policy_type_lower in terms or category == policy_type_lower:
                        search_terms = terms
                        break
                
                # If we have search terms, look for any matching policies
                if search_terms:
                    for blob in blobs:
                        blob_name = blob.name.lower()
                        if blob_name.endswith('.keep'):
                            continue
                            
                        for term in search_terms:
                            if term in blob_name:
                                target_file = blob.name
                                logger.info(f"Found policy match via synonym {term}: {target_file}")
                                break
                        
                        if target_file:
                            break
            
            # If we found a matching file, get its content
            if target_file:
                logger.info(f"Retrieving content for policy document: {target_file}")
                result = self.get_resource_content(target_file)
                # Add the file path to the result
                result["file_path"] = target_file
                return result
            else:
                # List available policies for diagnostic purposes
                available_policies = [
                    blob.name.replace(policies_prefix, "") 
                    for blob in blobs 
                    if not blob.name.endswith('.keep') and blob.name != policies_prefix
                ]
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
                
            # Look for guides that match the requested type
            guide_type_lower = guide_type.lower()
            
            # First try exact match in a directory with the guide type name
            target_file = None
            
            # Check for direct match in directory name
            direct_match_prefix = f"{guides_prefix}{guide_type_lower}/"
            direct_matches = [
                blob.name for blob in blobs 
                if blob.name.startswith(direct_match_prefix) and 
                not blob.name.endswith('.keep') and 
                "guide" in blob.name.lower()
            ]
            
            if direct_matches:
                target_file = direct_matches[0]
                logger.info(f"Found direct directory match: {target_file}")
            
            # If no direct directory match, try to find a file with the guide type in its name
            if not target_file:
                # Look for any guide that contains the guide_type in its name
                for blob in blobs:
                    blob_name = blob.name.lower()
                    # Skip directory markers and non-markdown files
                    if blob_name.endswith('.keep') or not blob_name.endswith('.md'):
                        continue
                        
                    # Look for the guide type in the filename
                    # Prioritize filenames that explicitly mention guides
                    if guide_type_lower in blob_name and "guide" in blob_name:
                        target_file = blob.name
                        logger.info(f"Found guide with type in filename: {target_file}")
                        break
            
            # If no guide with guide_type in name, try a more general approach
            if not target_file:
                for blob in blobs:
                    blob_name = blob.name.lower()
                    # Check if any part of the guide type is in any part of the filepath
                    if not blob_name.endswith('.keep') and blob_name.endswith('.md'):
                        path_parts = guide_type_lower.split('_')
                        for part in path_parts:
                            if part in blob_name and len(part) >= 4:  # Avoid matching too short terms
                                target_file = blob.name
                                logger.info(f"Found guide with partial match: {target_file}")
                                break
                        if target_file:
                            break
            
            # If we found a matching file, get its content
            if target_file:
                logger.info(f"Retrieving content for wellness guide: {target_file}")
                result = self.get_resource_content(target_file)
                # Add the file path to the result
                result["file_path"] = target_file
                return result
            else:
                # If no specific match, try a generic stress guide as fallback for stress-related queries
                if "stress" in guide_type_lower or "anxiety" in guide_type_lower:
                    generic_stress_guide = guides_prefix + "mental_health/stress_management_guide.md"
                    blob = self.bucket.blob(generic_stress_guide)
                    if blob.exists():
                        logger.info(f"No specific guide found, using generic stress guide: {generic_stress_guide}")
                        result = self.get_resource_content(generic_stress_guide)
                        result["file_path"] = generic_stress_guide
                        return result
                    
                    # Try even more generic mental health guide
                    generic_mental_guide = guides_prefix + "mental_health/mental_health_guide.md"
                    blob = self.bucket.blob(generic_mental_guide)
                    if blob.exists():
                        logger.info(f"No specific guide found, using generic mental health guide: {generic_mental_guide}")
                        result = self.get_resource_content(generic_mental_guide)
                        result["file_path"] = generic_mental_guide
                        return result
                
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
    
    def get_report(self, report_type: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Find and retrieve a report by type.
        
        Args:
            report_type: Type of report (e.g., "wellness", "leave_trends", "department")
            filters: Optional filters to apply to the report
            
        Returns:
            Dict with report content
        """
        try:
            if not self.storage_client or not self.bucket:
                logger.error("Storage client or bucket not initialized")
                return {"error": "Storage service not properly initialized", "suggestion": "Check your Cloud Storage configuration"}
                
            reports_prefix = "aggregated_reports/"
            logger.info(f"Looking for report with type: {report_type}")
            
            # Try to list blobs to see if we have access
            try:
                blobs = list(self.bucket.list_blobs(prefix=reports_prefix, max_results=10))
                logger.info(f"Found {len(blobs)} report blobs")
            except Exception as e:
                logger.error(f"Error listing reports: {str(e)}")
                return {"error": f"Could not access reports: {str(e)}", "suggestion": "Check your Google Cloud credentials and permissions"}
                
            # Normalize report type for searching
            report_type_lower = report_type.lower()
            
            # Look for any report that matches the type
            target_file = None
            
            # First try direct matching with report type
            for blob in blobs:
                blob_name = blob.name.lower()
                if blob_name.endswith('.keep'):
                    continue
                
                # Check if report type appears in the filename
                if report_type_lower in blob_name:
                    target_file = blob.name
                    logger.info(f"Found direct report match: {target_file}")
                    break
            
            # If no direct match, try alternative terms
            if not target_file:
                # Map of common report terms to search
                report_synonyms = {
                    "wellness": ["wellness", "wellbeing", "health"],
                    "leave_trends": ["leave", "absence", "time_off"],
                    "department": ["department", "team", "group"],
                    "engagement": ["engagement", "satisfaction", "survey"],
                    "roi": ["roi", "return", "investment", "financial"]
                }
                
                # See if our report type matches any known categories
                search_terms = []
                for category, terms in report_synonyms.items():
                    if report_type_lower in terms or category == report_type_lower:
                        search_terms = terms
                        break
                
                # If we have search terms, look for any matching reports
                if search_terms:
                    for blob in blobs:
                        blob_name = blob.name.lower()
                        if blob_name.endswith('.keep'):
                            continue
                            
                        for term in search_terms:
                            if term in blob_name:
                                target_file = blob.name
                                logger.info(f"Found report match via synonym {term}: {target_file}")
                                break
                        
                        if target_file:
                            break
            
            # If we found a matching file, get its content
            if target_file:
                logger.info(f"Retrieving content for report: {target_file}")
                result = self.get_resource_content(target_file)
                # Add the file path to the result
                result["file_path"] = target_file
                return result
            else:
                # List available reports for diagnostic purposes
                available_reports = [
                    blob.name.replace(reports_prefix, "") 
                    for blob in blobs 
                    if not blob.name.endswith('.keep') and blob.name != reports_prefix
                ]
                logger.warning(f"No report found for '{report_type}'. Available reports: {available_reports}")
                
                return {
                    "message": f"No report found for '{report_type}'",
                    "available_reports": available_reports,
                    "suggestion": "You could create a report with this name and upload it to the Cloud Storage bucket."
                }
                
        except Exception as e:
            logger.error(f"Error finding report: {str(e)}")
            return {"error": f"Could not find report: {str(e)}", 
                    "suggestion": "Check the logs for more details and ensure your Cloud Storage bucket is properly configured."} 