#!/usr/bin/env python3
"""
Cat Code 1.0 - VS Code Clone with Cat Copilot
CatSDK by Team Flames / Samsoft

Embedded CatLLM Engine (Emulated DeepSeek R1 14B style)
Fully self-contained - no downloads, no API calls
Sophisticated pattern matching + Markov chains + templates
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import random
import time
import threading
import hashlib
from collections import defaultdict

# ============================================================================
# CATLLM ENGINE - Emulated 14B Parameter Language Model
# ============================================================================

class CatLLM:
    """
    CatLLM v1.0 - Emulated DeepSeek R1 14B Distill
    
    Architecture simulation:
    - Pattern recognition layer (regex + keyword matching)
    - Context window (tracks conversation/code history)
    - Markov chain text generation
    - Template-based code completion
    - Probabilistic response selection
    - Simulated "thinking" tokens
    
    No actual neural network - pure algorithmic simulation
    """
    
    def __init__(self):
        self.model_id = "CatLLM-14B-Distill-v1"
        self.context_window = 4096
        self.temperature = 0.7
        self.top_p = 0.9
        self.context = []
        self.code_memory = {}
        self.thinking = False
        
        self._init_python_knowledge()
        self._init_code_templates()
        self._init_chat_responses()
        
    def _init_python_knowledge(self):
        """Python syntax and semantics knowledge"""
        self.python_keywords = {
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try',
            'except', 'finally', 'with', 'as', 'import', 'from', 'return',
            'yield', 'raise', 'pass', 'break', 'continue', 'lambda', 'async',
            'await', 'global', 'nonlocal', 'assert', 'del', 'in', 'is', 'not',
            'and', 'or', 'True', 'False', 'None'
        }
        
        self.builtin_functions = {
            'print': ('print(value, ..., sep=" ", end="\\n")', 'Print objects'),
            'len': ('len(obj)', 'Return length'),
            'range': ('range(stop)', 'Generate sequence'),
            'str': ('str(object)', 'Convert to string'),
            'int': ('int(x)', 'Convert to integer'),
            'float': ('float(x)', 'Convert to float'),
            'list': ('list(iterable)', 'Create list'),
            'dict': ('dict(**kwargs)', 'Create dictionary'),
            'set': ('set(iterable)', 'Create set'),
            'open': ('open(file, mode="r")', 'Open file'),
            'input': ('input(prompt)', 'Read input'),
            'type': ('type(object)', 'Return type'),
            'isinstance': ('isinstance(obj, cls)', 'Check type'),
            'enumerate': ('enumerate(iterable)', 'Enumerate'),
            'zip': ('zip(*iterables)', 'Zip iterables'),
            'map': ('map(func, iterable)', 'Map function'),
            'filter': ('filter(func, iterable)', 'Filter'),
            'sorted': ('sorted(iterable)', 'Sort'),
            'sum': ('sum(iterable)', 'Sum values'),
            'min': ('min(iterable)', 'Minimum'),
            'max': ('max(iterable)', 'Maximum'),
            'abs': ('abs(x)', 'Absolute value'),
            'round': ('round(x, n)', 'Round number'),
        }
        
        self.common_imports = {
            'os': ['path', 'getcwd', 'listdir', 'mkdir', 'remove', 'environ'],
            'sys': ['argv', 'exit', 'path', 'version', 'platform'],
            'json': ['load', 'loads', 'dump', 'dumps'],
            'math': ['sqrt', 'sin', 'cos', 'tan', 'pi', 'e', 'floor', 'ceil'],
            'random': ['random', 'randint', 'choice', 'shuffle', 'sample'],
            'datetime': ['datetime', 'date', 'time', 'timedelta'],
            're': ['match', 'search', 'findall', 'sub', 'compile'],
            'collections': ['defaultdict', 'Counter', 'deque', 'namedtuple'],
            'pathlib': ['Path'],
            'typing': ['List', 'Dict', 'Tuple', 'Optional', 'Union', 'Any'],
            'tkinter': ['Tk', 'Frame', 'Label', 'Button', 'Entry', 'Text'],
            'pygame': ['init', 'display', 'event', 'draw', 'sprite'],
        }
        
    def _init_code_templates(self):
        """Code completion patterns"""
        self.patterns = {
            r'^def\s+(\w+)\s*\($': self._complete_function_def,
            r'^class\s+(\w+)': self._complete_class_def,
            r'^import\s+(\w*)$': self._complete_import,
            r'^from\s+(\w+)\s+import\s*(\w*)$': self._complete_from_import,
            r'^if\s+': self._complete_if,
            r'^for\s+(\w+)\s+in\s+': self._complete_for,
            r'^while\s+': self._complete_while,
            r'^try:\s*$': self._complete_try,
            r'^with\s+': self._complete_with,
            r'^print\($': self._complete_print,
            r'(\w+)\.\s*$': self._complete_attribute,
            r'^#\s*': self._complete_comment,
        }
        
    def _init_chat_responses(self):
        """Chat response templates"""
        self.greetings = [
            "Meow! 🐱 How can I help you code today?",
            "Hey there! Cat Copilot ready to help~ nyaa~",
            "*stretches paws* Ready for some purr-fect code!",
            "Mrow! What are we building today?",
            "🐱 CatLLM online! Let's code something awesome~",
        ]
        
        self.thinking_phrases = [
            "Let me think about that...",
            "*thinking noises* 🤔",
            "Hmm, analyzing your code...",
            "Processing... *purrs computationally*",
            "One moment~",
        ]
        
        self.explanations = {
            'function': "A function is a reusable block of code. Define with `def name(args):`",
            'class': "A class bundles data and methods. Define with `class Name:`",
            'loop': "Loops repeat code. `for` iterates, `while` repeats until false.",
            'list': "Lists are ordered collections. Create with `[]`, access by index.",
            'dict': "Dicts store key-value pairs. Create with `{}`, access by key.",
            'exception': "Handle errors with `try/except` to avoid crashes.",
            'import': "Imports bring in external code. `import x` or `from x import y`",
        }
        
        self.error_help = {
            'SyntaxError': "Check colons, parentheses, quotes, and indentation!",
            'NameError': "Variable/function not defined. Check spelling or imports.",
            'TypeError': "Wrong type. Check if mixing strings/numbers.",
            'IndexError': "Index out of range. Lists start at 0!",
            'KeyError': "Key not in dict. Use `.get(key, default)`.",
            'AttributeError': "Object doesn't have that attribute/method.",
            'ImportError': "Module not found. Check name and installation.",
            'IndentationError': "Use consistent indentation (4 spaces).",
        }
    
    # ========================================================================
    # Code Completion
    # ========================================================================
    
    def complete(self, code_context, cursor_line, cursor_col):
        """Generate code completions"""
        self.thinking = True
        time.sleep(random.uniform(0.03, 0.1))
        
        suggestions = []
        current_line = cursor_line.strip()
        
        for pattern, handler in self.patterns.items():
            match = re.match(pattern, current_line)
            if match:
                suggestions.extend(handler(match, code_context))
                break
        
        if not suggestions:
            suggestions = self._complete_generic(current_line, code_context)
        
        self.thinking = False
        return suggestions[:8]
    
    def _complete_function_def(self, match, context):
        func_name = match.group(1) if match.lastindex else "func"
        suggestions = []
        
        if 'init' in func_name.lower():
            suggestions.append("self):\n        pass")
            suggestions.append("self, name, value):\n        self.name = name\n        self.value = value")
        elif 'get' in func_name.lower():
            suggestions.append("self, key):\n        return self._data.get(key)")
        elif 'set' in func_name.lower():
            suggestions.append("self, key, value):\n        self._data[key] = value")
        elif 'is_' in func_name.lower() or 'has_' in func_name.lower():
            suggestions.append("self):\n        return bool(self._value)")
        elif 'load' in func_name.lower():
            suggestions.append("filename):\n        with open(filename, 'r') as f:\n            return f.read()")
        elif 'save' in func_name.lower():
            suggestions.append("data, filename):\n        with open(filename, 'w') as f:\n            f.write(data)")
        elif 'main' in func_name.lower():
            suggestions.append("):\n        print('Hello, World!')\n\n\nif __name__ == '__main__':\n    main()")
        else:
            suggestions.append("):\n        pass")
            suggestions.append("arg1, arg2):\n        return arg1 + arg2")
            suggestions.append("*args, **kwargs):\n        pass")
        
        return suggestions
    
    def _complete_class_def(self, match, context):
        class_name = match.group(1) if match.lastindex else "MyClass"
        return [
            f':\n    """A {class_name} class."""\n    \n    def __init__(self):\n        pass',
            f':\n    def __init__(self, name):\n        self.name = name\n    \n    def __repr__(self):\n        return f"{class_name}({{self.name}})"',
        ]
    
    def _complete_import(self, match, context):
        partial = match.group(1) if match.lastindex else ""
        suggestions = [m for m in sorted(self.common_imports.keys()) if m.startswith(partial)]
        return suggestions[:8]
    
    def _complete_from_import(self, match, context):
        module = match.group(1)
        partial = match.group(2) if match.lastindex > 1 else ""
        if module in self.common_imports:
            return [i for i in self.common_imports[module] if i.startswith(partial)]
        return []
    
    def _complete_if(self, match, context):
        return [
            "condition:\n        pass",
            "x is not None:\n        pass",
            "len(items) > 0:\n        pass",
        ]
    
    def _complete_for(self, match, context):
        var = match.group(1) if match.lastindex else "item"
        return [
            f"\n        print({var})",
            f"\n        result.append({var})",
        ]
    
    def _complete_while(self, match, context):
        return ["True:\n        pass", "condition:\n        break"]
    
    def _complete_try(self, match, context):
        return [
            '\n        pass\n    except Exception as e:\n        print(f"Error: {e}")',
        ]
    
    def _complete_with(self, match, context):
        return [
            "open(filename, 'r') as f:\n        content = f.read()",
        ]
    
    def _complete_print(self, match, context):
        return ['"Hello, World!")', 'f"Value: {value}")', '*args, sep=", ")']
    
    def _complete_attribute(self, match, context):
        obj = match.group(1).lower()
        attrs = {
            'self': ['_data', '_cache', '__init__', '__str__'],
            'str': ['strip()', 'split()', 'join()', 'replace()', 'lower()', 'upper()'],
            'list': ['append()', 'extend()', 'pop()', 'remove()', 'sort()'],
            'dict': ['get()', 'keys()', 'values()', 'items()', 'update()'],
            'os': ['path', 'getcwd()', 'listdir()', 'mkdir()'],
            'path': ['exists()', 'join()', 'dirname()', 'basename()'],
            'f': ['read()', 'write()', 'readline()', 'close()'],
        }
        return attrs.get(obj, ['__class__', '__dict__'])
    
    def _complete_comment(self, match, context):
        return ["TODO: ", "FIXME: ", "NOTE: ", "Initialize ", "Handle ", "Process "]
    
    def _complete_generic(self, line, context):
        words = line.split()
        current = words[-1] if words else ""
        suggestions = []
        
        for kw in self.python_keywords:
            if kw.startswith(current.lower()):
                suggestions.append(kw)
        
        for builtin in self.builtin_functions:
            if builtin.startswith(current.lower()):
                suggestions.append(f"{builtin}()")
        
        return suggestions
    
    # ========================================================================
    # Chat Interface
    # ========================================================================
    
    def chat(self, message, code_context=""):
        """Process chat and generate response"""
        self.thinking = True
        self.context.append({"role": "user", "content": message})
        time.sleep(random.uniform(0.15, 0.4))
        
        response = self._generate_response(message, code_context)
        
        self.context.append({"role": "assistant", "content": response})
        self.thinking = False
        return response
    
    def _generate_response(self, message, code_context):
        msg = message.lower()
        
        # Greetings
        if any(g in msg for g in ['hello', 'hi', 'hey', 'meow', 'sup']):
            return random.choice(self.greetings)
        
        # Error help
        for err, help_text in self.error_help.items():
            if err.lower() in msg:
                return f"🐱 {err}? {help_text}"
        
        # Explanations
        for concept, explanation in self.explanations.items():
            if concept in msg:
                return f"🐱 {explanation}"
        
        # Explain code
        if 'explain' in msg or 'what does' in msg:
            return self._explain_code(code_context)
        
        # Fix help
        if any(w in msg for w in ['fix', 'help', 'error', 'bug']):
            return self._suggest_fix(code_context)
        
        # How to
        if 'how to' in msg or 'how do' in msg:
            return self._how_to(message)
        
        # Generate
        if any(w in msg for w in ['write', 'create', 'make', 'generate']):
            return self._generate_code(message)
        
        return random.choice([
            "🐱 Tell me more about what you're building!",
            "🐱 I can help with code completion, explanations, and debugging!",
            "🐱 What would you like to code today?",
        ])
    
    def _explain_code(self, code):
        if not code.strip():
            return "🐱 Paste some code and I'll explain it!"
        
        explanation = "🐱 Here's what I see:\n\n"
        for line in code.strip().split('\n')[:8]:
            line = line.strip()
            if line.startswith('def '):
                m = re.match(r'def\s+(\w+)', line)
                if m: explanation += f"• Function `{m.group(1)}`\n"
            elif line.startswith('class '):
                m = re.match(r'class\s+(\w+)', line)
                if m: explanation += f"• Class `{m.group(1)}`\n"
            elif line.startswith('import ') or line.startswith('from '):
                explanation += f"• Import: `{line}`\n"
            elif line.startswith('if '): explanation += "• Conditional\n"
            elif line.startswith('for ') or line.startswith('while '): explanation += "• Loop\n"
            elif line.startswith('return '): explanation += "• Return statement\n"
        
        return explanation + "\nAsk me about any part! 🐱"
    
    def _suggest_fix(self, code):
        return """🐱 Quick debugging checklist:

