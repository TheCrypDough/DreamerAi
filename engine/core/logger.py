import sys
import os
from loguru import logger
from pathlib import Path
from datetime import datetime

class DreamerLogger:
    def __init__(self, log_dir: str = r"C:\DreamerAI\docs\logs", level: str = "DEBUG"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        dev_log_dir = self.log_dir / "dev_logs"
        error_log_dir = self.log_dir / "raw_error_logs"
        dev_log_dir.mkdir(parents=True, exist_ok=True)
        error_log_dir.mkdir(parents=True, exist_ok=True)

        log_file_path = dev_log_dir / "dreamerai_dev_{time:YYYY-MM-DD}.log"
        error_log_path = error_log_dir / "errors_{time:YYYY-MM-DD}.log"
        rules_log_path = self.log_dir / "rules_check.log"

        logger.remove()

        logger.add(
            sys.stderr,
            level=level.upper(),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )

        logger.add(
            log_file_path,
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True
        )

        logger.add(
            error_log_path,
            level="ERROR",
            rotation="5 MB",
            retention="90 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
            enqueue=True
        )

        logger.add(
            rules_log_path,
            level="INFO",
            rotation="1 MB",
            retention="10 days",
            format="{message}",
            filter=lambda record: "rules_check" in record["extra"],
            enqueue=True
        )

        self.logger = logger
        self.logger.info("DreamerLogger initialized.")

    def get_logger(self):
        """Returns the configured logger instance.""" 
        return self.logger

try:
    logger_instance = DreamerLogger().get_logger()
    logger_instance.info("Global logger instance created.")
except Exception as e:
    print(f"FATAL: Failed to initialize logger: {e}")
    logger_instance = print

def log_rules_check(action: str):
    """Logs a rule check action with the specific required format."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger_instance.bind(rules_check=True).info(f"Action: {action}, Rules reviewed: Yes, Timestamp: {timestamp}")

# Example Usage (can be run with `python -m engine.core.logger`)
if __name__ == "__main__":
    logger_instance.debug("This is a debug message.")
    logger_instance.info("This is an info message.")
    logger_instance.warning("This is a warning message.")
    logger_instance.error("This is an error message.")
    log_rules_check("Tested logger initialization")
    try:
        1 / 0
    except ZeroDivisionError:
        logger_instance.exception("Caught an exception!")

    print(f"Logs should be written to: {Path(r'C:\DreamerAI\docs\logs').resolve()}") 