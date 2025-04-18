# C:\DreamerAI\main.py
# Main entry point for DreamerAI backend testing and eventual service start.
import asyncio
import os
import sys
from typing import Dict, Optional, List, Any
from pathlib import Path
import json # For printing dicts
import time # For unique test project name
import traceback # Added for better error reporting

# Ensure engine directory is in path
project_root_main = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_main not in sys.path:
    sys.path.insert(0, project_root_main)

# Import necessary components
try:
    from engine.agents.base import BaseAgent # Need BaseAgent for type hinting
    # from engine.agents.promptimizer import PromptimizerAgent # Assume exists Day 7+
    from engine.agents.main_chat import ChefJeff
    from engine.agents.planning import PlanningAgent # Arch V1/V2
    # from engine.agents.frontend_agent import LamarAgent # <-- Import Lamar
    # from engine.agents.backend_agent import DudleyAgent # <-- Import Dudley
    # Import other agents as they are implemented...
    # from engine.agents.planning import Arch # Example for later
    from engine.agents.coding_manager import NexusAgent # V1 Placeholder
    # from engine.agents.agent_utils import save_code_to_file
    # from engine.agents.administrator import LewisAgent # V1 Placeholder D17+
    # from engine.agents.communications import HermieAgent # V1 Placeholder D19+
    # Placeholders for others if needed by tests/structure
    # from engine.agents.suggestions import SophiaAgent
    # from engine.agents.education import SparkAgent
    # ... Specialists, QA, Docs, Deploy ...
    # from engine.agents.research import RiddickAgent
    # from engine.agents.security import ShadeAgent
    # from engine.agents.ui_generator import ZiggyAgent
    # from engine.agents.optimization import OgreAgent
    # from engine.agents.plugin_manager import BillyAgent
    # from engine.agents.review_manager import ArtemisAgent

    # from engine.core.workflow import DreamerFlow # Keep if testing flow later
    from engine.core.logger import logger_instance as logger
    from engine.core.workflow import DreamerFlow # <--- Uncomment this line
except ImportError as e:
    print(f"CRITICAL ERROR importing modules in main.py: {e}")
    print("Ensure all agent files and core modules exist and venv is active.")
    traceback.print_exc() # Print full traceback for import errors
    sys.exit(1)
except Exception as e:
     print(f"CRITICAL UNEXPECTED ERROR during imports in main.py: {e}")
     traceback.print_exc()
     sys.exit(1)

# Define user directory (can be made dynamic later)
# Use raw string for Windows paths
DEFAULT_USER_DIR = r"C:\DreamerAI\Users\TestUserMain" # Use consistent test user dir

