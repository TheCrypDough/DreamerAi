# C:\DreamerAI\engine\agents\administrator.py (CORRECTED for BaseAgent V2)
import asyncio
import os
import json
import traceback
from typing import Optional, Any, Dict, List
from pathlib import Path

# Add project root for sibling imports AND TOOLCHEST_PATH calculation
import sys
project_root_lewis = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_lewis not in sys.path: sys.path.insert(0, project_root_lewis)

try:
    # Inherit from functional BaseAgent V2
    from engine.agents.base import BaseAgent, AgentState, Message
    from engine.core.logger import logger_instance as logger, log_rules_check
except ImportError as e:
    # Fallback dummies...
    print(f"ERROR importing in administrator.py: {e}")
    # Define dummy BaseAgent, AgentState, logger etc.
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
    class AgentState: IDLE='idle'; RUNNING='running'; FINISHED='finished' # Added RUNNING/FINISHED
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


LEWIS_AGENT_NAME = "Lewis"
# CORRECTED Path using project_root variable defined above
TOOLCHEST_PATH = Path(project_root_lewis) / "tools" / "toolchest.json"

class LewisAgent(BaseAgent):
    """
    Lewis Agent V1: Administrator. Manages toolchest.json cache.
    Inherits functional BaseAgent V2.
    """
    # Type hint for the cache - Use Field for Pydantic model integration
    # toolchest: Dict[str, List[Dict[str, Any]]] = Field(default_factory=lambda: {"tools": [], "mcp_protocols": []})
    # V1: Simpler init, load cache directly as instance attribute
    toolchest: Dict[str, List[Dict[str, Any]]] = {"tools": [], "mcp_protocols": []}
    # Declare 'agents' as an optional field for the model
    agents: Optional[Dict[str, BaseAgent]] = None

    #agents: Optional[Dict[str, BaseAgent]] = None # Stored for future V2+ use

    def __init__(self, user_dir: str, agents: Optional[Dict[str, BaseAgent]] = None, **kwargs):
        # Initialize BaseAgent V2 first - This sets up logger, paths like _agent_base_dir, etc.
        super().__init__(name=LEWIS_AGENT_NAME, user_dir=user_dir, **kwargs)
        self.agents = agents or {} # Store agent references for future use

        # V1 Specific: Load tool data from JSON into cache AFTER BaseAgent init
        self._load_toolchest() # Now self.logger exists from super init

        self.logger.info(f"{self.name} V1 Initialized (Inherits BaseAgent V2).")
        self.logger.info(f"Loaded {len(self.toolchest.get('tools',[]))} tools, {len(self.toolchest.get('mcp_protocols',[]))} protocols into cache.")
        # self._agent_base_dir is available here if needed AFTER super().__init__
        # self.logger.debug(f"Agent Base Dir (from BaseAgent V2): {self._agent_base_dir}")

    # V1 Method: Load from JSON into self.toolchest cache
    def _load_toolchest(self):
        """Loads tool and protocol data from toolchest.json into memory cache."""
        log_rules_check(f"Loading toolchest cache from {TOOLCHEST_PATH}") # Use global check function
        # Use self.logger provided by BaseAgent V2
        if not hasattr(self, 'logger'): self.logger = logger # Safety fallback if super init somehow failed logger
        try:
            if TOOLCHEST_PATH.is_file():
                with open(TOOLCHEST_PATH, 'r', encoding='utf-8') as f:
                    # Use parse_obj_as for potential validation later? V1 simple load.
                    loaded_data = json.load(f)
                    # Basic validation for V1
                    if isinstance(loaded_data, dict) and isinstance(loaded_data.get('tools'), list):
                         self.toolchest = loaded_data
                         # Ensure protocols list exists if missing
                         if 'mcp_protocols' not in self.toolchest:
                              self.toolchest['mcp_protocols'] = []
                    else:
                         raise ValueError("Invalid toolchest structure: expected dict with 'tools' list.")
                self.logger.info(f"Successfully loaded toolchest cache from JSON.")
            else:
                 self.logger.error(f"Toolchest file not found: {TOOLCHEST_PATH}. Cache is empty.")
                 self.toolchest = {"tools": [], "mcp_protocols": []} # Ensure empty cache
        except json.JSONDecodeError as e:
             self.logger.error(f"Failed to decode toolchest JSON: {e}. Cache is empty.")
             self.toolchest = {"tools": [], "mcp_protocols": []}
        except Exception as e:
            self.logger.error(f"Failed loading toolchest cache: {e}", exc_info=True) # Log traceback
            self.toolchest = {"tools": [], "mcp_protocols": []}

    # --- V1 Methods Operating on the Cache ---
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """ Retrieves info for a specific tool from the IN-MEMORY CACHE. Case-insensitive. """
        tool_name_lower = tool_name.lower()
        # Search self.toolchest cache dictionary
        found_tool = next((tool for tool in self.toolchest.get("tools", [])
                           if isinstance(tool, dict) and tool.get("name", "").lower() == tool_name_lower), None)
        if found_tool:
            self.logger.debug(f"Found tool '{tool_name}' in cache.")
        else:
             self.logger.warning(f"Tool '{tool_name}' not found in cache.")
        return found_tool

    def list_tools_by_category(self, category: str) -> List[str]: # Return list of names
        """ Lists tool names from the IN-MEMORY CACHE by category. Case-insensitive. """
        category_lower = category.lower()
        # Filter self.toolchest cache dictionary
        matching_tools = [
            tool.get('name') for tool in self.toolchest.get("tools", [])
            if isinstance(tool, dict) and tool.get("mcp_category", "").lower() == category_lower and tool.get('name')
        ]
        self.logger.debug(f"Found {len(matching_tools)} tools for category '{category}' in cache.")
        return matching_tools

    # --- Future V2+ Method Placeholder ---
    async def request_research(self, query: str, project_context_path: str) -> Dict[str, Any]:
        # Logic from Day 52/97 goes here V2+
        self.logger.warning("request_research called on Lewis V1 - functionality planned for V2+.")
        return {"status": "skipped", "message": "Research requests require Lewis V2+"}

    # --- Run/Step ---
    # V1 uses the default BaseAgent V2 async run/step methods which log and handle state.
    # No need to override run unless specific Lewis V1 run logic is needed.
    # Provide the required step implementation.
    async def step(self, input_data: Optional[Any] = None) -> Any:
        """ V1: Lewis doesn't have specific step logic yet. Satisfies abstract method. """
        self.logger.debug(f"{self.name} V1 step called, no specific action defined.")
        # V1 Lewis likely remains IDLE unless specifically tasked
        # if self.state == AgentState.RUNNING: # Check state if needed
        #     self.state = AgentState.FINISHED
        return None

    # Inherited shutdown will save memory via BaseAgent V2

