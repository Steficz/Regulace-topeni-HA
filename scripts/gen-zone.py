#!/usr/bin/env python3
"""Generator: HA automations + Lovelace karty pro vsech 12 mistnosti.
Ridici seznam ROOMS zde — stejna mapa se pouziva i v docs.
Spust:
  python3 scripts/gen-zone.py > ha/automations-vyt-z2-z12.yaml
  python3 scripts/gen-zone.py --lovelace > ha/lovelace-vyt.yaml
"""
import sys

# (id, slug friendly, nazev) — j1 je rucne v ha/automations-vyt.yaml
ROOMS = [
    ("j1",  "Muj pokoj"),
    ("j2",  "Hostovský"),
    ("j3",  "Koupelna dole"),
    ("j4",  "Kuchyně"),
    ("j5",  "Obývák 2"),
    ("j6",  "Předsíň"),
    ("j7",  "Šatna dole"),
    ("j8",  "Koupelna nahoře"),
    ("j9",  "Ložnice nahoře"),
    ("j10", "Horní paluba"),
    ("j11", "Horní šatna"),
    ("j12", "Horní pokoj"),
]

TMPL = '''- alias: "Vyt {J}: box zadava ventil"
  triggers:
    - trigger: mqtt
      topic: "vyt/{j}/valve"
  actions:
    - choose:
        - conditions: "{{{{ trigger.payload == 'ON' }}}}"
          sequence: [{{action: switch.turn_on, target: {{entity_id: switch.vyt_{j}}}}}]
        - conditions: "{{{{ trigger.payload == 'OFF' }}}}"
          sequence: [{{action: switch.turn_off, target: {{entity_id: switch.vyt_{j}}}}}]
  mode: queued

- alias: "Vyt: TTL heartbeat {J}"
  triggers:
    - trigger: state
      entity_id: sensor.vyt_{j}_teplota
      to: "unavailable"
      for: "00:10:00"
  actions:
    - action: switch.turn_off
      target: {{entity_id: switch.vyt_{j}}}
    - action: persistent_notification.create
      data:
        notification_id: vyt_offline_{j}
        title: "Vytapeni {J} ({name}) offline"
        message: "Box {J} se 10 min neoziva — ventil {name} vypnut. Zkontroluj napajeni/Wi-Fi."
'''

CARD = '''          - type: entities
            title: "{J} · {name}"
            show_header_toggle: false
            entities:
              - entity: sensor.vyt_{j}_teplota
                name: Teplota
              - entity: number.vyt_{j}_cilova_teplota
                name: Cíl
              - entity: sensor.vyt_{j}_co2
                name: CO₂
              - entity: sensor.vyt_{j}_vlhkost
                name: Vlhkost
              - entity: switch.vyt_{j}
                name: "Ventil (ruční override)"
              - entity: sensor.vyt_{j}_rssi
                name: Signál
'''

if "--lovelace" in sys.argv:
    print("# AUTO-GENEROVANO scripts/gen-zone.py --lovelace")
    print("title: Vytápění")
    print("views:")
    print("  - title: Vytápění")
    print("    path: vytapeni")
    print("    icon: mdi:radiator")
    print("    cards:")
    print("      - type: markdown")
    print('        content: "## Regulace 12 pokojů · centrála RPi3 + GPIO (nebo ESP actor) · MVP pilot v běhu"')
    print("      - type: grid")
    print("        columns: 3")
    print("        cards:")
    for j, name in ROOMS:
        print(CARD.format(J=j.upper(), j=j, name=name), end="")
    sys.exit(0)

out = ["# AUTO-GENEROVANO z scripts/gen-zone.py — zdroj pravdy = ROOMS v tomto skriptu\n"]
for j, name in ROOMS[1:]:
    out.append(TMPL.format(J=j.upper(), j=j, name=name))
sys.stdout.write("\n".join(out))
