"""trida pro zalozku editoru."""

import tkinter as tk
from tkinter import ttk
import re
from .syntax import SyntaxHighlighter
from .autocomplete import AutocompleteManager

class EditorTab(ttk.Frame):
    def __init__(self, notebook: ttk.Notebook, status_var: tk.StringVar, file_path: str | None = None) -> None:
        super().__init__(notebook)
        self.status_var: tk.StringVar = status_var
        self.file_path: str | None = file_path
        self.has_changes: bool = False
        
        # panel pro cisla radku
        self.line_numbers: tk.Text = tk.Text(self, width=4, padx=4, takefocus=0, border=0, state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # hlavni text. oblast
        self.text_area: tk.Text = tk.Text(self, undo=True, wrap='none', border=0)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # scrollbar
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scrollbar)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # inicializace pomocniku (syntax a naseptavac)
        self.highlighter = SyntaxHighlighter(self.text_area)
        self.autocomplete = AutocompleteManager(self.text_area, self.on_content_change)

        self._create_context_menu()
        self._bind_events()

    def _bind_events(self) -> None:
        """napojeni klaves a mysi."""
        self.text_area.bind('<<Modified>>', self.on_text_modified)
        self.text_area.bind('<KeyRelease>', self._on_key_release)
        self.text_area.bind('<ButtonRelease-1>', self.update_cursor_status)
        self.text_area.bind('<Any-KeyPress>', self.on_content_change)
        self.text_area.bind('<Button-1>', self.on_content_change)
        self.text_area.bind('<MouseWheel>', self.on_content_change)
        self.text_area.bind('<Button-3>', self._show_context_menu)
        
        # specialni klavesy
        self.text_area.bind('<Key>', self._on_key_type)
        self.text_area.bind('<Return>', self._on_return_key)
        self.text_area.bind('<Up>', self.autocomplete.handle_up_down)
        self.text_area.bind('<Down>', self.autocomplete.handle_up_down)
        
        self.text_area.bind('<Tab>', lambda e: "break" if self.autocomplete.window and self.autocomplete.window.winfo_viewable() and not self.autocomplete.insert_word() else None)
        self.text_area.bind('<Escape>', lambda e: "break" if self.autocomplete.window and self.autocomplete.window.winfo_viewable() and not self.autocomplete.hide() else None)

    def _create_context_menu(self) -> None:
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Kopírovat", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Vyjmout", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Vložit", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Vybrat vše", command=lambda: (self.text_area.tag_add(tk.SEL, "1.0", tk.END), "break"))

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def update_cursor_status(self, event: tk.Event | None = None) -> None:
        pos = self.text_area.index(tk.INSERT)
        radek, sloupec = pos.split('.')
        self.status_var.set(f"radek: {radek}, sloupec: {sloupec}")
        self.highlighter.highlight_brackets()

    def _on_key_release(self, event: tk.Event) -> None:
        self.update_cursor_status()
        if event.keysym not in ("Up", "Down", "Return", "Tab", "Escape", "Left", "Right"):
            self.autocomplete.show()

    def _on_key_type(self, event: tk.Event) -> str | None:
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        closers = (")", "]", "}", '"', "'")
        if event.char in closers and self.text_area.get("insert", "insert+1c") == event.char:
            self.text_area.mark_set("insert", "insert+1c")
            return "break"
        if event.char in pairs:
            self.text_area.insert("insert", event.char + pairs[event.char])
            self.text_area.mark_set("insert", "insert-1c")
            self.on_content_change()
            return "break"
        return None

    def _on_return_key(self, event: tk.Event) -> str | None:
        if self.autocomplete.window and self.autocomplete.window.winfo_viewable():
            self.autocomplete.insert_word()
            return "break"
        current_line = self.text_area.get("insert linestart", "insert")
        match = re.match(r'^(\s*)', current_line)
        current_indent = match.group(1) if match else ""
        extra_indent = "    " if current_line.rstrip().endswith(":") else ""
        self.text_area.insert("insert", "\n" + current_indent + extra_indent)
        self.on_content_change()
        return "break"

    def on_text_modified(self, event: tk.Event | None = None) -> None:
        if self.text_area.edit_modified():
            if not self.has_changes:
                self.has_changes = True
                current_text = self.master.tab(self, "text")
                if not current_text.startswith("*"):
                    self.master.tab(self, text="*" + current_text)
            self.text_area.edit_modified(False)

    def apply_theme(self, is_dark: bool) -> None:
        if is_dark:
            self.text_area.config(bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
            self.line_numbers.config(bg="#252526", fg="#858585")
            self.context_menu.config(bg="#252526", fg="#ffffff", activebackground="#37373d", activeforeground="#ffffff")
        else:
            self.text_area.config(bg="white", fg="black", insertbackground="black")
            self.line_numbers.config(bg="#f0f0f0", fg="black")
            self.context_menu.config(bg="white", fg="black", activebackground="#0078d7", activeforeground="white")
            
        self.highlighter.apply_theme(is_dark)
        self.autocomplete.apply_theme(is_dark)
        self.highlighter.highlight_all()

    def _on_scrollbar(self, *args) -> None:
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def on_content_change(self, event: tk.Event | None = None) -> None:
        self.after(10, self.update_line_numbers)
        self.after(10, self.highlighter.highlight_all)
        self.after(10, self.update_cursor_status)

    def update_line_numbers(self) -> None:
        lines = self.text_area.get('1.0', tk.END).count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text_area.yview()[0])