#!/usr/bin/env python3
"""Generuje kompletni ESPHome yaml pro centralni akter (var B) — 12 kanalu.
Spust: python3 scripts/gen-central.py > firmware/esphome/central-actor.yaml
"""
PINS = ["GPIO4","GPIO16","GPIO17","GPIO18","GPIO19","GPIO21",
        "GPIO22","GPIO23","GPIO25","GPIO27","GPIO32","GPIO33"]

print("""# ============================================================
# Varianta B — centralni akter na ESP32 (AUTO-GENEROVANO
# scripts/gen-central.py — source pravdy = PINS v nem)
# ESP32 devkit v4 + ESPHome; 12x gpio switch (INVERTED) -> IN relay boardu.
#
# Zapojeni (Smart Electronics 8CH boardy, low-trigger, 2x8=16 kanalu):
#   VCC desky      <- ESP32 3V3 (napaji opto-LEDky, ~2 mA/kanal)
#   INx            <- GPIO dle tabulky; LOW = relé SEP (proto inverted)
#   JD-VCC jumper  ODREZAT; JD-VCC <- externi 5V/3A PSU "+"; GND PSU <- JD-GND
#   GND ESP32 se k desce NEPOJUVA — uplna galvanicka izolace optoclennem.
# ============================================================
substitutions:
  device_name: vyt-central
  friendly_name: "Vyt Central"    # prefix entit switch.vyt_central_jX_ventil

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp32:
  board: esp32dev
  framework:
    type: arduino

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password   #[REDACTED]
  ap:
    ssid: "${device_name}-fallback"
    password: "zmen-heslo-zde"      #[REDACTED]

captive_portal:
logger:
api:
  encryption:
    key: "REPLACE_VYGENERUJ_DASHBOARD" #[REDACTED]
ota:
  - platform: esphome
    password: "REPLACE_VYGENERUJ_DASHBOARD" #[REDACTED]

mqtt:
  broker: 192.168.1.10
  username: !secret mqtt_user   #[REDACTED]
  password: !secret mqtt_pass   #[REDACTED]
  topic_prefix: esphome/${device_name}
  on_message:
""")
for i, pin in enumerate(PINS, 1):
    print(f"""    - topic: vyt/j{i}/valve
      then:
        - if:
            condition:
              lambda: 'return x.find("ON") != std::string::npos;'
            then:
              - switch.turn_on: v{i}
            else:
              - switch.turn_off: v{i}""")

print("\nswitch:")
for i, pin in enumerate(PINS, 1):
    print(f"""  - platform: gpio
    name: "J{i} ventil"
    id: v{i}
    pin: {pin}
    inverted: true
    restore_mode: ALWAYS_OFF""")
