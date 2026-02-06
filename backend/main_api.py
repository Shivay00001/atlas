from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import platform
import psutil
import os
import asyncio
from datetime import datetime
from sqlmodel import Session, select
from database import create_db_and_tables, get_session, Setting, CommandHistory
import aiofiles

app = FastAPI(title="Atlas AI Assistant Pro", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Models ---
class SystemInfo(BaseModel):
    platform: str
    processor: str
    ram_total: str
    ram_available: str
    ram_percent: float
    disk_usage: str
    disk_percent: float
    cpu_percent: float

class FileItem(BaseModel):
    name: str
    path: str
    type: str # 'file' or 'directory'
    size: Optional[int] = None
    modified: Optional[float] = None

class ChatMessage(BaseModel):
    role: str
    content: str

# --- Endpoints ---

@app.get("/system-info", response_model=SystemInfo)
async def get_system_info():
    """Get real-time system metrics"""
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu = psutil.cpu_percent(interval=None)
    
    return SystemInfo(
        platform=f"{platform.system()} {platform.release()}",
        processor=platform.processor() or platform.machine(),
        ram_total=f"{ram.total / (1024**3):.2f} GB",
        ram_available=f"{ram.available / (1024**3):.2f} GB",
        ram_percent=ram.percent,
        disk_usage=f"{disk.used / (1024**3):.0f} GB / {disk.total / (1024**3):.0f} GB",
        disk_percent=disk.percent,
        cpu_percent=cpu
    )

@app.get("/files", response_model=List[FileItem])
async def list_files(path: str = "."):
    """Real file system explorer"""
    try:
        # Security check: prevent going above root if needed, but for local tool we allow it
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Path not found")
            
        items = []
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    items.append(FileItem(
                        name=entry.name,
                        path=entry.path,
                        type='directory' if entry.is_dir() else 'file',
                        size=entry.stat().st_size if entry.is_file() else None,
                        modified=entry.stat().st_mtime
                    ))
                except PermissionError:
                    continue
        return sorted(items, key=lambda x: (x.type != 'directory', x.name.lower()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(messages: List[ChatMessage]):
    """Simulated AI Chat (Placeholder for LLM integration)"""
    # In a real product, this would call OpenAI/Anthropic/Local LLM
    last_msg = messages[-1].content.lower()
    
    response = "I can help you with that. "
    if "file" in last_msg:
        response += "I can browse your file system. Use the Files tab to explore."
    elif "system" in last_msg or "cpu" in last_msg:
        response += "Checking system status... Your CPU is running optimally."
    else:
        response += f"I processed your request: '{last_msg}'. How else can I assist you?"
        
    return {"role": "assistant", "content": response}

@app.get("/history", response_model=List[CommandHistory])
async def get_history(session: Session = Depends(get_session)):
    """Get command history from database"""
    history = session.exec(select(CommandHistory).order_by(CommandHistory.timestamp.desc()).limit(50)).all()
    return history

@app.post("/execute")
async def execute_command(command: str, session: Session = Depends(get_session)):
    """Execute a real system command (Caution!)"""
    # For safety in this demo, we only allow specific commands or mock them
    # In a real "Agent", this would use `subprocess`
    
    timestamp = datetime.now().isoformat()
    output = ""
    status = "success"
    
    try:
        if command.startswith("echo "):
            output = command[5:]
        elif command == "ping":
            output = "Pong! System is online."
        else:
            # Mock execution for safety
            output = f"Executed: {command}"
            
        # Save to DB
        db_entry = CommandHistory(command=command, timestamp=timestamp, status=status, output=output)
        session.add(db_entry)
        session.commit()
        session.refresh(db_entry)
        
        return db_entry
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/processes")
async def get_processes():
    """Get running processes with details"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by CPU usage
    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    return processes[:50]  # Return top 50 to avoid payload bloat

@app.post("/processes/{pid}/kill")
async def kill_process(pid: int):
    """Kill a process by PID"""
    try:
        process = psutil.Process(pid)
        process.terminate()
        return {"status": "success", "message": f"Process {pid} terminated"}
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=404, detail="Process not found")
    except psutil.AccessDenied:
        raise HTTPException(status_code=403, detail="Permission denied")

def get_dir_size(path):
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_dir_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total

@app.get("/disk-analysis")
async def analyze_disk(path: str = "."):
    """Analyze folder sizes with real recursive calculation"""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Path not found")
        
    results = []
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    # Calculate real size (this might be slow for huge dirs, but it's "real")
                    size = get_dir_size(entry.path)
                    results.append({"name": entry.name, "type": "directory", "size": size})
                else:
                    results.append({"name": entry.name, "type": "file", "size": entry.stat().st_size})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Sort by size, largest first
    return sorted(results, key=lambda x: x['size'], reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
