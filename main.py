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

# Import necessary components for this specific test
try:
    from engine.agents.base import BaseAgent # Need BaseAgent for type hinting
    from engine.agents.communications import HermieAgent # Agent being tested
    from engine.core.logger import logger_instance as logger
    # Import DB Pool functions ONLY for shutdown if needed
    # Assume D100 PG refactor is done - we need the PG pool init/close
    from engine.core.db import initialize_db_pool, close_db_pool
except ImportError as e:
    print(f"CRITICAL ERROR importing modules in main.py: {e}")
    # If the error is about db pool funcs, comment them out below too!
    if 'initialize_db_pool' in str(e) or 'close_db_pool' in str(e):
        print("NOTE: DB Pool functions not found in engine.core.db. Proceeding without DB Pool init/close for this test.")
        initialize_db_pool = None
        close_db_pool = None
    else:
        traceback.print_exc()
        sys.exit(1)
except Exception as e:
     print(f"CRITICAL UNEXPECTED ERROR during imports in main.py: {e}")
     traceback.print_exc()
     sys.exit(1)

DEFAULT_USER_DIR = r"C:\DreamerAI\Users\TestUserMain_D18" # Use a specific dir maybe

async def run_hermie_v1_test():
    logger.info("--- Initializing Backend for Hermie V1 Test ---")
    # Assume initialize_db_pool() uses DATABASE_URL env var for PG
    if initialize_db_pool: # Only call if import succeeded
        await initialize_db_pool() # Init DB Pool for BaseAgent V2 consistency
    else:
        logger.warning("Skipping DB Pool initialization.")

    user_workspace_dir = Path(DEFAULT_USER_DIR)
    user_workspace_dir.mkdir(parents=True, exist_ok=True) # Ensure base user dir exists

    # --- Agent Initialization ---
    agents: Dict[str, BaseAgent] = {}
    hermie_agent_instance: Optional[HermieAgent] = None
    try:
        # Instantiate Hermie V1 (placeholder)
        # Passing agents dict for future compatibility, but Hermie V1 doesn't use it.
        hermie_agent_instance = HermieAgent(agents=agents, user_dir=str(user_workspace_dir))
        agents["Hermie"] = hermie_agent_instance # Add to dict if needed later
        logger.info("Hermie V1 agent instantiated.")
    except Exception as e:
        logger.exception(f"Hermie initialization failed: {e}")
        if close_db_pool: await close_db_pool()
        return

    # --- Test Hermie V1 Directly --- #
    print("\n" + "="*10 + " Testing Hermie V1 Placeholder " + "="*10)
    if hermie_agent_instance:
        print(f"Calling Hermie V1 placeholder run...")
        try:
            hermie_result = await hermie_agent_instance.run(input_context="Direct Test Trigger D18")
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
        print("ERROR: Hermie agent could not be instantiated.")
    print("="*50)

    # --- Agent Shutdown --- #
    logger.info("\n--- Shutting Down Agents ---")
    if hermie_agent_instance: # Only shutdown instantiated agent
         if hasattr(hermie_agent_instance, 'shutdown'):
             logger.debug(f"Shutting down Hermie...")
             try: await hermie_agent_instance.shutdown()
             except Exception as shut_e: logger.error(f"Error shutting down Hermie: {shut_e}")

    if close_db_pool: # Only call if import succeeded
        await close_db_pool() # Close DB Pool
        logger.info("DB Pool closed.")
    else:
        logger.warning("Skipping DB Pool closure.")

    print("\n--- Day 18 Test Finished ---")


if __name__ == "__main__":
    # Ensure venv active.
    # Assumes Hermie RAG DB seed script ran successfully IF seeding was desired.
    asyncio.run(run_hermie_v1_test()) 