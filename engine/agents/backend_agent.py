# C:\DreamerAI\engine\agents\backend_agent.py

import asyncio
import os
import traceback
from typing import Optional, Any, Dict
from pathlib import Path

# Add project root for sibling imports
import sys
project_root_be = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_be not in sys.path:
    sys.path.insert(0, project_root_be)

try:
    from engine.agents.base import BaseAgent, AgentState, Message
    from engine.ai.llm import LLM
    from engine.core.logger import logger_instance as logger, log_rules_check
    from engine.agents.agent_utils import save_code_to_file
except ImportError as e:
    print(f"Error importing modules in backend_agent.py: {e}")
    # Dummy classes / functions for parsing
    class BaseAgent:
        def __init__(self, *args, **kwargs): self.logger=print; self.name="DummyBE"; self.memory=Memory()
    class AgentState: IDLE,RUNNING,FINISHED,ERROR = 1,2,3,4
    class Message: pass
    class Memory:
        def add_message(self, *args, **kwargs): pass
    class LLM:
        def generate(self, *args, **kwargs): return "Placeholder BE Code Error"
    import logging
    logger = logging.getLogger(__name__)
    def log_rules_check(action): logger.info(f"RULES CHECK (import failed): {action}")

BACKEND_AGENT_NAME = "Dudley"

class DudleyAgent(BaseAgent):
    """
    Dudley: The Backend Coding Agent. Generates Python/FastAPI code from blueprint.
    V1 focuses on generating a basic main backend file.
    """
    def __init__(self, user_dir: str, **kwargs):
        super().__init__(name=BACKEND_AGENT_NAME, user_dir=user_dir, **kwargs)
        # Assign to _llm as per BaseAgent design
        self._llm = LLM()
        logger.info(f"DudleyAgent '{self.name}' initialized.")

    async def run(self, blueprint_content: str, project_output_path: str) -> Dict[str, Any]:
        """Generates backend code based on the blueprint."""
        self.state = AgentState.RUNNING
        log_rules_check(f"Running {self.name} to generate backend code.")
        logger.info(f"'{self.name}' starting backend code generation...")
        self.memory.add_message(Message(role="system", content="Task: Generate backend code based on blueprint."))

        # Define target paths
        output_dir = Path(project_output_path) / "backend" # Target output dir: output/backend
        output_file = output_dir / "main.py" # Target output file

        prompt = f"""
        **Role:** You are Dudley, a specialist Backend Developer AI for DreamerAI.
        **Task:** Generate Python code for a backend server based on the project blueprint below.
        **Target Framework:** FastAPI (as specified in DreamerAI's Tech Stack).
        **Project Blueprint:**
        ```markdown
        {blueprint_content}
        ```
        **Output Requirements:**
        - Generate a single Python file (`main.py`) containing a basic FastAPI application.
        - Include necessary imports (`FastAPI`, `uvicorn`, maybe `pydantic` for basic models if mentioned in blueprint).
        - Create a FastAPI app instance: `app = FastAPI()`.
        - Implement a simple root GET endpoint (`@app.get("/")`) that returns a JSON welcome message (e.g., `{{'message': 'Backend Online'}}`).
        - Include the standard boilerplate to run the app using `uvicorn.run()` within `if __name__ == '__main__':` (bind to host "0.0.0.0").
        - Ensure the code is clean, well-commented, and follows basic Python/FastAPI best practices (e.g., use type hints).
        - **ONLY output the raw Python code for main.py. Do not include explanations or markdown formatting.**
        """

        try:
            logger.debug("Requesting LLM generation for backend code...")
            # Use default model preference for Dudley in V1
            generated_code = await self._llm.generate(prompt, max_tokens=2000) # Use _llm

            if generated_code.startswith("ERROR:"):
                logger.error(f"LLM generation failed for {self.name}: {generated_code}")
                self.state = AgentState.ERROR
                return {"status": "error", "message": f"LLM failed: {generated_code}"}

            # Basic cleanup
            generated_code = generated_code.strip().strip('```python').strip('```').strip()

            self.memory.add_message(Message(role="assistant", content=f"Generated backend code snippet: {generated_code[:150]}..."))
            logger.info(f"Backend code generated by {self.name}.")

            # Save the code using helper
            if save_code_to_file(output_file, generated_code):
                self.state = AgentState.FINISHED
                return {"status": "success", "file_path": str(output_file)}
            else:
                self.state = AgentState.ERROR
                return {"status": "error", "message": f"Failed to save backend code to {output_file}"}

        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = f"Unexpected error during {self.name} run: {e}" # General error message
            logger.exception(error_msg)
            return {"status": "error", "message": error_msg}
        finally:
             current_state = self.state
             if current_state == AgentState.FINISHED:
                 self.state = AgentState.IDLE # Reset to IDLE after successful run
             logger.info(f"'{self.name}' run finished. Final state: {self.state} (was {current_state})")

    async def step(self, input_data: Optional[Any] = None) -> Any:
         logger.warning(f"{self.name}.step() called, but run() expects specific args. Step not supported in V1.")
         self.state = AgentState.ERROR
         return {"error": f"{self.name} cannot be executed via step() in V1."}

# Test block from guide removed as it's better placed in main.py or dedicated test files.
# (Test block logic will be integrated into main.py in a later task) 