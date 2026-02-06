"""
ShivAI Atlas - File Operations Module
File and folder management automation
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import time
import json

from ..core.logger import get_logger
from ..core.permissions import permission_manager, PermissionType, RiskLevel

logger = get_logger(__name__)

class FileActions:
    """File and folder operations"""
    
    def __init__(self):
        logger.info("FileActions initialized")
    
    def _check_permission(self, action: str, risk_level: RiskLevel, params: dict = None) -> bool:
        """Check if file action is permitted"""
        granted, reason = permission_manager.check_permission(
            PermissionType.FILES, action, risk_level, params or {}
        )
        if not granted:
            logger.warning(f"Permission denied for {action}: {reason}")
        return granted
    
    # ==================== FILE OPERATIONS ====================
    
    def create_file(self, path: str, content: str = "") -> Dict[str, Any]:
        """Create a new file"""
        if not self._check_permission("create_file", RiskLevel.LOW, {"path": path}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {path}")
            return {"success": True, "message": f"File created: {path}"}
        
        except Exception as e:
            logger.error(f"Failed to create file {path}: {e}")
            return {"success": False, "message": str(e)}
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents"""
        if not self._check_permission("read_file", RiskLevel.LOW, {"path": path}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read file: {path}")
            return {"success": True, "content": content, "size": len(content)}
        
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            return {"success": False, "message": str(e)}
    
    def write_file(self, path: str, content: str, mode: str = 'w') -> Dict[str, Any]:
        """Write content to file"""
        if not self._check_permission("write_file", RiskLevel.MEDIUM, {"path": path}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote to file: {path}")
            return {"success": True, "message": f"Content written to {path}"}
        
        except Exception as e:
            logger.error(f"Failed to write file {path}: {e}")
            return {"success": False, "message": str(e)}
    
    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file"""
        if not self._check_permission("delete_file", RiskLevel.HIGH, {"path": path}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            os.remove(path)
            logger.info(f"Deleted file: {path}")
            return {"success": True, "message": f"Deleted: {path}"}
        
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
            return {"success": False, "message": str(e)}
    
    def rename_file(self, old_path: str, new_path: str) -> Dict[str, Any]:
        """Rename a file"""
        if not self._check_permission("rename_file", RiskLevel.MEDIUM, 
                                     {"old": old_path, "new": new_path}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            os.rename(old_path, new_path)
            logger.info(f"Renamed: {old_path} -> {new_path}")
            return {"success": True, "message": f"Renamed to {new_path}"}
        
        except Exception as e:
            logger.error(f"Failed to rename {old_path}: {e}")
            return {"success": False, "message": str(e)}
    
    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a file"""
        if not self._check_permission("copy_file", RiskLevel.MEDIUM, 
                                     {"source": source, "dest": destination}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            shutil.copy2(source, destination)
            logger.info(f"Copied: {source} -> {destination}")
            return {"success": True, "message": f"Copied to {destination}"}
        
        except Exception as e:
            logger.error(f"Failed to copy {source}: {e}")
            return {"success": False, "message": str(e)}
    
    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a file"""
        if not self._check_permission("move_file", RiskLevel.MEDIUM, 
                                     {"source": source, "dest": destination}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            shutil.move(source, destination)
            logger.info(f"Moved: {source} -> {destination}")
            return {"success": True, "message": f"Moved to {destination}"}
        
        except Exception as e:
            logger.error(f"Failed to move {source}: {e}")
            return {"success": False, "message": str(e)}
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return {"success": False, "message": "File not found"}
            
            stat = file_path.stat()
            info = {
                "name": file_path.name,
                "path": str(file_path.absolute()),
                "size": stat.st_size,
                "size_mb": f"{stat.st_size / (1024**2):.2f}",
                "created": time.ctime(stat.st_ctime),
                "modified": time.ctime(stat.st_mtime),
                "is_file": file_path.is_file(),
                "is_dir": file_path.is_dir(),
                "extension": file_path.suffix
            }
            
            return {"success": True, "info": info}
        
        except Exception as e:
            logger.error(f"Failed to get file info for {path}: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== FOLDER OPERATIONS ====================
    
    def create_folder(self, path: str) -> Dict[str, Any]:
        """Create a folder"""
        if not self._check_permission("create_folder", RiskLevel.LOW, {"path": path}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {path}")
            return {"success": True, "message": f"Folder created: {path}"}
        
        except Exception as e:
            logger.error(f"Failed to create folder {path}: {e}")
            return {"success": False, "message": str(e)}
    
    def delete_folder(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """Delete a folder"""
        if not self._check_permission("delete_folder", RiskLevel.CRITICAL, {"path": path}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
            
            logger.info(f"Deleted folder: {path}")
            return {"success": True, "message": f"Deleted: {path}"}
        
        except Exception as e:
            logger.error(f"Failed to delete folder {path}: {e}")
            return {"success": False, "message": str(e)}
    
    def list_files(self, path: str, pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
        """List files in a directory"""
        try:
            folder = Path(path)
            if not folder.exists():
                return {"success": False, "message": "Folder not found"}
            
            files = []
            if recursive:
                items = folder.rglob(pattern)
            else:
                items = folder.glob(pattern)
            
            for item in items:
                try:
                    stat = item.stat()
                    files.append({
                        "name": item.name,
                        "path": str(item.absolute()),
                        "size": stat.st_size,
                        "modified": time.ctime(stat.st_mtime),
                        "is_file": item.is_file(),
                        "is_dir": item.is_dir()
                    })
                except Exception:
                    pass
            
            return {"success": True, "files": files, "count": len(files)}
        
        except Exception as e:
            logger.error(f"Failed to list files in {path}: {e}")
            return {"success": False, "message": str(e)}
    
    def copy_folder(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a folder"""
        if not self._check_permission("copy_folder", RiskLevel.HIGH, 
                                     {"source": source, "dest": destination}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            shutil.copytree(source, destination)
            logger.info(f"Copied folder: {source} -> {destination}")
            return {"success": True, "message": f"Copied to {destination}"}
        
        except Exception as e:
            logger.error(f"Failed to copy folder {source}: {e}")
            return {"success": False, "message": str(e)}
    
    # ==================== ADVANCED OPERATIONS ====================
    
    def organize_desktop(self) -> Dict[str, Any]:
        """Organize desktop files into folders"""
        if not self._check_permission("organize_desktop", RiskLevel.MEDIUM):
            return {"success": False, "message": "Permission denied"}
        
        try:
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                return {"success": False, "message": "Desktop folder not found"}
            
            # Create organization folders
            folders = {
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"],
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
                "Videos": [".mp4", ".avi", ".mkv", ".mov"],
                "Music": [".mp3", ".wav", ".flac", ".m4a"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Programs": [".exe", ".msi"]
            }
            
            moved_count = 0
            for folder_name, extensions in folders.items():
                folder_path = desktop / folder_name
                folder_path.mkdir(exist_ok=True)
                
                for ext in extensions:
                    for file in desktop.glob(f"*{ext}"):
                        if file.is_file():
                            try:
                                shutil.move(str(file), str(folder_path / file.name))
                                moved_count += 1
                            except Exception:
                                pass
            
            logger.info(f"Organized desktop: moved {moved_count} files")
            return {"success": True, "message": f"Organized {moved_count} files", "count": moved_count}
        
        except Exception as e:
            logger.error(f"Failed to organize desktop: {e}")
            return {"success": False, "message": str(e)}
    
    def clean_temp_files(self) -> Dict[str, Any]:
        """Clean temporary files"""
        if not self._check_permission("clean_temp", RiskLevel.HIGH):
            return {"success": False, "message": "Permission denied"}
        
        try:
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            
            deleted_count = 0
            deleted_size = 0
            
            for item in temp_dir.iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        deleted_count += 1
                        deleted_size += size
                    elif item.is_dir():
                        shutil.rmtree(item)
                        deleted_count += 1
                except Exception:
                    pass
            
            size_mb = deleted_size / (1024**2)
            logger.info(f"Cleaned temp files: {deleted_count} items, {size_mb:.2f} MB")
            return {
                "success": True, 
                "message": f"Cleaned {deleted_count} items",
                "count": deleted_count,
                "size_mb": f"{size_mb:.2f}"
            }
        
        except Exception as e:
            logger.error(f"Failed to clean temp files: {e}")
            return {"success": False, "message": str(e)}
    
    def search_files(self, directory: str, filename: str, recursive: bool = True) -> Dict[str, Any]:
        """Search for files by name"""
        try:
            folder = Path(directory)
            if not folder.exists():
                return {"success": False, "message": "Directory not found"}
            
            results = []
            if recursive:
                items = folder.rglob(f"*{filename}*")
            else:
                items = folder.glob(f"*{filename}*")
            
            for item in items:
                try:
                    results.append({
                        "name": item.name,
                        "path": str(item.absolute()),
                        "is_file": item.is_file(),
                        "size": item.stat().st_size if item.is_file() else 0
                    })
                except Exception:
                    pass
            
            return {"success": True, "results": results, "count": len(results)}
        
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return {"success": False, "message": str(e)}
    
    def create_backup(self, source: str, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create backup of file or folder"""
        if not self._check_permission("create_backup", RiskLevel.MEDIUM, {"source": source}):
            return {"success": False, "message": "Permission denied"}
        
        try:
            source_path = Path(source)
            if not source_path.exists():
                return {"success": False, "message": "Source not found"}
            
            if backup_name is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_name = f"{source_path.name}_backup_{timestamp}"
            
            backup_path = source_path.parent / backup_name
            
            if source_path.is_file():
                shutil.copy2(source, backup_path)
            else:
                shutil.copytree(source, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return {"success": True, "message": "Backup created", "path": str(backup_path)}
        
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {"success": False, "message": str(e)}

# Global instance
file_actions = FileActions()
