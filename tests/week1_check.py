import asyncio
import sys
import os

# Adjust path for imports
project_root_check = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_check not in sys.path:
    sys.path.insert(0, project_root_check)

async def run_checks():
    print("--- Running Week 1 Sanity Checks ---")

    # Check DB Connection
    print("\nChecking Database Connection...")
    db = None # Define db outside try block
    test_proj_id = None # Define test_proj_id outside try block
    try:
        from engine.core.db import DreamerDB # Import inside function
        db = DreamerDB()
        # Add a dummy entry and retrieve it
        test_proj_id = db.add_project("SanityCheck", "system", "C:/path/check") # Use forward slashes for path consistency
        if test_proj_id:
             print(f"DB Add Project SUCCESS (ID: {test_proj_id})")
             retrieved = db.get_project(test_proj_id)
             if retrieved:
                 # Convert Row object to dict for printing
                 print(f"DB Get Project SUCCESS: {dict(retrieved)}")
             else:
                 print("DB Get Project FAILED")
        else:
            print("DB Add Project FAILED")
        print("DB Check: OK")
    except Exception as e:
        print(f"DB Check FAILED: {e}")
    finally:
        if db:
            # Clean up dummy entry
            if test_proj_id:
                try:
                    db.delete_project(test_proj_id)
                    print(f"DB Cleaned up dummy project ID: {test_proj_id}")
                except Exception as e_del:
                    print(f"DB Cleanup FAILED for project ID {test_proj_id}: {e_del}")
            try:
                db.close()
                print("DB Connection closed.")
            except Exception as e_close:
                 print(f"DB Close FAILED: {e_close}")


    # Check LLM Connection/Instantiation
    print("\nChecking LLM Instantiation & Generation...")
    try:
        from engine.ai.llm import LLM # Import inside function
        llm = LLM()
        print("LLM Instantiation: OK")
        print("Attempting LLM generation (may use Ollama or Cloud)...")
        # Ensure Ollama is running or relevant API keys are in .env
        response = await llm.generate("Simple test prompt: respond with OK")
        print(f"LLM Generate Attempt Response: {response}") # Will show AI response or error message
        print("LLM Check: COMPLETE (Check response validity)")
    except Exception as e:
        print(f"LLM Check FAILED: {e}")

    print("\n--- Week 1 Checks Finished ---")

if __name__ == "__main__":
     # Ensure Ollama is running for best test results
     # Ensure .env file has keys for cloud tests if desired
     print(f"Running checks from: {os.getcwd()}")
     asyncio.run(run_checks()) 