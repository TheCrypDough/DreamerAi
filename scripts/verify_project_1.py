import sys
import os
from pathlib import Path

# Ensure the project root is in the path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"PYTHON_VERIFY: Checking for Project ID 1...")

exists = False
error_message = None

try:
    # Use the shared instance, assuming server.py/other modules manage its lifecycle fine
    # If this fails, it indicates a deeper issue with db initialization
    from engine.core.db import db_instance
    print(f"PYTHON_VERIFY: Imported db_instance.")

    project = db_instance.get_project(1)
    if project:
        print(f"PYTHON_VERIFY: Found project data: {dict(project)}")
        exists = True
    else:
        print(f"PYTHON_VERIFY: Project ID 1 not found in database.")
        exists = False

except ImportError as e:
    error_message = f"ImportError: {e}. Ensure engine.core.db exists and is importable."
    print(f"PYTHON_VERIFY: {error_message}")
except Exception as e:
    import traceback
    error_message = f"Exception: {e}\n{traceback.format_exc()}"
    print(f"PYTHON_VERIFY: {error_message}")
finally:
    # Avoid closing the shared db_instance connection here,
    # as it might be in use by the running server process.
    # Let the main application manage its lifecycle.
    print(f"PYTHON_VERIFY: Check complete. Project Exists: {exists}")

# Exit with 0 if exists, 1 if not or error, for potential scripting use
sys.exit(0 if exists else 1) 