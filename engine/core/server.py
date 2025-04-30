import uvicorn
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Body, Depends # Added Body and Depends for VC endpoints
from fastapi.middleware.cors import CORSMiddleware # To allow frontend requests
import sys
import os
import time # For timestamp generation
from typing import Optional, Dict, Any # Added Dict, Any for VC endpoints
from pathlib import Path
import json
import traceback # Added for detailed exception logging
from dependency_injector.wiring import inject, Provide # Added for DI

# Add project root to path for sibling imports (engine, etc.)
# Adjust based on actual execution context if needed
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try to import keytar for secure token storage
try:
    import keytar
    KEYTAR_AVAILABLE_BACKEND = True
except ImportError: 
    KEYTAR_AVAILABLE_BACKEND = False
    logger.error("Backend keytar missing!")

try:
    from .logger import logger_instance as logger
    from .db import db_instance # Use the initialized DB instance from db.py
    from .project_manager import ProjectManager # NEW import
    from engine.agents.main_chat import ChefJeff # Keep Jeff import for its endpoint
    from engine.core.version_control import VersionControl
except ImportError as e:
     logger.error(f"Failed core imports in server.py: {e}")
     db_instance = None
     ProjectManager = None # Ensure ProjectManager is None if import fails
     ChefJeff = None # Ensure ChefJeff is None if import fails
     VersionControl = None # Ensure VersionControl is None if import fails

# Import container wiring
try:
    from engine.di.container import Container
except ImportError:
    logger.error("Failed to import Dependency Injection Container!")
    Container = None

# Import User model for auth verification
try:
    from engine.models.user import UserSchema
    from engine.core.auth import get_current_active_user
except ImportError:
    logger.error("Failed to import User auth models!")
    UserSchema = None
    get_current_active_user = None

# Import WebSocket Manager
try:
    from engine.core.dream_theatre_service import manager # Use the singleton manager instance
except ImportError:
    logger.error("Failed to import ConnectionManager for Dream Theatre!")
    manager = None # Allow server to start but WS will fail

# --- Constants for Backend Keytar Store ---
GITHUB_KEYCHAIN_SERVICE_BE = 'DreamerAI_GitHub_Backend_D66' # Unique backend service name
GITHUB_KEYCHAIN_ACCOUNT_BE = 'user_github_token_for_user_{uid}' # User-scoped V2 naming pattern

# --- Helper to Get GitHub Token from Backend Keychain (V2: User Scoped) ---
async def get_token_from_keychain(user_uid: str) -> Optional[str]:
    """ Retrieves GitHub token securely stored by the backend via keytar for a SPECIFIC user. """
    if not KEYTAR_AVAILABLE_BACKEND: 
        logger.error("Keytar unavailable on backend.")
        return None
    
    # Construct user-specific account name
    account_name = GITHUB_KEYCHAIN_ACCOUNT_BE.format(uid=user_uid)
    try:
        token = await keytar.get_password(GITHUB_KEYCHAIN_SERVICE_BE, account_name)
        if not token: 
            logger.warning(f"No GitHub token found in keychain for account {account_name}.")
        else: 
            logger.debug("Retrieved GitHub token from backend keychain.")
        return token
    except Exception as e:
        # Catch specific errors maybe? V1 log generic.
        logger.error(f"Failed to get GitHub token from keychain for account {account_name}: {e}")
        return None

# --- Helper to Save GitHub Token to Backend Keychain (NEW) ---
async def save_token_to_keychain(user_uid: str, token: str) -> bool:
    """ Securely stores GitHub token via backend keytar for a SPECIFIC user. """
    if not KEYTAR_AVAILABLE_BACKEND: 
        logger.error("Keytar unavailable on backend.")
        return False
    
    account_name = GITHUB_KEYCHAIN_ACCOUNT_BE.format(uid=user_uid)
    try:
        await keytar.set_password(GITHUB_KEYCHAIN_SERVICE_BE, account_name, token)
        logger.info(f"Stored GitHub token securely in backend keychain for account {account_name}.")
        return True
    except Exception as e:
        logger.exception(f"Failed to store GitHub token in keychain for account {account_name}: {e}")
        return False

# --- Helper to Get Project Path and Verify Ownership ---
async def get_project_path_for_user(project_id: int, user: UserSchema, db_pool) -> Path:
    """Get project path and verify the user owns the project."""
    async with db_pool.acquire() as conn:
        query = "SELECT * FROM projects WHERE id = $1"
        project = await conn.fetchrow(query, project_id)
        
        if not project:
            logger.error(f"Project with ID {project_id} not found.")
            raise HTTPException(404, f"Project not found: {project_id}")
        
        # Verify project ownership
        if project['user_uid'] != user.firebase_uid:
            logger.error(f"User {user.firebase_uid} attempted to access project {project_id} owned by {project['user_uid']}.")
            raise HTTPException(403, "You don't have permission to access this project.")
        
        project_path = Path(project['project_path'])
        if not project_path.exists():
            logger.error(f"Project path {project_path} doesn't exist on the filesystem.")
            raise HTTPException(500, "Project directory not found on server.")
            
        return project_path

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

