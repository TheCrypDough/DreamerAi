# C:\DreamerAI\engine\agents\planning.py
# Placeholder for Arch (Planning) Agent
# Implementation details to follow.

import asyncio
import os
import traceback
from typing import Optional, Any, Dict # Added Dict hint
from pathlib import Path

# Add project root for sibling imports
import sys
project_root_plan = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_plan not in sys.path:
    sys.path.insert(0, project_root_plan)

try:
    from engine.agents.base import BaseAgent, AgentState, Message
    from engine.ai.llm import LLM
    from engine.core.logger import logger_instance as logger, log_rules_check
except ImportError as e:
    print(f"Error importing modules in planning.py: {e}")
    # Dummy classes for parsing
    class BaseAgent:
        def __init__(self, *args, **kwargs):
            self.logger=print
            self.name="DummyPlanner"
    class AgentState: IDLE,RUNNING,FINISHED,ERROR = 1,2,3,4
    class Message: pass
    class LLM: 
        def generate(self, *args, **kwargs):
             return "# Placeholder Plan Error"
    import logging
    logger = logging.getLogger(__name__)
    def log_rules_check(action): logger.info(f"RULES CHECK (import failed): {action}")

PLANNING_AGENT_NAME = "Arch" # Archimedes

class PlanningAgent(BaseAgent):
    """
    Arch: The Planning Agent. Generates project blueprints based on input.
    V1 focuses on text input to create blueprint.md.
    """
    def __init__(self, user_dir: str, **kwargs):
        # Planning might involve complex reasoning, default to non-distilled if choice exists?
        # For now, assume BaseAgent handles model selection based on config/distill flag.
        # If specific model needed, LLM instance could be overridden here.
        super().__init__(name=PLANNING_AGENT_NAME, user_dir=user_dir, **kwargs)
        self._llm = LLM() # Assign to private _llm attribute
        logger.info(f"PlanningAgent '{self.name}' initialized.")

    # --- NEW V1 Placeholder Method ---
    async def receive_task(self, task_data: Dict[str, Any]):
        """ V1: Placeholder to acknowledge task receipt from Hermie. """
        task_desc = task_data.get("task_description", "Unknown task")
        log_rules_check(f"{self.name} received task simulation") # Use global check
        self.logger.info(f"ARCH V1: Received task data via receive_task(): '{task_desc[:100]}...'") # Use instance logger
        # Check if memory attribute exists and is not None before adding message
        if hasattr(self, 'memory') and self.memory:
             self.memory.add_message(Message(role="system", content=f"Received task memo: {task_desc[:100]}"))
        else:
             self.logger.warning("Memory not available for Arch V1 receive_task logging.")
        # In V2+, this would trigger planning logic or add to Arch's queue
        await asyncio.sleep(0.05) # Simulate minimal processing acknowledgement

    def _get_output_path(self, base_user_project_path: str) -> Path:
        """Determines the path to save the blueprint."""
        # Ensure base path is Path object
        base_path = Path(base_user_project_path)
        # Define specific output location within the project structure
        output_dir = base_path / "Overview"
        output_dir.mkdir(parents=True, exist_ok=True) # Ensure 'Overview' subdir exists
        return output_dir / "blueprint.md"


    async def run(self, project_idea: str, project_context_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a project blueprint based on the textual idea.

        Args:
            project_idea: The core idea or goal provided by the user (potentially refined).
            project_context_path: The base path for the specific user project (e.g., C:/Users/.../Projects/MyWebApp).
                                  Required to know where to save the output.

        Returns:
            A dictionary containing the status and the path to the blueprint or an error message.
        """
        self.state = AgentState.RUNNING
        log_rules_check(f"Running PlanningAgent for idea: {project_idea[:50]}...")
        logger.info(f"'{self.name}' starting plan generation run...")
        self.memory.add_message(Message(role="system", content=f"Generate plan for: {project_idea}")) # Add task to memory

        if not project_context_path:
            error_msg = "Project context path is required to save the blueprint."
            logger.error(error_msg)
            self.state = AgentState.ERROR
            return {"status": "error", "message": error_msg}

        # --- Prepare Prompt ---
        # TODO: Later, incorporate RAG context, user files context, etc.
        prompt = f"""
        **Role:** You are Arch, an expert AI project planner for DreamerAI.
        **Task:** Generate a structured project blueprint in Markdown format based on the following user idea.
        **User Idea:** "{project_idea}"

        **Output Requirements:**
        - Start with a clear Title (e.g., `# Blueprint: [Project Name]`)
        - Include sections for:
            - **Project Summary:** Briefly restate the core goal.
            - **Core Features:** List key functionalities (3-5 minimum).
            - **Potential Tech Stack:** Suggest suitable frontend/backend/database technologies (consider flexibility).
            - **High-Level Steps:** Outline the main phases of development (e.g., Setup, UI Design, Backend Logic, API Dev, Testing, Deployment).
            - **Next Steps:** Suggest immediate next actions.
        - Use Markdown formatting (headings, lists).
        - Be detailed enough to guide initial development but flexible for iteration.
        """

        # --- Generate Plan ---
        try:
            logger.debug("Requesting LLM generation for blueprint...")
            # Use default model preference from config for Arch for now
            blueprint_content = await self._llm.generate(prompt, max_tokens=2000) # Allow longer response

            if blueprint_content.startswith("ERROR:"):
                logger.error(f"LLM generation failed: {blueprint_content}")
                self.state = AgentState.ERROR
                return {"status": "error", "message": f"LLM failed: {blueprint_content}"}

            self.memory.add_message(Message(role="assistant", content=f"Generated blueprint snippet: {blueprint_content[:100]}..."))
            logger.info("Blueprint content generated successfully.")

            # --- Save Blueprint --- 
            output_file_path = self._get_output_path(project_context_path)
            logger.debug(f"Blueprint output target: {output_file_path}")
            try:
                logger.debug(f"Attempting to save blueprint to {output_file_path}...")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(blueprint_content)
                logger.info(f"Blueprint successfully saved to {output_file_path}")
                self.state = AgentState.FINISHED
                return {"status": "success", "blueprint_path": str(output_file_path), "content_preview": blueprint_content[:200]+"...", "message": "Blueprint generated and saved."}

            except IOError as e:
                error_msg = f"Failed to save blueprint to {output_file_path}: {e}"
                logger.error(error_msg)
                self.state = AgentState.ERROR
                return {"status": "error", "message": error_msg}

        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = f"Unexpected error during LLM generation or saving: {e}" # Updated error message slightly
            logger.exception(error_msg) # Log full traceback
            return {"status": "error", "message": error_msg}
        finally:
             current_state = self.state
             if self._llm: # Example check, adjust logic as needed
                 pass # Placeholder for potential cleanup or checks

             if current_state == AgentState.FINISHED:
                  self.state = AgentState.IDLE
             logger.info(f"'{self.name}' run finished. Final state: {self.state} (was {current_state})")


    # Implement abstract step method - delegate to run for now
    async def step(self, input_data: Optional[Any] = None) -> Any:
        """ BaseAgent requires step. Delegate Arch's logic to run(). Needs project_idea & project_context_path."""
        logger.warning("PlanningAgent step() called, but run() expects project_idea and project_context_path. Cannot execute via step() directly yet.")
        # How step() gets context needs design within DreamerFlow later
        # For now, step is non-functional for PlanningAgent.
        self.state = AgentState.ERROR
        return {"error": "PlanningAgent cannot be executed via step() in V1."}


# --- Test Block ---
# Test block will be added in a later task after run() is implemented.
# async def test_planning_agent():
#    pass
#
# if __name__ == "__main__":
#    pass 