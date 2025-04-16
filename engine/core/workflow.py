# C:\DreamerAI\engine\core\workflow.py
# Placeholder for DreamerFlow orchestrator class 

import asyncio
from typing import Dict, Any, Optional

# Add project root for sibling imports
import sys
import os
project_root_wf = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_wf not in sys.path:
    sys.path.insert(0, project_root_wf)

try:
    from engine.agents.base import BaseAgent # Assuming BaseAgent is in engine/agents/
    from engine.core.logger import logger_instance as logger, log_rules_check
except ImportError as e:
    print(f"Error importing modules in workflow.py: {e}")
    # Dummy classes for parsing
    class BaseAgent: pass
    import logging
    logger = logging.getLogger(__name__)
    def log_rules_check(action): logger.info(f"RULES CHECK (import failed): {action}")


class DreamerFlow:
    """
    Orchestrates the execution flow of DreamerAI agents.
    Manages the sequence and interaction of the 28 Dream Team agents.
    """
    def __init__(self, agents: Dict[str, BaseAgent], user_dir: str):
        """
        Initializes the DreamerFlow orchestrator.

        Args:
            agents: A dictionary mapping agent names to their instantiated objects.
            user_dir: The base directory for the current user's workspace.
        """
        if not agents:
            logger.error("DreamerFlow initialized with an empty agent dictionary!")
        self.agents = agents
        self.user_dir = user_dir
        # Define the high-level conceptual steps (actual logic implemented later)
        self.workflow_stages = [
            "Input Processing", # Promptimizer -> Jeff
            "Planning",         # Hermie -> Arch/Lewis
            "Building",         # Hermie -> Nexus -> Coders
            "Testing",          # Nexus -> Bastion/Daedalus/Herc
            "Documentation",    # Herc -> Scribe
            "Deployment Prep",  # Scribe -> Nike
            "Maintenance Setup" # Nike -> Ziggy/Ogre (Post-build)
        ]
        logger.info(f"DreamerFlow initialized with agents: {list(self.agents.keys())}")
        logger.info(f"Target User Directory: {self.user_dir}")


    async def execute(self, initial_user_input: str) -> Any:
        """
        Executes the main DreamerAI workflow.
        Currently (Day 9), this primarily passes input to Chef Jeff.
        Complex multi-agent orchestration will be added in later stages.

        Args:
            initial_user_input: The initial request or prompt from the user.

        Returns:
            The final result or response after processing (currently Jeff's response).
        """
        log_rules_check("Executing DreamerFlow") # Log rule check before execution
        logger.info(f"--- Starting DreamerFlow Execution for Input: '{initial_user_input[:100]}...' ---")

        # --- Stage 1: Input Processing ---
        # For now, directly pass to Jeff. Later, Promptimizer would run first.
        jeff_agent = self.agents.get("Jeff")

        if not jeff_agent:
            error_msg = "Critical Error: 'Jeff' (Main Chat Agent) not found in agents dictionary."
            logger.error(error_msg)
            return {"error": error_msg}

        try:
            logger.debug("Delegating initial input to Jeff...")
            # Call Jeff's run method (defined in Day 8)
            jeff_response = await jeff_agent.run(user_input=initial_user_input)
            logger.info("Jeff execution finished.")
            # logger.debug(f"Jeff's response snippet: {str(jeff_response)[:100]}...") # Careful logging PII

            # --- Subsequent Stages (Placeholders for Future Implementation) ---
            # Example:
            # planner_input = jeff_response # Or extracted task from Jeff's run
            # plan = await self.agents['Arch'].run(planner_input)
            # build_result = await self.agents['Nexus'].run(plan)
            # ... etc. ...

            logger.info("--- DreamerFlow Execution Finished (Initial Stage) ---")
            # For Day 9, we just return Jeff's response
            return jeff_response

        except KeyError as e:
             error_msg = f"Agent key error during workflow execution: {e}. Is agent registered?"
             logger.error(error_msg)
             return {"error": error_msg}
        except AttributeError as e:
             # Check specifically if the error is about the 'run' method
             if "'run'" in str(e):
                 error_msg = f"AttributeError: Agent '{jeff_agent.name if jeff_agent else 'Unknown'}' likely missing 'run' method: {e}"
             else:
                 error_msg = f"Attribute error during workflow execution: {e}"
             logger.error(error_msg, exc_info=True) # Log traceback for attribute errors
             return {"error": error_msg}
        except Exception as e:
            error_msg = f"An unexpected error occurred during DreamerFlow execution: {e}"
            logger.exception(error_msg) # Log full traceback
            return {"error": error_msg} 