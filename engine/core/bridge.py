# C:\DreamerAI\engine\core\bridge.py
import asyncio
import json
import aiohttp
import traceback
from typing import Dict, Any

try:
    # Attempt to import the logger instance assuming it's configured
    from .logger import logger_instance as logger
except ImportError:
    # Fallback to standard logging if logger_instance is not available
    import logging
    logger = logging.getLogger(__name__)
    # Basic configuration for the fallback logger if needed
    logging.basicConfig(level=logging.INFO)
    logger.warning("Could not import logger_instance from .logger, using standard logging.")

# Define the target URL for the frontend listener
FRONTEND_LISTENER_URL = "http://localhost:3131/update"

async def send_to_ui(message_payload: Dict[str, Any]):
    """
    Sends a structured message payload asynchronously to the Electron UI listener.

    Args:
        message_payload: A dictionary containing message details.
                         Expected format: {"agent": str, "type": str, "payload": Any}
                         e.g., {"agent": "Jeff", "type": "chat_response", "payload": "Hello there!"}
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Set a reasonable timeout for the request
            async with session.post(FRONTEND_LISTENER_URL, json=message_payload, timeout=5) as response:
                response_text = await response.text() # Read response for logging
                if response.status == 200:
                    logger.debug(f"Successfully sent message to UI: Type='{message_payload.get('type', 'N/A')}', Agent='{message_payload.get('agent', 'N/A')}'")
                    logger.debug(f"UI Listener response: {response_text}")
                else:
                    logger.error(f"Failed to send message to UI. Status: {response.status}, Response: {response_text}, Payload: {message_payload}")
    except aiohttp.ClientConnectionError as e:
        logger.error(f"UI Bridge Connection Error: Cannot connect to {FRONTEND_LISTENER_URL}. Is the frontend running and listener active? Error: {e}")
    except asyncio.TimeoutError:
        logger.error(f"UI Bridge Timeout: Request to {FRONTEND_LISTENER_URL} timed out.")
    except json.JSONDecodeError as e:
         logger.error(f"UI Bridge JSON Error: Could not serialize payload. Error: {e}. Payload: {message_payload}")
    except Exception as e:
        logger.error(f"UI Bridge Error: Unexpected error sending message: {e}\n{traceback.format_exc()}")

# --- Basic Test Block ---
async def test_bridge():
    print("--- Testing UI Bridge ---")
    test_payload_1 = {"agent": "System", "type": "status", "payload": "Bridge test message 1."}
    test_payload_2 = {"agent": "Jeff", "type": "chat_response", "payload": {"text": "Test reply from Jeff via bridge.", "timestamp": "now"}}

    print(f"Sending payload 1 to {FRONTEND_LISTENER_URL}: {test_payload_1}")
    await send_to_ui(test_payload_1)
    await asyncio.sleep(1) # Pause slightly between tests

    print(f"Sending payload 2 to {FRONTEND_LISTENER_URL}: {test_payload_2}")
    await send_to_ui(test_payload_2)
    print("--- Bridge Test Finished --- Check frontend console for received messages.")


if __name__ == "__main__":
    # NOTE: This test requires the Electron App (App.jsx listener) to be running first!
    # Run: `cd C:\DreamerAI\app` then `npm start`
    # Then run this script: `cd C:\DreamerAI` then `.\venv\Scripts\activate` then `python -m engine.core.bridge`
    # Improved fallback logger handling for the test block
    try:
        from .logger import logger_instance
    except ImportError:
        print("Running bridge test with basic logging configuration.")
    
    asyncio.run(test_bridge()) 