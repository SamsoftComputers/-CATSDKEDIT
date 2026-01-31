import tkinter as tk
from tkinter import ttk, scrolledtext, font
import threading
import time
import random
import re
from datetime import datetime

# --- CONFIGURATION & VISUALS (Cursor / Dark Modern Theme) ---
THEME = {
    "bg": "#0d1117",           # Main Window Background
    "fg": "#e6edf3",           # Main Text
    "sidebar": "#161b22",      # Explorer/Chat Background
    "editor_bg": "#0d1117",    # Editor Background
    "panel_bg": "#161b22",     # Terminal Background
    "border": "#30363d",       # Borders
    "accent": "#2f81f7",       # Blue Accent (Cursor-like)
    "selection": "#1f6feb",    # Text Selection
    "success": "#238636",      # Green
    "warning": "#d29922",      # Orange
    "error": "#f85149",        # Red
    
    # Syntax Highlighting Colors
    "keyword": "#ff7b72",      # Red (import, def)
    "function": "#d2a8ff",     # Purple
    "string": "#a5d6ff",       # Light Blue
    "comment": "#8b949e",      # Grey
    "class": "#f0883e",        # Orange
    "number": "#79c0ff",       # Blue
}

# --- PROCEDURAL GENERATION ASSETS ---

# A virtual file system for Ralph to navigate
VIRTUAL_FS = {
    "src": {
        "server.py": "python",
        "utils.py": "python",
        "api.rs": "rust",
        "App.jsx": "javascript",
        "styles.css": "css",
    },
    "kernel": {
        "boot.c": "c",
        "memory.h": "c",
    },
    "scripts": {
        "deploy.sh": "bash",
    },
    "README.md": "markdown"
}

# Complex task templates that Ralph will try to "solve"
GOALS = [
    {
        "name": "Refactor Authentication Logic",
        "steps": [
            {"action": "chat", "msg": "Auth logic is spaghetti. Refactoring to JWT."},
            {"action": "open", "file": "src/server.py"},
            {"action": "think", "duration": 2},
            {"action": "edit", "content": "\ndef verify_token(token):\n    try:\n        # Decoding JWT payload\n        payload = jwt.decode(token, SECRET, algorithms=['HS256'])\n        return payload\n    except jwt.ExpiredSignatureError:\n        return None\n"},
            {"action": "terminal", "cmd": "pytest tests/auth_test.py"},
            {"action": "chat", "msg": "Tests passed. Merging."}
        ]
    },
    {
        "name": "Optimize Rendering Engine",
        "steps": [
            {"action": "chat", "msg": "FPS is dropping. Need to optimize the render loop."},
            {"action": "open", "file": "kernel/boot.c"},
            {"action": "edit", "content": "\nvoid render_frame() {\n    // Use double buffering\n    if (buffer_ready) {\n        swap_buffers();\n    }\n    // Clear V-Sync\n    gpu_sync();\n}\n"},
            {"action": "terminal", "cmd": "make build"},
            {"action": "chat", "msg": "Kernel rebuilt. Performance increased by 15%."}
        ]
    },
    {
        "name": "Update Frontend Components",
        "steps": [
            {"action": "chat", "msg": "The UI looks like 1999. Updating components."},
            {"action": "open", "file": "src/App.jsx"},
            {"action": "think", "duration": 1.5},
            {"action": "edit", "content": "\nconst Dashboard = () => {\n  const [data, setData] = useState(null);\n  useEffect(() => {\n    fetchData().then(d => setData(d));\n  }, []);\n\n  return (\n    <div className=\"dashboard-container\">\n      <Header title=\"RalphOS\" />\n      <Sidebar />\n    </div>\n  );\n};\n"},
            {"action": "terminal", "cmd": "npm run build"},
            {"action": "chat", "msg": "Build successful. Deploying to edge."}
        ]
    },
    {
        "name": "Rewrite Memory Allocator",
        "steps": [
            {"action": "chat", "msg": "Memory leaks detected. Rewriting allocator in Rust."},
            {"action": "open", "file": "src/api.rs"},
            {"action": "edit", "content": "\nfn unsafe_allocation(size: usize) -> *mut u8 {\n    // DANGER: Manual memory management\n    unsafe {\n        let layout = Layout::from_size_align(size, 8).unwrap();\n        alloc(layout)\n    }\n}\n"},
            {"action": "terminal", "cmd": "cargo check"},
            {"action": "chat", "msg": "Borrow checker is happy. I am happy."}
        ]
    }
]

