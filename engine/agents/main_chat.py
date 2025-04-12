# C:\DreamerAI\engine\agents\main_chat.py
# Implements Chef Jeff, the main user interaction agent.

import asyncio
import sys
from pathlib import Path
import traceback
from typing import Optional, Any

# Add project root to handle imports
project_root = Path(__file__).parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from engine.agents.base import BaseAgent, AgentState, Message
    from engine.core.logger import logger_instance as logger
    from engine.ai.llm import LLM
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    from pydantic import Field
except ImportError as e:
    print(f"Error importing necessary modules: {e}")
    # Attempt to provide more context if possible
    if 'chromadb' in str(e) or 'sentence_transformers' in str(e):
        print("Ensure 'chromadb' and 'sentence-transformers' are installed in the venv.")
    sys.exit(1)

# --- Placeholder Functions ---
# These will be replaced by actual integrations later (UI Bridge, n8n)
def route_tasks_n8n(task_details: dict):
    logger.info(f"[PLACEHOLDER] Routing task to n8n: {task_details}")
    # In future, call n8n webhook or API
    return {"status": "task_routed_placeholder", "task_id": "n8n-123"}

def send_update_to_ui(update_message: str):
    logger.info(f"[PLACEHOLDER] Sending update to UI: {update_message}")
    # In future, send via WebSocket bridge
    return {"status": "ui_updated_placeholder"}
# --- End Placeholder Functions ---


class ChefJeff(BaseAgent):
    """
    Chef Jeff: The main chat agent responsible for user interaction,
    understanding requests, providing information, using RAG, and
    coordinating with other agents (via placeholders initially).
    """
    # Define fields directly in the class body for Pydantic validation
    rules: str = Field(default="", description="Loaded rules from rules_jeff.md")
    rag_client: Optional[Any] = Field(None, description="ChromaDB client instance")
    rag_collection: Optional[Any] = Field(None, description="ChromaDB collection instance")
    embedding_model: Optional[Any] = Field(None, description="SentenceTransformer model instance")
    rag_persist_dir: Path = Field(default_factory=lambda: project_root / "data" / "rag_dbs" / "rag_jeff", description="Path to ChromaDB persistent directory")
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", description="Name of the sentence-transformer model")
    llm: LLM = Field(..., description="LLM service instance")

    def __init__(self, llm_instance: LLM, **data: Any):
        # Pass llm_instance directly to super() for Pydantic validation
        # Remove explicit user_dir, rely on it being in **data
        super().__init__(name="Jeff", distill=False, llm=llm_instance, **data)
        # Load rules and initialize RAG after BaseAgent init is complete
        self._load_rules()
        self._initialize_rag()
        logger.info(f"ChefJeff agent initialized. Rules loaded. RAG Initialized (Persist Dir: {self.rag_persist_dir}).")

    def _load_rules(self):
        """Loads agent-specific rules from rules_jeff.md."""
        try:
            rules_path = project_root / "engine" / "agents" / "rules_jeff.md"
            if rules_path.exists():
                self.rules = rules_path.read_text()
                logger.info(f"Successfully loaded rules from {rules_path}")
            else:
                logger.warning(f"Rules file not found at {rules_path}. Proceeding without specific rules.")
                self.rules = "Default Rule: Be helpful and conversational."
        except Exception as e:
            logger.error(f"Error loading rules for Jeff: {e}")
            self.rules = "Error Rule: Could not load rules."

    def _initialize_rag(self):
        """Initializes the ChromaDB client and loads the embedding model."""
        try:
            logger.info(f"Initializing ChromaDB client from persistent directory: {self.rag_persist_dir}")
            self.rag_client = chromadb.Client(Settings(
                persist_directory=str(self.rag_persist_dir)
            ))
            # Use get_or_create_collection for robustness
            collection_name = "jeff_context"
            self.rag_collection = self.rag_client.get_or_create_collection(name=collection_name)
            logger.info(f"Successfully connected to/created ChromaDB collection: {collection_name}")

            logger.info(f"Loading sentence-transformers model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Sentence-transformers model '{self.embedding_model_name}' loaded.")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB or load embedding model: {e}\n{traceback.format_exc()}")
            self.rag_client = None
            self.rag_collection = None
            self.embedding_model = None

    async def _retrieve_rag_context(self, query: str, n_results: int = 2) -> str:
        """Retrieves relevant context from the ChromaDB RAG based on the query."""
        if not self.rag_collection or not self.embedding_model:
            logger.warning("RAG collection or embedding model not initialized. Skipping RAG retrieval.")
            return "No RAG context available (Initialization failed)."

        try:
            logger.info(f"Retrieving RAG context for query: '{query[:50]}...'")
            query_embedding = self.embedding_model.encode([query]) # Encode query
            results = self.rag_collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )

            # Extract document content from results
            # ChromaDB returns a dict-like structure, we need 'documents' for the query
            documents = results.get('documents', [[]])[0] # Get documents for the first (only) query embedding

            if documents:
                context = "\n\n".join(documents)
                logger.info(f"Retrieved {len(documents)} RAG context snippets.")
                return context
            else:
                logger.info("No relevant RAG context found.")
                return "No specific context found in the knowledge base."
        except Exception as e:
            logger.error(f"Error retrieving RAG context: {e}\n{traceback.format_exc()}")
            return "Error retrieving context from knowledge base."

    # Signature must match BaseAgent.step
    async def step(self, input_data: Optional[Any] = None) -> Any:
        """Processes a single user message step."""
        if not isinstance(input_data, Message):
             # Handle cases where input_data might not be a Message (e.g., initial run)
             # For now, we assume step is called with a Message after the initial run.
             # If called directly with string/other, need error handling or conversion.
             if isinstance(input_data, str):
                 user_message = Message(role="user", content=input_data)
             else:
                 # Or raise an error, or return an error state message?
                 error_content = f"Invalid input type for step: {type(input_data)}"
                 self.logger.error(error_content)
                 self.state = AgentState.ERROR
                 return Message(role="assistant", content=f"Error: {error_content}")
        else:
            user_message = input_data

        self.state = AgentState.RUNNING
        logger.info(f"Jeff processing message: '{user_message.content[:100]}...'")
        # Only add if it's a user message not already in memory from run()
        if not any(m.content == user_message.content and m.role == user_message.role for m in self.memory.messages):
             self.memory.add_message(user_message)

        send_update_to_ui(f"Jeff is thinking about: {user_message.content[:50]}...") # Placeholder UI update

        # 1. Retrieve RAG Context
        rag_context = await self._retrieve_rag_context(user_message.content)

        # 2. Prepare messages for LLM generate (list of dicts)
        messages_for_llm = []
        # Add system prompt incorporating rules and RAG context
        system_prompt = f"Agent Rules:\n{self.rules}\n\nRelevant Information from Knowledge Base:\n{rag_context}\n\nRole: You are Chef Jeff, a helpful assistant."
        messages_for_llm.append({"role": "system", "content": system_prompt})
        # Add conversation history
        messages_for_llm.extend(self.memory.get_history()) # BaseAgent memory stores dicts
        # Add the current user message (it should already be the last one in history if added correctly)
        # logger.debug(f"Messages prepared for LLM: {messages_for_llm}") # Can be verbose

        # 3. Generate Response using LLM
        response_content = None # Initialize to None
        try:
            # Log the agent name being used for provider lookup
            logger.info(f"Calling LLM.generate for agent: '{self.name}'")
            response_content = await self.llm.generate(
                messages=messages_for_llm, # Pass the list of message dicts
                agent_name=self.name # Ensures config-driven model selection
                # Add other parameters like max_tokens, temperature if needed
            )
            if response_content:
                 logger.info(f"LLM generated response snippet: {response_content[:100]}...")
            else:
                 logger.warning(f"LLM.generate returned None or empty response for agent '{self.name}'")
                 response_content = "I received an empty response from the AI model." # Default content

            # Use 'role' for Message model
            assistant_message = Message(role="assistant", content=response_content)

            # Simulate task routing if needed (simple keyword check for demo)
            if "build" in user_message.content.lower() or "create" in user_message.content.lower() or "code" in user_message.content.lower():
                 route_tasks_n8n({"request": user_message.content, "agent": "Jeff"})

        except Exception as e:
            logger.error(f"LLM generation failed for Jeff: {e}\n{traceback.format_exc()}")
            # Use 'role' for Message model
            error_content = f"Apologies, I encountered an error trying to process that: {e}"
            assistant_message = Message(role="assistant", content=error_content)
            response_content = error_content # Ensure response_content has a value for logging below

        # 4. Add response to memory and update UI (placeholder)
        self.memory.add_message(assistant_message)
        # Ensure response_content is not None before slicing
        log_snippet = response_content[:50] if response_content else "[No Content]"
        send_update_to_ui(f"Jeff responded: {log_snippet}...") # Placeholder UI update

        self.state = AgentState.IDLE
        # Return type must match BaseAgent.step (Any)
        return assistant_message # Message object is compatible with Any

    # Signature must match BaseAgent.run
    async def run(self, initial_input: Optional[Any] = None) -> Any:
        """Handles an initial message and enters a basic processing loop (for testing)."""
        logger.info(f"ChefJeff starting run with initial message.")

        # Handle initial_input according to BaseAgent's logic (which adds it to memory)
        # The BaseAgent run loop will call self.step with the latest message content
        # Therefore, we just need to call the superclass run method.

        # Ensure BaseAgent logic runs correctly for initial input handling and loop
        final_result = await super().run(initial_input=initial_input)

        logger.info(f"ChefJeff finished processing initial message. Final result: {str(final_result)[:100]}...")
        return final_result


