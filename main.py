# C:\DreamerAI\main.py
# Main entry point for DreamerAI backend testing and eventual service start.
import asyncio
import os
import sys
from typing import Dict
from pathlib import Path # <-- Import Path
import json # For printing dicts
import time # For unique test project name

# Ensure engine directory is in path
project_root_main = os.path.abspath(os.path.dirname(__file__))
if project_root_main not in sys.path:
    sys.path.insert(0, project_root_main)

# Import necessary components
try:
    from engine.agents.base import BaseAgent, AgentState, Message # Use V2 functional base
    # from engine.agents.promptimizer import PromptimizerAgent # Assume exists Day 7+
    # from engine.agents.main_chat import ChefJeff
    # from engine.agents.planning import PlanningAgent # Arch
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
except ImportError as e:
    print(f"FATAL Error importing modules in main.py: {e}")
    print("Ensure all required agent files and core modules exist and venv is active.")
    import traceback
    traceback.print_exc() # Print full traceback for import errors
    sys.exit(1)
except Exception as e:
     print(f"Unexpected FATAL Error during imports in main.py: {e}")
     import traceback
     traceback.print_exc()
     sys.exit(1)

# Define user directory (can be made dynamic later)
# Use raw string for Windows paths
DEFAULT_USER_DIR = r"C:\DreamerAI\Users\TestUserMain" # Use consistent test user dir

async def run_dreamer_flow_and_tests():
    # Setup paths using a main test project name
    user_workspace_dir = Path(DEFAULT_USER_DIR)
    # Use timestamp for unique project run
    timestamp = int(time.time())
    test_project_name = f"MainTestRun_NexusV1_{timestamp}"
    test_project_context_path = user_workspace_dir / "Projects" / test_project_name
    test_project_output_path = test_project_context_path / "output"
    # Ensure base project dir exists for context passed to agents V1
    test_project_context_path.mkdir(parents=True, exist_ok=True)
    test_project_output_path.mkdir(parents=True, exist_ok=True) # Nexus V1 needs this path even if not writing V1
    logger.info(f"Main Test Run Project Context Path: {test_project_context_path}")
    logger.info(f"Main Test Run Output Path: {test_project_output_path}")

    # --- Agent Initialization --- (Example Structure)
    agents: Dict[str, BaseAgent] = {}
    try:
        logger.info("Initializing agent placeholders...")
        # Instantiate ONLY Nexus for Day 15 V1 Test
        agents["Nexus"] = NexusAgent(user_dir=str(user_workspace_dir)) # Pass empty agents dict V1 is default
        logger.info("Nexus V1 placeholder instantiated.")

        # --- Commented out other agent instantiations ---
        # agents["Promptimizer"] = PromptimizerAgent(user_dir=str(user_workspace_dir))
        # agents["Jeff"] = ChefJeff(user_dir=str(user_workspace_dir))
        # agents["Arch"] = PlanningAgent(user_dir=str(user_workspace_dir))
        # agents["Lewis"] = LewisAgent(agents=agents, user_dir=...) # Example if needed
        # agents["Hermie"] = HermieAgent(agents=agents, user_dir=...) # Example if needed
        # ... etc ...

    except Exception as e:
        logger.exception(f"Agent initialization failed: {e}")
        return # Stop if agents can't init

    # --- Workflow Initialization (V1 Flow test deferred until D16) ---
    # dreamer_flow = DreamerFlow(agents=agents, user_dir=str(user_workspace_dir))

    # --- Test Nexus V1 Placeholder Directly --- (UPDATED for Day 15 V1)
    print("\n" + "="*10 + " Testing Nexus V1 Placeholder (Simulation Only) " + "="*10)
    nexus_agent = agents.get("Nexus")
    # Simulate blueprint content
    blueprint_for_nexus_v1 = "# Blueprint: Simple API\n Features: GET /status"

    if nexus_agent:
        print(f"Calling Nexus V1 placeholder run...")
        try:
            nexus_result = await nexus_agent.run(
                blueprint_content=blueprint_for_nexus_v1,
                # Provide the output path Nexus V1 run signature expects V1
                project_output_path=str(test_project_output_path)
                )
            print(f"Nexus V1 Result: {json.dumps(nexus_result, indent=2)}") # Pretty print result

            # Verification Steps - UPDATED for V1 Placeholder
            print("\nACTION REQUIRED (Verify Nexus V1 Simulation):")
            print(f"1. Check Nexus V1 Result above: 'status' should be 'success', message indicates simulation.")
            print(f"2. Check logs (dreamerai_dev.log) for 'V1 SIMULATION: Analyzing blueprint...' message.")
            print(f"3. Check logs for multiple 'V1 SIMULATION: ... Simulating delegation of Task...' messages.")
            print(f"4. Verify NO errors occurred during Nexus V1 run execution (check logs for exceptions/errors)." )
            print(f"5. Verify NO code files were generated in the output path by this run: {test_project_output_path}")
            # Assertion to check status programmatically
            assert nexus_result.get("status") == "success", "Nexus V1 run status was not success!"
            print(" -> Nexus V1 Simulation Test Verification Steps Passed (Manual Log Check Recommended)." )

        except Exception as nexus_e:
             print(f"ERROR running Nexus V1 test: {nexus_e}")
             logger.exception("Nexus V1 test block failed.")
    else:
        print("ERROR: Nexus agent not found.")
    print("="*40)


    # --- Keep Other Direct Agent Tests Commented Out --- 
    # ... (Jeff RAG test, etc.) ...

    # --- Agent Shutdown Loop ---
    print("\n--- Shutting Down Agents ---")
    for name, agent in agents.items():
        if hasattr(agent, 'shutdown'):
            print(f"Shutting down {name}...")
            try: await agent.shutdown()
            except Exception as shut_e: print(f"Error shutting down {name}: {shut_e}")
    print("Agent shutdown sequence complete.")


if __name__ == "__main__":
    # Ensure venv active, BaseAgent V2 applied, Nexus seed script run
    print(f"Running main.py test sequence from: {os.getcwd()}")
    asyncio.run(run_dreamer_flow_and_tests())
    print("Main test sequence finished.") 