import asyncio
import os
import traceback
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from loguru import logger
from datetime import datetime # Added for error logging timestamp

# Configure agent-level logger (can be customized further)
# Ensures agents have a logger instance readily available
agent_logger = logger.bind(agent=True)

class Message(BaseModel):
    """Represents a single message in the agent's memory."""
    role: str  # e.g., "user", "assistant", "system"
    content: str

class Memory(BaseModel):
    """Manages the conversation history for an agent."""
    messages: List[Message] = Field(default_factory=list)
    max_history: int = 50  # Limit memory history size

    def add_message(self, msg: Message):
        """Adds a message to the history, enforcing max length."""
        if not isinstance(msg, Message):
            try:
                # Attempt to create Message if dict is passed
                msg = Message(**msg)
            except ValidationError as e:
                agent_logger.error(f"Invalid message format: {msg}. Error: {e}")
                # Optionally raise error or just log and skip
                return

        self.messages.append(msg)
        # Trim history if it exceeds max length
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        agent_logger.debug(f"Message added. Memory size: {len(self.messages)}")

    def get_history(self) -> List[Dict[str, str]]:
        """Returns the message history as a list of dicts."""
        return [msg.model_dump() for msg in self.messages] # Use model_dump for Pydantic v2

    def get_last_message_content(self, role_filter: Optional[str] = None) -> Optional[str]:
        """Gets the content of the last message, optionally filtering by role."""
        relevant_messages = self.messages
        if role_filter:
            relevant_messages = [m for m in self.messages if m.role == role_filter]

        if not relevant_messages:
            return None
        return relevant_messages[-1].content

class AgentState:
    """Defines possible states for an agent."""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"

class BaseAgent(BaseModel, ABC):
    """Abstract Base Class for all DreamerAI agents."""
    name: str = Field(..., description="Unique name of the agent")
    user_dir: str = Field(..., description="Path to the user's workspace directory for this project")
    state: str = Field(default=AgentState.IDLE, description="Current state of the agent")
    memory: Memory = Field(default_factory=Memory, description="Agent's conversation/task memory")
    max_steps: int = Field(default=10, description="Maximum execution steps for the run loop")
    logger: Any = Field(default=agent_logger, description="Agent-specific logger instance")
    agent_chat_dir: str = Field(default="", description="Path to the agent's specific chat log directory")

    # Allow arbitrary types for flexibility with future integrations (like LLM clients)
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        """Initializes the BaseAgent."""
        super().__init__(**data)
        # Calculate and set the agent_chat_dir AFTER super().__init__ has validated base fields
        self.agent_chat_dir = os.path.join(self.user_dir, "Chats", self.name)
        os.makedirs(self.agent_chat_dir, exist_ok=True)
        # Patch the logger instance bound to this agent instance with its name
        self.logger = self.logger.patch(lambda record: record.update(name=self.name))
        self.logger.info(f"Agent '{self.name}' initialized for user dir: {self.user_dir}")

    @abstractmethod
    async def step(self, input_data: Optional[Any] = None) -> Any:
        """
        Perform a single step of the agent's logic.
        Must be implemented by subclasses.
        Should return the result of the step or indicate completion/error.
        """
        pass

    async def run(self, initial_input: Optional[Any] = None) -> Any:
        """
        Runs the agent's main execution loop.
        Handles state transitions, step execution, and basic error handling.
        """
        self.state = AgentState.RUNNING
        self.logger.info(f"Agent '{self.name}' starting run...")
        if initial_input:
            # Assuming initial input is typically user text
            if isinstance(initial_input, str):
                 self.memory.add_message(Message(role="user", content=initial_input))
            elif isinstance(initial_input, dict) and 'role' in initial_input and 'content' in initial_input:
                 self.memory.add_message(Message(**initial_input))
            else:
                 self.logger.warning(f"Received initial_input of unexpected type: {type(initial_input)}")
                 self.memory.add_message(Message(role="user", content=str(initial_input))) # Attempt conversion

        results = []
        current_step = 0
        last_result = None

        try:
            while self.state == AgentState.RUNNING and current_step < self.max_steps:
                current_step += 1
                self.logger.debug(f"Executing step {current_step}/{self.max_steps}")

                # Pass relevant context to the step method if needed
                # For now, using the last message content or initial input
                step_input = self.memory.get_last_message_content() or initial_input
                last_result = await self.step(step_input)
                results.append(last_result)

                # Basic check: If step returns None or specific signal, maybe finish?
                # Subclasses should manage their state more explicitly within step()
                # if last_result is None: # Placeholder for completion condition
                #      self.state = AgentState.FINISHED
                #      self.logger.info("Step returned None, considering run finished.")

                # Simple state check (subclass should ideally set state in step)
                if self.state == AgentState.FINISHED:
                    self.logger.info(f"Agent reached FINISHED state at step {current_step}.")
                    break
                elif self.state == AgentState.ERROR:
                    self.logger.error(f"Agent reached ERROR state at step {current_step}.")
                    break # Exit loop on error state set by step()

            if self.state == AgentState.RUNNING: # If loop finished by max_steps
                self.logger.warning(f"Run finished due to max_steps ({self.max_steps}) reached.")
                self.state = AgentState.FINISHED # Consider it finished, potentially incomplete

        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = f"Unhandled error during run: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            # Log error to agent's chat dir for specific context
            try:
                error_file = os.path.join(self.agent_chat_dir, "error.log")
                with open(error_file, "a") as f:
                    f.write(f"[{datetime.now()}] {error_msg}\n")
            except Exception as log_e:
                 self.logger.error(f"Failed to write to agent error log: {log_e}")
            # Maybe return error or raise? For now, returning error message.
            return {"error": error_msg} # Return structured error
        finally:
            if self.state not in [AgentState.ERROR, AgentState.RUNNING]: # RUNNING might imply interruption
                final_state = AgentState.IDLE # Reset to IDLE unless error or explicit ongoing state
            else:
                 final_state = self.state # Keep ERROR or RUNNING if set that way
            self.logger.info(f"Agent run finished. Final internal state before reset/return: {self.state}")
            if self.state != AgentState.ERROR: # Only reset if not ended in error
                 self.state = AgentState.IDLE

        # Return the final result or aggregated results
        # Returning the last result for simplicity now
        return last_result

    # Helper to potentially send updates to UI via bridge (implementation deferred)
    async def send_update_to_ui(self, message: str):
        self.logger.debug(f"Sending update to UI (placeholder): {message}")
        # Example of potential future implementation:
        # try:
        #     from ..core.bridge import send_to_ui # Avoid circular import issues at top level
        #     await send_to_ui(f"{self.name}: {message}")
        # except Exception as bridge_e:
        #     self.logger.error(f"Failed to send update to UI bridge: {bridge_e}")
        pass

