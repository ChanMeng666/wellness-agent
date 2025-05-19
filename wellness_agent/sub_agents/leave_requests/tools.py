"""Tools for leave requests agent."""

import os
import uuid
from typing import Dict, List, Optional, Literal, Any, Union
from datetime import datetime, timedelta
from google.adk.tools import FunctionTool

from wellness_agent.services.service_factory import ServiceFactory

# Initialize service factory
service_factory = ServiceFactory()

# Tool handler functions
def submit_quick_request_handler(
    request_type: Literal["sick_day", "remote_work", "flexible_hours", "reduced_meetings"],
    start_date: str,
    end_date: Optional[str] = None,
    disclosure_level: Literal["no_reason", "work_impact_only", "general_health"] = "no_reason",
    work_impact_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit a quick, low-friction leave or accommodation request.
    
    Args:
        request_type: The type of leave or accommodation requested
        start_date: When the request should begin (YYYY-MM-DD)
        end_date: When the request should end, if applicable (YYYY-MM-DD)
        disclosure_level: How much health information to share with manager
        work_impact_notes: Optional notes about work impact (not health details)
        
    Returns:
        Confirmation and next steps
    """
    try:
        # In a real implementation, we would get the profile_id from authentication
        # For demo purposes, we'll use a mock profile ID
        employee_id = os.getenv("DEMO_PROFILE_ID", "demo_profile_123")
        
        # Get the leave request service
        leave_request_service = service_factory.get_leave_request_service()
        
        # Create the leave request
        leave_request = leave_request_service.create_leave_request(
            employee_id=employee_id,
            request_type=request_type,
            start_date=start_date,
            end_date=end_date,
            disclosure_level=disclosure_level,
            work_impact_notes=work_impact_notes
        )
        
        # Format based on request type
        request_descriptions = {
            "sick_day": "sick leave",
            "remote_work": "remote work",
            "flexible_hours": "flexible hours",
            "reduced_meetings": "reduced meeting schedule"
        }
        
        description = request_descriptions.get(request_type, "leave")
        date_range = f"{start_date}" if start_date == end_date or not end_date else f"{start_date} to {end_date}"
        
        # Create notification messages based on disclosure level
        manager_notifications = {
            "no_reason": "Team member will be unavailable on the specified dates.",
            "work_impact_only": f"Team member will be unavailable. Notes: {work_impact_notes}",
            "general_health": f"Team member will be unavailable due to health reasons. Notes: {work_impact_notes}"
        }
        
        notification = manager_notifications.get(disclosure_level, manager_notifications["no_reason"])
        
        return {
            "status": "success",
            "message": f"Your request for {description} on {date_range} has been submitted.",
            "request_id": leave_request.request_id,
            "what_happens_next": [
                f"Your manager will receive the following notification: '{notification}'",
                "Your calendar will be updated automatically with your status",
                "You can check the status of your request below"
            ]
        }
    except Exception as e:
        print(f"Error submitting quick request: {e}")
        # Fall back to mock response for demonstration
        request_id = f"LR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        return {
            "status": "success",
            "message": f"Your request has been submitted (mock).",
            "request_id": request_id,
            "what_happens_next": [
                "Your manager will be notified.",
                "You can check the status of your request below."
            ]
        }

def create_accommodation_plan_handler(
    accommodation_types: List[Literal["remote_work", "flexible_schedule", "physical_modification", "meeting_adjustments", "responsibility_adjustments"]],
    duration: Literal["2_weeks", "1_month", "3_months", "6_months", "ongoing"],
    frequency: Literal["daily", "specific_days", "as_needed", "continuous"],
    specific_days: Optional[List[str]] = None,
    functional_limitations: Optional[List[str]] = None,
    privacy_level: Literal["minimum", "limited", "standard"] = "minimum",
    manager_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a longer-term accommodation plan with appropriate privacy controls.
    
    Args:
        accommodation_types: The types of accommodations being requested
        duration: How long the accommodations are needed
        frequency: How often the accommodations are needed
        specific_days: Required if frequency is "specific_days" (e.g., ["Monday", "Thursday"])
        functional_limitations: Optional descriptions of work-related limitations (not medical details)
        privacy_level: How much detail to share with manager/HR
        manager_notes: Optional notes for manager (focus on work impact, not health)
        
    Returns:
        The created plan and next steps
    """
    try:
        # In a real implementation, we would get the profile_id from authentication
        # For demo purposes, we'll use a mock profile ID
        employee_id = os.getenv("DEMO_PROFILE_ID", "demo_profile_123")
        
        # Get the accommodation plan service
        accommodation_plan_service = service_factory.get_accommodation_plan_service()
        
        # Create the accommodation plan
        plan = accommodation_plan_service.create_accommodation_plan(
            employee_id=employee_id,
            accommodation_types=accommodation_types,
            duration=duration,
            frequency=frequency,
            specific_days=specific_days,
            functional_limitations=functional_limitations,
            privacy_level=privacy_level,
            manager_notes=manager_notes
        )
        
        # Format the accommodation types for display
        accommodation_descriptions = {
            "remote_work": "Remote work arrangement",
            "flexible_schedule": "Flexible schedule",
            "physical_modification": "Workplace physical modifications",
            "meeting_adjustments": "Meeting accommodations",
            "responsibility_adjustments": "Adjusted responsibilities"
        }
        
        accommodations = [accommodation_descriptions.get(accom, accom) for accom in accommodation_types]
        
        # Privacy level determines what information is shared
        privacy_descriptions = {
            "minimum": "Only accommodation details shared, no health information",
            "limited": "Functional limitations shared without specific health details",
            "standard": "General health category shared with specific accommodations"
        }
        
        # Next steps vary based on privacy level and accommodation complexity
        complex_request = len(accommodation_types) > 1 or "physical_modification" in accommodation_types
        
        if complex_request:
            next_steps = [
                "Your request will be reviewed by HR within 2 business days",
                "You may be asked for additional information about workplace needs",
                "A meeting with your manager and HR may be scheduled to discuss implementation"
            ]
        else:
            next_steps = [
                "Your request is being processed automatically",
                "Your manager will be notified with the appropriate level of detail",
                "Implementation will begin on the next business day"
            ]
        
        return {
            "status": "success",
            "message": "Your accommodation plan has been created.",
            "plan_id": plan.plan_id,
            "plan_details": {
                "accommodations": accommodations,
                "duration": duration,
                "frequency": frequency if frequency != "specific_days" else f"specific days: {', '.join(specific_days or [])}",
                "privacy_level": privacy_descriptions.get(privacy_level),
                "review_date": plan.review_date
            },
            "next_steps": next_steps
        }
    except Exception as e:
        print(f"Error creating accommodation plan: {e}")
        # Fall back to mock response for demonstration
        plan_id = f"AP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        return {
            "status": "success",
            "message": "Your accommodation plan has been created (mock).",
            "plan_id": plan_id,
            "plan_details": {
                "accommodations": accommodation_types,
                "duration": duration,
                "frequency": frequency,
                "privacy_level": privacy_level
            },
            "next_steps": [
                "Your request is being processed."
            ]
        }

