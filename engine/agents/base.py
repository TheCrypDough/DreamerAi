# C:\DreamerAI\engine\agents\base.py (COMPLETE REPLACEMENT - Verified ChromaDB/ST - Day 72 Implementation)
import asyncio
import os
import json
import traceback
import uuid # For generating unique RAG IDs
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union, Callable # Added Callable
from pydantic import BaseModel, Field, ValidationError, parse_obj_as, PrivateAttr, model_validator
from pathlib import Path
import importlib # For dynamic imports if needed later

# Add project root for sibling imports
import sys
project_root_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_base not in sys.path: sys.path.insert(0, project_root_base)

# --- Core Imports (Logger, EventManager) ---
# Attempt imports, provide dummies if they fail to allow module loading
try:
    from engine.core.logger import logger_instance as logger, log_rules_check
except ImportError:
    import logging
    logger = logging.getLogger("base_agent_fallback")
    def log_rules_check(action: str): logger.debug(f"Fallback Rules Check: {action}")
    logger.warning("BaseAgent: Custom logger not found, using basic logging.")

try:
    from engine.core.event_manager import event_manager
    EVENT_MANAGER_AVAILABLE = True
except ImportError:
    EVENT_MANAGER_AVAILABLE = False
    # Dummy EventManager for fallback
    class DummyEventManager:
        async def publish(self, *args, **kwargs): pass
        def subscribe(self, *args, **kwargs): pass
        def unsubscribe(self, *args, **kwargs): pass
    event_manager = DummyEventManager()
    logger.warning("BaseAgent: EventManager not found, event publishing disabled.")


# --- RAG Imports (ChromaDB/ST) ---
RAG_LIBS_OK = False
chromadb = None
SentenceTransformer = None
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    RAG_LIBS_OK = True
    logger.debug("BaseAgent: ChromaDB and SentenceTransformers libraries loaded.")
except ImportError as e:
    logger.warning(f"BaseAgent: RAG libs (chromadb, sentence-transformers) not found: {e}. RAG features disabled.")


# --- LLM Import ---
LLM = None
CONFIG = {}
try:
    # Attempt to import CONFIG as well if needed by LLM init
    from engine.ai.llm import LLM, CONFIG
except ImportError:
    logger.error("BaseAgent: Cannot import LLM class from engine.ai.llm.")


# --- Data Models ---
class Message(BaseModel):
    """ Represents a single message in memory or communication. """
    role: str # e.g., "user", "assistant", "system", "user_raw", "assistant_refined"
    content: str

    class Config:
        extra = 'allow' # Allow extra fields if needed later

class Memory(BaseModel):
    """ Manages conversation history for an agent. """
    messages: List[Message] = Field(default_factory=list)
    max_history: int = 50

    def add_message(self, msg: Union[Message, Dict]):
        """ Adds a message (dict or Message object) to history, enforcing max length. """
        if not isinstance(msg, Message):
            try:
                # Attempt to create Message if dict is passed, allow extra fields V1 simple
                msg = Message(**msg)
            except ValidationError as e:
                logger.error(f"Memory Error: Invalid message format: {msg}. Error: {e}")
                return
            except Exception as e:
                 logger.error(f"Memory Error: Failed to create Message from dict: {msg}. Error: {e}")
                 return

        self.messages.append(msg)
        # Trim history if it exceeds max length
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        # logger.debug(f"Message added. Memory size: {len(self.messages)}")

    def get_history(self) -> List[Dict]:
        """ Returns the message history as a list of dictionaries. """
        return [msg.dict() for msg in self.messages]

    def load_history(self, history_list: List[Dict]):
        """ Loads history from a list of dictionaries, handling potential errors. """
        loaded_messages = []
        for i, item in enumerate(history_list):
             try:
                 loaded_messages.append(Message(**item))
             except ValidationError as e:
                 logger.error(f"Memory Load Error: Skipping invalid message at index {i}. Data: {item}. Error: {e}")
             except Exception as e:
                 logger.error(f"Memory Load Error: Skipping message at index {i} due to unexpected error: {e}. Data: {item}.")

        # Apply max history limit *after* loading valid messages
        self.messages = loaded_messages[-self.max_history:]
        logger.debug(f"Memory loaded {len(self.messages)} valid messages (max: {self.max_history}).")

    def get_last_message_content(self, role_filter: Optional[str] = None) -> Optional[str]:
        """ Gets the content of the last message, optionally filtering by role. """
        relevant_messages = self.messages
        if role_filter:
            relevant_messages = [m for m in self.messages if m.role == role_filter]
        return relevant_messages[-1].content if relevant_messages else None


