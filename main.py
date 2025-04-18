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
# Corrected path joining for reliability
project_root_main = os.path.dirname(os.path.abspath(__file__))
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
    from engine.agents.administrator import LewisAgent # V1 Placeholder D17+ <-- Import Lewis
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
    from engine.core.workflow import DreamerFlow
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
    logger.info("--- Initializing DreamerAI Backend (DreamerFlow V2 + Lewis V1 Test) ---") # Updated Title
    # Initialize dependencies like DB pool first (if using Day 100+ structure)
    # await initialize_db_pool() # Keep commented out for Day 17

    # Define paths using a unique name for this flow test run
    test_project_name_flow = f"FlowV2_LewisV1_Test_D17_{int(time.time())}" # Updated Test Name
    user_workspace_dir = Path(DEFAULT_USER_DIR)
    # Base project path - Flow's execute method handles creating subdirs now
    test_project_context_path = user_workspace_dir / "Projects" / test_project_name_flow
    test_project_context_path.parent.mkdir(parents=True, exist_ok=True) # Ensure Projects dir exists

    # --- Agent Initialization ---
    agents: Dict[str, BaseAgent] = {}
    dreamer_flow: Optional[DreamerFlow] = None
    try:
        # Instantiate agents needed for Flow V2 (Jeff, Arch, Nexus) AND Lewis V1
        logger.info("Instantiating required agents (Jeff, Arch, Nexus, Lewis)...")
        agents["Jeff"] = ChefJeff(user_dir=str(user_workspace_dir))
        agents["Arch"] = PlanningAgent(user_dir=str(user_workspace_dir))
        agents["Nexus"] = NexusAgent(user_dir=str(user_workspace_dir)) # V1 Placeholder
        agents["Lewis"] = LewisAgent(user_dir=DEFAULT_USER_DIR) # <-- Instantiate Lewis V1, passing user_dir

        # Instantiate others if needed later
        # ...

        logger.info("Agents for Flow V2 (Jeff, Arch, Nexus V1 Sim) and Lewis V1 instantiated.")

        # --- Workflow Initialization ---
        # Pass only agents needed by V2 flow for this test
        flow_agents_v2 = {name: agent for name, agent in agents.items() if name in ["Jeff", "Arch", "Nexus"]}
        dreamer_flow = DreamerFlow(agents=flow_agents_v2, user_dir=str(user_workspace_dir))
        logger.info("DreamerFlow V2 instantiated.")

    except Exception as e:
        logger.exception(f"Agent or Flow initialization failed: {e}")
        # await close_db_pool() # Keep commented out
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

    # --- Verification Steps (Flow V2) ---
    print("\nACTION REQUIRED (Verify Flow V2 Execution):")
    print("1. Check logs verify Jeff V1 run completed.")
    print("2. Check logs verify Arch V1 run completed and blueprint path logged.")
    expected_blueprint_path = test_project_context_path / 'Overview' / 'blueprint.md'
    print(f"3. Check file system for blueprint: {expected_blueprint_path}")
    print("4. Check logs verify Nexus V1 simulation ran AFTER Arch.")
    is_success = isinstance(final_flow_result, dict) and final_flow_result.get("status") == "success"
    success_msg = "SUCCESS" if is_success else "FAILURE (or unexpected format)"
    print(f"5. Verify final printed result above shows Nexus V1 success: {success_msg}")
    print("6. Verify NO functional code generation occurred (No files in output/ dir from Flow V2 run).")


    # --- NEW: Lewis V1 Direct Agent Tests ---
    logger.info("\n--- Running Lewis V1 Direct Agent Tests ---")
    if "Lewis" in agents:
        try:
            lewis_agent = agents["Lewis"]
            # Ensure toolchest.json exists (create dummy if not)
            toolchest_dir = os.path.join(project_root_main, "tools")
            toolchest_path = os.path.join(toolchest_dir, "toolchest.json")
            if not os.path.exists(toolchest_path):
                os.makedirs(toolchest_dir, exist_ok=True)
                dummy_toolchest = {
                    "tools": [{"name": "DummyTool", "category": "Testing", "description": "A placeholder."}],
                    "protocols": []
                }
                with open(toolchest_path, "w") as f:
                    json.dump(dummy_toolchest, f, indent=2)
                logger.warning(f"Created dummy toolchest at {toolchest_path}")

            logger.info("Testing Lewis: List all tools by category...")
            # Corrected: Pass a valid category name
            category_tools = lewis_agent.list_tools_by_category("AI")
            logger.info(f"Tools in category 'AI': {json.dumps(category_tools, indent=2)}")

            logger.info("Testing Lewis: Get info for specific tool 'MCP_Github_create_or_update_file'...")
            # Note: MCP_Github_create_or_update_file is NOT currently in toolchest.json, expect None
            # tool_info = lewis_agent.get_tool_info("MCP_Github_create_or_update_file")
            # Instead, let's test with a tool that *is* in the toolchest, like "Ollama"
            tool_name_test = "Ollama"
            logger.info(f"Testing Lewis: Get info for specific tool '{tool_name_test}'...")
            tool_info = lewis_agent.get_tool_info(tool_name_test)
            if tool_info:
                logger.info(f"Info for tool '{tool_name_test}': {json.dumps(tool_info, indent=2)}")
            else:
                logger.warning(f"Tool '{tool_name_test}' not found in Lewis's toolchest.")

            logger.info("Testing Lewis: Get info for non-existent tool...")
            non_existent_tool_info = lewis_agent.get_tool_info("NonExistentTool")
            logger.info(f"Lewis get_tool_info('NonExistentTool') result: {non_existent_tool_info}")

        except Exception as e:
            logger.error(f"Error during Lewis V1 direct tests: {e}", exc_info=True)
    else:
        logger.warning("Lewis agent not found in agents dictionary, skipping tests.")
    logger.info("--- Lewis V1 Direct Agent Tests Finished ---")

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
    # await close_db_pool() # Keep commented out
    # logger.info("DB Pool closed.")
    logger.info("--- Main Test Sequence Finished ---")


if __name__ == "__main__":
    # Ensure venv active
    # Ensure relevant RAG DBs seeded if agents use them on init/run
    # Ensure tools/toolchest.json exists for Lewis V1 test
    print(f"Executing main.py for DreamerFlow V2 + Lewis V1 Test from: {os.getcwd()}")
    try:
        asyncio.run(run_dreamer_flow_and_tests())
    except Exception as main_run_e:
         print(f"FATAL ERROR running main asyncio loop: {main_run_e}")
         traceback.print_exc() 