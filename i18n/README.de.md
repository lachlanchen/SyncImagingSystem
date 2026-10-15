[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` ist ein Python-Arbeitsbereich für synchronisierte Aufnahmeprozesse von Frame-Kameras und Event-Kameras, organisiert um praxisnahe Workflows für EVK/DAVIS und Hikrobot/Haikang Kameras.

## 🧭 Schnellnavigator

| Bereich | Link |
|---|---|
| Haupt-Workflows | [Nutzung](#nutzung) |
| Projekt-Setup | [Installation](#installation) |
| Fehlerbehebung | [Fehlerbehebung](#fehlerbehebung) |
| Beitrag leisten | [Mitwirken](#mitwirken) |
| Support | [❤️ Support](#-support) |

## 📌 Ueberblick

`SyncImagingSystem` ist ein Python-Arbeitsbereich für synchronisierte Aufnahmeprozesse von Frame-Kameras und Event-Kameras.

Es bietet drei zentrale, aktive Workflows:

| Skript | Zweck | Hinweise |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | Vereinheitlichte GUI für Frame + Event | Unterstützt Hikrobot/Haikang Frame-Kamera plus EVK- oder DAVIS-Event-Kamera |
| `unified_event_gui.py` | Reine Event-GUI | EVK + DAVIS Capture mit Auto-Erkennung und Aufzeichnung pro Lauf |
| `save_davis_tcp.py` | DAVIS-Capture-Skript | Unterstützt direkten Kameramodus und DV Viewer Netzwerk-TCP-Modus |

Das Repository enthält außerdem SDK-/Sample-Bundles der Hersteller und frühere Prototypen als Referenz.

## 🚀 Features

| Bereich | Highlights |
|---|---|
| 🎛️ Vereinheitlichte GUI | Vereinte Frame- + Event-GUI mit gerätespezifischen Bedienelementen und gemeinsamem Start-/Stoppen. |
| ⚡ Event GUI | Event-only-GUI mit Mehrgeräte-Anschluss, Vorschau und Aufnahmefunktionen. |
| 📡 DAVIS-Quellen | DAVIS-Aufnahme über direkte Hardware (`INPUT_MODE = "camera"`) oder DV Viewer Netzwerkstream (`INPUT_MODE = "network"`, Standardports `7777/7778`). |
| 💾 Ausgabeformate | Aufnahmeausgaben umfassen `.avi`, `.raw`, `.aedat4` und optional komprimiertes `events.npz`. |
| 🗂️ Lauf-Organisation | Automatische, zeitgestempelte Laufordner unter `recordings/` oder `davis_output/`. |
| 🔧 Steuerung | EVK-Bias-Steuerung in den vereinten GUI-Workflows. |
| 🪞 Frame-Transformation | Vertikales Spiegeln, horizontales Spiegeln und 90-Grad-Drehung in der Dual-Kamera-GUI. |
| 🖥️ Fenster-Management | Hilfslogik für Preview-Fensterplatzierung in Multi-Window-Workflows (insbesondere unter Windows). |

## 🧩 Projektstruktur

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # Haupt-GUI für kombinierte Frame+Event-Aufnahme (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Ältere integrierte Frame+EVK-GUI-Variante
├── unified_event_gui.py                         # Reine Event-GUI für EVK + DAVIS
├── save_davis_tcp.py                            # DAVIS-Aufnahme (Kamera oder DV Viewer TCP)
├── code-legacy/                                 # Historische Skripte/Prototypen
├── evk_sdk/                                     # Prophesee/Metavision SDK-Skripte und Beispiele
├── haikang_sdk/                                 # Hikrobot/Haikang SDK-Bundles und Beispiele
├── i18n/                                        # Übersetzungsverzeichnis
├── recordings/                                  # Laufzeit-Ausgabe (gitignored, bei Nutzung erstellt)
└── davis_output/                                # Laufzeit-Ausgabe für save_davis_tcp.py (gitignored)
```

## 🛠️ Voraussetzungen

### Hardware

- Hikrobot/Haikang Frame-Kamera (für Frame-Workflows).
- EVK-Event-Kamera und/oder DAVIS-Event-Kamera.

### Betriebssystem

- Windows ist der Primärzielbereich für vollständige SDK-Integration von Frame-Kameras sowie für das Vorschaufenster-Positionierungsverhalten.
- Linux/macOS können Teile der Event-Pipeline ausführen, aber vollständige Gleichwertigkeit ist nicht garantiert.

### Python

- Python 3.x.

### Python-Pakete

Installieren Sie die zentralen Laufzeitabhängigkeiten in Ihrer aktiven Umgebung:

```bash
pip install numpy opencv-python dv-processing
```

Für EVK-Workflows installieren Sie die Prophesee Metavision Python-Pakete, die in Ihrer Umgebung verfügbar sind.

Für das Windows-Fenstersteuerungsverhalten in GUI-Vorschauen:

```bash
pip install pywin32
```

## 🧪 Installation

1. Klonen Sie das Repository.
2. Öffnen Sie ein Terminal im Wurzelverzeichnis:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Erstellen/aktivieren Sie Ihre Python-Umgebung.
4. Installieren Sie die Abhängigkeiten (siehe oben).
5. Stellen Sie sicher, dass die benötigten Kamera-SDK-Runtimes/Treiber für Ihre Geräte installiert sind.

Annahme-Hinweis: Die genaue Treiber-/Firmware-Matrix der Anbieter ist im Repository noch nicht vollständig dokumentiert; behalten Sie Ihr lokal funktionierendes SDK-Setup bei.

## ▶️ Nutzung

### 1) Vereinte Frame + Event GUI (empfohlener integrierter Workflow)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Das bietet:

- Auto-Scan für Frame- und Event-Geräte beim Start.
- Frame-Kamerasteuerung: Verbinden, Aufnehmen, Vorschau, Aufzeichnen, Belichtung/Verstärkung.
- Event-Kamerasteuerung: Verbinden, Erfassen, Visualisieren, Aufzeichnen.
- Vereinte Steuerung: Vorschau und Aufzeichnung für beide Seiten gemeinsam starten/stoppen.
- Ausgabeordner- und Dateipräfix-Steuerung in der GUI.

Standard-Ausgabeverhalten:

| Ausgabe | Muster |
|---|---|
| Basisverzeichnis | `recordings/` |
| Laufordner | `<prefix>_<timestamp>/` |
| Frame-Dateien | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Event-Dateien (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Event-Dateien (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` beim Stoppen) |

### 2) Event-only GUI

```bash
python unified_event_gui.py
```

Standardverhalten:

- Basisausgabeverzeichnis: `recordings/`
- Standard-Laufpräfix: `session`
- Geräteerkennung:
  - DAVIS via `dv.io.camera.discover()`
  - EVK als `EVK:auto`, wenn Metavision-Module verfügbar sind
- Aufnahme-Ausgaben:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` und `events.npz` (falls gepufferte Events vorhanden sind)

### 3) DAVIS-Capture-Skript (Kamera oder DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Standardkonstanten im Skript:

| Konstante | Standard |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` für DV Viewer TCP) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

Ausgabeverzeichnisformat:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- Typische Dateien: `events.npz`, `frames.avi`, `output.aedat4`

## ⚙️ Konfiguration

### `save_davis_tcp.py`

Passen Sie die oberen Konstanten in Großbuchstaben an, um Folgendes zu konfigurieren:

- Eingabequelle (`INPUT_MODE`)
- Netzwerk-Endpunkt (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- Aufnahmedauer (`CAPTURE_SECONDS`)
- Ausgabe-Schalter (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- Vorschauverhalten (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Laufzeit-Einstellungen in der GUI beinhalten:

- Ausgabeordner und Dateiname-Präfix
- Frame-Transformationen (Vertikalspiegelung, Horizontalspiegelung, Rotation)
- Frame-Belichtungs- und Gain-Regler
- EVK-Bias-Steuerungen (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) falls unterstützt

### `unified_event_gui.py`

Wichtige Standards (änderbar im Skript):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 💡 Beispiele

### Beispiel A: Direkte DAVIS-Kameraaufnahme für 10 Sekunden

Bearbeiten Sie `save_davis_tcp.py`:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

Ausführen:

```bash
python save_davis_tcp.py
```

### Beispiel B: DAVIS-Daten über DV Viewer via TCP empfangen

Bearbeiten Sie `save_davis_tcp.py`:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

Ausführen:

```bash
python save_davis_tcp.py
```

### Beispiel C: Event-only-Sitzung mit verbundenem EVK und DAVIS

```bash
python unified_event_gui.py
```

Dann in der GUI:

1. Auf `Scan` klicken.
2. Ausgewählte Geräte verbinden.
3. Ausgabeordner/Vorlage setzen.
4. `Record All` nutzen, um synchronisierte Ausgabeordner pro Lauf zu starten.

## 🛠️ Entwicklungshinweise

- Es ist kein Build-System oder Paket-Metadaten definiert (`pyproject.toml`, `requirements.txt`, etc. fehlen aktuell).
- Skripte werden direkt über Python-Entrypoints gestartet.
- Die Konfiguration basiert überwiegend auf Skriptkonstanten und GUI-Steuerelementen, nicht auf CLI-Flags.
- SDK-Verzeichnisse der Anbieter sind absichtlich im Repository enthalten:
  - `evk_sdk/`
  - `haikang_sdk/`
- Ausgabe-/Datenartefakte sind in .gitignore enthalten, einschließlich:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, etc.
- Die Dual-Kamera-GUI enthält Vorschauplatzierungslogik, um Fenster-Pop-in zu reduzieren und zu vermeiden, dass Vorschaufenster die Hauptsteuerung verdecken, besonders unter Windows.

## 🧭 Fehlerbehebung

- Keine Geräte beim Start gefunden.
  - Prüfen Sie Kamerakabel, Stromversorgung und Treiber.
  - Bestätigen Sie Geräteberechtigungen und dass Frame-/Event-Runtimes installiert sind.
- Misch-GUI hängt beim ersten Vorschauframe.
  - Starten Sie mit getrennten Frame- und Event-Geräten, verbinden Sie erneut und scannen Sie danach erneut.
- DAVIS Netzwerkmodus empfängt keine Daten.
  - Prüfen Sie, ob DV Viewer Stream-Ports zu `EVENTS_PORT`/`FRAMES_PORT` passen.
  - Überprüfen Sie Firewall-Regeln für Loopback und UDP/TCP-Traffic im lokalen Modus.
- `.npz` oder `.aedat4` Event-Dateien werden nicht erzeugt.
  - Prüfen Sie, ob die Speicher-Schalter in `save_davis_tcp.py` aktiviert sind.
  - Bestätigen Sie Schreibrechte im Ausgabeverzeichnis.
- Fensterposition springt auf Windows.
  - Stellen Sie sicher, dass `pywin32` installiert ist und Python die erforderlichen Berechtigungen hat.

## 🗺️ Roadmap

Geplante, dokumentations- und nutzerorientierte Verbesserungen (im Repository noch nicht vollständig umgesetzt):

1. Abhängigkeiten in einer festen Anforderungsdatei zentral zusammenfassen.
2. Schlanke CLI-Alternativen für nicht-GUI-Capture-Modi ergänzen.
3. SDK- und Firmware-Kompatibilitätsmatrix erweitern.
4. Sichere, hardwareunabhängige Tests für Projektkonstanten und Dateilayout-Logik ergänzen.

## 👥 Mitwirken

Beiträge sind willkommen.

1. Beschränken Sie Änderungen auf Script-Workflows und vermeiden Sie die Änderung des Laufzeitverhaltens der Aufnahme, außer wenn ein Kamerapfad absichtlich angepasst wird.
2. Bewahren Sie den bestehenden Kamerathread-Lebenszyklus und das Output-Ordnerlayout, sofern keine klare Begründung in der Änderung besteht.
3. Validieren Sie geänderte Pfade/Skripte mit mindestens einem vollständigen lokalen Aufnahme-Lauf.
4. Fügen Sie Annahmen und den Hardware-Kontext in die PR-Beschreibung ein.

## 📩 Kontakt

Wenn Sie Integrationshilfe für ein bestimmtes Hardware-Setup benötigen, geben Sie bitte Kamera-Modell, Betriebssystem und die genaue Fehlerausgabe in Ihrer Issue-Beschreibung an.

## 📜 Lizenz

Zur Zeit ist im Repository-Root keine Lizenzdatei vorhanden. Fügen Sie eine `LICENSE`-Datei hinzu, bevor Sie öffentlich verteilen.


## ❤️ Support

<!-- support:start -->
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)
[![LazyingArt Support](https://img.shields.io/badge/LazyingArt-Support-0EA5E9?style=for-the-badge)](https://chat.lazying.art/donate)
[![PayPal Support](https://img.shields.io/badge/PayPal-Support-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen)
[![Stripe Support](https://img.shields.io/badge/Stripe-Support-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
<!-- support:end -->