class AgentState:
    """ Defines possible states for an agent. """
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished" # Task completed successfully
    ERROR = "error"     # Task failed due to internal error
    WAITING_USER = "waiting_user" # Waiting for user input
    WAITING_SUBAGENT = "waiting_subagent" # Waiting for another agent


# --- Base Agent V2 Class ---
class BaseAgent(BaseModel, ABC):
    """
    V2: Abstract Base Class with integrated foundational components:
    - Rules Loading (`self.rules_content`)
    - Memory Persistence (`self.memory`, save/load to JSON)
    - ChromaDB/SentenceTransformer RAG (`self.query_rag`, `self.store_in_rag`)
    - State Management with Event Publishing (`self.state` property)
    - Configurable LLM Access (`self.llm`)
    - Basic Run Loop and Shutdown Hook
    - Standardized Paths
    - Logger per instance
    """
    # --- Core Identification ---
    name: str = Field(..., description="Unique name of the agent")
    user_dir: str = Field(..., description="Path to the user's base workspace directory")
    project_context_path: Optional[Path] = Field(default=None, description="Path to the specific project context directory, if applicable")

    # --- Configuration ---
    distill: bool = Field(default=False, description="Flag indicating if distilled model should be preferred (Placeholder V1)") # Default False V1
    max_steps: int = Field(default=20, description="Maximum steps for the default run loop")

    # --- Core Components (Managed Internally) ---
    memory: Memory = Field(default_factory=Memory)
    rules_content: Optional[str] = Field(default=None, exclude=True) # Loaded from rules file
    llm: Optional[LLM] = Field(default=None, exclude=True) # LLM instance

    # --- Internal State & Helpers (PrivateAttr prevents inclusion in model dump/validation) ---
    _state: str = PrivateAttr(default=AgentState.IDLE)
    _logger: Any = PrivateAttr(default=None) # Logger instance assigned in __init__
    _rag_initialized: bool = PrivateAttr(default=False)
    _rag_client: Optional[Any] = PrivateAttr(default=None) # ChromaDB Client
    _rag_collection: Optional[Any] = PrivateAttr(default=None) # ChromaDB Collection
    _st_model: Optional[Any] = PrivateAttr(default=None) # Sentence Transformer Model

    # --- File Paths (PrivateAttr - derived, not configured directly) ---
    _agent_base_dir: Optional[Path] = PrivateAttr(default=None)
    _agent_chat_dir: Optional[Path] = PrivateAttr(default=None)
    _rules_file_path: Optional[Path] = PrivateAttr(default=None)
    _memory_file_path: Optional[Path] = PrivateAttr(default=None)
    _rag_db_path: Optional[Path] = PrivateAttr(default=None) # Directory path for ChromaDB

    class Config:
        arbitrary_types_allowed = True # Allow types like Logger, LLM instance

    # --- Initialization & Setup ---
    def __init__(self, **data: Any):
        """ Initializes BaseAgent, sets up paths, loads components. """
        super().__init__(**data)
        self._logger = logger.bind(agent_name=self.name) # Bind logger immediately
        self._setup_paths()
        self._ensure_directories()
        self._load_rules()
        self._initialize_rag_db()
        self._load_memory_from_disk()
        self._initialize_llm() # Initialize LLM *after* config might be available?
        self._logger.info(f"Agent '{self.name}' V2 Initialized. RAG OK: {self._rag_initialized}. Mem Msgs: {len(self.memory.messages)}.")

    def _setup_paths(self):
        """ Sets up standard file/directory paths based on name and user_dir. """
        try:
            self._agent_base_dir = Path(self.user_dir) # Base user workspace path
            self._agent_chat_dir = self._agent_base_dir / "Chats" / self.name
            # Rules are central in V1/V2
            self._rules_file_path = Path(project_root_base) / "engine" / "agents" / f"rules_{self.name.lower()}.md"
            self._memory_file_path = self._agent_chat_dir / "memory.json"
            # RAG DB path is a DIRECTORY for ChromaDB persistence
            self._rag_db_path = Path(project_root_base) / "data" / "rag_dbs" / f"rag_{self.name.lower()}.db"
            # Project context path is passed in, not derived here typically
            # self.project_context_path might be updated by orchestrator/caller
        except Exception as e:
            self._logger.error(f"Error setting up paths: {e}")

    def _ensure_directories(self):
        """ Creates necessary directories if they don't exist. """
        try:
            if self._agent_chat_dir: self._agent_chat_dir.mkdir(parents=True, exist_ok=True)
            if self._rag_db_path: self._rag_db_path.parent.mkdir(parents=True, exist_ok=True) # Ensure parent data/rag_dbs exists
        except OSError as e:
            self._logger.error(f"Failed creating agent directories: {e}")

    @property
    def logger(self) -> Any:
        """ Provides access to the bound logger instance. """
        # Returns fallback logger if custom one failed during init
        return self._logger or logging.getLogger(self.name)

    @property
    def state(self) -> str: return self._state
    @state.setter
    def state(self, value: str):
        """ Sets the state and publishes an event if changed via EventManager. """
        if value not in vars(AgentState).values(): # Basic validation
             self.logger.error(f"Invalid state value assigned: {value}")
             return
        if value != self._state:
            self.logger.trace(f"State Change: {self._state} -> {value}")
            old_state = self._state; self._state = value
            if EVENT_MANAGER_AVAILABLE:
                payload = {"agent": self.name, "status": self._state, "previous": old_state}
                # Fire-and-forget publish V1
                asyncio.create_task(event_manager.publish("agent.status.changed", payload))
            else:
                self.logger.warning("Event Manager unavailable, cannot publish state change.")

    def _initialize_llm(self):
        """ Initializes the LLM instance. V1 uses global config implicitly. """
        if self.llm: return # Allow injection V2+
        if not LLM: self.logger.error("LLM Class not available!"); return
        try:
            # V1: Assumes LLM() constructor reads global CONFIG or uses defaults.
            # V2+: DI container would provide configured instance.
            self.llm = LLM()
            self.logger.debug("LLM instance initialized via BaseAgent.")
        except Exception as e:
            self.logger.error(f"LLM init failed in BaseAgent: {e}")
            self.llm = None

    def _load_rules(self):
        """ Loads agent-specific rules from markdown file into self.rules_content. """
        log_rules_check(f"Loading rules for {self.name}") # Use global check function
        if not self._rules_file_path: self.logger.error("Rules file path not set."); return
        try:
            if self._rules_file_path.is_file():
                 self.rules_content = self._rules_file_path.read_text(encoding='utf-8')
                 self.logger.debug(f"Rules loaded successfully from {self._rules_file_path}.")
            else: self.logger.warning(f"Rules file not found: {self._rules_file_path}."); self.rules_content = None
        except Exception as e:
             self.logger.error(f"Failed loading rules from {self._rules_file_path}: {e}")
             self.rules_content = f"# ERROR LOADING RULES: {e}"

    def _initialize_rag_db(self):
        """ V2: Initializes ChromaDB Client, Collection, and SentenceTransformer Model. """
        if not RAG_LIBS_OK:
             self.logger.warning("RAG Libraries not available, skipping RAG init.")
             self._rag_initialized = False; return
        if not self._rag_db_path:
            self.logger.error("RAG DB path not set, cannot initialize RAG.")
            self._rag_initialized = False; return

        self.logger.debug(f"Initializing RAG V2 (ChromaDB/ST) using path: {self._rag_db_path}")
        try:
            # --- Embedding Model ---
            model_name = 'all-MiniLM-L6-v2' # Default V1
            # TODO V2: Make model configurable via main config.toml?
            self.logger.debug(f"Loading Sentence Transformer model: {model_name}...")
            self._st_model = SentenceTransformer(model_name)
            self.logger.info(f"SentenceTransformer model '{model_name}' loaded.")

            # --- ChromaDB Client & Collection ---
            # PersistentClient uses the specified directory to store DB files
            self.logger.debug(f"Connecting ChromaDB PersistentClient at: {self._rag_db_path}")
            self._rag_client = chromadb.PersistentClient(path=str(self._rag_db_path))
            collection_name = f"{self.name.lower()}_v2_collection" # More specific name
            self.logger.debug(f"Getting/Creating ChromaDB collection: '{collection_name}'")
            # Get or create the collection. Use default embedding function handling or specify.
            # For stability, explicitly using the loaded ST model is often better.
            # Create embedding function instance for ChromaDB
            from chromadb.utils import embedding_functions
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

            self._rag_collection = self._rag_client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function # Explicitly pass embedding function
                # metadata={"hnsw:space": "cosine"} # Example metadata if needed
            )
            self.logger.info(f"ChromaDB client connected, using collection '{collection_name}'. Items: {self._rag_collection.count()}")
            self._rag_initialized = True

        except Exception as e:
             self.logger.exception(f"BaseAgent failed to initialize RAG components")
             self._rag_client = None; self._rag_collection = None; self._st_model = None
             self._rag_initialized = False

    def _load_memory_from_disk(self):
        """ Loads conversation history from agent's memory file into self.memory. """
        self.memory = Memory() # Ensure fresh memory object
        if not self._memory_file_path: logger.error("Memory file path not set."); return
        if self._memory_file_path.is_file():
            self.logger.debug(f"Loading memory from {self._memory_file_path}...")
            try:
                 memory_json = self._memory_file_path.read_text(encoding='utf-8')
                 # Add check for empty file
                 if not memory_json.strip():
                      self.logger.warning("Memory file is empty. Starting fresh.")
                      return
                 history_list = json.loads(memory_json)
                 self.memory.load_history(history_list) # Use pydantic model loader
                 self.logger.info(f"Loaded {len(self.memory.messages)} messages from disk.")
            except json.JSONDecodeError as e:
                 self.logger.error(f"Failed parsing memory file {self._memory_file_path}: {e}. Starting fresh memory.")
                 self.memory = Memory() # Reset on parse failure
            except Exception as e:
                 self.logger.error(f"Failed loading memory from {self._memory_file_path}: {e}. Starting fresh memory.")
                 self.memory = Memory()
        else:
            self.logger.info(f"No prior memory file found at {self._memory_file_path}. Starting fresh memory.")

    def _save_memory_to_disk(self):
        """ Saves current conversation history (self.memory) to agent's memory file. """
        if not self._memory_file_path: logger.warning("Memory file path not set, cannot save."); return
        if not self.memory or not self.memory.messages: logger.debug("No memory content to save."); return

        self.logger.debug(f"Saving memory ({len(self.memory.messages)} messages) to {self._memory_file_path}...")
        try:
             memory_list = self.memory.get_history()
             # Ensure directory exists just before writing
             self._agent_chat_dir.mkdir(parents=True, exist_ok=True)
             # Write atomically? V1 simple write.
             with open(self._memory_file_path, 'w', encoding='utf-8') as f:
                 json.dump(memory_list, f, indent=2)
             self.logger.debug("Memory saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save memory to {self._memory_file_path}: {e}")


    async def query_rag(self, query: str, n_results: int = 3, filter_metadata: Optional[Dict]=None) -> List[str]:
        """ V2: Queries agent's ChromaDB collection using SentenceTransformer embeddings. """
        if not self._rag_initialized or not self._rag_collection or not self._st_model:
            self.logger.warning("RAG query skipped: RAG components not initialized.")
            return []

        self.logger.debug(f"Querying RAG (Collection: {self._rag_collection.name}): '{query[:50]}...'" )
        try:
            query = str(query) # Ensure string
            # Embed query (Sync model encode in thread)
            loop = asyncio.get_running_loop()
            # SentenceTransformer encode returns list of embeddings (even for single query)
            query_embedding_list = await loop.run_in_executor(None, lambda: self._st_model.encode([query]).tolist())
            if not query_embedding_list:
                 raise ValueError("Embedding generation failed.")
            query_embedding = query_embedding_list[0] # Get the single embedding

            # Perform ChromaDB query
            results = self._rag_collection.query(
                query_embeddings=[query_embedding], # Chroma expects list of embeddings
                n_results=n_results,
                where=filter_metadata, # Optional metadata filter e.g., {"source": "rules"}
                include=['documents'] # Only fetch documents V1
                )

            documents = results.get('documents', [[]])[0] # Structure is [[doc1, doc2]]
            self.logger.debug(f"RAG Query V2 returned {len(documents)} documents.")
            return documents if documents else []
        except Exception as e:
            self.logger.exception(f"RAG query failed")
            return []

    async def store_in_rag(self, documents: List[str], ids: Optional[List[str]] = None, metadatas: Optional[List[dict]] = None):
        """ V2: Stores documents (with optional IDs/metadata) in agent's ChromaDB collection. """
        if not self._rag_initialized or not self._rag_collection or not self._st_model:
            self.logger.warning("RAG store skipped: RAG components not initialized.")
            return False
        if not documents: logger.warning("RAG store skipped: No documents provided."); return True

        self.logger.debug(f"Storing {len(documents)} document(s) in RAG (Collection: {self._rag_collection.name})...")
        try:
            # Generate unique IDs if not provided
            effective_ids = ids or [str(uuid.uuid4()) for _ in documents]
            if len(effective_ids) != len(documents): raise ValueError("Mismatch between document count and ID count.")

            # Embed documents (Sync model encode in thread)
            loop = asyncio.get_running_loop()
            embeddings = await loop.run_in_executor(None, lambda: self._st_model.encode(documents).tolist())
            if len(embeddings) != len(documents): raise ValueError("Embedding generation count mismatch.")

            # Add to collection (Use upsert to handle potential ID conflicts gracefully)
            self._rag_collection.upsert(
                ids=effective_ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas # Optional metadata
            )
            self.logger.info(f"Stored/Upserted {len(documents)} document(s) in RAG collection '{self._rag_collection.name}'. New Count: {self._rag_collection.count()}")
            return True
        except Exception as e:
            self.logger.exception(f"RAG store/upsert failed")
            return False

    @abstractmethod
    async def step(self, input_data: Optional[Any] = None) -> Any:
        """
        Perform a single step of the agent's core logic.
        Must be implemented by subclasses.
        Should return results or signal completion/state change.
        Input format depends on the agent's design (e.g., last message, full history, specific dict).
        """
        pass

    async def run(self, initial_input: Optional[Any] = None) -> Any:
        """
        Default run loop: Executes the 'step' method repeatedly until max_steps
        or a terminal state (FINISHED, ERROR) is reached. Manages state transitions
        and basic error handling. Publishes state change events.
        """
        # Check if already running maybe? Add reentrancy lock V2+?
        original_state = self.state # Store original state if restarting
        self.state = AgentState.RUNNING # Setter publishes event
        if self.state != AgentState.RUNNING: self.logger.warning("State transition to RUNNING failed?"); # Should not happen

        self.logger.info(f"Agent '{self.name}' V2 starting run...")
        if initial_input:
            self.memory.add_message({"role": "user", "content": str(initial_input)})

        results = []; current_step = 0; last_result = None
        try:
            while self.state == AgentState.RUNNING and current_step < self.max_steps:
                current_step += 1
                self.logger.debug(f"Executing step {current_step}/{self.max_steps}")
                # Pass relevant context to step - V1 simple: pass last message content? Or full history?
                # Subclass step implementation dictates what it expects. Pass history dict V1 simple.
                step_input_ctx = self.memory.get_history()
                last_result = await self.step(step_input_ctx)
                results.append(last_result) # Store step results if needed

                # State Check: The step method SHOULD ideally set the agent's state
                # (e.g., self.state = AgentState.FINISHED). This loop relies on that.
                if self.state != AgentState.RUNNING:
                     self.logger.info(f"Run loop exiting due to state change to '{self.state}' at step {current_step}.")
                     break

            # If loop finished due to max_steps while still RUNNING
            if self.state == AgentState.RUNNING:
                 self.logger.warning(f"Run finished due to max_steps ({self.max_steps}) reached.")
                 self.state = AgentState.FINISHED # Set state to Finished via setter (publishes event)

        except Exception as e:
            self.logger.exception("Unhandled error during agent run loop")
            self.state = AgentState.ERROR # Publishes event
            last_result = {"error": f"Agent run failed: {e}"} # Ensure error propagates

        finally:
            # Final state logging and potential reset
            final_run_state = self._state # Get current state value directly
            # Reset to IDLE only if the final state wasn't ERROR
            if final_run_state == AgentState.FINISHED:
                 self.state = AgentState.IDLE # Let setter publish final transition to IDLE
            self.logger.info(f"Agent '{self.name}' run finished. Final internal state: {self.state}")

        # Return the result of the last successful step, or error info
        return last_result


    async def shutdown(self):
        """ Performs cleanup, including saving memory state. """
        self.logger.info(f"Agent '{self.name}' V2 shutting down...");
        self._save_memory_to_disk();
        # Add other specific agent cleanup here if needed by subclasses (super().shutdown())
        self.logger.info(f"Agent '{self.name}' V2 shutdown complete.");

    async def send_update_to_ui(self, content: Any, update_type: str):
        """ V1: Sends an update payload to the UI listener via the bridge (Day 13). """
        # Assumes bridge module is available and functional
        try:
            # Use dynamic import maybe? Or ensure loaded at startup
            from engine.core.bridge import send_to_ui
            payload = {
                "agent": self.name,
                "type": update_type,
                "payload": content # Content can be string, dict, list etc.
            }
            self.logger.debug(f"Sending UI update: Type='{update_type}' -> Payload='{str(content)[:100]}...'" )
            # Fire-and-forget V1 - does not wait for UI acknowledgment
            asyncio.create_task(send_to_ui(payload))
        except ImportError:
            self.logger.error("engine.core.bridge not found, cannot send UI update.")
        except Exception as e:
            self.logger.error(f"Failed sending UI update via bridge: {e}")