# --- MODIFY Auth Endpoint (/auth/github/token D25/66) ---
@app.post("/auth/github/token")
@inject # Make sure container available if db access added later maybe?
async def receive_github_token_and_store_backend(
    request: Request,
    # Future: Inject User from internal JWT maybe via different Depends
    # user: UserSchema = Depends(get_current_active_user) # V2+ need user context here too! V1 implicit.
    # V1 Hack: How do we get user_uid here reliably?
    # Option 1: UI sends UID along with token (INSECURE).
    # Option 2: Endpoint requires internal JWT header + returns success? (Better)
    # Decision V1: Require internal JWT from D101, use UID from there for keytar.
    current_user: UserSchema = Depends(get_current_active_user) # Use the internal auth dependency!
):
    """ Receives GitHub token obtained by UI, stores it SECURELY in backend keytar. """
    token = None; uid = current_user.firebase_uid # Get UID from verified internal JWT
    try: 
        data = await request.json(); 
        token = data.get("token")
    except: 
        raise HTTPException(400, "Invalid JSON.")
    
    if not token: 
        raise HTTPException(400, "Token required.")

    logger.info(f"Received GitHub token from UI for user {uid}. Storing in backend keychain...")
    store_ok = await save_token_to_keychain(uid, token)

    if store_ok:
        return {"status": "success", "message": "GitHub token received and stored securely."}
    else:
        raise HTTPException(500, "Failed to store GitHub token securely in backend.")

# --- Add NEW VC Remote Endpoints ---
@app.post("/projects/{project_id}/vc/remote/create")
@inject
async def create_github_repo_endpoint(
    project_id: int,
    payload: Dict[str, Any] = Body({"repo_name": None, "private": False}),
    user: UserSchema = Depends(get_current_active_user),
    db_pool = Depends(Provide[Container.db_pool_provider]) # V1 Pool DI Hack
):
    repo_name = payload.get("repo_name")
    is_private = payload.get("private", False)
    pool = await db_pool() # V1 get pool
    
    if not pool: 
        raise HTTPException(503, "DB Pool unavailable.")
    if not VersionControl: 
        raise HTTPException(503, "VC Service unavailable.")

    try:
        project_path = await get_project_path_for_user(project_id, user, pool) # Existing helper D106 check
        if not repo_name: 
            repo_name = f"{project_path.name}-dreamerai-{int(time.time())}" # Auto-name

        logger.info(f"User {user.firebase_uid} creating GitHub repo '{repo_name}' @ {project_path}")
        github_token = await get_token_from_keychain(user.firebase_uid) # Secure retrieve for this user
        if not github_token: 
            raise HTTPException(401, "Backend GitHub token missing or inaccessible.")

        vc = VersionControl(str(project_path))
        if not vc.repo: 
            vc.init_repo() # Init repo if needed before setting remote

        clone_url = await vc.create_github_repo(repo_name, github_token, is_private) # Pass token

        if clone_url: 
            return {"status": "success", "message": "GitHub repository created.", "clone_url": clone_url}
        else: 
            raise HTTPException(500, "Failed to create GitHub repository.") # VC method logs detail
    except HTTPException as http_exc: 
        raise http_exc
    except Exception as e: 
        logger.exception(f"Error creating GitHub repo: {e}")
        raise HTTPException(500, f"Internal server error: {e}")


@app.post("/projects/{project_id}/vc/remote/push")
@inject
async def push_to_github_endpoint(
    project_id: int,
    payload: Dict[str, Any] = Body(...),
    user: UserSchema = Depends(get_current_active_user),
    db_pool = Depends(Provide[Container.db_pool_provider]) # V1 Pool DI Hack
):
    branch = payload.get("branch") if payload else None
    pool = await db_pool() # V1 get pool
    
    if not pool: 
        raise HTTPException(503, "DB Pool unavailable.")
    if not VersionControl: 
        raise HTTPException(503, "VC Service unavailable.")

    try:
        project_path = await get_project_path_for_user(project_id, user, pool) # Get/Verify path
        logger.info(f"User {user.firebase_uid} pushing project {project_id} @ {project_path}")

        vc = VersionControl(str(project_path))
        if not vc.repo: 
            raise HTTPException(400, "Local repo not initialized.")

        # Token NOT needed for vc.push_to_remote V1 (relies on system auth)
        success = await vc.push_to_remote(branch=branch)

        if success: 
            return {"status": "success", "message": "Push attempted (Verify via System Git/GitHub)."}
        else: 
            raise HTTPException(500, "Push command failed. Check backend logs/system auth.")
    except HTTPException as http_exc: 
        raise http_exc
    except Exception as e: 
        logger.exception(f"Error pushing to GitHub: {e}")
        raise HTTPException(500, f"Internal server error: {e}")

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