"""FastAPI server for the Wellness Agent."""

import os
import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI, Request, Depends, HTTPException, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from wellness_agent.agent import root_agent
from wellness_agent.privacy.callbacks import privacy_callback
from wellness_agent.services.service_factory import ServiceFactory
from wellness_agent.services.db.memory_service import MemoryService
from wellness_agent.shared_libraries.memory import _set_initial_states

# Load environment variables
load_dotenv()

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)

# Initialize service factory
service_factory = ServiceFactory()

# Initialize memory service
memory_service = MemoryService()

# Create the FastAPI app
app = FastAPI(
    title="Wellness Agent API",
    description="API for the AI Wellness Agent",
    version="0.1.0"
)

# Add CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend" / "public"

# Mount the static files directory
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Define request/response models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Chat history")
    user_id: Optional[str] = Field(None, description="User ID for context")
    user_role: Optional[str] = Field(None, description="User role (employee, hr, employer)")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    session_id: Optional[str] = Field(None, description="Session ID for continuity")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID for continuity")
    usage: Dict[str, Any] = Field({}, description="Token usage information")

# Authentication dependency (simplified for demonstration)
async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Simple authentication dependency.
    
    In a real implementation, this would validate a JWT token or session.
    """
    if not authorization:
        # For demo purposes, use a default user
        return {
            "user_id": os.getenv("DEMO_PROFILE_ID", "demo_profile_123"),
            "role": "employee",
            "organization_id": os.getenv("DEMO_ORGANIZATION_ID", "demo_org_456")
        }
    
    # In a real implementation, validate the token and return user info
    # For now, just parse a simple token format
    try:
        # Format: "Bearer user_id:role:org_id"
        if not authorization.startswith("Bearer "):
            raise ValueError("Invalid token format")
        
        token = authorization.replace("Bearer ", "")
        parts = token.split(":")
        
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        return {
            "user_id": parts[0],
            "role": parts[1],
            "organization_id": parts[2]
        }
    except Exception as e:
        logger.warning(f"Authentication error: {e}")
        # Fall back to demo user
        return {
            "user_id": os.getenv("DEMO_PROFILE_ID", "demo_profile_123"),
            "role": "employee",
            "organization_id": os.getenv("DEMO_ORGANIZATION_ID", "demo_org_456")
        }

def load_default_profile(user_role: str) -> Dict[str, Any]:
    """
    Load a default profile based on user role.
    
    Args:
        user_role: The role of the user (employee, hr_manager, employer)
        
    Returns:
        A dictionary with default profile data
    """
    # Determine the appropriate profile path based on role
    if user_role == "hr_manager":
        profile_path = "wellness_agent/db/default_profiles/hr_default.json"
    elif user_role == "employer":
        profile_path = "wellness_agent/db/default_profiles/employer_default.json"
    else:  # Default to employee
        profile_path = "wellness_agent/db/default_profiles/employee_default.json"
    
    # Try to load the profile
    try:
        with open(profile_path, "r") as file:
            data = json.load(file)
            logger.info(f"Loaded default profile for {user_role} from {profile_path}")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Error loading default profile: {e}")
        # Return minimal default data
        return {
            "user_profile": {
                "user_role": user_role
            }
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Chat with the wellness agent.
    """
    try:
        # Get user information
        user_id = request.user_id or current_user["user_id"]
        user_role = request.user_role or current_user["role"]
        organization_id = request.organization_id or current_user["organization_id"]
        
        # Session management - either use existing or create new
        session_id = request.session_id
        session = None
        
        if session_id:
            # Try to get existing session
            session = memory_service.get_session(session_id)
        
        if not session:
            # Create a new session
            session_id = str(uuid.uuid4())
            session = memory_service.create_new_session(user_id, user_role)
            session_id = session.session_id
            
            # Load default profile data for new sessions
            default_profile = load_default_profile(user_role)
            
            # Initialize the session state with the default profile
            if not session.state:
                session.state = {}
            
            # Use the memory module's function to properly set initial states
            _set_initial_states(default_profile, session.state)
            
            logger.info(f"Created new session {session_id} for user {user_id} with role {user_role}")
        
        # Prepare the state with user information and session
        state = session.state if session.state else {}
        
        # Ensure basic information is in the state
        state.update({
            "user_id": user_id,
            "user_role": user_role,
            "organization_id": organization_id,
            "session_id": session_id,
            "system_time": datetime.now().isoformat()
        })
        
        # Record the new message in the session history
        session.add_message(
            role=request.messages[-1].role,
            content=request.messages[-1].content
        )
        
        # Apply privacy callback to state
        state = privacy_callback(state)
        
        # Get the latest user message
        latest_message = request.messages[-1].content
        
        # Check if this is a simple confirmation of a previous suggestion
        is_confirmation = False
        previous_suggestion = None
        
        # Look for confirmation words in a short message
        confirmation_words = ["yes", "sure", "ok", "okay", "please", "go ahead", "continue"]
        if len(latest_message.split()) <= 3 and any(word in latest_message.lower() for word in confirmation_words):
            # Look at previous messages to find what was suggested
            if len(request.messages) >= 3:  # Need at least user, assistant, user
                previous_assistant_msg = request.messages[-2].content.lower()
                if "wellness_guide_tool" in previous_assistant_msg or "guide" in previous_assistant_msg:
                    is_confirmation = True
                    if "work-life balance" in previous_assistant_msg or "work life balance" in previous_assistant_msg:
                        previous_suggestion = "work_life_balance"
                    elif "stress" in previous_assistant_msg:
                        previous_suggestion = "stress"
                    elif "mental health" in previous_assistant_msg:
                        previous_suggestion = "mental_health"
                    else:
                        previous_suggestion = "general_wellness"
                    
                    logger.info(f"Detected confirmation response to previous suggestion about: {previous_suggestion}")
                    
                elif "policy_document_tool" in previous_assistant_msg or "policy" in previous_assistant_msg:
                    is_confirmation = True
                    if "leave" in previous_assistant_msg:
                        previous_suggestion = "leave_policy"
                    elif "mental health" in previous_assistant_msg:
                        previous_suggestion = "mental_health_leave"
                    else:
                        previous_suggestion = "general_policy"
                    
                    logger.info(f"Detected confirmation response to previous suggestion about: {previous_suggestion}")
        
        # Detect data tool requests in the message
        data_request = None
        
        # If this is a confirmation of a previous suggestion, handle accordingly
        if is_confirmation and previous_suggestion:
            if previous_suggestion == "work_life_balance":
                try:
                    from wellness_agent.tools.data_tools import get_wellness_guide
                    data_request = {
                        "tool": "wellness_guide",
                        "data": get_wellness_guide(guide_type="work_life_balance")
                    }
                    logger.info(f"Retrieved work-life balance guide based on user confirmation")
                except Exception as e:
                    logger.error(f"Error retrieving work-life balance guide: {str(e)}")
                    
            elif previous_suggestion == "stress":
                try:
                    from wellness_agent.tools.data_tools import get_wellness_guide
                    data_request = {
                        "tool": "wellness_guide",
                        "data": get_wellness_guide(guide_type="stress")
                    }
                    logger.info(f"Retrieved stress management guide based on user confirmation")
                except Exception as e:
                    logger.error(f"Error retrieving stress guide: {str(e)}")
                    
            elif previous_suggestion == "mental_health":
                try:
                    from wellness_agent.tools.data_tools import get_wellness_guide
                    data_request = {
                        "tool": "wellness_guide",
                        "data": get_wellness_guide(guide_type="mental_health")
                    }
                    logger.info(f"Retrieved mental health guide based on user confirmation")
                except Exception as e:
                    logger.error(f"Error retrieving mental health guide: {str(e)}")
                    
            elif previous_suggestion == "leave_policy" or previous_suggestion == "mental_health_leave":
                try:
                    from wellness_agent.tools.data_tools import get_policy_document
                    data_request = {
                        "tool": "policy_document",
                        "data": get_policy_document(policy_type="leave")
                    }
                    logger.info(f"Retrieved leave policy based on user confirmation")
                except Exception as e:
                    logger.error(f"Error retrieving leave policy: {str(e)}")
                    
            elif previous_suggestion == "general_wellness":
                try:
                    from wellness_agent.tools.data_tools import get_wellness_guide
                    data_request = {
                        "tool": "wellness_guide",
                        "data": get_wellness_guide(guide_type="general_wellness")
                    }
                    logger.info(f"Retrieved general wellness guide based on user confirmation")
                except Exception as e:
                    logger.error(f"Error retrieving general wellness guide: {str(e)}")
                    
        # Continue with the regular detection logic if no confirmation was handled
        elif "department leave rate" in latest_message.lower() or "highest leave rate" in latest_message.lower():
            try:
                from wellness_agent.tools.data_tools import get_department_leave_rates
                data_request = {
                    "tool": "department_leave_rates",
                    "data": get_department_leave_rates()
                }
                logger.info("Retrieved department leave rates from real database")
            except Exception as e:
                logger.error(f"Error retrieving department leave rates: {str(e)}")
                
        # Employer-specific query - ROI on wellness initiatives
        elif "roi" in latest_message.lower() or \
             ("return" in latest_message.lower() and "investment" in latest_message.lower()) or \
             ("wellness" in latest_message.lower() and "initiatives" in latest_message.lower() and "return" in latest_message.lower()):
            try:
                from wellness_agent.tools.data_tools import get_wellness_report
                data_request = {
                    "tool": "wellness_report",
                    "data": get_wellness_report(report_type="wellness")
                }
                logger.info(f"Retrieved wellness ROI report for employer from real database")
            except Exception as e:
                logger.error(f"Error retrieving wellness ROI report: {str(e)}")
                
        # Employer-specific query - Compare departments
        elif ("compare" in latest_message.lower() and "department" in latest_message.lower()) or \
             ("metrics" in latest_message.lower() and "across department" in latest_message.lower()) or \
             ("department" in latest_message.lower() and "comparison" in latest_message.lower()):
            try:
                from wellness_agent.tools.data_tools import get_department_stats
                data_request = {
                    "tool": "department_stats",
                    "data": get_department_stats(months=6)  # Get 6 months of data for comparison
                }
                logger.info(f"Retrieved department comparison data for employer from real database")
            except Exception as e:
                logger.error(f"Error retrieving department comparison data: {str(e)}")
                
        # Employer-specific query - Annual wellness report
        elif ("annual" in latest_message.lower() and "wellness" in latest_message.lower()) or \
             ("wellness" in latest_message.lower() and "report" in latest_message.lower()) or \
             ("yearly" in latest_message.lower() and "wellness" in latest_message.lower()):
            try:
                from wellness_agent.tools.data_tools import get_wellness_report
                data_request = {
                    "tool": "wellness_report",
                    "data": get_wellness_report(report_type="annual")
                }
                logger.info(f"Retrieved annual wellness report for employer from real database")
            except Exception as e:
                logger.error(f"Error retrieving annual wellness report: {str(e)}")
                
        elif "wellness program" in latest_message.lower() or "program effectiveness" in latest_message.lower():
            try:
                from wellness_agent.tools.data_tools import get_wellness_programs
                data_request = {
                    "tool": "wellness_programs",
                    "data": get_wellness_programs()
                }
                logger.info("Retrieved wellness programs from real database")
            except Exception as e:
                logger.error(f"Error retrieving wellness programs: {str(e)}")
                
        elif "health trend" in latest_message.lower() or "stress level trend" in latest_message.lower():
            trend_type = "stress_levels"
            if "work life" in latest_message.lower():
                trend_type = "work_life_balance"
            elif "physical" in latest_message.lower():
                trend_type = "physical_activity"
                
            try:
                from wellness_agent.tools.data_tools import get_health_trends
                data_request = {
                    "tool": "health_trends",
                    "data": get_health_trends(trend_type=trend_type)
                }
                logger.info(f"Retrieved health trends for {trend_type} from real database")
            except Exception as e:
                logger.error(f"Error retrieving health trends: {str(e)}")

        # Add handling for wellness guides and resources
        elif ("stress" in latest_message.lower() and "resource" in latest_message.lower()) or \
             "feeling stressed" in latest_message.lower() or \
             "mental health resources" in latest_message.lower() or \
             "wellness guide" in latest_message.lower() or \
             ("work-life balance" in latest_message.lower() and "track" in latest_message.lower()) or \
             ("work life balance" in latest_message.lower() and "track" in latest_message.lower()) or \
             ("balance" in latest_message.lower() and "track" in latest_message.lower()) or \
             ("track" in latest_message.lower() and "wellness" in latest_message.lower()):
            
            # Determine guide type based on the query
            guide_type = "general_wellness"
            
            if "work life" in latest_message.lower() or "work-life" in latest_message.lower() or \
               "balance" in latest_message.lower():
                guide_type = "work_life_balance"
                logger.info(f"Detected work-life balance tracking request: '{latest_message}'")
            elif "stress" in latest_message.lower():
                guide_type = "stress"
            elif "mental health" in latest_message.lower():
                guide_type = "mental_health"
                
            try:
                from wellness_agent.tools.data_tools import get_wellness_guide
                data_request = {
                    "tool": "wellness_guide",
                    "data": get_wellness_guide(guide_type=guide_type)
                }
                logger.info(f"Retrieved wellness guide for {guide_type} from real database")
            except Exception as e:
                logger.error(f"Error retrieving wellness guide: {str(e)}")
        
        # Add handling for listing available resources
        elif "available resources" in latest_message.lower() or "what resources" in latest_message.lower():
            resource_type = None
            if "wellness" in latest_message.lower() or "guide" in latest_message.lower():
                resource_type = "wellness_guides"
            elif "policy" in latest_message.lower():
                resource_type = "policy_documents"
            elif "report" in latest_message.lower():
                resource_type = "aggregated_reports"
                
            try:
                from wellness_agent.tools.data_tools import list_available_resources
                data_request = {
                    "tool": "list_resources",
                    "data": list_available_resources(resource_type=resource_type)
                }
                logger.info(f"Listed available resources with prefix {resource_type or 'all'} from real database")
            except Exception as e:
                logger.error(f"Error listing available resources: {str(e)}")
                
        # Enhanced policy detection with better recognition of mental health days
        elif "policy" in latest_message.lower() or \
             "leave policy" in latest_message.lower() or \
             "mental health day" in latest_message.lower() or \
             "mental health days" in latest_message.lower() or \
             "entitled to" in latest_message.lower() or \
             ("how many" in latest_message.lower() and "days" in latest_message.lower()) or \
             ("time off" in latest_message.lower() and "mental" in latest_message.lower()):
            
            # Determine policy type based on the query
            policy_type = "leave"
            
            if "accommodation" in latest_message.lower():
                policy_type = "accommodation"
            elif "remote" in latest_message.lower() or "work from home" in latest_message.lower():
                policy_type = "remote_work"
            # Add better handling for specific leave types
            elif "menstruation" in latest_message.lower() or "period" in latest_message.lower():
                policy_type = "menstruation_leave"
            elif "parental" in latest_message.lower() or "maternity" in latest_message.lower() or "paternity" in latest_message.lower():
                policy_type = "parental_leave"
            elif "sick" in latest_message.lower():
                policy_type = "sick_leave"
            elif "mental health" in latest_message.lower():
                policy_type = "mental_health_leave"
            
            # Log more detailed information about the policy request
            logger.info(f"Detected policy request: '{latest_message}' - Using policy type: {policy_type}")
                
            try:
                from wellness_agent.tools.data_tools import get_policy_document
                data_request = {
                    "tool": "policy_document",
                    "data": get_policy_document(policy_type=policy_type)
                }
                logger.info(f"Retrieved policy document for {policy_type} from real database")
            except Exception as e:
                logger.error(f"Error retrieving policy document: {str(e)}")
        
        # Prepare data tool information for the prompt
        data_tools_instructions = """
        When asked about company data, please use these functionalities:
        
        For HR Managers:
        - You can access department leave rates with department_leave_rates_tool
        - You can access wellness program effectiveness with wellness_programs_tool
        - You can see health trends with health_trends_tool
        - You can retrieve policy documents with policy_document_tool
        
        For Employers:
        - You can analyze wellness ROI with wellness_report_tool
        - You can compare departments with department_stats_tool
        - You can view organization-wide trends with leave_trends_tool
        
        For Employees:
        - You can access wellness guides with wellness_guide_tool
        - You can find information about policies with policy_document_tool
        
        Always respect privacy: Never show individual employee data to HR or employers, only anonymized aggregated statistics.
        """
        
        # Build the prompt
        full_prompt = f"""You are a workplace wellness assistant. The user's role is: {user_role}.
        
        {data_tools_instructions}
        
        USER QUERY: {latest_message}
        """
        
        # Include real data if retrieved
        if data_request:
            full_prompt += f"\n\nRESULT FROM {data_request['tool']}_tool:\n"
            
            # For policy documents with mental health days, highlight the specific information
            if data_request['tool'] == "policy_document" and "mental health" in latest_message.lower():
                full_prompt += "When responding, focus specifically on the mental health days information in the policy.\n\n"
                
                # Process content to highlight mental health days if present
                if 'content' in data_request['data'] and isinstance(data_request['data']['content'], str):
                    content = data_request['data']['content']
                    
                    # Try to find and highlight mental health days section
                    lines = content.split('\n')
                    mental_health_content = ""
                    
                    for i, line in enumerate(lines):
                        if "mental health" in line.lower():
                            # Add this line and a few surrounding lines for context
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            mental_health_content = '\n'.join(lines[start:end])
                            break
                    
                    # If we found relevant content, prepend it as a highlight
                    if mental_health_content:
                        full_prompt += "HIGHLIGHTED SECTION ABOUT MENTAL HEALTH DAYS:\n"
                        full_prompt += mental_health_content + "\n\n"
                        full_prompt += "FULL POLICY DOCUMENT:\n"
            
            # For wellness guides with tracking requests, highlight the tracking information
            elif data_request['tool'] == "wellness_guide" and "track" in latest_message.lower():
                full_prompt += "When responding, focus on practical ways the user can track and improve their wellness.\n\n"
                
                # Process content to highlight tracking information if present
                if 'content' in data_request['data'] and isinstance(data_request['data']['content'], str):
                    content = data_request['data']['content']
                    
                    # Try to find and highlight tracking-related content
                    tracking_keywords = ["track", "monitor", "journal", "diary", "log", "record", "measure"]
                    lines = content.split('\n')
                    tracking_content = []
                    
                    for i, line in enumerate(lines):
                        if any(keyword in line.lower() for keyword in tracking_keywords):
                            # Add this line and a couple surrounding lines for context
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            tracking_content.append('\n'.join(lines[start:end]))
                    
                    # If we found relevant content, prepend it as highlights
                    if tracking_content:
                        full_prompt += "HIGHLIGHTED TRACKING-RELATED SECTIONS:\n"
                        full_prompt += "\n---\n".join(tracking_content) + "\n\n"
                        full_prompt += "FULL GUIDE CONTENT:\n"
                        
                # Add specific instructions for work-life balance tracking
                if "work life balance" in latest_message.lower() or "work-life balance" in latest_message.lower():
                    full_prompt += "\nPresent the information as actionable steps for tracking work-life balance. Include concrete examples of tools or methods the user can use to track their balance.\n"
            
            # For employer-specific queries, emphasize business metrics and ROI
            elif user_role == "employer" and data_request['tool'] in ["wellness_report", "department_stats"]:
                full_prompt += "When responding, focus on the business impact, ROI, and actionable insights for leadership. The user is an employer/leader looking for organization-level data.\n\n"
                
                # Add specific instructions based on the type of employer query
                if data_request['tool'] == "wellness_report" and "roi" in latest_message.lower():
                    full_prompt += "Analyze the ROI data in detail. Present concrete numbers and percentages about cost savings, productivity improvements, and reduced absenteeism. Compare results to industry benchmarks when available.\n\n"
                    
                elif data_request['tool'] == "department_stats" and "compare" in latest_message.lower():
                    full_prompt += "Present a clear comparison between departments, highlighting top performers and areas for improvement. Suggest targeted interventions for departments with lower metrics.\n\n"
                    
                elif "report" in latest_message.lower():
                    full_prompt += "Summarize the key findings from the annual report, focusing on trends, achievements, and opportunities. Include participation rates, satisfaction scores, and business impact metrics.\n\n"
            
            # Add the full data
            full_prompt += json.dumps(data_request['data'], indent=2)
            full_prompt += "\n\nPlease respond based on this actual data from our database. Always present the information in a clear, organized way and explain what the data means."
            
            # Additional guidance for specific query types
            if "mental health day" in latest_message.lower() or "how many" in latest_message.lower():
                full_prompt += "\n\nThe user is specifically asking about entitlement or quantity. Please provide a direct and clear answer about the number or amount if this information is available in the data."
        else:
            full_prompt += "\n\nFor data-related questions, please explain that you need to use specific tools to retrieve the data."
        
        # Use a very simplified approach - direct to Gemini
        try:
            # Import vertexai for direct access
            import google.generativeai as genai
            
            # Configure the API
            if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE").upper() == "TRUE":
                # Use VertexAI
                import vertexai
                from vertexai.generative_models import GenerativeModel
                
                # Initialize Vertex AI with project and location
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
                location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                vertexai.init(project=project_id, location=location)
                
                # Create the model
                model = GenerativeModel("gemini-1.5-flash")
                response_text = model.generate_content(full_prompt).text
                
            else:
                # Use Google AI Studio API key
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))
                
                # Create the model
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(full_prompt)
                response_text = response.text
                
        except Exception as e:
            logger.error(f"Error with direct Gemini call: {str(e)}")
            # Fallback response
            response_text = f"I'm having trouble connecting to the AI service. Please check your configuration and try again later. Error details: {str(e)}"
        
        # Record the agent's response in the session history
        session.add_message(
            role="assistant",
            content=response_text
        )
        
        # Update the session state
        session.update_state(state)
        
        # Save the updated session
        memory_service.save_session(session)
        
        return {
            "response": response_text,
            "session_id": session_id,
            "usage": {}  # In a real implementation, we would track and return token usage
        }
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "ok", "version": "0.1.0"}

