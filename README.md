# Regulace vytápění — 12 místností, Home Assistant

Systém room-by-room regulace radiátorového vytápění. Každá místnost má stěnový měřicí box (teplota, vlhkost, CO₂) na stávající tenké lince a voskový pohon ventilu 24 V na stávající silné lince. Rozhodování probíhá v boxu, výkon spíná centrála.

## Architektura

```
Stěnový box (×12)                      Centrála
ESP32-C6 + SHT40 + SCD40               RPi 3: Home Assistant, Mosquitto, Tailscale
buck 24→5 V (tenká linka)              + 3× 8CH relay board
regulace: bang-bang, hystereze ±0.3/0.5 K,          ├── varianta A: GPIO Pi přímo
mrazovka, min ON/OFF režimové doby             └── varianta B: ESP32 akter (doporučeno)
        │                                          │
        └── Wi-Fi 2.4 / MQTT ──► HA ──► relé ──► 24 V PSU ──► silná linka ──► pohon NC M30×1.5
```

- Box publikuje setpoint i stav; centrála vykonává a hlídá failsafe (TTL heartbeat).
- Bez napájení zavírá ventil pružina (typ pohonu NC).

## Místnosti a mapa

| id | místnost | MQTT topic | HA entita |
|---|---|---|---|
| J1 | Můj pokoj | `vyt/j1/*` | `switch.vyt_j1` |
| J2 | Hostovský | `vyt/j2/*` | `switch.vyt_j2` |
| J3 | Koupelna dole | `vyt/j3/*` | `switch.vyt_j3` |
| J4 | Kuchyně | `vyt/j4/*` | `switch.vyt_j4` |
| J5 | Obývák 2 | `vyt/j5/*` | `switch.vyt_j5` |
| J6 | Předsíň | `vyt/j6/*` | `switch.vyt_j6` |
| J7 | Šatna dole | `vyt/j7/*` | `switch.vyt_j7` |
| J8 | Koupelna nahoře | `vyt/j8/*` | `switch.vyt_j8` |
| J9 | Ložnice nahoře | `vyt/j9/*` | `switch.vyt_j9` |
| J10 | Horní paluba | `vyt/j10/*` | `switch.vyt_j10` |
| J11 | Horní šatna | `vyt/j11/*` | `switch.vyt_j11` |
| J12 | Horní pokoj | `vyt/j12/*` | `switch.vyt_j12` |

Zdroj mapy: `scripts/gen-zone.py` (proměnná `ROOMS`).

## MQTT interface

| Topic | Směr | Payload | Retain |
|---|---|---|---|
| `vyt/jX/valve` | box → centrála | `ON` / `OFF` | ano |
| `vyt/jX/setpoint` | HA → box | `21.5` | ano |
| `vyt/jX/heartbeat` | box → HA | `online` | ne (30 s) |
| `vyt/jX/preset` | HA → box | `comfort/eco/away/sleep` | ano |

## Hardware — specifikace

| Součástka | Specifikace | Množství |
|---|---|---|
| Měřicí box | ESP32-C6, SHT40 (I2C), SCD40 (I2C), buck MP1584 24→5 V, pojistka 0.5 A | 12 |
| Pohon ventilu | voskový, 24 V DC, NC, závit M30×1.5 | 12 |
| Spínání | 3× 8CH relay board, TONGLING JQC-3FF-S-Z 5V (optočleny, low-trigger, JD-VCC oddělen, cívky z 5 V/3 A PSU) | 3 (24 kan.) |
| Zdroj ventilů | 24 V / 5 A | 1 |
| Řídicí unit | RPi 3, HA OS, NVMe | 1 |
| Akter (varianta B) | ESP32 devkit | 1 |
| Ochrana | 12× pojistka 1 A (ventily), 12× 0.5 A (boxy) | 24 |

Parametry sítě: Wi-Fi 2.4 GHz, 13–14 klientů; broker `192.168.1.10:1883` (statická reservace).

## Dokumentace

| Dokument | Obsah |
|---|---|
| [docs/design-v0.4.md](docs/design-v0.4.md) | inženýrské rozvedení, dimenzování linek, selhání |
| [docs/setup-prirucka.md](docs/setup-prirucka.md) | instalace po krocích: HA, MQTT, GPIO/akter, boxy, flashování, uvedení do provozu |
| [docs/installace-centrala.md](docs/installace-centrala.md) | zapojení centrály, GPIO tabulky |
| [docs/installace-pokoj.md](docs/installace-pokoj.md) | stavba a montáž boxu, měřicí checklist |
| [docs/nakupni-plan.md](docs/nakupni-plan.md) | nákup: MVP 1 místnost / plný rozsah |
| [docs/3d-tisk.md](docs/3d-tisk.md) | tiskové modely a pravidla |
| [docs/senzory.md](docs/senzory.md) | srovnání senzorů a volba |

## Repozitář

```
firmware/esphome/box.yaml             šablona stěnového boxu (×12, substitutions)
firmware/esphome/central-actor.yaml   varianta B — ESP32 akter (generovaný)
ha/switch-gpio.md                     varianta A — GPIO switches v HA
ha/automations-vyt.yaml               J1 vzor + boot-safe-off, mrazovka, CO2, scény
ha/automations-vyt-z2-z12.yaml        generované zóny J2–J12
ha/lovelace-vyt.yaml                  dashboard (generovaný)
scripts/gen-zone.py                   generator automations/dash (ROOMS)
scripts/gen-central.py                generator aktéru (PINS)
hardware/scad/                        parametrické krabice (OpenSCAD)
```

Po změně mapy místností/pinů: `python3 scripts/gen-zone.py > ... && python3 scripts/gen-central.py > ...` a commit.

## Stav

- [x] design v0.4 finalized (12 místností, varianty A/B centrály)
- [ ] nákup MVP
- [ ] pilot J1: flash boxu, relay kanál, měření pohonu + RSSI
- [ ] rollout J2–J12
- [ ] plány, notifikace na telefon, doladění hysterezí
