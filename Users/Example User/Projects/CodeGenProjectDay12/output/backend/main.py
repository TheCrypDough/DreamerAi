# main.py
# Backend server for the Simple Counter Web App

import uvicorn
from fastapi import FastAPI
from typing import Dict

# Create a FastAPI application instance
# This is the main entry point for the API
app = FastAPI(
    title="Simple Counter Backend",
    description="Minimal FastAPI backend for the counter application.",
    version="0.1.0",
)

@app.get("/", tags=["Root"])
async def read_root() -> Dict[str, str]:
    """
    Root endpoint to check if the backend is running.
    Returns a simple welcome message.
    """
    return {"message": "Backend Online"}

# Placeholder for future counter-related endpoints
# Example:
# @app.get("/api/v1/counter", tags=["Counter"])
# async def get_counter() -> Dict[str, int]:
#     # In a real application, this would fetch from a database or state
#     return {"current_value": 0} # Returning a hardcoded initial value for now

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    # "main:app" tells Uvicorn to look for the 'app' instance in the 'main.py' file.
    # host="0.0.0.0" makes the server accessible on the network.
    # port=8000 specifies the port number.
    # reload=True enables auto-reloading during development when code changes.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)