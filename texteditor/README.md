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

## 📁 Struktura projektu

Projekt je logicky rozdělen do více souborů pro lepší přehlednost:

```text
texteditor/
├── pyproject.toml       # Konfigurace pro instalaci balíčku
├── README.md            # Dokumentace projektu
└── editor/              # Hlavní balíček aplikace
    ├── __init__.py
    ├── app.py           # Hlavní okno, menu a globální správa vzhledu
    ├── main.py          # Spouštěcí skript aplikace
    └── tab.py           # Logika jednotlivých záložek a práce s textem
```

## 🛠️ Instalace

Pro správné fungování a propojení všech souborů je potřeba projekt nainstalovat pomocí nástroje `pip`.

1. Otevři terminál a ujisti se, že jsi v kořenové složce projektu (`texteditor`).
2. Spusť instalační příkaz (pro Windows):
   ```bash
   py -m pip install .
   ```

## 🚀 Spuštění

Po úspěšné instalaci můžeš editor spustit tímto příkazem z jakékoliv složky:

```bash
py -m editor.main
```
*(Případně pomocí příkazu `spustit-editor`, pokud je takto nastaven tvůj `pyproject.toml`.)*

## ⌨️ Klávesové zkratky

| Zkratka | Akce |
| :--- | :--- |
| `Ctrl + N` | Nový soubor |
| `Ctrl + O` | Otevřít soubor |
| `Ctrl + S` | Uložit soubor |
| `Ctrl + H` | Nahradit vše |
| `Ctrl + D` | Přepnout tmavý/světlý režim |

---
*Vytvořeno v rámci výuky a pro radost z programování.*