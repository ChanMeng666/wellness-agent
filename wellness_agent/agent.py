"""Main Wellness Agent implementation."""

from google.adk.agents import Agent
from typing import Dict, Any
from google.genai import types

from wellness_agent.prompts import ROOT_INSTRUCTION
from wellness_agent.sub_agents.employee_support.agent import employee_support_tool
from wellness_agent.sub_agents.hr_manager.agent import hr_manager_tool
from wellness_agent.sub_agents.employer_insights.agent import employer_insights_tool
from wellness_agent.sub_agents.search.agent import search_tool
from wellness_agent.privacy.callbacks import privacy_callback

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

# Update the root agent instruction to mention the search capability
ROOT_INSTRUCTION_UPDATED = ROOT_INSTRUCTION + """
You can also use the search_tool to find relevant wellness information from reputable sources on the web.
When a user needs information that isn't in your knowledge base, consider using the search_tool to help them.
"""

root_agent = Agent(
    name="wellness_support_agent",
    description="A comprehensive agent for workplace wellness that supports employees, HR, and employers with privacy-focused tools",
    model="gemini-1.5-flash",
    instruction=ROOT_INSTRUCTION_UPDATED,
    tools=[
        employee_support_tool,
        hr_manager_tool,
        employer_insights_tool,
        search_tool
    ],
    state_callback=privacy_callback,
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