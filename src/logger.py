import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger instance with a standard format.
    
    Args:
        name (str): Name of the module requesting the logger.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers if logger already exists
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to console handler
        ch.setFormatter(formatter)
        
        # Add console handler to logger
        logger.addHandler(ch)
        
    return logger
