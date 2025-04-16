# C:\DreamerAI\tests\week1_check.py - Temporary Check Script for Day 7

import asyncio
import sys
import os
from pathlib import Path

# Adjust path for imports
# Assuming this script is in C:\DreamerAI\tests\
project_root_check = Path(__file__).resolve().parent.parent # C:\DreamerAI
if str(project_root_check) not in sys.path:
    sys.path.insert(0, str(project_root_check))

# Use logger if available, otherwise basic print
try:
    from engine.core.logger import logger_instance as logger
except ImportError:
    logger = None
    print("WARN: Custom logger not found, using basic print statements.")

def log_info(message):
    if logger:
        logger.info(message)
    else:
        print(f"INFO: {message}")

def log_error(message, exc_info=False):
    if logger:
        logger.error(message, exc_info=exc_info)
    else:
        print(f"ERROR: {message}")

async def run_checks():
    log_info("--- Running Week 1 Sanity Checks ---")

    # Check DB Connection
    log_info("\nChecking Database Connection...")
    db = None # Define db outside try block
    db_check_ok = False
    try:
        from engine.core.db import DreamerDB # Import inside function
        db_path = project_root_check / "data" / "db" / "dreamer.db"
        log_info(f"Attempting to connect to DB at: {db_path}")
        db = DreamerDB(db_path=str(db_path)) # Pass path if needed by constructor
        
        # Verify connection/cursor if possible (depends on DreamerDB implementation)
        # Simple check: If instantiation didn't raise error, assume basic connection OK
        log_info("DB Instantiation: OK")
        
        # Optional: Add a dummy entry and retrieve it (if methods exist)
        # test_proj_id = db.add_project("SanityCheck", "system", "C:/path/check")
        # if test_proj_id:
        #     log_info(f"DB Add Project SUCCESS (ID: {test_proj_id})")
        #     retrieved = db.get_project(test_proj_id)
        #     if retrieved:
        #          log_info(f"DB Get Project SUCCESS: {dict(retrieved)}")
        #     else:
        #          log_error("DB Get Project FAILED")
        # else:
        #     log_error("DB Add Project FAILED")
        db_check_ok = True # Mark as OK if instantiation succeeded
    except ImportError:
        log_error("DB Check FAILED: Could not import DreamerDB from engine.core.db")
    except Exception as e:
        log_error(f"DB Check FAILED: {e}", exc_info=True)
    finally:
        if db:
            try:
                db.close()
                log_info("DB Connection closed.")
            except Exception as e_close:
                log_error(f"Error closing DB connection: {e_close}")

    # Check LLM Connection/Instantiation
    log_info("\nChecking LLM Instantiation & Generation...")
    llm_check_ok = False
    llm_instantiation_ok = False
    try:
        from engine.ai.llm import LLM # Import inside function
        # Ensure config files exist before trying to instantiate LLM
        config_path = project_root_check / "data" / "config" / "config.dev.toml"
        env_path = project_root_check / "data" / "config" / ".env.development"
        if not config_path.exists() or not env_path.exists():
             log_error("LLM Check SKIPPED: Config or .env file missing.")
        else:
             llm = LLM()
             log_info("LLM Instantiation: OK")
             llm_instantiation_ok = True
             log_info("Attempting LLM generation (may use Ollama or Cloud)...")
             # Use a simple, non-creative prompt
             response = await llm.generate("Simple test prompt: respond with OK")
             log_info(f"LLM Generate Attempt Response: {response}") 
             # Basic check: Response shouldn't be None or the specific error message
             if response and "ERROR:" not in response:
                  llm_check_ok = True
             else:
                  log_error(f"LLM generation might have failed. Response: {response}")
             log_info("LLM Check: COMPLETE")
    except ImportError:
         log_error("LLM Check FAILED: Could not import LLM from engine.ai.llm")
    except Exception as e:
        log_error(f"LLM Check FAILED: {e}", exc_info=True)

    log_info("\n--- Week 1 Checks Finished ---")
    log_info(f"Database Check Status: {'OK' if db_check_ok else 'FAILED'}")
    log_info(f"LLM Instantiation Status: {'OK' if llm_instantiation_ok else 'FAILED'}")
    log_info(f"LLM Generation Check Status: {'OK' if llm_check_ok else 'FAILED/Check Output'}")

if __name__ == "__main__":
     # Ensure Ollama is running for best test results
     # Ensure .env file has keys for cloud tests if desired
     log_info(f"Running checks from: {os.getcwd()}")
     # Add note about prerequisites
     log_info("NOTE: Requires config/env files, venv active, potentially running Ollama/Redis (for full LLM test).")
     asyncio.run(run_checks()) 