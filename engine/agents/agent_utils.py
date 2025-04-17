# C:\DreamerAI\engine\agents\agent_utils.py
# Utility functions shared across agents

import os
import traceback
from pathlib import Path

# Add project root for sibling imports
import sys
project_root_utils = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_utils not in sys.path:
    sys.path.insert(0, project_root_utils)

try:
    from engine.core.logger import logger_instance as logger # Use main logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Could not import central logger in agent_utils. Using standard logging.")

def save_code_to_file(output_path: Path, content: str):
    """Saves generated code content to the specified path, creating dirs."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Code successfully saved to {output_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to save code to {output_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving code to {output_path}: {e}\n{traceback.format_exc()}")
        return False

# Example Usage / Test Block (Optional)
if __name__ == "__main__":
    print("Testing save_code_to_file utility...")
    test_dir = Path("./test_agent_utils_output")
    test_file_path = test_dir / "subdir" / "test_output.txt"
    test_content = "Hello from agent_utils test!"

    if save_code_to_file(test_file_path, test_content):
        print(f"Successfully saved to {test_file_path}")
        # Verify content
        try:
            with open(test_file_path, "r", encoding="utf-8") as f:
                read_content = f.read()
            print(f"Read back content: '{read_content}'")
            if read_content == test_content:
                print("Content verification PASSED.")
            else:
                print("Content verification FAILED.")
        except Exception as e:
            print(f"Error reading back file: {e}")
    else:
        print(f"Failed to save file.")

    # Clean up (optional)
    # import shutil
    # if test_dir.exists():
    #     shutil.rmtree(test_dir)
    #     print(f"Cleaned up test directory: {test_dir}") 