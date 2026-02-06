"""
ShivAI Atlas - Planner Agent
Intelligent planning and task decomposition
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..core.logger import get_logger
from ..core.memory import memory_agent
from ..core.config import config

logger = get_logger(__name__)

@dataclass
class PlanStep:
    """Single step in execution plan"""
    tool: str
    action: str
    params: Dict[str, Any]
    description: str

@dataclass
class ExecutionPlan:
    """Complete execution plan"""
    intent: str
    steps: List[PlanStep]
    confidence: float
    requires_confirmation: bool = False

class PlannerAgent:
    """Plans and decomposes user commands into executable steps"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        logger.info("PlannerAgent initialized")
    
    def _load_intent_patterns(self) -> Dict[str, List[Dict]]:
        """Load intent recognition patterns"""
        return {
            # File operations
            "create_file": [
                {"pattern": r"(file|फ़ाइल).*(banao|create|बनाओ)", "confidence": 0.9},
                {"pattern": r"(naya|नया).*(file|फ़ाइल)", "confidence": 0.85}
            ],
            "delete_file": [
                {"pattern": r"(file|फ़ाइल).*(delete|हटा|मिटा)", "confidence": 0.9},
                {"pattern": r"(remove|हटाओ).*(file|फ़ाइल)", "confidence": 0.85}
            ],
            "organize_desktop": [
                {"pattern": r"(desktop|डेस्कटॉप).*(organize|साफ|clean)", "confidence": 0.9},
                {"pattern": r"(desktop|डेस्कटॉप).*(arrange|व्यवस्थित)", "confidence": 0.85}
            ],
            
            # Application control
            "open_app": [
                {"pattern": r"(open|खोल).*(app|application|एप)", "confidence": 0.9},
                {"pattern": r"(start|चला|run).*(notepad|calculator|chrome)", "confidence": 0.85}
            ],
            "close_app": [
                {"pattern": r"(close|बंद|band).*(app|application)", "confidence": 0.9}
            ],
            
            # System control
            "screenshot": [
                {"pattern": r"(screenshot|स्क्रीनशॉट).*(le|ले|take)", "confidence": 0.9},
                {"pattern": r"(screen|स्क्रीन).*(capture|पकड़)", "confidence": 0.85}
            ],
            "volume_control": [
                {"pattern": r"(volume|आवाज़).*(up|down|mute|बढ़ा|घटा)", "confidence": 0.9}
            ],
            "shutdown": [
                {"pattern": r"(shutdown|बंद करो|band karo).*(computer|pc)", "confidence": 0.95},
                {"pattern": r"(computer|pc|system).*(off|बंद)", "confidence": 0.9}
            ],
            
            # Android operations
            "unlock_phone": [
                {"pattern": r"(phone|फोन).*(unlock|खोल)", "confidence": 0.9},
                {"pattern": r"(unlock|अनलॉक).*(phone|फोन)", "confidence": 0.9}
            ],
            "open_android_app": [
                {"pattern": r"(phone|फोन).*(whatsapp|telegram|youtube)", "confidence": 0.9},
                {"pattern": r"(android|एंड्रॉइड).*(open|खोल)", "confidence": 0.85}
            ],
            "android_screenshot": [
                {"pattern": r"(phone|फोन).*(screenshot|स्क्रीनशॉट)", "confidence": 0.9}
            ],
            
            # Messaging
            "send_whatsapp": [
                {"pattern": r"(whatsapp|व्हाट्सएप).*(send|भेज|message)", "confidence": 0.9},
                {"pattern": r"(message|संदेश).*(whatsapp|व्हाट्सएप)", "confidence": 0.85}
            ],
            "send_telegram": [
                {"pattern": r"(telegram|टेलीग्राम).*(send|भेज|message)", "confidence": 0.9}
            ],
            "check_messages": [
                {"pattern": r"(check|देख).*(messages|संदेश)", "confidence": 0.85},
                {"pattern": r"(unread|नए).*(messages|संदेश)", "confidence": 0.85}
            ],
            
            # Workflows
            "morning_routine": [
                {"pattern": r"(morning|सुबह).*(routine|दिनचर्या)", "confidence": 0.9}
            ],
            "backup_workflow": [
                {"pattern": r"(backup|बैकअप).*(create|बना|take)", "confidence": 0.9}
            ],
            
            # App builder
            "create_app": [
                {"pattern": r"(app|एप).*(banao|create|बनाओ)", "confidence": 0.85},
                {"pattern": r"(todo|calculator|notes).*(app|एप)", "confidence": 0.9}
            ],
            
            # General
            "system_info": [
                {"pattern": r"(system|सिस्टम).*(info|जानकारी)", "confidence": 0.9},
                {"pattern": r"(computer|कंप्यूटर).*(status|स्थिति)", "confidence": 0.85}
            ]
        }
    
    def parse_intent(self, command: str) -> tuple[str, float, Dict[str, Any]]:
        """Parse user command to identify intent"""
        command_lower = command.lower()
        best_intent = "unknown"
        best_confidence = 0.0
        entities = {}
        
        # Try to match patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                base_confidence = pattern_info["confidence"]
                
                if re.search(pattern, command_lower):
                    if base_confidence > best_confidence:
                        best_confidence = base_confidence
                        best_intent = intent
                        entities = self._extract_entities(command, intent)
        
        logger.info(f"Intent parsed: {best_intent} (confidence: {best_confidence})")
        return best_intent, best_confidence, entities
    
    def _extract_entities(self, command: str, intent: str) -> Dict[str, Any]:
        """Extract entities from command based on intent"""
        entities = {}
        command_lower = command.lower()
        
        # Extract app names
        apps = ["notepad", "calculator", "chrome", "firefox", "word", "excel", 
                "whatsapp", "telegram", "youtube", "camera"]
        for app in apps:
            if app in command_lower:
                entities["app_name"] = app
        
        # Extract file paths
        path_match = re.search(r'["\']([^"\']+)["\']', command)
        if path_match:
            entities["path"] = path_match.group(1)
        
        # Extract contact/chat names
        if "whatsapp" in intent or "telegram" in intent:
            # Try to find name after "to", "ko", etc.
            name_match = re.search(r'(?:to|ko|को)\s+([A-Za-z\s]+)', command, re.IGNORECASE)
            if name_match:
                entities["contact_name"] = name_match.group(1).strip()
        
        # Extract message text
        if "send" in intent or "message" in intent:
            # Text after quotes or "bolo"
            msg_match = re.search(r'(?:bolo|भेज|send)\s+["\']?([^"\']+)["\']?', command, re.IGNORECASE)
            if msg_match:
                entities["message_text"] = msg_match.group(1).strip()
        
        # Extract numbers
        numbers = re.findall(r'\d+', command)
        if numbers:
            entities["numbers"] = numbers
        
        return entities
    
    def create_plan(self, command: str) -> ExecutionPlan:
        """Create execution plan from command"""
        intent, confidence, entities = self.parse_intent(command)
        
        steps = []
        requires_confirmation = False
        
        # Build plan based on intent
        if intent == "create_file":
            path = entities.get("path", "new_file.txt")
            steps.append(PlanStep(
                tool="file_actions",
                action="create_file",
                params={"path": path, "content": ""},
                description=f"Create file: {path}"
            ))
        
        elif intent == "delete_file":
            if "path" in entities:
                steps.append(PlanStep(
                    tool="file_actions",
                    action="delete_file",
                    params={"path": entities["path"]},
                    description=f"Delete file: {entities['path']}"
                ))
                requires_confirmation = True
        
        elif intent == "organize_desktop":
            steps.append(PlanStep(
                tool="file_actions",
                action="organize_desktop",
                params={},
                description="Organize desktop files into folders"
            ))
        
        elif intent == "open_app":
            app_name = entities.get("app_name", "notepad")
            steps.append(PlanStep(
                tool="pc_actions",
                action="open_app",
                params={"app_name": app_name},
                description=f"Open application: {app_name}"
            ))
        
        elif intent == "close_app":
            app_name = entities.get("app_name", "")
            if app_name:
                steps.append(PlanStep(
                    tool="pc_actions",
                    action="close_app",
                    params={"process_name": app_name},
                    description=f"Close application: {app_name}"
                ))
        
        elif intent == "screenshot":
            steps.append(PlanStep(
                tool="pc_actions",
                action="take_screenshot",
                params={},
                description="Take screenshot"
            ))
        
        elif intent == "volume_control":
            if "up" in command.lower() or "बढ़ा" in command:
                action_type = "up"
            elif "down" in command.lower() or "घटा" in command:
                action_type = "down"
            else:
                action_type = "mute"
            
            steps.append(PlanStep(
                tool="pc_actions",
                action="control_volume",
                params={"action": action_type},
                description=f"Volume {action_type}"
            ))
        
        elif intent == "shutdown":
            steps.append(PlanStep(
                tool="pc_actions",
                action="shutdown_system",
                params={"mode": "shutdown", "delay": 60},
                description="Shutdown system in 60 seconds"
            ))
            requires_confirmation = True
        
        elif intent == "unlock_phone":
            steps.append(PlanStep(
                tool="android_bridge",
                action="unlock_phone",
                params={},
                description="Unlock Android phone"
            ))
        
        elif intent == "open_android_app":
            app_name = entities.get("app_name", "whatsapp")
            steps.append(PlanStep(
                tool="android_bridge",
                action="open_app",
                params={"package_name": app_name},
                description=f"Open {app_name} on Android"
            ))
        
        elif intent == "android_screenshot":
            steps.append(PlanStep(
                tool="android_bridge",
                action="take_screenshot",
                params={},
                description="Take Android screenshot"
            ))
        
        elif intent == "send_whatsapp":
            contact = entities.get("contact_name", "")
            message = entities.get("message_text", "")
            if contact and message:
                steps.append(PlanStep(
                    tool="enterchat_connector",
                    action="send_whatsapp_message",
                    params={"contact_name": contact, "message": message},
                    description=f"Send WhatsApp to {contact}"
                ))
        
        elif intent == "send_telegram":
            chat = entities.get("contact_name", "")
            message = entities.get("message_text", "")
            if chat and message:
                steps.append(PlanStep(
                    tool="enterchat_connector",
                    action="send_telegram_message",
                    params={"chat_name": chat, "message": message},
                    description=f"Send Telegram to {chat}"
                ))
        
        elif intent == "check_messages":
            steps.append(PlanStep(
                tool="enterchat_connector",
                action="get_unread_count",
                params={},
                description="Check unread messages"
            ))
        
        elif intent == "system_info":
            steps.append(PlanStep(
                tool="pc_actions",
                action="get_system_info",
                params={},
                description="Get system information"
            ))
        
        elif intent == "morning_routine":
            steps.append(PlanStep(
                tool="workflow_engine",
                action="execute_workflow",
                params={"workflow_name": "morning_routine"},
                description="Execute morning routine workflow"
            ))
        
        elif intent == "backup_workflow":
            steps.append(PlanStep(
                tool="workflow_engine",
                action="execute_workflow",
                params={"workflow_name": "backup_workflow"},
                description="Execute backup workflow"
            ))
        
        elif intent == "create_app":
            app_type = "todo"
            if "calculator" in command.lower():
                app_type = "calculator"
            elif "notes" in command.lower():
                app_type = "notes"
            
            steps.append(PlanStep(
                tool="app_builder",
                action="create_app",
                params={"app_type": app_type},
                description=f"Create {app_type} application"
            ))
        
        # If no steps were created, return unknown intent plan
        if not steps:
            steps.append(PlanStep(
                tool="unknown",
                action="unknown",
                params={"command": command},
                description=f"Unknown command: {command}"
            ))
        
        plan = ExecutionPlan(
            intent=intent,
            steps=steps,
            confidence=confidence,
            requires_confirmation=requires_confirmation
        )
        
        logger.info(f"Plan created with {len(steps)} steps")
        return plan
    
    def optimize_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize execution plan"""
        # Remove duplicate steps
        seen = set()
        optimized_steps = []
        
        for step in plan.steps:
            step_key = f"{step.tool}.{step.action}.{str(step.params)}"
            if step_key not in seen:
                seen.add(step_key)
                optimized_steps.append(step)
        
        plan.steps = optimized_steps
        logger.info(f"Plan optimized to {len(optimized_steps)} steps")
        return plan

# Global instance
planner_agent = PlannerAgent()
