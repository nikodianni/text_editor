"""modul pro naseptavac (autocomplete)."""

import tkinter as tk
import re
from typing import Callable

class AutocompleteManager:
    def __init__(self, text_area: tk.Text, on_insert_callback: Callable) -> None:
        self.text_area = text_area
        self.on_insert_callback = on_insert_callback
        self.window = None
        self.listbox = None
        self.is_dark = False

    def show(self) -> None:
        """zobrazi okno naseptavace."""
        line_start = self.text_area.get("insert linestart", "insert")
        match = re.search(r'[a-zA-Z_]\w*$', line_start)
        
        if not match:
            self.hide()
            return
            
        prefix = match.group()
        if len(prefix) < 2:
            self.hide()
            return
            
        text = self.text_area.get("1.0", tk.END)
        words = set(re.findall(r'\b[a-zA-Z_]\w*\b', text))
        matches = sorted([w for w in words if w.startswith(prefix) and w != prefix])
        
        python_keywords = ["print", "import", "def", "class", "return", "True", "False", "None", "if", "elif", "else", "while", "for"]
        for kw in python_keywords:
            if kw.startswith(prefix) and kw != prefix and kw not in matches:
                matches.append(kw)
        
        matches = sorted(list(set(matches)))

        if not matches:
            self.hide()
            return
            
        if not self.window:
            self.window = tk.Toplevel(self.text_area)
            self.window.wm_overrideredirect(True)
            self.listbox = tk.Listbox(self.window, font=("Consolas", 10), height=5)
            self.listbox.pack()
            self.listbox.bind("<Double-Button-1>", lambda e: self.insert_word())
            self.apply_theme(self.is_dark)

        self.listbox.delete(0, tk.END)
        for m in matches:
            self.listbox.insert(tk.END, m)
        self.listbox.selection_set(0)
        
        bbox = self.text_area.bbox("insert")
        if bbox:
            x, y, _, h = bbox
            rx = self.text_area.winfo_rootx() + x
            ry = self.text_area.winfo_rooty() + y + h
            self.window.geometry(f"+{rx}+{ry}")
            self.window.deiconify()

    def hide(self) -> None:
        """skryje okno naseptavace."""
        if self.window:
            self.window.withdraw()

    def insert_word(self) -> None:
        """vlozi vybrane slovo do editoru."""
        if not self.window or not self.window.winfo_viewable():
            return
            
        sel = self.listbox.curselection()
        if not sel: return
        
        word = self.listbox.get(sel[0])
        line_start = self.text_area.get("insert linestart", "insert")
        match = re.search(r'[a-zA-Z_]\w*$', line_start)
        
        if match:
            prefix_len = len(match.group())
            self.text_area.delete(f"insert-{prefix_len}c", "insert")
            self.text_area.insert("insert", word)
            self.hide()
            self.on_insert_callback()

    def apply_theme(self, is_dark: bool) -> None:
        """nastavi barvy naseptavace."""
        self.is_dark = is_dark
        if not self.window: return
        
        if is_dark:
            self.listbox.config(bg="#252526", fg="#d4d4d4", selectbackground="#37373d", selectforeground="white")
        else:
            self.listbox.config(bg="white", fg="black", selectbackground="#0078d7", selectforeground="white")

    def handle_up_down(self, event: tk.Event) -> str | None:
        """pohyb sipkami v naseptavaci."""
        if self.window and self.window.winfo_viewable():
            sel = self.listbox.curselection()
            if sel:
                idx = sel[0]
                if event.keysym == "Up" and idx > 0:
                    self.listbox.selection_clear(idx)
                    self.listbox.selection_set(idx - 1)
                    self.listbox.see(idx - 1)
                elif event.keysym == "Down" and idx < self.listbox.size() - 1:
                    self.listbox.selection_clear(idx)
                    self.listbox.selection_set(idx + 1)
                    self.listbox.see(idx + 1)
            return "break"
        return None