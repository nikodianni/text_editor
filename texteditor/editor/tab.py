"""trida pro zalozku editoru."""

import tkinter as tk
from tkinter import ttk
import re

class EditorTab(ttk.Frame):
    def __init__(self, notebook: ttk.Notebook, status_var: tk.StringVar, file_path: str | None = None) -> None:
        super().__init__(notebook)
        self.status_var: tk.StringVar = status_var
        self.file_path: str | None = file_path
        self.has_changes: bool = False
        
        # panel pro cisla radku
        self.line_numbers: tk.Text = tk.Text(self, width=4, padx=4, takefocus=0, border=0,
                                             state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # hlavni text. oblast
        self.text_area: tk.Text = tk.Text(self, undo=True, wrap='none', border=0)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # scrollbar
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scrollbar)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        
        # znacky pro syntax a vyhledavani
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("string", foreground="green")
        self.text_area.tag_configure("comment", foreground="gray")
        self.text_area.tag_configure("current_line", background="#e8f2fe")
        self.text_area.tag_configure("search_match", background="yellow", foreground="black")

        # vytvoreni kontextoveho menu
        self._create_context_menu()

        # sledovani zmen a pozice kurzoru
        self.text_area.bind('<<Modified>>', self.on_text_modified)
        self.text_area.bind('<KeyRelease>', self.update_cursor_status)
        self.text_area.bind('<ButtonRelease-1>', self.update_cursor_status)
        
        # akce pro klavesnici a mys
        self.text_area.bind('<Any-KeyPress>', self.on_content_change)
        self.text_area.bind('<Button-1>', self.on_content_change)
        self.text_area.bind('<MouseWheel>', self.on_content_change)
        
        # bindovani praveho tlacitka mysi
        self.text_area.bind('<Button-3>', self._show_context_menu)

        # chytre funkce pro kod
        self.text_area.bind('<Key>', self._on_key_type)
        self.text_area.bind('<Return>', self._on_return_key)

    def _create_context_menu(self) -> None:
        """vytvori vyskakovaci menu pro prave tlacitko."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Kopírovat", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Vyjmout", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Vložit", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Vybrat vše", command=self._select_all)

    def _show_context_menu(self, event: tk.Event) -> None:
        """zobrazi menu na pozici kurzoru mysi."""
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _select_all(self) -> str:
        """vybere veskery text v editoru."""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return 'break'

    def update_cursor_status(self, event: tk.Event | None = None) -> None:
        """aktualizuje pozici kurzoru ve stavovem radku."""
        pos = self.text_area.index(tk.INSERT)
        radek, sloupec = pos.split('.')
        self.status_var.set(f"radek: {radek}, sloupec: {sloupec}")

    def _on_key_type(self, event: tk.Event) -> str | None:
        """doplnovani a preskakovani znaku."""
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        closers = (")", "]", "}", '"', "'")
        
        # preskoc uzaviraci znak
        if event.char in closers:
            next_char = self.text_area.get("insert", "insert+1c")
            if next_char == event.char:
                self.text_area.mark_set("insert", "insert+1c")
                return "break"
        
        # vloz par a posun kurzor
        if event.char in pairs:
            opened = event.char
            closed = pairs[opened]
            self.text_area.insert("insert", opened + closed)
            self.text_area.mark_set("insert", "insert-1c")
            self.on_content_change()
            return "break"
        
        return None

    def _on_return_key(self, event: tk.Event) -> str:
        """auto-odsazovani."""
        current_line = self.text_area.get("insert linestart", "insert")
        match = re.match(r'^(\s*)', current_line)
        current_indent = match.group(1) if match else ""
        
        if current_line.rstrip().endswith(":"):
            extra_indent = "    "
        else:
            extra_indent = ""
            
        self.text_area.insert("insert", "\n" + current_indent + extra_indent)
        self.on_content_change()
        return "break"

    def on_text_modified(self, event: tk.Event | None = None) -> None:
        """oznaci zalozku za zmenenou."""
        if self.text_area.edit_modified():
            if not self.has_changes:
                self.has_changes = True
                current_text = self.master.tab(self, "text")
                if not current_text.startswith("*"):
                    self.master.tab(self, text="*" + current_text)
            self.text_area.edit_modified(False)

    def apply_theme(self, is_dark: bool) -> None:
        """nastavi barevne schema."""
        if is_dark:
            self.text_area.config(bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
            self.line_numbers.config(bg="#252526", fg="#858585")
            self.text_area.tag_configure("keyword", foreground="#569cd6")
            self.text_area.tag_configure("string", foreground="#ce9178")
            self.text_area.tag_configure("comment", foreground="#6a9955")
            self.text_area.tag_configure("current_line", background="#2a2d2e")
            
            # tmave tema pro kontextove menu
            self.context_menu.config(bg="#252526", fg="#ffffff", activebackground="#37373d", activeforeground="#ffffff")
        else:
            self.text_area.config(bg="white", fg="black", insertbackground="black")
            self.line_numbers.config(bg="#f0f0f0", fg="black")
            self.text_area.tag_configure("keyword", foreground="blue")
            self.text_area.tag_configure("string", foreground="green")
            self.text_area.tag_configure("comment", foreground="gray")
            self.text_area.tag_configure("current_line", background="#e8f2fe")
            
            # svetle tema pro kontextove menu
            self.context_menu.config(bg="white", fg="black", activebackground="#0078d7", activeforeground="white")
        
        self.highlight_syntax()

    def _on_scrollbar(self, *args) -> None:
        """synchro posuvniku."""
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def on_content_change(self, event: tk.Event | None = None) -> None:
        """spusti prepocet a zvyrazneni."""
        self.after(10, self.update_line_numbers)
        self.after(10, self.highlight_current_line)
        self.after(10, self.highlight_syntax)
        self.after(10, self.update_cursor_status)

    def update_line_numbers(self) -> None:
        """prepocet cisel radku."""
        lines = self.text_area.get('1.0', tk.END).count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def highlight_current_line(self) -> None:
        """zvyrazni aktualni radek."""
        self.text_area.tag_remove("current_line", "1.0", tk.END)
        self.text_area.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def highlight_syntax(self) -> None:
        """obarvi syntax pomoci regexu."""
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