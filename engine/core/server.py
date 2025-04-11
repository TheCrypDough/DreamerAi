import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Assuming logger_instance is globally available after Day 3 setup
try:
    from .logger import logger_instance as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__) # Fallback logger

try:
    from .db import DreamerDB
except ImportError:
    # This fallback is less ideal, but prevents crashing if db.py has issues
    DreamerDB = None
    logger.error("Failed to import DreamerDB from .db")

app = FastAPI(title="DreamerAI Backend")

db_instance: DreamerDB | None = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on server startup."""
    global db_instance
    if DreamerDB:
        try:
            db_instance = DreamerDB() # Creates instance, connects, and initializes tables
            logger.info("Database instance created successfully.")
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to initialize database on startup: {e}", exc_info=True)
            # Depending on requirements, you might want to prevent server startup here
    else:
        logger.warning("DreamerDB class not available, proceeding without database.")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on server shutdown."""
    if db_instance:
        db_instance.close()
        logger.info("Database connection closed on shutdown.")

# CORS Middleware Configuration
# Allow all origins for development simplicity. Restrict in production.
origins = [
    "*", # Allows all origins
    # You might want to restrict this more specifically later, e.g.:
    # "http://localhost:3000", # If using a specific port for React dev server
    # "file://", # May or may not work reliably depending on browser/Electron version
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

@app.get("/")
def read_root():
    """Root endpoint to check if the server is online."""
    logger.info("Root endpoint accessed.")
    return {"message": "DreamerAI Backend Online"}

# Add other endpoints here later (e.g., for agents, projects)

if __name__ == "__main__":
    logger.info("Starting DreamerAI backend server...")
    # Run the server locally on port 8000
    # reload=True is useful for development but should be False in production
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
    # Note: Using "server:app" tells uvicorn to look for the `app` instance
    # in the file named `server.py` (this file). 