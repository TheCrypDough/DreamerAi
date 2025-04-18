# C:\DreamerAI\scripts\seed_rag_jeff.py (UPDATED Pattern)
import sys
import os
import traceback
import asyncio # NEW Import
from pathlib import Path

project_root_seed = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_seed not in sys.path: sys.path.insert(0, project_root_seed)

try:
    # Import the specific agent class AND BaseAgent (needed potentially for context/errors)
    from engine.agents.main_chat import ChefJeff
    from engine.agents.base import BaseAgent # Import BaseAgent for type hints/checks maybe
    from engine.core.logger import logger_instance as logger
    SEED_LIBS_OK = True
except ImportError as e:
    print(f"ERROR importing in seed_rag_jeff: {e}. Is venv active? Are agents implemented?")
    SEED_LIBS_OK = False
    sys.exit(1)

# Define data and target agent config
AGENT_NAME = "Jeff"
USER_DIR_FOR_SEED = r"C:\DreamerAI\Users\SeedUser" # Use a dedicated or dummy user dir for seeding V1
SEED_DOCUMENTS = [
    "Jeff is DreamerAI's main chat agent, acting as the friendly frontman.",
    "Jeff interacts with users to understand their project ideas and collaborates with Sophia (suggestions) and Spark (education).",
    "Jeff hands off finalized project requirements to Hermie (communications).",
    "Key DreamerAI agents include Arch (planning), Nexus (coding manager), Lewis (administrator), and Riddick (research).",
    "DreamerAI aims to build AAA-grade applications using a team of specialized AI agents.",
    "The workflow generally starts with user input, refinement, planning, coding, QA, documentation, and deployment prep.",
    "Nexus manages the coding team including Lamar (Frontend), Dudley (Backend), and Specialists (Wormser, Gilbert, Poindexter)."
]
SEED_IDS = [f"jeff_fact_{i+1}" for i in range(len(SEED_DOCUMENTS))]


async def seed_agent_rag():
    """ Seeds the RAG DB for a specific agent using its store_in_rag method. """
    if not SEED_LIBS_OK: return

    # Ensure user dir exists for agent initialization (memory logs etc.)
    Path(USER_DIR_FOR_SEED).mkdir(parents=True, exist_ok=True)

    logger.info(f"Attempting to seed RAG DB for agent: {AGENT_NAME}")
    agent_instance = None
    try:
        # 1. Instantiate the agent (This also initializes its RAG DB/Collection)
        # Use the specific agent class (ChefJeff)
        agent_instance = ChefJeff(user_dir=USER_DIR_FOR_SEED)
        if not agent_instance._rag_initialized: # Check flag set by BaseAgent V2
             raise Exception(f"RAG components failed to initialize for agent {AGENT_NAME}. Cannot seed.")

        # Optional: Clear existing collection before seeding? Depends on desired behavior.
        # Be careful clearing production data! Only for dev seeding.
        # count_before = agent_instance.rag_collection.count()
        # if count_before > 0:
        #     logger.warning(f"Collection '{agent_instance.rag_collection.name}' not empty ({count_before} items). Clearing before seeding...")
        #     # Need a way to clear - requires agent instance or direct ChromaDB client interaction.
        #     # agent_instance.rag_client.delete_collection(agent_instance.rag_collection.name)
        #     # agent_instance.rag_collection = agent_instance.rag_client.create_collection(...) # Recreate
        # For V1 seeding, let's assume we ADD or it overwrites based on IDs. Add checks later.


        # 2. Call the agent's store_in_rag method
        success = await agent_instance.store_in_rag(
            documents=SEED_DOCUMENTS,
            ids=SEED_IDS
        )

        if success:
             logger.info(f"Successfully seeded {len(SEED_DOCUMENTS)} documents into RAG for {AGENT_NAME}.")
             print(f"Seeding successful for {AGENT_NAME}. Collection count: {agent_instance.rag_collection.count()}")
        else:
             logger.error(f"Seeding failed for agent {AGENT_NAME}.")
             print(f"ERROR: Seeding failed for {AGENT_NAME}. Check logs.")

    except Exception as e:
        logger.exception(f"Error during RAG seeding for {AGENT_NAME}")
        print(f"ERROR during seeding for {AGENT_NAME}: {e}")
    finally:
        # Optional: Cleanup agent instance if needed?
        # BaseAgent doesn't have complex shutdown V1 beyond memory save.
        pass

if __name__ == "__main__":
    print(f"Executing RAG seed script for {AGENT_NAME}...")
    asyncio.run(seed_agent_rag())
    print("Seed script finished.") 