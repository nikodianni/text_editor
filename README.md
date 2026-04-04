# Můj Python Editor

Jednoduchý, ale šikovný textový a kódový editor napsaný v Pythonu s využitím knihovny Tkinter. Editor je rozdělený do modulární struktury a nabízí moderní funkce včetně plnohodnotného tmavého režimu.

## 🌟 Hlavní funkce

* **Podpora více záložek:** Možnost mít otevřeno několik souborů najednou.
* **Tmavý režim (Dark Mode):** Globální tmavý vzhled inspirovaný editorem VS Code (přepínání pomocí `Ctrl+D`).
* **Zvýrazňování syntaxe:** Automatické obarvování klíčových slov, textových řetězců a komentářů v Pythonu.
* **Číslování řádků:** Dynamický panel s čísly řádků, který se synchronizuje se scrollováním textu.
* **Zvýraznění aktivního řádku:** Vizuální odlišení řádku, na kterém se aktuálně nachází kurzor.
* **Najít a nahradit:** Funkce pro hromadné nahrazování textu (`Ctrl+H`).
* **Klávesové zkratky:** Podpora standardních zkratek (`Ctrl+N`, `Ctrl+O`, `Ctrl+S`).

## 📋 Požadavky

* Nainstalovaný **Python 3.x** (doporučena verze 3.12 a novější)
* Git (pro stažení repozitáře)

## 🛠️ Stažení a instalace

Pro správné fungování a propojení všech souborů je potřeba projekt stáhnout a nainstalovat pomocí nástroje `pip`.

1. Otevři terminál a naklonuj si tento repozitář:
   ```bash
   git clone [https://github.com/nikodianni/text_editor.git](https://github.com/nikodianni/text_editor.git)
   ```

2. Přesuň se do složky projektu:
   ```bash
   cd text_editor
   ```

3. Spusť instalační příkaz (pro Windows):
   ```bash
   py -m pip install .
   ```
   *(Poznámka: Na Linuxu/macOS použij `python3 -m pip install .`)*

## 🚀 Spuštění

Po úspěšné instalaci můžeš editor spustit tímto příkazem z jakékoliv složky:

```bash
py -m editor.main
```
*(Případně pomocí příkazu `spustit-editor`, pokud to podporuje tvé nastavení prostředí.)*

## ⌨️ Klávesové zkratky

| Zkratka | Akce |
| :--- | :--- |
| `Ctrl + N` | Nový soubor |
| `Ctrl + O` | Otevřít soubor |
| `Ctrl + S` | Uložit soubor |
| `Ctrl + H` | Nahradit vše |
| `Ctrl + D` | Přepnout tmavý/světlý režim |

## 📁 Struktura projektu

```text
text_editor/
├── pyproject.toml       # Konfigurace pro instalaci balíčku
├── README.md            # Dokumentace projektu
└── editor/              # Hlavní balíček aplikace
    ├── __init__.py
    ├── app.py           # Hlavní okno, menu a globální správa vzhledu
    ├── main.py          # Spouštěcí skript aplikace
    └── tab.py           # Logika jednotlivých záložek a práce s textem
```

---
*Vytvořeno v rámci výuky a pro radost z programování.*