# --- V2 Test Block ---
if __name__ == "__main__":
    # Dummy derived class for testing BaseAgent functionality
    class TestV2Agent(BaseAgent):
        async def step(self, input_data: Optional[Any] = None) -> Any:
            """ Simple step for testing RAG and memory. """
            self.logger.info("TestV2Agent step executing...")
            last_user_msg = self.memory.get_last_message_content("user") or "default search"
            last_agent_msg = self.memory.get_last_message_content("assistant")

            # Example RAG Query
            self.logger.info(f"Step: Querying RAG about '{last_user_msg[:30]}...'" )
            rag_res = await self.query_rag(last_user_msg, n_results=1)
            rag_summary = f"Found {len(rag_res)} RAG results." if rag_res else "No relevant RAG results found."

            # Example step logic completion
            result = f"Step processed user msg: '{last_user_msg[:20]}...'. {rag_summary}"
            self.memory.add_message({"role": "assistant", "content": result})

            # Finish after 3 assistant messages
            if len([m for m in self.memory.messages if m.role == 'assistant']) >= 3:
                self.logger.info("TestV2Agent reaching FINISHED state.")
                self.state = AgentState.FINISHED

            return {"step_result": result, "rag_found": bool(rag_res)}

    async def main_base_test():
        print("\n" + "="*10 + " Testing BaseAgent V2 with RAG (ChromaDB/ST) " + "="*10)
        # Setup Test Environment
        test_user_dir = Path("./test_base_agent_v2_workspace").resolve()
        print(f"Test Workspace: {test_user_dir}")
        import shutil
        if test_user_dir.exists():
            print("Cleaning up previous test workspace...")
            shutil.rmtree(test_user_dir)
        test_user_dir.mkdir(parents=True, exist_ok=True)
        print("Test workspace prepared.")

        agent = None # Define agent outside try block for cleanup
        try:
            # 1. Instantiate Agent
            print("\n[1] Instantiating TestV2Agent...")
            agent = TestV2Agent(name="TesterV2", user_dir=str(test_user_dir))
            print(f"  Agent Initialized. RAG Status OK: {agent._rag_initialized}")
            assert agent._rag_initialized, "RAG FAILED to initialize!"

            # 2. Store initial data in RAG
            print("\n[2] Storing initial data in RAG...")
            docs = ["The sky is blue.", "Grass is green.", "The sun is bright yellow."]
            ids = ["fact1", "fact2", "fact3"]
            store_ok = await agent.store_in_rag(docs, ids)
            print(f"  Store successful: {store_ok}")
            assert store_ok, "Failed to store initial data!"
            count = agent._rag_collection.count()
            print(f"  Collection count: {count}")
            assert count == 3, "Incorrect item count after store!"

            # 3. Run agent simulation (triggers step -> query_rag)
            print("\n[3] Running agent simulation (queries RAG)...")
            await agent.run(initial_input="What color is the sky?")
            await agent.run(initial_input="Is grass purple?") # Should trigger next step
            await agent.run(initial_input="Sun color?") # Should trigger final step & finish

            # 4. Verify Final State & Memory
            print("\n[4] Verifying final state and memory...")
            print(f"  Final Agent State: {agent.state}")
            assert agent.state == AgentState.IDLE, "Agent did not return to IDLE state."
            assert len(agent.memory.messages) > 5, "Memory does not seem to contain expected interactions."
            print(f"  Memory has {len(agent.memory.messages)} messages.")
            # Check last message example
            last_mem = agent.memory.messages[-1]
            print(f"  Last memory message: Role={last_mem.role}, Content='{last_mem.content[:50]}...'" )
            assert last_mem.role == "assistant" # Should be assistant's last message

            # 5. Verify Memory Persistence
            print("\n[5] Testing Memory Persistence...")
            await agent.shutdown() # Saves memory
            assert agent._memory_file_path.exists(), "Memory file was not saved!"
            print(f"  Memory file exists: {agent._memory_file_path.name}")

            agent_reloaded = TestV2Agent(name="TesterV2", user_dir=str(test_user_dir)) # Reloads memory
            print(f"  Agent reloaded. Loaded {len(agent_reloaded.memory.messages)} messages.")
            assert len(agent_reloaded.memory.messages) == len(agent.memory.messages), "Reloaded memory message count mismatch!"
            assert agent_reloaded.memory.messages[-1].content == agent.memory.messages[-1].content, "Last message content mismatch after reload!"
            print("  Memory Persistence Test Passed.")

            print("\n--- BaseAgent V2 Test Successfully Completed ---")

        except Exception as e:
            print(f"\n--- BaseAgent V2 Test FAILED ---")
            logger.exception(f"Test failed with error: {e}")
            traceback.print_exc()
        finally:
            # Optional: Clean up test workspace
            # if test_user_dir.exists():
            #     print("\nCleaning up test workspace...")
            #     shutil.rmtree(test_user_dir)
            pass

    # Run the async test function
    asyncio.run(main_base_test()) 