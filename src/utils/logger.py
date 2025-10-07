"""Logging utility for the Mental Health Dashboard."""

import sys
from pathlib import Path
from loguru import logger
from src.utils.config_loader import get_config


def setup_logger():
    """Configure logger based on config settings."""
    config = get_config()
    log_config = config.config.get('logging', {})
    
    # Remove default handler
    logger.remove()
    
    # Get log level
    log_level = log_config.get('level', 'INFO')
    
    # Console handler
    if 'console' in log_config.get('output', ['console']):
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
    
    # File handler
    if 'file' in log_config.get('output', []):
        log_path = Path(log_config.get('file_path', 'logs/dashboard.log'))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=log_config.get('rotation', '1 day'),
            retention=log_config.get('retention', '30 days'),
            compression="zip"
        )
    
    return logger


# Initialize logger
log = setup_logger()
