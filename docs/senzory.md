# Senzory pro stěnový box — srovnání a volba

## Srovnání

| Model | Měří | Princip přesnosti | T | RH | CO₂ reálný | Odběr | ESPHome | Cena Kč |
|---|---|---|---|---|---|---|---|---|
| **SHT40** | T, RH | kapacitní | ±0.2…0.3 K | ±2 % | — | µA–mA | nativní `sht4x` | 60–150 |
| **HDC3020** | T, RH | kapacitní (TI premium) | ±0.2 K | ±2 %, dlouhodobě stabilnější | — | µA–mA | nativní `hdc302x` (od 2024.x) | 300–500 |
| **AHT21** | T, RH | kapacitní | ±0.3…0.5 K | ±2 % | — | µA | `aht20` (kompatibilní) | 30–60 |
| **BME280** | T, RH, tlak | kapacitní + barometr | ±1 K | ±3 % | — | mA | nativní `bme280` | 150–250 |
| **SCD40** | **CO₂ ppm**, T, RH (doplňkové) | photoakustický NDIR | ±0.25 K | ±3 % | **ANO** | prům. ~10 mA, špička při měření | nativní `scd4x` | 700–1200 |
| **SCD30** | CO₂ ppm, T, RH | NDIR (starší, větší) | ±0.5 K | ±3 % | ANO | větší | nativní `scd3x` | 900–1500 |
| **ENS160** (+AHT21 combo) | VOC index, eCO2, AQI 1–5 | MOX + ML model | — | — | **NE** — eCO2 je odvozený od VOC | ~15 mW pulsů | nativní `ens160_i2c` | 100–150 (combo) |
| **BME680/688** | T, RH, P, VOC | MOX (rezistivní MOX) | ±1 K | ±3 % | NE | vyšší (heater cykly) | `bme680`; 688 ověřit | 300–600 |
| **SGP40** (+SHT31) | VOC/NOx index | MOX | — | — | NE | střední | vlastní komponent, ověřit | 300–450 |

## Rozhodnutí pro tento projekt
1. **Regulační větev (topení): SHT40** — přesnost ±0.2 K, nejnižší cena, nativní podpora. HDC3020 = premium alternativa (+200–350 Kč/ks, +8 Kč za místnost) pro lepší dlouhodobou stabilitu RH; pro topení přínos nulový, pro vlhkost/mírné plísně ANO. Volba: **SHT40, na request HDC3020**.
2. **CO₂: SCD40** — jediný v seznamu, co reálně měří CO₂ (NDIR). MOX senzory (ENS160/BME680/SGP40) CO₂ **neumí** — jejich "eCO2" je odhad z VOC a v ložnici plné spících lidí hlásí normu (doloženo i v ESPHome docs: "For real CO2, buy an SCD4x"). T/RH u SCD40 slouží jen ke kompenzaci, ne pro regulaci.
3. **VOC/seznaovací kvalita vzduchu: ENS160+AHT21 volitelně** (+130 Kč/box, native od ESPHome 2023.11,sdílená I2C bus, adresy 0x52/0x53 — konflikty žádné). Přidá AQI 1–5 a "čichový" alert (obarva, vaření, plísně). Podmínka: kompenzace T/RH (součást combo desky). Start: 1 h burn-in, pak 3 min warm-up při rebootu.
4. **Vylučujeme:** BME280 (tlak k ničemu, T/RH horší a dražší než SHT40/AHT21), BME680/688 (heater odběr, jen index, srovnatelná cena s lepším ENS160), SGP40 (starší generace, horší podpora).

## Adresy I2C v boxu (SCD40 + SHT40 [+ ENS160])
`SHT40: 0x44 (volitelně 0x45) · SCD40: 0x62 · ENS160: 0x52 · AHT21: 0x38` — průnik žádný, jedna smyčka SDA/SCL.

## Dopad na rozpočet thin-link
Odběr s ENS160 navíc: +~5 mA průměrně na 3.3V → +0.7 mA na 24V straně. Zbývá v hranicích §3 designu (dimenzováno na 50 mA špičku).

## Varianta nákupů
- **Standard (doporučeno):** SHT40 + SCD40 = box 1 080 Kč
- Premium RH: HDC3020 + SCD40 = box ~1 350 Kč
- Standard + VOC: SHT40 + SCD40 + ENS160AHT21 = box ~1 210 Kč
- Bez CO₂ (jen topení): SHT40 = box ~380 Kč — v tomto případě se vyplatí zeptat se předem, jestli to tak má opravdu být.
