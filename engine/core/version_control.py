# C:\DreamerAI\engine\core\version_control.py
import os
import traceback
from pathlib import Path
from typing import Optional
import asyncio # Added for async placeholders
import git
import logging
from engine.core.logger import logger_instance # Correct import

# Import GitPython - raises ImportError if not installed
try:
    from git import Repo, GitCommandError
    GITPYTHON_INSTALLED = True
except ImportError:
    git = None  # type: ignore
    Repo = None  # type: ignore
    GitCommandError = Exception  # type: ignore
    GITPYTHON_INSTALLED = False

# Setup logging
logger = logger_instance # Use the imported instance

class VersionControl:
    """Manages Git operations for project versioning within DreamerAI."""

    def __init__(self, project_path: str):
        """
        Initializes the VersionControl system for a given project path.

        Args:
            project_path (str): The absolute path to the project directory.
        """
        self.project_path = project_path
        self.repo = None
        try:
            if os.path.exists(os.path.join(project_path, '.git')):
                self.repo = git.Repo(self.project_path)
                logger.info(f"Existing Git repository loaded for project: {project_path}")
            else:
                self.repo = self.initialize_repository()
        except git.InvalidGitRepositoryError:
            logger.warning(f"Invalid Git repository detected at {project_path}. Attempting re-initialization.")
            self.repo = self.initialize_repository()
        except Exception as e:
            logger.error(f"Failed to initialize or load repository at {project_path}: {e}", exc_info=True)
            raise  # Re-raise critical errors

    def initialize_repository(self) -> git.Repo | None:
        """
        Initializes a new Git repository in the project path if one doesn't exist.

        Returns:
            git.Repo | None: The initialized Repo object or None if initialization failed.
        """
        try:
            repo = git.Repo.init(self.project_path)
            # Create initial .gitignore
            gitignore_path = os.path.join(self.project_path, '.gitignore')
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, 'w') as f:
                    f.write("# DreamerAI Generated Files\n")
                    f.write("*.log\n")
                    f.write("*.db\n") # Example: ignore database files
                    f.write("*.db-journal\n")
                    f.write("__pycache__/\n")
                    f.write("*.pyc\n")
                    f.write(".env*\n")
                    f.write("node_modules/\n")
                    f.write("dist/\n")
                    f.write("build/\n")
            logger.info(f"Initialized new Git repository and .gitignore in: {self.project_path}")
            return repo
        except Exception as e:
            logger.error(f"Failed to initialize Git repository at {self.project_path}: {e}", exc_info=True)
            return None

    def stage_changes(self, files: Optional[list[str]] = None):
        """
        Stages specified files or all changes if no files are provided.

        Args:
            files (list[str], optional): List of file paths relative to the project root to stage.
                                         Defaults to None, which stages all changes.
        """
        if not self.repo:
            logger.error("Repository not initialized. Cannot stage changes.")
            return

        try:
            if files:
                # Ensure paths are relative to repo root if absolute paths are given
                relative_files = []
                for f in files:
                    if os.path.isabs(f):
                        # Attempt to make relative; may fail if outside repo
                        try:
                             rel_path = os.path.relpath(f, self.project_path)
                             relative_files.append(rel_path)
                        except ValueError:
                            logger.warning(f"File {f} is outside the repository root {self.project_path}. Skipping.")
                    else:
                        relative_files.append(f) # Assume already relative

                logger.info(f"Staging specific files: {relative_files}")
                self.repo.index.add(relative_files)
            else:
                logger.info("Staging all changes.")
                self.repo.index.add('*') # Stage all tracked and untracked files
            logger.info("Changes staged successfully.")
            return True # Explicitly return True on success
        except Exception as e:
            logger.error(f"Failed to stage changes: {e}", exc_info=True)
            # Implicitly returns None on exception

    def commit_changes(self, message: str):
        """
        Commits staged changes with a given message.

        Args:
            message (str): The commit message.
        """
        if not self.repo:
            logger.error("Repository not initialized. Cannot commit changes.")
            return

        try:
            # Check if there are staged changes
            # diff returns empty list if no changes, raises BadName if HEAD doesn't exist (first commit)
            staged_changes = False
            try:
                if self.repo.index.diff("HEAD"): # Compare index against last commit
                     staged_changes = True
            except git.exc.BadName: # Handles the case where HEAD doesn't exist (initial commit)
                 if self.repo.index.diff(None): # Compare index against empty tree
                     staged_changes = True

            if not staged_changes and not self.repo.untracked_files:
                 # Also check untracked files specifically for the initial commit scenario
                 # where .gitignore might be the only change and needs staging first.
                 # A better approach might be to ensure .gitignore is staged *before* calling commit.
                 # Let's refine: stage_changes should be called before commit.
                 # This check primarily prevents empty commits.
                 logger.info("No changes staged for commit.")
                 return # Prevent empty commits

            self.repo.index.commit(message)
            logger.info(f"Changes committed successfully with message: '{message}'")
            return True # Explicitly return True on success
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}", exc_info=True)
            # Implicitly returns None on exception

    def get_status(self) -> str:
        """
        Gets the current status of the repository.

        Returns:
            str: A string describing the repository status (output of git status).
        """
        if not self.repo:
            logger.error("Repository not initialized. Cannot get status.")
            return "Error: Repository not initialized."
        try:
            # Fetch the status using git command directly for comprehensive output
            status_output = self.repo.git.status()
            logger.info("Retrieved repository status.")
            return status_output
        except Exception as e:
            logger.error(f"Failed to get repository status: {e}", exc_info=True)
            return f"Error getting status: {e}"

    def get_changed_files(self) -> dict:
        """
        Gets lists of modified, untracked, and staged files.

        Returns:
            dict: A dictionary with keys 'modified', 'untracked', 'staged'.
                  'staged' contains tuples (status, file_path).
        """
        if not self.repo:
            logger.error("Repository not initialized. Cannot get changed files.")
            return {'modified': [], 'untracked': [], 'staged': []}

        try:
            modified_files = [item.a_path for item in self.repo.index.diff(None)] # Files modified since last commit, unstaged
            untracked_files = self.repo.untracked_files
            # Staged files (added, modified, deleted) compared to HEAD
            staged_files_diff = self.repo.index.diff("HEAD") # Diff against the last commit
            staged_details = []
            for change in staged_files_diff:
                status = change.change_type # e.g., 'A' (added), 'M' (modified), 'D' (deleted), 'R' (renamed), 'C' (copied)
                path = change.a_path # Path in the index
                staged_details.append((status, path))

            # Handle initial commit case where HEAD doesn't exist
            # In this case, diff(None) shows all staged files as 'added' essentially.
            if not self.repo.head.is_valid():
                staged_files_diff_initial = self.repo.index.diff(None) # Diff against empty tree
                staged_details = []
                for change in staged_files_diff_initial:
                     # Treat all as 'added' or 'modified' for simplicity in initial commit context
                     status = change.change_type if change.change_type != 'D' else 'A' # Map deletions to additions? Maybe just use type.
                     path = change.a_path
                     staged_details.append((change.change_type, path))


            logger.info("Retrieved changed files status.")
            return {
                'modified': modified_files, # More accurately, these are unstaged changes to tracked files
                'untracked': untracked_files,
                'staged': staged_details
            }
        except git.exc.BadName: # Handle initial commit scenario for staged files
             staged_files_diff_initial = self.repo.index.diff(None)
             staged_details = [(change.change_type, change.a_path) for change in staged_files_diff_initial]
             logger.info("Retrieved changed files status (initial commit).")
             return {
                 'modified': [], # No 'HEAD' to compare against for modifications yet
                 'untracked': self.repo.untracked_files,
                 'staged': staged_details
             }

        except Exception as e:
            logger.error(f"Failed to get changed files: {e}", exc_info=True)
            return {'modified': [], 'untracked': [], 'staged': []}

    # --- Placeholder Remote Operations (Require Authentication/API Interaction Later) ---

    async def create_github_repo(self, name: str, access_token: str) -> Optional[str]:
        """
        Placeholder: Creates a new repository on GitHub. V1 Structure Only.
        Requires implemented GitHub OAuth and requests library.
        """
        logger.warning("Placeholder create_github_repo called. Requires Day 25+ Auth & API implementation.")
        # --- Example Logic (Deferred Implementation) ---
        # import requests
        # url = "https://api.github.com/user/repos"
        # headers = {"Authorization": f"token {access_token}", "Accept": "application/vnd.github.v3+json"}
        # data = {"name": name, "private": False} # Or True based on user choice
        # try:
        #    response = requests.post(url, headers=headers, json=data)
        #    if response.status_code == 201:
        #        remote_url = response.json()["clone_url"]
        #        logger.info(f"Successfully created GitHub repo: {name}")
        #        # Attempt to add remote if repo is initialized
        #        if self.repo:
        #             try:
        #                self.repo.create_remote("origin", remote_url)
        #                logger.info(f"Added remote 'origin': {remote_url}")
        #             except Exception as e:
        #                logger.warning(f"Could not add remote 'origin' for new repo: {e}")
        #        return remote_url
        #    else:
        #        logger.error(f"Failed to create GitHub repo ({response.status_code}): {response.text}")
        #        return None
        # except Exception as e:
        #    logger.error(f"Error calling GitHub API: {e}")
        #    return None
        # --- End Example Logic ---
        return None


    async def push_to_remote(self, remote_name: str = "origin", branch: Optional[str] = None) -> bool:
        """
        Placeholder: Pushes the current branch to the specified remote. V1 Structure Only.
        Requires remote to be configured and authentication handled (e.g., PAT, SSH key).
        """
        logger.warning(f"Placeholder push_to_remote called for remote '{remote_name}'. Requires Day 25+ Auth implementation.")
        if not self.repo:
            logger.error("Cannot push: Repository not initialized.")
            return False
        try:
            target_branch = branch or self.repo.active_branch.name
            logger.info(f"Simulating push to remote '{remote_name}' branch '{target_branch}'...")
            # --- Example Logic (Deferred Implementation) ---
            # remote = self.repo.remote(name=remote_name)
            # # GitPython push might require credential helper or SSH key setup on system
            # push_info = remote.push(refspec=f'{target_branch}:{target_branch}')
            # logger.info(f"Push successful: {push_info}")
            # --- End Example Logic ---
            await asyncio.sleep(0.1) # Simulate async placeholder
            return True # Simulate success
        except GitCommandError as e:
            logger.error(f"Git command failed during push simulation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during push simulation: {e}")
            return False

