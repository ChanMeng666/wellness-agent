"""
Data access tools for wellness agent that respect privacy.
"""

from google.adk.tools import FunctionTool
from typing import Dict, Any, Optional
from wellness_agent.services.db.firestore_service import FirestoreService
from wellness_agent.services.db.storage_service import StorageService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
firestore_service = FirestoreService()
storage_service = StorageService()

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
        The content of the policy document
    """
    logger.info(f"Getting policy document for {policy_type}")
    return storage_service.find_policy_document(policy_type)

def get_wellness_guide(guide_type: str) -> Dict[str, Any]:
    """
    Find and retrieve a wellness guide.
    
    Args:
        guide_type: Type of guide (e.g., "mental_health", "work_life_balance", "remote_work")
        
    Returns:
        The content of the wellness guide
    """
    logger.info(f"Getting wellness guide for {guide_type}")
    return storage_service.get_wellness_guide(guide_type)

def get_wellness_report(report_type: str) -> Dict[str, Any]:
    """
    Retrieve an aggregated wellness report.
    
    Args:
        report_type: Type of report (e.g., "wellness", "leave_trends", "department")
        
    Returns:
        The content of the report
    """
    logger.info(f"Getting wellness report for {report_type}")
    return storage_service.get_report(report_type)

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

wellness_guide_tool = FunctionTool(
    func=get_wellness_guide
)

wellness_report_tool = FunctionTool(
    func=get_wellness_report
)

list_resources_tool = FunctionTool(
    func=list_available_resources
)

# Export all tools
__all__ = [
    "department_stats_tool", 
    "leave_trends_tool",
    "health_trends_tool",
    "wellness_programs_tool",
    "department_leave_rates_tool",
    "policy_document_tool",
    "wellness_guide_tool",
    "wellness_report_tool",
    "list_resources_tool"
] 