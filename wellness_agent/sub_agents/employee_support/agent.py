"""Employee Support Agent implementation."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from wellness_agent.prompts import EMPLOYEE_AGENT_INSTRUCTION
from wellness_agent.tools import EMPLOYEE_TOOLS

employee_support_agent = Agent(
    name="employee_support_agent",
    description="An agent that helps employees track symptoms, get wellness tips, and request accommodations",
    model="gemini-1.5-flash",
    instruction=EMPLOYEE_AGENT_INSTRUCTION,
    tools=EMPLOYEE_TOOLS,
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

employee_support_tool = AgentTool(agent=employee_support_agent) 