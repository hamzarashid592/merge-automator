import logging
from logging.handlers import TimedRotatingFileHandler
import atexit
import os
from datetime import datetime


class LoggerSetup:
    _handlers_to_close = []

    @staticmethod
    def setup_logger(name, log_file_base, level=logging.INFO):
        """
        Set up a logger with a TimedRotatingFileHandler that creates daily log files.
        
        Parameters:
            name (str): Name of the logger.
            log_file_base (str): Base path for the log file (e.g., logs/git).
            level (int): Logging level (e.g., logging.INFO).
        
        Returns:
            logger: Configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Ensure the logs directory exists
        os.makedirs(os.path.dirname(log_file_base), exist_ok=True)

        # Add today's date to the base log file name
        date_suffix = datetime.now().strftime("%Y-%m-%d")
        log_file_with_date = f"{log_file_base}_{date_suffix}.log"

        # TimedRotatingFileHandler to rotate logs daily
        handler = TimedRotatingFileHandler(
            filename=log_file_with_date,  # Include date in the log file name
            when="midnight",         # Rotate logs at midnight
            interval=1,              # Rotate every 1 day
            backupCount=7,           # Keep logs for the last 7 days
            utc=True                 # Use UTC time for rotation
        )
        handler.suffix = "%Y-%m-%d"  # Suffix for the rotated log files
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

        # Console handler for debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

        logger.propagate = False

        # Register handler for cleanup at program exit
        LoggerSetup._handlers_to_close.append(handler)
        atexit.register(LoggerSetup._close_all_handlers)

        return logger

    @staticmethod
    def _close_all_handlers():
        """
        Ensure all registered handlers are flushed and closed properly at program exit.
        """
        for handler in LoggerSetup._handlers_to_close:
            handler.flush()
            handler.close()
        LoggerSetup._handlers_to_close.clear()  # Clear the list to avoid redundant calls

        logging.shutdown()
        if hasattr(os, 'sync'):
            os.sync()
