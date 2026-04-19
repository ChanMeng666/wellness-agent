"""Main Wellness Agent implementation."""

from google.adk.agents import Agent
from typing import Dict, Any
from google.genai import types

from wellness_agent.llm_config import create_model

from wellness_agent.prompts import ROOT_INSTRUCTION
from wellness_agent.sub_agents.employee_support.agent import employee_support_tool
from wellness_agent.sub_agents.hr_manager.agent import hr_manager_tool
from wellness_agent.sub_agents.employer_insights.agent import employer_insights_tool
from wellness_agent.sub_agents.search.agent import search_tool
from wellness_agent.sub_agents.leave_requests.agent import leave_requests_tool
from wellness_agent.privacy.callbacks import privacy_callback
from wellness_agent.shared_libraries.memory import load_user_profile, memorize, memorize_list, forget, get_memory, clear_memory_key
from wellness_agent.tools.data_tools import (
    department_stats_tool,
    leave_trends_tool,
    health_trends_tool,
    wellness_programs_tool,
    department_leave_rates_tool,
    policy_document_tool,
    wellness_guide_tool,
    wellness_report_tool,
    list_resources_tool,
    file_link_tool
)

# Note: privacy_callback is imported from wellness_agent.privacy.callbacks
# and used in server.py. The duplicate stub that was here has been removed.

# Update the root agent instruction to mention the data access capabilities
ROOT_INSTRUCTION_UPDATED = ROOT_INSTRUCTION + """
You can also use the search_tool to find relevant wellness information from reputable sources on the web.
When a user needs information that isn't in your knowledge base, consider using the search_tool to help them.

You can assist employees with discreet leave requests through the leave_requests_tool, which helps them
request time off or accommodations while preserving their privacy and dignity.

You have advanced memory capabilities to personalize the user experience:
- You can remember user preferences and wellness goals across conversations using memorize()
- You can build lists of important information with memorize_list()
- You can recall stored information with get_memory()
- You can remove outdated information with forget() and clear_memory_key()

Different user roles have different memory requirements:
- For employees: Remember their symptoms, wellness goals, and communication preferences
- For HR managers: Remember policy decisions, accommodation processes, and company structure
- For employers: Remember business metrics, ROI information, and strategic priorities

You have access to anonymized company data tools that respect privacy:
- Department statistics tools can provide anonymized metrics without revealing individual data
- Leave trend tools can analyze patterns while protecting individual privacy
- Health trend tools show aggregated wellness metrics without individual identification
- Policy and resource tools help you access company documents and wellness guides

Always respect privacy settings when using memory and data tools. Check the user's privacy_level 
before storing sensitive information or accessing health-related data. Never reveal individual 
employee health information to HR managers or employers - only provide aggregated, anonymized trends.
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
    model=create_model(),
    instruction="""You help store and retrieve information from the conversation. 

Use these memory tools to provide a personalized experience:
- memorize(key, value): Store a specific piece of information under a key
- memorize_list(key, value): Add to a list of values under a specific key
- forget(key, value): Remove a specific value from a list
- get_memory(key): Retrieve information stored under a key
- clear_memory_key(key): Remove an entire category of information

Follow these memory best practices:
1. Use descriptive key names that clearly identify the type of information
2. Store user preferences in dedicated keys (e.g., 'communication_style')
3. Use lists for tracking multiple related items (e.g., 'reported_symptoms')
4. Always respect privacy preferences when storing health information
5. Don't store unnecessary or redundant information

Only use the provided tools for memory operations.""",
    tools=memory_tool_list
)

# Create memory_tool as an AgentTool
memory_tool = AgentTool(agent=memory_agent)

# Create a data agent for accessing company data while respecting privacy
data_agent = Agent(
    name="data_agent",
    description="Agent for accessing company wellness data with privacy protections",
    model=create_model(),
    instruction="""You help retrieve and analyze company wellness data while strictly protecting employee privacy.

Only use these data tools as appropriate for the user's role:
- HR Managers can see department-level statistics and trends, but never individual employee data
- Employers can see organization-wide metrics and ROI information
- Employees should only see their own data or general wellness resources

When accessing files like wellness guides or policy documents:
- Use the file_link_tool to generate shareable links to documents
- Always provide a link when mentioning a specific document like wellness guides or policies
- Explain what each document contains briefly before sharing its link

PRIVACY RULES:
1. NEVER provide individual employee health data to HR managers or employers
2. Only provide aggregated, anonymized trend data at the department or company level
3. Clearly state the privacy protections in place when sharing data
4. When accessing reports or statistics, only focus on the trends, not individuals
5. Always mention that the data is anonymized when presenting results

Be transparent about data sources and privacy protections in all responses.""",
    tools=[
        department_stats_tool,
        leave_trends_tool,
        health_trends_tool,
        wellness_programs_tool,
        department_leave_rates_tool,
        policy_document_tool,
        wellness_guide_tool,
        wellness_report_tool,
        list_resources_tool,
        file_link_tool
    ]
)

# Create data_tool as an AgentTool
data_tool = AgentTool(agent=data_agent)

# Note: state_callback parameter has been removed as it's not supported in the current ADK version
# The privacy callback functionality is now applied in the server.py file before calling the agent
# The user profile loading is also handled in server.py since before_agent_call is not supported
root_agent = Agent(
    name="wellness_support_agent",
    description="A comprehensive agent for workplace wellness that supports employees, HR, and employers with privacy-focused tools",
    model=create_model(),
    instruction=ROOT_INSTRUCTION_UPDATED,
    tools=[
        employee_support_tool,
        hr_manager_tool,
        employer_insights_tool,
        search_tool,
        leave_requests_tool,
        memory_tool,
        data_tool
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