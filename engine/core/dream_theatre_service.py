# engine/core/dream_theatre_service.py
from fastapi import WebSocket
from typing import List, Dict, Optional
import asyncio
import json

try:
    # Attempt to import the logger instance
    from engine.core.logger import logger_instance as logger
except ImportError:
    # Fallback to standard logging if logger_instance is not found
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.info("Using standard logging for dream_theatre_service.")

class ConnectionManager:
    """Manages active WebSocket connections for the Dream Theatre service."""
    def __init__(self):
        # Structure: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        logger.info("Dream Theatre ConnectionManager initialized.")

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accepts a new WebSocket connection and registers it."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")
        # Optionally send a welcome message or initial state
        # await self.send_personal_message("Welcome to Dream Theatre!", client_id)

    def disconnect(self, websocket: WebSocket, client_id: str):
        """Removes a WebSocket connection upon disconnection."""
        if client_id in self.active_connections:
            # Ensure the websocket object matches before removing, though client_id should be unique
            if self.active_connections[client_id] == websocket:
                del self.active_connections[client_id]
                logger.info(f"WebSocket disconnected: {client_id}")
            else:
                 logger.warning(f"Disconnect request for {client_id}, but WebSocket object mismatch.")
        else:
            logger.warning(f"Attempted to disconnect non-existent client: {client_id}")

    async def send_personal_message(self, message: str, client_id: str):
        """Sends a plain text message to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(message)
                logger.debug(f"Sent personal message to {client_id}: {message[:50]}...")
            except Exception as e:
                logger.error(f"Error sending personal message to {client_id}: {e}")
                # Consider disconnecting if send fails consistently
                # self.disconnect(websocket, client_id)
        else:
            logger.warning(f"Attempted to send personal message to non-existent client: {client_id}")

    async def send_json_message(self, data: dict, client_id: str):
        """Sends a JSON message (dict) to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(data)
                logger.debug(f"Sent JSON message to {client_id}: {json.dumps(data)[:100]}...")
            except Exception as e:
                logger.error(f"Error sending JSON message to {client_id}: {e}")
                # Consider disconnecting if send fails consistently
                # self.disconnect(websocket, client_id)
        else:
            logger.warning(f"Attempted to send JSON message to non-existent client: {client_id}")

    async def broadcast_text(self, message: str):
        """Sends a plain text message to all connected clients."""
        if not self.active_connections:
            logger.info("Broadcast requested, but no clients connected.")
            return

        logger.info(f"Broadcasting text to {len(self.active_connections)} clients: {message[:50]}...")
        # Use asyncio.gather for concurrent sending
        results = await asyncio.gather(
            *[conn.send_text(message) for conn in self.active_connections.values()],
            return_exceptions=True
        )
        # Log any errors that occurred during broadcast
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                client_id = list(self.active_connections.keys())[i] # Not perfectly safe if dict changes during await
                logger.error(f"Error broadcasting text to client (likely {client_id}): {result}")

    async def broadcast_json(self, data: dict):
        """Sends a JSON message (dict) to all connected clients."""
        if not self.active_connections:
            logger.info("Broadcast requested, but no clients connected.")
            return

        logger.info(f"Broadcasting JSON to {len(self.active_connections)} clients: {json.dumps(data)[:100]}...")
        results = await asyncio.gather(
            *[conn.send_json(data) for conn in self.active_connections.values()],
            return_exceptions=True
        )
        # Log any errors that occurred during broadcast
        for i, result in enumerate(results):
             if isinstance(result, Exception):
                 client_id = list(self.active_connections.keys())[i] # Not perfectly safe if dict changes during await
                 logger.error(f"Error broadcasting JSON to client (likely {client_id}): {result}")

# --- Singleton Instance ---
# Create a single instance of the manager to be used throughout the application
manager = ConnectionManager()
logger.info("Singleton ConnectionManager instance 'manager' created for Dream Theatre.") 