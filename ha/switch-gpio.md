# HA GPIO switches — ventyly (relé)

## Jak na to v HAOS (doporučená cesta přes UI)
Integrace **GPIO (pygpiod)** je v HA OS dostupná, konfigurace se dělá přes UI:
Settings → Integrations → Add → **GPIO** → pro každý kanál pridať `Switch`:

| Entita (id) | název | GPIO (BCM) |
|---|---|---|
| switch.vyt_j1 | Ventil J1 | 4 |
| switch.vyt_j2 | Ventil J2 | 17 |
| switch.vyt_j3 | Ventil J3 | 27 |
| switch.vyt_j4 | Ventil J4 | 22 |
| switch.vyt_j5 | Ventil J5 | 23 |
| switch.vyt_j6 | Ventil J6 | 24 |
| switch.vyt_j7 | Ventil J7 | 5 |
| switch.vyt_j8 | Ventil J8 | 6 |

⚠️ Jména entit musí sedět s `ha/automations-vyt.yaml` a Lovelace. Pokud GUI navrhne jiné id, uprav automations (nebo naopak).

## Kontrola z terminálu (pro debugging)
```
ha shell   # nebo SSH do HAOS (skill: hermes-vps... ne — zde: HA add-on "Terminal & SSH")
gpiodetect; gpioinfo gpiochip0
# sepnutí kanálu J1:
gpioget/gpioset — nebo přes HA developer tools (spolehlivější)
```

## Chování při restartu HA / výpadku
- restart HA → GPIO se uvolní → relé rozepne → ventily NC zavřou (bezpečné)
- boxy opětovně publikují stav každé 4 min (repub_tick v firmwaru) → relé se obnoví do požadovaného stavu do ~5 minut
- pojistka: automation `vyt_boot_safe_off` při startu HA vypne všechny switche (ať žádný kanál nezůstane viset)

## Fallback: ESP32 v centrále místo GPIO
Kdyby pygpiod na tvém kernelu nedělal co má (viz docs/installace-centrala.md): ESP32-C6 + ESPHome, 8× `output` pin na IN relay boardu, subscribe MQTT `vyt/jX/valve` → `switch`. Zbytek systému (boxy, automations kromě mapování na switch, dashboard) se nemění — automations pak spínají `switch.vyt_jX_equal_esphome_entity`.
