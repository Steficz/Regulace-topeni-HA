# Instalace — centrála (RPi 3 + GPIO + relay board)

## Co kde bude
V centrální krabici (3D tisk nebo DIN krabička 200×120×75):
- RPi 3 s HA OS (SSD/USB disk, ne SD karta — dlouhodobý provoz!)
- napájecí 5 V/3 A USB PSU (pro Pi) + druhý 5 V/2–3 A PSU pro cívky relé
- 24 V/5 A PSU (Mean Well HDR-150-24 nebo levnější Ali) pro ventily + tenké linky
- 2× 8CH relay board (nebo 1× 16CH) — musí mít **optočlenový vstup** a podporu 3.3 V logiky
- lišta pojistek: 8× 1 A (ventily) + 8× 0.5 A (senzory), nebo automat. jističky 6A/10A
- svorkovnice: WAGO 2p×16 + ochranné svorky

## GPIO pinout
Kanály J1–J12 a přiřazení 12 GPIO: **canonical tabulka je `docs/setup-prirucka.md §3`** (tento dokument ji neopakuje, ať se nerozjíždějí).

## Zapojení relé boardu
1. **ODŘEZAT jumper JD-VCC** (oddělit cívky od logiky = optočlenová izolace funguje).
2. VCC (strana cívky) ← externí 5 V/2–3 A PSU `+`; GND (strana cívky) ← PSU `−`.
3. GND (strana logiky IN) ← **GND Raspberry Pi** (pin 6 nebo 9) — společná reference!
4. IN0..IN11 ← GPIO dle tabulky (ploché kabely / Dupont).
5. COM/NF kontakt relé do série s 24 V větví: `PSU 24V+ → pojistka 1A → relé COM → relé NO → silná linka žíla A → pohon → silná linka žíla B → PSU GND`.
6. Tenká linka: `PSU 24V+ → pojistka 0.5 A → žíla → box; žíla zpět → PSU GND` (nespíná se!).

> **Logika sepnutí:** HA GPIO switch sepnutí = relé ON = 24 V na pohon. NC voskový pohon: bez napětí zavřeno, s napětím otevírá → relé ON = topení ON. Při bootu Pi jsou GPIO input/pull-down → logika optočlenu nedodává signál → relé rozepnuto = bezpečný stav. Po startu HA navíc pojistka automation „vše OFF". Test: odpoj logiku, změřit kontinuitu na 24V svorkách — musí být otevřeno.

## Fallback, kdyby GPIO integration vrtala
HA OS `switch.gpio` (pygpiod) obvykle funguje bez problémů; alternativa bez měnění designu: **ESP32-C6/C3 v centrále jako „aktér"** s ESPHome (subscribe `vyt/jX/valve` → GPIO output → relay board). Firmware je připraven (viz git history, variant `central-actor.yaml`); MQTT topic se nemění.

## Krok za krokem
1. Nabootovat HA OS na RPi3 z SSD, doinstalovat add-ony: Mosquitto, Tailscale, ESPHome.
2. V `configuration.yaml` include soubory z `ha/` (switch-gpio, automations, lovelace resource).
3. Restart HA → 8 switch entit `switch.vyt_j1…j8`; ručně otestovat each s multimetrem na 24V svorkách.
4. Připojit jeden testovací pohon na J1, pojistka 1A.
5. V HA: `developer tools → actions → switch.turn_on switch.vyt_j1` → poslech cvaknutí + 24V na výstupu + stopky čas otevření pohonu.
6. Teprve pak krabice a montáž na zeď.
