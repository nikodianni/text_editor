"""hlavni okno aplikace editoru."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from .tab import EditorTab

class EditorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Můj Python Editor")
        self.geometry("900x700")
        
        self.is_dark_mode: bool = False
        self.style: ttk.Style = ttk.Style()
        
        # stavovy radek na spodku okna
        self.status_var: tk.StringVar = tk.StringVar(value="radek: 1, sloupec: 0")
        self.status_bar: ttk.Label = ttk.Label(self, textvariable=self.status_var, anchor=tk.E)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=2)
        
        # rozdeleni okna
        self.paned_window: ttk.PanedWindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # bocni panel
        self.tree: ttk.Treeview = ttk.Treeview(self.paned_window, show="tree")
        self.paned_window.add(self.tree, weight=0)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        
        # zalozky
        self.notebook: ttk.Notebook = ttk.Notebook(self.paned_window)
        self.paned_window.add(self.notebook, weight=1)
        self.notebook.bind('<<NotebookTabChanged>>', self.update_status_on_tab_change)
        
        # panel vyhledavani (skryty po spusteni)
        self.search_frame: ttk.Frame = ttk.Frame(self)
        self.search_var: tk.StringVar = tk.StringVar()
        self.search_var.trace_add("write", self.perform_search)
        
        ttk.Label(self.search_frame, text="Hledat:").pack(side=tk.LEFT, padx=5, pady=5)
        self.search_entry: ttk.Entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_entry.bind("<Escape>", self.hide_search_bar)
        
        ttk.Button(self.search_frame, text="Zavřít", command=self.hide_search_bar).pack(side=tk.LEFT, padx=5, pady=5)

        self.create_menu()
        self.add_new_tab()
        self.apply_global_theme()
        
        # nacteni aktualni slozky do panelu
        self.current_dir = os.getcwd()
        self.load_directory(self.current_dir, "")

        # odchyceni zavreni okna
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def update_status_on_tab_change(self, event: tk.Event) -> None:
        """obnovi stavovy radek pri prepnuti zalozky."""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.update_cursor_status()

    def show_search_bar(self, event: tk.Event | None = None) -> None:
        """zobrazi panel vyhledavani."""
        self.search_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.search_entry.focus_set()
        self.perform_search()

    def hide_search_bar(self, event: tk.Event | None = None) -> None:
        """skryje panel vyhledavani a smaze podbarveni."""
        self.search_frame.pack_forget()
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.text_area.tag_remove("search_match", "1.0", tk.END)
            current_tab.text_area.focus_set()

    def perform_search(self, *args) -> None:
        """vyhleda text a podbarvi vysledky."""
        current_tab = self.get_current_tab()
        if not current_tab: return
        
        # smazani starych vysledku
        current_tab.text_area.tag_remove("search_match", "1.0", tk.END)
        
        query = self.search_var.get()
        if not query: return
        
        start_pos = "1.0"
        while True:
            start_pos = current_tab.text_area.search(query, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos: break
            end_pos = f"{start_pos}+{len(query)}c"
            current_tab.text_area.tag_add("search_match", start_pos, end_pos)
            start_pos = end_pos

    def load_directory(self, path: str, parent: str) -> None:
        """nacte obsah slozky."""
        try:
            items = os.listdir(path)
            dirs = sorted([d for d in items if os.path.isdir(os.path.join(path, d))])
            files = sorted([f for f in items if os.path.isfile(os.path.join(path, f))])
            
            for d in dirs:
                if d.startswith('.'): continue
                full_path = os.path.join(path, d)
                node = self.tree.insert(parent, tk.END, text="[Složka] " + d, values=(full_path, "dir"))
                self.tree.insert(node, tk.END)
                
            for f in files:
                full_path = os.path.join(path, f)
                self.tree.insert(parent, tk.END, text="[Soubor] " + f, values=(full_path, "file"))
        except Exception:
            pass

    def on_tree_open(self, event: tk.Event) -> None:
        """rozbali slozku."""
        node = self.tree.focus()
        values = self.tree.item(node, "values")
        if values and values[1] == "dir":
            self.tree.delete(*self.tree.get_children(node))
            self.load_directory(values[0], node)

    def on_tree_double_click(self, event: tk.Event) -> None:
        """otevre soubor."""
        vyber = self.tree.selection()
        if not vyber: return
        
        item_id = vyber[0]
        values = self.tree.item(item_id, "values")
        if not values or values[1] != "file": return
        
        file_path = values[0]
        
        for tab in self.get_all_tabs():
            if tab.file_path == file_path:
                self.notebook.select(tab)
                return
                
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.add_new_tab(file_path, file.read())
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    def create_menu(self) -> None:
        """tvori horni menu."""
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Soubor", menu=file_menu)
        file_menu.add_command(label="Nový", command=self.add_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Otevřít...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Uložit", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Ukončit", command=self.on_exit)

        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Úpravy", menu=edit_menu)
        edit_menu.add_command(label="Hledat...", command=self.show_search_bar, accelerator="Ctrl+F")
        edit_menu.add_command(label="Nahradit vše...", command=self.replace_all, accelerator="Ctrl+H")
        
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Zobrazení", menu=view_menu)
        view_menu.add_command(label="Přepnout tmavý režim", command=self.toggle_theme, accelerator="Ctrl+D")

        self.bind("<Control-n>", lambda e: self.add_new_tab())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-f>", self.show_search_bar)
        self.bind("<Control-h>", lambda e: self.replace_all())
        self.bind("<Control-d>", lambda e: self.toggle_theme())

    def apply_global_theme(self) -> None:
        """aplikuje zvolene tema."""
        if self.is_dark_mode:
            bg_color = "#252526"
            fg_color = "#ffffff"
            self.style.theme_use('default')
            self.style.configure("TNotebook", background="#333333", borderwidth=0)
            self.style.configure("TNotebook.Tab", background="#2d2d2d", foreground=fg_color, padding=[10, 2])
            self.style.map("TNotebook.Tab", background=[("selected", "#1e1e1e")], foreground=[("selected", "#569cd6")])
            
            self.style.configure("Treeview", background="#252526", foreground=fg_color, fieldbackground="#252526", borderwidth=0)
            self.style.map("Treeview", background=[("selected", "#37373d")])
            
            self.config(bg=bg_color)
            self.menubar.config(bg=bg_color, fg=fg_color)
            
            # barvy panelu hledani a stavoveho radku
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        else:
            self.style.theme_use('vista' if os.name == 'nt' else 'clam')
            
            self.style.configure("Treeview", background="white", foreground="black", fieldbackground="white", borderwidth=0)
            self.style.map("Treeview", background=[("selected", "#0078d7")])
            
            self.config(bg="#f0f0f0")
            self.menubar.config(bg="#f0f0f0", fg="black")
            
            # barvy panelu hledani a stavoveho radku
            self.style.configure("TFrame", background="#f0f0f0")
            self.style.configure("TLabel", background="#f0f0f0", foreground="black")

        for tab_id in self.notebook.tabs():
            tab = self.notebook.nametowidget(tab_id)
            if isinstance(tab, EditorTab):
                tab.apply_theme(self.is_dark_mode)

    def toggle_theme(self) -> None:
        """prepne rezim."""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_global_theme()

    def add_new_tab(self, file_path: str | None = None, content: str = "") -> None:
        """vytvori novou zalozku."""
        new_tab = EditorTab(self.notebook, self.status_var, file_path)
        title = os.path.basename(file_path) if file_path else "Nový soubor"
        
        self.notebook.add(new_tab, text=title)
        
        if file_path:
            new_tab.text_area.insert("1.0", content)
            new_tab.has_changes = False
            
        self.notebook.select(new_tab)
        new_tab.apply_theme(self.is_dark_mode)
        new_tab.on_content_change()
        
        new_tab.text_area.edit_modified(False)

    def get_current_tab(self) -> EditorTab | None:
        """vrati aktivni zalozku."""
        current_tab_id = self.notebook.select()
        return self.notebook.nametowidget(current_tab_id) if current_tab_id else None

    def open_file(self) -> None:
        """dialog otevreni souboru."""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.add_new_tab(file_path, file.read())
            except Exception as e:
                messagebox.showerror("Chyba", str(e))

    def save_file(self) -> None:
        """ulozeni aktivni zalozky."""
        current_tab = self.get_current_tab()
        if not current_tab: return
        if not current_tab.file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if not file_path: return
            current_tab.file_path = file_path
            
        try:
            with open(current_tab.file_path, "w", encoding="utf-8") as file:
                file.write(current_tab.text_area.get("1.0", tk.END).rstrip())
            
            current_tab.has_changes = False
            self.notebook.tab(current_tab, text=os.path.basename(current_tab.file_path))
            messagebox.showinfo("Uloženo", "Soubor byl uložen.")
            
            self.tree.delete(*self.tree.get_children())
            self.load_directory(self.current_dir, "")
            
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    def replace_all(self) -> None:
        """nahrazeni textu."""
        current_tab = self.get_current_tab()
        if not current_tab: return
        hledat = simpledialog.askstring("Najít", "Hledat:")
        nahradit = simpledialog.askstring("Nahradit", "Nahradit za:")
        if hledat and nahradit is not None:
            obsah = current_tab.text_area.get("1.0", tk.END)
            novy_obsah = obsah.replace(hledat, nahradit)
            current_tab.text_area.delete("1.0", tk.END)
            current_tab.text_area.insert("1.0", novy_obsah)
            current_tab.on_content_change()

    def get_all_tabs(self) -> list[EditorTab]:
        """vrati vsechny zalozky."""
        return [self.notebook.nametowidget(tab_id) for tab_id in self.notebook.tabs() if isinstance(self.notebook.nametowidget(tab_id), EditorTab)]

    def on_exit(self) -> None:
        """varuje pred zavrenim."""
        zmeny = any(tab.has_changes for tab in self.get_all_tabs())
        
        if zmeny:
            odpoved = messagebox.askyesno(
                "Neuložené změny", 
                "Máte neuložené změny v některých souborech.\nOpravdu chcete editor zavřít a přijít o ně?"
            )
            if odpoved:
                self.destroy()
        else:
            self.destroy()