# Example Usage (for testing purposes, typically called from orchestration)
if __name__ == '__main__':
    # More robust workspace root detection
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        engine_dir = os.path.dirname(current_dir)
        workspace_root = os.path.dirname(engine_dir)
        if not os.path.basename(workspace_root).lower() == 'dreamerai':
             # Fallback if structure is different than expected
             workspace_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
             print(f"Warning: Workspace root detection might be inaccurate. Using: {workspace_root}")
    except NameError:
         workspace_root = "C:\\DreamerAI" # Hardcoded fallback if __file__ is not defined (e.g. interactive)
         print(f"Warning: Could not detect workspace root dynamically. Using fallback: {workspace_root}")

    tools_dir = os.path.join(workspace_root, 'tools')
    toolchest_file = os.path.join(tools_dir, 'toolchest.json')

    # Use the actual toolchest content if it exists, otherwise create a dummy one
    if not os.path.exists(toolchest_file):
        print(f"WARNING: {toolchest_file} not found. Creating dummy file for testing.")
        if not os.path.exists(tools_dir):
            try:
                os.makedirs(tools_dir)
            except OSError as e:
                 print(f"Error creating directory {tools_dir}: {e}. Testing might fail.")
                 # Decide if you want to proceed or exit
        try:
             with open(toolchest_file, 'w', encoding='utf-8') as f: # Added encoding
                 # Dummy structure matching expected format
                 json.dump({"tools": [{"name": "ExampleTool", "version": "1.0", "description": "A sample tool entry.", "mcp_category": "TestCategory"}], "mcp_protocols": []}, f, indent=4)
        except IOError as e:
             print(f"Error writing dummy toolchest file {toolchest_file}: {e}. Testing might fail.")

    async def test_lewis():
        # Instantiate Lewis - workspace_root is detected by BaseAgent
        print("\nInstantiating LewisAgent...")
        try:
            lewis = LewisAgent(workspace_root)
            print("LewisAgent instantiated successfully.")
        except Exception as e:
            print(f"ERROR: Failed to instantiate LewisAgent: {e}")
            return # Exit test if instantiation fails

        print("--- Testing Lewis Agent V1 --- (Requires tools/toolchest.json)")

        # Test listing tools
        print("\nTesting: List all tools...")
        list_result = await lewis.run(query="list")
        print("Result:", list_result)

        # Test listing tools by category
        print("\nTesting: List tools by category 'CoreTech'...")
        category_result = await lewis.run(category="CoreTech")
        print("Result:", category_result)

        print("\nTesting: List tools by category 'NonExistentCategory'...")
        category_result_missing = await lewis.run(category="NonExistentCategory")
        print("Result:", category_result_missing)

        # Test getting info for an existing tool
        print("\nTesting: Get info for tool 'Python'...")
        info_result_exists = await lewis.run(requested_tool="Python")
        print("Result:", info_result_exists)

        # Test getting info for a non-existent tool
        print("\nTesting: Get info for tool 'MissingTool'...")
        info_result_missing = await lewis.run(requested_tool="MissingTool")
        print("Result:", info_result_missing)

        # Test idle state
        print("\nTesting: Idle run (no query)...")
        idle_result = await lewis.run()
        print("Result:", idle_result)
        print("--- Lewis Agent V1 Tests Complete ---")

    # Run the async test function
    asyncio.run(test_lewis()) 