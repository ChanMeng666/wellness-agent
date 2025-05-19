"""FastAPI server for the Wellness Agent."""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Depends, HTTPException, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from wellness_agent.agent import root_agent
from wellness_agent.privacy.callbacks import privacy_callback
from wellness_agent.services.service_factory import ServiceFactory

# Load environment variables
load_dotenv()

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)

# Initialize service factory
service_factory = ServiceFactory()

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

# Define request/response models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Chat history")
    user_id: Optional[str] = Field(None, description="User ID for context")
    user_role: Optional[str] = Field(None, description="User role (employee, hr, employer)")
    organization_id: Optional[str] = Field(None, description="Organization ID")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
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
        # Prepare the state with user information
        state = {
            "user_id": request.user_id or current_user["user_id"],
            "user_role": request.user_role or current_user["role"],
            "organization_id": request.organization_id or current_user["organization_id"]
        }
        
        # Prepare messages in the required format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Apply privacy callback to state
        state = privacy_callback(state)
        
        # Call the agent
        response = root_agent.generate_content(
            [messages[-1]],  # Just the latest message
            generation_config={"state": state}
        )
        
        return {
            "response": response.text,
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

if __name__ == "__main__":
    # This is for development only. In production, use a proper ASGI server.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 