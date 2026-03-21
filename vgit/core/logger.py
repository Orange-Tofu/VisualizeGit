# core/logger.py
import logging
import os
from pathlib import Path

def setup_logger():
    """Configure a basic logger that writes to ~/.vgit/debug.log"""
    log_dir = Path.home() / ".vgit"
    log_file = log_dir / "debug.log"
    
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If we can't create the log dir, we might have issues writing.
        # But we won't crash here.
        pass

    logger = logging.getLogger("vgit")
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding multiple handlers if called repeatedly
    if not logger.handlers:
        try:
            handler = logging.FileHandler(str(log_file), encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except Exception:
            # Fallback to no-op handler if file is not writable
            logger.addHandler(logging.NullHandler())
            
    return logger

# Single instance for the application
logger = setup_logger()
