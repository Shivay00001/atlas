"""
ShivAI Atlas - Executor Agent
Executes planned actions using automation modules
"""

import time
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging

from .planner_agent import ExecutionPlan, PlanStep
from ..automation.pc_actions import pc_actions
from ..automation.file_actions import file_actions
from ..automation.android_bridge import android_bridge
from ..automation.enterchat_connector import enterchat_connector
from ..core.logger import get_logger, atlas_logger
from ..core.memory import memory_agent

logger = get_logger(__name__)

@dataclass
class ExecutionResult:
    """Result of executing a plan"""
    success: bool
    plan: ExecutionPlan
    step_results: List[Dict[str, Any]]
    total_duration_ms: int
    message: str

class ExecutorAgent:
    """Executes planned actions"""
    
    def __init__(self):
        self.tool_map = {
            "pc_actions": pc_actions,
            "file_actions": file_actions,
            "android_bridge": android_bridge,
            "enterchat_connector": enterchat_connector,
            "workflow_engine": None,  # Will be set later
            "app_builder": None  # Will be set later
        }
        logger.info("ExecutorAgent initialized")
    
    def set_workflow_engine(self, workflow_engine):
        """Set workflow engine reference"""
        self.tool_map["workflow_engine"] = workflow_engine
    
    def set_app_builder(self, app_builder):
        """Set app builder reference"""
        self.tool_map["app_builder"] = app_builder
    
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        """Execute a complete plan"""
        start_time = time.time()
        step_results = []
        overall_success = True
        
        logger.info(f"Executing plan with {len(plan.steps)} steps")
        
        for i, step in enumerate(plan.steps):
            step_start = time.time()
            
            logger.info(f"Step {i+1}/{len(plan.steps)}: {step.description}")
            atlas_logger.log_agent_action(
                "ExecutorAgent",
                f"Executing step {i+1}",
                {"tool": step.tool, "action": step.action}
            )
            
            # Execute step
            result = self._execute_step(step)
            
            step_duration = int((time.time() - step_start) * 1000)
            
            step_results.append({
                "step_number": i + 1,
                "description": step.description,
                "tool": step.tool,
                "action": step.action,
                "result": result,
                "duration_ms": step_duration,
                "success": result.get("success", False)
            })
            
            # Log to automation logger
            atlas_logger.log_automation(
                step.tool,
                step.action,
                "success" if result.get("success") else "failed",
                step.params
            )
            
            # If step failed and it's critical, stop execution
            if not result.get("success", False):
                overall_success = False
                if self._is_critical_step(step):
                    logger.warning(f"Critical step failed: {step.description}")
                    break
            
            # Small delay between steps
            time.sleep(0.1)
        
        total_duration = int((time.time() - start_time) * 1000)
        
        # Create result summary
        if overall_success:
            message = f"Successfully executed {len(step_results)} steps"
        else:
            failed_count = sum(1 for r in step_results if not r["success"])
            message = f"Execution completed with {failed_count} failures"
        
        execution_result = ExecutionResult(
            success=overall_success,
            plan=plan,
            step_results=step_results,
            total_duration_ms=total_duration,
            message=message
        )
        
        # Log to memory
        memory_agent.log_usage(
            command=plan.intent,
            agent="ExecutorAgent",
            success=overall_success,
            duration_ms=total_duration,
            metadata={"steps": len(step_results)}
        )
        
        logger.info(f"Plan execution completed: {message} in {total_duration}ms")
        
        return execution_result
    
    def _execute_step(self, step: PlanStep) -> Dict[str, Any]:
        """Execute a single step"""
        try:
            # Get the tool
            tool = self.tool_map.get(step.tool)
            
            if tool is None:
                return {
                    "success": False,
                    "message": f"Tool not found: {step.tool}"
                }
            
            # Get the action method
            if not hasattr(tool, step.action):
                return {
                    "success": False,
                    "message": f"Action not found: {step.action} in {step.tool}"
                }
            
            action_method = getattr(tool, step.action)
            
            # Execute action
            result = action_method(**step.params)
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            return {
                "success": False,
                "message": f"Execution error: {str(e)}"
            }
    
    def _is_critical_step(self, step: PlanStep) -> bool:
        """Check if step is critical (failure should stop execution)"""
        critical_actions = [
            "delete_file",
            "delete_folder",
            "shutdown_system",
            "reboot"
        ]
        return step.action in critical_actions
    
    def execute_single_action(self, tool: str, action: str, 
                             params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action directly"""
        step = PlanStep(
            tool=tool,
            action=action,
            params=params,
            description=f"{tool}.{action}"
        )
        
        return self._execute_step(step)
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        # Get recent usage stats
        recent_executions = memory_agent.db.fetch_all("""
            SELECT command, success, duration_ms, timestamp 
            FROM usage_stats 
            WHERE agent = 'ExecutorAgent'
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        stats = []
        for row in recent_executions:
            stats.append({
                "command": row["command"],
                "success": bool(row["success"]),
                "duration_ms": row["duration_ms"],
                "timestamp": row["timestamp"]
            })
        
        return {
            "recent_executions": stats,
            "tools_available": list(self.tool_map.keys())
        }
    
    def dry_run(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Simulate plan execution without actually running it"""
        steps_summary = []
        
        for i, step in enumerate(plan.steps):
            steps_summary.append({
                "step_number": i + 1,
                "description": step.description,
                "tool": step.tool,
                "action": step.action,
                "params": step.params,
                "estimated_duration": "~500ms"
            })
        
        return {
            "success": True,
            "mode": "dry_run",
            "total_steps": len(plan.steps),
            "steps": steps_summary,
            "requires_confirmation": plan.requires_confirmation,
            "estimated_total_duration": f"~{len(plan.steps) * 500}ms"
        }

# Global instance
executor_agent = ExecutorAgent()
