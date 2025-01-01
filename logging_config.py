import logging
from logging.handlers import RotatingFileHandler
import atexit
import os


class LoggerSetup:
    _handlers_to_close = []

    @staticmethod
    def setup_logger(name, log_file, level=logging.INFO, max_bytes=5000000, backup_count=2):
        """
        Set up a logger with rotating file handler and console handler.

        Parameters:
            name (str): Name of the logger.
            log_file (str): Path to the log file.
            level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
            max_bytes (int): Maximum size of the log file in bytes before rotation.
            backup_count (int): Number of backup files to keep.

        Returns:
            logger: Configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # File handler with rotation
        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

        # Console handler
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