# --- Test Block --- Note: This is from the guide, not intended for direct main.py use
async def test_version_control_local():
    print("--- Testing VersionControl (Local Ops) V1 ---")
    # Create a unique test repo path for each run
    test_repo_parent = Path("./test_vc_workspace_day24").resolve()
    repo_name = f"TestRepo_{int(asyncio.get_event_loop().time())}"
    test_repo_path = test_repo_parent / repo_name
    print(f"Test Repository Path: {test_repo_path}")

    if not GITPYTHON_INSTALLED:
        print("SKIPPING TEST: GitPython not installed.")
        return

    # Clean up previous runs if needed
    import shutil
    if test_repo_parent.exists():
        print("Cleaning up previous test workspace...")
        # shutil.rmtree(test_repo_parent) # Be careful with recursive delete

    try:
        # 1. Initialize
        print("\n1. Initializing Repo...")
        vc = VersionControl(str(test_repo_path))
        init_ok = vc.init_repo()
        print(f"Init successful: {init_ok}")
        if not init_ok: return # Stop test if init fails

        # 2. Create & Stage a file
        print("\n2. Creating and Staging File...")
        test_file = test_repo_path / "readme.md"
        with open(test_file, "w") as f:
            f.write("# Test Project\n")
        print(f"Created {test_file.name}")
        stage_ok = vc.stage_all_changes()
        print(f"Stage successful: {stage_ok}")
        if not stage_ok: return

        # 3. Commit changes
        print("\n3. Committing Changes...")
        commit_ok = vc.commit_changes("Initial commit - Add readme")
        print(f"Commit successful: {commit_ok}")
        if not commit_ok: return

        # 4. Modify & Stage & Commit again
        print("\n4. Modifying and Committing Again...")
        with open(test_file, "a") as f:
             f.write("\nAdded another line.")
        print(f"Modified {test_file.name}")
        stage_ok_2 = vc.stage_all_changes()
        print(f"Stage successful: {stage_ok_2}")
        commit_ok_2 = vc.commit_changes("Update readme")
        print(f"Commit successful: {commit_ok_2}")

        # 5. Test placeholder remote calls
        print("\n5. Testing Placeholder Remote Calls...")
        create_ok = await vc.create_github_repo("test-repo-name", "DUMMY_TOKEN") # Expect None/False/Warning
        print(f"Create GitHub Repo (Placeholder) Result: {create_ok}")
        push_ok = await vc.push_to_remote() # Expect True (simulated success)/Warning
        print(f"Push (Placeholder) Result: {push_ok}")


        print("\n--- VersionControl Local Ops Test Finished ---")
        print(f"Verify manually: Check for .git folder and content in {test_repo_path}")

    except Exception as e:
        print(f"An error occurred during the VC test: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # Requires Git installed on system and GitPython library
    # pip install GitPython
    import asyncio # Required for the test block
    print(f"Running Version Control Test Block from: {os.getcwd()}")
    asyncio.run(test_version_control_local()) 