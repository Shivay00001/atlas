"""
ShivAI Atlas - Workflow Engine
Automated multi-step routines and workflows
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from ..core.config import TEMPLATES_DIR
from ..core.logger import get_logger
from ..core.memory import memory_agent
from ..agents.planner_agent import PlanStep, ExecutionPlan

logger = get_logger(__name__)

class WorkflowEngine:
    """Manages and executes workflows"""
    
    def __init__(self):
        self.templates_dir = TEMPLATES_DIR / "workflow_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._init_default_workflows()
        logger.info("WorkflowEngine initialized")
    
    def _init_default_workflows(self):
        """Initialize default workflow templates"""
        default_workflows = {
            "morning_routine": {
                "name": "Morning Routine",
                "description": "Daily morning productivity setup",
                "category": "productivity",
                "steps": [
                    {
                        "tool": "pc_actions",
                        "action": "get_system_info",
                        "params": {},
                        "description": "Check system status"
                    },
                    {
                        "tool": "file_actions",
                        "action": "organize_desktop",
                        "params": {},
                        "description": "Organize desktop files"
                    },
                    {
                        "tool": "pc_actions",
                        "action": "open_app",
                        "params": {"app_name": "chrome"},
                        "description": "Open browser"
                    },
                    {
                        "tool": "enterchat_connector",
                        "action": "get_unread_count",
                        "params": {},
                        "description": "Check messages"
                    }
                ]
            },
            "backup_workflow": {
                "name": "Backup Workflow",
                "description": "Backup important files and folders",
                "category": "maintenance",
                "steps": [
                    {
                        "tool": "file_actions",
                        "action": "create_folder",
                        "params": {"path": "C:/Users/Public/AtlasBackup"},
                        "description": "Create backup folder"
                    },
                    {
                        "tool": "file_actions",
                        "action": "copy_folder",
                        "params": {
                            "source": "C:/Users/Public/Documents",
                            "destination": "C:/Users/Public/AtlasBackup/Documents"
                        },
                        "description": "Backup Documents"
                    },
                    {
                        "tool": "file_actions",
                        "action": "clean_temp_files",
                        "params": {},
                        "description": "Clean temporary files"
                    }
                ]
            },
            "productivity_setup": {
                "name": "Productivity Setup",
                "description": "Open all productivity apps",
                "category": "productivity",
                "steps": [
                    {
                        "tool": "pc_actions",
                        "action": "minimize_all_windows",
                        "params": {},
                        "description": "Minimize all windows"
                    },
                    {
                        "tool": "pc_actions",
                        "action": "open_app",
                        "params": {"app_name": "chrome"},
                        "description": "Open Chrome"
                    },
                    {
                        "tool": "pc_actions",
                        "action": "open_app",
                        "params": {"app_name": "notepad"},
                        "description": "Open Notepad"
                    },
                    {
                        "tool": "pc_actions",
                        "action": "open_app",
                        "params": {"app_name": "calculator"},
                        "description": "Open Calculator"
                    }
                ]
            },
            "evening_cleanup": {
                "name": "Evening Cleanup",
                "description": "End of day cleanup routine",
                "category": "maintenance",
                "steps": [
                    {
                        "tool": "file_actions",
                        "action": "organize_desktop",
                        "params": {},
                        "description": "Organize desktop"
                    },
                    {
                        "tool": "file_actions",
                        "action": "clean_temp_files",
                        "params": {},
                        "description": "Clean temp files"
                    },
                    {
                        "tool": "pc_actions",
                        "action": "take_screenshot",
                        "params": {},
                        "description": "Take daily screenshot"
                    }
                ]
            },
            "phone_sync": {
                "name": "Phone Sync",
                "description": "Sync and backup phone data",
                "category": "android",
                "steps": [
                    {
                        "tool": "android_bridge",
                        "action": "connect_device",
                        "params": {},
                        "description": "Connect Android device"
                    },
                    {
                        "tool": "android_bridge",
                        "action": "get_device_info",
                        "params": {},
                        "description": "Get device info"
                    },
                    {
                        "tool": "android_bridge",
                        "action": "take_screenshot",
                        "params": {},
                        "description": "Take phone screenshot"
                    },
                    {
                        "tool": "android_bridge",
                        "action": "get_battery_status",
                        "params": {},
                        "description": "Check battery"
                    }
                ]
            }
        }
        
        # Save default workflows to templates
        for workflow_id, workflow_data in default_workflows.items():
            template_file = self.templates_dir / f"{workflow_id}.json"
            if not template_file.exists():
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(workflow_data, f, indent=2, ensure_ascii=False)
                
                # Also save to memory database
                memory_agent.save_workflow(
                    name=workflow_id,
                    description=workflow_data["description"],
                    steps=workflow_data["steps"],
                    category=workflow_data["category"]
                )
    
    def execute_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Execute a workflow by name"""
        try:
            # Load workflow from memory
            workflow = memory_agent.get_workflow(workflow_name)
            
            if not workflow:
                # Try loading from template file
                workflow = self._load_workflow_template(workflow_name)
            
            if not workflow:
                return {
                    "success": False,
                    "message": f"Workflow not found: {workflow_name}"
                }
            
            # Convert to ExecutionPlan
            steps = []
            for step_data in workflow["steps"]:
                steps.append(PlanStep(
                    tool=step_data["tool"],
                    action=step_data["action"],
                    params=step_data.get("params", {}),
                    description=step_data["description"]
                ))
            
            plan = ExecutionPlan(
                intent=f"workflow_{workflow_name}",
                steps=steps,
                confidence=1.0,
                requires_confirmation=False
            )
            
            # Execute using ExecutorAgent
            from ..agents.executor_agent import executor_agent
            result = executor_agent.execute_plan(plan)
            
            # Update workflow usage
            memory_agent.update_workflow_usage(workflow_name)
            
            logger.info(f"Workflow '{workflow_name}' executed: {result.success}")
            
            return {
                "success": result.success,
                "message": result.message,
                "workflow_name": workflow_name,
                "steps_executed": len(result.step_results),
                "duration_ms": result.total_duration_ms,
                "results": result.step_results
            }
        
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_name}: {e}")
            return {
                "success": False,
                "message": f"Workflow execution failed: {str(e)}"
            }
    
    def _load_workflow_template(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Load workflow from template file"""
        try:
            template_file = self.templates_dir / f"{workflow_name}.json"
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Failed to load workflow template: {e}")
            return None
    
    def create_workflow(self, name: str, description: str, 
                       steps: List[Dict[str, Any]], category: str = "custom") -> Dict[str, Any]:
        """Create a new custom workflow"""
        try:
            # Validate steps
            for step in steps:
                if not all(k in step for k in ["tool", "action", "params", "description"]):
                    return {
                        "success": False,
                        "message": "Invalid step format. Required: tool, action, params, description"
                    }
            
            # Save to memory
            success = memory_agent.save_workflow(name, description, steps, category)
            
            if success:
                # Also save as template
                workflow_data = {
                    "name": name,
                    "description": description,
                    "category": category,
                    "steps": steps
                }
                
                template_file = self.templates_dir / f"{name}.json"
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(workflow_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Created workflow: {name}")
                return {
                    "success": True,
                    "message": f"Workflow '{name}' created successfully",
                    "workflow_name": name
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save workflow"
                }
        
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def list_workflows(self, category: Optional[str] = None) -> Dict[str, Any]:
        """List all available workflows"""
        try:
            workflows = memory_agent.list_workflows(category)
            return {
                "success": True,
                "workflows": workflows,
                "count": len(workflows)
            }
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_workflow(self, name: str) -> Dict[str, Any]:
        """Get workflow details"""
        try:
            workflow = memory_agent.get_workflow(name)
            if workflow:
                return {
                    "success": True,
                    "workflow": workflow
                }
            else:
                return {
                    "success": False,
                    "message": f"Workflow not found: {name}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def delete_workflow(self, name: str) -> Dict[str, Any]:
        """Delete a workflow"""
        try:
            # Delete from memory database
            memory_agent.db.execute("DELETE FROM workflows WHERE name = ?", (name,))
            
            # Delete template file
            template_file = self.templates_dir / f"{name}.json"
            if template_file.exists():
                template_file.unlink()
            
            logger.info(f"Deleted workflow: {name}")
            return {
                "success": True,
                "message": f"Workflow '{name}' deleted"
            }
        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def schedule_workflow(self, workflow_name: str, schedule: str) -> Dict[str, Any]:
        """Schedule a workflow for automatic execution"""
        # This would integrate with a scheduler (like APScheduler)
        # For now, just store the schedule preference
        try:
            memory_agent.remember(
                f"workflow_schedule_{workflow_name}",
                schedule,
                category="schedules"
            )
            
            return {
                "success": True,
                "message": f"Workflow '{workflow_name}' scheduled: {schedule}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

# Global instance
workflow_engine = WorkflowEngine()
