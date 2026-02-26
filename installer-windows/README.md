---
description: Windows Installer bauen (Inno Setup)
---

## Voraussetzungen

- Docker Desktop (muss der Nutzer selbst installieren)
- Inno Setup (ISCC.exe) auf dem Build-PC

## Inhalt

- `docker-for-school.iss` erstellt den Installer
- `start-docker-for-school.ps1` startet nur `modern-homepage` und öffnet den Browser

## Build

1. Inno Setup installieren
2. In diesem Ordner ausführen:

```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\docker-for-school.iss
```

## Ergebnis

- `Docker-for-School-Setup.exe` erscheint in `installer-windows/`

## Nutzung (Schüler)

1. Docker Desktop installieren
2. `Docker-for-School-Setup.exe` installieren
3. Desktop-Icon oder Startmenü: **Docker-for-School**
