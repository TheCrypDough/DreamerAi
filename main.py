# C:\DreamerAI\main.py
# Main entry point for DreamerAI backend testing and eventual service start.
import asyncio
import os
import sys
from typing import Dict

# Ensure engine directory is in path
project_root_main = os.path.abspath(os.path.dirname(__file__))
if project_root_main not in sys.path:
    sys.path.insert(0, project_root_main)

# Import necessary components
try:
    from engine.agents.base import BaseAgent # Need BaseAgent for type hinting
    from engine.agents.main_chat import ChefJeff # Import Jeff
    from engine.agents.planning import PlanningAgent # <-- Import Arch
    # Import other agents as they are implemented...
    # from engine.agents.planning import Arch # Example for later
    from engine.core.workflow import DreamerFlow
    from engine.core.logger import logger_instance as logger
except ImportError as e:
    print(f"Error importing modules in main.py: {e}")
    print("Please ensure all core components (BaseAgent, ChefJeff, DreamerFlow, logger) are implemented.")
    sys.exit(1)

# Define user directory (can be made dynamic later)
# Use raw string for Windows paths
DEFAULT_USER_DIR = r"C:\DreamerAI\Users\Example User"

async def run_dreamer_flow():
    """
    Initializes agents and runs a test execution of the DreamerFlow.
    Includes calling PlanningAgent (Arch) after Jeff.
    """
    logger.info("--- Initializing DreamerAI Backend ---")
    # Define test project details
    test_user_name = "Example User" # Matches DEFAULT_USER_DIR
    test_project_name = "ArchTestProject"
    user_workspace_dir = DEFAULT_USER_DIR # C:\DreamerAI\Users\Example User
    test_project_context_path = os.path.join(user_workspace_dir, "Projects", test_project_name) # C:\...\Projects\ArchTestProject

    # Ensure directories exist for the test
    os.makedirs(test_project_context_path, exist_ok=True)
    logger.info(f"Ensured test project context path exists: {test_project_context_path}")

    # --- Agent Initialization ---
    agents: Dict[str, BaseAgent] = {}
    try:
        # Instantiate Jeff (Requires user_dir)
        agents["Jeff"] = ChefJeff(user_dir=user_workspace_dir)
        agents["Arch"] = PlanningAgent(user_dir=user_workspace_dir) # <-- Instantiate Arch
        logger.info("ChefJeff and PlanningAgent agents instantiated.")

        # Add other agents here as implemented...
        # e.g., agents["Arch"] = Arch(user_dir=DEFAULT_USER_DIR)
        # For Day 9, we only have Jeff implemented. Placeholders can be added later if needed for dict completeness.

    except NameError as ne:
         logger.error(f"Agent class not found during instantiation: {ne}. Has it been implemented?")
         print(f"ERROR: Required agent class not found: {ne}. Exiting.")
         sys.exit(1)
    except Exception as e:
        logger.exception(f"Failed to initialize agents: {e}")
        print(f"ERROR: Failed to initialize agents: {e}. Exiting.")
        sys.exit(1)


    # --- Workflow Initialization ---
    if not agents:
        logger.error("No agents were instantiated. Cannot start DreamerFlow.")
        print("ERROR: No agents available for DreamerFlow. Exiting.")
        sys.exit(1)

    try:
        dreamer_flow = DreamerFlow(agents=agents, user_dir=user_workspace_dir)
        logger.info("DreamerFlow instantiated.")
    except Exception as e:
        logger.exception(f"Failed to initialize DreamerFlow: {e}")
        print(f"ERROR: Failed to initialize DreamerFlow: {e}. Exiting.")
        sys.exit(1)


    # --- Test Execution ---
    test_input = f"Hi Jeff, let's plan a project called '{test_project_name}' about a personal blog."
    logger.info(f"\n--- Running Test Execution with Input: '{test_input}' ---")

    # 1. Initial interaction with Jeff (via Flow)
    # Note: Current DreamerFlow.execute only calls Jeff
    jeff_response = await dreamer_flow.execute(initial_user_input=test_input)

    print("\n--- Jeff's Initial Response --- (via Flow)")
    if isinstance(jeff_response, dict) and 'error' in jeff_response:
        print(f"Jeff ERROR: {jeff_response['error']}")
        # Decide if flow should stop on Jeff error - for now, continue to Arch
    else:
        print(f"Jeff Response Snippet: {str(jeff_response)[:200]}...")

    # 2. Pass the idea to Arch (using Jeff's response or original idea)
    # For this test, let's use the original idea concept derived from the input
    plan_idea = f"Create the '{test_project_name}' personal blog project mentioned in the chat."
    print(f"\n--- Calling Planning Agent (Arch) directly for: '{plan_idea}' ---")
    # Need a way to call Arch *through* the flow eventually,
    # for now, call directly using the instantiated agent object
    # We also need to provide the specific project context path
    if "Arch" in agents:
        arch_result = await agents['Arch'].run(
            project_idea=plan_idea,
            project_context_path=test_project_context_path
            )

        print("\n--- Arch's Planning Result ---")
        print(arch_result)
        if isinstance(arch_result, dict) and arch_result.get("status") == "success":
             print(f"==> Blueprint expected at: {arch_result.get('blueprint_path')}")
        elif isinstance(arch_result, dict):
             print(f"==> Planning failed or pending: {arch_result.get('message')}")
        else:
            print(f"==> Unexpected result from Arch: {arch_result}")
    else:
        print("\n--- Arch not found in agents dictionary. Skipping planning step. ---")


    logger.info("--- Test Execution Finished ---")
    print("--------------------------------")


if __name__ == "__main__":
    # Pre-requisites:
    # 1. Activate venv: C:\DreamerAI\venv\Scripts\activate
    # 2. Run Ollama server OR have Cloud API keys in .env.development
    # 3. RAG DB for Jeff seeded (from Day 8)
    # 4. Run main script: python main.py (from C:\DreamerAI)
    print(f"Running main.py from: {os.getcwd()}")
    asyncio.run(run_dreamer_flow()) 