async def run_dreamer_flow_and_tests():
    logger.info("--- Initializing DreamerAI Backend (DreamerFlow V2 Test) ---")
    # Initialize dependencies like DB pool first (if using Day 100+ structure)
    # await initialize_db_pool() # Keep commented out for Day 16

    # Define paths using a unique name for this flow test run
    test_project_name_flow = f"FlowV2Test_D16_{int(time.time())}"
    user_workspace_dir = Path(DEFAULT_USER_DIR)
    # Base project path - Flow's execute method handles creating subdirs now
    test_project_context_path = user_workspace_dir / "Projects" / test_project_name_flow
    test_project_context_path.parent.mkdir(parents=True, exist_ok=True) # Ensure Projects dir exists

    # --- Agent Initialization ---
    agents: Dict[str, BaseAgent] = {}
    dreamer_flow: Optional[DreamerFlow] = None
    try:
        # Instantiate agents needed for Flow V2 (Jeff, Arch, Nexus)
        logger.info("Instantiating required agents for Flow V2 test...")
        agents["Jeff"] = ChefJeff(user_dir=str(user_workspace_dir))
        agents["Arch"] = PlanningAgent(user_dir=str(user_workspace_dir))
        agents["Nexus"] = NexusAgent(user_dir=str(user_workspace_dir)) # V1 Placeholder

        # Instantiate others if keeping their direct tests (commented out V16)
        # logger.info("Instantiating other placeholder agents...")
        # agents["Lewis"] = LewisAgent(agents=agents, user_dir=...) # Lewis needs agent dict now D52+
        # ... instantiate placeholders for Lewis, Sophia, Spark etc. ...

        logger.info("Agents for Flow V2 (Jeff, Arch, Nexus V1 Sim) instantiated.")

        # --- Workflow Initialization ---
        # Pass only agents needed by V2 flow for this test
        flow_agents_v2 = {name: agent for name, agent in agents.items() if name in ["Jeff", "Arch", "Nexus"]}
        dreamer_flow = DreamerFlow(agents=flow_agents_v2, user_dir=str(user_workspace_dir))
        logger.info("DreamerFlow V2 instantiated.")

    except Exception as e:
        logger.exception(f"Agent or Flow initialization failed: {e}")
        # await close_db_pool() # Keep commented out for Day 16
        return # Stop if core components fail to init


    # --- Execute Core Workflow (Jeff V1 -> Arch V1 -> Nexus V1 Sim) ---
    test_input = f"Plan project '{test_project_name_flow}': Basic command-line timer app."
    logger.info(f"\n--- Running DreamerFlow V2 Execute with Input: '{test_input}' ---")

    final_flow_result: Any = {"status": "error", "error": "Flow did not execute"}
    try:
        final_flow_result = await dreamer_flow.execute(
            initial_user_input=test_input,
            test_project_name=test_project_name_flow # Pass name for consistent path generation
            )
    except Exception as flow_exec_e:
         logger.exception(f"DreamerFlow execute encountered an unhandled exception: {flow_exec_e}")
         final_flow_result = {"status": "error", "error": str(flow_exec_e), "stage": "Flow Execute"}


    logger.info("--- DreamerFlow V2 Execution Finished (from main.py) ---")
    print("\n--- Final Workflow Result (Nexus V1 Placeholder Output) ---")
    try:
        print(json.dumps(final_flow_result, indent=2))
    except TypeError as json_e:
         print(f"Could not serialize result to JSON: {json_e}\nRaw result: {final_flow_result}")
    print("-------------------------------------------------------")

    # --- Verification Steps (Updated for Day 16 Flow) ---
    print("\nACTION REQUIRED (Verify Flow V2 Execution):")
    print("1. Check logs verify Jeff V1 run completed.")
    print("2. Check logs verify Arch V1 run completed and blueprint path logged.")
    # Construct expected path for verification message
    expected_blueprint_path = test_project_context_path / 'Overview' / 'blueprint.md'
    print(f"3. Check file system for blueprint: {expected_blueprint_path}")
    print("4. Check logs verify Nexus V1 simulation ran AFTER Arch.")
    # Check the actual result dictionary status
    is_success = isinstance(final_flow_result, dict) and final_flow_result.get("status") == "success"
    success_msg = "SUCCESS" if is_success else "FAILURE (or unexpected format)"
    print(f"5. Verify final printed result above shows Nexus V1 success: {success_msg}")
    print("6. Verify NO functional code generation occurred (No files in output/ dir from this run).")


    # --- Keep Existing Direct Agent Tests (Optional Run - Commented Out for Day 16) ---
    # logger.info(f"\n--- Running Other Direct Agent Tests ---")
    # await test_lewis_v5(...)
    # await test_sophia_v2(...)
    # ... etc ...


    # --- Agent Shutdown ---
    logger.info("\n--- Shutting Down Agents ---")
    for name, agent in agents.items(): # Shutdown ALL instantiated agents
        # Use hasattr for safety, good practice
        if hasattr(agent, 'shutdown') and callable(agent.shutdown):
            logger.debug(f"Shutting down {name}...")
            try:
                # Ensure shutdown is awaited if it's async
                shutdown_method = agent.shutdown()
                if asyncio.iscoroutine(shutdown_method):
                    await shutdown_method
            except Exception as shut_e:
                 logger.error(f"Error shutting down {name}: {shut_e}", exc_info=True)
        else:
            logger.warning(f"Agent {name} does not have a callable shutdown method.")

    # Close DB Pool if it was initialized
    # await close_db_pool() # Keep commented out for Day 16
    # logger.info("DB Pool closed.")
    logger.info("--- Main Test Sequence Finished ---")


if __name__ == "__main__":
    # Ensure venv active
    # Ensure relevant RAG DBs seeded if agents use them on init/run
    # (Jeff/Arch/Nexus V1 placeholders don't heavily rely on RAG for this test)
    print(f"Executing main.py for DreamerFlow V2 Test from: {os.getcwd()}")
    try:
        asyncio.run(run_dreamer_flow_and_tests())
    except Exception as main_run_e:
         print(f"FATAL ERROR running main asyncio loop: {main_run_e}")
         traceback.print_exc() 