# Main entry point for DreamerAI backend 

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
    from engine.ai.llm import LLM # Added import for LLM service needed by Jeff
    # Import other agents as they are implemented...
    # from engine.agents.planning import Arch # Example for later
    from engine.core.workflow import DreamerFlow
    from engine.core.logger import logger_instance as logger
except ImportError as e:
    print(f"Error importing modules in main.py: {e}")
    print("Please ensure all core components (BaseAgent, ChefJeff, LLM, DreamerFlow, logger) are implemented.")
    sys.exit(1)

# Define user directory (can be made dynamic later)
# Use raw string for Windows paths
DEFAULT_USER_DIR = r"C:\DreamerAI\Users\Example User"

async def run_dreamer_flow():
    """
    Initializes agents and runs a test execution of the DreamerFlow.
    """
    logger.info("--- Initializing DreamerAI Backend ---")
    os.makedirs(DEFAULT_USER_DIR, exist_ok=True) # Ensure user dir exists

    # --- Agent Initialization ---
    # Instantiate all agents needed for the workflow.
    # Start with Jeff, add others as they are built.
    agents: Dict[str, BaseAgent] = {}
    try:
        # Instantiate LLM Service first, as Jeff requires it
        try:
            llm_service = LLM()
            logger.info("LLM service initialized for main.py.")
        except Exception as llm_e:
            logger.exception(f"Failed to initialize LLM service: {llm_e}")
            print(f"ERROR: Cannot proceed without LLM service. Check engine/ai/llm.py and config. Exiting.")
            sys.exit(1)

        # Instantiate Jeff (Requires llm_instance and user_dir)
        agents["Jeff"] = ChefJeff(llm_instance=llm_service, user_dir=DEFAULT_USER_DIR)
        logger.info("ChefJeff agent instantiated.")

        # Add other agents here as implemented...
        # e.g., agents["Arch"] = Arch(user_dir=DEFAULT_USER_DIR)
        # For Day 9, we only have Jeff implemented.

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
        dreamer_flow = DreamerFlow(agents=agents, user_dir=DEFAULT_USER_DIR)
        logger.info("DreamerFlow instantiated.")
    except Exception as e:
        logger.exception(f"Failed to initialize DreamerFlow: {e}")
        print(f"ERROR: Failed to initialize DreamerFlow: {e}. Exiting.")
        sys.exit(1)


    # --- Test Execution ---
    # Example input to test the flow (primarily tests Jeff interaction for now)
    test_input = "Hi Jeff, let's plan a simple website."
    logger.info(f"\n--- Running Test Execution with Input: '{test_input}' ---")

    result = await dreamer_flow.execute(initial_user_input=test_input)

    logger.info("--- Test Execution Finished ---")
    print("\n--- Workflow Execution Result ---")
    if isinstance(result, dict) and 'error' in result:
        print(f"Execution finished with ERROR: {result['error']}")
    else:
        # Assuming result is a Message object from BaseAgent or similar
        # Safely access content attribute, fall back to string representation
        response_content = getattr(result, 'content', str(result))
        print(f"Final Output Snippet: {response_content[:200]}...")
    print("--------------------------------")


if __name__ == "__main__":
    # Pre-requisites:
    # 1. Activate venv: C:\DreamerAI\venv\Scripts\activate
    # 2. Run Ollama server OR have Cloud API keys in .env.development
    # 3. RAG DB for Jeff seeded (from Day 8)
    # 4. Run main script: python main.py (from C:\DreamerAI)
    print(f"Running main.py from: {os.getcwd()}")
    asyncio.run(run_dreamer_flow()) 