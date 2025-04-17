import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware # To allow frontend requests
import sys
import os
from typing import Optional # Added for github_token type hint
from pathlib import Path
import json
import traceback # Added for detailed exception logging

# Add project root to path for sibling imports (engine, etc.)
# Adjust based on actual execution context if needed
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from engine.core.logger import logger_instance as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.warning("Could not import logger_instance, using basic logging.")

# NEW: Import ChefJeff
try:
    from engine.agents.main_chat import ChefJeff
except ImportError:
    logger.error("Failed to import ChefJeff agent in server.py!")
    ChefJeff = None # Allow server to start but endpoint will fail

# --- FastAPI App Initialization ---
app = FastAPI(title="DreamerAI Backend API", version="0.1.0")

# --- CORS Middleware ---
# Allow requests from the Electron frontend (adjust origin if different)
# For development, allowing all origins might be okay, but restrict in production.
origins = [
    "http://localhost", # Base domain
    "http://localhost:3000", # Default React dev server port (if used)
    "http://localhost:3131",  # UI Bridge listener port
    "app://.", # Allow Electron app origin
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Global Variables / State (Use cautiously, consider context/dependency injection) ---
# Example: Store GitHub token globally (Needs proper user session management later)
github_token: Optional[str] = None

# TODO: Need a better way to manage agent instances and user sessions/directories.
# For Day 14, we instantiate Jeff per request, using a default path. This is NOT scalable.
DEFAULT_USER_DIR_SERVER = r"C:\DreamerAI\Users\Example User"
# Ensure default dir exists for the agent run
os.makedirs(os.path.join(DEFAULT_USER_DIR_SERVER, "Projects"), exist_ok=True)
os.makedirs(os.path.join(DEFAULT_USER_DIR_SERVER, "Chats", "Jeff"), exist_ok=True)

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """Root endpoint to check if the backend is online."""
    logger.info("Root endpoint accessed. Backend is online.")
    return {"message": "DreamerAI Backend Online - Welcome!"}

# Placeholder for setting GitHub token (from Day 51/53 logic) - needs refinement
@app.post("/set-github-token")
async def set_github_token(request: Request):
    global github_token
    try:
        data = await request.json()
        token = data.get('token')
        if not token:
            raise HTTPException(status_code=400, detail="Token required in request body")
        github_token = token
        logger.info("Received and stored GitHub token.")
        return {"status": "ok", "message": "GitHub token received"}
    except Exception as e:
        logger.error(f"Error setting GitHub token: {e}")
        raise HTTPException(status_code=500, detail="Failed to process token")

# --- NEW Endpoint for Jeff ---
@app.post("/agents/jeff/chat")
async def handle_jeff_chat(request: Request):
    """Endpoint to receive user chat messages and forward them to Jeff."""
    logger.info("Received request for /agents/jeff/chat")
    if not ChefJeff: # Check if import failed
        logger.error("ChefJeff agent class not loaded. Cannot process chat.")
        raise HTTPException(status_code=500, detail="Chat agent service is unavailable.")

    try:
        data = await request.json()
        user_input = data.get("user_input")

        if not user_input:
            logger.warning("Received chat request with empty input.")
            raise HTTPException(status_code=400, detail="User input cannot be empty.")

        logger.debug(f"Received user input for Jeff: '{user_input[:50]}...'")

        # TODO: TEMPORARY - Instantiate Jeff per request. Need proper agent lifecycle mgmt later.
        # Use the default user dir for now. Future requires user context.
        logger.warning("Instantiating ChefJeff per request (temporary).")
        jeff_agent = ChefJeff(user_dir=DEFAULT_USER_DIR_SERVER)

        # Execute Jeff's run method (which includes sending response via bridge)
        # We don't directly use the return value here for the chat panel display.
        agent_result = await jeff_agent.run(user_input=user_input)

        # Return acknowledgment to the calling frontend fetch
        logger.info("Jeff agent run initiated. Response sent via bridge.")
        return {"status": "received", "message": "Input sent to Jeff for processing."}

    except json.JSONDecodeError:
         logger.error("Failed to decode JSON body for Jeff chat.")
         raise HTTPException(status_code=400, detail="Invalid JSON format in request body.")
    except Exception as e:
        logger.exception(f"Error handling Jeff chat request: {e}") # Log full traceback
        raise HTTPException(status_code=500, detail=f"Internal server error processing chat: {str(e)}")

# Add more endpoints here later for:
# - /create-project, /create-subproject (Day 25)
# - /optimize-prompt (Day 30)
# - /templates, /upload-template (Day 54)
# - /set-model (Day 56)
# - /export-project (Day 57)
# - /set-user-token (Firebase - Day 58)
# - /commit, /push, /repo-status (Version Control - Day 53)
# - Agent-specific endpoints if needed (e.g., /jeff/chat)


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Starting DreamerAI Backend Server...")
    # Use port 8000 for the backend API server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    # Note: Running directly might differ from deployment (e.g., using Gunicorn) 