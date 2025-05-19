"""Privacy callbacks for the Wellness Agent."""

import copy
from typing import Dict, Any, Optional

def privacy_callback(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    A callback to ensure proper privacy controls are enforced.
    
    This callback:
    1. Checks user role and permissions
    2. Filters sensitive data based on role
    3. Logs access attempts for compliance
    4. Applies privacy transformations as needed
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with privacy protections applied
    """
    # Make a copy to avoid modifying the original
    filtered_state = copy.deepcopy(state)
    
    # Get current user role from state
    user_role = filtered_state.get("user_role", "unknown")
    
    # Log access for compliance (would be implemented with proper logging in production)
    print(f"Privacy callback executed for user role: {user_role}")
    
    # Filter the state based on role
    if user_role == "employee":
        # Employees can only see their own data
        _filter_for_employee(filtered_state)
    elif user_role == "hr":
        # HR can see anonymous aggregated data and manage requests
        _filter_for_hr(filtered_state)
    elif user_role == "employer":
        # Employers can only see organization-level aggregated data
        _filter_for_employer(filtered_state)
    
    return filtered_state

def _filter_for_employee(state: Dict[str, Any]) -> None:
    """
    Filter state for employee role.
    
    Args:
        state: State to filter (modified in-place)
    """
    # Keep personal data but remove organization-wide data
    if "organization_data" in state:
        del state["organization_data"]
    
    # Only keep aggregated data about the user's department if it exists
    if "department_data" in state:
        state["department_data"] = {"aggregated_only": True}
    
    # Sanitize request data to only show the employee's own requests
    if "accommodation_requests" in state and "user_id" in state:
        user_id = state["user_id"]
        state["accommodation_requests"] = [
            req for req in state["accommodation_requests"]
            if req.get("user_id") == user_id
        ]

def _filter_for_hr(state: Dict[str, Any]) -> None:
    """
    Filter state for HR role.
    
    Args:
        state: State to filter (modified in-place)
    """
    # Remove individual employee health data
    if "employee_health_data" in state:
        del state["employee_health_data"]
    
    # Only keep anonymized symptom data
    if "symptom_data" in state:
        # Replace with anonymized version
        if "anonymized_symptom_data" in state:
            state["symptom_data"] = state["anonymized_symptom_data"]
        else:
            del state["symptom_data"]
    
    # Replace personal details in accommodation requests with anonymous versions
    if "accommodation_requests" in state:
        for request in state["accommodation_requests"]:
            # Only show personal details if 'anonymity_level' is 'shareable'
            if request.get("anonymity_level") != "shareable":
                if "user_id" in request:
                    request["user_id"] = "anonymous"
                if "profile_id" in request:
                    request["profile_id"] = "anonymous"
                if "notes" in request:
                    request["notes"] = "Details redacted for privacy"

def _filter_for_employer(state: Dict[str, Any]) -> None:
    """
    Filter state for employer role.
    
    Args:
        state: State to filter (modified in-place)
    """
    # Employers can only see organizational metrics and aggregated data
    
    # Remove all individual employee data
    keys_to_remove = [
        "employee_health_data", 
        "symptom_data",
        "accommodation_requests"
    ]
    
    for key in keys_to_remove:
        if key in state:
            del state[key]
    
    # Ensure metrics meet minimum group size requirements
    if "organizational_metrics" in state:
        metrics = state["organizational_metrics"]
        
        # Filter out any metrics with fewer than 5 employees
        if "department_metrics" in metrics:
            metrics["department_metrics"] = {
                dept: data for dept, data in metrics["department_metrics"].items()
                if data.get("employee_count", 0) >= 5
            }
        
        # Minimum employee count for any metric
        min_count = 5
        
        # Filter any other metrics that don't meet minimum count
        for metric_key in list(metrics.keys()):
            if metric_key.endswith("_metrics") and isinstance(metrics[metric_key], dict):
                metrics[metric_key] = {
                    k: v for k, v in metrics[metric_key].items()
                    if not isinstance(v, dict) or v.get("employee_count", 0) >= min_count
                } 