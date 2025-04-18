# C:\DreamerAI\engine\agents\planning.py
# Placeholder for Arch (Planning) Agent
# Implementation details to follow.

import asyncio
import os
import json
import traceback
from typing import Optional, Any, Dict, List
from pathlib import Path

# Add project root for sibling imports
import sys
project_root_arch = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_arch not in sys.path:
    sys.path.insert(0, project_root_arch)

try:
    from engine.agents.base import BaseAgent, AgentState, Message
    from engine.ai.llm import LLM
    from engine.core.logger import logger_instance as logger, log_rules_check
except ImportError as e:
    print(f"ERROR importing in planning.py: {e}")
    # Dummy fallbacks (copy from another agent if needed)
    class BaseAgent: # Dummy BaseAgent
        def __init__(self, name, user_dir, **kwargs): self.name=name; self.user_dir=user_dir; self._state='idle'; self.logger=print
        async def query_rag(self, *args, **kwargs): return []
        async def store_in_rag(self, *args, **kwargs): return False
        async def run(self, *args, **kwargs): return {}
        async def step(self, *args, **kwargs): return {}
        async def shutdown(self): pass
        def _load_rules(self): self.rules_content=None
        @property
        def state(self): return self._state
        @state.setter
        def state(self, value): self._state = value
    class AgentState: IDLE='idle'; RUNNING='running'; FINISHED='finished'
    class Message: pass
    # Use a basic print logger for fallback
    class FallbackLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
        def exception(self, msg): print(f"EXCEPTION: {msg}"); traceback.print_exc()
        def bind(self, **kwargs): return self # Allow bind chaining
    logger = FallbackLogger()
    def log_rules_check(a): logger.debug(f"Fallback Rules Check: {a}")


ARCH_AGENT_NAME = "Arch"

