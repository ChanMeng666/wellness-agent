#!/usr/bin/env python
"""Development server for the Wellness Agent."""

import uvicorn
import os
from dotenv import load_dotenv

def run_server():
    """Run the development server."""
    # Load environment variables
    load_dotenv()
    
    # Log configuration
    print("Starting Wellness Agent development server...")
    print(f"Environment: {'production' if os.getenv('PRODUCTION') else 'development'}")
    
    # Start the server
    uvicorn.run(
        "wellness_agent.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,  # Enable auto-reload for development
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

if __name__ == "__main__":
    run_server() 