# Design v0.4 — kompletní specifikace

## 1. Systémové rozhodnutí
| Rozhodnutí | Hodnota | Proč |
|---|---|---|
| Mózga + výkon | RPi 3 (HA) + GPIO + 16CH relay board | znovuvyužití existujícího HW; žádné další zařízení v centrále; HA má GPIO rovnou |
| Senzor + regulace | ESP32-C6 stěnový box ×8 | regulace na měřicím místě; nezávislost na HA; C6 = cesta k Thread/Matter do budoucna |
| Teplota/vlhkost | SHT40 (±0.2 °C, I2C) | nejlepší poměr cena/přesnost; alternativy AHT10 (levnější, ±0.3), BME280 (přidaný tlak — k ničemu) |
| CO₂ | SCD40 (photoacoustic, I2C, ±40 ppm+5 %) | malý, levný (~700 Kč Ali / 900–1200 CZ), minimální odběr; SCD30 větší+dražší bez přínosu; MH-Z19B drift+UART |
| Napájení boxů | 24 V po stávající tenké lince → buck MP1584 na 5 V → AMS1117/LDO 3V3 | fyzika tenkého drátu (viz README); 5 V rozvod = brown-out |
| Ventily | voskový pohon 24 V **NC** M30×1.5 | shodné s testovacím kusem; NC = bez napětí zavřeno (viz failsafe) |
| Komunikace | Wi-Fi 2.4 + MQTT | 10 klientů; RSSI ověří pilot; 2. AP za 600 Kč když potřeba |
| Remote | Tailscale add-on | bez pevné IP, bez otevřených portů |

## 2. Centrála — RPi 3 + GPIO
### Připojení (detail v docs/installace-centrala.md)
- 2× 8CH relay board (nebo 1× 16CH), **JD-VCC jumper ODŘEZAT**, cívky napájené z vlastního 5 V/3 A PSU (společná GND s Pi!)
- IN piny ← GPIO BCM: `4, 17, 27, 22, 23, 24, 5, 6` (J1–J8)
- 24 V/5 A PSU → pojistky 1 A/kanál → NOVY kontakt relé → silná linka → pohon
- Tenké linky → 24 V přes pojistky 0.5 A/kanál přímo (nespínají se, jen napájejí boxy)

### Pozn. ke spolehlivosti relé
Voskový pohon má nájezdový proud ~0.3 A po dobu několika sekund — pro relé (10 A kontakt) trivialita. Spínacích cyklů bude max ~50/den celkem → mechanické relé vydrží roky (100k+ cyklus/kanál).

## 3. Stěnový box
### Osazenka
| Díl | Kde | Cena Kč |
|---|---|---|
| ESP32-C6 (supermini / dev) | Ali / CZ e-shop | 150–250 |
| SHT40 breakout | Ali | 60–120 |
| SCD40 breakout | Ali (~700) / Mouser (~1200) | 700–1200 |
| buck MP1584 3602 mini (24→5V) | Ali | 20–40 |
| LDO 3.3V (součást C6 dev desky, nebo ME6211) | — | 0–15 |
| pojistka 0.5 A + držák, svorky 2p×2 | CZ hooby | 40 |
| krabice 3D tisk (viz hardware/scad) | — | ~30 filament |
| **celkem / ks** | | **~1000–1600** |

### Chování (firmware/esphome/box.yaml)
- měří T/RH/CO₂, publikuje every 15 s + heartbeat 30 s
- lokální bang-bang: ON při T < cíl − 0.3 °C, OFF při T > cíl + 0.5 °C; min ON 25 min / min OFF 20 min
- mrazovka: T < 8 °C → vynutit ON (přes HA relé)
- cíl + režim dostává z HA přes MQTT (`vyt/jX/setpoint`, `vyt/jX/preset`); při ztrátě MQTT drží poslední
- publikuje požadavek ventilu: `vyt/jX/valve` = ON/OFF (retained)

## 4. Home Assistant
- **HA OS na RPi 3** (3B i 3B+), Mosquitto add-on, Tailscale add-on
- relé = `switch` přes GPIO (ha/switch-gpio.yaml); fallback řešení v docs/installace-centrala.md
- automation ha/automations-vyt.yaml: MQTT→switch map, TTL heartbeat failsafe, mrazový trickle, notifikace offline, CO₂ alert (>1400 ppm), OKNO detekce (volitelně)
- planner: Helpers → Schedule pro každý pokoj (Comfort/Eco/Away/Sleep), presety → MQTT setpoint
- recorder: retention 2 dny (SD/SSD disk!), system_monitor hlídání

## 5. Bezpečnost / selhání
| Scénář | Chování |
|---|---|
| Výpadek 230 V | ventily zavřou pružinou (NC) — dům chladne; po návratu HA restartuje, boxy se znovu připojí, logika naběhne |
| Výpadek WiFi boxu | box reguluje dál LOKÁLNĚ (relé zůstává v posledním stavu); HA po 30 min notifikuje + sepnou mrazový trickle |
| Výpadek HA / restart | HA po startu smaže TTL stavy; boxy hlásí heartbeat do 30 s; relé setne dle posledního retained MQTT — retence `valve` topicu to drží konzistentní |
| Zkratl / pojistka | 1 A/ventil, 0.5 A/senzor — pojistky v centrále, přehledné v krabici |

## 6. Open items (do pilotu)
1. Měření RSSI ve všech 8 místnostech (telefon: app WiFi Analyzer) → rozhodnout 2. AP
2. Stopky: čas otevření/zavření tvého 24V NC pohonu → doladit min ON/OFF
3. Ověřit, že tenká linka je Cu (ne telefonní pásek CuCl — při 0.05 měď OK, CuCl by šlo méně)
4. Pilotní pokoj: který?
5. Kotel: ponecháme bez zásahu; volitelně později boiler-demand kontakt (relé kanál zbývá — 16relé board, 8 použitých, 8 volných!)
