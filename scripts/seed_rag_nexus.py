# C:\DreamerAI\scripts\seed_rag_nexus.py (Uses BaseAgent V2 store_in_rag)
import sys
import os
import traceback
import asyncio
from pathlib import Path

project_root_seed = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_seed not in sys.path: sys.path.insert(0, project_root_seed)

try:
    # Import the specific agent class
    from engine.agents.coding_manager import NexusAgent
    from engine.core.logger import logger_instance as logger
    SEED_LIBS_OK = True
except ImportError as e:
    print(f"ERROR importing in seed_rag_nexus: {e}. Is venv active? Are agents implemented?")
    SEED_LIBS_OK = False
    sys.exit(1)

# --- Define data and target agent config ---
AGENT_NAME = "Nexus"
USER_DIR_FOR_SEED = r"C:\DreamerAI\Users\SeedUserNexus" # Use a dedicated or dummy user dir
SEED_DOCUMENTS = [
    "Nexus manages coding agents. First, trigger frontend (Lamar), then backend (Dudley) for initial code generation based on the blueprint.",
    "Ensure the complete project blueprint and the correct output path are passed to coding agents."
]
SEED_IDS = [f"nexus_fact_{i+1}" for i in range(len(SEED_DOCUMENTS))]
# -----------------------------------------

async def seed_agent_rag():
    """ Seeds the RAG DB for Nexus using its store_in_rag method. """
    if not SEED_LIBS_OK: return

    Path(USER_DIR_FOR_SEED).mkdir(parents=True, exist_ok=True)
    logger.info(f"Attempting to seed RAG DB for agent: {AGENT_NAME}")
    agent_instance = None
    try:
        # Instantiate the agent (which initializes RAG via BaseAgent V2)
        agent_instance = NexusAgent(user_dir=USER_DIR_FOR_SEED)
        if not agent_instance._rag_initialized:
             raise Exception(f"RAG components failed to initialize for agent {AGENT_NAME}. Cannot seed.")

        # Call the agent's store_in_rag method
        success = await agent_instance.store_in_rag(
            documents=SEED_DOCUMENTS,
            ids=SEED_IDS
        )

        if success:
             logger.info(f"Successfully seeded {len(SEED_DOCUMENTS)} documents into RAG for {AGENT_NAME}.")
             # Access count via the private attribute as agent_instance doesn't expose rag_collection directly
             count = agent_instance._rag_collection.count() if agent_instance._rag_collection else 'N/A'
             print(f"Seeding successful for {AGENT_NAME}. Collection count: {count}")
        else:
             logger.error(f"Seeding failed for agent {AGENT_NAME}.")
             print(f"ERROR: Seeding failed for {AGENT_NAME}. Check logs.")

    except Exception as e:
        logger.exception(f"Error during RAG seeding for {AGENT_NAME}")
        print(f"ERROR during seeding for {AGENT_NAME}: {e}")

if __name__ == "__main__":
    print(f"Executing RAG seed script for {AGENT_NAME}...")
    asyncio.run(seed_agent_rag())
    print("Seed script finished.") 