# Rozdělení HW na lokalitě (topena + UniFi)

Stav naměřeno 2026-11-10 (Pi3 = 100.86.188.1, RPi 3B 1GB, SSD 235G, uptime 16d):
- UniFi Network Application: java 229 MB + mongod 76 MB ≈ **305 MB RSS**
- volná RAM: 354 MB; swap používán 747 MB; na Pi3 běží i dockerd + tailscaled
- ESPHome kompilace firmware: špička ~1 GB+ (přes 1 GB RAM Pi3 neprojde bez selhání)

## Varianta 1 (doporučeno): Z2W = UniFi, Pi3 = čistě HAOS
| Zařízení | Role | Pozn. |
|---|---|---|
| Pi Zero 2 W (aarch64, 512 MB) | UniFi Controller | arm64 build; `JAVA_OPTS=-Xmx384m`; zapnout zram (raspi-config); high-endurance karta nebo USB; idle ~0.7 W |
| RPi 3B 1GB + SSD | HA OS (heating, MQTT, Tailscale) | plná RAM pro HA; firmware compile externě (viz níže) |
| laptop/PC | ESPHome compile + USB flash | `esphome run` z PC, OTA aktualizace pak už jen 30MB binárky |

Postup migrace UniFi:
1. Na Pi3: Settings → System → Backup → stáhnout .unifi backup (nebo `/usr/lib/unifi/data/backup`).
2. Z2W: Raspberry Pi OS 64-bit Lite → `apt install unifi` z repo Ubiquiti (arm64), nebo docker `jacobalberty/unifi:latest` s `-e UNSPEC_JAVA_OPTS="-Xmx384m"`.
3. V controlleru restore backupu → AP se adoptují samy (APy bez controlleru fungují dál, výpadek nevadí).
4. Přepsat DNS/DHCP/adopt adresy: APy musí vidět controller → nastavit `inform_url/adopt` na IP Z2W (v UI: Settings → System → Advanced → Controller hostname/IP), nebo DHCP option 43.
5. Na Z2W nainstalovat tailscale (stejný tailnet), přesměrovat záložku/panely z `100.86.188.1:8443` na novou IP.
6. Pi3 po ověření: `systemctl disable unifi` → nainstalovat HAOS (SSD se smaže, backup Pi3 předtím).

## Varianta 2 (bez nákupu/posunu): vše na Pi3 v Dockeru
- Pi3 zůstane, HA pojede jako **HA Container** (ne HAOS) vedle UniFi kontejneru, mem limitů:
  `unifi: mem 700m`, `homeassistant: mem 400m`, `mosquitto: mem 64m` + zram + `vm.swappiness=10`
- Omezení, která musíš akceptovat: **žádný ESPHome add-on** (compile na PC), žádné heavier integrations, retention recorder 1 den, update HA = krátké swapové dušení.
- Risk: jeden blast radius — výpadek Pi = HA i síťová správa. Výpadek zhasne dashboard; topení fail-safe: NC ventily zavřou pružinou.
- Vhodné jako dočasné řešení před upgrade na Pi4/Pi5 (2-4GB).

## Cesta ven, až budou peníze
Pi 4 4GB/ Pi 5 = HA+topení, Z2W = UniFi. Případně UCG-Ultra (~1 200 Kč) hostuje UniFi nativně a Pi se uvolní úplně.
