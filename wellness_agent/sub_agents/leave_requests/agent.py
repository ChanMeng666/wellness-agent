"""Leave requests agent implementation."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
from google.genai import types

from wellness_agent.sub_agents.leave_requests.prompts import (
    LEAVE_REQUESTS_INSTRUCTION,
    QUICK_REQUEST_INSTRUCTIONS,
    ACCOMMODATION_PLAN_INSTRUCTIONS
)
from wellness_agent.sub_agents.leave_requests.tools import (
    submit_quick_request_tool,
    create_accommodation_plan_tool,
    check_request_status_tool,
    explain_policy_tool
)
from wellness_agent.shared_libraries.memory import memorize, memorize_list, forget, get_memory

# Enhanced instruction with memory capabilities
LEAVE_REQUESTS_MEMORY_INSTRUCTION = LEAVE_REQUESTS_INSTRUCTION + """
You have access to memory tools that allow you to:
- Remember user preferences and previous requests with memorize() and memorize_list()
- Recall past request information with get_memory()
- Update or remove outdated request information with forget()

Use these memory capabilities to:
- Remember the user's preferred request types and formats
- Keep track of pending and past requests to provide updates
- Store privacy preferences for different types of requests
- Recall accommodations that worked well for similar situations
- Remember company policies relevant to leave requests

Always prioritize privacy and ensure users understand how their data is used.
"""

QUICK_REQUEST_MEMORY_INSTRUCTIONS = QUICK_REQUEST_INSTRUCTIONS + """
You can use memory tools to remember the user's preferred request format and previous request patterns
to streamline the process for them over time.
"""

ACCOMMODATION_PLAN_MEMORY_INSTRUCTIONS = ACCOMMODATION_PLAN_INSTRUCTIONS + """
You can use memory tools to track the user's accommodation plan over time, helping them make adjustments
as needed and learn which accommodations are most effective for their situation.
"""

# Memory tools
memory_tools = [
    FunctionTool(func=memorize),
    FunctionTool(func=memorize_list),
    FunctionTool(func=forget),
    FunctionTool(func=get_memory)
]

# Create sub-agents for specific tasks
quick_request_agent = Agent(
    name="quick_request_agent",
    description="An agent that helps employees submit quick leave requests with privacy",
    model="gemini-1.5-flash",
    instruction=QUICK_REQUEST_MEMORY_INSTRUCTIONS,
    tools=[submit_quick_request_tool] + memory_tools,
)

accommodation_plan_agent = Agent(
    name="accommodation_plan_agent",
    description="An agent that helps employees create longer-term accommodation plans",
    model="gemini-1.5-flash",
    instruction=ACCOMMODATION_PLAN_MEMORY_INSTRUCTIONS,
    tools=[create_accommodation_plan_tool] + memory_tools,
)

# Create the main leave requests agent
leave_requests_agent = Agent(
    name="leave_requests_agent",
    description="An agent that helps employees request time off or accommodations with dignity and privacy",
    model="gemini-1.5-flash",
    instruction=LEAVE_REQUESTS_MEMORY_INSTRUCTION,
    tools=[
        AgentTool(agent=quick_request_agent),
        AgentTool(agent=accommodation_plan_agent),
        check_request_status_tool,
        explain_policy_tool
    ] + memory_tools,
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

# Export the agent tool for the main agent
leave_requests_tool = AgentTool(agent=leave_requests_agent) 