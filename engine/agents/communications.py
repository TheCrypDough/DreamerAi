# C:\DreamerAI\engine\agents\communications.py
# Placeholder for Hermie (Communications Hub) Agent
# Implementation details to follow.

# from .base import BaseAgent
# class CommunicationsAgent(BaseAgent):
#     pass 

import asyncio
import os
import json
import traceback
from typing import Optional, Any, Dict, List
from pathlib import Path

# Add project root...
import sys
project_root_hermie = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_hermie not in sys.path: sys.path.insert(0, project_root_hermie)

try:
    # Inherit from functional BaseAgent V2
    from pydantic import Field
    from engine.agents.base import BaseAgent, AgentState, Message
    from engine.core.logger import logger_instance as logger, log_rules_check
    # Need PlanningAgent and LewisAgent for type hints and calls (NEW)
    from engine.agents.planning import PlanningAgent
    from engine.agents.administrator import LewisAgent
    # RAG Import handled by BaseAgent V2 init check
except ImportError as e:
    # Fallback dummies...
    logger.error(f"Failed to import manager agents or base components in Hermie: {e}") # Updated error message
    import logging; logger = logging.getLogger(__name__); AgentState=type('AgentState', (), {'IDLE':'idle','RUNNING':'running','FINISHED':'finished','ERROR':'error'}); Message=dict; BaseAgent=object; log_rules_check=print; Field=lambda **k: None # Basic dummies
    PlanningAgent, LewisAgent = None, None # Define as None if import fails (NEW)

HERMIE_AGENT_NAME = "Hermie"

# --- Define DEFAULT_USER_DIR mirroring main.py --- # ADDED
DEFAULT_USER_DIR = r"C:\DreamerAI\Users\Example User"

