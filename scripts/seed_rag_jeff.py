import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os

# Set up ChromaDB persistent directory
db_dir = r"C:\DreamerAI\data\rag_dbs"
os.makedirs(db_dir, exist_ok=True)
chroma_path = os.path.join(db_dir, "rag_jeff")
client = chromadb.PersistentClient(path=chroma_path)

# Use default embedding function (for placeholder, not production)
embedding_func = embedding_functions.DefaultEmbeddingFunction()

# Create or get collection
collection = client.get_or_create_collection(
    name="jeff_context",
    embedding_function=embedding_func
)

# Seed data
documents = [
    "DreamerAI is a desktop application designed to help users create AAA-grade software applications using a team of 28 specialized AI agents.",
    "The goal of DreamerAI is to make app development fast, educational, and accessible to users from beginners to experts, focusing on quality over unrealistic speed.",
    "Chef Jeff is the main chat agent. He interacts with the user, understands their requirements, answers questions, and coordinates tasks with the backend agent team.",
    "The Dream Team includes agents for planning (Arch), coding management (Nexus), administration (Lewis), communication (Hermie), security (Bastion), testing (Herc), documentation (Scribe), deployment (Nike) and many others.",
    "DreamerAI features a 'Dreamer Desktop' panelized UI allowing customization, and the 'Spark' engine for integrated education."
]
metadatas = [
    {"source": "seed"},
    {"source": "seed"},
    {"source": "seed"},
    {"source": "seed"},
    {"source": "seed"}
]
ids = [f"jeff_seed_{i}" for i in range(len(documents))]

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"Seeded ChromaDB collection 'jeff_context' at {chroma_path}")

# Test retrieval
query = "What is Jeff's role?"
results = collection.query(
    query_texts=[query],
    n_results=2
)
print("Test retrieval results:", results)