# Basic Test Block (can be run with `python -m engine.agents.base`)
if __name__ == "__main__":

    # Example Dummy Agent for Testing
    class TestAgent(BaseAgent):
        async def step(self, input_data: Optional[Any] = None) -> Any:
            # Get current step count based on *assistant* messages in memory
            step_count = sum(1 for msg in self.memory.messages if msg.role == "assistant") + 1
            self.logger.info(f"TestAgent executing step {step_count} with input: {input_data}")
            await asyncio.sleep(0.1) # Simulate work
            if step_count >= 3: # Finish after 3 *assistant* steps
                self.state = AgentState.FINISHED
                result = "Test Complete"
            else:
                result = f"Step {step_count} processed input: {input_data}"

            self.memory.add_message(Message(role="assistant", content=result))
            await self.send_update_to_ui(result) # Simulate UI update
            return result

    async def main():
        print("Testing BaseAgent...")
        # Use a temporary directory relative to this file for testing
        test_user_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_user_workspace"))
        print(f"Using test user directory: {test_user_dir}")
        if not os.path.exists(test_user_dir):
            os.makedirs(test_user_dir)
            print(f"Created test directory: {test_user_dir}")

        agent = TestAgent(name="Tester001", user_dir=test_user_dir, max_steps=5)
        print(f"Initial State: {agent.state}")
        result = await agent.run(initial_input="Start Test Run")
        print(f"Run Result: {result}")
        print(f"Final State (should be IDLE): {agent.state}")
        print("Memory History:")
        for msg in agent.memory.get_history():
            print(f"- {msg['role']}: {msg['content']}")
        print("--- Test Complete ---")

        # Test error handling (optional)
        # print("\nTesting Error Handling...")
        # class ErrorAgent(BaseAgent):
        #     async def step(self, input_data: Optional[Any] = None) -> Any:
        #         raise ValueError("Simulated step error")
        # error_agent = ErrorAgent(name="ErrorProne", user_dir=test_user_dir)
        # error_result = await error_agent.run("Trigger error")
        # print(f"Error Agent Final State: {error_agent.state}")
        # print(f"Error Agent Result: {error_result}")

    asyncio.run(main()) 