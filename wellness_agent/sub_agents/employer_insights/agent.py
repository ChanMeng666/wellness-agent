"""Employer Insights Agent implementation."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from wellness_agent.prompts import EMPLOYER_AGENT_INSTRUCTION
from wellness_agent.tools import EMPLOYER_TOOLS

employer_insights_agent = Agent(
    name="employer_insights_agent",
    description="An agent that helps employers calculate ROI, forecast workforce impacts, and get organizational insights",
    model="gemini-1.5-flash",
    instruction=EMPLOYER_AGENT_INSTRUCTION,
    tools=EMPLOYER_TOOLS,
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

employer_insights_tool = AgentTool(agent=employer_insights_agent) 