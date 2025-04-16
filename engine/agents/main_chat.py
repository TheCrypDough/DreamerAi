# C:\DreamerAI\engine\agents\main_chat.py
# Placeholder for Jeff (Main Chat) Agent
# Implementation details to follow on Day 8.

# from .base import BaseAgent # Will inherit later
# class MainChatAgent(BaseAgent):
#     pass 

import asyncio
import os
import traceback
import json
from typing import Optional, Any, Dict, List
from pathlib import Path
import sys # Import sys module
from pydantic import PrivateAttr # Import PrivateAttr

# Core Imports (Leveraging BaseAgent V2)
try:
    # Add project root to sys.path if necessary (should be handled globally but good practice)
    project_root_mc = Path(__file__).resolve().parent.parent.parent
    if str(project_root_mc) not in sys.path:
        sys.path.insert(0, str(project_root_mc))
        
    from engine.agents.base import BaseAgent, AgentState, Message # Use V2 BaseAgent
    from engine.core.logger import logger_instance as logger, log_rules_check
    # Temporarily comment out event manager import as it doesn't exist yet (Day 62)
    # from engine.core.event_manager import event_manager 
    # EVENT_MANAGER_AVAILABLE = True
    EVENT_MANAGER_AVAILABLE = False # Assume not available for now
    # LLM import for type hint
    from engine.ai.llm import LLM 
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    # Log the original import error more clearly
    logger.error(f"Jeff V1 Critical Error: Could not import core dependencies (BaseAgent, logger, event_manager?): {e}", exc_info=True)
    # Define Dummy classes if core imports fail
    class BaseAgent: 
        def __init__(self, *args, **kwargs): pass # Basic init for super()
    class AgentState: IDLE, RUNNING, FINISHED, ERROR = 0, 1, 2, 3
    class Message: pass
    def log_rules_check(msg): pass
    # Dummy event manager
    class event_manager:
        @staticmethod
        async def publish(*args, **kwargs): pass
    EVENT_MANAGER_AVAILABLE = False
    LLM = type(None) # Dummy type for Optional hint if import fails

# n8n/Comms Imports
try:
    import aiohttp # For functional n8n call
    from engine.ai.llm import CONFIG # For n8n config
except ImportError:
    aiohttp = None; CONFIG = {}; 
    logger.error("Jeff V1 Error: Cannot import aiohttp/CONFIG. n8n trigger disabled.")

