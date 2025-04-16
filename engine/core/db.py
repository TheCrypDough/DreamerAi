# Placeholder for Day 5 DreamerDB implementation 
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Any
# Assuming logger_instance is globally available after Day 3 setup
try:
    from engine.core.logger import logger_instance as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__) # Fallback logger

class DreamerDB:
    """
    Manages the SQLite database connection and operations for DreamerAI.
    NOTE: This implementation uses SQLite for initial development ease.
    Production deployment anticipates migration to PostgreSQL for scalability.
    """
    def __init__(self, db_path: str = r"C:\DreamerAI\data\db\dreamer.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        try:
            self.connect()
            self._initialize_tables()
            logger.info(f"Database connection established and initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False) # Allow multi-thread access if needed later by FastAPI
            self.conn.row_factory = sqlite3.Row # Access columns by name
            self.cursor = self.conn.cursor()
            logger.debug("Database connected.")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database {self.db_path}: {e}")
            self.conn = None
            self.cursor = None
            raise

    def _initialize_tables(self):
        """Creates necessary tables if they don't exist."""
        if not self.cursor:
            logger.error("Cannot initialize tables, cursor is not available.")
            return
        try:
            # Projects Table: Tracks high-level projects
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    user_id TEXT, -- Placeholder for user association
                    status TEXT DEFAULT 'NEW', -- e.g., NEW, IN_PROGRESS, COMPLETED, ARCHIVED
                    project_path TEXT NOT NULL UNIQUE, -- Path in Users/ directory
                    output_path TEXT, -- Path for generated outputs (may differ)
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Chats Table: Stores conversation history snippets (can grow large)
            # Consider alternative storage (e.g., separate files, NoSQL) if performance degrades
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    agent_name TEXT NOT NULL,
                    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            """)
            # Add more tables later as needed (e.g., subprojects, tasks, agent_memory)
            self.conn.commit()
            logger.info("Core database tables initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize tables: {e}")
            raise

    def add_project(self, name: str, user_id: str, project_path: str, output_path: Optional[str] = None) -> Optional[int]:
        """Adds a new project to the database."""
        if not self.cursor or not self.conn:
            logger.error("Database not connected, cannot add project.")
            return None
        try:
            timestamp = datetime.now()
            self.cursor.execute("""
                INSERT INTO projects (name, user_id, status, project_path, output_path, created_at, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, user_id, 'NEW', project_path, output_path or project_path, timestamp, timestamp))
            self.conn.commit()
            project_id = self.cursor.lastrowid
            logger.info(f"Project '{name}' (ID: {project_id}) added for user '{user_id}'.")
            return project_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to add project '{name}'. Integrity error (maybe path exists?): {e}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to add project '{name}': {e}")
            return None

    def get_project(self, project_id: int) -> Optional[sqlite3.Row]:
         """Retrieves a project by its ID."""
         if not self.cursor: return None
         try:
             self.cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
             return self.cursor.fetchone()
         except sqlite3.Error as e:
             logger.error(f"Failed to get project ID {project_id}: {e}")
             return None

    def add_chat_message(self, project_id: int, agent_name: str, role: str, content: str):
        """Adds a chat message linked to a project."""
        if not self.cursor or not self.conn: return
        try:
            self.cursor.execute("""
                INSERT INTO chats (project_id, agent_name, role, content)
                VALUES (?, ?, ?, ?)
            """, (project_id, agent_name, role, content))
            self.conn.commit()
            # logger.debug(f"Chat message added for project {project_id}, agent {agent_name}")
        except sqlite3.Error as e:
            logger.error(f"Failed to add chat message for project {project_id}: {e}")


    def close(self):
        """Closes the database connection."""
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed.")
            except sqlite3.Error as e:
                logger.error(f"Error closing database connection: {e}")
        self.conn = None
        self.cursor = None

# Instantiate DB (consider dependency injection later)
# This line will create the DB file on module import if it doesn't exist.
db_instance = DreamerDB()

# Example Usage
if __name__ == "__main__":
    logger.info("Testing DreamerDB...")
    test_db = DreamerDB(db_path=r"C:\DreamerAI\data\db\test_dreamer.db") # Use a test DB
    project_id = test_db.add_project("TestProject1", "user123", "C:/DreamerAI/Users/TestUser/Projects/TestProject1")
    if project_id:
        logger.info(f"Added project with ID: {project_id}")
        project_data = test_db.get_project(project_id)
        if project_data:
            logger.info(f"Retrieved project: {dict(project_data)}")
            test_db.add_chat_message(project_id, "Jeff", "user", "Build me a website")
            test_db.add_chat_message(project_id, "Jeff", "assistant", "Sure, what kind?")
            logger.info("Added test chat messages.")
        else:
            logger.error("Failed to retrieve test project.")
    else:
        logger.error("Failed to add test project.")
    test_db.close()
    # Clean up test db file
    try:
        os.remove(r"C:\DreamerAI\data\db\test_dreamer.db")
        logger.info("Cleaned up test database file.")
    except OSError as e:
        logger.error(f"Error removing test database: {e}") 