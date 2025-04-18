# C:\DreamerAI\engine\core\workflow.py
# Placeholder for DreamerFlow orchestrator class 

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import traceback
import sys
import json # Import json for logging potentially complex results

# Add project root for sibling imports
project_root_wf = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_wf not in sys.path: sys.path.insert(0, project_root_wf)

try:
    from engine.agents.base import BaseAgent, AgentState # Needs AgentState V1
    from engine.core.logger import logger_instance as logger, log_rules_check
except ImportError as e:
    # Dummy classes for parsing/basic run
    print(f"CRITICAL Error importing modules in workflow.py: {e}")
    class BaseAgent:
        # Minimal dummy structure if needed for type hints or basic calls
        pass
    class AgentState:
        IDLE = 'idle'
        RUNNING = 'running'
        FINISHED = 'finished'
        ERROR = 'error'
    import logging
    logger = logging.getLogger(__name__)
    log_rules_check = print


class DreamerFlow:
    """
    Orchestrates the execution flow of DreamerAI agents.
    Manages the sequence and interaction of the Dream Team agents.
    """
    def __init__(self, agents: Dict[str, BaseAgent], user_dir: str):
        """
        Initializes the DreamerFlow orchestrator. Requires dict of instantiated agents.
        """
        if not agents:
            logger.error("DreamerFlow initialized with an empty agent dictionary!")
            # Consider raising error? Or proceed with limited functionality? V1 proceed.
        self.agents = agents
        self.user_dir = user_dir
        # Workflow stages for potential future use in Dream Theatre etc.
        self.workflow_stages = [
            "Input Refinement (Promptimizer)",
            "User Interaction (Jeff)",
            "Planning (Arch)",
            "Coding Management (Nexus)",
            "Security Scan (Bastion)",
            "Testing (Herc)",
            "Documentation (Scribe)",
            "Deployment Prep (Nike)"
        ]
        self._state = AgentState.IDLE # Internal state for the flow itself? Optional V1
        logger.info(f"DreamerFlow initialized with agents: {list(self.agents.keys())}")
        logger.info(f"Target User Directory: {self.user_dir}")

    @property
    def state(self) -> str: return self._state
    @state.setter
    def state(self, value: str): # Basic state setter for flow
        if value != self._state:
            logger.info(f"DreamerFlow State Change: {self._state} -> {value}")
            self._state = value
            # Publish flow state change event later?

    async def execute(self, initial_user_input: str, test_project_name: Optional[str] = None) -> Any:
        """
        Executes the main DreamerAI workflow (V2: Jeff -> Arch -> Nexus(V1 Sim)).
        Uses functional BaseAgent V2 capabilities (async run, etc.).

        Args:
            initial_user_input: The initial request or prompt from the user.
            test_project_name: (Optional for testing) A specific name for the project context.

        Returns:
            The final result (Nexus V1 simulation result) or an error dictionary.
        """
        log_rules_check("Executing DreamerFlow V2") # Adhere to rules
        logger.info(f"--- Starting DreamerFlow Execution V2: Input='{initial_user_input[:100]}...' ---")
        self.state = AgentState.RUNNING

        # --- Determine Project Context ---
        # TODO D112: Replace this with proper context resolution API call later.
        if not test_project_name:
            test_project_name = f"FlowTest_D16_{int(asyncio.get_event_loop().time())}"
        user_base = Path(self.user_dir)
        project_context_path = user_base / "Projects" / test_project_name
        project_output_path = project_context_path / "output" # Standard output subfolder

        # Ensure key directories exist before agents might need them
        try:
            project_context_path.mkdir(parents=True, exist_ok=True)
            (project_context_path / "Overview").mkdir(parents=True, exist_ok=True) # For Arch V1/V2
            project_output_path.mkdir(parents=True, exist_ok=True) # For Nexus/Coders V1+
            logger.info(f"Using Project Context Path: {project_context_path}")
            logger.info(f"Using Project Output Path: {project_output_path}")
        except OSError as e:
             logger.error(f"Failed creating project directories: {e}")
             self.state = AgentState.ERROR
             return {"status": "error", "error": f"Directory creation failed: {e}", "stage": "Setup"}


        # --- Initialize Workflow Variables ---
        final_result: Any = {"status": "failed", "error": "Workflow V2 did not complete."}
        blueprint_content: Optional[str] = None
        blueprint_path: Optional[str] = None
        # Variable to hold input for the next agent, starts with initial input
        current_input = initial_user_input

        # --- Agent Execution Sequence V2 ---
        try:
            # --- Stage 1: Jeff (V1 using BaseAgent V2) ---
            logger.info("--- Starting Stage 1: Jeff ---")
            jeff_agent = self.agents.get("Jeff")
            if not jeff_agent: raise KeyError("Jeff agent not found")
            # Use await because BaseAgent V2 run is async
            jeff_result = await jeff_agent.run(user_input=current_input)
            logger.info(f"Jeff execution complete. Result snippet: {str(jeff_result)[:100]}...")
            # V1: Assume core idea for Arch is still the initial input
            # V2+ Jeff should return structured output indicating task/idea for Arch
            core_project_idea = current_input
            # TODO V2+: Check jeff_result for errors or specific instructions?


            # --- Stage 2: Arch (V1/V2 using BaseAgent V2) ---
            logger.info("--- Starting Stage 2: Arch ---")
            arch_agent = self.agents.get("Arch")
            if not arch_agent: raise KeyError("Arch agent not found")
            logger.info(f"Executing Arch for idea: '{core_project_idea[:50]}...'")
            # Pass context path needed by Arch V1/V2
            arch_result = await arch_agent.run(
                project_idea=core_project_idea,
                project_context_path=str(project_context_path)
            )
            logger.info(f"Arch execution complete. Result Status: {arch_result.get('status')}")

            if arch_result.get("status") != "success":
                raise Exception(f"Arch (Planning) failed: {arch_result.get('message', 'Unknown planning error')}")

            blueprint_path = arch_result.get("blueprint_path") # Arch V2+ should return path
            if not blueprint_path or not Path(blueprint_path).exists():
                 raise FileNotFoundError(f"Arch succeeded but blueprint file not found at {blueprint_path}")

            logger.info(f"Blueprint generated by Arch at: {blueprint_path}")
            # Read blueprint content for Nexus
            try:
                 blueprint_content = Path(blueprint_path).read_text(encoding="utf-8")
                 logger.debug("Blueprint content read successfully for Nexus.")
            except Exception as e:
                raise IOError(f"Failed to read blueprint content from {blueprint_path}: {e}")


            # --- Stage 3: Nexus (V1 Placeholder Simulation using BaseAgent V2) ---
            logger.info("--- Starting Stage 3: Nexus (V1 Simulation) ---")
            nexus_agent = self.agents.get("Nexus")
            if not nexus_agent: raise KeyError("Nexus agent not found")
            logger.info("Executing Nexus V1 simulation...")
            # Pass blueprint and output path
            nexus_result = await nexus_agent.run(
                blueprint_content=blueprint_content,
                project_output_path=str(project_output_path)
            )
            logger.info(f"Nexus V1 Simulation complete. Status: {nexus_result.get('status')}")
            if nexus_result.get("status") != "success":
                 # Log error but allow flow to finish V1 for placeholder
                 logger.error(f"Nexus V1 simulation failed unexpectedly: {nexus_result.get('message')}")

            # --- Flow V2 Ends Here ---
            final_result = nexus_result # Return the result from the last step V1/V2
            logger.info(f"--- DreamerFlow Execution V2 Finished. Final Status: {final_result.get('status', 'unknown')} ---")
            self.state = AgentState.FINISHED
            return final_result

        except KeyError as e:
             error_msg = f"Agent key error during workflow V2: {e}. Is agent initialized correctly in main.py?"
             logger.error(error_msg)
             self.state = AgentState.ERROR
             return {"error": error_msg, "status": "failed", "stage": "Agent Lookup"}
        except FileNotFoundError as e:
             error_msg = f"File not found during workflow V2 (likely blueprint): {e}"
             logger.error(error_msg)
             self.state = AgentState.ERROR
             return {"error": error_msg, "status": "failed", "stage": "File Access"}
        except IOError as e:
              error_msg = f"File reading error during workflow V2 (likely blueprint): {e}"
              logger.error(error_msg)
              self.state = AgentState.ERROR
              return {"error": error_msg, "status": "failed", "stage": "File Read"}
        except Exception as e:
            error_msg = f"An unexpected error occurred during DreamerFlow V2 execution: {e}"
            logger.exception(error_msg) # Log full traceback
            self.state = AgentState.ERROR
            return {"error": error_msg, "status": "failed", "stage": "Unknown"}
        finally:
             # Reset state if finished successfully
             if self._state == AgentState.FINISHED:
                 self.state = AgentState.IDLE 