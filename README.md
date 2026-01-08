# WLANThermo BBQ – Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.0.1-informational)
![Lizenz](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024%2B-blue)
![Support](https://img.shields.io/badge/support-Kein%20Support%20enthalten-lightgrey)
![Owner](https://img.shields.io/badge/code%20owner-@MStapelfeldt-purple)

**Version:** 0.0.1  
**Code Owner:** @MStapelfeldt  
**Lizenz:** MIT

> **Hinweis & Haftungsausschluss**
> Dies ist eine Community-Integration für WLANThermo BBQ.  
> **Kein Support** durch den Autor. Forks, Weiterentwicklung und Bugfixes sind willkommen.  
> **Keine Gewähr/Haftung** – Nutzung auf eigene Gefahr.

## Übersicht
Diese Integration verbindet Home Assistant mit einem WLANThermo BBQ (ESP32/Nano/Next). Sie liest Sensordaten und Pitmaster-Status aus und stellt diese als Entitäten bereit.

## Features
- Automatische Erkennung und Einrichtung über die Home Assistant-Oberfläche
- Temperatur-Sensoren für alle Kanäle (Name & Nummer)
- Pitmaster-Sensoren (z.B. Duty Cycle)
- Systeminformationen: RSSI, Batteriestatus, Ladevorgang
- Konfigurierbare Scan-Intervalle
- Unterstützung für verschiedene WLANThermo-Modelle
- Offline-toleranter Start (Entitäten werden verfügbar, sobald das Gerät online ist)

## API-Referenz
- Offizielle HTTP-API: https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP
- Routen **kleingeschrieben** verwenden (`/setpitmaster`, `/setchannels`, `/setpid`, `/setsystem`)
- Für Pitmaster-Writes: vollständige verschachtelte PM-Objekte im Array senden

## Manuelle Installation
1. Repository entpacken
2. `custom_components/wlanthermo_bbq` nach `<HA config>/custom_components/` kopieren
3. Home Assistant neu starten

## Installation über HACS

1. Öffne Home Assistant und gehe zu **Einstellungen → Geräte & Dienste → HACS**.
2. Wähle **Integrationen** und klicke oben rechts auf die drei Punkte (⋮) → **Benutzerdefiniertes Repository**.
3. Gib die URL dieses Repositories ein: `https://github.com/MStapelfeldt/wlanthermo_bbq` und wähle **Integration** als Typ.
4. Suche nach **WLANThermo BBQ** in HACS, installiere die Integration und starte Home Assistant neu.

## Einrichtung
1. Home Assistant öffnen
2. Einstellungen → Geräte & Dienste → **Integration hinzufügen** → **WLANThermo BBQ**
3. Host, Port und ggf. Pfad-Präfix angeben

## Einrichtung der Integration

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. Suche nach **WLANThermo BBQ** und wähle sie aus.
3. Gib die IP-Adresse deines WLANThermo BBQ Geräts ein und wähle ggf. das Modell aus.
4. Schließe die Einrichtung ab und wähle die gewünschte Version, falls mehrere angezeigt werden.

## Entitäten (Beispiele)
- **Pitmaster**: Duty Cycle, Kanal, PID-Status, Sollwert
- **Kanäle**: Temperatur, Alarm, Sensortyp, Min/Max
- **System**: RSSI, Batteriestatus, Ladevorgang

## Konfiguration
Die Integration nutzt einen Konfigurationsdialog (Config Flow). Es sind keine manuellen YAML-Einträge notwendig.

## Entwicklung & Beiträge
Pull Requests, Fehlerberichte und Feature-Wünsche sind willkommen!
