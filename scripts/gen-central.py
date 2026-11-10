#!/usr/bin/env python3
"""Generuje kompletni ESPHome yaml pro centralni akter (var B) — 12 kanalu.
Spust: python3 scripts/gen-central.py > firmware/esphome/central-actor.yaml
"""
PINS = ["GPIO4","GPIO16","GPIO17","GPIO18","GPIO19","GPIO21",
        "GPIO22","GPIO23","GPIO25","GPIO27","GPIO32","GPIO33"]

print("""# ============================================================
# Varianta B — centralni akter na ESP32 (AUTO-GENEROVANO
# scripts/gen-central.py — source pravdy = PINS v nem)
# ESP32 devkit v4 + ESPHome; 12x gpio switch -> IN relay boardu.
# Vyhoda: pri restartu/rebootu HA (a) GPIO Pi nespadnou do inputu,
# (b) topeni bezima dal; RPi je "mozna", ale ne elektricka cesta.
#
# Zapojeni: relay board JD-VCC ODREZAT; cevky z vlastniho 5V/3A PSU;
# GND logiky relay boardu === GND ESP32 (spolecny zem, napr. přes USB
# napajeci GND, nebo kabelem). INx <-> GPIO dle tabulky níže.
# ============================================================
substitutions:
  device_name: vyt-central
  friendly_name: "Centrála — akter ventilů"

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
    inverted: false
    restore_mode: ALWAYS_OFF""")
