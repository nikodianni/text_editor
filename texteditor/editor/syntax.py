"""modul pro zvyraznovani syntaxe a zavorek."""

import tkinter as tk
import re

class SyntaxHighlighter:
    def __init__(self, text_area: tk.Text) -> None:
        self.text_area = text_area
        self._init_tags()

    def _init_tags(self) -> None:
        """zakladni nastaveni tagu pro barvy."""
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("string", foreground="green")
        self.text_area.tag_configure("comment", foreground="gray")
        self.text_area.tag_configure("current_line", background="#e8f2fe")
        self.text_area.tag_configure("search_match", background="yellow", foreground="black")
        self.text_area.tag_configure("bracket_match", background="lightgreen", foreground="black")

    def apply_theme(self, is_dark: bool) -> None:
        """prebarvi tagy podle tematu."""
        if is_dark:
            self.text_area.tag_configure("keyword", foreground="#569cd6")
            self.text_area.tag_configure("string", foreground="#ce9178")
            self.text_area.tag_configure("comment", foreground="#6a9955")
            self.text_area.tag_configure("current_line", background="#2a2d2e")
            self.text_area.tag_configure("bracket_match", background="#4d4d4d", foreground="white")
        else:
            self.text_area.tag_configure("keyword", foreground="blue")
            self.text_area.tag_configure("string", foreground="green")
            self.text_area.tag_configure("comment", foreground="gray")
            self.text_area.tag_configure("current_line", background="#e8f2fe")
            self.text_area.tag_configure("bracket_match", background="lightgreen", foreground="black")

    def highlight_all(self) -> None:
        """obarvi syntax a zvyrazni aktualni radek."""
        # aktualni radek
        self.text_area.tag_remove("current_line", "1.0", tk.END)
        self.text_area.tag_add("current_line", "insert linestart", "insert lineend+1c")

        # syntax (klicova slova, stringy, komentare)
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

    def highlight_brackets(self) -> None:
        """zvyrazni parove zavorky kolem kurzoru."""
        self.text_area.tag_remove("bracket_match", "1.0", tk.END)
        pos = self.text_area.index(tk.INSERT)
        
        char_after = self.text_area.get(pos, f"{pos}+1c")
        char_before = self.text_area.get(f"{pos}-1c", pos)

        pairs = {'(': ')', '[': ']', '{': '}'}
        rev_pairs = {')': '(', ']': '[', '}': '{'}

        if char_after in pairs:
            self._find_and_tag(pos, char_after, pairs[char_after], 1)
        elif char_before in rev_pairs:
            self._find_and_tag(f"{pos}-1c", char_before, rev_pairs[char_before], -1)

    def _find_and_tag(self, start_pos: str, char: str, match_char: str, direction: int) -> None:
        """najde spojenou zavorku."""
        txt = self.text_area.get("1.0", tk.END)
        idx_str = self.text_area.count("1.0", start_pos, "chars")
        idx = idx_str[0] if idx_str else 0
        depth = 1

        match_idx = -1
        if direction == 1:
            for i in range(idx + 1, len(txt)):
                if txt[i] == char: depth += 1
                elif txt[i] == match_char: depth -= 1
                if depth == 0:
                    match_idx = i; break
        else:
            for i in range(idx - 1, -1, -1):
                if txt[i] == char: depth += 1
                elif txt[i] == match_char: depth -= 1
                if depth == 0:
                    match_idx = i; break

        if match_idx != -1:
            self.text_area.tag_add("bracket_match", f"1.0+{idx}c", f"1.0+{idx+1}c")
            self.text_area.tag_add("bracket_match", f"1.0+{match_idx}c", f"1.0+{match_idx+1}c")