import tkinter as tk
from tkinter import ttk
import re

class EditorTab(ttk.Frame):
    def __init__(self, notebook, file_path=None):
        super().__init__(notebook)
        self.file_path = file_path
        self.has_changes = False
        
        self.line_numbers = tk.Text(self, width=4, padx=4, takefocus=0, border=0,
                                    state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.text_area = tk.Text(self, undo=True, wrap='none', border=0)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scrollbar)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("string", foreground="green")
        self.text_area.tag_configure("comment", foreground="gray")
        self.text_area.tag_configure("current_line", background="#e8f2fe")

        # Sledovani zmen pres udalost <<Modified>>
        self.text_area.bind('<<Modified>>', self.on_text_modified)
        
        self.text_area.bind('<Any-KeyPress>', self.on_content_change)
        self.text_area.bind('<Button-1>', self.on_content_change)
        self.text_area.bind('<MouseWheel>', self.on_content_change)

    def on_text_modified(self, event=None):
        if self.text_area.edit_modified():
            if not self.has_changes:
                self.has_changes = True
                # Prida hvezdicku do nazvu zalozky, aby uzivatel videl zmenu
                current_text = self.master.tab(self, "text")
                if not current_text.startswith("*"):
                    self.master.tab(self, text="*" + current_text)
            self.text_area.edit_modified(False)

    def apply_theme(self, is_dark):
        if is_dark:
            dark_bg = "#1e1e1e"
            dark_fg = "#d4d4d4"
            line_bg = "#252526"
            
            self.text_area.config(bg=dark_bg, fg=dark_fg, insertbackground="white")
            self.line_numbers.config(bg=line_bg, fg="#858585")
            self.text_area.tag_configure("keyword", foreground="#569cd6")
            self.text_area.tag_configure("string", foreground="#ce9178")
            self.text_area.tag_configure("comment", foreground="#6a9955")
            self.text_area.tag_configure("current_line", background="#2a2d2e")
        else:
            self.text_area.config(bg="white", fg="black", insertbackground="black")
            self.line_numbers.config(bg="#f0f0f0", fg="black")
            self.text_area.tag_configure("keyword", foreground="blue")
            self.text_area.tag_configure("string", foreground="green")
            self.text_area.tag_configure("comment", foreground="gray")
            self.text_area.tag_configure("current_line", background="#e8f2fe")
        
        self.highlight_syntax()

    def _on_scrollbar(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def on_content_change(self, event=None):
        self.after(10, self.update_line_numbers)
        self.after(10, self.highlight_current_line)
        self.after(10, self.highlight_syntax)

    def update_line_numbers(self):
        lines = self.text_area.get('1.0', tk.END).count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def highlight_current_line(self):
        self.text_area.tag_remove("current_line", "1.0", tk.END)
        self.text_area.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def highlight_syntax(self):
        for tag in ["keyword", "string", "comment"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)
        text_content = self.text_area.get("1.0", tk.END)
        keywords = [r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\bdef\b', r'\bclass\b', r'\breturn\b']
        for kw in keywords:
            for match in re.finditer(kw, text_content):
                self.text_area.tag_add("keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r'[\'"].*?[\'"]', text_content):
            self.text_area.tag_add("string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r'#.*', text_content):
            self.text_area.tag_add("comment", f"1.0+{match.start()}c", f"1.0+{match.end()}c")