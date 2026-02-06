"""
ShivAI Atlas - Permissions & Safety System
User consent-based access control for all capabilities
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict
import logging

from .config import config, DATA_DIR
from .logger import get_logger

logger = get_logger(__name__)

class PermissionType(Enum):
    """Types of permissions in Atlas"""
    FILES = "files"
    KEYBOARD_MOUSE = "keyboard_mouse"
    SCREEN_CAPTURE = "screen_capture"
    ANDROID = "android"
    ENTERCHAT = "enterchat"
    NETWORK = "network"
    AI_REMOTE = "ai_remote"

class RiskLevel(Enum):
    """Risk levels for actions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PermissionRequest:
    """Represents a permission request"""
    permission_type: PermissionType
    action: str
    description: str
    risk_level: RiskLevel
    params: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            'permission_type': self.permission_type.value,
            'action': self.action,
            'description': self.description,
            'risk_level': self.risk_level.value,
            'params': self.params,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class AuditLogEntry:
    """Audit log entry for tracking actions"""
    timestamp: datetime
    action: str
    permission_type: str
    risk_level: str
    status: str  # granted, denied, executed, failed
    details: Dict[str, Any]
    agent: str
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'permission_type': self.permission_type,
            'risk_level': self.risk_level,
            'status': self.status,
            'details': self.details,
            'agent': self.agent
        }