# --- Test Execution Block ---
if __name__ == "__main__":
    print("--- Running ChefJeff Test Block ---")
    # Ensure necessary setup is done (e.g., .env loaded, config exists)

    # Check if DB exists before running, else seed script should be run first
    rag_db_test_path = project_root / "data" / "rag_dbs" / "rag_jeff"
    if not rag_db_test_path.exists():
         print(f"ERROR: RAG DB directory not found at {rag_db_test_path}")
         print("Please run the seed script first: python scripts/seed_rag_jeff.py")
         sys.exit(1)
    else:
        print(f"Found RAG DB directory: {rag_db_test_path}")


    async def main_test():
        logger.info("Initializing LLM for test...")
        try:
            llm_service = LLM() # Loads config automatically
            logger.info("LLM service initialized.")

            logger.info("Instantiating ChefJeff...")
            # Pass only the required llm_instance; Pydantic handles defaults for other fields
            jeff = ChefJeff(llm_instance=llm_service)
            logger.info("ChefJeff instantiated.")

            test_query = "What is DreamerAI?"
            logger.info(f"Sending test query to Jeff: '{test_query}'")
            final_response = await jeff.run(test_query)

            print("\n--- Test Query ---")
            print(f"User: {test_query}")
            print("\n--- Jeff's Final Response ---")
            print(f"Jeff: {final_response.content}")

            print("\n--- Jeff's Memory ---")
            print(jeff.memory.get_history())

        except Exception as e:
            print(f"\nERROR during test execution: {e}")
            traceback.print_exc()

    # Run the async test function
    asyncio.run(main_test())
    print("\n--- ChefJeff Test Block Finished ---") 