def check_request_status_handler(
    request_id: Optional[str] = None,
    include_past_requests: bool = False
) -> Dict[str, Any]:
    """
    Check the status of leave and accommodation requests.
    
    Args:
        request_id: Optional specific request to check
        include_past_requests: Whether to include previously completed requests
        
    Returns:
        Current status and next steps
    """
    try:
        # In a real implementation, we would get the profile_id from authentication
        # For demo purposes, we'll use a mock profile ID
        employee_id = os.getenv("DEMO_PROFILE_ID", "demo_profile_123")
        
        # Get the services
        leave_request_service = service_factory.get_leave_request_service()
        accommodation_plan_service = service_factory.get_accommodation_plan_service()
        
        # If a specific request ID is provided, show details for that request
        if request_id:
            # Check if it's a leave request
            if request_id.startswith("LR-"):
                leave_request = leave_request_service.get_leave_request(request_id)
                if leave_request:
                    # Add detailed next steps based on request status
                    if leave_request.status == "approved":
                        next_steps = [
                            "Your calendar has been updated to reflect this request",
                            "Your manager has been notified with your preferred privacy level",
                            "You can cancel or modify this request if needed"
                        ]
                    elif leave_request.status == "pending":
                        next_steps = [
                            "Your request is awaiting approval",
                            "You should receive a response within 1 business day",
                            "You can modify your request if needed"
                        ]
                    else:
                        next_steps = ["This request has been completed."]
                    
                    return {
                        "status": "success",
                        "message": f"Status of request {request_id}: {leave_request.status.upper()}",
                        "request_details": leave_request.to_dict(),
                        "next_steps": next_steps
                    }
            # Check if it's an accommodation plan
            elif request_id.startswith("AP-"):
                plan = accommodation_plan_service.get_accommodation_plan(request_id)
                if plan:
                    # Add detailed next steps based on plan status
                    if plan.status == "approved":
                        next_steps = [
                            "Your accommodation plan has been approved",
                            "Your manager has been notified with your preferred privacy level",
                            "Implementation will begin on the next business day"
                        ]
                    elif plan.status == "pending":
                        next_steps = [
                            "Your plan is under review",
                            "You should receive a response within 2 business days",
                            "You can add additional information if needed"
                        ]
                    else:
                        next_steps = ["This plan has been completed."]
                    
                    return {
                        "status": "success",
                        "message": f"Status of accommodation plan {request_id}: {plan.status.upper()}",
                        "plan_details": plan.to_dict(),
                        "next_steps": next_steps
                    }
            
            # If we get here, the request wasn't found
            return {
                "status": "error",
                "message": f"No request found with ID {request_id}."
            }
        
        # Otherwise, show all recent requests
        leave_requests = leave_request_service.get_leave_requests_by_employee(
            employee_id=employee_id,
            include_completed=include_past_requests
        )
        
        accommodation_plans = accommodation_plan_service.get_accommodation_plans_by_employee(
            employee_id=employee_id,
            active_only=not include_past_requests
        )
        
        # Format the requests for display
        formatted_leave_requests = [request.to_dict() for request in leave_requests]
        formatted_plans = [plan.to_dict() for plan in accommodation_plans]
        
        return {
            "status": "success",
            "message": "Here are your leave and accommodation requests:",
            "leave_requests": formatted_leave_requests,
            "accommodation_plans": formatted_plans
        }
    except Exception as e:
        print(f"Error checking request status: {e}")
        # Fall back to mock response for demonstration
        
        # Sample list of requests for demonstration
        recent_requests = [
            {
                "request_id": "LR-20250520-123",
                "type": "sick_day",
                "status": "approved",
                "dates": "2025-05-22",
                "submitted": "2025-05-20"
            },
            {
                "request_id": "AP-20250518-456",
                "type": "accommodation_plan",
                "status": "under_review",
                "accommodations": ["remote_work", "flexible_schedule"],
                "submitted": "2025-05-18"
            }
        ]
        
        past_requests = [
            {
                "request_id": "LR-20250501-321",
                "type": "flexible_hours",
                "status": "completed",
                "dates": "2025-05-03 to 2025-05-10",
                "submitted": "2025-05-01"
            }
        ]
        
        if request_id:
            mock_request = next((r for r in recent_requests + past_requests if r["request_id"] == request_id), None)
            
            if not mock_request:
                return {
                    "status": "error",
                    "message": f"No request found with ID {request_id}."
                }
            
            return {
                "status": "success",
                "message": f"Status of request {request_id}: {mock_request['status'].upper()} (mock data)",
                "request_details": mock_request,
                "next_steps": ["This is mock data for demonstration purposes."]
            }
            
        return {
            "status": "success",
            "message": "Here are your leave and accommodation requests (mock data):",
            "recent_requests": recent_requests,
            "past_requests": past_requests if include_past_requests else None
        }