1. Balanced parentheses/brackets?
2. Correct indentation (4 spaces)?
3. Variables defined before use?
4. Typos in names?
5. Right data types?

Paste your error message for specific help! 🐱"""
    
    def _how_to(self, msg):
        msg = msg.lower()
        
        if 'read' in msg and 'file' in msg:
            return """🐱 Read a file:

```python
with open('file.txt', 'r') as f:
    content = f.read()
```"""
        
        if 'write' in msg and 'file' in msg:
            return """🐱 Write a file:

```python
with open('file.txt', 'w') as f:
    f.write('Hello!')
```"""
        
        if 'list' in msg:
            return """🐱 Lists:

```python
my_list = [1, 2, 3]
my_list.append(4)
my_list[0]  # First item
```"""
        
        if 'dict' in msg:
            return """🐱 Dicts:

```python
d = {'key': 'value'}
d['new'] = 'item'
d.get('key', 'default')
```"""
        
        if 'loop' in msg:
            return """🐱 Loops:

```python
for item in collection:
    print(item)

for i, item in enumerate(collection):
    print(i, item)
```"""
        
        return "🐱 What specifically would you like to know how to do?"
    
    def _generate_code(self, msg):
        msg = msg.lower()
        
        if 'hello' in msg:
            return '🐱 Here you go:\n\n```python\nprint("Hello, World!")\n```'
        
        if 'game' in msg:
            return """🐱 Simple game:

