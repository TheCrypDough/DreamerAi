# C:\DreamerAI\scripts\seed_rag_jeff.py
# Temporary script to initialize and seed Jeff's RAG database using ChromaDB and sentence-transformers.
# This script creates a persistent ChromaDB collection and seeds it with context snippets for Chef Jeff.

import sys
import os
import traceback
from pathlib import Path

# Add project root to handle imports when running script directly
project_root_seed = Path(__file__).parent.parent.resolve()
if str(project_root_seed) not in sys.path:
    sys.path.insert(0, str(project_root_seed))

# Try to use the main logger instance
try:
    from engine.core.logger import logger_instance as logger
    print("Using main logger instance.")
except ImportError:
    import logging
    # Basic fallback logging if main logger fails (e.g., if run before logger fully set up)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    print("Main logger not found, using basic logging for seeding.")

# Define path for Jeff's RAG database (ChromaDB persistent directory)
db_dir = project_root_seed / "data" / "rag_dbs"
chroma_persist_dir = db_dir / "rag_jeff"

# --- Sample Seed Data ---
SEED_DATA = [
    "DreamerAI is a desktop application designed to help users create AAA-grade software applications using a team of 28 specialized AI agents.",
    "The goal of DreamerAI is to make app development fast, educational, and accessible to users from beginners to experts, focusing on quality over unrealistic speed.",
    "Chef Jeff is the main chat agent. He interacts with the user, understands their requirements, answers questions, and coordinates tasks with the backend agent team.",
    "The Dream Team includes agents for planning (Arch), coding management (Nexus), administration (Lewis), communication (Hermie), security (Bastion), testing (Herc), documentation (Scribe), deployment (Nike), and many others.",
    "DreamerAI features a 'Dreamer Desktop' panelized UI allowing customization, and the 'Spark' engine for integrated education.",
    "When starting a project, provide Jeff with your core idea. Arch will then create a plan, and Nexus will manage the coding process."
]

def seed_chromadb():
    logger.info(f"Attempting to seed ChromaDB for Jeff at: {chroma_persist_dir}")

    # Ensure the parent directory exists
    chroma_persist_dir.mkdir(parents=True, exist_ok=True)

    # Import ChromaDB and sentence-transformers
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        logger.info("ChromaDB and SentenceTransformer imported successfully.")
    except ImportError as e:
        logger.error(f"Import error: {e}. Please ensure chromadb and sentence-transformers are installed in the venv.")
        print(f"\nERROR: Import error - {e}. Ensure 'chromadb' and 'sentence-transformers' are installed.")
        sys.exit(1)

    # Initialize ChromaDB client with persistent storage
    logger.info(f"Initializing ChromaDB client, persisting to: {chroma_persist_dir}")
    try:
        client = chromadb.Client(Settings(
            persist_directory=str(chroma_persist_dir)
        ))
        logger.info("ChromaDB client initialized.")
    except Exception as client_e:
        logger.error(f"Failed to initialize ChromaDB client: {client_e}\n{traceback.format_exc()}")
        print(f"\nERROR initializing ChromaDB client: {client_e}")
        sys.exit(1)

    # Create or get the collection
    collection_name = "jeff_context"
    logger.info(f"Getting or creating collection: {collection_name}")
    collection = client.get_or_create_collection(collection_name)
    logger.info(f"Collection '{collection_name}' ready.")

    # Check if seeding has already happened (by checking if first ID exists)
    if collection.get(ids=["seed-1"]):
        logger.warning("Collection already contains seed data (ID 'seed-1' found). Skipping seeding.")
        print("\nCollection appears to be already seeded. Skipping.")
        return # Exit safely if already seeded

    # Load the sentence-transformers model
    model_name = "all-MiniLM-L6-v2"
    logger.info(f"Loading sentence-transformers model: {model_name}")
    try:
        model = SentenceTransformer(model_name)
        logger.info(f"Model {model_name} loaded.")
    except Exception as model_e:
        logger.error(f"Failed to load sentence-transformers model '{model_name}': {model_e}\n{traceback.format_exc()}")
        print(f"\nERROR loading SentenceTransformer model: {model_e}")
        sys.exit(1)

    # Generate embeddings for the seed data
    logger.info("Generating embeddings for seed data...")
    embeddings = model.encode(SEED_DATA, show_progress_bar=True)
    logger.info("Embeddings generated.")

    # Prepare documents and ids
    documents = SEED_DATA
    ids = [f"seed-{i+1}" for i in range(len(SEED_DATA))]

    # Add documents to the collection
    logger.info("Adding documents to ChromaDB collection...")
    try:
        collection.add(
            documents=documents,
            embeddings=embeddings.tolist(), # Convert numpy array to list for ChromaDB
            ids=ids
        )
        logger.info(f"Successfully added {len(documents)} documents to collection '{collection_name}'.")
        print(f"\nSuccessfully seeded collection '{collection_name}' in {chroma_persist_dir} with {len(documents)} entries.")
    except Exception as add_e:
        logger.error(f"Failed to add documents to ChromaDB: {add_e}\n{traceback.format_exc()}")
        print(f"\nERROR adding documents to ChromaDB: {add_e}")

    # Persistence is handled automatically in ChromaDB >=1.0.0
    # client.persist() # Removed as per user feedback and modern ChromaDB API
    logger.info("ChromaDB seeding process complete (persistence automatic).")

if __name__ == "__main__":
    print(f"\nExecuting ChromaDB seed script for Jeff from: {os.getcwd()}")
    try:
        seed_chromadb()
        print("\nChromaDB seeding process finished successfully.")
    except Exception as e:
        logger.error(f"ChromaDB seeding script failed: {e}\n{traceback.format_exc()}")
        print(f"\nERROR: Seeding script failed: {e}")