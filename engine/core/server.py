import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware # To allow frontend requests
import sys
import os
from typing import Optional # Added for github_token type hint
from pathlib import Path

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
    logger.warning("Could not import custom logger, using basic logging.")


# --- FastAPI App Initialization ---
app = FastAPI(title="DreamerAI Backend API", version="0.1.0")

# --- CORS Middleware ---
# Allow requests from the Electron frontend (adjust origin if different)
# For development, allowing all origins might be okay, but restrict in production.
origins = [
    "http://localhost", # Base domain
    "http://localhost:3000", # Default React dev server port (if used)
    "app://.", # Allow Electron app origin
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for easy dev start - tighten later!
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Global Variables / State (Use cautiously, consider context/dependency injection) ---
# Example: Store GitHub token globally (Needs proper user session management later)
github_token: Optional[str] = None

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