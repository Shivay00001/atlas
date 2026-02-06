"""
ShivAI Atlas - Logging System
Centralized logging with file and console output
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

class AtlasLogger:
    """Custom logger for ShivAI Atlas"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            AtlasLogger._initialized = True
    
    def _setup_logging(self):
        """Setup logging configuration"""
        from .config import config, LOGS_DIR
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (rotating)
        file_handler = RotatingFileHandler(
            config.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Create specialized loggers
        self.agent_logger = self._create_logger('atlas.agents', LOGS_DIR / 'agents.log')
        self.automation_logger = self._create_logger('atlas.automation', LOGS_DIR / 'automation.log')
        self.security_logger = self._create_logger('atlas.security', LOGS_DIR / 'security.log')
        self.api_logger = self._create_logger('atlas.api', LOGS_DIR / 'api.log')
    
    def _create_logger(self, name: str, log_file: Path) -> logging.Logger:
        """Create a specialized logger"""
        logger = logging.getLogger(name)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger by name"""
        return logging.getLogger(name)
    
    def log_agent_action(self, agent_name: str, action: str, details: dict):
        """Log agent actions"""
        self.agent_logger.info(f"{agent_name} - {action} - {details}")
    
    def log_automation(self, tool: str, action: str, result: str, params: dict = None):
        """Log automation actions"""
        msg = f"Tool: {tool} | Action: {action} | Result: {result}"
        if params:
            msg += f" | Params: {params}"
        self.automation_logger.info(msg)
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """Log security-related events"""
        log_func = getattr(self.security_logger, severity.lower(), self.security_logger.info)
        log_func(f"{event_type} - {details}")
    
    def log_api_request(self, method: str, endpoint: str, status: int, duration: float):
        """Log API requests"""
        self.api_logger.info(f"{method} {endpoint} - Status: {status} - Duration: {duration:.3f}s")

# Global logger instance
atlas_logger = AtlasLogger()

def get_logger(name: str = "atlas") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
