"""Leave requests agent implementation."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
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

# Create sub-agents for specific tasks
quick_request_agent = Agent(
    name="quick_request_agent",
    description="An agent that helps employees submit quick leave requests with privacy",
    model="gemini-1.5-flash",
    instruction=QUICK_REQUEST_INSTRUCTIONS,
    tools=[submit_quick_request_tool],
)

accommodation_plan_agent = Agent(
    name="accommodation_plan_agent",
    description="An agent that helps employees create longer-term accommodation plans",
    model="gemini-1.5-flash",
    instruction=ACCOMMODATION_PLAN_INSTRUCTIONS,
    tools=[create_accommodation_plan_tool],
)

# Create the main leave requests agent
leave_requests_agent = Agent(
    name="leave_requests_agent",
    description="An agent that helps employees request time off or accommodations with dignity and privacy",
    model="gemini-1.5-flash",
    instruction=LEAVE_REQUESTS_INSTRUCTION,
    tools=[
        AgentTool(agent=quick_request_agent),
        AgentTool(agent=accommodation_plan_agent),
        check_request_status_tool,
        explain_policy_tool
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

# Export the agent tool for the main agent
leave_requests_tool = AgentTool(agent=leave_requests_agent) 