class PlanningAgent(BaseAgent):
    """
    Arch Agent V1: Planner.
    Receives input from Jeff, generates a blueprint.md file.
    Inherits functional BaseAgent V2.
    """
    def __init__(self, user_dir: str, **kwargs):
        super().__init__(name=ARCH_AGENT_NAME, user_dir=user_dir, **kwargs)
        self.logger.info(f"{self.name} V1 Initialized (Inherits BaseAgent V2).")
        # V1: No specific Arch state needed yet

    async def step(self, input_data: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """
        V1: Simulates planning based on input (likely from Jeff).
        Generates a basic blueprint.md in the designated project path.
        Relies on the 'project_name' being passed in input_data or context.
        """
        self.state = AgentState.RUNNING
        log_rules_check(f"{self.name} V1 step triggered.")
        self.logger.debug(f"Arch V1 received input: {input_data}")

        # --- Input Validation & Path Setup --- #
        if not isinstance(input_data, dict):
            self.logger.error("Invalid input_data format: expected dict.")
            self.state = AgentState.FINISHED # Mark as finished on error
            return {"status": "error", "error": "Invalid input format. Expected dict.", "agent": self.name}

        user_request = input_data.get("user_request", "No user request provided.")
        project_name = input_data.get("project_name")

        if not project_name:
            self.logger.error("Missing 'project_name' in input_data for Arch.")
            self.state = AgentState.FINISHED
            return {"status": "error", "error": "Missing 'project_name' in input data.", "agent": self.name}

        # --- Determine Output Path (Corrected using BaseAgent V2 properties) ---
        # self._agent_base_dir is the agent's base dir (e.g., Users/TestUser/Agents/Arch)
        # We need the project's path, derived from user_dir and project_name
        # self.user_dir is the base user dir (e.g., Users/TestUser)
        try:
            project_base_path = Path(self.user_dir) / "Projects" / project_name
            # V1: Define a subfolder for Arch's main output (blueprint)
            overview_dir = project_base_path / "Overview"
            overview_dir.mkdir(parents=True, exist_ok=True)
            blueprint_path = overview_dir / "blueprint.md"
            self.logger.info(f"Target blueprint path: {blueprint_path}")
        except Exception as path_e:
             self.logger.error(f"Error creating project path structure: {path_e}", exc_info=True)
             self.state = AgentState.FINISHED
             return {"status": "error", "error": f"Failed to create project directory structure: {path_e}", "agent": self.name}

        # --- RAG Query (Optional for V1, example placeholder) --- #
        # In V2+, query RAG for relevant architectural patterns based on user_request
        rag_results = []
        try:
            # Example: query for 'basic web app structure' if relevant
            # rag_results = await self.query_rag(f"architectural patterns for {user_request}", k=1)
            self.logger.info("Skipping RAG query for Arch V1.") # V1 doesn't use RAG yet
        except Exception as rag_e:
            self.logger.warning(f"RAG query failed (non-critical for V1): {rag_e}")

        # --- LLM Call (Simulated for V1 Placeholder) --- #
        # In a real V1/V2, you'd call the LLM to generate the blueprint content
        # based on user_request and RAG results.
        blueprint_content = f"""
# Blueprint for Project: {project_name}

## Request:
{user_request}

## V1 Placeholder Plan:

This is a placeholder blueprint generated by Arch V1.

*   **Core Component:** Main Application Logic (details TBD)
*   **Interface:** Command Line Interface (CLI)
*   **Technology:** Python

*(Full LLM generation planned for V2)*
"""
        self.logger.info("Generated V1 placeholder blueprint content.")

        # --- Save Blueprint --- #
        try:
            with open(blueprint_path, 'w', encoding='utf-8') as f:
                f.write(blueprint_content)
            self.logger.info(f"Successfully wrote V1 blueprint to {blueprint_path}")
            self.state = AgentState.FINISHED
            return {
                "status": "success",
                "message": f"Arch V1 completed. Blueprint generated.",
                "blueprint_path": str(blueprint_path), # Return path for next step
                "agent": self.name
            }
        except IOError as io_e:
            self.logger.error(f"Failed to write blueprint file: {io_e}", exc_info=True)
            self.state = AgentState.FINISHED
            return {"status": "error", "error": f"Failed to write blueprint file: {io_e}", "agent": self.name}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Arch step: {e}", exc_info=True)
            self.state = AgentState.FINISHED
            return {"status": "error", "error": f"Unexpected error: {e}", "agent": self.name}

# Inherited run/shutdown methods from BaseAgent V2 are sufficient for V1

# Example Usage (for testing purposes, typically called from orchestration like DreamerFlow)
if __name__ == '__main__':
    print("--- Testing Arch Agent V1 --- (Requires BaseAgent V2 functional)")
    # Use a consistent user dir for testing
    test_user_dir = "C:\\DreamerAI\\Users\\TestUserArchV1"
    test_project_name = f"ArchV1_TestProject_{int(time.time())}"
    Path(test_user_dir).mkdir(parents=True, exist_ok=True)

    async def test_arch():
        print(f"\nInstantiating Arch V1 for user: {test_user_dir}...")
        try:
            arch = PlanningAgent(user_dir=test_user_dir)
            print("ArchAgent instantiated successfully.")
        except Exception as e:
            print(f"ERROR: Failed to instantiate ArchAgent: {e}")
            traceback.print_exc()
            return

        test_input = {
            "user_request": "Create a simple Python script that counts down from 10.",
            "project_name": test_project_name
        }
        print(f"\nRunning Arch V1 step with input:\n{json.dumps(test_input, indent=2)}")

        # Use the step method directly for isolated testing
        result = await arch.step(test_input)
        print(f"\nArch V1 step finished. Result:\n{json.dumps(result, indent=2)}")

        # Verification
        if isinstance(result, dict) and result.get("status") == "success":
            bp_path = result.get("blueprint_path")
            if bp_path and Path(bp_path).is_file():
                print(f"\nSUCCESS: Blueprint found at {bp_path}")
                try:
                    with open(bp_path, 'r', encoding='utf-8') as f:
                        print("--- Blueprint Content ---:")
                        print(f.read())
                        print("-------------------------")
                except Exception as read_e:
                    print(f"Error reading blueprint: {read_e}")
            else:
                print(f"\nERROR: Blueprint path missing or file not found: {bp_path}")
        else:
            print("\nERROR: Arch V1 step did not return success status.")

        print("\nShutting down Arch V1...")
        await arch.shutdown()
        print("--- Arch Agent V1 Test Complete ---")

    # Run the async test function
    asyncio.run(test_arch()) 