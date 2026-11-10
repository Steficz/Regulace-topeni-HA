# Instalace — centrála (RPi 3 + GPIO + relay board)

## Co kde bude
V centrální krabici (3D tisk nebo DIN krabička 200×120×75):
- RPi 3 s HA OS (SSD/USB disk, ne SD karta — dlouhodobý provoz!)
- napájecí 5 V/3 A USB PSU (pro Pi) + druhý 5 V/2–3 A PSU pro cívky relé
- 24 V/5 A PSU (Mean Well HDR-150-24 nebo levnější Ali) pro ventily + tenké linky
- 3× 8CH relay board TONGLING (vlastněné; optočleny, JD-VCC header, cívky 5 V)
- lišta pojistek: 8× 1 A (ventily) + 8× 0.5 A (senzory), nebo automat. jističky 6A/10A
- svorkovnice: WAGO 2p×16 + ochranné svorky

## GPIO pinout
Kanály J1–J12 a přiřazení 12 GPIO: **canonical tabulka je `docs/setup-prirucka.md §3`** (tento dokument ji neopakuje, ať se nerozjíždějí).

## Zapojení relé boardů (vlastněné 3× 8CH TONGLING JQC-3FF-S-Z, optočleny, low-trigger)

> Na bench fotkách je žlutý jumper JD-VCC↔VCC nasazený a VCC napájená z Pi 5V s společnou GND — **takto to pro 3.3V logiku nepoužívat** (HIGH 3.3V na 5V opto vstupu může relé ani vypnout). Přepoj dle bodů 1–4.
1. **ODŘEZAT jumper JD-VCC** (oddělit cívkovou větev od logiky).
2. JD-VCC ← externí 5 V/3 A PSU `+`; JD-GND ← PSU `−` (strana cívek).
3. VCC desky (logika) ← **3V3 Raspberry Pi** (sytí opto-LEDky ~2 mA/kanál). **GND Pi se s deskou nepojuje** — úplná galvanická izolace.
4. IN0..IN11 ← GPIO dle tabulky. **Logika je LOW = relé SEPNUTÉ** → HA GPIO switch i akter nastaven `inverted`.
5. Kontrola bezpečného startu: VCC desky zapoj, IN nech viset → relé MUSÍ být rozepnutá (desky mívají pull-up na IN; když ne, přidej na IN R 10k k VCC desky).
6. COM/NO kontakt relé do série s 24 V větví: `PSU 24V+ → pojistka 1A → relé COM → relé NO → silná linka žíla A → pohon → silná linka žíla B → PSU GND`.
7. Tenká linka: `PSU 24V+ → pojistka 0.5 A → žíla → box; žíla zpět → PSU GND` (nespíná se!).

> **Logika sepnutí:** HA switch ON = GPIO LOW = opto vodi = relé sepnuto = 24 V na pohon → topení (NC voskový pohon bez napětí zavře). Při bootu Pi jsou GPIO input + pull-up na IN → relé rozepnuta = bezpečný start. Po startu HA zajišťuje bezpečný stav automation „boot safe off".

## Fallback, kdyby GPIO integrace vrtala
HA OS GPIO (pygpiod) obvykle funguje; celý design se nemění:* **ESP32 akter** (`firmware/esphome/central-actor.yaml`, varianta B) — MQTT topics, automations i dashboard zůstávají.

## Krok za krokem
1. Nabootovat HA OS na RPi3 z NVMe, doinstalovat add-ony: Mosquitto, Tailscale, ESPHome.
2. V `configuration.yaml` include soubory z `ha/` (switch-gpio, automations, lovelace resource).
3. Restart HA → 8 switch entit `switch.vyt_j1…j8`; ručně otestovat each s multimetrem na 24V svorkách.
4. Připojit jeden testovací pohon na J1, pojistka 1A.
5. V HA: `developer tools → actions → switch.turn_on switch.vyt_j1` → poslech cvaknutí + 24V na výstupu + stopky čas otevření pohonu.
6. Teprve pak krabice a montáž na zeď.
