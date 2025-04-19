# C:\DreamerAI\engine\core\project_manager.py
import os
import traceback
from pathlib import Path
from typing import Optional
import logging # Import standard logging first

# Attempt to import the custom logger, fallback to standard logging
try:
    from .logger import logger_instance as logger
except ImportError:
    # Explicitly use logging.getLogger to avoid potential linter confusion
    logger = logging.getLogger(__name__) # Use the imported logging module
    logger.warning("Could not import custom logger 'logger_instance'. Falling back to standard logging.")

class ProjectManager:
    """Handles creation and management of project/subproject file structures."""

    def __init__(self, user_base_dir: str = r"C:\DreamerAI\Users"):
        self.user_base_dir = Path(user_base_dir)
        if not self.user_base_dir.exists():
            logger.warning(f"User base directory does not exist: {self.user_base_dir}")
            # Consider creating it? Or rely on Day 1 setup. For now, log warning.

    def get_project_path(self, user_id: str, project_name: str) -> Path:
        """Constructs the path to a user's specific project directory."""
        # Basic sanitization (more needed for production)
        safe_user_id = "".join(c for c in user_id if c.isalnum() or c in (' ', '_')).rstrip()
        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_')).rstrip()
        return self.user_base_dir / safe_user_id / "Projects" / safe_project_name

    def create_subproject_structure(self, parent_project_path: Path, subproject_name: str) -> Optional[Path]:
        """
        Creates the necessary directory structure for a new subproject.

        Args:
            parent_project_path: The Path object to the parent project's directory.
            subproject_name: The name for the new subproject.

        Returns:
            The Path object to the created subproject directory, or None on failure.
        """
        try:
            # Basic sanitization (more needed for production)
            safe_subproject_name = "".join(c for c in subproject_name if c.isalnum() or c in (' ', '_')).rstrip()
            if not safe_subproject_name:
                 logger.error("Subproject name is invalid or empty after sanitization.")
                 return None

            subprojects_base_dir = parent_project_path / "Subprojects"
            subproject_dir = subprojects_base_dir / safe_subproject_name
            chats_dir = subproject_dir / "Chats" # Standard location for subproject chats

            # Create directories
            # Use exist_ok=True to avoid errors if they already exist somehow
            subproject_dir.mkdir(parents=True, exist_ok=True)
            chats_dir.mkdir(exist_ok=True)

            logger.info(f"Created subproject structure at: {subproject_dir}")
            return subproject_dir

        except OSError as e:
            logger.error(f"Failed to create directory structure for subproject '{subproject_name}' at {parent_project_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating subproject structure: {e}\n{traceback.format_exc()}")
            return None

# Example Usage / Test Block
if __name__ == "__main__":
    print("--- Testing Project Manager ---")
    manager = ProjectManager()
    test_user = "TestUserPM"
    test_proj = "MainWebApp"
    test_subproj = "User Authentication Module"

    # Construct parent path
    parent_path = manager.get_project_path(test_user, test_proj)
    print(f"Parent Project Path: {parent_path}")

    # Create parent structure for test if needed
    # Normally created by add_project logic elsewhere
    (parent_path / "Overview").mkdir(parents=True, exist_ok=True)

    # Test creating subproject structure
    print(f"Attempting to create subproject structure for: '{test_subproj}'")
    created_path = manager.create_subproject_structure(parent_path, test_subproj)

    if created_path:
        print(f"Subproject structure created successfully: {created_path}")
        print(f"Chats directory should exist: { (created_path / 'Chats').exists() }")
        # Optional: Clean up test directories
        # import shutil
        # shutil.rmtree(manager.user_base_dir / test_user)
        # print("Cleaned up test user directory.")
    else:
        print("Subproject structure creation failed.") 