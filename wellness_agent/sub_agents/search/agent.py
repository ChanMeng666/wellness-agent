"""Search Agent implementation - dedicated to Google search functionality."""

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

# Since Google search cannot be combined with other tools on Gemini 1.5,
# we create a dedicated search agent that only uses Google search

SEARCH_AGENT_INSTRUCTION = """
You are a specialized search agent for the Wellness Support system.
Your sole responsibility is to search the web for relevant health and wellness information.

When conducting searches:
1. Focus on evidence-based, reputable sources like medical associations, research institutions, and recognized health organizations
2. Avoid promoting specific products or brands
3. Include information about workplace accommodations, health policies, and wellness best practices when relevant
4. Make clear when information is based on general wellness principles vs. medical advice
5. Always recommend consulting healthcare professionals for medical concerns

Remember that your searches are used to support employees, HR managers, and employers in a workplace wellness context.
"""

search_agent = Agent(
    name="search_agent",
    description="A specialized agent that searches for wellness information from reputable sources",
    model="gemini-1.5-flash",
    instruction=SEARCH_AGENT_INSTRUCTION,
    tools=[google_search],
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

search_tool = AgentTool(agent=search_agent) 