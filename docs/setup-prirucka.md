# Setup příručka — co kam nainstalovat, jak nastavit, jak připojit

Verze: 12 místností (mapa `scripts/gen-zone.py → ROOMS`). Dvě varianty centrály: **A = RPi GPIO přímo**, **B = ESP32 akter (doporučeno)**. Obě používají stejný relay board i MQTT tok — liší se jen „rukou, která spíná relé".

## 0. Místnosti
| id | místnost | id | místnost |
|---|---|---|---|
| J1 | Můj pokoj | J7 | Šatna dole |
| J2 | Hostovský | J8 | Koupelna nahoře |
| J3 | Koupelna dole | J9 | Ložnice nahoře |
| J4 | Kuchyně | J10 | Horní paluba |
| J5 | Obývák 2 | J11 | Horní šatna |
| J6 | Předsíň | J12 | Horní pokoj |

## 1. Raspberry Pi 3 — Home Assistant OS
1. Stáhni `haos_ova-x.x.rpi3-64.img.xz` (latest stable) z github.com/home-assistant/operating-system/releases.
2. Zápis na NVMe: USB NVMe box + **Raspberry Pi Imager** (Select OS → Use custom → img) nebo `balenaEtcher`.
3. RPi 3B+ boot z NVMe: vyžaduje aktualizaci EEPROM (XHCI bootloader): bootni jednou z microSD (rpi-imager → Raspberry Pi OS Lite), spusť `sudo rpi-eeprom-update -a` + `sudo rpi-eeprom-config --edit` `BOOT_ORDER=0xf416`, reboot, pak přepiš NVMe a vyhoď SD. (3B bez + nepodporuje USB boot → na 3B dej HAOS na kvalitní microSD kartou a později migruj.)
4. První start: http://homeassistant.local:8123 → onboarding (účet, dům, domov).
5. **Statická IP Pi**: na routeru DHCP reservace podle MAC → `192.168.1.10` (musí sedět v MQTT adresa brokeru v firmware! a v Tailscale to pak jedno).
6. Add-ony (Settings → Add-ons → Store): **Mosquitto broker**, **Tailscale**, **ESPHome**, **Studio Code Server** (volitelně).

## 2. MQTT
1. Mosquitto add-on → Configuration: zapni `custom: {allow_anonymous: false}` a vytvoř user: Settings → System → Users? — nejjednodušší: v `configuration.yaml` HA create `mqtt:` integraci (UI: Settings → Devices → Add Integration → MQTT → host 127.0.0.1) a pro ESP devices přidat usera do add-onu `mosquitto` přes „configuration → password file" nebo addon option `logins: [{username: vyt, password: HESLO}]` (REDACT — vlastní).
2. ESP32 firmware všude: `broker: 192.168.1.10`, user/pass totéž co v boxu, `topic_prefix: esphome/<device>`.
3. Test: `mosquitto_pub` z Terminal&SSH add-onu: `mosquitto_pub -h 127.0.0.1 -u vyt -P 'HESLO' -t vyt/j1/valve -m ON -r` → v HA máš slyšet trigger.

## 3. Centrála varianta A — GPIO RPi (12 relé)
| kanál | GPIO BCM (header pin) | | kanál | GPIO BCM |
|---|---|---|---|---|
| J1 | 4 (pin 7) | | J7 | 7 (pin 26) |
| J2 | 17 (pin 11) | | J8 | 8 (pin 24) |
| J3 | 27 (pin 13) | | J9 | 10 (pin 19) |
| J4 | 22 (pin 15) | | J10 | 9 (pin 21) |
| J5 | 23 (pin 16) | | J11 | 11 (pin 23) |
| J6 | 24 (pin 18) | | J12 | 25 (pin 22) |
| GND | pin 6 nebo 9 → GND logiky relay boardu |

- **Boardy: 3× 8CH TONGLING (vlastněné, JQC-3FF-S-Z 5V, optočleny, header GND/VCC/JD-VCC) — IN nízkoaktivní (LOW = relé SEPNUTÉ).**
- Zapojení: **VCC desky ← 3V3 Pi** (sytí opto-LEDky ~2 mA/kanál), **IN ← GPIO dle tabulky**, **JD-VCC jumper ODŘEZAT**, JD-VCC ← externí 5 V/3 A PSU (cívky), JD-GND ← GND PSU; **GND Pi se s deskou NEPOJUJE** — úplná galvanická izolace.
- HA: Integrace **GPIO** → 12× switch dle tabulky (entity `switch.vyt_j1…j12`), u každého zapnout **Inverted** (LOW=ON).
- ⚠: GPIO 2/3 vyhrazeny I2C pro budoucí expanzi, 14/15 UART.

