# DychMon
### Prototyp systému na monitorovanie dýchania psov v celkovej anestézii

## O projekte
Dychmon je prototyp systému na kontinuálne monitorovanie dýchania psov. Projekt vznikol ako súčasť záverečnej práce s cieľom navrhnúť a implementovať cenovo dostupný systém na monitorovanie respiračnej aktivity pomocou elastického hrudného pásu so stretch senzorom. Respiračný signál je spracovávaný v reálnom čase a zobrazený prostedníctvom grafického rozhrania.

## Hlavné vlastnosti
- kontinuálne monitorovanie respiračného signálu
- zobrazenie dychovej krivky v reálnom čase
- priebežný výpočet dychovej frekvencie
- export nameraných dát do CSV
- modulárna architektúra programu
- podpora reálneho aj simulačného režimu

## Hardvér
- Raspberry Pi
- ADS1115 16-bitový A/D prevodník
- stretch senzor
- elastický hrudný pás

## Softvér
Projekt je implementovaný v jazyky Python, použité knižnice:
- Matplotlib
- NumPy
- SciPy
- Tkinter
- Adafruit Blinka
- Adafruit CircuitPython ADS1x15

## Architektúra
Modulárna aplikácia v jazyku Python, hlavné použité moduly: 
- **gui/** – grafické používateľské rozhranie
- **measurement/** – zber a spracovanie nameraných dát
- **sensors/** – komunikácia so senzormi (ADS1115 alebo simulačný režim)
- **logger/** – zaznamenávanie udalostí a diagnostických informácií
- **config.py** – konfiguračné parametre systému

Architektúra umožňuje rozšírenie systému o nové senzory, algoritmy a funkcie.

## Inštalácia
Projekt je určený pre Raspberry Pi s operačným systémom Raspberry Pi OS.
Pred spustením programu je potrebné nainštalovať požadované Python knižnice uvedené vyššie.


## Spustenie
Program je možné spustiť jediným príkazom:

```bash
python dychmon_gui.py
```

## Spracovanie signálu
Stretch senzor sníma zmeny napnutia elastického hrudného pásu spôsobené pohybom hrudníka počas dýchania.
Analógový signál je digitalizovaný pomocou A/D prevodníka ADS1115 a následne spracovaný v prostredí Python.

Program zabezpečuje:
- zber dát zo stretch senzora,
- digitalizáciu analógového signálu pomocou ADS1115,
- detekciu lokálnych maxím respiračného signálu,
- priebežný výpočet dychovej frekvencie,
- grafické zobrazenie dychovej krivky,
- export nameraných dát do CSV.

## Technická validácia
Prototyp bol testovaný na siedmich psoch počas celkovej anestézie v podmienkach bežnej veterinárnej praxe.

Technická validácia bola realizovaná porovnaním dychovej frekvencie určenej algoritmom s manuálnym počítaním dychov skúseným anesteziológom počas rovnakého časového intervalu.

Cieľom validácie bolo overiť technickú realizovateľnosť navrhnutého riešenia.

## Limity prototypu
Projekt predstavuje výskumný prototyp a nie je certifikovanou zdravotníckou pomôckou. Výsledky slúžia výhradne na technické overenie navrhnutého princípu monitorovania.

Presnosť merania môže byť ovplyvnená:
- nesprávnym umiestnením hrudného pásu,
- pohybom pacienta počas merania,
- kvalitou senzorového signálu,
- mechanickými vlastnosťami stretch senzora.

## Budúci vývoj
Ďalší vývoj projektu bude zameraný najmä na:
- detekciu jednotlivých dychových cyklov,
- alarm pri apnoe,
- adaptívne spracovanie signálu
- hodnotenie kvality signálu,
- bezdrôtovú komunikáciu,
- batériové napájanie,
- implementáciu na mikrokontroléri,
- integráciu s veterinárnymi monitorovacími systémami,
- podporu ďalších fyziologických senzorov.

## Autor
doc. MVDr. Mária Kuricová, PhD., MBA
- Univerzita veterinárskeho lekárstva a farmácie v Košiciach
- Slovenská republika

