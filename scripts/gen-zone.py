#!/usr/bin/env python3
"""Vygeneruje automations pro zbylych 7 zón podle vzoru J1 (ha/automations-vyt.yaml).
Spust:  python3 scripts/gen-zone.py > ha/automations-vyt-z2-z8.yaml
Potom sloucit do automations, nebo includnout oba soubory."""
import sys

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
        title: "Vytápění {J} offline"
        message: "Box {J} se 10 min neozývá — ventil vypnut. Zkontroluj napájení/Wi-Fi."
'''

out = []
for i in range(2, 9):
    j = f"j{i}"
    out.append(TMPL.format(J=j.upper(), j=j))
sys.stdout.write("# AUTO-GENEROVANO z scripts/gen-zone.py — ruka jen do zdrojoveho vzoru\n")
sys.stdout.write("\n".join(out))
