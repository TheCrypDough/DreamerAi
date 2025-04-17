# C:\DreamerAI\main.py
# Main entry point for DreamerAI backend testing and eventual service start.
import asyncio
import os
import sys
from typing import Dict
from pathlib import Path # <-- Import Path

# Ensure engine directory is in path
project_root_main = os.path.abspath(os.path.dirname(__file__))
if project_root_main not in sys.path:
    sys.path.insert(0, project_root_main)

# Import necessary components
try:
    from engine.agents.base import BaseAgent # Need BaseAgent for type hinting
    from engine.agents.main_chat import ChefJeff # Import Jeff
    from engine.agents.planning import PlanningAgent # <-- Import Arch
    from engine.agents.frontend_agent import LamarAgent # <-- Import Lamar
    from engine.agents.backend_agent import DudleyAgent # <-- Import Dudley
    # Import other agents as they are implemented...
    # from engine.agents.planning import Arch # Example for later
    from engine.core.workflow import DreamerFlow
    from engine.core.logger import logger_instance as logger
except ImportError as e:
    print(f"Error importing modules in main.py: {e}")
    print("Check file paths and ensure all agent files exist.") # Updated error message
    sys.exit(1)

# Define user directory (can be made dynamic later)
# Use raw string for Windows paths
DEFAULT_USER_DIR = r"C:\DreamerAI\Users\Example User"

async def run_dreamer_flow():
    """
    Initializes agents and runs a test execution of the DreamerFlow.
    Includes Arch -> Lamar & Dudley steps.
    """
    logger.info("--- Initializing DreamerAI Backend ---")
    # Define test project details
    test_user_name = "Example User" # Matches DEFAULT_USER_DIR
    test_project_name = "CodeGenProjectDay12"
    user_workspace_dir = Path(DEFAULT_USER_DIR) # Use Path object
    test_project_context_path = user_workspace_dir / "Projects" / test_project_name
    # Define output path within project context path
    test_project_output_path = test_project_context_path / "output"
    test_project_overview_path = test_project_context_path / "Overview" # Path for blueprint

    # Ensure directories exist for the test using pathlib
    test_project_context_path.mkdir(parents=True, exist_ok=True)
    test_project_output_path.mkdir(parents=True, exist_ok=True)
    # Arch's run method should create Overview if needed
    logger.info(f"Ensured base test project path exists: {test_project_context_path}")
    logger.info(f"Output path set to: {test_project_output_path}")

    # --- Agent Initialization ---
    agents: Dict[str, BaseAgent] = {}
    try:
        # Instantiate Jeff (Requires user_dir)
        agents["Jeff"] = ChefJeff(user_dir=str(user_workspace_dir))
        agents["Arch"] = PlanningAgent(user_dir=str(user_workspace_dir))
        agents["Lamar"] = LamarAgent(user_dir=str(user_workspace_dir))   # <-- Instantiate Lamar
        agents["Dudley"] = DudleyAgent(user_dir=str(user_workspace_dir)) # <-- Instantiate Dudley
        logger.info("Jeff, Arch, Lamar, Dudley agents instantiated.")

        # Add other agents here as implemented...
        # e.g., agents["Arch"] = Arch(user_dir=DEFAULT_USER_DIR)
        # For Day 9, we only have Jeff implemented. Placeholders can be added later if needed for dict completeness.

    except NameError as ne:
         logger.error(f"Agent class not found during instantiation: {ne}. Check imports.")
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
        dreamer_flow = DreamerFlow(agents=agents, user_dir=str(user_workspace_dir))
        logger.info("DreamerFlow instantiated.")
    except Exception as e:
        logger.exception(f"Failed to initialize DreamerFlow: {e}")
        print(f"ERROR: Failed to initialize DreamerFlow: {e}. Exiting.")
        sys.exit(1)


    # --- Test Execution ---
    logger.info(f"\n--- Running Day 13 Test Execution (Includes Bridge Test) ---") # Updated log

    # **NEW: Call Jeff to test the bridge**
    jeff_input = "Hello Jeff! Just testing the connection."
    print(f"\n--- Calling Jeff with: '{jeff_input}' (Bridge Test) ---")
    try:
        jeff_result = await agents['Jeff'].run(user_input=jeff_input)
        print(f"Jeff Result: {jeff_result}")
        # Check logs and frontend console for the bridged message
    except Exception as e:
        logger.error(f"Error running Jeff for bridge test: {e}")
        print(f"ERROR running Jeff: {e}")

    # 1. Call Arch to generate blueprint
    plan_idea = "Basic web application with a counter. Frontend using React shows a number and increment/decrement buttons. Minimal FastAPI backend (placeholder for now)."
    print(f"\n--- Calling Arch for: '{plan_idea}' ---")
    arch_result = await agents['Arch'].run(
        project_idea=plan_idea,
        project_context_path=str(test_project_context_path) # Pass base project path
        )
    print(f"Arch Result: {arch_result}")

    blueprint_path_str = arch_result.get("blueprint_path")
    blueprint_content = None
    if arch_result.get("status") == "success" and blueprint_path_str:
        blueprint_path = Path(blueprint_path_str) # Convert to Path
        if blueprint_path.exists():
            print(f"Blueprint generated at: {blueprint_path}")
            try:
                with open(blueprint_path, "r", encoding="utf-8") as f:
                    blueprint_content = f.read()
                logger.info(f"Successfully read blueprint: {blueprint_path}")
            except Exception as e:
                logger.error(f"Failed to read blueprint file {blueprint_path}: {e}")
                print(f"ERROR: Could not read blueprint file.")
        else:
             print(f"ERROR: Arch reported success but blueprint file not found at {blueprint_path}.")
             logger.error(f"Blueprint file missing: {blueprint_path}")
    else:
         print(f"ERROR: Planning failed or blueprint path missing. Cannot run coding agents.")
         logger.error(f"Planning failed: {arch_result.get('message')}")

    # 2. Call Lamar & Dudley if blueprint exists
    if blueprint_content:
        print(f"\n--- Calling Dudley (Backend) with Blueprint ---")
        dudley_result = await agents['Dudley'].run(
            blueprint_content=blueprint_content,
            project_output_path=str(test_project_output_path) # Pass output sub-path
            )
        print(f"Dudley Result: {dudley_result}")
        if dudley_result.get("status") == "success":
             print(f"==> Backend code saved to: {dudley_result.get('file_path')}")
        else:
             print(f"==> Dudley failed: {dudley_result.get('message')}")

        print(f"\n--- Calling Lamar (Frontend) with Blueprint ---")
        lamar_result = await agents['Lamar'].run(
             blueprint_content=blueprint_content,
             project_output_path=str(test_project_output_path)
             )
        print(f"Lamar Result: {lamar_result}")
        if lamar_result.get("status") == "success":
             print(f"==> Frontend code saved to: {lamar_result.get('file_path')}")
        else:
             print(f"==> Lamar failed: {lamar_result.get('message')}")
    else:
        print("Skipping coding agents due to missing blueprint.")


    logger.info("--- Test Execution Finished ---")
    print("--------------------------------")


if __name__ == "__main__":
    # Pre-requisites:
    # 1. Activate venv: C:\DreamerAI\venv\Scripts\activate
    # 2. Run Ollama server OR have Cloud API keys in .env.development
    # 3. RAG DB for Jeff seeded (from Day 8) - Not directly used in this test
    # 4. Run main script: python main.py (from C:\DreamerAI)
    print(f"Running main.py from: {os.getcwd()}")
    asyncio.run(run_dreamer_flow()) 