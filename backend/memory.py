"""
ShivAI Atlas - Memory Agent & Database
Long-term memory storage and retrieval system
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from .config import config
from .logger import get_logger

logger = get_logger(__name__)

class MemoryDatabase:
    """SQLite database for Atlas memory"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or config.db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            cursor = self.conn.cursor()
            
            # Memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Workflows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    steps TEXT NOT NULL,
                    category TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    usage_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Usage stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    agent TEXT,
                    success BOOLEAN,
                    duration_ms INTEGER,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    intent TEXT,
                    confidence REAL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch one result"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Fetch all results"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

class MemoryAgent:
    """Agent for managing long-term memory"""
    
    def __init__(self):
        self.db = MemoryDatabase()
        logger.info("MemoryAgent initialized")
    
    def remember(self, key: str, value: Any, category: str = "general", 
                metadata: Dict[str, Any] = None) -> bool:
        """Store a memory"""
        try:
            value_str = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
            metadata_str = json.dumps(metadata or {}, ensure_ascii=False)
            
            self.db.execute("""
                INSERT OR REPLACE INTO memories (key, value, category, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value_str, category, metadata_str))
            
            logger.info(f"Memory stored: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    def recall(self, key: str) -> Optional[Any]:
        """Retrieve a memory"""
        try:
            row = self.db.fetch_one("SELECT value FROM memories WHERE key = ?", (key,))
            if row:
                try:
                    return json.loads(row['value'])
                except json.JSONDecodeError:
                    return row['value']
            return None
        except Exception as e:
            logger.error(f"Failed to recall memory: {e}")
            return None
    
    def search_memories(self, category: Optional[str] = None, 
                       limit: int = 50) -> List[Dict[str, Any]]:
        """Search memories by category"""
        try:
            if category:
                rows = self.db.fetch_all(
                    "SELECT * FROM memories WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
                    (category, limit)
                )
            else:
                rows = self.db.fetch_all(
                    "SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def forget(self, key: str) -> bool:
        """Delete a memory"""
        try:
            self.db.execute("DELETE FROM memories WHERE key = ?", (key,))
            logger.info(f"Memory forgotten: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to forget memory: {e}")
            return False
    
    def save_workflow(self, name: str, description: str, steps: List[Dict[str, Any]], 
                     category: str = "custom") -> bool:
        """Save a workflow"""
        try:
            steps_str = json.dumps(steps, ensure_ascii=False)
            self.db.execute("""
                INSERT OR REPLACE INTO workflows (name, description, steps, category)
                VALUES (?, ?, ?, ?)
            """, (name, description, steps_str, category))
            
            logger.info(f"Workflow saved: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            return False
    
    def get_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a workflow"""
        try:
            row = self.db.fetch_one("SELECT * FROM workflows WHERE name = ?", (name,))
            if row:
                result = dict(row)
                result['steps'] = json.loads(result['steps'])
                return result
            return None
        except Exception as e:
            logger.error(f"Failed to get workflow: {e}")
            return None
    
    def list_workflows(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all workflows"""
        try:
            if category:
                rows = self.db.fetch_all(
                    "SELECT * FROM workflows WHERE category = ? AND enabled = 1 ORDER BY name",
                    (category,)
                )
            else:
                rows = self.db.fetch_all(
                    "SELECT * FROM workflows WHERE enabled = 1 ORDER BY name"
                )
            
            workflows = []
            for row in rows:
                wf = dict(row)
                wf['steps'] = json.loads(wf['steps'])
                workflows.append(wf)
            
            return workflows
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    def update_workflow_usage(self, name: str):
        """Update workflow usage statistics"""
        try:
            self.db.execute("""
                UPDATE workflows 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (name,))
        except Exception as e:
            logger.error(f"Failed to update workflow usage: {e}")
    
    def log_usage(self, command: str, agent: str, success: bool, 
                 duration_ms: int, metadata: Dict[str, Any] = None):
        """Log command usage statistics"""
        try:
            metadata_str = json.dumps(metadata or {}, ensure_ascii=False)
            self.db.execute("""
                INSERT INTO usage_stats (command, agent, success, duration_ms, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (command, agent, success, duration_ms, metadata_str))
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")
    
    def save_conversation(self, user_input: str, agent_response: str, 
                         intent: str = None, confidence: float = None,
                         metadata: Dict[str, Any] = None):
        """Save conversation turn"""
        try:
            metadata_str = json.dumps(metadata or {}, ensure_ascii=False)
            self.db.execute("""
                INSERT INTO conversations (user_input, agent_response, intent, confidence, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (user_input, agent_response, intent, confidence, metadata_str))
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        try:
            rows = self.db.fetch_all(
                "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []
    
    def set_preference(self, key: str, value: Any) -> bool:
        """Set user preference"""
        try:
            value_str = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
            self.db.execute("""
                INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value_str))
            return True
        except Exception as e:
            logger.error(f"Failed to set preference: {e}")
            return False
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        try:
            row = self.db.fetch_one("SELECT value FROM user_preferences WHERE key = ?", (key,))
            if row:
                try:
                    return json.loads(row['value'])
                except json.JSONDecodeError:
                    return row['value']
            return default
        except Exception as e:
            logger.error(f"Failed to get preference: {e}")
            return default
    
    def suggest_workflows(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Suggest workflows based on usage patterns"""
        try:
            rows = self.db.fetch_all("""
                SELECT * FROM workflows 
                WHERE enabled = 1 
                ORDER BY usage_count DESC, last_used DESC 
                LIMIT ?
            """, (limit,))
            
            suggestions = []
            for row in rows:
                wf = dict(row)
                wf['steps'] = json.loads(wf['steps'])
                suggestions.append(wf)
            
            return suggestions
        except Exception as e:
            logger.error(f"Failed to suggest workflows: {e}")
            return []

# Global memory agent instance
memory_agent = MemoryAgent()
