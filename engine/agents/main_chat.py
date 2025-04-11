# C:\DreamerAI\engine\agents\main_chat.py
# Implements Chef Jeff, the main user interaction agent.

import asyncio
import sys
from pathlib import Path
import traceback

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
    def __init__(self, llm_instance: LLM):
        super().__init__(name="Jeff", user_dir=None, distill=False, llm_instance=llm_instance)
        self.rules: str = ""
        self.rag_client = None
        self.rag_collection = None
        self.embedding_model = None
        self.rag_persist_dir = project_root / "data" / "rag_dbs" / "rag_jeff"
        self.embedding_model_name = "all-MiniLM-L6-v2"
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
            # Get the specific collection seeded earlier
            collection_name = "jeff_context"
            self.rag_collection = self.rag_client.get_collection(name=collection_name)
            logger.info(f"Successfully connected to ChromaDB collection: {collection_name}")

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

    async def step(self, user_message: Message) -> Message:
        """Processes a single user message step."""
        self.state = AgentState.RUNNING
        logger.info(f"Jeff processing message: '{user_message.content[:100]}...'")
        self.memory.add_message(user_message)
        send_update_to_ui(f"Jeff is thinking about: {user_message.content[:50]}...") # Placeholder UI update

        # 1. Retrieve RAG Context
        rag_context = await self._retrieve_rag_context(user_message.content)

        # 2. Format Prompt
        prompt_template = f"""
User Query: {user_message.content}

Relevant Information from Knowledge Base:
{rag_context}

Agent Rules:
{self.rules}

Conversation History:
{self.memory.get_formatted_history(last_n=5)}

Based on the rules, conversation history, and relevant information, provide a helpful and conversational response to the User Query.
If the query seems like a task request (e.g., 'build an app', 'write code'), acknowledge it and mention that you will coordinate with the backend team (placeholder call: route_tasks_n8n).
Response:
"""
        logger.debug(f"Formatted prompt for LLM (excluding history details): {prompt_template[:200]}...") # Log snippet

        # 3. Generate Response using LLM
        try:
            logger.info(f"Calling LLM (provider for 'Jeff': {self.llm.get_provider_for_agent('Jeff')})")
            response_content = await self.llm.generate(
                prompt_template,
                agent_name=self.name # Ensures config-driven model selection
                # Add other parameters like max_tokens, temperature if needed
            )
            logger.info(f"LLM generated response snippet: {response_content[:100]}...")
            assistant_message = Message(sender="Jeff", content=response_content)

            # Simulate task routing if needed (simple keyword check for demo)
            if "build" in user_message.content.lower() or "create" in user_message.content.lower() or "code" in user_message.content.lower():
                 route_tasks_n8n({"request": user_message.content, "agent": "Jeff"})

        except Exception as e:
            logger.error(f"LLM generation failed for Jeff: {e}\n{traceback.format_exc()}")
            assistant_message = Message(sender="Jeff", content=f"Apologies, I encountered an error trying to process that: {e}")

        # 4. Add response to memory and update UI (placeholder)
        self.memory.add_message(assistant_message)
        send_update_to_ui(f"Jeff responded: {assistant_message.content[:50]}...") # Placeholder UI update

        self.state = AgentState.IDLE
        return assistant_message

    async def run(self, initial_message_content: str):
        """Handles an initial message and enters a basic processing loop (for testing)."""
        logger.info(f"ChefJeff starting run with initial message.")
        initial_message = Message(sender="User", content=initial_message_content)
        response = await self.step(initial_message)
        logger.info(f"ChefJeff finished processing initial message. Final response: {response.content[:100]}...")
        return response


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
            print(jeff.memory.get_formatted_history())

        except Exception as e:
            print(f"\nERROR during test execution: {e}")
            traceback.print_exc()

    # Run the async test function
    asyncio.run(main_test())
    print("\n--- ChefJeff Test Block Finished ---") 