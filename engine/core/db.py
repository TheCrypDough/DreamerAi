# Placeholder for Day 5 DreamerDB implementation 
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Any, Dict
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

            # --- NEW: Subprojects Table ---
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS subprojects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_project_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    subproject_path TEXT NOT NULL UNIQUE, -- Path within parent project dir
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            """)
            # Index for faster lookup by parent project
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_subproj_parent ON subprojects (parent_project_id);
            """)

            self.conn.commit()
            logger.info("Core database tables initialized successfully (incl. subprojects).")
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

    # --- NEW: Add Subproject Method ---
    def add_subproject(self, parent_project_id: int, name: str, subproject_path: str) -> Optional[int]:
        """Adds a new subproject linked to a parent project."""
        if not self.cursor or not self.conn:
            logger.error("Database not connected, cannot add subproject.")
            return None
        try:
            timestamp = datetime.now()
            self.cursor.execute("""
                INSERT INTO subprojects (parent_project_id, name, subproject_path, created_at, last_modified)
                VALUES (?, ?, ?, ?, ?)
            """, (parent_project_id, name, subproject_path, timestamp, timestamp))
            self.conn.commit()
            subproject_id = self.cursor.lastrowid
            logger.info(f"Subproject '{name}' (ID: {subproject_id}) added for Parent Project ID {parent_project_id}.")
            return subproject_id
        except sqlite3.IntegrityError as e:
            # Could be UNIQUE constraint on path, or foreign key issue
            logger.error(f"Failed to add subproject '{name}'. Integrity error: {e}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to add subproject '{name}': {e}")
            return None

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
    # Ensure necessary imports for standalone execution
    import os
    from pathlib import Path
    # Ensure logger is available if needed within this block
    try:
        from engine.core.logger import logger_instance as logger
    except ImportError:
        import logging
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.StreamHandler()) # Ensure output goes to console
        logger.setLevel(logging.INFO)

    logger.info("Running db.py main block to ensure Project ID 1 exists...")

    # Use the main DB instance directly
    # db_instance is created when the module is imported
    from engine.core.db import db_instance

    target_project_id = 1
    project_name = "TestProject1"
    user_id = "Example User"
    # Construct the standard project path
    # Need ProjectManager temporarily for path construction consistency
    try:
        from engine.core.project_manager import ProjectManager
        pm = ProjectManager()
        project_path = pm.get_project_path(user_id, project_name)
    except ImportError:
        logger.error("Could not import ProjectManager. Cannot reliably determine project path.")
        project_path = Path(f"C:/DreamerAI/Users/{user_id}/Projects/{project_name}") # Fallback path
        logger.warning(f"Using fallback project path: {project_path}")

    logger.info(f"Target Project: '{project_name}' (ID: {target_project_id}) for User: '{user_id}'")
    logger.info(f"Expected Path: {project_path}")

    # Check if project already exists
    existing_project = db_instance.get_project(target_project_id)

    if existing_project:
        logger.info(f"Project ID {target_project_id} ('{existing_project['name']}') already exists. Path: {existing_project['project_path']}")
        # Optional: Verify path matches expected path?
        if Path(existing_project['project_path']) != project_path:
             logger.warning(f"Existing project path {existing_project['project_path']} does not match expected {project_path}")
    else:
        logger.info(f"Project ID {target_project_id} not found. Attempting to create...")
        # Ensure directory structure exists first
        try:
            overview_path = project_path / "Overview"
            overview_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory structure exists: {overview_path}")
        except Exception as e:
            logger.error(f"FAILED to create directory structure at {project_path}: {e}", exc_info=True)
            # Optionally exit or just log and try DB add anyway?
            # Forcing DB add attempt even if dir fails, to see if DB itself works.

        # Add the project to the database
        added_id = db_instance.add_project(name=project_name, user_id=user_id, project_path=str(project_path))

        if added_id == target_project_id:
            logger.info(f"Successfully added project '{project_name}' with ID: {added_id}")
            # Add initial chat messages if needed
            db_instance.add_chat_message(added_id, 'Jeff', 'user', 'Initial setup message via db.py main.')
            db_instance.add_chat_message(added_id, 'Jeff', 'assistant', 'Acknowledged setup via db.py main.')
            logger.info("Added initial chat messages.")
        elif added_id:
            logger.warning(f"Added project '{project_name}' but received ID {added_id} instead of expected {target_project_id}. This might cause issues.")
        else:
            logger.error(f"FAILED to add project '{project_name}' to the database.")

    # Close the connection if this script opened it (db_instance handles its own)
    # No, db_instance is shared, don't close it here.
    logger.info("db.py main block finished.")

# Consider adding subproject creation/retrieval test to __main__ 