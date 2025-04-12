import sys
import os
from loguru import logger
from pathlib import Path

class DreamerLogger:
    def __init__(self, log_dir: str = r"C:\DreamerAI\docs\logs", level: str = "DEBUG"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True) # Ensure log directory exists

        # Use static filenames to append to single files
        log_file_path = self.log_dir / "dreamerai_dev.log"
        error_log_path = self.log_dir / "errors.log"
        rules_log_path = self.log_dir / "rules_check.log" # Keep this specific name for rules checks

        # Remove default logger to prevent duplicate console output
        logger.remove()

        # Configure Console Logger
        logger.add(
            sys.stderr,
            level=level.upper(),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )

        # Configure Main Development Log File Sink
        logger.add(
            log_file_path,
            level="DEBUG", # Log debug messages and above to the file
            rotation="10 MB", # Rotate log file when it reaches 10MB
            retention="30 days", # Keep logs for 30 days
            compression="zip", # Compress rotated files
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True # Make logging asynchronous for performance
        )

        # Configure Error Log File Sink
        logger.add(
            error_log_path,
            level="ERROR", # Log only errors and critical messages
            rotation="5 MB",
            retention="90 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}", # Include exception details
            enqueue=True
        )

        # Configure Rules Check Log File Sink (Specific format as required by rules)
        logger.add(
            rules_log_path,
            level="INFO", # Log info level for rule checks
            rotation="1 MB",
            retention="10 days",
            format="{message}", # Special format: "Action: ..., Rules reviewed: Yes, Timestamp: ..."
            filter=lambda record: "rules_check" in record["extra"], # Only log messages with 'rules_check' extra data
            enqueue=True
        )

        self.logger = logger
        self.logger.info("DreamerLogger initialized.")

    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger

# Initialize logger globally for easy import elsewhere
# Note: Consider dependency injection for larger applications
try:
    logger_instance = DreamerLogger().get_logger()
    logger_instance.info("Global logger instance created.")
except Exception as e:
    print(f"FATAL: Failed to initialize logger: {e}")
    # Fallback to basic print if logger fails
    logger_instance = print

# Example specific log function for rules check
def log_rules_check(action: str):
    """Logs a rule check action with the specific required format."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Corrected format string
    # Use .opt(lazy=True) potentially if message formatting is expensive
    # Use .bind() to add the 'extra' data for filtering
    logger_instance.bind(rules_check=True).info(f"Action: {action}, Rules reviewed: Yes, Guide consulted: Yes, Env verified: NA, Timestamp: {timestamp}") # Added missing fields to match rule format

# Example Usage (can be run with `python -m engine.core.logger`)
if __name__ == "__main__":
    logger_instance.debug("This is a debug message.")
    logger_instance.info("This is an info message.")
    logger_instance.warning("This is a warning message.")
    logger_instance.error("This is an error message.")
    log_rules_check("Tested logger initialization") # Use the helper function
    try:
        1 / 0
    except ZeroDivisionError:
        logger_instance.exception("Caught an exception!")

    print(f"Logs should be written to: {Path(r'C:\DreamerAI\docs\logs').resolve()}") 