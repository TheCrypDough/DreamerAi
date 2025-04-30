import uvicorn
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect # Added WebSocket imports
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
    from .logger import logger_instance as logger
    from .db import db_instance # Use the initialized DB instance from db.py
    from .project_manager import ProjectManager # NEW import
    from engine.agents.main_chat import ChefJeff # Keep Jeff import for its endpoint
except ImportError as e:
     logger.error(f"Failed core imports in server.py: {e}")
     db_instance = None
     ProjectManager = None # Ensure ProjectManager is None if import fails
     ChefJeff = None # Ensure ChefJeff is None if import fails

# Import WebSocket Manager
try:
    from engine.core.dream_theatre_service import manager # Use the singleton manager instance
except ImportError:
    logger.error("Failed to import ConnectionManager for Dream Theatre!")
    manager = None # Allow server to start but WS will fail

# --- FastAPI App Initialization ---
app = FastAPI(title="DreamerAI Backend API", version="0.1.0")

# --- CORS Middleware ---
# Allow requests from the Electron frontend (adjust origin if different)
# For development, allowing all origins might be okay, but restrict in production.
origins = [
    "*" # Allow all origins for development testing (including WebSockets)
    # "http://localhost", # Base domain
    # "http://localhost:3000", # Default React dev server port (if used)
    # "http://localhost:3131",  # UI Bridge listener port
    # "app://.", # Allow Electron app origin
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use the updated origins list
    allow_credentials=True, # Keep this True if you need cookies/auth headers
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

# --- Instantiate Core Services ---
# TODO: Replace with proper dependency injection later
project_manager_instance = ProjectManager() if ProjectManager else None

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

        logger.debug(f"Received user input for Jeff: '{user_input[:50]}...'" )

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

# --- NEW Endpoint for Subprojects --- # Placed before WebSocket for logical grouping
@app.post("/projects/{project_id}/subprojects", status_code=201)
async def create_subproject_endpoint(project_id: int, request: Request):
    """Endpoint to create a new subproject under a given parent project."""
    logger.info(f"Received request to create subproject for parent project ID: {project_id}")

    if not db_instance:
         logger.error("Subproject creation failed: Database service unavailable.")
         raise HTTPException(status_code=503, detail="Database service unavailable.")
    if not project_manager_instance:
         logger.error("Subproject creation failed: Project manager service unavailable.")
         raise HTTPException(status_code=503, detail="Project manager service unavailable.")

    try:
        data = await request.json()
        subproject_name = data.get("subproject_name")
        # user_id_from_request = data.get("user_id", "Example User") # TODO: Get from auth later

        if not subproject_name:
            logger.warning("Subproject creation failed: subproject_name missing.")
            raise HTTPException(status_code=400, detail="subproject_name is required.")

        # 1. Verify parent project exists and get its path
        parent_project = db_instance.get_project(project_id)
        if not parent_project:
            logger.warning(f"Subproject creation failed: Parent project ID {project_id} not found.")
            raise HTTPException(status_code=404, detail=f"Parent project with ID {project_id} not found.")

        parent_project_path = Path(parent_project["project_path"])
        logger.debug(f"Found parent project path: {parent_project_path}")

        # 2. Create directory structure using ProjectManager
        subproject_dir_path = project_manager_instance.create_subproject_structure(
            parent_project_path=parent_project_path,
            subproject_name=subproject_name
        )

        if not subproject_dir_path:
            # Error already logged by project_manager
            raise HTTPException(status_code=500, detail="Failed to create subproject directory structure.")

        # 3. Add subproject record to database
        # Store relative path for portability
        relative_subproject_path = subproject_dir_path.relative_to(parent_project_path)
        subproject_id = db_instance.add_subproject(
            parent_project_id=project_id,
            name=subproject_name,
            subproject_path=str(relative_subproject_path)
        )

        if not subproject_id:
            # Error already logged by db
            # Optional: Attempt to clean up created directory if DB fails? Complex.
            raise HTTPException(status_code=500, detail="Failed to save subproject record to database.")

        logger.info(f"Subproject '{subproject_name}' (ID: {subproject_id}) created successfully for project {project_id}.")
        return {
            "status": "success",
            "message": f"Subproject '{subproject_name}' created successfully.",
            "subproject_id": subproject_id,
            "path": str(subproject_dir_path) # Return absolute path for confirmation
        }

    except json.JSONDecodeError:
         logger.error("Subproject creation failed: Invalid JSON format in request body.")
         raise HTTPException(status_code=400, detail="Invalid JSON format in request body.")
    except Exception as e:
        logger.exception(f"Error creating subproject for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error creating subproject: {str(e)}")

# --- NEW Endpoint for GitHub Auth Token Receipt (Day 25) ---
@app.post("/auth/github/token")
async def receive_github_token(request: Request):
    """
    Endpoint to receive the GitHub access token obtained by the frontend OAuth flow.
    V1 simply stores it in a global variable (placeholder).
    """
    global github_token # Allow modification of global var
    logger.info("Received request at /auth/github/token")
    try:
        data = await request.json()
        token = data.get("token")

        if not token or not isinstance(token, str):
            logger.warning("Received invalid or missing token in request body.")
            raise HTTPException(status_code=400, detail="Valid 'token' string required in request body.")

        # V1: Store globally - UNSAFE FOR PRODUCTION / MULTI-USER
        # TODO: Implement secure, user-specific token storage (e.g., encrypted in DB linked to user session)
        github_token = token
        logger.info(f"Successfully received and stored GitHub access token (globally - V1). Token starts with: {token[:10]}...") # Log prefix only

        return {"status": "success", "message": "GitHub token received by backend."}

    except json.JSONDecodeError:
         logger.error("Failed to decode JSON body for GitHub token.")
         raise HTTPException(status_code=400, detail="Invalid JSON format in request body.")
    except Exception as e:
        logger.exception(f"Error receiving GitHub token: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error receiving token: {str(e)}")

# --- Dream Theatre WebSocket Endpoint ---
@app.websocket("/ws/dream-theatre/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    logger.info(f"WebSocket connection attempt received for client: {client_id}")
    if not manager:
        logger.error("ConnectionManager not available. Cannot handle WebSocket connection.")
        await websocket.close(code=1008) # Policy Violation
        return

    try:
        logger.info(f"Attempting manager.connect for client: {client_id}")
        await manager.connect(websocket, client_id)
        logger.info(f"Successfully completed manager.connect for client: {client_id}")
    except Exception as connect_exc:
         logger.error(f"*** EXCEPTION during manager.connect for {client_id}: {connect_exc} ***", exc_info=True)
         await websocket.close(code=1011)
         return

    try:
        while True:
            # Keep connection open, listen for messages (if frontend needs to send any)
            # For V1, we mostly broadcast FROM server, so listening might be minimal.
            data = await websocket.receive_text()
            logger.info(f"Dream Theatre WS received from {client_id}: {data}")
            # Example broadcast:
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        logger.info(f"Dream Theatre WebSocket client {client_id} disconnected.")
    except Exception as e:
        logger.error(f"Error in Dream Theatre WebSocket loop for {client_id}: {e}", exc_info=True)
    finally:
        logger.info(f"Disconnecting client {client_id} in finally block.")
        manager.disconnect(websocket, client_id)

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
    # Use port 8090 for consistency with launch command
    uvicorn.run(app, host="127.0.0.1", port=8090, log_level="info")
    # Note: Running directly might differ from deployment (e.g., using Gunicorn)