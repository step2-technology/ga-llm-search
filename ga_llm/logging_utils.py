# File: ga_llm/logging_utils.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.2
# Description: Structured logger with console and file outputs

import logging
import os
from datetime import datetime

def setup_logger(name: str, log_dir="logs") -> logging.Logger:
    """
    Creates a logger with both file and console handlers.
    Log file is named with timestamp to avoid overwrite.
    """
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(log_dir, f"{name}_{timestamp}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # Avoid duplicate handlers

    # File handler (all logs)
    fh = logging.FileHandler(logfile, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # Console handler (only key info)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
