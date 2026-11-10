# Regulace vytápění — 8 pokojů (Řízeno Home Assistantem)

**Stav: design v0.4 schválený architektura — HW pilot připraven na náklistek.**
Dům: 2 patra, ~200 m²/patro, centrála v přízemí. Na každý pokoj existují 2 linky z centrály:
- **silná 2×0.5–0.75 mm²** → k radiátoru (pro pohon ventilu)
- **tenká 2×~0.1 mm² (0.05–0.1)** → do místa starého prostorového čidla (napájení stěnového boxu)

## Architektura v0.4 — stručně

```
[Stěnový box ×8]                       [Centrála — RPi 3]
ESP32-C6 + SHT40 + SCD40               HA + Mosquitto + Tailscale
buck 24→5V (z tenké linky)             GPIO ──► 16CH relay board ──► 24V/5A PSU
regulace běží ZDE (bang-bang)                      │ jističe 1A/kanál
        │                                          │
        └── Wi-Fi / MQTT ──► HA ──► automation ──► switch (relé) ──► silná linka ──► pohon 24V NC M30x1.5
```

- **Regulace (hystereze, mrazovka) žije na stěnovém boxu** — správné měřicí místo, nezávislost na HA.
- **Povel ventilu**: box publikuje MQTT `vyt/jX/valve` → HA automation přepne relé na GPIO → 24 V jde po silné lince do voskového pohonu.
- **Žádná centrální ESP32** — výkonná stage = RPi 3 GPIO + reléový board (znovuvyužití hardwaru, který už máš).
- **Failsafe**: heartbeat boxu 30 s; HA hlídá TTL (10 min bez TL = relé OFF + notifikace); výpadek napájení = NC pružinou zavře; mrazový trickle v HA automation.

## Proč 24 V po tenké lince a buck v každém boxu (ne 5 V rozvod)

| | 5 V rozvod | 24 V rozvod + buck 60 Kč |
|---|---|---|
| Proud boxu (špička ~1 W) | ~200 mA | ~45 mA |
| Úbytek na 35 Ω (0.05 mm²/50 m) | **7 V → na boxu 0 V, brown-out** | 1.6 V → 22.4 V ✓ |
| Zdroj | RPi 5V pin (~1 A budget, šumový) | nezávislý PSU + jistič/kanál |

Buck (MP1584/3602 mini) stojí 20–40 Kč — to není položka, za kterou stojí riskovat nestabilní systém. 5 V rozvod je na tomto drátě fyzikálně vyloučený.

## Proč Wi-Fi, ne Thread/Zigbee
- ESP32-C6 umí Wi-Fi + 802.15.4 (Thread) zároveň, ale **Wi-Fi klient nemůže být redundance Thread mesh bez border routeru** (Thread provoz nemůže být překládán do Wi-Fi klientů „zadarmo“); vyžadoval by BR (SkyConnect/RPi dongle) a složitost navíc.
- 10 zařízení na 2.4 GHz z routeru v přízemí, nejvzdálenější ~50 m vzduchem přes 2 patra: rozhodne pilot **měřením RSSI**; slabé místo se řeší druhým AP/mesh uzlem za ~600 Kč — levnější a jednodušší než jakýkoliv mesh protokol.
- C6 proti C3 má připravenou cestu k Thread/Matter, kdybys chtěl v budoucnu rozšíření (okna, pohyby) — firmware se jen přidá.

## Složka tohoto repozitáře
```
README.md                  ← toto
docs/design-v0.4.md        ← kompletní design (nahrazuje v0.3)
docs/installace-centrala.md    ← RPi3 + relé + 24V PSU + jističe + GPIO pinout
docs/installace-pokoj.md   ← stavba stěnového boxu, pilot, měření dynamiky
docs/3d-tisk.md            ← parametrické modely (hardware/scad) + hotové alternativy
firmware/esphome/box.yaml  ← ESPHome firmware stěnového boxu (šablona ×8)
ha/switch-gpio.yaml        ← relé jako HA switch (pygpiod)
ha/automations-vyt.yaml    ← mapování MQTT→relé, TTL failsafe, mrazovka, notifikace
ha/lovelace-vyt.yaml       ← dashboard (dark, 8 zón + CO2 + stavy ventilů)
hardware/scad/*.scad       ← krabice na 3D tisk (senzorový box, ventil, centrála)
```

## Cena (kabeláž existuje — 0 Kč)
| Položka | ks | Kč celkem |
|---|---|---|
| Stěnový box (C6 + SHT40 + SCD40 + buck + příslušenství) | 8 | 5 600–7 200 |
| Pohon 24 V NC M30×1.5 | 8 | 2 400–4 000 |
| Relé board 16CH + 5V PSU + jističe + svorkovnice + PSU 24V/5A | 1 | ~1 700 |
| 3D tisk (filament) | — | ~300 |
| **Celkem** | | **~10–13 tis. Kč** |

## Roadmap
1. [ ] Nákup dílů (odkazy v docs/design-v0.4.md)
2. [ ] Pilot 1 pokoj: box + relay kanál + HA automation + Tailscale; měření RSSI a časů pohonu
3. [ ] Doladit parametry z pilotu → ostatní 3 pokoje
4. [ ] Plné nasazení, plány/režimy, notifikace, doladění dashboardu
5. [ ] Volitelně: 2. AP, UPS pro centrálu, boiler-demand kontakt