class HermieAgent(BaseAgent):
    """
    Hermie: The Communications Agent V1.
    Simulates routing tasks from Jeff (via run input) to Arch and Lewis.
    """
    # agents field definition already Optional via BaseAgent inheritance or explicit Optional
    # (Assuming BaseAgent or this class marks it appropriately for Pydantic)
    agents: Optional[Dict[str, BaseAgent]] = Field(default=None, init=False) # Ensure pydantic knows it's not part of initial data

    # Modified __init__ to accept Optional agents, assign after super
    def __init__(self, agents: Optional[Dict[str, BaseAgent]] = None, user_dir: str = DEFAULT_USER_DIR, **kwargs):
        # Set name and user_dir first for BaseAgent's Pydantic validation
        kwargs['name'] = HERMIE_AGENT_NAME
        kwargs['user_dir'] = user_dir
        super().__init__(**kwargs) # Pass only kwargs recognized by BaseAgent/Pydantic model

        # Now assign the agents dictionary after BaseAgent init is complete
        if agents:
            self.agents = agents
            logger.info(f"HermieAgent '{self.name}' V1 initialized with agent references: {list(self.agents.keys())}")
        else:
            self.agents = {}
            logger.warning(f"HermieAgent '{self.name}' V1 initialized WITHOUT agent references!")
        # self.rules_file = os.path.join(r"C:\DreamerAI\engine\agents", f"rules_{self.name.lower()}.md") # BaseAgent V2 handles this
        # self._load_rules() # BaseAgent V2 handles this

    # BaseAgent V2 handles _load_rules etc.

    # Added placeholder for broadcast_dream_theatre_update
    async def broadcast_dream_theatre_update(self, update: Dict[str, Any]):
        """ Placeholder for sending updates to the Dream Theatre UI. """
        # In a real implementation, this would use a WebSocket or similar mechanism
        # provided via the Bridge or a dedicated event system.
        self.logger.debug(f"(Simulated) Broadcasting to Dream Theatre: {update.get('event', 'Unknown event')}")
        await asyncio.sleep(0.01) # Simulate async call

    # Replace previous placeholder run method with V1 routing logic
    async def run(self, task_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        V1 Run: Receives task data (simulating from Jeff via n8n placeholder trigger)
        and calls receive_task on Arch and Lewis.
        """
        self.state = AgentState.RUNNING
        if task_data is None: task_data = {"task_description": "Default test task for Hermie"}
        task_desc = task_data.get("task_description", "No description")

        # log_rules_check(f"Running {self.name} V1 routing simulation") # Use instance logger
        self.logger.info(f"Running {self.name} V1 routing simulation...") # Use instance logger
        self.logger.info(f"'{self.name}' V1 received task data: {task_desc[:50]}...")
        self.memory.add_message(Message(role="system", content=f"Received task: {task_desc}"))

        results = {"status": "failed", "routed_to": [], "errors": []}

        targets = ["Arch", "Lewis"] # V1: Distribute to planner and admin
        for target_name in targets:
            target_agent = self.agents.get(target_name)
            # Check if target_agent exists and has the 'receive_task' async method
            if target_agent and hasattr(target_agent, 'receive_task') and asyncio.iscoroutinefunction(getattr(target_agent, 'receive_task', None)):
                try:
                    self.logger.debug(f"Hermie routing task to {target_name}...")
                    # Pass the received task data dictionary directly
                    await target_agent.receive_task(task_data)
                    self.logger.info(f"Task successfully routed to {target_name} (simulated receipt).")
                    results["routed_to"].append(target_name)
                except Exception as e:
                    error_msg = f"Error calling receive_task on {target_name}: {e}"
                    self.logger.exception(error_msg) # Log full traceback
                    results["errors"].append({target_name: error_msg})
            elif not target_agent:
                 error_msg = f"Agent '{target_name}' not found in Hermie's dictionary."
                 self.logger.error(error_msg)
                 results["errors"].append({target_name: error_msg})
            else:
                # Handle case where receive_task exists but is not an async function or is missing
                error_msg = f"Agent '{target_name}' does not have a suitable 'receive_task' async method."
                self.logger.error(error_msg)
                results["errors"].append({target_name: error_msg})

        # Determine final status
        if results["routed_to"] and not results["errors"]:
            results["status"] = "success"
        elif results["routed_to"] and results["errors"]:
             results["status"] = "partial_success"
        # If no routing succeeded, status remains "failed"

        # Simulate broadcast (logic TBD)
        await self.broadcast_dream_theatre_update({"event": "task_distributed", "targets": targets, "task": task_desc[:50]})

        # Transition state based on outcome
        if results["status"] == "success" or results["status"] == "partial_success":
             self.state = AgentState.FINISHED
        else:
             self.state = AgentState.ERROR

        # BaseAgent V2 handles IDLE transition from FINISHED/ERROR if configured

        self.logger.info(f"'{self.name}' V1 routing simulation finished. Status: {results['status']}")
        self.memory.add_message(Message(role="assistant", content=f"Routing simulated. Status: {results['status']}"))
        return results

    async def step(self, input_data: Optional[Any] = None) -> Any:
        """ V1: Step delegates to run simulation. """
        self.logger.warning(f"{self.name}.step() called. V1 placeholder delegates to run().")
        return await self.run(input_data)

    # Test function placeholder (can be removed or updated for V1 test if needed)
    # async def test_hermie_agent_v1(self):
    #     self.logger.info(f"--- Testing {self.name} V1 ---")
    #     test_task = {"task_description": "Test task for Hermie V1 routing"}
    #     result = await self.run(task_data=test_task)
    #     self.logger.info(f"Test Result: {result}")
    #     self.logger.info(f"--- Test {self.name} V1 Complete ---")

# Keep __main__ block if needed for standalone testing, otherwise remove/comment out
# if __name__ == "__main__":
#     # Example usage for standalone testing (requires setting up dummy agents)
#     user_dir = r"C:\DreamerAI\Users\TestUserHermie"
#     # Create dummy agents for testing
#     dummy_arch = BaseAgent(name="Arch", user_dir=user_dir)
#     dummy_lewis = BaseAgent(name="Lewis", user_dir=user_dir)
#     # Add dummy receive_task methods
#     async def dummy_receive(task_data): logger.info(f"Dummy Received: {task_data['task_description'][:20]}")
#     dummy_arch.receive_task = dummy_receive
#     dummy_lewis.receive_task = dummy_receive
#     test_agents = {"Arch": dummy_arch, "Lewis": dummy_lewis}
#     hermie = HermieAgent(agents=test_agents, user_dir=user_dir)
#     asyncio.run(hermie.test_hermie_agent_v1()) 