"""
ShivAI Atlas - Android Bridge
ADB-based Android device control and automation
"""

import subprocess
import re
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from ..core.config import config
from ..core.logger import get_logger
from ..core.permissions import permission_manager, PermissionType, RiskLevel

logger = get_logger(__name__)

class AndroidBridge:
    """Android device control via ADB"""
    
    def __init__(self):
        self.adb_path = config.android.adb_path or "adb"
        self.device_id = config.android.device_id
        self.connected = False
        logger.info("AndroidBridge initialized")
    
    def _check_permission(self, action: str, risk_level: RiskLevel, params: dict = None) -> bool:
        """Check if Android action is permitted"""
        if not config.android.enabled:
            logger.warning("Android bridge is disabled in settings")
            return False
        
        granted, reason = permission_manager.check_permission(
            PermissionType.ANDROID, action, risk_level, params or {}
        )
        if not granted:
            logger.warning(f"Permission denied for {action}: {reason}")
        return granted
    
    def _run_adb_command(self, command: List[str], timeout: int = 30) -> tuple[bool, str]:
        """Execute ADB command"""
        try:
            cmd = [self.adb_path]
            if self.device_id:
                cmd.extend(["-s", self.device_id])
            cmd.extend(command)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    # ==================== CONNECTION ====================
    
    def check_adb_available(self) -> Dict[str, Any]:
        """Check if ADB is available"""
        try:
            result = subprocess.run(
                [self.adb_path, "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                return {"success": True, "available": True, "version": version}
            else:
                return {"success": False, "available": False, "message": "ADB not found"}
        
        except Exception as e:
            return {"success": False, "available": False, "message": str(e)}
    
    def list_devices(self) -> Dict[str, Any]:
        """List connected Android devices"""
        try:
            success, output = self._run_adb_command(["devices"])
            
            if not success:
                return {"success": False, "message": output}
            
            devices = []
            for line in output.split('\n')[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            "id": parts[0],
                            "status": parts[1]
                        })
            
            return {"success": True, "devices": devices, "count": len(devices)}
        
        except Exception as e:
            logger.error(f"Failed to list devices: {e}")
            return {"success": False, "message": str(e)}
    
    def connect_device(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Connect to a device"""
        try:
            # List devices first
            devices_result = self.list_devices()
            if not devices_result["success"]:
                return devices_result
            
            devices = devices_result["devices"]
            if not devices:
                return {"success": False, "message": "No devices connected"}
            
            # Select device
            if device_id:
                self.device_id = device_id
            elif len(devices) == 1:
                self.device_id = devices[0]["id"]
            else:
                return {
                    "success": False,
                    "message": "Multiple devices found. Please specify device_id",
                    "devices": devices
                }
            
            # Test connection
            success, output = self._run_adb_command(["shell", "echo", "test"])
            if success:
                self.connected = True
                config.android.device_id = self.device_id
                config.save()
                logger.info(f"Connected to device: {self.device_id}")
                return {"success": True, "message": f"Connected to {self.device_id}", "device_id": self.device_id}
            else:
                return {"success": False, "message": f"Failed to connect: {output}"}
        
        except Exception as e:
            logger.error(f"Failed to connect device: {e}")
            return {"success": False, "message": str(e)}
    
    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from device"""
        self.connected = False
        self.device_id = None
        logger.info("Disconnected from device")
        return {"success": True, "message": "Disconnected"}
    
    # ==================== DEVICE INFO ====================
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        try:
            info = {}
            
            # Model
            success, output = self._run_adb_command(["shell", "getprop", "ro.product.model"])
            if success:
                info["model"] = output.strip()
            
            # Android version
            success, output = self._run_adb_command(["shell", "getprop", "ro.build.version.release"])
            if success:
                info["android_version"] = output.strip()
            
            # Manufacturer
            success, output = self._run_adb_command(["shell", "getprop", "ro.product.manufacturer"])
            if success:
                info["manufacturer"] = output.strip()
            
            # Serial
            success, output = self._run_adb_command(["get-serialno"])
            if success:
                info["serial"] = output.strip()
            
            return {"success": True, "info": info}
        
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {"success": False, "message": str(e)}
    
    def get_battery_status(self) -> Dict[str, Any]:
        """Get battery status"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("get_battery", RiskLevel.LOW):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, output = self._run_adb_command(["shell", "dumpsys", "battery"])
            if not success:
                return {"success": False, "message": output}
            
            battery = {}
            for line in output.split('\n'):
                if 'level:' in line:
                    battery["level"] = int(line.split(':')[1].strip())
                elif 'status:' in line:
                    battery["status"] = line.split(':')[1].strip()
                elif 'temperature:' in line:
                    temp = int(line.split(':')[1].strip())
                    battery["temperature"] = f"{temp / 10}°C"
            
            return {"success": True, "battery": battery}
        
        except Exception as e:
            logger.error(f"Failed to get battery status: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== SCREEN CONTROL ====================
    
    def take_screenshot(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """Take screenshot of Android screen"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("take_screenshot", RiskLevel.MEDIUM):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if save_path is None:
                from ..core.config import GENERATED_APPS_DIR
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = str(GENERATED_APPS_DIR / f"android_screen_{timestamp}.png")
            
            # Take screenshot on device
            device_path = f"/sdcard/screenshot_{int(time.time())}.png"
            success, _ = self._run_adb_command(["shell", "screencap", "-p", device_path])
            
            if not success:
                return {"success": False, "message": "Failed to capture screenshot"}
            
            # Pull screenshot to PC
            success, _ = self._run_adb_command(["pull", device_path, save_path])
            
            # Delete from device
            self._run_adb_command(["shell", "rm", device_path])
            
            if success:
                logger.info(f"Screenshot saved: {save_path}")
                return {"success": True, "message": "Screenshot taken", "path": save_path}
            else:
                return {"success": False, "message": "Failed to pull screenshot"}
        
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return {"success": False, "message": str(e)}
    
    def get_screen_size(self) -> Dict[str, Any]:
        """Get screen resolution"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        try:
            success, output = self._run_adb_command(["shell", "wm", "size"])
            if success:
                match = re.search(r'(\d+)x(\d+)', output)
                if match:
                    return {
                        "success": True,
                        "width": int(match.group(1)),
                        "height": int(match.group(2))
                    }
            
            return {"success": False, "message": "Failed to get screen size"}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== APP CONTROL ====================
    
    def open_app(self, package_name: str) -> Dict[str, Any]:
        """Open an app by package name"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("open_app", RiskLevel.MEDIUM, {"package": package_name}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            # Common apps mapping
            common_apps = {
                "whatsapp": "com.whatsapp",
                "telegram": "org.telegram.messenger",
                "chrome": "com.android.chrome",
                "youtube": "com.google.android.youtube",
                "camera": "com.android.camera",
                "settings": "com.android.settings",
                "gallery": "com.google.android.apps.photos",
                "maps": "com.google.android.apps.maps"
            }
            
            pkg = common_apps.get(package_name.lower(), package_name)
            
            success, output = self._run_adb_command([
                "shell", "monkey", "-p", pkg, "-c", 
                "android.intent.category.LAUNCHER", "1"
            ])
            
            if success:
                logger.info(f"Opened app: {pkg}")
                return {"success": True, "message": f"Opened {package_name}", "package": pkg}
            else:
                return {"success": False, "message": f"Failed to open app: {output}"}
        
        except Exception as e:
            logger.error(f"Failed to open app: {e}")
            return {"success": False, "message": str(e)}
    
    def close_app(self, package_name: str) -> Dict[str, Any]:
        """Close an app"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("close_app", RiskLevel.MEDIUM, {"package": package_name}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, output = self._run_adb_command(["shell", "am", "force-stop", package_name])
            
            if success:
                logger.info(f"Closed app: {package_name}")
                return {"success": True, "message": f"Closed {package_name}"}
            else:
                return {"success": False, "message": output}
        
        except Exception as e:
            logger.error(f"Failed to close app: {e}")
            return {"success": False, "message": str(e)}
    
    def list_installed_apps(self) -> Dict[str, Any]:
        """List installed apps"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        try:
            success, output = self._run_adb_command(["shell", "pm", "list", "packages"])
            
            if not success:
                return {"success": False, "message": output}
            
            apps = []
            for line in output.split('\n'):
                if line.startswith('package:'):
                    apps.append(line.replace('package:', '').strip())
            
            return {"success": True, "apps": apps, "count": len(apps)}
        
        except Exception as e:
            logger.error(f"Failed to list apps: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== INPUT CONTROL ====================
    
    def tap(self, x: int, y: int) -> Dict[str, Any]:
        """Tap at coordinates"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("tap", RiskLevel.MEDIUM, {"x": x, "y": y}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, output = self._run_adb_command(["shell", "input", "tap", str(x), str(y)])
            
            if success:
                logger.info(f"Tapped at ({x}, {y})")
                return {"success": True, "message": f"Tapped at ({x}, {y})"}
            else:
                return {"success": False, "message": output}
        
        except Exception as e:
            logger.error(f"Failed to tap: {e}")
            return {"success": False, "message": str(e)}
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> Dict[str, Any]:
        """Swipe gesture"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("swipe", RiskLevel.LOW):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, output = self._run_adb_command([
                "shell", "input", "swipe", 
                str(x1), str(y1), str(x2), str(y2), str(duration)
            ])
            
            if success:
                return {"success": True, "message": "Swipe executed"}
            else:
                return {"success": False, "message": output}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def type_text(self, text: str) -> Dict[str, Any]:
        """Type text on Android"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("type_text", RiskLevel.MEDIUM, {"text": text[:50]}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            # Replace spaces with %s for ADB
            text_encoded = text.replace(' ', '%s')
            success, output = self._run_adb_command(["shell", "input", "text", text_encoded])
            
            if success:
                logger.info(f"Typed text: {text[:50]}...")
                return {"success": True, "message": "Text entered"}
            else:
                return {"success": False, "message": output}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def press_key(self, keycode: int) -> Dict[str, Any]:
        """Press a key by keycode"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("press_key", RiskLevel.LOW, {"keycode": keycode}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, output = self._run_adb_command(["shell", "input", "keyevent", str(keycode)])
            
            if success:
                return {"success": True, "message": f"Pressed key {keycode}"}
            else:
                return {"success": False, "message": output}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # Common key shortcuts
    def press_home(self) -> Dict[str, Any]:
        """Press home button"""
        return self.press_key(3)
    
    def press_back(self) -> Dict[str, Any]:
        """Press back button"""
        return self.press_key(4)
    
    def press_menu(self) -> Dict[str, Any]:
        """Press menu button"""
        return self.press_key(82)
    
    # ==================== DEVICE ACTIONS ====================
    
    def unlock_phone(self) -> Dict[str, Any]:
        """Unlock phone (swipe up)"""
        if not self.connected:
            return {"success": False, "message": "No device connected"}
        
        if not self._check_permission("unlock_phone", RiskLevel.MEDIUM):
            return {"success": False, "message": "Permission denied"}
        
        try:
            # Wake up
            self._run_adb_command(["shell", "input", "keyevent", "26"])
            time.sleep(0.5)
            
            # Swipe up to unlock
            size_result = self.get_screen_size()
            if size_result["success"]:
                width = size_result["width"]
                height = size_result["height"]
                self.swipe(width//2, height-100, width//2, 100)
                
                logger.info("Phone unlocked")
                return {"success": True, "message": "Phone unlocked"}
            else:
                return {"success": False, "message": "Failed to get screen size"}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def reboot(self) -> Dict[str, Any]:
        """Reboot device"""
        if not self._check_permission("reboot", RiskLevel.CRITICAL):
            return {"success": False, "message": "Permission denied"}
        
        try:
            success, output = self._run_adb_command(["reboot"])
            if success:
                self.connected = False
                return {"success": True, "message": "Device rebooting"}
            else:
                return {"success": False, "message": output}
        except Exception as e:
            return {"success": False, "message": str(e)}

# Global instance
android_bridge = AndroidBridge()