class ChefJeff(BaseAgent):
    """ V1: Chat, uses BaseAgent V2 (ChromaDB RAG), functional n8n handoff, progress sim. """
    _llm: Optional[LLM] = PrivateAttr(default=None)

    def __init__(self, user_dir: str, **kwargs):
        try:
            # Initialize BaseAgent first
            super().__init__(name="Jeff", user_dir=user_dir, **kwargs) # Removed distill=False for now if Base V1
            self.logger.info(f"BaseAgent initialized for {self.name}.")

            # Explicitly initialize LLM and assign to private attribute
            try:
                from engine.ai.llm import LLM # Re-import locally if needed
                self._llm = LLM()
                if self._llm:
                    self.logger.info(f"{self.name} V1 explicitly initialized LLM instance.")
                else:
                     # This case shouldn't happen if LLM() returns instance or raises
                     self.logger.error(f"{self.name} V1 failed to initialize LLM instance (returned None).") 
            except Exception as e:
                self.logger.error(f"{self.name} V1 failed during explicit LLM initialization: {e}", exc_info=True)
                self._llm = None # Ensure it's None on error

        except TypeError as e:
             logger.error(f"TypeError during super().__init__ in ChefJeff: {e}. Is BaseAgent import failing?", exc_info=True)
             self.name = "Jeff"
             self.user_dir = user_dir
             self.logger = logger 
             self._state = AgentState.ERROR 
             self._llm = None 
             self.rules_content = None
             self.memory = None
        
        logger.info(f"ChefJeff Agent '{self.name}' V1 Initialized.") # Simplified log message

    # Remove _load_rules, _retrieve_rag_context - Handled by BaseAgent V2 via self.rules_content, self.query_rag

    async def route_tasks_n8n(self, task_description: str, project_id="TODO_ProjID_Jeff"):
        """ V1 Functional Handoff (Uses Day 33 logic - Assumed functional) """
        # Uses self.logger from BaseAgent
        self.logger.info(f"HANDOFF V1 (Jeff -> n8n): Task='{task_description[:50]}' Project='{project_id}'")
        log_rules_check(f"Jeff triggering n8n handoff") # Adhere to rules check
        webhook_url = CONFIG.get('n8n',{}).get('task_webhook_url')
        auth_token = CONFIG.get('n8n',{}).get('auth_token')
        if not webhook_url or not aiohttp: 
            self.logger.error("n8n webhook URL or aiohttp missing."); 
            return False
        payload = {"task_description": task_description, "source": self.name, "project_id": project_id}
        headers = {'Content-Type': 'application/json'}
        if auth_token: headers['X-N8N-API-KEY'] = auth_token # Adjust header if needed

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                 async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if 200 <= response.status < 300: 
                        self.logger.info("n8n workflow triggered."); 
                        return True
                    else: 
                        self.logger.error(f"n8n trigger failed: {response.status}"); 
                        return False
        except Exception as e: 
            self.logger.exception("n8n call failed"); 
            return False

    async def simulate_downstream_progress(self, task_description: str):
        """ V1 Progress Sim (Uses Day 73 logic) - Event Manager potentially unavailable """
        self.logger.info(f"Jeff V1 starting progress broadcast simulation for task: {task_description[:30]}...")
        if not EVENT_MANAGER_AVAILABLE: 
            self.logger.warning("Event Manager not available, skipping progress simulation.")
            return 
        steps = [("Planning", 15), ("Building Code", 40), ("Testing (Sim)", 75), ("Docs (Sim)", 90), ("Ready (Sim)", 100)]
        try: # Wrap publish calls
            for step_name, percent in steps:
                await asyncio.sleep(0.5) # Slightly shorter delay V1 maybe
                self.logger.debug(f"Simulating progress: {step_name} - {percent}%")
                # Comment out the actual publish call
                # await event_manager.publish(
                #     "agent.workflow.progress",
                #     {"step": step_name, "percent": percent, "detail": f"{step_name} phase started..."}
                # )
            self.logger.info("Jeff V1 progress simulation finished (events commented out).")
        except Exception as e: self.logger.error(f"Error during progress simulation: {e}")

    async def run(self, user_input: Optional[str] = None) -> Any: # Keep run structure similar to Day 73
        # Use direct state assignment for now, assuming BaseAgent setter might rely on events
        self._state = AgentState.RUNNING 
        self.logger.info(f"'{self.name}' V1 starting interaction run (using BaseAgent V2 logic). State: {self._state}")
        final_response_content = "Error: Jeff V1 processing failed."
        task_identified = False
        task_description = ""
        response_content = ""

        # 1. Get Input & Update Memory (BaseAgent V2 handles load, use add_message)
        if user_input is None: 
            user_input = self.memory.messages[-1].content if hasattr(self, 'memory') and self.memory and self.memory.messages else None; # Get last user msg, check memory exists
        if user_input is None: 
            self.logger.error("No user input provided or found in memory.")
            self._state=AgentState.ERROR; 
            return {"error": "No input provided."}
        
        # Ensure memory object exists before adding message
        if not hasattr(self, 'memory') or self.memory is None:
             self.logger.error("Memory object not initialized in BaseAgent.")
             self._state=AgentState.ERROR; 
             return {"error": "Memory system unavailable."}
        self.memory.add_message({"role": "user", "content": user_input})

        try:
            # 2. Access Rules (BaseAgent) & Query RAG (BaseAgent V2 - ChromaDB)
            rules = self.rules_content if hasattr(self, 'rules_content') else "Be helpful and informative." 
            self.logger.info("Querying RAG via BaseAgent V2...") # Added log for verification
            # Ensure query_rag method exists
            if not hasattr(self, 'query_rag') or not callable(self.query_rag):
                self.logger.error("query_rag method not available in BaseAgent.")
                rag_context = []
            else:
                rag_context = await self.query_rag(user_input, n_results=3) # Use BaseAgent V2 helper
            
            rag_str = "\n".join([f"- {r}" for r in rag_context]) if rag_context else "No specific background info found."
            self.logger.debug(f"RAG context found: {rag_str[:100]}...")

            # 3. Prepare Enhanced Prompt V1 (Simpler than V2)
            # Ensure get_history exists
            history_list = self.memory.get_history() if hasattr(self.memory, 'get_history') else []
            history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history_list[-4:]]) 
            prompt = f"""**Role:** Jeff, friendly DreamerAI assistant. Rules: {rules[:150]}...
            **Background Info:** {rag_str[:400]}
            **Chat History:** {history_str}
            **User Said:** {user_input}
            **Task:** Respond conversationally. Identify if user wants to *start building* something (build, create, plan, make etc.). If so, acknowledge you'll start the process.
            **Output:** Your conversational response only.
            """
            self.logger.debug(f"LLM Prompt prepared (first 100): {prompt[:100]}...")

            # 4. Generate Response (Use _llm)
            if not self._llm: raise Exception("LLM unavailable") # Check private attribute
            response_content = await self._llm.generate(prompt, agent_name=self.name)
            if response_content.startswith("ERROR:"): raise Exception(f"LLM Error: {response_content}")
            self.memory.add_message({"role": "assistant", "content": response_content})
            final_response_content = response_content # Store successful response

            # --- Send Immediate Chat Response (Bridge D13 via BaseAgent V2 send_update_to_ui) ---
            # Temporarily comment out bridge call
            # await self.send_update_to_ui(response_content, update_type="chat_response")
            self.logger.info("Jeff V1 generated response (UI bridge call commented out).")
            # -----------------------------------------------------------------------------------

            # 5. Identify Task & Trigger Handoff/Progress Sim (Keep V1 keyword logic)
            task_keywords = ["build", "create", "plan", "generate", "make", "develop", "code"]
            user_input_lower = user_input.lower()
            if any(keyword in user_input_lower for keyword in task_keywords):
                 task_description = user_input # Simple V1: use whole input
                 task_identified = True

            if task_identified:
                 self.logger.info(f"Task identified. Triggering n8n handoff & progress sim...")
                 # Comment out event manager publish for handoff start
                 # if EVENT_MANAGER_AVAILABLE: await event_manager.publish("agent.workflow.progress", {"step": "Task Handoff", "percent": 5})
                 success = await self.route_tasks_n8n(task_description)
                 if success: await self.simulate_downstream_progress(task_description)
                 else: self.logger.error("Task handoff to n8n failed!")

            # 6. Final State
            self._state = AgentState.FINISHED 
            self.logger.info(f"Jeff V1 run finished. State: {self._state}")

        except Exception as e:
            self._state = AgentState.ERROR 
            final_response_content = f"Jeff V1 Error: {e}"
            self.logger.exception(f"Error during Jeff V1 run")
            # Send error via bridge (commented out)
            # try:
            #      await self.send_update_to_ui(final_response_content, "error")
            # except Exception as send_err:
            #      self.logger.error(f"Failed to send error update to UI: {send_err}")

        finally:
            # State transition (FINISHED -> IDLE or ERROR -> IDLE)
            final_state = self._state # Access current state before changing
            self._state = AgentState.IDLE 
            self.logger.info(f"'{self.name}' V1 interaction run finished. State transition: {final_state} -> {self._state}")

        # Return conversational response OR error dict
        return final_response_content if final_state != AgentState.ERROR else {"error": final_response_content}

    async def step(self, input_data: Optional[Any] = None) -> Any:
        # Basic step V1 delegates to run
        self.logger.debug(f"{self.name} step called, delegating to run...")
        if isinstance(input_data, str):
            return await self.run(user_input=input_data)
        # Handle case where step might be called without suitable input e.g. from default BaseAgent run loop
        return await self.run() # Attempt run without new input (might use memory)

    # Remove BaseAgent methods if Jeff was overriding them (unlikely V1)
    # e.g., remove _load_rules, _retrieve_rag_context if they existed here

