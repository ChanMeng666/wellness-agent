"""HR Manager Agent implementation."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from wellness_agent.prompts import HR_AGENT_INSTRUCTION
from wellness_agent.tools import HR_TOOLS

hr_manager_agent = Agent(
    name="hr_manager_agent",
    description="An agent that helps HR managers view anonymous trends, manage accommodations, and update policies",
    model="gemini-1.5-flash",
    instruction=HR_AGENT_INSTRUCTION,
    tools=HR_TOOLS,
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

hr_manager_tool = AgentTool(agent=hr_manager_agent) 