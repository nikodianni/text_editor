# Můj Python Editor 📝

Jednoduchý textový editor vytvořený v Pythonu pomocí vestavěné knihovny `tkinter`. 
Tento projekt vznikl jako praktické cvičení pro zdokonalení mých dovedností v Pythonu, zejména v objektově orientovaném programování (OOP), tvorbě grafického uživatelského rozhraní (GUI) a práci s regulárními výrazy.

## Hlavní funkce
* **Záložky (Tabs):** Možnost mít otevřeno více souborů najednou.
* **Číslování řádků:** Dynamické číslování, které se aktualizuje při psaní a scrollování.
* **Zvýraznění syntaxe (Syntax Highlighting):** Základní obarvování klíčových slov (např. `if`, `while`, `for`, `def`), řetězců a komentářů v Python kódu.
* **Zvýraznění aktuálního řádku:** Pro lepší orientaci v textu.
* **Najít a nahradit:** Funkce pro hromadné přepisování textu (např. přepsání všech výskytů určité proměnné).
* **Naposledy otevřené soubory:** Rychlý přístup k nedávno upravovaným souborům přes horní menu.

## Použité technologie
* **Python 3.8+**
* **Tkinter:** Pro vytvoření oken, tlačítek a textových polí.
* **re (Regular Expressions):** Pro vyhledávání vzorů v textu a obarvování syntaxe.
* **os:** Pro základní práci s cestami k souborům.

## Jak projekt nainstalovat a spustit

Díky modernímu balíčkování přes `jahudka.toml` je instalace a spuštění velmi snadné.

1. Naklonuj si tento repozitář nebo stáhni zdrojové kódy.
2. Otevři terminál ve složce s projektem (tam, kde je soubor `jahudka.toml`).
3. Nainstaluj projekt pomocí příkazu:
   ```bash
   pip install .
