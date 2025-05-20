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
        
        # Prepare messages in the required format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Call the agent
        response = root_agent.generate_content(
            [messages[-1]],  # Just the latest message
            generation_config={"state": state}
        )
        
        # Record the agent's response in the session history
        session.add_message(
            role="assistant",
            content=response.text
        )
        
        # Update the session state
        session.update_state(state)
        
        # Save the updated session
        memory_service.save_session(session)
        
        return {
            "response": response.text,
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