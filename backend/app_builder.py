"""
ShivAI Atlas - App Builder
Generate GUI applications from templates
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from ..core.config import TEMPLATES_DIR, GENERATED_APPS_DIR
from ..core.logger import get_logger

logger = get_logger(__name__)

class AppBuilder:
    """Builds GUI applications from templates"""
    
    def __init__(self):
        self.templates_dir = TEMPLATES_DIR / "app_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = GENERATED_APPS_DIR
        self._init_templates()
        logger.info("AppBuilder initialized")
    
    def _init_templates(self):
        """Initialize app templates"""
        templates = {
            "todo": self._get_todo_template(),
            "calculator": self._get_calculator_template(),
            "notes": self._get_notes_template(),
            "timer": self._get_timer_template()
        }
        
        for name, code in templates.items():
            template_file = self.templates_dir / f"{name}.py"
            if not template_file.exists():
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(code)
    
    def create_app(self, app_type: str, app_name: Optional[str] = None,
                  custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new app from template"""
        try:
            app_name = app_name or f"{app_type}_app"
            custom_params = custom_params or {}
            
            # Get template code
            template = self._get_template(app_type)
            if not template:
                return {
                    "success": False,
                    "message": f"Unknown app type: {app_type}"
                }
            
            # Customize template
            code = self._customize_template(template, app_name, custom_params)
            
            # Create app directory
            app_dir = self.output_dir / app_name
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Write main file
            main_file = app_dir / "main.py"
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Create run script
            run_script = app_dir / "run.bat"
            with open(run_script, 'w') as f:
                f.write(f"@echo off\npython main.py\npause")
            
            logger.info(f"Created app: {app_name} ({app_type})")
            
            return {
                "success": True,
                "message": f"App '{app_name}' created successfully",
                "app_name": app_name,
                "app_type": app_type,
                "path": str(app_dir),
                "main_file": str(main_file)
            }
        
        except Exception as e:
            logger.error(f"Failed to create app: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def _get_template(self, app_type: str) -> Optional[str]:
        """Get template code for app type"""
        templates = {
            "todo": self._get_todo_template(),
            "calculator": self._get_calculator_template(),
            "notes": self._get_notes_template(),
            "timer": self._get_timer_template()
        }
        return templates.get(app_type)
    
    def _customize_template(self, template: str, app_name: str, 
                          params: Dict[str, Any]) -> str:
        """Customize template with parameters"""
        code = template.replace("{{APP_NAME}}", app_name)
        
        for key, value in params.items():
            code = code.replace(f"{{{{{key}}}}}", str(value))
        
        return code
    
    def _get_todo_template(self) -> str:
        """Todo app template"""
        return '''
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("{{APP_NAME}}")
        self.root.geometry("600x500")
        
        self.tasks = []
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="✓ Todo List", font=("Arial", 20, "bold"))
        header.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.task_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.task_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        add_btn = tk.Button(input_frame, text="Add", command=self.add_task,
                          bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Task list
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = tk.Listbox(list_frame, font=("Arial", 11),
                                      yscrollcommand=scrollbar.set)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Complete", command=self.complete_task,
                bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_task,
                bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear All", command=self.clear_all,
                bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
    
    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append({"task": task, "done": False})
            self.refresh_list()
            self.task_entry.delete(0, tk.END)
    
    def complete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            idx = selection[0]
            self.tasks[idx]["done"] = True
            self.refresh_list()
    
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            idx = selection[0]
            del self.tasks[idx]
            self.refresh_list()
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all tasks?"):
            self.tasks = []
            self.refresh_list()
    
    def refresh_list(self):
        self.task_listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            status = "✓" if task["done"] else "○"
            text = f"{status} {task['task']}"
            self.task_listbox.insert(tk.END, text)
            if task["done"]:
                self.task_listbox.itemconfig(i, fg="gray")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
'''
    
    def _get_calculator_template(self) -> str:
        """Calculator app template"""
        return '''
import tkinter as tk
from tkinter import ttk

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("{{APP_NAME}}")
        self.root.geometry("350x450")
        self.root.resizable(False, False)
        
        self.equation = ""
        self.setup_ui()
    
    def setup_ui(self):
        # Display
        display = tk.Entry(self.root, font=("Arial", 20), justify="right",
                         bd=10, bg="#f0f0f0")
        display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)
        self.display = display
        
        # Buttons
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
            ('C', 5, 0), ('←', 5, 1), ('(', 5, 2), (')', 5, 3)
        ]
        
        for (text, row, col) in buttons:
            btn = tk.Button(self.root, text=text, font=("Arial", 16),
                          command=lambda t=text: self.on_button_click(t),
                          bg="#4CAF50" if text == "=" else "#e0e0e0")
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
        
        # Configure grid
        for i in range(6):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
    
    def on_button_click(self, char):
        if char == '=':
            try:
                result = eval(self.equation)
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
                self.equation = str(result)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
                self.equation = ""
        elif char == 'C':
            self.equation = ""
            self.display.delete(0, tk.END)
        elif char == '←':
            self.equation = self.equation[:-1]
            self.display.delete(0, tk.END)
            self.display.insert(0, self.equation)
        else:
            self.equation += str(char)
            self.display.delete(0, tk.END)
            self.display.insert(0, self.equation)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
'''
    
    def _get_notes_template(self) -> str:
        """Notes app template"""
        return '''
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("{{APP_NAME}}")
        self.root.geometry("700x500")
        
        self.current_file = None
        self.setup_ui()
    
    def setup_ui(self):
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Text area
        self.text_area = tk.Text(self.root, font=("Arial", 12), wrap=tk.WORD,
                                undo=True)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.text_area)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_area.yview)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", anchor=tk.W,
                                   bg="#e0e0e0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.status_bar.config(text="New file")
    
    def open_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"),
                                                     ("All Files", "*.*")])
        if file:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.current_file = file
                self.status_bar.config(text=f"Opened: {file}")
    
    def save_file(self):
        if self.current_file:
            content = self.text_area.get(1.0, tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_bar.config(text=f"Saved: {self.current_file}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                           filetypes=[("Text Files", "*.txt"),
                                                    ("All Files", "*.*")])
        if file:
            content = self.text_area.get(1.0, tk.END)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.current_file = file
            self.status_bar.config(text=f"Saved: {file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
'''
    
    def _get_timer_template(self) -> str:
        """Timer app template"""
        return '''
import tkinter as tk
from tkinter import ttk

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("{{APP_NAME}}")
        self.root.geometry("400x300")
        
        self.time_left = 0
        self.running = False
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        tk.Label(self.root, text="⏱ Timer", font=("Arial", 24, "bold")).pack(pady=20)
        
        # Time display
        self.time_label = tk.Label(self.root, text="00:00", 
                                   font=("Arial", 48, "bold"))
        self.time_label.pack(pady=20)
        
        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Minutes:").pack(side=tk.LEFT, padx=5)
        self.minutes_entry = tk.Entry(input_frame, width=10, font=("Arial", 14))
        self.minutes_entry.pack(side=tk.LEFT, padx=5)
        self.minutes_entry.insert(0, "5")
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        self.start_btn = tk.Button(btn_frame, text="Start", command=self.start,
                                   bg="#4CAF50", fg="white", font=("Arial", 12),
                                   width=10)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(btn_frame, text="Pause", command=self.pause,
                                   bg="#FF9800", fg="white", font=("Arial", 12),
                                   width=10, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Reset", command=self.reset,
                bg="#f44336", fg="white", font=("Arial", 12),
                width=10).pack(side=tk.LEFT, padx=5)
    
    def start(self):
        if not self.running:
            try:
                minutes = int(self.minutes_entry.get())
                self.time_left = minutes * 60
                self.running = True
                self.start_btn.config(state=tk.DISABLED)
                self.pause_btn.config(state=tk.NORMAL)
                self.countdown()
            except ValueError:
                pass
    
    def pause(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
    
    def reset(self):
        self.running = False
        self.time_left = 0
        self.time_label.config(text="00:00")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
    
    def countdown(self):
        if self.running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.time_label.config(text=f"{mins:02d}:{secs:02d}")
            self.time_left -= 1
            self.root.after(1000, self.countdown)
        elif self.running and self.time_left == 0:
            self.time_label.config(text="Done!")
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
'''
    
    def list_templates(self) -> Dict[str, Any]:
        """List available app templates"""
        templates = ["todo", "calculator", "notes", "timer"]
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
    
    def list_created_apps(self) -> Dict[str, Any]:
        """List all created apps"""
        try:
            apps = []
            if self.output_dir.exists():
                for app_dir in self.output_dir.iterdir():
                    if app_dir.is_dir():
                        apps.append({
                            "name": app_dir.name,
                            "path": str(app_dir),
                            "created": app_dir.stat().st_ctime
                        })
            
            return {
                "success": True,
                "apps": apps,
                "count": len(apps)
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

# Global instance
app_builder = AppBuilder()