def explain_policy_handler(
    policy_type: Literal["sick_leave", "remote_work", "accommodations", "privacy_rights", "all"]
) -> Dict[str, Any]:
    """
    Explain company leave and accommodation policies in accessible language.
    
    Args:
        policy_type: The type of policy to explain
        
    Returns:
        Policy explanation and employee rights
    """
    # This would pull from a company policy database in a real implementation
    
    policy_explanations = {
        "sick_leave": {
            "summary": "Sick leave allows you to take time off when you're not feeling well, without disclosing specific health details.",
            "key_points": [
                "You have 10 paid sick days per year",
                "No doctor's note is required for 1-2 day absences",
                "You can use sick days for mental health, not just physical illness",
                "Sick days can be used for family care as well"
            ],
            "how_to_use": "Simply submit a sick day request through this assistant. Your manager will be notified that you're taking sick leave without any health details.",
            "employee_rights": "You have the right to take sick leave without disclosing your specific health condition to your manager."
        },
        "remote_work": {
            "summary": "Remote work allows you to work from a location other than the office, which can be requested as an accommodation.",
            "key_points": [
                "Regular remote work (1-2 days/week) can be arranged with your manager directly",
                "Extended remote work may require an accommodation request",
                "Remote work accommodations can be temporary or ongoing",
                "All remote workers have the same performance expectations and rights"
            ],
            "how_to_use": "For health-related remote work needs, submit a request through this assistant. You control how much health information is shared.",
            "employee_rights": "You have the right to request remote work as an accommodation for health needs, even if your role typically requires office presence."
        },
        "accommodations": {
            "summary": "Workplace accommodations are adjustments to help you perform your job effectively while managing health conditions.",
            "key_points": [
                "Accommodations can include schedule changes, workspace modifications, equipment, or job duty adjustments",
                "Medical documentation may be required for ongoing accommodations",
                "Accommodations are evaluated based on business needs and your requirements",
                "Accommodations are reviewed periodically to ensure they're still effective"
            ],
            "how_to_use": "Submit an accommodation request through this assistant. For complex needs, you can create a detailed accommodation plan.",
            "employee_rights": "You have the right to reasonable accommodations for health conditions. The company must engage in an interactive process to find solutions."
        },
        "privacy_rights": {
            "summary": "Your health information is private and protected, even when requesting leave or accommodations.",
            "key_points": [
                "Health information is only shared on a need-to-know basis",
                "You control how much detail is shared with your direct manager",
                "Medical documentation is stored securely and separately from personnel files",
                "You can request to review any health information the company has on file"
            ],
            "how_to_use": "When making requests, you'll see privacy options that let you control information sharing.",
            "employee_rights": "You have the right to privacy regarding your health information. Discrimination based on health status is prohibited."
        }
    }
    
    if policy_type == "all":
        return {
            "status": "success",
            "message": "Here's an overview of company leave and accommodation policies:",
            "policies": {k: v["summary"] for k, v in policy_explanations.items()},
            "note": "Select a specific policy type for more detailed information."
        }
    
    policy = policy_explanations.get(policy_type)
    if not policy:
        return {
            "status": "error",
            "message": f"Policy type '{policy_type}' not found. Available types: sick_leave, remote_work, accommodations, privacy_rights."
        }
    
    return {
        "status": "success",
        "message": f"Here's information about {policy_type} policy:",
        "policy": policy
    }

# Create the tool instances
submit_quick_request_tool = FunctionTool(func=submit_quick_request_handler)
create_accommodation_plan_tool = FunctionTool(func=create_accommodation_plan_handler)
check_request_status_tool = FunctionTool(func=check_request_status_handler)
explain_policy_tool = FunctionTool(func=explain_policy_handler) 