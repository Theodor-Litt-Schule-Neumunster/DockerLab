# docker-for-school
Docker for School ist eine vor konfigurierte Docker-Umgebung für Schulen, mit der Entwicklungs- und Programmierumgebungen schnell und einheitlich bereitgestellt werden können. Sie ermöglicht plattformunabhängiges Arbeiten ohne aufwendige Installation und sorgt für reproduzierbare Setups im Unterricht, bei Projekten und Workshops.

## Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [Schnellstart](#schnellstart)
- [Verfügbare Dienste](#verfügbare-dienste)
  - [Homepage](#homepage)
  - [VS Code Server](#vs-code-server)
  - [Windows Server 2022](#windows-server-2022)
  - [Debian](#debian)
- [Verwaltung](#verwaltung)
- [Konfiguration](#konfiguration)

## Voraussetzungen

Stellen Sie sicher, dass auf Ihrem System die folgenden Anwendungen installiert sind:
- Docker
- Docker Compose

## Schnellstart

1. Klonen Sie dieses Repository oder laden Sie die Dateien herunter.
2. Öffnen Sie ein Terminal im Hauptverzeichnis des Projekts.
3. Führen Sie den folgenden Befehl aus, um alle Dienste im Hintergrund zu starten:
   ```bash
   docker-compose up -d
   ```
4. Öffnen Sie Ihren Webbrowser und navigieren Sie zu `http://localhost:3000`, um auf das Dashboard zuzugreifen.

## Verfügbare Dienste

### Homepage

Ein zentrales Dashboard, das eine Übersicht über alle laufenden Dienste bietet und den Zugriff darauf erleichtert.

- **URL:** `http://localhost:3000`
- **Konfiguration:** Die Konfigurationsdateien befinden sich im Ordner `./homepage-config`.

### VS Code Server

Eine webbasierte Instanz von Visual Studio Code, die eine vollständige Entwicklungsumgebung im Browser bereitstellt.

- **URL:** `http://localhost:8080`
- **Projektdaten:** Der Ordner `./vscode-data` wird in den Container eingebunden und enthält Ihre Projektdateien.
- **Konfiguration:** Benutzereinstellungen für VS Code werden im Ordner `./vscode-config` gespeichert.

### Windows Server 2022

Eine virtuelle Maschine mit Windows Server 2022, die über RDP oder eine Weboberfläche zugänglich ist.

- **RDP-Zugang:** Verbinden Sie sich mit einem RDP-Client Ihrer Wahl mit der Adresse `localhost:3390`.
- **Web-Oberfläche:** `http://localhost:8006`
- **Daten:** Der Ordner `./windowsserver2022` wird als Speicher für die virtuelle Maschine verwendet.

### Debian

Eine virtuelle Maschine mit dem Betriebssystem Debian.

- **Web-Oberfläche:** `http://localhost:8007`
- **Daten:** Der Ordner `./debian` wird als Speicher für die virtuelle Maschine verwendet.

## Verwaltung

- **Alle Dienste starten:**
  ```bash
  docker-compose up -d
  ```
- **Alle Dienste stoppen:**
  ```bash
  docker-compose down
  ```
- **Logs anzeigen:**
  ```bash
  docker-compose logs -f <service_name>
  ```
  (z.B. `docker-compose logs -f vscode`)

## Konfiguration

Jeder Dienst speichert seine Daten und Konfiguration in lokalen Ordnern, die im `docker-compose.yml` unter `volumes` definiert sind. Dies ermöglicht es Ihnen, Anpassungen vorzunehmen und sicherzustellen, dass Ihre Daten auch nach einem Neustart der Container erhalten bleiben.

## Lizenz

- Windows
  > https://github.com/dockur/windows
  > Lizenz: GNU General Public License v3.0 (GPL-3.0)
  > Copyright © dockur contributors

- Qemu
  > https://github.com/qemus/qemu
  > Lizenz: GNU General Public License v2.0 (GPL-2.0)
  > Copyright © QEMU contributors

- Homepage
  > https://github.com/gethomepage/homepage
  > Lizenz: GNU General Public License v3.0 (GPL-3.0)
  > Copyright © Homepage Contributors
