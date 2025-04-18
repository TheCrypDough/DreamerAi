# C:\\DreamerAI\\main.py (REVISED FOR DAY 19 - Hermie V1 Direct Test)
import asyncio
import os
import sys
from typing import Dict, Optional, List, Any
from pathlib import Path
import json
import traceback

# Add project root...
project_root_main = os.path.abspath(os.path.join(os.path.dirname(__file__), '.')) # Use . for root
if project_root_main not in sys.path: sys.path.insert(0, project_root_main)

# Import necessary components for this specific test
try:
    from engine.agents.base import BaseAgent
    from engine.agents.main_chat import ChefJeff
    from engine.agents.planning import PlanningAgent
    from engine.agents.coding_manager import NexusAgent
    from engine.agents.administrator import LewisAgent
    from engine.agents.communications import HermieAgent # <-- Import Hermie
    # Don't need Lamar/Dudley imports here if Nexus V1 instantiates them
    from engine.core.logger import logger_instance as logger
    # Import DB Pool functions if needed for BaseAgent V2
    # from engine.core.db import initialize_db_pool, close_db_pool
except ImportError as e:
    print(f"CRITICAL ERROR importing modules in main.py: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
     print(f"CRITICAL UNEXPECTED ERROR during imports in main.py: {e}")
     traceback.print_exc()
     sys.exit(1)

DEFAULT_USER_DIR = r"C:\DreamerAI\Users\TestUserMain_D19" # Re-introduce for clarity

async def run_dreamer_test(): # Rename function for clarity
    logger.info("--- Initializing DreamerAI Backend (for Hermie V1 Direct Routing Test) ---")
    # DB Pool Initialization (Optional - depends if BaseAgent V2 needs it)
    # if initialize_db_pool:
    #     await initialize_db_pool()

    # BaseAgent V2 handles user dir creation within its init
    user_workspace_dir = Path(DEFAULT_USER_DIR)
    user_workspace_dir.mkdir(parents=True, exist_ok=True) # Ensure base user dir exists

    # --- Agent Initialization --- #
    agents: Dict[str, BaseAgent] = {}
    try:
        # Instantiate all agents needed for Hermie's test context
        # Pass user_dir EXPLICITLY to all agents
        agents["Jeff"] = ChefJeff(user_dir=str(user_workspace_dir))
        agents["Arch"] = PlanningAgent(user_dir=str(user_workspace_dir))
        agents["Lewis"] = LewisAgent(user_dir=str(user_workspace_dir))
        agents["Nexus"] = NexusAgent(user_dir=str(user_workspace_dir))
        # Instantiate Hermie *passing the agents dictionary* AND user_dir
        agents["Hermie"] = HermieAgent(agents=agents, user_dir=str(user_workspace_dir))
        logger.info("Jeff, Arch, Lewis, Nexus, Hermie agents instantiated.")

    except Exception as e:
        logger.exception(f"Agent initialization failed: {e}")
        # if close_db_pool:
        #     await close_db_pool()
        return

    # --- Test Hermie V1 Directly --- #
    # Simulate the task description that Jeff's handoff would generate
    simulated_task_data = {
        "task_description": "User wants to plan a new project: 'SolarSystemVisualizer'",
        "source": "Jeff",
        "project_id": "placeholder_123" # Example extra context
    }
    logger.info(f"\n--- Directly Calling Hermie V1 Run with Task Data ---")

    hermie_agent = agents.get("Hermie")
    if hermie_agent:
        try:
            hermie_result = await hermie_agent.run(task_data=simulated_task_data)

            print("\n--- Hermie V1 Final Results ---")
            print(json.dumps(hermie_result, indent=2))
            print("\nACTION REQUIRED: Check logs to verify Arch and Lewis logged task receipt.")

            # Basic Verification based on Hermie's V1 run logic
            if hermie_result.get("status") == "success":
                print("\n -> Hermie V1 Routing Test PASSED (Reported Success).")
            elif hermie_result.get("status") == "partial_success":
                print("\n -> Hermie V1 Routing Test PARTIALLY PASSED (Reported Partial Success - Check errors).")
                print(f"   Errors: {hermie_result.get('errors')}")
            else:
                print("\n -> Hermie V1 Routing Test FAILED (Reported Failure - Check errors).")
                print(f"   Errors: {hermie_result.get('errors')}")

        except Exception as hermie_e:
             print(f"ERROR running Hermie V1 test: {hermie_e}")
             logger.exception("Hermie V1 direct run test block failed.")
    else:
        print("ERROR: Hermie agent not found in dictionary!")

    # --- Agent Shutdown --- #
    logger.info("\n--- Shutting Down Agents ---")
    for agent_name, agent_instance in agents.items():
         if hasattr(agent_instance, 'shutdown'):
             logger.debug(f"Shutting down {agent_name}...")
             try: await agent_instance.shutdown()
             except Exception as shut_e: logger.error(f"Error shutting down {agent_name}: {shut_e}")

    # DB Pool Closure (Optional)
    # if close_db_pool:
    #     await close_db_pool()
    #     logger.info("DB Pool closed.")

    logger.info("--- Hermie V1 Direct Routing Test Execution Finished ---")
    print("-"*40)


if __name__ == "__main__":
    # Ensure Rules files exist for Arch, Lewis, Hermie (BaseAgent should handle this)
    # Ensure venv active.
    asyncio.run(run_dreamer_test()) # Call the renamed test function 