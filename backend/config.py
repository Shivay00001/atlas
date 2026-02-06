"""
ShivAI Atlas - Core Configuration Module
Manages all system settings, paths, and environment variables
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "db"
TEMPLATES_DIR = DATA_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"
GENERATED_APPS_DIR = BASE_DIR / "generated_apps"

# Ensure directories exist
for directory in [DATA_DIR, DB_DIR, TEMPLATES_DIR, LOGS_DIR, GENERATED_APPS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

@dataclass
class PermissionsConfig:
    """User consent-based permissions"""
    can_access_files: bool = False
    can_control_keyboard_mouse: bool = False
    can_capture_screen: bool = False
    can_control_android: bool = False
    can_control_enterchat: bool = False
    can_use_network: bool = False
    can_use_ai_remote: bool = False
    ask_every_time_files: bool = True
    ask_every_time_keyboard: bool = True
    ask_every_time_screen: bool = True
    ask_every_time_android: bool = True
    ask_every_time_enterchat: bool = True

@dataclass
class VoiceConfig:
    """Voice engine configuration"""
    enabled: bool = True
    language: str = "hi-IN"  # Hindi by default
    fallback_language: str = "en-US"
    tts_rate: int = 150
    tts_volume: float = 0.9
    use_offline_sr: bool = False
    vosk_model_path: Optional[str] = None

@dataclass
class EnterChatConfig:
    """EnterChat integration configuration"""
    enabled: bool = False
    api_url: str = "http://localhost:9000"
    api_key: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3

@dataclass
class AndroidConfig:
    """Android ADB configuration"""
    enabled: bool = False
    adb_path: Optional[str] = None
    device_id: Optional[str] = None
    connection_timeout: int = 10

@dataclass
class AIServiceConfig:
    """AI/LLM service configuration"""
    enabled: bool = False
    provider: str = "anthropic"  # anthropic, openai, local
    api_key: Optional[str] = None
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000
    temperature: float = 0.7

class AtlasConfig:
    """Main configuration manager for ShivAI Atlas"""
    
    CONFIG_FILE = DATA_DIR / "config.json"
    
    def __init__(self):
        self.permissions = PermissionsConfig()
        self.voice = VoiceConfig()
        self.enterchat = EnterChatConfig()
        self.android = AndroidConfig()
        self.ai_service = AIServiceConfig()
        
        # Server settings
        self.server_host = "0.0.0.0"
        self.server_port = 8000
        self.debug_mode = False
        
        # Database
        self.db_path = DB_DIR / "atlas.db"
        
        # Logging
        self.log_level = "INFO"
        self.log_file = LOGS_DIR / "atlas.log"
        
        # Load from file if exists
        self.load()
    
    def load(self) -> bool:
        """Load configuration from JSON file"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Load permissions
                    if 'permissions' in data:
                        self.permissions = PermissionsConfig(**data['permissions'])
                    
                    # Load voice config
                    if 'voice' in data:
                        self.voice = VoiceConfig(**data['voice'])
                    
                    # Load enterchat config
                    if 'enterchat' in data:
                        self.enterchat = EnterChatConfig(**data['enterchat'])
                    
                    # Load android config
                    if 'android' in data:
                        self.android = AndroidConfig(**data['android'])
                    
                    # Load AI service config
                    if 'ai_service' in data:
                        self.ai_service = AIServiceConfig(**data['ai_service'])
                    
                    # Load server settings
                    if 'server' in data:
                        self.server_host = data['server'].get('host', self.server_host)
                        self.server_port = data['server'].get('port', self.server_port)
                        self.debug_mode = data['server'].get('debug', self.debug_mode)
                    
                    # Load logging settings
                    if 'logging' in data:
                        self.log_level = data['logging'].get('level', self.log_level)
                
                return True
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
        return False
    
    def save(self) -> bool:
        """Save configuration to JSON file"""
        try:
            data = {
                'permissions': asdict(self.permissions),
                'voice': asdict(self.voice),
                'enterchat': asdict(self.enterchat),
                'android': asdict(self.android),
                'ai_service': asdict(self.ai_service),
                'server': {
                    'host': self.server_host,
                    'port': self.server_port,
                    'debug': self.debug_mode
                },
                'logging': {
                    'level': self.log_level
                }
            }
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'permissions': asdict(self.permissions),
            'voice': asdict(self.voice),
            'enterchat': asdict(self.enterchat),
            'android': asdict(self.android),
            'ai_service': asdict(self.ai_service),
            'server': {
                'host': self.server_host,
                'port': self.server_port,
                'debug': self.debug_mode
            },
            'paths': {
                'base': str(BASE_DIR),
                'data': str(DATA_DIR),
                'db': str(DB_DIR),
                'templates': str(TEMPLATES_DIR),
                'logs': str(LOGS_DIR),
                'generated_apps': str(GENERATED_APPS_DIR)
            }
        }

# Global config instance
config = AtlasConfig()
