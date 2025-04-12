import asyncio
import sys
import os

# Adjust path to import from engine
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

print(f"Python Executable: {sys.executable}")
print(f"System Path: {sys.path}")

async def test_llm():
    print("\n--- Testing LLM ---")
    try:
        # Ensure imports happen *after* path adjustment
        from engine.ai.llm import LLM
        print("LLM imported successfully.")
        llm_instance = LLM()
        print("LLM instantiated successfully.")
        # Note: Actual generation might require configuration/models
        # This is a basic check of the method call structure
        # response = await llm_instance.generate("test prompt")
        # print(f"LLM generate called (mock response for now): {response}")
        print("LLM generate structure looks okay (actual call commented out for now).")
    except ImportError as e:
        print(f"LLM Import Error: {e}. Check structure and dependencies.")
    except Exception as e:
        print(f"LLM Error: {e}")

def test_db():
    print("\n--- Testing DreamerDB ---")
    db_instance = None
    test_proj_id = None # Keep track of ID for potential cleanup/verification
    try:
        # Ensure imports happen *after* path adjustment
        from engine.core.db import DreamerDB
        print("DreamerDB imported successfully.")
        db_instance = DreamerDB()
        print("DreamerDB instantiated successfully.")

        # Add a dummy entry and retrieve it
        print("Attempting to add dummy project 'SanityCheck'...")
        test_proj_id = db_instance.add_project("SanityCheck", "system", "C:/path/check") # Using path from example
        if test_proj_id:
             print(f"DB Add Project SUCCESS (ID: {test_proj_id})")
             print(f"Attempting to retrieve project ID: {test_proj_id}...")
             retrieved = db_instance.get_project(test_proj_id)
             if retrieved:
                 # Convert Row object to dict for printing if necessary
                 try:
                     retrieved_dict = dict(retrieved)
                     print(f"DB Get Project SUCCESS: {retrieved_dict}")
                 except TypeError: # Handle potential issues if conversion isn't direct
                     print(f"DB Get Project SUCCESS (raw row): {retrieved}")

             else:
                 print("DB Get Project FAILED")
                 # Log this as an issue if retrieval fails after successful add
        else:
            print("DB Add Project FAILED")
            # Log this as an issue

        print("DB Check: OK (Add/Get attempted)")

    except ImportError as e:
        print(f"DreamerDB Import Error: {e}. Check structure and dependencies.")
    except Exception as e:
        print(f"DreamerDB Error during Add/Get: {e}")
    finally:
        if db_instance:
            # Optional: Add cleanup logic here if needed, e.g., delete test_proj_id
            # Consider if the test DB should be ephemeral or if cleanup is manual
            try:
                db_instance.close()
                print("DreamerDB connection closed.")
            except Exception as e:
                print(f"Error closing DreamerDB connection: {e}")

if __name__ == "__main__":
    print("--- Starting Week 1 Basic Functionality Check (Updated) ---")
    # Ensure Ollama is running for best test results
    # Ensure .env file has keys for cloud tests if desired
    print(f"Running checks from: {os.getcwd()}")
    test_db() # Run DB test first
    asyncio.run(test_llm()) # Then run async LLM test
    print("\n--- Check Complete ---") 