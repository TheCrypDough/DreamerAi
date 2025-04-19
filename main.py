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
    from engine.core.workflow import DreamerFlow # <-- ADD THIS IMPORT
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

DEFAULT_USER_DIR = r"C:\DreamerAI\Users\Example User"

async def run_dreamer_flow_and_tests(): # Renamed function
    logger.info("--- Initializing DreamerAI Backend (Week 3 Review Test) ---")
    # Use a fresh project name for this full flow test
    test_project_name = f"Week3FlowTest_{int(asyncio.get_event_loop().time())}"
    user_workspace_dir = Path(DEFAULT_USER_DIR)
    # Directory creation should happen within agents/flow as needed, not duplicated here
    # Example: user_workspace_dir / "Projects" / test_project_name

    logger.info(f"Using Project Name: {test_project_name}")

    # --- Agent Initialization ---
    agents: Dict[str, BaseAgent] = {}
    try:
        # Instantiate all agents required by DreamerFlow V2 and Lewis test
        # BaseAgent V2 handles user_dir creation
        agents["Jeff"] = ChefJeff(user_dir=str(user_workspace_dir))
        agents["Arch"] = PlanningAgent(user_dir=str(user_workspace_dir))
        agents["Nexus"] = NexusAgent(user_dir=str(user_workspace_dir))
        agents["Lewis"] = LewisAgent(user_dir=str(user_workspace_dir))
        # Hermie is created but not called by flow.execute V2
        # Need to pass agents dict here if Hermie's init requires it (potential fix for prior error)
        agents["Hermie"] = HermieAgent(agents=agents, user_dir=str(user_workspace_dir))
        logger.info("Jeff, Arch, Nexus, Lewis, Hermie agents instantiated.")
    except Exception as e:
        logger.exception(f"Failed to initialize agents: {e}")
        print(f"ERROR: Failed to initialize agents: {e}. Exiting.")
        # Consider more graceful shutdown or error handling
        sys.exit(1) # Exit if core agents fail

    # --- Workflow Initialization ---
    try:
        dreamer_flow = DreamerFlow(agents=agents, user_dir=str(user_workspace_dir))
        logger.info("DreamerFlow instantiated.")
    except Exception as e:
        logger.exception(f"Failed to initialize DreamerFlow: {e}")
        print(f"ERROR: Failed to initialize DreamerFlow: {e}. Exiting.")
        sys.exit(1)

    # --- Execute Core Workflow (Jeff -> Arch -> Nexus) ---
    test_input = f"Plan and build V1 for project '{test_project_name}' - a simple Python CLI tool that counts words in a file."
    logger.info(f"\n--- Running DreamerFlow V2 Execute with Input: '{test_input}' ---")

    # Use the DreamerFlow V2 execute method from Day 16
    # Ensure DreamerFlow.execute handles project path creation internally now
    final_flow_result = await dreamer_flow.execute(
        initial_user_input=test_input,
        test_project_name=test_project_name # Pass project name for path generation
        )

    logger.info("--- DreamerFlow V2 Execution Finished (from main.py) ---")
    print("\n--- Final Workflow Result (from Nexus via Flow) ---")
    print(json.dumps(final_flow_result, indent=2))
    print("-----------------------------------------")
    print("\nACTION REQUIRED: Check corresponding project folders for blueprint and code files.")
    # Construct expected path for user verification
    expected_project_path = user_workspace_dir / 'Projects' / test_project_name
    print(f"Look in: {expected_project_path}")

    # --- Test Lewis V1 Directly (Keep this test) ---
    print("\n--- Testing Lewis V1 Info Retrieval ---")
    lewis_agent = agents.get("Lewis")
    if lewis_agent:
        try:
            tool_info = lewis_agent.get_tool_info("Ollama")
            print(f"Lewis info for 'Ollama': {tool_info}")
            frontend_tools = lewis_agent.list_tools_by_category("Frontend")
            print(f"Lewis 'Frontend' tools: {frontend_tools}")
        except Exception as lewis_e:
             logger.error(f"Error during Lewis V1 test: {lewis_e}")
             print(f"ERROR testing Lewis: {lewis_e}")
    else:
        print("ERROR: Lewis agent not found for testing.")
    print("-----------------------------------------")

    # --- Agent Shutdown (Optional but good practice) ---
    logger.info("\n--- Shutting Down Agents (Placeholder) ---")
    # Implement graceful shutdown if agents have resources to release
    # for agent_name, agent_instance in agents.items():
    #      if hasattr(agent_instance, 'shutdown'):
    #          logger.debug(f"Shutting down {agent_name}...")
    #          try: await agent_instance.shutdown()
    #          except Exception as shut_e: logger.error(f"Error shutting down {agent_name}: {shut_e}")

if __name__ == "__main__":
    # Ensure all prerequisites are met (venv, Ollama/Keys, DB seeds if needed, toolchest.json)
    logger.info("Starting Week 3 Integration Test...")
    try:
        asyncio.run(run_dreamer_flow_and_tests()) # Call the test function
        logger.info("Week 3 Integration Test Completed Successfully.")
    except Exception as main_e:
        logger.exception("Critical error during main execution.")
        print(f"CRITICAL ERROR: {main_e}")
        sys.exit(1)

    # The uvicorn server runs the app defined in server.py, not this main.py directly.
    # main.py is primarily for testing or utility scripts now.
    # We will run the server via: python engine/core/server.py
    logger.info("main.py executed. Note: Backend server should be started via 'python engine/core/server.py'") 