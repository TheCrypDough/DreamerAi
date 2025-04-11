import asyncio
import logging
from typing import Dict, Any, Optional
from pydantic import Field

# Corrected relative imports based on file structure
from engine.agents.base import BaseAgent, AgentState
from engine.ai.llm import LLM
# Corrected import and usage of logger
from engine.core.logger import logger_instance as global_logger

# Initialize logger for this module by patching the global instance
logger = global_logger.patch(lambda record: record.update(name="NexusAgent"))

class Nexus(BaseAgent):
    """
    The orchestrator agent responsible for managing the overall AI workflow,
    delegating tasks to specialized agents, and maintaining the central state.
    """
    # Add the missing field definition for the LLM instance
    llm: LLM = Field(..., description="Instance of the LLM class for AI interactions")
    # Placeholder for managing other agents - will be expanded later
    agents: Dict[str, BaseAgent] = Field(default_factory=dict, description="Registry of specialized agents")
    workflow_state: Dict[str, Any] = Field(default_factory=dict, description="Central state managed by Nexus")

    def __init__(self, llm: LLM, user_dir: str = "C:/DreamerAI/Users/Default", **data: Any):
        """
        Initializes the Nexus agent.

        Args:
            llm: An instance of the LLM class to interact with language models.
            user_dir: The directory for user-specific data.
            **data: Additional keyword arguments passed to BaseAgent.
        """
        # Pass all arguments, including the Nexus-specific 'llm',
        # along with fixed 'name' and provided 'user_dir' to the super().__init__ call.
        # Pydantic will handle validation and assignment of all fields defined in Nexus and BaseAgent.
        super().__init__(llm=llm, name="Nexus", user_dir=user_dir, **data)

        # Post-initialization logic can go here if needed, but field assignments
        # like self.llm = llm are handled by Pydantic via the super() call.
        logger.info(f"Nexus agent initialized with LLM. User dir: {self.user_dir}")
        # Setting state AFTER super().__init__ is complete.
        self.state = AgentState.IDLE

    async def register_agent(self, agent: BaseAgent):
        """Registers a specialized agent with Nexus."""
        if agent.name in self.agents:
            logger.warning(f"Agent '{agent.name}' already registered. Overwriting.")
        self.agents[agent.name] = agent
        logger.info(f"Agent '{agent.name}' registered with Nexus.")

    async def delegate_task(self, agent_name: str, task_details: Dict[str, Any]) -> Any:
        """Delegates a task to a specific registered agent."""
        if agent_name not in self.agents:
            logger.error(f"Attempted to delegate task to unregistered agent: {agent_name}")
            raise ValueError(f"Agent '{agent.name}' not registered.")

        agent = self.agents[agent_name]
        logger.info(f"Delegating task to agent '{agent_name}': {task_details.get('description', 'No description')}")
        try:
            result = await agent.run(task_details) # Assuming run takes task details
            logger.info(f"Task completed by agent '{agent_name}'.")
            return result
        except Exception as e:
            logger.exception(f"Error during task delegation to agent '{agent_name}': {e}")
            raise

    async def step(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core logic step for Nexus. Determines the next action based on input
        and current workflow state. This will become more complex.

        Args:
            input_data: Data received for processing (e.g., user prompt).

        Returns:
            Output data after processing the step.
        """
        self.state = AgentState.RUNNING
        logger.info(f"Nexus starting step with input: {input_data}")

        # --- Basic Example ---
        # In a real scenario, Nexus would analyze the input, consult its state,
        # decide which agent(s) to call, format the sub-tasks, and manage results.
        # For now, just use the LLM manager directly for a simple echo/generation.

        prompt = input_data.get("prompt", "Describe the role of the Nexus agent.")
        logger.debug(f"Using prompt for LLM: '{prompt}'")

        try:
            # Format prompt into messages list
            messages = [{"role": "user", "content": prompt}]
            # Extract config values
            max_tokens = 150
            temperature = 0.7 # Assuming default if not specified

            # Corrected generate call with messages list and individual parameters
            response = await self.llm.generate(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            logger.info("LLM generation successful via LLM.") # Corrected log message
            output = {"response": response}

        except Exception as e:
            logger.exception(f"Error during LLM generation in Nexus step: {e}")
            output = {"error": "Failed to generate response.", "details": str(e)}
            self.state = AgentState.ERROR
            # In a real system, might try fallback or alert user/system
            return output # Return early on error

        # --- End Basic Example ---

        logger.info(f"Nexus step completed. Output: {output}")
        if self.state != AgentState.ERROR:
            self.state = AgentState.IDLE
        return output

    async def run(self, initial_prompt: str) -> Dict[str, Any]:
        """
        Runs the main loop or entry point for the Nexus agent.
        For now, just performs a single step based on the initial prompt.
        """
        logger.info(f"Nexus run initiated with prompt: '{initial_prompt}'")
        input_data = {"prompt": initial_prompt}
        result = await self.step(input_data)
        logger.info("Nexus run finished.")
        return result

# --- Test Execution Block ---
if __name__ == "__main__":
    async def main():
        print("--- Running Nexus Agent Test ---")
        # Setup basic logging to console for the test
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        test_logger = logging.getLogger("NexusTest")

        # Create LLM (requires config files setup from Day 6)
        try:
            test_logger.info("Initializing LLM...")
            # Note: LLM class initializes providers in its __init__
            llm_instance = LLM() # Corrected instantiation: LLM()
            # No separate initialize() call needed as it happens in LLM.__init__
            # We rely on the __init__ having completed successfully if no exception occurs
            test_logger.info("LLM initialized successfully.")
        except Exception as e:
            test_logger.exception(f"Failed to initialize LLM: {e}")
            print("--- Test Failed: LLM Initialization Error ---")
            return

        # Initialize Nexus
        test_logger.info("Initializing Nexus Agent...")
        nexus_agent = Nexus(llm=llm_instance)
        test_logger.info("Nexus Agent initialized.")

        # Example Run
        test_prompt = "Explain the concept of an orchestrator agent in an AI system like DreamerAI in one sentence."
        test_logger.info(f"Running Nexus with test prompt: '{test_prompt}'")

        try:
            result = await nexus_agent.run(test_prompt)
            test_logger.info(f"Nexus run completed. Result:")
            print(result) # Print the final result
        except Exception as e:
            test_logger.exception(f"Error during Nexus test run: {e}")
            print(f"--- Test Failed: Error during Nexus run: {e} ---")
            return

        print("--- Nexus Agent Test Completed Successfully ---")

    # Run the async main function
    asyncio.run(main()) 