"""
ShivAI Atlas - PC Automation Engine
System-level automation capabilities for Windows
"""

import os
import subprocess
import platform
import psutil
import pyautogui
import ctypes
from pathlib import Path
from typing import Optional, Dict, Any, List
import time
import logging

from ..core.logger import get_logger
from ..core.permissions import permission_manager, PermissionType, RiskLevel

logger = get_logger(__name__)

# Configure PyAutoGUI safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class PCActions:
    """PC automation and system control"""
    
    def __init__(self):
        self.system = platform.system()
        logger.info(f"PCActions initialized on {self.system}")
    
    def _check_permission(self, action: str, risk_level: RiskLevel, params: dict = None) -> bool:
        """Check if action is permitted"""
        granted, reason = permission_manager.check_permission(
            PermissionType.KEYBOARD_MOUSE, action, risk_level, params or {}
        )
        if not granted:
            logger.warning(f"Permission denied for {action}: {reason}")
        return granted
    
    # ==================== APPLICATION CONTROL ====================
    
    def open_app(self, app_name: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Open an application"""
        if not self._check_permission("open_app", RiskLevel.LOW, {"app": app_name}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if self.system == "Windows":
                if path:
                    os.startfile(path)
                else:
                    # Common Windows apps
                    app_paths = {
                        "notepad": "notepad.exe",
                        "calculator": "calc.exe",
                        "paint": "mspaint.exe",
                        "explorer": "explorer.exe",
                        "cmd": "cmd.exe",
                        "powershell": "powershell.exe",
                        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                        "edge": "msedge.exe",
                        "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                        "vscode": r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME'))
                    }
                    
                    app_key = app_name.lower()
                    if app_key in app_paths:
                        subprocess.Popen(app_paths[app_key], shell=True)
                    else:
                        os.startfile(app_name)
            
            logger.info(f"Opened app: {app_name}")
            return {"success": True, "message": f"Opened {app_name}"}
        
        except Exception as e:
            logger.error(f"Failed to open app {app_name}: {e}")
            return {"success": False, "message": str(e)}
    
    def close_app(self, process_name: str) -> Dict[str, Any]:
        """Close an application by process name"""
        if not self._check_permission("close_app", RiskLevel.MEDIUM, {"process": process_name}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            killed = 0
            for proc in psutil.process_iter(['name']):
                if process_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed += 1
            
            logger.info(f"Closed {killed} instances of {process_name}")
            return {"success": True, "message": f"Closed {killed} instances", "count": killed}
        
        except Exception as e:
            logger.error(f"Failed to close app {process_name}: {e}")
            return {"success": False, "message": str(e)}
    
    def list_running_apps(self) -> Dict[str, Any]:
        """List all running applications"""
        try:
            processes = []
            for proc in psutil.process_iter(['name', 'pid', 'memory_percent', 'cpu_percent']):
                try:
                    processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'memory': f"{proc.info['memory_percent']:.2f}%",
                        'cpu': f"{proc.info['cpu_percent']:.2f}%"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {"success": True, "processes": processes, "count": len(processes)}
        
        except Exception as e:
            logger.error(f"Failed to list apps: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== KEYBOARD CONTROL ====================
    
    def type_text(self, text: str, interval: float = 0.05) -> Dict[str, Any]:
        """Type text using keyboard"""
        if not self._check_permission("type_text", RiskLevel.MEDIUM, {"text": text[:50]}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: {text[:50]}...")
            return {"success": True, "message": f"Typed {len(text)} characters"}
        
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return {"success": False, "message": str(e)}
    
    def press_key(self, key: str, presses: int = 1) -> Dict[str, Any]:
        """Press a key"""
        if not self._check_permission("press_key", RiskLevel.LOW, {"key": key}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            pyautogui.press(key, presses=presses)
            logger.info(f"Pressed key: {key} x{presses}")
            return {"success": True, "message": f"Pressed {key}"}
        
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            return {"success": False, "message": str(e)}
    
    def hotkey(self, *keys) -> Dict[str, Any]:
        """Press a combination of keys"""
        if not self._check_permission("hotkey", RiskLevel.LOW, {"keys": list(keys)}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"Pressed hotkey: {'+'.join(keys)}")
            return {"success": True, "message": f"Pressed {'+'.join(keys)}"}
        
        except Exception as e:
            logger.error(f"Failed to press hotkey: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== MOUSE CONTROL ====================
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """Move mouse to position"""
        if not self._check_permission("move_mouse", RiskLevel.LOW, {"x": x, "y": y}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
            return {"success": True, "message": f"Moved to ({x}, {y})"}
        
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return {"success": False, "message": str(e)}
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
             button: str = 'left', clicks: int = 1) -> Dict[str, Any]:
        """Click mouse"""
        if not self._check_permission("click", RiskLevel.MEDIUM, {"x": x, "y": y}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button)
            else:
                pyautogui.click(clicks=clicks, button=button)
            
            logger.info(f"Clicked at ({x}, {y}) with {button} button x{clicks}")
            return {"success": True, "message": f"Clicked {clicks} times"}
        
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return {"success": False, "message": str(e)}
    
    def get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== SCREENSHOT ====================
    
    def take_screenshot(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot"""
        granted, reason = permission_manager.check_permission(
            PermissionType.SCREEN_CAPTURE, "take_screenshot", RiskLevel.MEDIUM
        )
        if not granted:
            return {"success": False, "message": reason}
        
        try:
            if save_path is None:
                from ..core.config import GENERATED_APPS_DIR
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = str(GENERATED_APPS_DIR / f"screenshot_{timestamp}.png")
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            
            logger.info(f"Screenshot saved: {save_path}")
            return {"success": True, "message": "Screenshot taken", "path": save_path}
        
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== SYSTEM CONTROL ====================
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "cpu_cores": psutil.cpu_count(),
                "cpu_usage": f"{cpu_percent}%",
                "ram_total": f"{memory.total / (1024**3):.2f} GB",
                "ram_used": f"{memory.used / (1024**3):.2f} GB",
                "ram_percent": f"{memory.percent}%",
                "disk_total": f"{disk.total / (1024**3):.2f} GB",
                "disk_used": f"{disk.used / (1024**3):.2f} GB",
                "disk_percent": f"{disk.percent}%"
            }
            
            return {"success": True, "info": info}
        
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"success": False, "message": str(e)}
    
    def control_volume(self, action: str, level: Optional[int] = None) -> Dict[str, Any]:
        """Control system volume"""
        if not self._check_permission("control_volume", RiskLevel.LOW, {"action": action}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if self.system == "Windows":
                if action == "mute":
                    pyautogui.press("volumemute")
                elif action == "up":
                    pyautogui.press("volumeup", presses=5)
                elif action == "down":
                    pyautogui.press("volumedown", presses=5)
                elif action == "set" and level is not None:
                    # This is simplified; real implementation would use Windows API
                    pyautogui.press("volumemute")
                    time.sleep(0.1)
                    pyautogui.press("volumeup", presses=level // 2)
            
            logger.info(f"Volume control: {action}")
            return {"success": True, "message": f"Volume {action}"}
        
        except Exception as e:
            logger.error(f"Failed to control volume: {e}")
            return {"success": False, "message": str(e)}
    
    def shutdown_system(self, mode: str = "shutdown", delay: int = 60) -> Dict[str, Any]:
        """Shutdown/restart/sleep system"""
        if not self._check_permission("shutdown_system", RiskLevel.CRITICAL, {"mode": mode}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if self.system == "Windows":
                if mode == "shutdown":
                    os.system(f"shutdown /s /t {delay}")
                elif mode == "restart":
                    os.system(f"shutdown /r /t {delay}")
                elif mode == "sleep":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                elif mode == "hibernate":
                    os.system("shutdown /h")
            
            logger.info(f"System {mode} initiated with {delay}s delay")
            return {"success": True, "message": f"System will {mode} in {delay} seconds"}
        
        except Exception as e:
            logger.error(f"Failed to {mode} system: {e}")
            return {"success": False, "message": str(e)}
    
    def cancel_shutdown(self) -> Dict[str, Any]:
        """Cancel scheduled shutdown"""
        try:
            if self.system == "Windows":
                os.system("shutdown /a")
            
            logger.info("Shutdown cancelled")
            return {"success": True, "message": "Shutdown cancelled"}
        
        except Exception as e:
            logger.error(f"Failed to cancel shutdown: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== WINDOW MANAGEMENT ====================
    
    def minimize_all_windows(self) -> Dict[str, Any]:
        """Minimize all windows"""
        if not self._check_permission("minimize_all", RiskLevel.LOW):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if self.system == "Windows":
                pyautogui.hotkey('win', 'd')
            
            logger.info("Minimized all windows")
            return {"success": True, "message": "All windows minimized"}
        
        except Exception as e:
            logger.error(f"Failed to minimize windows: {e}")
            return {"success": False, "message": str(e)}
    
    def switch_window(self) -> Dict[str, Any]:
        """Switch to next window (Alt+Tab)"""
        if not self._check_permission("switch_window", RiskLevel.LOW):
            return {"success": False, "message": "Permission denied"}
        
        try:
            pyautogui.hotkey('alt', 'tab')
            logger.info("Switched window")
            return {"success": True, "message": "Window switched"}
        
        except Exception as e:
            logger.error(f"Failed to switch window: {e}")
            return {"success": False, "message": str(e)}
    
    def open_task_manager(self) -> Dict[str, Any]:
        """Open Windows Task Manager"""
        if not self._check_permission("open_task_manager", RiskLevel.LOW):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if self.system == "Windows":
                pyautogui.hotkey('ctrl', 'shift', 'esc')
            
            logger.info("Opened Task Manager")
            return {"success": True, "message": "Task Manager opened"}
        
        except Exception as e:
            logger.error(f"Failed to open Task Manager: {e}")
            return {"success": False, "message": str(e)}

# Global instance
pc_actions = PCActions()
