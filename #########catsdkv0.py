#!/usr/bin/env python3
# Cat's Edit 0.1 - Zed UI Clone
# Core program.py

import tkinter as tk
from tkinter import ttk, font, messagebox
import os
import sys
from pathlib import Path

class CatsEdit:
    def __init__(self, root):
        self.root = root
        self.root.title("Cat's Edit 0.1")
        self.root.geometry("1200x800")
        
        # Remove default title bar
        self.root.overrideredirect(True)
        
        # Variables
        self.current_file = None
        self.zoom_level = 1.0
        self.dark_mode = True
        
        self.setup_styles()
        self.create_custom_titlebar()
        self.create_menu()
        self.create_main_interface()
        self.bind_shortcuts()
        
        # Center window
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'sidebar': '#151515',
            'titlebar': '#0d0d0d',
            'accent': '#ff6b35',
            'selection': '#264f78',
            'text': '#e6e6e6'
        }
        
    def create_custom_titlebar(self):
        # Title bar frame
        self.titlebar = tk.Frame(self.root, bg=self.colors['titlebar'], height=30)
        self.titlebar.pack(fill=tk.X)
        self.titlebar.pack_propagate(False)
        
        # Drag functionality
        self.titlebar.bind('<Button-1>', self.start_move)
        self.titlebar.bind('<B1-Motion>', self.on_move)
        
        # Title
        title_label = tk.Label(self.titlebar, text="Cat's Edit 0.1", 
                              bg=self.colors['titlebar'], fg=self.colors['text'],
                              font=('Segoe UI', 10))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Window controls
        controls_frame = tk.Frame(self.titlebar, bg=self.colors['titlebar'])
        controls_frame.pack(side=tk.RIGHT)
        
        # Minimize button
        min_btn = tk.Button(controls_frame, text='─', bg=self.colors['titlebar'], 
                           fg=self.colors['text'], bd=0, padx=10,
                           command=self.root.iconify)
        min_btn.pack(side=tk.LEFT)
        
        # Close button
        close_btn = tk.Button(controls_frame, text='✕', bg=self.colors['titlebar'],
                            fg=self.colors['text'], bd=0, padx=10,
                            command=self.root.destroy)
        close_btn.pack(side=tk.LEFT)
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def create_menu(self):
        # Menu bar
        menubar = tk.Menu(self.root, bg=self.colors['bg'], fg=self.colors['text'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl+=")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Sidebar", command=self.toggle_sidebar)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        
    def create_main_interface(self):
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = tk.Frame(main_container, width=200, bg=self.colors['sidebar'])
        main_container.add(self.sidebar)
        
        # Sidebar content
        sidebar_label = tk.Label(self.sidebar, text="EXPLORER", bg=self.colors['sidebar'],
                                fg="#888888", font=('Segoe UI', 9, 'bold'))
        sidebar_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # File tree (simplified)
        self.file_tree = ttk.Treeview(self.sidebar, style="Custom.Treeview")
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Editor area
        editor_frame = tk.Frame(main_container, bg=self.colors['bg'])
        main_container.add(editor_frame)
        
        # Tab bar
        self.tab_frame = tk.Frame(editor_frame, bg=self.colors['sidebar'], height=35)
        self.tab_frame.pack(fill=tk.X)
        self.tab_frame.pack_propagate(False)
        
        # Tabs container
        self.tabs_container = tk.Frame(self.tab_frame, bg=self.colors['sidebar'])
        self.tabs_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add tab button
        add_tab_btn = tk.Button(self.tab_frame, text="+", bg=self.colors['sidebar'],
                               fg=self.colors['text'], bd=0, width=3,
                               command=self.add_tab)
        add_tab_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text editor with scrollbars
        text_frame = tk.Frame(editor_frame, bg=self.colors['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, padx=5, pady=5,
                                   bg=self.colors['sidebar'], fg="#888888",
                                   state='disabled', bd=0, font=('Consolas', 11))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(text_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(editor_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(fill=tk.X)
        
        # Main text widget
        self.text_area = tk.Text(text_frame, wrap=tk.NONE, bg=self.colors['bg'],
                                fg=self.colors['text'], insertbackground=self.colors['text'],
                                selectbackground=self.colors['selection'],
                                bd=0, font=('Consolas', 11), undo=True,
                                yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.text_area.yview)
        h_scrollbar.config(command=self.text_area.xview)
        
        # Status bar
        self.status_bar = tk.Frame(editor_frame, height=25, bg=self.colors['sidebar'])
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        # Status items
        status_left = tk.Label(self.status_bar, text="Ln 1, Col 1",
                              bg=self.colors['sidebar'], fg="#888888")
        status_left.pack(side=tk.LEFT, padx=10)
        
        status_right = tk.Label(self.status_bar, text="UTF-8 • CRLF • Python",
                              bg=self.colors['sidebar'], fg="#888888")
        status_right.pack(side=tk.RIGHT, padx=10)
        
        # Add initial tab
        self.add_tab()
        
    def add_tab(self):
        tab = tk.Frame(self.tabs_container, bg=self.colors['sidebar'])
        tab.pack(side=tk.LEFT, padx=(5,0), pady=5)
        
        tab_label = tk.Label(tab, text="untitled", bg=self.colors['sidebar'],
                            fg=self.colors['text'], padx=10)
        tab_label.pack(side=tk.LEFT)
        
        close_btn = tk.Button(tab, text="×", bg=self.colors['sidebar'],
                            fg="#888888", bd=0, width=2,
                            command=lambda: self.close_tab(tab))
        close_btn.pack(side=tk.LEFT)
        
        # Highlight active tab
        for widget in self.tabs_container.winfo_children():
            widget.config(bg=self.colors['sidebar'])
        tab.config(bg=self.colors['bg'])
        
    def close_tab(self, tab):
        tab.destroy()
        
    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.update_title()
        
    def open_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.current_file = file_path
                    self.update_title()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
                
    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".py")
        if file_path:
            self.current_file = file_path
            self.save_file()
            self.update_title()
            
    def update_title(self):
        title = "Cat's Edit 0.1"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        for widget in self.titlebar.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(text=title)
                
    def undo(self):
        try:
            self.text_area.edit_undo()
        except:
            pass
            
    def redo(self):
        try:
            self.text_area.edit_redo()
        except:
            pass
            
    def cut(self):
        self.text_area.event_generate("<<Cut>>")
        
    def copy(self):
        self.text_area.event_generate("<<Copy>>")
        
    def paste(self):
        self.text_area.event_generate("<<Paste>>")
        
    def zoom_in(self):
        current_size = self.text_area['font'].split()[1]
        new_size = int(current_size) + 1
        self.text_area.config(font=('Consolas', new_size))
        
    def zoom_out(self):
        current_size = self.text_area['font'].split()[1]
        if int(current_size) > 6:
            new_size = int(current_size) - 1
            self.text_area.config(font=('Consolas', new_size))
            
    def reset_zoom(self):
        self.text_area.config(font=('Consolas', 11))
        
    def toggle_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.colors = {
                'bg': '#1a1a1a',
                'fg': '#ffffff',
                'sidebar': '#151515',
                'titlebar': '#0d0d0d',
                'accent': '#ff6b35',
                'selection': '#264f78',
                'text': '#e6e6e6'
            }
        else:
            self.colors = {
                'bg': '#ffffff',
                'fg': '#000000',
                'sidebar': '#f5f5f5',
                'titlebar': '#e0e0e0',
                'accent': '#007acc',
                'selection': '#add6ff',
                'text': '#333333'
            }
        self.apply_colors()
        
    def apply_colors(self):
        self.titlebar.config(bg=self.colors['titlebar'])
        self.text_area.config(bg=self.colors['bg'], fg=self.colors['text'],
                            insertbackground=self.colors['text'],
                            selectbackground=self.colors['selection'])
        self.sidebar.config(bg=self.colors['sidebar'])
        self.status_bar.config(bg=self.colors['sidebar'])

def main():
    root = tk.Tk()
    app = CatsEdit(root)
    root.mainloop()

if __name__ == "__main__":
    main()