```python
import random

number = random.randint(1, 100)
while True:
    guess = int(input("Guess: "))
    if guess == number:
        print("You win! 🎉")
        break
    print("Higher!" if guess < number else "Lower!")
```"""
        
        return "🐱 Tell me more about what you want to build!"
    
    def get_status(self):
        return {'model': self.model_id, 'context': len(self.context), 'thinking': self.thinking}


# ============================================================================
# CAT CODE IDE
# ============================================================================

class CatCode:
    def __init__(self, root):
        self.root = root
        self.root.title("Cat Code")
        self.root.geometry("600x400")
        
        self.current_file = None
        self.llm = CatLLM()
        
        self.colors = {
            'bg': '#1e1e1e',
            'sidebar': '#252526',
            'sidebar_active': '#37373d',
            'titlebar': '#323233',
            'editor': '#1e1e1e',
            'text': '#d4d4d4',
            'text_dim': '#808080',
            'accent': '#007acc',
            'line_numbers': '#858585',
            'selection': '#264f78',
            'cursor': '#aeafad',
            'tab_active': '#1e1e1e',
            'tab_inactive': '#2d2d2d',
            'status_bar': '#007acc',
            'border': '#3c3c3c',
            'copilot': '#6e40c9',
        }
        
        self.root.configure(bg=self.colors['titlebar'])
        self.setup_ui()
        self.bind_events()
        
    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_titlebar()
        
        content = tk.Frame(self.main_frame, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True)
        
        self.create_activity_bar(content)
        self.create_sidebar(content)
        self.create_editor_area(content)
        self.create_status_bar()
        
    def create_titlebar(self):
        titlebar = tk.Frame(self.main_frame, bg=self.colors['titlebar'], height=28)
        titlebar.pack(fill=tk.X)
        titlebar.pack_propagate(False)
        
        title = tk.Label(titlebar, text="🐱 Cat Code", bg=self.colors['titlebar'],
                        fg=self.colors['text'], font=('Segoe UI', 9))
        title.pack(side=tk.LEFT, padx=10)
        
        for menu_name in ['File', 'Edit', 'View', 'Help']:
            btn = tk.Label(titlebar, text=menu_name, bg=self.colors['titlebar'],
                          fg=self.colors['text_dim'], font=('Segoe UI', 9), padx=8)
            btn.pack(side=tk.LEFT)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.colors['sidebar']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.colors['titlebar']))
            btn.bind('<Button-1>', lambda e, m=menu_name: self.show_menu(m))
        
        controls = tk.Frame(titlebar, bg=self.colors['titlebar'])
        controls.pack(side=tk.RIGHT)
        
        for sym, cmd in [('─', self.root.iconify), ('□', self.toggle_maximize), ('✕', self.root.quit)]:
            btn = tk.Label(controls, text=sym, bg=self.colors['titlebar'],
                          fg=self.colors['text_dim'], font=('Segoe UI', 10), width=4)
            btn.pack(side=tk.LEFT)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#c42b1c' if b.cget('text')=='✕' else self.colors['sidebar']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.colors['titlebar']))
            btn.bind('<Button-1>', lambda e, c=cmd: c())
        
        titlebar.bind('<Button-1>', self.start_drag)
        titlebar.bind('<B1-Motion>', self.on_drag)
        
    def create_activity_bar(self, parent):
        activity = tk.Frame(parent, bg=self.colors['sidebar'], width=40)
        activity.pack(side=tk.LEFT, fill=tk.Y)
        activity.pack_propagate(False)
        
        icons = [('📁', 'Explorer', self.toggle_sidebar), ('🔍', 'Search', None),
                 ('🔀', 'Git', None), ('🐛', 'Debug', None), ('🐱', 'Copilot', self.toggle_copilot)]
        
        for icon, tip, cmd in icons:
            btn = tk.Label(activity, text=icon, bg=self.colors['sidebar'],
                          fg=self.colors['text_dim'], font=('Segoe UI', 12),
                          width=3, height=2, cursor='hand2')
            btn.pack(pady=1)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(fg=self.colors['text']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(fg=self.colors['text_dim']))
            if cmd: btn.bind('<Button-1>', lambda e, c=cmd: c())
            if 'Copilot' in tip: self.copilot_btn = btn
        
        tk.Frame(activity, bg=self.colors['sidebar']).pack(fill=tk.BOTH, expand=True)
        
        settings = tk.Label(activity, text='⚙', bg=self.colors['sidebar'],
                           fg=self.colors['text_dim'], font=('Segoe UI', 12), cursor='hand2')
        settings.pack(pady=5)
        
    def create_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=150)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        header = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        header.pack(fill=tk.X, pady=5)
        
        tk.Label(header, text="EXPLORER", bg=self.colors['sidebar'],
                fg=self.colors['text_dim'], font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=10)
        
        tree = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        tree.pack(fill=tk.BOTH, expand=True, padx=5)
        
        for f in ['📄 main.py', '📄 utils.py', '📁 src', '  📄 app.py', '📄 README.md']:
            item = tk.Label(tree, text=f, bg=self.colors['sidebar'],
                           fg=self.colors['text'], font=('Consolas', 8), anchor='w', cursor='hand2')
            item.pack(fill=tk.X, pady=1)
            item.bind('<Enter>', lambda e, i=item: i.configure(bg=self.colors['sidebar_active']))
            item.bind('<Leave>', lambda e, i=item: i.configure(bg=self.colors['sidebar']))
        
    def create_editor_area(self, parent):
        editor_container = tk.Frame(parent, bg=self.colors['editor'])
        editor_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tab_bar = tk.Frame(editor_container, bg=self.colors['tab_inactive'], height=30)
        self.tab_bar.pack(fill=tk.X)
        self.tab_bar.pack_propagate(False)
        
        self.add_tab("main.py")
        
        editor_frame = tk.Frame(editor_container, bg=self.colors['editor'])
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, pady=5,
                                   bg=self.colors['editor'], fg=self.colors['line_numbers'],
                                   font=('Consolas', 9), bd=0, state='disabled', highlightthickness=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.editor = tk.Text(editor_frame, bg=self.colors['editor'], fg=self.colors['text'],
                             insertbackground=self.colors['cursor'], selectbackground=self.colors['selection'],
                             font=('Consolas', 9), bd=0, undo=True, highlightthickness=0,
                             wrap='none', padx=5, pady=5)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(editor_frame, command=self.editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=scrollbar.set)
        
        sample = '''#!/usr/bin/env python3
"""Cat Code Example"""

def hello_world():
    """Print greeting."""
    print("Hello from Cat Code! 🐱")

def main():
    hello_world()

if __name__ == "__main__":
    main()
'''
        self.editor.insert('1.0', sample)
        self.update_line_numbers()
        
        self.create_copilot_panel(editor_container)
        
    def create_copilot_panel(self, parent):
        self.copilot_panel = tk.Frame(parent, bg=self.colors['bg'], width=200)
        
        header = tk.Frame(self.copilot_panel, bg=self.colors['sidebar'], height=28)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🐱 Cat Copilot", bg=self.colors['sidebar'],
                fg=self.colors['copilot'], font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT, padx=8, pady=5)
        
        close = tk.Label(header, text="✕", bg=self.colors['sidebar'],
                        fg=self.colors['text_dim'], cursor='hand2')
        close.pack(side=tk.RIGHT, padx=8)
        close.bind('<Button-1>', lambda e: self.toggle_copilot())
        
        tk.Label(self.copilot_panel, text=f"Model: {self.llm.model_id}",
                bg=self.colors['bg'], fg=self.colors['text_dim'],
                font=('Consolas', 7)).pack(anchor='w', padx=8, pady=3)
        
        self.chat_display = tk.Text(self.copilot_panel, bg=self.colors['editor'],
                                   fg=self.colors['text'], font=('Consolas', 8),
                                   bd=0, highlightthickness=1,
                                   highlightbackground=self.colors['border'],
                                   wrap='word', state='disabled')
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        input_frame = tk.Frame(self.copilot_panel, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X, padx=8, pady=8)
        
        self.chat_input = tk.Entry(input_frame, bg=self.colors['editor'],
                                  fg=self.colors['text'], font=('Consolas', 8),
                                  bd=0, highlightthickness=1,
                                  highlightbackground=self.colors['border'],
                                  insertbackground=self.colors['cursor'])
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_input.bind('<Return>', self.send_chat)
        
        send = tk.Button(input_frame, text="➤", bg=self.colors['copilot'],
                        fg='white', font=('Segoe UI', 8), bd=0,
                        command=lambda: self.send_chat(None))
        send.pack(side=tk.RIGHT, padx=(3,0))
        
        self.add_chat_message("assistant", random.choice(self.llm.greetings))
        
    def add_tab(self, filename):
        tab = tk.Frame(self.tab_bar, bg=self.colors['tab_active'])
        tab.pack(side=tk.LEFT, padx=(0,1))
        
        icon = "🐍" if filename.endswith('.py') else "📄"
        tk.Label(tab, text=icon, bg=self.colors['tab_active'],
                font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=(6,2), pady=6)
        
        tk.Label(tab, text=filename, bg=self.colors['tab_active'],
                fg=self.colors['text'], font=('Segoe UI', 8)).pack(side=tk.LEFT, pady=6)
        
        close = tk.Label(tab, text="×", bg=self.colors['tab_active'],
                        fg=self.colors['text_dim'], font=('Segoe UI', 8), cursor='hand2')
        close.pack(side=tk.LEFT, padx=(4,6), pady=6)
        
    def create_status_bar(self):
        status = tk.Frame(self.main_frame, bg=self.colors['status_bar'], height=20)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)
        
        tk.Label(status, text="🔀 main", bg=self.colors['status_bar'],
                fg='white', font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=8)
        
        for item in ['Ln 1, Col 1', 'Spaces: 4', 'UTF-8', 'Python', '🐱']:
            tk.Label(status, text=item, bg=self.colors['status_bar'],
                    fg='white', font=('Segoe UI', 7)).pack(side=tk.RIGHT, padx=6)
    
    def bind_events(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-space>', lambda e: self.trigger_completion())
        self.root.bind('<Control-Shift-p>', lambda e: self.command_palette())
        
        self.editor.bind('<KeyRelease>', self.on_key_release)
        self.editor.bind('<Tab>', self.handle_tab)
        
    def on_key_release(self, e):
        self.update_line_numbers()
        if e.char and (e.char.isalnum() or e.char in '._'):
            self.root.after(80, self.check_completion)
    
    def check_completion(self):
        pos = self.editor.index(tk.INSERT)
        line_num = int(pos.split('.')[0])
        line = self.editor.get(f"{line_num}.0", f"{line_num}.end")
        code = self.editor.get("1.0", tk.END)
        
        suggestions = self.llm.complete(code, line, pos)
        if suggestions:
            self.show_completion_popup(suggestions)
    
    def show_completion_popup(self, suggestions):
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg=self.colors['sidebar'])
        
        bbox = self.editor.bbox(tk.INSERT)
        if bbox:
            x = self.editor.winfo_rootx() + bbox[0]
            y = self.editor.winfo_rooty() + bbox[1] + 18
            popup.geometry(f"+{x}+{y}")
        
        for sugg in suggestions[:6]:
            item = tk.Label(popup, text=f"  {sugg[:40]}", bg=self.colors['sidebar'],
                           fg=self.colors['text'], font=('Consolas', 8),
                           anchor='w', padx=4, pady=2)
            item.pack(fill=tk.X)
            item.bind('<Enter>', lambda e, l=item: l.configure(bg=self.colors['selection']))
            item.bind('<Leave>', lambda e, l=item: l.configure(bg=self.colors['sidebar']))
            item.bind('<Button-1>', lambda e, s=sugg, p=popup: self.insert_completion(s, p))
        
        popup.bind('<FocusOut>', lambda e: popup.destroy())
        self.root.after(2500, lambda: popup.destroy() if popup.winfo_exists() else None)
        
    def insert_completion(self, text, popup):
        self.editor.insert(tk.INSERT, text)
        popup.destroy()
        
    def handle_tab(self, e):
        self.editor.insert(tk.INSERT, "    ")
        return 'break'
        
    def update_line_numbers(self):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        count = int(self.editor.index('end').split('.')[0])
        self.line_numbers.insert('1.0', '\n'.join(str(i) for i in range(1, count)))
        self.line_numbers.config(state='disabled')
    
    def toggle_copilot(self):
        if self.copilot_panel.winfo_ismapped():
            self.copilot_panel.pack_forget()
            self.copilot_btn.configure(fg=self.colors['text_dim'])
        else:
            self.copilot_panel.pack(side=tk.RIGHT, fill=tk.Y)
            self.copilot_btn.configure(fg=self.colors['copilot'])
            self.chat_input.focus_set()
    
    def send_chat(self, e):
        msg = self.chat_input.get().strip()
        if not msg: return
        
        self.chat_input.delete(0, tk.END)
        self.add_chat_message("user", msg)
        
        code = self.editor.get("1.0", tk.END)
        
        def respond():
            resp = self.llm.chat(msg, code)
            self.root.after(0, lambda: self.add_chat_message("assistant", resp))
        
        threading.Thread(target=respond, daemon=True).start()
    
    def add_chat_message(self, role, content):
        self.chat_display.config(state='normal')
        prefix = "👤 You:" if role == "user" else "🐱 Copilot:"
        self.chat_display.insert(tk.END, f"\n{prefix}\n{content}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def start_drag(self, e):
        self._dx, self._dy = e.x, e.y
        
    def on_drag(self, e):
        x = self.root.winfo_x() + (e.x - self._dx)
        y = self.root.winfo_y() + (e.y - self._dy)
        self.root.geometry(f"+{x}+{y}")
    
    def toggle_maximize(self):
        geo = self.root.geometry().split('+')[0]
        self.root.geometry("1000x700" if geo == "600x400" else "600x400")
    
    def toggle_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, before=self.editor.master.master)
    
    def show_menu(self, name):
        if name == 'File':
            menu = tk.Menu(self.root, tearoff=0, bg=self.colors['sidebar'], fg=self.colors['text'])
            menu.add_command(label="New File       Ctrl+N", command=self.new_file)
            menu.add_command(label="Open File      Ctrl+O", command=self.open_file)
            menu.add_command(label="Save           Ctrl+S", command=self.save_file)
            menu.add_separator()
            menu.add_command(label="Exit", command=self.root.quit)
            menu.post(self.root.winfo_x() + 60, self.root.winfo_y() + 50)
    
    def command_palette(self):
        pal = tk.Toplevel(self.root)
        pal.overrideredirect(True)
        pal.geometry(f"300x30+{self.root.winfo_x()+150}+{self.root.winfo_y()+60}")
        pal.configure(bg=self.colors['sidebar'])
        
        entry = tk.Entry(pal, bg=self.colors['editor'], fg=self.colors['text'],
                        font=('Consolas', 10), bd=0, highlightthickness=1,
                        highlightbackground=self.colors['accent'])
        entry.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        entry.insert(0, "> ")
        entry.focus_set()
        entry.bind('<Escape>', lambda e: pal.destroy())
        entry.bind('<Return>', lambda e: pal.destroy())
    
    def trigger_completion(self):
        self.check_completion()
        
    def new_file(self):
        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.update_line_numbers()
        
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Python", "*.py"), ("All", "*.*")])
        if path:
            try:
                with open(path, 'r') as f:
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert("1.0", f.read())
                self.current_file = path
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w') as f:
                    f.write(self.editor.get("1.0", tk.END))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            path = filedialog.asksaveasfilename(defaultextension=".py")
            if path:
                self.current_file = path
                self.save_file()


def main():
    root = tk.Tk()
    app = CatCode(root)
    root.mainloop()

if __name__ == "__main__":
    main()
