# C:\DreamerAI\main.py (REVISED FOR DAY 18 - Hermie V1 Test ONLY)
import asyncio
import os
import sys
from typing import Dict, Optional, List, Any
from pathlib import Path
import json
import traceback

# Add project root...
project_root_main = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_main not in sys.path: sys.path.insert(0, project_root_main)

# Import necessary components
try:
    from engine.agents.base import BaseAgent
    # Import Hermie and potentially others needed ONLY for instantiation context if Hermie's __init__ requires it V1
    from engine.agents.communications import HermieAgent
    # Import other agents IF keeping their direct test blocks below
    from engine.agents.administrator import LewisAgent # Example if Lewis test is kept
    # ... (Specialists, etc.) ...
    from engine.core.logger import logger_instance as logger
    # Import DB Pool functions if needed for other tests or shutdown
    # from engine.core.db import initialize_db_pool, close_db_pool # Keep commented unless needed by other tests
except ImportError as e:
    print(f"CRITICAL ERROR importing modules in main.py: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
     print(f"CRITICAL UNEXPECTED ERROR during imports in main.py: {e}")
     traceback.print_exc()
     sys.exit(1)

DEFAULT_USER_DIR = r"C:\DreamerAI\Users\TestUserMain"

async def run_agent_tests(): # Renamed function to reflect focus
    logger.info("--- Initializing DreamerAI Backend (Direct Agent Tests - Day 18 Focus) ---")
    # await initialize_db_pool() # Keep commented

    user_workspace_dir = Path(DEFAULT_USER_DIR)
    user_workspace_dir.mkdir(parents=True, exist_ok=True) # Ensure base user dir exists

    # --- Agent Initialization --- #
    agents: Dict[str, BaseAgent] = {}
    try:
        # Instantiate Hermie V1 (placeholder)
        # Passing agents dict for future compatibility, but Hermie V1 doesn't use it.
        agents["Hermie"] = HermieAgent(agents=agents, user_dir=str(user_workspace_dir))
        # Instantiate others ONLY if their direct tests are being kept below
        try: agents["Lewis"] = LewisAgent(user_dir=str(user_workspace_dir)) # Keep Lewis test setup
        except NameError: logger.warning("LewisAgent not defined, skipping...")
        # ...
        logger.info("Agents required for Day 18 tests instantiated.")
    except Exception as e:
        logger.exception(f"Agent initialization failed: {e}")
        # await close_db_pool() # Keep commented
        return

    # --- Test Hermie V1 Directly --- #
    print("\n" + "="*10 + " Testing Hermie V1 Placeholder " + "="*10)
    hermie_agent = agents.get("Hermie")
    if hermie_agent:
        print(f"Calling Hermie V1 placeholder run...")
        try:
            hermie_result = await hermie_agent.run(input_context="Direct Test Trigger D18")
            print(f"Hermie V1 Result: {json.dumps(hermie_result, indent=2)}")
            # Verification
            assert hermie_result.get("status") == "success", "Hermie V1 run status incorrect!"
            assert "simulation complete" in hermie_result.get("message",""), "Hermie V1 message incorrect!"
            print("\n -> Hermie V1 Placeholder Test PASSED.")
            print(" -> ACTION REQUIRED: Check logs for Hermie V1 simulation messages.")
        except Exception as hermie_e:
             print(f"ERROR running Hermie V1 test: {hermie_e}")
             logger.exception("Hermie V1 test block failed.")
    else:
        print("ERROR: Hermie agent not found for testing.")
    print("="*50)

    # --- Optional: Keep Other Direct Agent Tests Here If Needed --- #
    # Example: Keeping Lewis V1 Test Block from Day 17
    print("\n" + "="*10 + " Testing Lewis V1 Placeholder " + "="*10)
    lewis_agent = agents.get("Lewis")
    if lewis_agent:
        try:
            logger.info("Testing Lewis: List tools by category 'AI'...")
            category_tools = lewis_agent.list_tools_by_category("AI") # Uses cache
            logger.info(f"Tools in category 'AI': {json.dumps(category_tools, indent=2)}")

            tool_name_test = "Ollama"
            logger.info(f"Testing Lewis: Get info for specific tool '{tool_name_test}'...")
            tool_info = lewis_agent.get_tool_info(tool_name_test) # Uses cache
            if tool_info:
                logger.info(f"Info for tool '{tool_name_test}': {json.dumps(tool_info, indent=2)}")
            else:
                logger.warning(f"Tool '{tool_name_test}' not found in Lewis's toolchest.")
            print(" -> Lewis V1 Placeholder Test Block Finished (Check Logs).")
        except Exception as e:
            logger.error(f"Error during Lewis V1 direct tests: {e}", exc_info=True)
    else:
        logger.warning("Lewis agent not found in agents dictionary, skipping tests.")
    print("="*50)
    # ... (Other tests like Specialists V1, QA V1, etc. can be added here) ...

    # --- Agent Shutdown --- #
    logger.info("\n--- Shutting Down Agents ---")
    for name, agent in agents.items():
        if hasattr(agent, 'shutdown'):
            logger.debug(f"Shutting down {name}...")
            try: await agent.shutdown()
            except Exception as shut_e: logger.error(f"Error shutting down {name}: {shut_e}")

    # await close_db_pool() # Keep commented
    # logger.info("DB Pool closed.")
    print("\n--- All Day 18 Tests Finished ---")


if __name__ == "__main__":
    # Ensure venv active.
    # Ensure Hermie RAG DB seed script (seed_rag_hermie.py) ran successfully.
    # Does NOT require n8n running for this specific test.
    asyncio.run(run_agent_tests()) 