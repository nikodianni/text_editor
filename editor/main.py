import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import re
import os

class EditorTab(ttk.Frame):
    """Trida pro jednu zalozku v editoru"""
    def __init__(self, notebook, file_path=None):
        super().__init__(notebook)
        self.file_path = file_path
        
        # levy panel na cisla radku, nejde do nej psat (state disabled)
        self.line_numbers = tk.Text(self, width=4, padx=4, takefocus=0, border=0,
                                    background="#f0f0f0", state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # hlavni pole kam se pise text
        self.text_area = tk.Text(self, undo=True, wrap='none')
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # posuvnik napravo
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scrollbar)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        
        # nastaveni barev pro ruzne veci v textu (klicova slova atd)
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("string", foreground="green")
        self.text_area.tag_configure("comment", foreground="gray")
        self.text_area.tag_configure("current_line", background="#e8f2fe")

        # co se stane kdyz zmacknu klavesu nebo kliknu mysi
        self.text_area.bind('<Any-KeyPress>', self.on_content_change)
        self.text_area.bind('<Button-1>', self.on_content_change)
        self.text_area.bind('<MouseWheel>', self.on_content_change)

    def _on_scrollbar(self, *args):
        """propojeni posuvniku s textem a cislama radku aby se hybaly stejne"""
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def on_content_change(self, event=None):
        """zavola se po kazde zmene, updatne barvy a cisla radku. after 10 je tam aby to melo chvilku cas."""
        self.after(10, self.update_line_numbers)
        self.after(10, self.highlight_current_line)
        self.after(10, self.highlight_syntax)

    def update_line_numbers(self):
        """spocita radky a vypise jejich cisla doleva"""
        # zjistime kolik mame celkem radku
        lines = self.text_area.get('1.0', tk.END).count('\n')
        
        # vytvorime dlouhy text s cislama pod sebou (1 \n 2 \n 3...)
        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        
        # odemkneme levy panel, prepiseme cisla a zase zamkneme
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        
        # aby se spravne scrollovaly i ty cisla
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def highlight_current_line(self):
        """obarvi radek kde zrovna blika kurzor"""
        self.text_area.tag_remove("current_line", "1.0", tk.END)
        self.text_area.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def highlight_syntax(self):
        """prohleda text a obarvi to co zname (if, while atd)"""
        # nejdriv smazeme stary barvy aby se to nepletlo
        for tag in ["keyword", "string", "comment"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)

        text_content = self.text_area.get("1.0", tk.END)

        # 1. hledame klicova slova a barvime je na modro
        keywords = [r'\bif\b', r'\bwhile\b', r'\bwhen\b', r'\bfor\b', r'\bdef\b', r'\bclass\b']
        for kw in keywords:
            for match in re.finditer(kw, text_content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_area.tag_add("keyword", start, end)

        # 2. hledame text v uvozovkach a barvime na zeleno
        for match in re.finditer(r'[\'"].*?[\'"]', text_content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_area.tag_add("string", start, end)

        # 3. hledame komentare zacinajici mrizkou (az do konce radku)
        for match in re.finditer(r'#.*', text_content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_area.tag_add("comment", start, end)


class EditorApp(tk.Tk):
    """Hlavni okno cele aplikace"""
    def __init__(self):
        super().__init__()
        self.title("Můj Python Editor")
        self.geometry("800x600")
        
        # tady ukladame historii, po vypnuti programu se to ale smaze
        self.recent_files = [] 

        # notebook = panel se zalozkama
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_menu()
        self.add_new_tab() # hned pri startu udelame jednu prazdnou zalozku

    def create_menu(self):
        """vytvori horni listu (Soubor, Upravy atd)"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # menu Soubor
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Soubor", menu=file_menu)
        file_menu.add_command(label="Nový", command=self.add_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Otevřít...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Uložit", command=self.save_file, accelerator="Ctrl+S")
        
        # podmenu na historii souboru
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Naposledy otevřené", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Ukončit", command=self.quit)

        # menu Upravy
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Úpravy", menu=edit_menu)
        edit_menu.add_command(label="Nahradit vše...", command=self.replace_all, accelerator="Ctrl+H")

        # klavesove zkratky aby to slo i pres klavesnici
        self.bind("<Control-n>", lambda e: self.add_new_tab())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-h>", lambda e: self.replace_all())

    def get_current_tab(self):
        """zjisti v jake zalozce zrovna jsem (ktera je aktivni)"""
        current_tab_id = self.notebook.select()
        if current_tab_id:
            return self.notebook.nametowidget(current_tab_id)
        return None

    def add_new_tab(self, file_path=None, content=""):
        """prida novou zalozku. kdyz neni file_path tak je to novy prazdny soubor."""
        new_tab = EditorTab(self.notebook, file_path)
        
        if file_path:
            title = os.path.basename(file_path)
            new_tab.text_area.insert("1.0", content)
            self.update_recent_files(file_path)
        else:
            title = "Nový soubor"

        self.notebook.add(new_tab, text=title)
        self.notebook.select(new_tab)
        new_tab.on_content_change() # vynutime obarveni hned po otevreni

    def open_file(self):
        """otevre okno pro vyber souboru a nacte ho do nove zalozky"""
        file_path = filedialog.askopenfilename(filetypes=[("Textové soubory", "*.txt"), ("Python soubory", "*.py"), ("Všechny soubory", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.add_new_tab(file_path, content)
            except Exception as e:
                messagebox.showerror("Chyba", f"Nepodařilo se otevřít soubor:\n{e}")

    def save_file(self):
        """ulozi aktualni zalozku do souboru. kdyz to je novy soubor, zepta se kam."""
        current_tab = self.get_current_tab()
        if not current_tab: return

        if current_tab.file_path is None:
            # je to novy soubor, takze se ptame kam ho ulozit
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                     filetypes=[("Textové soubory", "*.txt"), ("Python", "*.py"), ("Vše", "*.*")])
            if not file_path:
                return # uzivatel kliknul na zrusit
            current_tab.file_path = file_path
            self.notebook.tab(current_tab, text=os.path.basename(file_path))

        try:
            content = current_tab.text_area.get("1.0", tk.END)
            with open(current_tab.file_path, "w", encoding="utf-8") as file:
                file.write(content.rstrip()) # rstrip da pryc prazdny znaky na konci co dela tkinter
            messagebox.showinfo("Úspěch", "Soubor byl úspěšně uložen.")
            self.update_recent_files(current_tab.file_path)
        except Exception as e:
            messagebox.showerror("Chyba", f"Nepodařilo se uložit soubor:\n{e}")

    def update_recent_files(self, file_path):
        """prida soubor do historie a updatne to rozbalovaci menu"""
        # kdyz uz tam je, dame ho pryc a pridame na zacatek
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        
        # nechame tam max 5 souboru at toho neni moc
        self.recent_files = self.recent_files[:5]
        
        # smazeme stary menu a udelame ho znovu s novyma cestama
        self.recent_menu.delete(0, tk.END)
        for path in self.recent_files:
            self.recent_menu.add_command(label=os.path.basename(path), 
                                         command=lambda p=path: self.open_specific_file(p))

    def open_specific_file(self, file_path):
        """otevre soubor kdyz na nej kliknu v historii"""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.add_new_tab(file_path, content)
            except Exception as e:
                messagebox.showerror("Chyba", f"Nelze otevřít: {e}")
        else:
            messagebox.showwarning("Chyba", "Soubor už asi neexistuje.")

    def replace_all(self):
        """najde a nahradi vsechny vyskyty slova v textu"""
        current_tab = self.get_current_tab()
        if not current_tab: return

        hledat = simpledialog.askstring("Nahradit", "Co chceš najít?")
        if not hledat: return
        
        nahradit = simpledialog.askstring("Nahradit", f"Čím chceš nahradit '{hledat}'?")
        if nahradit is None: return # kliknuto na zrusit

        # vezmeme cely text, nahradime to a vlozime zpatky
        obsah = current_tab.text_area.get("1.0", tk.END)
        novy_obsah = obsah.replace(hledat, nahradit)
        
        current_tab.text_area.delete("1.0", tk.END)
        current_tab.text_area.insert("1.0", novy_obsah)
        current_tab.on_content_change()
        
        pocet = obsah.count(hledat)
        messagebox.showinfo("Hotovo", f"Nahrazeno {pocet} výskytů.")

def main():
    """hlavni funkce pro spusteni (dobre pro pyproject.toml)"""
    app = EditorApp()
    app.mainloop()

if __name__ == "__main__":
    main()