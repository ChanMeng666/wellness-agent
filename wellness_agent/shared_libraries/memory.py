"""Memory management system for the Wellness Agent."""

from datetime import datetime
import json
import os
from typing import Dict, Any, List, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions.state import State
from google.adk.tools import ToolContext

from wellness_agent.db.models import Session, User, SymptomsLog, LeaveRequest, WellnessTip

# Environment variable for loading default profiles, similar to the travel-concierge approach
DEFAULT_PROFILE_PATH = os.getenv(
    "WELLNESS_AGENT_PROFILE", "wellness_agent/db/default_profiles/employee_default.json"
)

def memorize_list(key: str, value: str, tool_context: ToolContext) -> Dict[str, str]:
    """
    Store information as a list item under the specified key.
    
    Args:
        key: the label indexing the memory where the value will be stored
        value: the information to be stored
        tool_context: The ADK tool context containing the state
        
    Returns:
        A status message dictionary
    """
    mem_dict = tool_context.state
    if key not in mem_dict:
        mem_dict[key] = []
    if value not in mem_dict[key]:
        mem_dict[key].append(value)
    return {"status": f'Stored "{key}": "{value}"'}

def memorize(key: str, value: str, tool_context: ToolContext) -> Dict[str, str]:
    """
    Store a single key-value pair in memory.
    
    Args:
        key: the label indexing the memory to store the value
        value: the information to be stored
        tool_context: The ADK tool context containing the state
        
    Returns:
        A status message dictionary
    """
    mem_dict = tool_context.state
    mem_dict[key] = value
    return {"status": f'Stored "{key}": "{value}"'}

def forget(key: str, value: str, tool_context: ToolContext) -> Dict[str, str]:
    """
    Remove a specific value from a list stored under the given key.
    
    Args:
        key: the label indexing the memory to remove from
        value: the specific value to remove
        tool_context: The ADK tool context containing the state
        
    Returns:
        A status message dictionary
    """
    mem_dict = tool_context.state
    if key in mem_dict and isinstance(mem_dict[key], list) and value in mem_dict[key]:
        mem_dict[key].remove(value)
        return {"status": f'Removed "{value}" from "{key}"'}
    return {"status": f'Could not find "{value}" in "{key}"'}

def clear_memory_key(key: str, tool_context: ToolContext) -> Dict[str, str]:
    """
    Clear an entire memory key.
    
    Args:
        key: the label indexing the memory to clear
        tool_context: The ADK tool context containing the state
        
    Returns:
        A status message dictionary
    """
    mem_dict = tool_context.state
    if key in mem_dict:
        del mem_dict[key]
        return {"status": f'Cleared memory key "{key}"'}
    return {"status": f'Memory key "{key}" not found'}

def get_memory(key: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve information stored under the specified key.
    
    Args:
        key: the label indexing the memory to retrieve
        tool_context: The ADK tool context containing the state
        
    Returns:
        A dictionary with the requested value or a status message
    """
    mem_dict = tool_context.state
    if key in mem_dict:
        return {"value": mem_dict[key]}
    return {"status": f'Memory key "{key}" not found', "value": None}

def _set_initial_states(source: Dict[str, Any], target: State | Dict[str, Any]):
    """
    Set up initial session state given a JSON object of states.
    
    Args:
        source: A JSON object of states
        target: The session state object to insert into
    """
    # Set system time if not already present
    if "system_time" not in target:
        target["system_time"] = str(datetime.now())
    
    # Set user profile flag if not already set
    if "profile_initialized" not in target:
        target["profile_initialized"] = True
        target.update(source)
        
        # Set specific wellness-related state variables
        profile = source.get("user_profile", {})
        if profile:
            target["user_id"] = profile.get("user_id", "anonymous")
            target["user_role"] = profile.get("user_role", "employee")
            target["privacy_level"] = profile.get("privacy_level", "standard")
            
            # For employee role, set up wellness tracking state
            if profile.get("user_role") == "employee":
                target["last_symptom_check"] = str(datetime.now())
                target["symptom_tracking_enabled"] = profile.get("symptom_tracking_enabled", True)
                target["notification_preferences"] = profile.get("notification_preferences", {"daily_check_in": True})

def load_user_profile(callback_context: CallbackContext):
    """
    Load a user profile from storage or use a default.
    Set this as a callback before_agent_call of the root_agent.
    
    Args:
        callback_context: The callback context containing the session state
    """
    # Check if environment is set to use mock services
    use_mock = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
    
    # Check if a specific user role is specified in the query or state
    user_role = callback_context.state.get("user_role", "employee")
    
    # Determine the appropriate profile path based on role
    profile_path = DEFAULT_PROFILE_PATH
    if user_role == "hr_manager":
        profile_path = "wellness_agent/db/default_profiles/hr_default.json"
    elif user_role == "employer":
        profile_path = "wellness_agent/db/default_profiles/employer_default.json"
    
    # Override with environment variable if specified
    profile_path = os.getenv("WELLNESS_AGENT_PROFILE", profile_path)
    
    if use_mock:
        # Load from a JSON file for mock mode
        try:
            with open(profile_path, "r") as file:
                data = json.load(file)
                print(f"\nLoading Initial State for {user_role} from file: {profile_path}\n")
                _set_initial_states(data, callback_context.state)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading profile: {str(e)}")
            # Set minimal default state
            _set_initial_states({"user_profile": {"user_role": user_role}}, callback_context.state)
    else:
        # In production, load from database
        # This would be implemented to connect to your database
        # For now, we'll set a minimal default state
        _set_initial_states({"user_profile": {"user_role": user_role}}, callback_context.state)

def sync_state_to_database(state: Dict[str, Any]) -> bool:
    """
    Synchronize the current session state to the database.
    This should be called periodically or at the end of interactions.
    
    Args:
        state: The current session state
        
    Returns:
        True if successful, False otherwise
    """
    # Check if environment is set to use mock services
    use_mock = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
    
    if use_mock:
        # In mock mode, just print the state that would be saved
        print(f"\nMock sync to database: {state}\n")
        return True
    
    try:
        # In production mode, this would save to your actual database
        # Implementation would depend on your database structure
        # This is a placeholder
        user_id = state.get("user_id", "anonymous")
        # Database operations would go here
        return True
    except Exception as e:
        print(f"Error syncing state to database: {str(e)}")
        return False 