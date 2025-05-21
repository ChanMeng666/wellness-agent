"""
Data access tools for wellness agent that respect privacy.
"""

from google.adk.tools import FunctionTool
from typing import Dict, Any, Optional
from wellness_agent.services.db.firestore_service import FirestoreService
from wellness_agent.services.db.storage_service import StorageService
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
firestore_service = FirestoreService()
storage_service = StorageService()

# Initialize service for data operations
use_mock = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
logger.info(f"Initializing data tools with USE_MOCK_SERVICES={use_mock}")

def get_department_stats(department: Optional[str] = None, months: int = 3) -> Dict[str, Any]:
    """
    Get anonymized department statistics.
    
    Args:
        department: Optional specific department to analyze (Engineering, Marketing, Operations, Sales, HR, Finance, or Company-wide)
        months: Number of months to retrieve (default: 3)
        
    Returns:
        Aggregated department metrics with no individual employee data
    """
    logger.info(f"Getting department stats for {department if department else 'all'} over {months} months")
    return firestore_service.get_department_stats(department, months)

def get_leave_trends(department: Optional[str] = None, months: int = 6) -> Dict[str, Any]:
    """
    Get anonymized leave trends.
    
    Args:
        department: Optional specific department to analyze
        months: Number of months to analyze (default: 6)
        
    Returns:
        Aggregated leave data with no individual employee information
    """
    logger.info(f"Getting leave trends for {department if department else 'all'} over {months} months")
    return firestore_service.get_leave_trends(department, months)

def get_health_trends(trend_type: str = "stress_levels", months: int = 6) -> Dict[str, Any]:
    """
    Get anonymized health trend data.
    
    Args:
        trend_type: Type of health trend to analyze (stress_levels, work_life_balance, physical_activity, wellness_program_effectiveness)
        months: Number of months to analyze (default: 6)
        
    Returns:
        Aggregated health trends with no individual employee information
    """
    logger.info(f"Getting health trends for {trend_type} over {months} months")
    return firestore_service.get_health_trends(trend_type, months)

def get_wellness_programs() -> Dict[str, Any]:
    """
    Get information about wellness programs.
    
    Returns:
        Information about wellness programs and their effectiveness
    """
    logger.info("Getting wellness programs")
    return firestore_service.get_wellness_programs()

def get_department_leave_rates() -> Dict[str, Any]:
    """
    Get anonymized leave rates by department.
    
    Returns:
        Department leave rates sorted from highest to lowest
    """
    logger.info("Getting department leave rates")
    return firestore_service.get_department_leave_rates()

def get_policy_document(policy_type: str) -> Dict[str, Any]:
    """
    Find and retrieve a company policy document.
    
    Args:
        policy_type: Type of policy (e.g., "leave", "remote_work", "accommodation")
        
    Returns:
        The content of the policy document with a signed URL for file access
    """
    logger.info(f"Getting policy document for {policy_type}")
    # Get the policy document content
    policy_result = storage_service.find_policy_document(policy_type)
    
    # If the policy was found and has a file path, generate a signed URL
    if "error" not in policy_result and "file_path" in policy_result:
        file_path = policy_result["file_path"]
        # Get a signed URL for the file - use a longer expiration time (120 minutes)
        url_result = storage_service.generate_signed_url(file_path, expiration_minutes=120)
        
        if "url" in url_result:
            # Add the URL to the policy result
            policy_result["url"] = url_result["url"]
            policy_result["expires_in_minutes"] = url_result["expires_in_minutes"]
            logger.info(f"Successfully generated signed URL for policy document: {policy_type}")
        else:
            # Log the error but still return the policy content
            error_msg = url_result.get("error", "Unknown error generating signed URL")
            logger.error(f"Failed to generate signed URL for policy {policy_type}: {error_msg}")
            policy_result["url_error"] = error_msg
    
    return policy_result

