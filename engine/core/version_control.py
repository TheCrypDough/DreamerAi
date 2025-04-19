# C:\DreamerAI\engine\core\version_control.py
import os
import traceback
from pathlib import Path
from typing import Optional
import asyncio # Added for async placeholders

# Import GitPython - raises ImportError if not installed
try:
    import git
    from git import Repo, GitCommandError
    GITPYTHON_INSTALLED = True
except ImportError:
    git = None
    Repo = None
    GitCommandError = Exception # Define dummy exception
    GITPYTHON_INSTALLED = False

try:
    from .logger import logger_instance as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class VersionControl:
    """Handles Git operations for user projects."""

    def __init__(self, repo_path: str):
        """
        Initializes the VersionControl manager for a specific repository path.

        Args:
            repo_path: The absolute path to the local Git repository.
        """
        self.repo_path = Path(repo_path)
        self.repo: Optional[Repo] = None

        if not GITPYTHON_INSTALLED:
            logger.error("GitPython library is not installed. Version control features disabled.")
            # Optionally raise error or just disable functionality
            return

        # Ensure the base directory exists, but repo might not yet
        self.repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Try to open existing repo, otherwise it stays None until init_repo is called
        if self.repo_path.exists() and (self.repo_path / ".git").is_dir():
            try:
                self.repo = Repo(self.repo_path)
                logger.info(f"Opened existing Git repository at: {self.repo_path}")
            except Exception as e:
                logger.error(f"Failed to open existing repository at {self.repo_path}: {e}")
        else:
            logger.info(f"No existing Git repository found at: {self.repo_path}. Use init_repo() to create one.")

    def init_repo(self, remote_url: Optional[str] = None) -> bool:
        """
        Initializes a new Git repository at the specified path.

        Args:
            remote_url: Optional URL for the 'origin' remote.

        Returns:
            True if initialization was successful or repo already exists, False otherwise.
        """
        if not GITPYTHON_INSTALLED: return False
        if self.repo:
            logger.warning(f"Repository already initialized at {self.repo_path}")
            # Optionally verify remote if passed?
            return True

        logger.info(f"Initializing new Git repository at: {self.repo_path}")
        try:
            # Ensure the directory itself exists before initializing
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.init(self.repo_path)
            logger.info("Repository initialized successfully.")
            if remote_url:
                try:
                    self.repo.create_remote("origin", remote_url)
                    logger.info(f"Added remote 'origin': {remote_url}")
                except Exception as e: # Catch potential errors if remote already exists
                     logger.warning(f"Could not add remote 'origin' ({remote_url}): {e}")
                     # If remote exists, maybe try setting url instead? repo.remotes.origin.set_url(remote_url)
            return True
        except GitCommandError as e:
            logger.error(f"Git command failed during init: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}\n{traceback.format_exc()}")

        self.repo = None # Ensure repo is None on failure
        return False

    def stage_all_changes(self) -> bool:
        """Stages all changes (added, modified, deleted) in the repository."""
        if not self.repo:
            logger.error("Cannot stage changes: Repository not initialized or loaded.")
            return False
        logger.debug("Staging all changes...")
        try:
            self.repo.git.add(all=True)
            logger.info("All changes staged.")
            return True
        except GitCommandError as e:
            logger.error(f"Git command failed during staging: {e}")
            return False
        except Exception as e:
             logger.error(f"Unexpected error during staging: {e}")
             return False

    def commit_changes(self, message: str) -> bool:
        """
        Commits staged changes with the provided message.

        Args:
            message: The commit message.

        Returns:
            True if commit was successful, False otherwise.
        """
        if not self.repo:
            logger.error("Cannot commit: Repository not initialized or loaded.")
            return False
        if not message:
            logger.error("Cannot commit: Commit message cannot be empty.")
            return False

        logger.info(f"Attempting commit with message: '{message}'")
        try:
            # Check if there's anything staged to commit
            # Handle case where HEAD doesn't exist yet (first commit)
            is_first_commit = not self.repo.head.is_valid()
            has_staged_changes = False
            if not is_first_commit:
                # If not the first commit, check diff against HEAD
                has_staged_changes = self.repo.index.diff("HEAD") is not None
            else:
                # If it IS the first commit, any staged changes count
                # Check if the index has entries (this is a bit indirect, might need refinement)
                has_staged_changes = bool(self.repo.index.entries)

            # Also consider untracked files just added
            has_untracked_staged = bool(self.repo.untracked_files)

            if not has_staged_changes and not has_untracked_staged and not self.repo.is_dirty(index=False, working_tree=False, untracked_files=False):
                 logger.warning("No changes staged or modified; nothing to commit.")
                 return True # Arguably success, as state is clean

            self.repo.index.commit(message)
            logger.info("Commit successful.")
            return True
        except GitCommandError as e:
            logger.error(f"Git command failed during commit: {e}")
            # Specific error for empty commit:
            if "nothing to commit" in str(e).lower() or "no changes added to commit" in str(e).lower():
                 logger.warning("Caught 'nothing to commit' error, treating as non-failure.")
                 return True
            return False
        except Exception as e:
            logger.error(f"Unexpected error during commit: {e}\n{traceback.format_exc()}")
            return False

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