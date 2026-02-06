"""
ShivAI Atlas - EnterChat Connector
Integration with EnterChat vX messaging super-client
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..core.config import config
from ..core.logger import get_logger
from ..core.permissions import permission_manager, PermissionType, RiskLevel

logger = get_logger(__name__)

class EnterChatConnector:
    """EnterChat messaging integration"""
    
    def __init__(self):
        self.base_url = config.enterchat.api_url
        self.api_key = config.enterchat.api_key
        self.timeout = config.enterchat.timeout
        self.retry_attempts = config.enterchat.retry_attempts
        self.connected = False
        logger.info("EnterChatConnector initialized")
    
    def _check_permission(self, action: str, risk_level: RiskLevel, params: dict = None) -> bool:
        """Check if EnterChat action is permitted"""
        if not config.enterchat.enabled:
            logger.warning("EnterChat is disabled in settings")
            return False
        
        granted, reason = permission_manager.check_permission(
            PermissionType.ENTERCHAT, action, risk_level, params or {}
        )
        if not granted:
            logger.warning(f"Permission denied for {action}: {reason}")
        return granted
    
    def _make_request(self, method: str, endpoint: str, data: dict = None, 
                     retry: int = 0) -> tuple[bool, Any]:
        """Make HTTP request to EnterChat API"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                return False, "Invalid HTTP method"
            
            if response.status_code in [200, 201]:
                return True, response.json() if response.text else {}
            elif response.status_code == 429 and retry < self.retry_attempts:
                # Rate limited, retry
                import time
                time.sleep(2 ** retry)
                return self._make_request(method, endpoint, data, retry + 1)
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        
        except requests.exceptions.Timeout:
            if retry < self.retry_attempts:
                return self._make_request(method, endpoint, data, retry + 1)
            return False, "Request timed out"
        
        except Exception as e:
            logger.error(f"EnterChat API request failed: {e}")
            return False, str(e)
    
    # ==================== CONNECTION ====================
    
    def check_connection(self) -> Dict[str, Any]:
        """Check if EnterChat is accessible"""
        try:
            success, result = self._make_request("GET", "/api/health")
            
            if success:
                self.connected = True
                return {
                    "success": True,
                    "connected": True,
                    "message": "EnterChat is accessible",
                    "version": result.get("version", "unknown")
                }
            else:
                self.connected = False
                return {
                    "success": False,
                    "connected": False,
                    "message": f"Cannot connect to EnterChat: {result}"
                }
        
        except Exception as e:
            self.connected = False
            logger.error(f"Failed to check EnterChat connection: {e}")
            return {
                "success": False,
                "connected": False,
                "message": str(e)
            }
    
    def get_supported_apps(self) -> Dict[str, Any]:
        """Get list of supported messaging apps"""
        try:
            success, result = self._make_request("GET", "/api/apps")
            
            if success:
                return {
                    "success": True,
                    "apps": result.get("apps", []),
                    "count": len(result.get("apps", []))
                }
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== MESSAGING ====================
    
    def send_message(self, app_id: str, conversation_id: str, text: str, 
                    attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send a message via EnterChat"""
        if not self._check_permission("send_message", RiskLevel.MEDIUM, {
            "app": app_id,
            "conversation": conversation_id,
            "text": text[:100]
        }):
            return {"success": False, "message": "Permission denied"}
        
        try:
            data = {
                "app_id": app_id,
                "conversation_id": conversation_id,
                "text": text,
                "attachments": attachments or []
            }
            
            success, result = self._make_request("POST", "/api/messages/send", data)
            
            if success:
                logger.info(f"Message sent via {app_id} to {conversation_id}")
                return {
                    "success": True,
                    "message": "Message sent",
                    "message_id": result.get("message_id")
                }
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {"success": False, "message": str(e)}
    
    def send_whatsapp_message(self, contact_name: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message by contact name"""
        if not self._check_permission("send_whatsapp", RiskLevel.MEDIUM, {
            "contact": contact_name,
            "message": message[:100]
        }):
            return {"success": False, "message": "Permission denied"}
        
        try:
            # First, find the conversation
            conversations = self.list_conversations("whatsapp")
            if not conversations["success"]:
                return conversations
            
            # Search for contact
            conversation_id = None
            for conv in conversations.get("conversations", []):
                if contact_name.lower() in conv.get("name", "").lower():
                    conversation_id = conv.get("id")
                    break
            
            if not conversation_id:
                return {
                    "success": False,
                    "message": f"Contact '{contact_name}' not found in WhatsApp"
                }
            
            # Send message
            return self.send_message("whatsapp", conversation_id, message)
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def send_telegram_message(self, chat_name: str, message: str) -> Dict[str, Any]:
        """Send Telegram message by chat name"""
        if not self._check_permission("send_telegram", RiskLevel.MEDIUM, {
            "chat": chat_name,
            "message": message[:100]
        }):
            return {"success": False, "message": "Permission denied"}
        
        try:
            conversations = self.list_conversations("telegram")
            if not conversations["success"]:
                return conversations
            
            conversation_id = None
            for conv in conversations.get("conversations", []):
                if chat_name.lower() in conv.get("name", "").lower():
                    conversation_id = conv.get("id")
                    break
            
            if not conversation_id:
                return {
                    "success": False,
                    "message": f"Chat '{chat_name}' not found in Telegram"
                }
            
            return self.send_message("telegram", conversation_id, message)
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== CONVERSATIONS ====================
    
    def list_conversations(self, app_id: str, limit: int = 50) -> Dict[str, Any]:
        """List conversations for a specific app"""
        try:
            success, result = self._make_request(
                "GET", 
                f"/api/conversations?app_id={app_id}&limit={limit}"
            )
            
            if success:
                conversations = result.get("conversations", [])
                return {
                    "success": True,
                    "conversations": conversations,
                    "count": len(conversations)
                }
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_unified_inbox(self, limit: int = 100) -> Dict[str, Any]:
        """Get unified inbox from all apps"""
        if not self._check_permission("get_inbox", RiskLevel.LOW):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, result = self._make_request(
                "GET", 
                f"/api/inbox/unified?limit={limit}"
            )
            
            if success:
                messages = result.get("messages", [])
                return {
                    "success": True,
                    "messages": messages,
                    "count": len(messages)
                }
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_conversation_messages(self, app_id: str, conversation_id: str, 
                                  limit: int = 50) -> Dict[str, Any]:
        """Get messages from a specific conversation"""
        if not self._check_permission("get_messages", RiskLevel.LOW, {
            "app": app_id,
            "conversation": conversation_id
        }):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, result = self._make_request(
                "GET",
                f"/api/messages?app_id={app_id}&conversation_id={conversation_id}&limit={limit}"
            )
            
            if success:
                messages = result.get("messages", [])
                return {
                    "success": True,
                    "messages": messages,
                    "count": len(messages)
                }
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== ADVANCED FEATURES ====================
    
    def search_messages(self, query: str, app_id: Optional[str] = None) -> Dict[str, Any]:
        """Search messages across apps"""
        try:
            params = f"?query={query}"
            if app_id:
                params += f"&app_id={app_id}"
            
            success, result = self._make_request("GET", f"/api/search{params}")
            
            if success:
                results = result.get("results", [])
                return {
                    "success": True,
                    "results": results,
                    "count": len(results)
                }
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_unread_count(self, app_id: Optional[str] = None) -> Dict[str, Any]:
        """Get unread message count"""
        try:
            endpoint = "/api/unread"
            if app_id:
                endpoint += f"?app_id={app_id}"
            
            success, result = self._make_request("GET", endpoint)
            
            if success:
                return {
                    "success": True,
                    "unread_count": result.get("count", 0),
                    "by_app": result.get("by_app", {})
                }
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def mark_as_read(self, app_id: str, conversation_id: str) -> Dict[str, Any]:
        """Mark conversation as read"""
        if not self._check_permission("mark_read", RiskLevel.LOW):
            return {"success": False, "message": "Permission denied"}
        
        try:
            data = {
                "app_id": app_id,
                "conversation_id": conversation_id
            }
            
            success, result = self._make_request("POST", "/api/messages/mark_read", data)
            
            if success:
                return {"success": True, "message": "Marked as read"}
            else:
                return {"success": False, "message": result}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== AUTOMATION HELPERS ====================
    
    def summarize_conversation(self, app_id: str, conversation_id: str, 
                              last_n_messages: int = 50) -> Dict[str, Any]:
        """Get last N messages for summarization"""
        try:
            messages_result = self.get_conversation_messages(
                app_id, conversation_id, last_n_messages
            )
            
            if not messages_result["success"]:
                return messages_result
            
            messages = messages_result.get("messages", [])
            
            # Format messages for summarization
            formatted = []
            for msg in messages:
                formatted.append({
                    "sender": msg.get("sender", "Unknown"),
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("timestamp", "")
                })
            
            return {
                "success": True,
                "messages": formatted,
                "count": len(formatted),
                "conversation_id": conversation_id,
                "app_id": app_id
            }
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def bulk_send(self, app_id: str, recipient_ids: List[str], 
                 message: str) -> Dict[str, Any]:
        """Send message to multiple recipients"""
        if not self._check_permission("bulk_send", RiskLevel.HIGH, {
            "app": app_id,
            "recipients": len(recipient_ids),
            "message": message[:100]
        }):
            return {"success": False, "message": "Permission denied"}
        
        try:
            results = []
            successful = 0
            failed = 0
            
            for recipient_id in recipient_ids:
                result = self.send_message(app_id, recipient_id, message)
                results.append({
                    "recipient_id": recipient_id,
                    "success": result["success"]
                })
                
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
            
            logger.info(f"Bulk send completed: {successful} successful, {failed} failed")
            return {
                "success": True,
                "message": f"Sent to {successful}/{len(recipient_ids)} recipients",
                "successful": successful,
                "failed": failed,
                "results": results
            }
        
        except Exception as e:
            return {"success": False, "message": str(e)}

# Global instance
enterchat_connector = EnterChatConnector()
