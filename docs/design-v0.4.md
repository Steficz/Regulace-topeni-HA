# Design v0.4 — technická specifikace

## 1. Rozsah
12 místností (mapa v `scripts/gen-zone.py → ROOMS`), 2 patra, centrála v přízemí, délka linek do 50 m. Na každou místnost existují dva dvouvodičové okruhy z centrály: silná linka 2×0.5–0.75 mm² (k radiátoru) a tenká linka 2×~0.1 mm² (do míst původního prostorového čidla).

## 2. Blokové schéma
```
[stěnový box ×12]                [HA: RPi 3 + NVMe]                [výkonová část]
ESP32-C6                         Home Assistant OS                 varianta A: GPIO Pi
SHT40  (T/RH, I2C)        Wi-Fi  Mosquitto :1883                   varianta B: ESP32 akter
SCD40  (CO2, I2C)      ─────────►Tailscale      ──MQTT────►         16CH relay board
buck 24→5 V                                        povel ventilu         │
regulace v boxu                                                 24V/5A PSU + pojistky
                                                                          │
                                                              silná linka ┴► pohon 24V NC M30×1.5
```

## 3. Dimenzování tenké linky
Měrný odpor mědi ρ = 0.0175 Ω·mm²/m. Smyčka (tam+zpět) při 50 m:

| Průřez | Odpor smyčky |
|---|---|
| 0.1 mm² | 17.5 Ω |
| 0.05 mm² | 35 Ω |

Odběr boxu ze 24 V: průměr ~20 mA, špička (Wi-Fi burst + měřicí cyklus SCD40) ~50 mA po dobu ≤ 1 s; vstupní C 220–470 µF tlumí špičky. Úbytek napětí ve špičce: 0.9–1.8 V. Rozpočet napájecí větve: 12 boxů × 50 mA = 0.6 A (součást 5A PSU). Ochrana: pojistka 0.5 A na kanál.

Rozvod 5 V přímo je vyloučen: špičkový proud ~200 mA na stejné smyčce = úbytek 3.5–7 V, pod napájecí práh ESP32-C6 (brown-out). Stabilizace 24→5 V je tudíž na místě odběru (buck MP1584, nastavit 5.00 V před zapojením).

## 4. Silná linka / ventilová větev
Pohon voskový 24 V DC: odběr ~95–100 mA trvale v činnosti, nájezd trvá minuty (ne milisekundy) — pro relé bez problémů. 12 kanálů paralelně = max ~1.2 A; počítáno i při plném souběhu 12 kanálů, 24V/5A PSU má rezervu. Pojistka 1 A/kanál. Spínací kontakt: relé (varianta A/B, viz §6). Logika: `relé sepnuto = 24 V na pohon = topení` (pohon NC: bez napětí zavřeno).

## 5. Stěnový box — specifikace
| Parametr | Hodnota |
|---|---|
| MCU | ESP32-C6 (Wi-Fi 4/6, 802.15.4 připraven pro budoucí Matter/Thread) |
| T/RH | SHT40, ±0.2 K, I2C (adresa 0x44/0x45) |
| CO₂ | SCD40, ±(40 ppm + 5 %), I2C (0x62), self-calibration zapnutá |
| Napájení | 24 V (tenká linka) → buck 5 V → LDO desky 3V3 |
| I2C piny | GPIO6 SDA, GPIO7 SCL (upravit dle desky, adresy odlišné → netlačí) |
| Firmware | ESPHome, `firmware/esphome/box.yaml` |
| Regulace | bang-bang: ON při T < cíl − 0.3 K, OFF při T > cíl + 0.5 K; min ON 25 min, min OFF 20 min; mrazovka T < 8 °C = vynutit ON |
| Publikace | T/RH/CO2 15 s, heartbeat 30 s, `vyt/jX/valve` retain + republish každé 4 min |
| Přijímá | `vyt/jX/setpoint`, `vyt/jX/preset` (retain) |
| Chování při ztrátě MQTT | reguluje dál podle posledního setpointu |

## 6. Centrála — dvě varianty spínání
### Varianta A — GPIO RPi přímo
Relay board IN pin ← GPIO Pi (tabulka 12 pinů: `docs/setup-prirucka.md §3`), switch platforma GPIO v HA. Výchozí stav po bootu/restartu HA: GPIO input → relé rozepnuta. Krátké výpadky topení při každém restartu HA; elektrická vazba Pi↔board přes společnou GND.

### Varianta B — ESP32 akter (doporučená)
`firmware/esphome/central-actor.yaml`: 12× `switch.gpio` → IN boardu, přijímá `vyt/jX/valve` přímo z brokeru. Restart/reboot HA je pro topení neviditelný (GPIO Pi se nikdy nepoužijí); akter startuje `restore_mode: ALWAYS_OFF` a do 4 min dostane retained stav od boxů. Akter je galvanicky oddělen od 230 V strany (napájení USB/5V, relé opto + vlastní cívkový PSU). Cena dílu ~200 Kč.

Obě varianty: relay board JD-VCC odříznout, cívky napájet z vlastního 5 V/3 A PSU, GND logiky = GND zdroj logiky (Pi u A / ESP32 u B).

## 7. Failsafe matice
| Porucha | Detekce | Akce |
|---|---|---|
| Box bez napájení / mrtvý | HA: sensor `unavailable` 10 min | `switch.vyt_jX` OFF + notification (TTL automation) |
| Restart HA | — | retained MQTT + republish boxů obnoví stav do 4 min; boxy regulují mezitím lokálně |
| Restart varianty B akter | boot 2 s, ALWAYS_OFF | retained topic doplní stav okamžitě při subscribe |
| Výpadek 230 V | — | ventily NC zavřou pružinou; po návratu se systém zrestartuje sám |
| Zkrat na lince | pojistka 1 A / 0.5 A | kanál mrtvý → detekováno jako heartbeat loss |
| Klesající T v místnosti | box | mrazovka < 8 °C vynutí ON |

## 8. Podpůrné systémy
- Broker: Mosquitto add-on, user+heslo (values v `secrets.yaml` / konfiguraci add-onu, ne v repo), `192.168.1.10` pevně (DHCP reservace).
- Přístup zvenčí: Tailscale add-on na Pi; HA bez port forwardingu a bez pevné IP.
- Časovače: HA planner/scény publikují setpoint přes `vyt/jX/setpoint`.
- Notifikace: mobile_app / persistent_notification (offline box, CO₂ > 1400 ppm 5 min, mráz < 8 °C).

## 9. Cena / nákup
MVP (1 místnost) a kompletní 12: **`docs/nakupni-plan.md`**. Kabeláž existuje.

## 10. Open items
| # | Položka | Stav |
|---|---|---|
| 1 | RSSI ve 12 místnostech | změřit v pilotu |
| 2 | Čas otevření/zavření pohonu | stopky v pilotu |
| 3 | Skutečný průřez tenkých linek (0.05 vs 0.1) | proměřit; design počítán s horším případem |
| 4 | Volba varianty A/B centrály | doporučení B, rozhodnout před pilotem |
| 5 | Pilotní místnost | J1 (Můj pokoj) |
