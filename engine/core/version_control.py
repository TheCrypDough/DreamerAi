# C:\DreamerAI\engine\core\version_control.py
import os
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio # Added for async placeholders
import git
import logging
from engine.core.logger import logger_instance # Correct import
import requests # For GitHub API

# Import GitPython - raises ImportError if not installed
try:
    from git import Repo, GitCommandError, PushInfo
    GITPYTHON_INSTALLED = True
except ImportError:
    git = None  # type: ignore
    Repo = None  # type: ignore
    GitCommandError = Exception  # type: ignore
    PushInfo = None  # type: ignore
    GITPYTHON_INSTALLED = False

# Setup logging
logger = logger_instance # Use the imported instance

class VersionControl:
    """ V2: Handles Local and Remote Git/GitHub operations asynchronously. """

    def __init__(self, repo_path: str):
        """ Initializes the VersionControl manager for a specific repository path. """
        self.repo_path = Path(repo_path)
        self.repo: Optional[Repo] = None

        if not GITPYTHON_INSTALLED:
            logger.error("GitPython library is not installed. Version control features disabled.")
            return

        # Ensure the repo path itself exists if we're operating on it
        if not self.repo_path.is_dir():
             # Maybe create it? Or assume caller ensures it exists? V1 Assume parent exists.
             self.repo_path.mkdir(parents=True, exist_ok=True)
             logger.warning(f"Repo path {self.repo_path} did not exist, created.")
             # If just created, no .git dir will exist yet

        if (self.repo_path / ".git").is_dir():
            try:
                self.repo = Repo(self.repo_path)
                logger.info(f"Opened existing Git repository at: {self.repo_path}")
            except Exception as e:
                logger.error(f"Failed to open existing repository at {self.repo_path}: {e}")
        else:
            logger.info(f"No existing Git repository found at: {self.repo_path}. Use init_repo() to create one.")

    # --- Local Operations (Keep Sync V1 unless causing blocking issues) ---
    def init_repo(self, remote_url: Optional[str] = None) -> bool:
        if not GITPYTHON_INSTALLED: return False
        if self.repo: logger.warning(f"Repo already exists at {self.repo_path}"); return True
        logger.info(f"Initializing new Git repo at: {self.repo_path}")
        try:
            self.repo = Repo.init(self.repo_path)
            logger.info("Local repository initialized successfully.")
            if remote_url: self._set_origin_remote(remote_url)
            return True
        except Exception as e: logger.exception(f"Failed to initialize repo: {e}"); self.repo=None; return False

    def _set_origin_remote(self, url: str) -> bool:
        if not self.repo: return False
        try:
            origin = self.repo.remote(name='origin')
            if origin.url != url:
                with origin.config_writer as cw: cw.set("url", url)
                logger.info(f"Updated remote 'origin' URL to: {url}")
            else: logger.debug("Remote 'origin' URL already set.")
        except ValueError: # Remote doesn't exist
            self.repo.create_remote('origin', url)
            logger.info(f"Added remote 'origin': {url}")
        except Exception as e: logger.error(f"Failed setting remote 'origin' to {url}: {e}"); return False
        return True

    def stage_all_changes(self) -> bool:
        if not self.repo: logger.error("Stage fail: Repo not loaded."); return False
        logger.debug("Staging all changes...");
        try: self.repo.git.add(all=True); logger.info("All changes staged."); return True
        except Exception as e: logger.error(f"Staging error: {e}"); return False

    def commit_changes(self, message: str) -> bool:
        if not self.repo: logger.error("Commit fail: Repo not loaded."); return False
        if not message: logger.error("Commit fail: Message empty."); return False
        logger.info(f"Attempting commit: '{message}'")
        try:
            # Check for changes BEFORE trying to commit
            if not self.repo.is_dirty(untracked_files=True) and not self.repo.index.diff("HEAD"):
                 logger.warning("Commit skipped: No changes staged or modified."); return True
            self.repo.index.commit(message); logger.info("Commit successful."); return True
        except GitCommandError as e:
            if "nothing to commit" in str(e).lower(): logger.warning("Commit reported no changes."); return True
            logger.error(f"Commit GitCommandError: {e}"); return False
        except Exception as e: logger.exception(f"Commit error: {e}"); return False

    def get_status(self) -> Dict[str, Any]:
        if not self.repo: return {"status":"uninitialized", "error":"Repo not loaded."}
        try:
             branch = self.repo.active_branch.name; is_dirty = self.repo.is_dirty(untracked_files=True)
             staged = bool(self.repo.index.diff("HEAD")); untracked = len(self.repo.untracked_files)
             log = self.repo.git.log('-1', '--pretty=%h %s');
             return {"status": "ready", "branch": branch, "is_dirty": is_dirty, "has_staged_changes": staged, "untracked_files": untracked, "last_commit": log.strip() if log else "None"}
        except Exception as e: logger.error(f"Error getting status: {e}"); return {"status":"error", "error": f"{e}"}

    # --- Functional Async Remote Operations ---

    async def create_github_repo(self, name: str, token: str, private: bool = False) -> Optional[str]:
        """ ASYNC: Creates a GitHub repo using requests API call in executor. Sets local origin. """
        if not token: logger.error("Cannot create repo: GitHub token missing."); return None
        api_url = "https://api.github.com/user/repos"
        headers = { "Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json", "X-GitHub-Api-Version": "2022-11-28" }
        payload = { "name": name, "private": private, "auto_init": False }
        logger.info(f"Async create GitHub repo '{name}' via API...")

        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None,
                lambda: requests.post(api_url, headers=headers, json=payload, timeout=20)
            )
            response.raise_for_status() # Raise HTTPError for 4xx/5xx

            if response.status_code == 201:
                repo_data = response.json(); clone_url = repo_data.get("clone_url")
                if not clone_url: logger.error("GitHub API response missing clone_url."); return None
                logger.info(f"Async GitHub repo created successfully: {clone_url}")
                # Attempt to set remote AFTER repo creation confirmed
                self._set_origin_remote(clone_url)
                return clone_url
            else:
                logger.error(f"Unexpected success status {response.status_code} creating repo: {response.text}")
                return None
        except requests.exceptions.HTTPError as http_err:
             # Log specific error for repo already exists (422) or auth issue (401)
             status_code = http_err.response.status_code
             error_text = http_err.response.text
             logger.error(f"HTTP error creating GitHub repo '{name}': {status_code} - {error_text}")
             if status_code == 422: logger.error("-> This likely means the repository name already exists on GitHub.")
             elif status_code == 401: logger.error("-> This likely means the GitHub token is invalid or lacks 'repo' scope.")
        except requests.exceptions.RequestException as req_err: logger.error(f"Network error creating repo '{name}': {req_err}")
        except Exception as e: logger.exception(f"Unexpected error creating repo '{name}': {e}")
        return None

    async def push_to_remote(self, remote_name: str = "origin", branch: Optional[str] = None) -> bool:
        """
        ASYNC: Pushes to remote using GitPython in executor.
        *** V1 RELIES ON SYSTEM-LEVEL GIT AUTH (SSH Key/HTTPS Helper). Token NOT used here. ***
        """
        logger.warning(f"Attempting ASYNC push to '{remote_name}'. [V1 RELIES ON SYSTEM GIT AUTH: SSH/Helper]")
        if not self.repo: logger.error("Push fail: Repo not loaded."); return False
        if not GITPYTHON_INSTALLED: logger.error("Push fail: GitPython missing."); return False
        try: remote = self.repo.remote(name=remote_name)
        except ValueError: logger.error(f"Push fail: Remote '{remote_name}' missing."); return False

        try:
            target_branch = branch or self.repo.active_branch.name
            logger.info(f"Attempting async push: {target_branch} -> {remote_name}...")
            loop = asyncio.get_running_loop()
            # Run blocking GitPython push call in executor
            # Need to pass necessary arguments to the push lambda if not accessible via self
            # push_lambda = lambda: remote.push(refspec=f'{target_branch}:{target_branch}')
            # Simplified: Assume remote and target_branch are stable
            push_infos = await loop.run_in_executor(None, remote.push, f'{target_branch}:{target_branch}')

            # Analyze PushInfo flags (more detailed logging)
            push_failed = False; failure_details = []
            for info in push_infos:
                if info.flags & PushInfo.ERROR: failure_details.append(f"[ERROR {info.local_ref or 'N/A'}] {info.summary}")
                if info.flags & PushInfo.REJECTED: failure_details.append(f"[REJECTED {info.local_ref or 'N/A'}] {info.summary}")
                if info.flags & PushInfo.REMOTE_REJECTED: failure_details.append(f"[REMOTE_REJ {info.local_ref or 'N/A'}] {info.summary}")
                if info.flags & PushInfo.REMOTE_FAILURE: failure_details.append(f"[REMOTE_FAIL {info.local_ref or 'N/A'}] {info.summary}")
            if failure_details:
                 logger.error(f"Push failed. Details: {'; '.join(failure_details)}")
                 return False
            else:
                 logger.info(f"Push command executed successfully for branch '{target_branch}' to remote '{remote_name}'.")
                 return True
        except GitCommandError as e:
            error_detail = str(e.stderr or e.stdout or e).strip() # Get most specific error
            logger.error(f"Push failed (GitCommandError): {error_detail}")
            if "permission denied" in error_detail.lower() or "authentication failed" in error_detail.lower():
                logger.error(">>> Push Error suggests SYSTEM Git Authentication Failure! Configure SSH Key or HTTPS Credential Helper. <<<")
            return False
        except Exception as e: logger.exception(f"Unexpected error during async push: {e}"); return False

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