# Random "Thoughts" to display in status bar
THOUGHTS = [
    "Compiling shaders...",
    "Rebalancing binary trees...",
    "Ignored a linting error (it was annoying)...",
    "Checking StackOverflow (simulated)...",
    "Drinking virtual coffee...",
    "Centering a div...",
    "Resolving git merge conflict...",
    "Reading documentation...",
]

# --- UI COMPONENTS ---

class EditorPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["editor_bg"])
        
        # Tabs bar (Simulated)
        self.tabs_frame = tk.Frame(self, bg=THEME["bg"], height=30)
        self.tabs_frame.pack(fill="x", side="top")
        self.tab_label = tk.Label(self.tabs_frame, text="No File Open", bg=THEME["bg"], fg=THEME["fg"], font=("Segoe UI", 9))
        self.tab_label.pack(side="left", padx=10, pady=5)
        
        # Code Area
        self.text_area = scrolledtext.ScrolledText(
            self, bg=THEME["editor_bg"], fg=THEME["fg"],
            font=("Consolas", 11), insertbackground=THEME["accent"],
            borderwidth=0, highlightthickness=0
        )
        self.text_area.pack(fill="both", expand=True, padx=5, pady=0)
        
        # Status Bar
        self.status_bar = tk.Label(self, text="Ralph Agent: IDLE", bg=THEME["accent"], fg="white", font=("Segoe UI", 9), anchor="w")
        self.status_bar.pack(fill="x", side="bottom")

        self.setup_tags()

    def setup_tags(self):
        # Syntax highlighting tags
        self.text_area.tag_configure("keyword", foreground=THEME["keyword"])
        self.text_area.tag_configure("function", foreground=THEME["function"])
        self.text_area.tag_configure("string", foreground=THEME["string"])
        self.text_area.tag_configure("comment", foreground=THEME["comment"])
        self.text_area.tag_configure("class", foreground=THEME["class"])

    def highlight_syntax(self):
        content = self.text_area.get("1.0", tk.END)
        
        # Simple regex-based highlighting
        replacements = [
            (r'\b(def|class|import|from|return|if|else|while|for|try|except|const|let|var|function|fn|pub|impl|struct|void|int|char)\b', "keyword"),
            (r'\b([a-zA-Z_]\w*)(?=\()', "function"),
            (r'(".*?"|\'.*?\')', "string"),
            (r'(//.*|#.*)', "comment"),
            (r'\b([A-Z][a-zA-Z0-9_]*)\b', "class")
        ]
        
        for regex, tag in replacements:
            for match in re.finditer(regex, content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.text_area.tag_add(tag, start, end)

    def set_file(self, filename, content=""):
        self.tab_label.config(text=f" {filename} ", bg=THEME["sidebar"])
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)
        self.highlight_syntax()

    def append_text(self, text):
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.highlight_syntax()

class TerminalPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["panel_bg"], height=150)
        self.pack_propagate(False)
        
        header = tk.Frame(self, bg=THEME["bg"], height=25)
        header.pack(fill="x")
        tk.Label(header, text=" TERMINAL ", fg=THEME["fg"], bg=THEME["bg"], font=("Segoe UI", 8, "bold")).pack(side="left", padx=5)

        self.term_text = scrolledtext.ScrolledText(
            self, bg=THEME["panel_bg"], fg=THEME["fg"],
            font=("Consolas", 10), borderwidth=0, highlightthickness=0
        )
        self.term_text.pack(fill="both", expand=True)
        self.log("Ralph Agent Terminal initialized...")

    def log(self, message):
        self.term_text.insert(tk.END, f"\n$ {message}")
        self.term_text.see(tk.END)

    def log_raw(self, message):
        self.term_text.insert(tk.END, f"\n{message}")
        self.term_text.see(tk.END)

class ExplorerPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["sidebar"], width=200)
        self.pack_propagate(False)
        
        tk.Label(self, text="EXPLORER", bg=THEME["sidebar"], fg=THEME["comment"], font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", padx=10, pady=5)
        
        self.tree = ttk.Treeview(self, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True)
        
        # Style the tree
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=THEME["sidebar"], foreground=THEME["fg"], fieldbackground=THEME["sidebar"], borderwidth=0)
        style.map("Treeview", background=[('selected', THEME["selection"])])
        
        self.populate()

    def populate(self):
        root_node = self.tree.insert("", "end", text="PROJECT-RALPH", open=True)
        for folder, files in VIRTUAL_FS.items():
            if isinstance(files, dict):
                folder_node = self.tree.insert(root_node, "end", text=folder, open=True)
                for file in files:
                    self.tree.insert(folder_node, "end", text=file)
            else:
                self.tree.insert(root_node, "end", text=folder) # It's a file at root

class ChatPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["sidebar"], width=250)
        self.pack_propagate(False)
        
        tk.Label(self, text="RALPH AI CHAT", bg=THEME["sidebar"], fg=THEME["fg"], font=("Segoe UI", 9, "bold")).pack(fill="x", pady=5)
        
        self.history = scrolledtext.ScrolledText(
            self, bg=THEME["sidebar"], fg=THEME["fg"],
            font=("Segoe UI", 10), wrap="word", borderwidth=0
        )
        self.history.pack(fill="both", expand=True, padx=5, pady=5)
        self.add_message("Ralph", "Agent initialized. Ready to vibe code.")

    def add_message(self, sender, msg):
        self.history.insert(tk.END, f"\n[{sender}]: ", "bold")
        self.history.insert(tk.END, f"{msg}\n")
        self.history.see(tk.END)
        self.history.tag_configure("bold", font=("Segoe UI", 10, "bold"), foreground=THEME["accent"])

# --- THE BRAIN (AUTONOMOUS AGENT) ---

class RalphAgent:
    def __init__(self, editor, terminal, chat):
        self.editor = editor
        self.terminal = terminal
        self.chat = chat
        self.running = True
        self.current_goal_idx = 0
        
    def start(self):
        threading.Thread(target=self.run_loop, daemon=True).start()

    def type_code(self, text):
        """Simulates human typing"""
        for char in text:
            if not self.running: break
            self.editor.append_text(char)
            # Random delay for realistic typing feel
            time.sleep(random.uniform(0.01, 0.08)) 
            
            # Occasional pause for "thinking"
            if random.random() < 0.05:
                time.sleep(0.3)

    def run_loop(self):
        while self.running:
            # 1. Pick a Goal
            goal = GOALS[self.current_goal_idx % len(GOALS)]
            self.editor.status_bar.config(text=f"Ralph Agent: {goal['name']}")
            
            # 2. Execute Steps
            for step in goal["steps"]:
                if not self.running: break
                
                action = step["action"]
                
                if action == "chat":
                    time.sleep(1)
                    self.chat.add_message("Ralph", step["msg"])
                    
                elif action == "open":
                    time.sleep(1)
                    self.editor.status_bar.config(text=f"Ralph Agent: Opening {step['file']}...")
                    self.editor.set_file(step['file'], content="# File opened by Ralph\n")
                    self.terminal.log(f"opening {step['file']}")
                    
                elif action == "edit":
                    self.editor.status_bar.config(text="Ralph Agent: Writing code...")
                    self.type_code(step["content"])
                    
                elif action == "terminal":
                    self.editor.status_bar.config(text="Ralph Agent: Running commands...")
                    time.sleep(1)
                    self.terminal.log(step["cmd"])
                    time.sleep(0.5)
                    self.terminal.log_raw("... Executing ...")
                    time.sleep(1.5)
                    self.terminal.log_raw(f"Process finished with exit code 0 ({random.randint(100, 900)}ms)")
                
                elif action == "think":
                    thought = random.choice(THOUGHTS)
                    self.editor.status_bar.config(text=f"Ralph Agent: {thought}")
                    time.sleep(step["duration"])

                time.sleep(1)

            # Goal Complete
            self.chat.add_message("Ralph", f"Completed: {goal['name']}. Taking a quick break.")
            self.current_goal_idx += 1
            time.sleep(3)

# --- MAIN APP ---

class RalphIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ralph Code - Autonomous Agent Simulator")
        self.geometry("1100x700")
        self.configure(bg=THEME["bg"])
        
        # Main Layout (Paned Window)
        self.main_pane = tk.PanedWindow(self, orient="horizontal", bg=THEME["bg"], sashwidth=2)
        self.main_pane.pack(fill="both", expand=True)

        # Left: Explorer
        self.explorer = ExplorerPanel(self.main_pane)
        self.main_pane.add(self.explorer, minsize=150)

        # Center: Editor + Terminal (Vertical split)
        self.center_pane = tk.PanedWindow(self.main_pane, orient="vertical", bg=THEME["bg"], sashwidth=2)
        self.main_pane.add(self.center_pane, minsize=500)
        
        self.editor = EditorPanel(self.center_pane)
        self.center_pane.add(self.editor, stretch="always")
        
        self.terminal = TerminalPanel(self.center_pane)
        self.center_pane.add(self.terminal, minsize=150)

        # Right: Chat
        self.chat = ChatPanel(self.main_pane)
        self.main_pane.add(self.chat, minsize=250)

        # Start Ralph
        self.agent = RalphAgent(self.editor, self.terminal, self.chat)
        self.after(1000, self.agent.start)

if __name__ == "__main__":
    app = RalphIDE()
    app.mainloop()
