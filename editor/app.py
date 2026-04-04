import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from editor.tab import EditorTab  # import zalozky z druheho souboru

class EditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Můj Python Editor")
        self.geometry("900x700")
        
        self.is_dark_mode = False
        self.style = ttk.Style()
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_menu()
        self.add_new_tab()
        self.apply_global_theme()

    def create_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Soubor", menu=file_menu)
        file_menu.add_command(label="Nový", command=self.add_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Otevřít...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Uložit", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Ukončit", command=self.quit)

        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Úpravy", menu=edit_menu)
        edit_menu.add_command(label="Nahradit vše...", command=self.replace_all, accelerator="Ctrl+H")
        
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Zobrazení", menu=view_menu)
        view_menu.add_command(label="Přepnout tmavý režim", command=self.toggle_theme, accelerator="Ctrl+D")

        self.bind("<Control-n>", lambda e: self.add_new_tab())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-h>", lambda e: self.replace_all())
        self.bind("<Control-d>", lambda e: self.toggle_theme())

    def apply_global_theme(self):
        if self.is_dark_mode:
            bg_color = "#252526"
            fg_color = "#ffffff"
            self.style.theme_use('default')
            self.style.configure("TNotebook", background="#333333", borderwidth=0)
            self.style.configure("TNotebook.Tab", background="#2d2d2d", foreground=fg_color, padding=[10, 2])
            self.style.map("TNotebook.Tab", background=[("selected", "#1e1e1e")], foreground=[("selected", "#569cd6")])
            
            self.config(bg=bg_color)
            self.menubar.config(bg=bg_color, fg=fg_color)
        else:
            self.style.theme_use('vista' if os.name == 'nt' else 'clam')
            self.config(bg="#f0f0f0")
            self.menubar.config(bg="#f0f0f0", fg="black")

        for tab_id in self.notebook.tabs():
            tab = self.notebook.nametowidget(tab_id)
            tab.apply_theme(self.is_dark_mode)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_global_theme()

    def add_new_tab(self, file_path=None, content=""):
        new_tab = EditorTab(self.notebook, file_path)
        title = os.path.basename(file_path) if file_path else "Nový soubor"
        if file_path:
            new_tab.text_area.insert("1.0", content)

        self.notebook.add(new_tab, text=title)
        self.notebook.select(new_tab)
        new_tab.apply_theme(self.is_dark_mode)
        new_tab.on_content_change()

    def get_current_tab(self):
        current_tab_id = self.notebook.select()
        return self.notebook.nametowidget(current_tab_id) if current_tab_id else None

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.add_new_tab(file_path, file.read())
            except Exception as e:
                messagebox.showerror("Chyba", str(e))

    def save_file(self):
        current_tab = self.get_current_tab()
        if not current_tab: return
        if not current_tab.file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if not file_path: return
            current_tab.file_path = file_path
            self.notebook.tab(current_tab, text=os.path.basename(file_path))
        try:
            with open(current_tab.file_path, "w", encoding="utf-8") as file:
                file.write(current_tab.text_area.get("1.0", tk.END).rstrip())
            messagebox.showinfo("Uloženo", "Soubor byl uložen.")
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    def replace_all(self):
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