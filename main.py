# C:\\DreamerAI\\main.py (REVISED FOR DAY 19 - Hermie V1 Direct Test)
import asyncio
import os
import sys
from typing import Dict, Optional, List, Any
from pathlib import Path
import json
import traceback
import httpx # NEW Import for Day 25 Test

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
    from engine.core.workflow import DreamerFlow
    from engine.core.version_control import VersionControl # <-- Import VersionControl
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

    # --- NEW: Test Version Control V1 (Local Ops) ---
    print("\n--- Testing VersionControl V1 Local Ops ---")
    # Use a subfolder within the test project's context path for the VC repo
    # This ensures cleanup is tied to the project test
    # Define path using variables from above
    # Need to generate a unique name here or reuse one consistently
    # Using a fixed name for simplicity, ensure cleanup if rerunning manually
    test_project_name_vc = "FlowV2_LewisV1_VC_Test_D24" # Changed variable name to avoid conflict
    user_workspace_dir_vc = Path(DEFAULT_USER_DIR) # Use separate path object
    test_project_context_path = user_workspace_dir_vc / "Projects" / test_project_name_vc
    # Create the base project dir if it doesn't exist for the test
    test_project_context_path.mkdir(parents=True, exist_ok=True)

    vc_test_repo_path = test_project_context_path / "vc_test_repo" # Subdir for VC test
    # Ensure the specific repo subdir exists before VC init
    vc_test_repo_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"VC Test Repo Path: {vc_test_repo_path}")

    try:
        vc = VersionControl(str(vc_test_repo_path))
        # 1. Init
        if vc.initialize_repository():
            logger.info("VC Test: Init OK.")
            # 2. Create file & stage
            (vc_test_repo_path / "sample.txt").write_text("Hello GitPython from DreamerAI")
            if vc.stage_changes():
                logger.info("VC Test: Stage OK.")
                # 3. Commit
                if vc.commit_changes("Test commit via DreamerAI VC - Day 24"):
                    logger.info("VC Test: Commit OK.")
                    print("VC Test: Local Init, Stage, Commit SUCCESSFUL.")
                else: logger.error("VC Test: Commit FAILED.")
            else: logger.error("VC Test: Stage FAILED.")
        else: logger.error("VC Test: Init FAILED.")

        # 4. Test placeholders (optional, just confirms they run without error)
        await vc.push_to_remote() # Placeholder push

    except Exception as e:
        logger.exception("VC Test: Unexpected error during test.")
        print(f"ERROR during VC Test: {e}")

    print("-----------------------------------------")

    # --- NEW: Test GitHub Token Endpoint (Day 25) ---
    await test_github_token_endpoint()

    print("\n--- All Tests Finished ---")
    print("-----------------------------------------")
    logger.info("run_dreamer_flow_and_tests finished.") # Added final log

# --- NEW Test function for GitHub Endpoint ---
async def test_github_token_endpoint():
    """Tests the backend endpoint for receiving the GitHub token."""
    print("\n--- Testing GitHub Token Endpoint (/auth/github/token) ---")
    backend_url = "http://localhost:8090/auth/github/token" # CORRECTED PORT to 8090
    # Use a realistic looking prefix for a test token
    dummy_token = "gho_Test123DummyTokenForDreamerAIxyz"
    payload = {"token": dummy_token}

    try:
        # Use httpx.AsyncClient for making async requests
        async with httpx.AsyncClient() as client:
            logger.debug(f"POSTing dummy token to {backend_url}...")
            response = await client.post(backend_url, json=payload, timeout=10) # Increased timeout slightly

            if response.status_code == 200:
                logger.info(f"GitHub Token Endpoint Test SUCCESS: Status {response.status_code}, Response: {response.json()}")
                print(f"Token Endpoint Test: SUCCESS ({response.status_code}) - Backend received token.")
            else:
                # Log the detailed error from FastAPI if possible
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", response.text)
                except Exception:
                    pass # Keep raw text if not JSON
                logger.error(f"GitHub Token Endpoint Test FAILED: Status {response.status_code}, Detail: {error_detail}")
                print(f"Token Endpoint Test: FAILED ({response.status_code}) - Detail: {error_detail}. Check backend logs.")

    except httpx.ConnectError as exc:
         logger.error(f"HTTPX Connect Error during token endpoint test: {exc}")
         print(f"Token Endpoint Test: FAILED - Connection error: {exc}. Is backend server (python -m engine.core.server) running on port 8000?")
    except httpx.RequestError as exc:
        logger.error(f"HTTPX Request Error during token endpoint test: {exc}")
        print(f"Token Endpoint Test: FAILED - Request error: {exc}.")
    except Exception as e:
        logger.exception("Token Endpoint Test: Unexpected error during test.")
        print(f"Token Endpoint Test: FAILED - Unexpected error: {e}")

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