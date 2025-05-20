"""Main Wellness Agent implementation."""

from google.adk.agents import Agent
from typing import Dict, Any
from google.genai import types

from wellness_agent.prompts import ROOT_INSTRUCTION
from wellness_agent.sub_agents.employee_support.agent import employee_support_tool
from wellness_agent.sub_agents.hr_manager.agent import hr_manager_tool
from wellness_agent.sub_agents.employer_insights.agent import employer_insights_tool
from wellness_agent.sub_agents.search.agent import search_tool
from wellness_agent.sub_agents.leave_requests.agent import leave_requests_tool
from wellness_agent.privacy.callbacks import privacy_callback
from wellness_agent.shared_libraries.memory import load_user_profile, memorize, memorize_list, forget, get_memory, clear_memory_key

# Custom callback for privacy controls - kept for reference but not used
def privacy_callback(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    A callback to ensure proper privacy controls are enforced.
    
    This would be expanded in a real implementation to:
    1. Check user role and permissions
    2. Filter sensitive data based on role
    3. Log access attempts for compliance
    4. Apply differential privacy as needed
    """
    # Get current user role from state
    user_role = state.get("user_role", "unknown")
    
    # In a real implementation, we would filter state based on role
    # This is just a stub for demonstration
    print(f"Privacy callback executed for user role: {user_role}")
    
    return state

# Update the root agent instruction to mention the memory capabilities
ROOT_INSTRUCTION_UPDATED = ROOT_INSTRUCTION + """
You can also use the search_tool to find relevant wellness information from reputable sources on the web.
When a user needs information that isn't in your knowledge base, consider using the search_tool to help them.

You can assist employees with discreet leave requests through the leave_requests_tool, which helps them
request time off or accommodations while preserving their privacy and dignity.

You have memory capabilities to remember important information about users and their wellness journey:
- You can remember key information that will be useful in future conversations
- You can recall user preferences and historical data across sessions
- Users' private health data is stored securely and respects their privacy preferences
"""

# Create a memory agent with the memory functions
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool

# Create function-based tools for memory operations
memory_tool_list = [
    FunctionTool(
        func=memorize
    ),
    FunctionTool(
        func=memorize_list
    ),
    FunctionTool(
        func=forget
    ),
    FunctionTool(
        func=get_memory
    ),
    FunctionTool(
        func=clear_memory_key
    )
]

# Create a memory agent
memory_agent = Agent(
    name="memory_agent",
    description="Agent for managing conversation memory",
    model="gemini-1.5-flash",
    instruction="You help store and retrieve information from the conversation. Only use the provided tools for memory operations.",
    tools=memory_tool_list
)

# Create memory_tool as an AgentTool
memory_tool = AgentTool(agent=memory_agent)

# Note: state_callback parameter has been removed as it's not supported in the current ADK version
# The privacy callback functionality is now applied in the server.py file before calling the agent
# The before_agent_call parameter is also not supported in the current ADK version
root_agent = Agent(
    name="wellness_support_agent",
    description="A comprehensive agent for workplace wellness that supports employees, HR, and employers with privacy-focused tools",
    model="gemini-1.5-flash",
    instruction=ROOT_INSTRUCTION_UPDATED,
    tools=[
        employee_support_tool,
        hr_manager_tool,
        employer_insights_tool,
        search_tool,
        leave_requests_tool,
        memory_tool
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
    )
)

# Export the agent as the default for the application
__all__ = ["root_agent"] 