class PermissionManager:
    """Manages all permission checking and auditing"""
    
    AUDIT_LOG_FILE = DATA_DIR / "audit_log.jsonl"
    PENDING_REQUESTS_FILE = DATA_DIR / "pending_requests.json"
    
    def __init__(self):
        self.pending_requests: List[PermissionRequest] = []
        self._load_pending_requests()
    
    def _load_pending_requests(self):
        """Load pending permission requests from disk"""
        try:
            if self.PENDING_REQUESTS_FILE.exists():
                with open(self.PENDING_REQUESTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert back to PermissionRequest objects
                    self.pending_requests = [
                        PermissionRequest(
                            permission_type=PermissionType(req['permission_type']),
                            action=req['action'],
                            description=req['description'],
                            risk_level=RiskLevel(req['risk_level']),
                            params=req['params'],
                            timestamp=datetime.fromisoformat(req['timestamp'])
                        ) for req in data
                    ]
        except Exception as e:
            logger.error(f"Failed to load pending requests: {e}")
    
    def _save_pending_requests(self):
        """Save pending requests to disk"""
        try:
            with open(self.PENDING_REQUESTS_FILE, 'w', encoding='utf-8') as f:
                data = [req.to_dict() for req in self.pending_requests]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save pending requests: {e}")
    
    def check_permission(self, permission_type: PermissionType, action: str, 
                        risk_level: RiskLevel = RiskLevel.MEDIUM,
                        params: Dict[str, Any] = None) -> tuple[bool, Optional[str]]:
        """
        Check if an action is permitted
        Returns: (is_granted, reason_if_denied)
        """
        params = params or {}
        
        # Map permission types to config flags
        permission_map = {
            PermissionType.FILES: config.permissions.can_access_files,
            PermissionType.KEYBOARD_MOUSE: config.permissions.can_control_keyboard_mouse,
            PermissionType.SCREEN_CAPTURE: config.permissions.can_capture_screen,
            PermissionType.ANDROID: config.permissions.can_control_android,
            PermissionType.ENTERCHAT: config.permissions.can_control_enterchat,
            PermissionType.NETWORK: config.permissions.can_use_network,
            PermissionType.AI_REMOTE: config.permissions.can_use_ai_remote,
        }
        
        # Check if permission is enabled
        if not permission_map.get(permission_type, False):
            reason = f"Permission {permission_type.value} is disabled. Enable it in Settings."
            logger.warning(f"Permission denied: {reason}")
            self._log_audit(action, permission_type.value, risk_level.value, "denied", 
                          {"reason": reason}, "system")
            return False, reason
        
        # Check "ask every time" flags
        ask_every_time_map = {
            PermissionType.FILES: config.permissions.ask_every_time_files,
            PermissionType.KEYBOARD_MOUSE: config.permissions.ask_every_time_keyboard,
            PermissionType.SCREEN_CAPTURE: config.permissions.ask_every_time_screen,
            PermissionType.ANDROID: config.permissions.ask_every_time_android,
            PermissionType.ENTERCHAT: config.permissions.ask_every_time_enterchat,
        }
        
        if ask_every_time_map.get(permission_type, False):
            # Create pending request for user confirmation
            request = PermissionRequest(
                permission_type=permission_type,
                action=action,
                description=self._get_action_description(action, params),
                risk_level=risk_level,
                params=params,
                timestamp=datetime.now()
            )
            self.pending_requests.append(request)
            self._save_pending_requests()
            
            logger.info(f"Permission request created for: {action}")
            return False, "User confirmation required. Check pending requests."
        
        # Permission granted
        self._log_audit(action, permission_type.value, risk_level.value, "granted", 
                      params, "system")
        return True, None
    
    def _get_action_description(self, action: str, params: Dict[str, Any]) -> str:
        """Generate human-readable description of action"""
        descriptions = {
            'delete_file': f"Delete file: {params.get('path', 'unknown')}",
            'create_file': f"Create file: {params.get('path', 'unknown')}",
            'execute_command': f"Execute: {params.get('command', 'unknown')}",
            'take_screenshot': "Capture screen screenshot",
            'control_mouse': "Control mouse movements",
            'control_keyboard': f"Type text: {params.get('text', 'unknown')}",
            'adb_command': f"Android command: {params.get('command', 'unknown')}",
            'send_message': f"Send message via EnterChat to {params.get('recipient', 'unknown')}",
            'network_request': f"Make network request to {params.get('url', 'unknown')}",
        }
        return descriptions.get(action, f"Action: {action}")
    
    def approve_request(self, request_index: int) -> bool:
        """Approve a pending permission request"""
        try:
            if 0 <= request_index < len(self.pending_requests):
                request = self.pending_requests.pop(request_index)
                self._save_pending_requests()
                
                self._log_audit(
                    request.action, 
                    request.permission_type.value, 
                    request.risk_level.value, 
                    "approved", 
                    request.params, 
                    "user"
                )
                logger.info(f"Request approved: {request.action}")
                return True
        except Exception as e:
            logger.error(f"Failed to approve request: {e}")
        return False
    
    def deny_request(self, request_index: int) -> bool:
        """Deny a pending permission request"""
        try:
            if 0 <= request_index < len(self.pending_requests):
                request = self.pending_requests.pop(request_index)
                self._save_pending_requests()
                
                self._log_audit(
                    request.action, 
                    request.permission_type.value, 
                    request.risk_level.value, 
                    "denied_by_user", 
                    request.params, 
                    "user"
                )
                logger.info(f"Request denied: {request.action}")
                return True
        except Exception as e:
            logger.error(f"Failed to deny request: {e}")
        return False
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending permission requests"""
        return [req.to_dict() for req in self.pending_requests]
    
    def _log_audit(self, action: str, permission_type: str, risk_level: str,
                  status: str, details: Dict[str, Any], agent: str):
        """Log action to audit trail"""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            action=action,
            permission_type=permission_type,
            risk_level=risk_level,
            status=status,
            details=details,
            agent=agent
        )
        
        try:
            with open(self.AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_audit_log(self, limit: int = 100, 
                     permission_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve audit log entries"""
        logs = []
        try:
            if self.AUDIT_LOG_FILE.exists():
                with open(self.AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if permission_type is None or entry['permission_type'] == permission_type:
                                logs.append(entry)
                
                # Return most recent entries first
                logs = logs[-limit:]
                logs.reverse()
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
        
        return logs

# Global permission manager instance
permission_manager = PermissionManager()