def get_organization_report(report_type: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retrieve an organization-level aggregated report.
    
    Args:
        report_type: Type of report (e.g., "wellness", "leave_trends")
        filters: Optional filters to apply to the report
        
    Returns:
        The report data
    """
    filters = filters or {}
    logger.info(f"Getting organization report for {report_type} with filters {filters}")
    return storage_service.get_report(report_type, filters)

def get_employee_metrics(employee_id: str, metric_type: str) -> Dict[str, Any]:
    """
    Retrieve employee-specific wellness metrics.
    
    Args:
        employee_id: The employee ID
        metric_type: Type of metric (e.g., "wellness", "leave", "performance")
        
    Returns:
        The employee metrics data
    """
    logger.info(f"Getting employee metrics for {employee_id} of type {metric_type}")
    # For now we'll just return a placeholder. In the future, this would query a metrics service.
    return {
        "message": f"Retrieved {metric_type} metrics for employee {employee_id}",
        "metrics": {
            "type": metric_type,
            "employee_id": employee_id,
            "data": [
                {"date": "2023-01-01", "value": 7.5},
                {"date": "2023-02-01", "value": 8.0},
                {"date": "2023-03-01", "value": 7.2},
                {"date": "2023-04-01", "value": 8.3}
            ]
        }
    }

def get_department_metrics(department_id: str, metric_type: str) -> Dict[str, Any]:
    """
    Retrieve department-level wellness metrics.
    
    Args:
        department_id: The department ID
        metric_type: Type of metric (e.g., "wellness", "leave", "performance")
        
    Returns:
        The department metrics data
    """
    logger.info(f"Getting department metrics for {department_id} of type {metric_type}")
    # For now we'll just return a placeholder. In the future, this would query a metrics service.
    return {
        "message": f"Retrieved {metric_type} metrics for department {department_id}",
        "metrics": {
            "type": metric_type,
            "department_id": department_id,
            "data": [
                {"date": "2023-01-01", "value": 7.8},
                {"date": "2023-02-01", "value": 7.9},
                {"date": "2023-03-01", "value": 8.1},
                {"date": "2023-04-01", "value": 8.0}
            ]
        }
    }

def get_wellness_guide(guide_type: str) -> Dict[str, Any]:
    """
    Find and retrieve a wellness guide.
    
    Args:
        guide_type: Type of guide (e.g., "mental_health", "work_life_balance", "remote_work")
        
    Returns:
        The content of the wellness guide with a signed URL for file access
    """
    logger.info(f"Getting wellness guide for {guide_type}")
    # Get the guide content
    guide_result = storage_service.get_wellness_guide(guide_type)
    
    # If the guide was found and has a file path, generate a signed URL
    if "error" not in guide_result and "file_path" in guide_result:
        file_path = guide_result["file_path"]
        # Get a signed URL for the file - use a longer expiration time (120 minutes)
        url_result = storage_service.generate_signed_url(file_path, expiration_minutes=120)
        
        if "url" in url_result:
            # Add the URL to the guide result
            guide_result["url"] = url_result["url"]
            guide_result["expires_in_minutes"] = url_result["expires_in_minutes"]
            logger.info(f"Successfully generated signed URL for wellness guide: {guide_type}")
        else:
            # Log the error but still return the guide content
            error_msg = url_result.get("error", "Unknown error generating signed URL")
            logger.error(f"Failed to generate signed URL for wellness guide {guide_type}: {error_msg}")
            guide_result["url_error"] = error_msg
    
    return guide_result

def get_file_link(file_path: str) -> Dict[str, Any]:
    """
    Generate a signed URL for a specific file in Cloud Storage.
    
    Args:
        file_path: The path of the file in Cloud Storage
        
    Returns:
        Dict containing the signed URL and metadata
    """
    logger.info(f"Generating link for file: {file_path}")
    # Use a longer expiration time for more reliability (120 minutes)
    result = storage_service.generate_signed_url(file_path, expiration_minutes=120)
    
    if "error" in result:
        logger.error(f"Failed to generate file link for {file_path}: {result.get('error')}")
    else:
        logger.info(f"Successfully generated signed URL for file: {file_path}")
        
    return result

def get_wellness_report(report_type: str) -> Dict[str, Any]:
    """
    Retrieve an aggregated wellness report.
    
    Args:
        report_type: Type of report (e.g., "wellness", "leave_trends", "department")
        
    Returns:
        The content of the report with a signed URL for file access
    """
    logger.info(f"Getting wellness report for {report_type}")
    # Get the report content
    report_result = storage_service.get_report(report_type)
    
    # If the report was found and has a file path, generate a signed URL
    if "error" not in report_result and "file_path" in report_result:
        file_path = report_result["file_path"]
        # Get a signed URL for the file - use a longer expiration time (120 minutes)
        url_result = storage_service.generate_signed_url(file_path, expiration_minutes=120)
        
        if "url" in url_result:
            # Add the URL to the report result
            report_result["url"] = url_result["url"]
            report_result["expires_in_minutes"] = url_result["expires_in_minutes"]
            logger.info(f"Successfully generated signed URL for wellness report: {report_type}")
        else:
            # Log the error but still return the report content
            error_msg = url_result.get("error", "Unknown error generating signed URL")
            logger.error(f"Failed to generate signed URL for report {report_type}: {error_msg}")
            report_result["url_error"] = error_msg
    
    return report_result

def list_available_resources(resource_type: Optional[str] = None) -> Dict[str, Any]:
    """
    List available wellness resources.
    
    Args:
        resource_type: Optional type of resource to list (e.g., "wellness_guides", "policy_documents", "aggregated_reports")
        
    Returns:
        List of available resources
    """
    prefix = f"{resource_type}/" if resource_type else ""
    logger.info(f"Listing resources with prefix: {prefix}")
    return storage_service.list_resources(prefix)

# Create function tools
department_stats_tool = FunctionTool(
    func=get_department_stats
)

leave_trends_tool = FunctionTool(
    func=get_leave_trends
)

health_trends_tool = FunctionTool(
    func=get_health_trends
)

wellness_programs_tool = FunctionTool(
    func=get_wellness_programs
)

department_leave_rates_tool = FunctionTool(
    func=get_department_leave_rates
)

policy_document_tool = FunctionTool(
    func=get_policy_document
)

organization_report_tool = FunctionTool(
    func=get_organization_report
)

employee_metrics_tool = FunctionTool(
    func=get_employee_metrics
)

department_metrics_tool = FunctionTool(
    func=get_department_metrics
)

wellness_guide_tool = FunctionTool(
    func=get_wellness_guide
)

wellness_report_tool = FunctionTool(
    func=get_wellness_report
)

list_resources_tool = FunctionTool(
    func=list_available_resources
)

file_link_tool = FunctionTool(
    func=get_file_link
)

# Export all tools
__all__ = [
    "department_stats_tool", 
    "leave_trends_tool",
    "health_trends_tool",
    "wellness_programs_tool",
    "department_leave_rates_tool",
    "policy_document_tool",
    "organization_report_tool",
    "employee_metrics_tool",
    "department_metrics_tool",
    "wellness_guide_tool",
    "wellness_report_tool",
    "list_resources_tool",
    "file_link_tool"
] 