## 4. Centrála varianta B — ESP32 akter (DOPORUČUJI)
Proč B oproti A na RPi 3 + NVMe:
| | A: RPi GPIO | **B: ESP32 akter** |
|---|---|---|
| restart/reboot HA | GPIO se uvolní → **všechny ventily na 1–2 min spadnou** (NC zavřou), než boxy republishnou | akter žije dál — HA reboot **nezpůsobí žádné přeruštění** |
| elektrické riziko | 3.3 V logika Pi přímo u 24 V/5 V výkonové stage; špatná masa/cívka → riziko pro Pi (128GB NVMe, sídlo HA) | Pi se k relé vůbec nepojí; levná deska (200 Kč) je pojišťka |
| stabilita ovladače | pygpiod na HAOS občas záhadně mizí po updatu kernelu | GPIO v ESPHome = ověřeno 100k+ instalacemi |
| realtime | Linux je ne-RT; spin delay ~ms ok, ale boot 60–90 s | boot 2 s |
| monitoring | — | teplota/deska/heartbeat v ESPHome, OTA upgrade |
| mínus | — | +200 Kč, +1 flash, +1 zařízení na Wi-Fi |
1. V ESPHome add-onu: New device → import z repozitáře (nebo paste) `firmware/esphome/central-actor.yaml`, doplň `secrets.yaml` (wifi, mqtt user/pass), flash USB, pojmenuj `vyt-central`.
2. GPIO→IN mapování dle hlavičky souboru (GPIO4=J1 … GPIO33=J12); boardy zapojeny jako v A — VCC desky na **3V3 ESP32**, GND s deskou nepojuj.
3. `restore_mode: ALWAYS_OFF` + `inverted: true` — akter startuje do bezpečna (GPIO HIGH = relé rozepnuto); boxy mu do 4 min řeknou pravdu.

## 5. Stěnový box ×12
1. ESPHome add-on → copy `firmware/esphome/box.yaml` → `vyt-j1.yaml` … `vyt-j12.yaml` (přepis `substitutions`), u každého i2c piny dle desky, flash USB.
2. Zapojení (vše +/− dle štítků):
```
tenká linka (+,−) →[pojistka 0.5A]→ buck IN(24V)  buck OUT(5V, nastav multimetrem PŘED zapojením!) → C6 5V pin
C6 3V3 → SCD40 VCC + SHT40 VCC ; GND společná ; SDA=GPIO6, SCL=GPIO7 obou čidel (I2C sdílené)
silná linka ← z relay kanálu COM/NO; pohon 24V NC mezi silnou linkou a GND sběrnicí 24V
```
3. Krabice: `hardware/scad/sensor-box.scad`; SCD40 k větrání, anténa nahoře; montáž ve výšce ~1.5 m, mimo radiátor/slunko.

## 6. Uvedení do provozu (checklist)
1. [ ] Pi boot, HA, 3 add-ony jede; router reservace 192.168.1.10
2. [ ] Mosquitto user; `mosquitto_pub` test výše projde
3. [ ] varianta B: `vyt-central` online v ESPHome; ručně: `mosquitto_pub -t vyt/j1/valve -m ON -r` → cvaknutí relé J1, 24 V na výstupu multimetrem
4. [ ] box `vyt-j1` online; T/RH/CO2 entity v HA; number cíl → publish setpointu; `tail` na mosquitto: `vyt/j1/valve` reaguje na změnu T (dálkově: fén/zima)
5. [ ] TTL: odpoj box od napájení → do 10 min relé OFF + notification
6. [ ] měření pilotu: čas otevření pohonu stopkami (zápis do docs/installace-pokoj.md), RSSI všech 12 místností
7. [ ] reproducible: `python3 scripts/gen-zone.py`/`gen-central.py` po změně ROOMS/PINS; commit do tohto repozitáře

## 7. Repository maintenance
Po každé změně: `git add -A && git commit -m "..." && git push` (klíč `id_ed25519_regulace`, core.sshCommand nastaven). Status MVP → plný provoz se značí v README.
