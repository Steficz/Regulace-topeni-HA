# Plán nákupu — MVP (1 místnost) → plných 12 místností

Ceny orientační (listopad 2026), CZ e-shopy: GrandLine, GUDLIK, led-ex, DO-METRO, Alza (PSU); levnější cesta AliExpress (dodání 2–4 týdny).

## MVP — pilot 1 místnost („Můj pokoj")
Použiješ: RPi 3 + NVMe 128 GB (máš) · 16CH relay board (máš) · testovací pohon 24V NC (máš).

| # | Položka | ks | ~Ks/ks | Kč | Kde |
|---|---|---|---|---|---|
| 1 | ESP32-C6 supermini (nebo devkit) | 1 | 200 | 200 | Ali / GUDLIK |
| 2 | SHT40 breakout (I2C) | 1 | 100 | 100 | Ali |
| 3 | SCD40 breakout | 1 | 750 | 750 | Ali (nebo ~1200 Mouser/CZ) |
| 4 | buck MP1584 / mini 3602 (24→5V) | 2 | 30 | 60 | Ali (1 náhradní) |
| 5 | PSU 24 V/5 A (Mean Well HDR-150-24) | 1 | 520 | 520 | CZ e-shop |
| 6 | USB PSU 5 V/3 A (kvalitní, např. Mean Well/generic) | 1 | 150 | 150 | CZ |
| 7 | pojistkové pouzdro + pojistky 1A, 0.5A | 4+4 | — | 150 | CZ hobby |
| 8 | svorkovnice 2p (WAGO 221-212 nebo volnoběžné) | 4 | 15 | 60 | CZ |
| 9 | Dupont jumper wires, kabel, cín, drobné | — | — | 150 | CZ |
| 10 | ESP32 classic devkit V4 (varianta B — akter) | 1 | 200 | 200 | Ali/CZ |
| 11 | krabice 3D tisk (filament) | — | — | 50 | — |
| | **MVP celkem** | | | **~2 440 Kč** | |

MVP test: box běží, MQTT flow do relé, změříš dynamiku pohonu + RSSI. Rozhodnutí po pilotu: dotah signálu (2. AP?).

## Plný rozsah — 12 místností
| # | Položka | ks | Kč/ks | Kč |
|---|---|---|---|---|
| 1 | stěnový box: díly 1–5 z MVP (C6+SHT40+SCD40+buck) | 12 | ~1 080 | **12 960** |
| 2 | pohon 24V NC M30×1.5 (SALUS T30NC-24 / ICMA TRP-24NC / Ali) | 12 (11 koupit) | 350–500 | **3 850–5 500** |
| 3 | krabičky u ventilů (3D tisk / svorkovnice IP20) | 12 | 25 | 300 |
| 4 | pojistky 24 ks + lišta držáků | — | — | 350 |
| 5 | svorkovnice rozšíření (řadové 6p/12p, kabelovody) | — | — | 400 |
| 6 | centrální krabice (nebo DIN 200×120×75 + tisk desky) | 1 | 150–250 | 200 |
| 7 | **volitelné:** druhý AP/mesh (2. patro, dle měření) | 1 | 600 | 600 |
| 8 | **volitelné:** UPS 12V + měnič / záloha 24V (failsafe po 230V outage) | 1 | 1 500 | 1 500 |
| | **Plný celkem** | | | **~18–21 tis. Kč** (bez volitelných ~17–19) |

Úspory varianty:
- bez CO₂ (jen SHT40): box ~380 Kč → 12 místností −~8.4 tis. Kč za celek
- SCD40 vs SCD30: SCD40 nižší cena a menší rozměry než SCD30; volba SCD40.
- pohony Ali (tvoje testovací, ~150 Kč/ks + doprava) vs CZ sklad (350+): riziko delší dodání, ale funkčně doloženo tebou.

Kapacity počítané pro 12: 24V/5A PSU ✓ (peak 12×(100+45)mA ≈ 1.75 A), relay board 16CH ✓ (12+, 4 volné), zdroj pro Pi: NVMe+WiFi ~0.7 A na 5V z vlastního PSU, GPIO varianta: cívky 12×70 mA = 0.84 A → 5V/3A PSU s rezervou ✓.
