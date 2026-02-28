[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## Überblick

`SyncImagingSystem` ist ein Python-Workspace für synchronisierte Frame-Kamera- und Event-Kamera-Aufnahme.

Es bietet drei aktive Haupt-Workflows:

1. `DualCamera_separate_transform_davis+evk.py`: einheitliche GUI für Frame- + Event-Aufnahme (Hikrobot/Haikang-Frame-Kamera + EVK- oder DAVIS-Event-Kamera).
2. `unified_event_gui.py`: reine Event-GUI für EVK- und DAVIS-Geräte.
3. `save_davis_tcp.py`: DAVIS-Aufnahmeskript mit direktem Kameramodus und DV-Viewer-TCP-Netzwerkmodus.

Das Repository enthält außerdem Vendor-SDK-/Sample-Bundles und historische Prototypen als Referenz.

## Funktionen

| Bereich | Highlights |
|---|---|
| 🎛️ Einheitliche GUI | Einheitliche Frame- + Event-Aufnahme-GUI mit gerätespezifischen Bedienelementen und gemeinsamen Start/Stopp-Steuerungen. |
| ⚡ Event-GUI | Reine Event-GUI mit Connect/Preview/Record für mehrere Geräte. |
| 📡 DAVIS-Quellen | DAVIS-Aufnahme von direkter Hardware (`INPUT_MODE = "camera"`) oder DV-Viewer-Netzwerkstream (`INPUT_MODE = "network"`, Standardports `7777/7778`). |
| 💾 Ausgabeformate | Aufnahmeausgaben umfassen `.avi`, `.raw`, `.aedat4` und optional komprimiertes `events.npz`. |
| 🗂️ Lauf-Organisation | Automatische, zeitgestempelte Run-Ordner unter `recordings/` oder `davis_output/`. |
| 🔧 Steuerung | EVK-Bias-Steuerungen in den einheitlichen GUI-Workflows. |
| 🪞 Frame-Transformation | Vertikales Flippen, horizontales Flippen und 90-Grad-Rotation in der Dual-Kamera-GUI. |
| 🖥️ Fensterverwaltung | Hilfslogik zur Positionierung von Vorschaufenstern für Multi-Window-Workflows (insbesondere unter Windows). |

## Projektstruktur

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # Haupt-GUI für kombinierte Frame+Event-Aufnahme (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Ältere integrierte Frame+EVK-GUI-Variante
├── unified_event_gui.py                         # Reine Event-GUI für EVK + DAVIS
├── save_davis_tcp.py                            # DAVIS-Aufnahme (Kamera oder DV Viewer TCP)
├── code-legacy/                                 # Historische Skripte/Prototypen
├── evk_sdk/                                     # Prophesee/Metavision-SDK-Skripte und Samples
├── haikang_sdk/                                 # Hikrobot/Haikang-SDK-Bundles und Samples
├── i18n/                                        # Übersetzungsverzeichnis
├── recordings/                                  # Laufzeitausgabe (gitignored, wird bei Nutzung erstellt)
└── davis_output/                                # Laufzeitausgabe für save_davis_tcp.py (gitignored)
```

## Voraussetzungen

### Hardware

- Hikrobot/Haikang-Frame-Kamera (für Frame-Workflows).
- EVK-Event-Kamera und/oder DAVIS-Event-Kamera.

### Betriebssystem

- Windows ist das primäre Ziel für vollständige Frame-Kamera-SDK-Integration und Vorschaufenster-Positionierung.
- Linux/macOS können Teile der Event-Pipeline ausführen, aber vollständige Funktionsparität ist nicht garantiert.

### Python

- Python 3.x.

### Python-Pakete

Installiere die Kern-Laufzeitabhängigkeiten in deiner aktiven Umgebung:

```bash
pip install numpy opencv-python dv-processing
```

Für EVK-Workflows installiere die in deiner Umgebung verfügbaren Prophesee-Metavision-Python-Pakete.

Für Windows-Fenstersteuerung in GUI-Vorschauen:

```bash
pip install pywin32
```

## Installation

1. Repository klonen.
2. Ein Terminal im Repository-Root öffnen:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Python-Umgebung erstellen/aktivieren.
4. Abhängigkeiten installieren (siehe oben).
5. Sicherstellen, dass die benötigten Kamera-SDK-Laufzeiten/Treiber für deine Geräte installiert sind.

Hinweis zur Annahme: Die exakte Vendor-Treiber-/Firmware-Versionsmatrix ist im Repository noch nicht vollständig dokumentiert; behalte dein lokal funktionierendes SDK-Setup bei.

## Nutzung

### 1) Einheitliche Frame- + Event-GUI (empfohlener integrierter Workflow)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Bereitgestellte Funktionen:

- Auto-Scan für Frame- und Event-Geräte beim Start.
- Frame-Kamera-Steuerung: verbinden, grabben, Vorschau, Aufnahme, Belichtung/Gain.
- Event-Kamera-Steuerung: verbinden, erfassen, visualisieren, aufnehmen.
- Gemeinsame Steuerung: Vorschau und Aufnahme für beide Seiten zusammen starten/stoppen.
- Steuerung von Ausgabeverzeichnis + Dateinamenpräfix in der GUI.

Standard-Ausgabeverhalten:

| Ausgabe | Muster |
|---|---|
| Basisverzeichnis | `recordings/` |
| Run-Ordner | `<prefix>_<timestamp>/` |
| Frame-Dateien | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Event-Dateien (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Event-Dateien (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` beim Stoppen) |