@app.get("/api/sessions/{user_id}")
async def get_user_sessions(
    user_id: str,
    active_only: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get all sessions for a user.
    
    This endpoint requires authentication and proper authorization.
    """
    # Simple authorization check
    if current_user["user_id"] != user_id and current_user["role"] != "hr_manager":
        raise HTTPException(status_code=403, detail="Not authorized to access these sessions")
    
    try:
        sessions = memory_service.get_user_sessions(user_id, active_only)
        return {
            "user_id": user_id,
            "sessions": [session.to_dict() for session in sessions]
        }
    except Exception as e:
        logger.error(f"Error retrieving user sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving user sessions: {str(e)}")

@app.get("/api/symptom_logs/{user_id}")
async def get_user_symptom_logs(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get symptom logs for a user.
    
    This endpoint requires authentication and proper authorization.
    """
    # Simple authorization check - users can only access their own logs, HR can access all
    if current_user["user_id"] != user_id and current_user["role"] != "hr_manager":
        raise HTTPException(status_code=403, detail="Not authorized to access these logs")
    
    try:
        # Convert date strings to datetime objects if provided
        start_datetime = datetime.fromisoformat(start_date) if start_date else None
        end_datetime = datetime.fromisoformat(end_date) if end_date else None
        
        logs = memory_service.get_user_symptom_logs(
            user_id=user_id,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        # If HR is accessing employee logs, ensure they only see anonymized data
        if current_user["user_id"] != user_id and current_user["role"] == "hr_manager":
            logs = [log.anonymize() for log in logs]
        
        return {
            "user_id": user_id if current_user["user_id"] == user_id else "anonymous",
            "log_count": len(logs),
            "logs": [log.to_dict() for log in logs]
        }
    except Exception as e:
        logger.error(f"Error retrieving symptom logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving symptom logs: {str(e)}")

@app.get("/")
async def serve_frontend():
    """
    Serve the frontend application.
    """
    return FileResponse(frontend_dir / "index.html")

@app.get("/{path:path}")
async def serve_frontend_paths(path: str):
    """
    Serve the frontend application for any route.
    
    This allows the frontend to handle client-side routing.
    """
    # First check if the file exists in the static directory
    file_path = frontend_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Otherwise, serve the index.html for client-side routing
    return FileResponse(frontend_dir / "index.html")

@app.get("/api/db/test-connection")
async def test_database_connections() -> Dict[str, Any]:
    """
    Test database connections.
    
    This endpoint tests connections to Firestore and BigQuery.
    """
    from wellness_agent.db.test_connection import test_all_connections
    
    try:
        results = test_all_connections()
        return results
    except Exception as e:
        logger.error(f"Error testing database connections: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error testing database connections: {str(e)}")

if __name__ == "__main__":
    # This is for development only. In production, use a proper ASGI server.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 