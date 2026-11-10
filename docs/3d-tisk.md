# 3D tisk — modely a postupy

Vlastní parametrické modely (OpenSCAD, uprav rozměry v UI sliders a exportuj STL):

| Soubor | Co | Předběžné rozměry | Tisk |
|---|---|---|---|
| `hardware/scad/sensor-box.scad` | stěnový box (C6 + SCD40), ventilace, montáž na zeď, viko na 4 šroubky | 54×44×30 mm | PLA+/PETG, 3 stěny, 20 % infill, bez supportů |
| `hardware/scad/valve-box.scad` | přechodová krabička u radiátoru (svorky → konektor pohonu) | 45×30×22 | PETG (teplejší prostředí u radiátoru!) |
| `hardware/scad/centrala-dp.scad` | montážní deska do centrální krabice (rozteče pro 2×8CH relay + PSU + svorkovnice) | dle krabice | PLA, 25 % |

Pravidla:
- **u radiátoru PETG** (PLA při 60 °C měkne)
- SCD40 **nesmí být utěsněný** — větrací štěrbiny do boků/spodu (model je obsahuje); nad krabicí neclonit (konvekce)
- ESP32 anténa k hornímu okraji, dál od kovových předmětů
- PLA ~30 g / 8 krabic ≈ 15 Kč filamentu, PETG 8 ks valve-box ≈ 10 Kč

## Hotové alternativy na Printables/MakerWorld (když nechceš tisknout vlastní)
- ESP32 Environmental Sensor Enclosure (ventilovaný, konvekce, friction-fit) — https://www.printables.com/model/357398-esp32-environmental-sensor-enclosure
- ESP32 38pin Wallhousing Wallmount Case (na zeď, šrouby, přístup USB) — https://www.printables.com/model/1179639-esp32-38pin-wallhousing-wallmount-case-box-enclosu
- ESP32 Simple enclosure (ventilace, snap lid; MakerWorld) — https://makerworld.com/en/models/1993672-esp32-simple-enclosure
- Pro centrálu: hledat „DIN rail box 3d print" / „powersupply mount 3d print" na Printables; nebo koupit DIN krabici IP43 za ~150 Kč a nechat si vytisknout jen montážní destičku.

> Všechny modely třetích stran mají svou licenci (většinou CC) — ověř před komerčním remixem; pro osobní použití OK.