### 2) Reine Event-GUI

```bash
python unified_event_gui.py
```

Standardverhalten:

- Basis-Ausgabeverzeichnis: `recordings/`
- Standard-Run-Präfix: `session`
- Geräteerkennung:
  - DAVIS über `dv.io.camera.discover()`
  - EVK als `EVK:auto`, wenn Metavision-Module verfügbar sind
- Aufnahmeausgaben:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` und `events.npz` (wenn gepufferte Events vorhanden sind)

### 3) DAVIS-Aufnahmeskript (Kamera oder DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Wichtige Standardkonstanten im Skript:

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

Format des Ausgabeverzeichnisses:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- Typische Dateien: `events.npz`, `frames.avi`, `output.aedat4`

## Konfiguration

### `save_davis_tcp.py`

Passe die obersten Konstanten in Großbuchstaben an, um Folgendes zu konfigurieren:

- Eingabequelle (`INPUT_MODE`)
- Netzwerk-Endpunkt (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- Aufnahmedauer (`CAPTURE_SECONDS`)
- Ausgabetoggles (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- Vorschauverhalten (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Zur Laufzeit in der GUI verfügbare Einstellungen:

- Ausgabeordner und Dateinamenpräfix
- Frame-Transformationen (vertikal/horizontal flippen, Rotation)
- Frame-Belichtungs- und Gain-Regler
- EVK-Bias-Steuerung (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) falls unterstützt

### `unified_event_gui.py`

Wichtige Standardwerte (im Skript editierbar):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## Beispiele

### Beispiel A: Direkte DAVIS-Kameraaufnahme für 10 Sekunden

`save_davis_tcp.py` bearbeiten:

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

### Beispiel B: DAVIS-Daten über TCP aus DV Viewer empfangen

`save_davis_tcp.py` bearbeiten:

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

### Beispiel C: Reine Event-Session mit verbundenem EVK und DAVIS

```bash
python unified_event_gui.py
```

Dann in der GUI:

1. Auf `Scan` klicken.
2. Ausgewählte Geräte verbinden.
3. Ausgabeordner/Präfix setzen.
4. Mit `Record All` synchronisierte Ausgabeordner pro Run starten.

## Entwicklungshinweise

- Aktuell ist kein Build-System oder Paket-Metadaten definiert (`pyproject.toml`, `requirements.txt` usw. fehlen).
- Skripte werden direkt über Python-Entrypoints gestartet.
- Die Konfiguration erfolgt überwiegend über Skriptkonstanten und GUI-Steuerungen, nicht über CLI-Flags.
- Vendor-SDK-Verzeichnisse bleiben absichtlich im Repository:
  - `evk_sdk/`
  - `haikang_sdk/`
- Ausgabe-/Datenartefakte sind in `.gitignore` enthalten, einschließlich:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz` usw.
- Die Dual-Kamera-GUI enthält Vorschaufenster-Positionierungslogik, um Pop-in zu reduzieren und zu verhindern, dass Fenster die Hauptsteuerungen verdecken, besonders unter Windows.