# --- Test Block for ChefJeff V1 ---
if __name__ == "__main__":
    import asyncio
    from pathlib import Path
    import time

    async def test_jeff_v1():
        print("--- Testing ChefJeff V1 --- Lvl 0")
        # Ensure a test user directory exists
        project_root_test = Path(__file__).resolve().parent.parent.parent
        test_user_dir = project_root_test / "Users" / "test_jeff_user"
        test_user_dir.mkdir(parents=True, exist_ok=True)
        print(f"Using test user directory: {test_user_dir}")

        # Check prerequisites (Config files for LLM/BaseAgent)
        config_path = project_root_test / "data" / "config" / "config.dev.toml"
        env_path = project_root_test / "data" / "config" / ".env.development"
        if not config_path.exists() or not env_path.exists():
            print("ERROR: config.dev.toml or .env.development not found. Cannot proceed.")
            return
            
        print("NOTE: This test assumes BaseAgent V2 is correctly implemented and functional.")
        print("Requires backend server (for bridge comms - Day 13+) and n8n (for handoff - Day 33+) to be running for full functionality testing.")
        print("Requires Ollama server to be running manually.")
        print("Requires RAG DB to be seeded (Day 8 Task 2 completed).")

        agent = None # Define agent outside try block
        try:
            # Instantiate ChefJeff
            # BaseAgent V2 handles LLM, RAG init based on name="Jeff"
            agent = ChefJeff(user_dir=str(test_user_dir))
            print(f"Agent '{agent.name}' V1 initialized.")

            # Check _llm private attribute
            if not agent._llm:
                 print("ERROR: LLM module (_llm) not set in BaseAgent __init__.")
                 return
            print("LLM instance (_llm) seems set by BaseAgent.")
            # RAG check remains conceptual unless BaseAgent exposes it
            print("RAG assumed initialized by BaseAgent.")

            # --- Test 1: Input triggering RAG and Task Handoff --- 
            print("\n--- Test 1: Sending message to trigger RAG & Handoff ---")
            test_input_1 = "What is the role of the Nexus agent? Then please plan a cool new game."
            print(f"User Input: {test_input_1}")
            
            response_1 = await agent.run(user_input=test_input_1)
            print(f"\nJeff V1 Response:")
            if isinstance(response_1, dict) and 'error' in response_1:
                 print(f"  ERROR: {response_1['error']}")
            else:
                 print(f"  Content: {response_1}")

            print("\n--- Verification Steps --- ")
            print("1. Check logs above for 'Querying RAG via BaseAgent V2...'")
            print("2. Check logs for successful LLM generation.")
            print("3. Check logs for 'HANDOFF V1 (Jeff -> n8n)...'.")
            print("4. Check logs for 'progress broadcast simulation...'.")
            print("5. If n8n is running, check its execution log for received webhook.")
            print("6. If backend server/bridge is running, check UI/console for chat response & Dream Theatre updates.")
            
            # --- Test 2: Follow-up message (Simple conversation) ---
            print("\n--- Test 2: Sending follow-up message ---")
            test_input_2 = "Thanks Jeff!"
            print(f"User Input: {test_input_2}")
            response_2 = await agent.run(user_input=test_input_2)
            print(f"\nJeff V1 Response:")
            if isinstance(response_2, dict) and 'error' in response_2:
                 print(f"  ERROR: {response_2['error']}")
            else:
                 print(f"  Content: {response_2}")
            print("(Expect no RAG query/handoff for this simple message)")
            
        except Exception as e:
            print(f"\n--- ERROR during Jeff V1 test execution --- ")
            print(f"Error: {e}")
            traceback.print_exc()
        # finally:
             # Optional: Add cleanup if needed (e.g., delete test user dir)
             # if agent and agent.user_dir_path.exists():
             #      # Add cleanup logic - careful with shutil.rmtree
             #      pass 
        
        print("\n--- ChefJeff V1 Test Finished ---")

    # Run the async test function
    asyncio.run(test_jeff_v1()) 