# Instalace — stěnový box (pokoj)

## Stavebnice (1 ks)
- deska: ESP32-C6 supermini (24×25 mm) — pájkou nebo Dupont do 2.54 mm šuplíkové lišty
- buck MP1584/3602 mini: nastavit **na 5.0 V MULTIMETREM PŘED** připojením Čidu!
- SHT40 breakout (4 piny: VCC, GND, SDA, SCL)
- SCD40 breakout (I2C + stejné VCC/GND; nutná ventilace krabice!)
- pojistka 0.5 A v řadě se žílou +, svorky 2p (tenká linka in) + 2p (silná linka nepoužita v boxu)
- 100 µF/35 V elektrolyt na vstup bucku + 100 µF/10 V na výstup (stabilita, špičky)

## Mechanicky
- krabice dle `hardware/scad/sensor-box.scad` (~52×42×26 mm, nebo 3D model dle docs/3d-tisk.md)
- montáž na zeď na místo stávajícího čidla (staré odpojit, svorky ponechat jako „kráva" přechodovka)
- SCD40 + SHT40 u spodních větracích štěrbin, ESP32 antenna u horního okraje (ne nad kovovou krabici!)
- výška instalace ~140–160 cm (výška hlavy v posteli vs. chodba), **mimo přímý sluneční paprsek a nad/dál radiátoru**

## Firmware (ESPHome)
1. V HA: add-on ESPHome → „New device" → `vyt-j1`, deska **ESP32-C6**, Wi-Fi SSID/heslo, MQTT enable.
2. Zkopírovat obsah `firmware/esphome/box.yaml`, nahradit `J1`/`j1` číslem pokoje, zadat MQTT broker (IP Pi, port 1883, user/pass z Mosquitto add-onu).
3. Flash přes USB (C6 supermini: Gilbert? norm. auto-detect; případně drž BOOT při plug-in).
4. OTA: po prvním flashi už se aktualizuje po Wi-Fi.

## Ověření
- v HA Settings → Devices: `vyt-j1` se senzory `teplota`, `vlhkost`, `co2`, binární `valve_request`
- rssi: ESPHome sensor `wifi_signal` — cíl > −70 dBm ve všech 8 místnostech (jinak 2. AP)
- simulace: `number.set` setpoint nad aktuální T → do 1 min `vyt/j1/valve` ON → HA relé sepnuté → 24 V na svorkách
- mrazovka: ochladit čidlo (led ve skle) pod 8 °C → valve ON i bez HA

## Pilot — co změřit a zapsat sem
- [ ] RSSI všech 8 místností:
- [ ] čas otevření pohonu (stopky, 24 V DC): ____ min; zavření (NC bez napětí): ____ min
- [ ] nájezdový proud pohonu (klešťový multimetr): ____ mA
- [ ] teplotní stabilita bez regulace vs s (24 h log): ±____ °C
- [ ] stabilita bucku při Wi-Fi burts (pokles na 5V linii): ____ V