## Fehlerbehebung

| Symptom | Prüfungen / Maßnahmen |
|---|---|
| `dv_processing`-Importfehler | `dv-processing` in der aktiven Umgebung installieren oder reparieren. Der direkte DAVIS-Kameramodus in `save_davis_tcp.py` benötigt `dv-processing`. |
| EVK-Import-/Modulfehler (`metavision_*`) | Prüfen, ob Metavision-SDK/Python-Module installiert und im Python-Pfad verfügbar sind. |
| Importfehler beim Frame-Kamera-SDK (`MvCameraControl_class` usw.) | Verifizieren, dass Hikrobot/Haikang-SDK-Dateien und Laufzeitabhängigkeiten vorhanden sind. Prüfen, ob lokal verwendete SDK-Pfade in den Skripten gültig sind. |
| Keine Geräte gefunden | Kamera-Verbindung, Stromversorgung und Berechtigungen prüfen. GUI-`Scan` nach erneutem Verbinden der Hardware erneut ausführen. |
| DAVIS-Vorschau zeigt nicht sofort Events | Ein Vorschaufenster kann mit leerem Frame öffnen, bis Event-Pakete eintreffen. |
| Vorschau ist nicht immer im Vordergrund oder nicht wie erwartet positioniert | Unter Windows `pywin32` installieren; auf Nicht-Windows-Plattformen ist das Verhalten eingeschränkt. |
| Aufnahmedateien enthalten nicht den erwarteten Inhalt | Manche Dateien werden erst beim Stoppen finalisiert; sicherstellen, dass die Aufnahme sauber beendet wird, bevor die App geschlossen wird. |

## Roadmap

- Gepinnte Abhängigkeitsdateien hinzufügen (`requirements.txt` oder `pyproject.toml`).
- Hardware-unabhängige, automatisierte Tests für Utility-Logik hinzufügen.
- Dokumentation für validierte Hardware-/Treiber-/Versionskombinationen erweitern.
- CLI-Argumente für aktuell hartkodierte Skriptkonstanten hinzufügen.
- Mehrsprachige README-Dateien in `i18n/` ergänzen und über die Sprachoptionenzeile verlinken.

## Mitwirken

Beiträge sind willkommen.

Empfohlener Ablauf:

1. Einen Branch für deine Änderung erstellen.
2. Änderungen fokussiert und hardware-sicher halten.
3. Durch Ausführen relevanter Skripte gegen verfügbare Geräte validieren.
4. Große generierte Aufnahmen/Daten nicht committen.
5. PR mit folgenden Angaben öffnen:
   - Hardware-/Software-Umgebung
   - Kamera-Setup
   - Port-/Viewer-Einstellungen (für Netzwerk-Workflows)
   - Beispiel-Ausgabepfade/-Logs

Hinweis zur Repository-Konvention: Commit-Nachrichten sind derzeit leichtgewichtig; kurze Imperativ-Nachrichten verwenden (zum Beispiel: `Add DAVIS capture docs`).

## Lizenz

Derzeit ist in diesem Repository keine explizite Lizenzdatei vorhanden.

Hinweis zur Annahme: Wenn dieses Projekt zur Weiterverteilung gedacht ist, füge eine `LICENSE`-Datei hinzu und aktualisiere diesen Abschnitt.

## Danksagungen

- Prophesee-Metavision-Ökosystem (`evk_sdk/` und zugehörige Python-Module).
- iniVation/dv-processing-Ökosystem für DAVIS-Handling.
- Hikrobot/Haikang-Kamera-SDK-Ressourcen im Verzeichnis `haikang_sdk/`.
