import asyncio
import os
import traceback
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, cast
from pydantic import BaseModel, Field, ValidationError, PrivateAttr
from pydantic_core import PydanticCustomError
from loguru import logger
from datetime import datetime

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
        return [msg.dict() for msg in self.messages]

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
    agent_chat_dir: Optional[str] = Field(None, init=False, description="Path to agent-specific chat logs")

    # Private attribute for LLM instance, specific agents will initialize it
    _llm: Optional[Any] = PrivateAttr(default=None)

    # Allow arbitrary types for flexibility with future integrations (like LLM clients)
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        """Initializes the BaseAgent (Pydantic part)."""
        super().__init__(**data)
        # Initialization needing validated fields moved to model_post_init

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization logic for non-Pydantic fields."""
        # Calculate and assign the path here
        self.agent_chat_dir = os.path.join(self.user_dir, "Chats", self.name)
        # Ensure user-specific directory exists
        os.makedirs(self.agent_chat_dir, exist_ok=True)
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
            self.memory.add_message(Message(role="user", content=str(initial_input)))

        results = []
        current_step = 0
        last_result = None

        try:
            while self.state == AgentState.RUNNING and current_step < self.max_steps:
                current_step += 1
                self.logger.debug(f"Executing step {current_step}/{self.max_steps}")

                # Pass relevant context to the step method if needed
                # For now, using the last message or initial input
                step_input = self.memory.get_last_message_content() or initial_input
                last_result = await self.step(step_input)
                results.append(last_result)

                # Basic check: If step returns None or specific signal, maybe finish?
                # Subclasses should manage their state more explicitly within step()
                if last_result is None: # Placeholder for completion condition
                     self.state = AgentState.FINISHED
                     self.logger.info("Step returned None, considering run finished.")

                # Simple state check (subclass should ideally set state in step)
                if self.state == AgentState.FINISHED:
                    self.logger.info(f"Agent reached FINISHED state at step {current_step}.")
                    break

            if self.state == AgentState.RUNNING:
                self.logger.warning(f"Run finished due to max_steps ({self.max_steps}) reached.")
                self.state = AgentState.FINISHED # Or maybe ERROR state?

        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = f"Unhandled error during run: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            # Log error to agent's chat dir for specific context
            if self.agent_chat_dir: # Check if path was set
                error_file = os.path.join(self.agent_chat_dir, "error.log")
                with open(error_file, "a") as f:
                    f.write(f"[{datetime.now()}] {error_msg}\n")
            else:
                self.logger.error("agent_chat_dir not set, cannot write specific error log.")
            return {"error": error_msg}
        finally:
            if self.state != AgentState.ERROR:
                self.state = AgentState.IDLE # Reset to IDLE unless error occurred
            self.logger.info(f"Agent run finished with state: {self.state}")

        # Return the final result or aggregated results
        # Returning the last result for simplicity now
        return last_result

    # Helper to potentially send updates to UI via bridge (implementation deferred)
    async def send_update_to_ui(self, message: str):
        self.logger.debug(f"Sending update to UI (placeholder): {message}")
        # from ..core.bridge import send_to_ui # Avoid circular import issues
        # await send_to_ui(f"{self.name}: {message}")
        pass

# Basic Test Block (can be run with `python -m engine.agents.base`)
if __name__ == "__main__":
    # Added missing import
    from datetime import datetime

    # Example Dummy Agent for Testing
    class TestAgent(BaseAgent):
        async def step(self, input_data: Optional[Any] = None) -> Any:
            step_count = len(self.memory.messages) # Simple way to track steps
            self.logger.info(f"TestAgent executing step {step_count} with input: {input_data}")
            if step_count >= 3: # Finish after 3 steps
                self.state = AgentState.FINISHED
                result = "Test Complete"
            else:
                result = f"Step {step_count} processed: {input_data}"

            self.memory.add_message(Message(role="assistant", content=result))
            await self.send_update_to_ui(result) # Simulate UI update
            return result

    async def main():
        print("Testing BaseAgent...")
        # Use a relative path for test dir robustness
        test_user_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_user_workspace"))
        if not os.path.exists(test_user_dir):
            os.makedirs(test_user_dir)
        print(f"Test user dir: {test_user_dir}")

        agent = TestAgent(name="Tester001", user_dir=test_user_dir)
        print(f"Initial State: {agent.state}")
        result = await agent.run(initial_input="Start Test Run")
        print(f"Final State: {agent.state}")
        print(f"Final Result: {result}")
        print("Memory History:")
        for msg in agent.memory.get_history():
            print(f"- {msg['role']}: {msg['content']}")

        # Optional: Clean up test directory (Uncomment if desired)
        # import shutil
        # try:
        #     shutil.rmtree(test_user_dir)
        #     print("Cleaned up test directory.")
        # except OSError as e:
        #     print(f"Error removing test directory {test_user_dir}: {e}")

    asyncio.run(main()) 