[English](README.md) · [العربية](i18n/README.ar.md) · [Español](i18n/README.es.md) · [Français](i18n/README.fr.md) · [日本語](i18n/README.ja.md) · [한국어](i18n/README.ko.md) · [Tiếng Việt](i18n/README.vi.md) · [中文 (简体)](i18n/README.zh-Hans.md) · [中文（繁體）](i18n/README.zh-Hant.md) · [Deutsch](i18n/README.de.md) · [Русский](i18n/README.ru.md)

# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## Overview

`SyncImagingSystem` is a Python workspace for synchronized frame-camera and event-camera capture.

It provides three main active workflows:

1. `DualCamera_separate_transform_davis+evk.py`: unified GUI for frame + event capture (Hikrobot/Haikang frame camera + EVK or DAVIS event camera).
2. `unified_event_gui.py`: event-only GUI for EVK and DAVIS devices.
3. `save_davis_tcp.py`: DAVIS capture script supporting direct camera mode and DV Viewer TCP network mode.

The repository also contains vendor SDK/sample bundles and historical prototypes for reference.

## Features

| Area | Highlights |
|---|---|
| 🎛️ Unified GUI | Unified frame + event capture GUI with per-device controls and unified start/stop controls. |
| ⚡ Event GUI | Event-only GUI with multi-device connect/preview/record operations. |
| 📡 DAVIS Sources | DAVIS capture from direct hardware (`INPUT_MODE = "camera"`) or DV Viewer network stream (`INPUT_MODE = "network"`, default ports `7777/7778`). |
| 💾 Output Formats | Recording outputs include `.avi`, `.raw`, `.aedat4`, and optional compressed `events.npz`. |
| 🗂️ Run Organization | Automatic timestamped run-folder organization under `recordings/` or `davis_output/`. |
| 🔧 Controls | EVK bias controls in unified GUI workflows. |
| 🪞 Frame Transform | Vertical flip, horizontal flip, and 90-degree rotation in the dual-camera GUI. |
| 🖥️ Windowing | Preview window placement helpers for multi-window workflows (notably on Windows). |

## Project Structure

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # Main unified frame+event GUI (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Older integrated frame+EVK GUI variant
├── unified_event_gui.py                         # Event-only GUI for EVK + DAVIS
├── save_davis_tcp.py                            # DAVIS capture (camera or DV Viewer TCP)
├── code-legacy/                                 # Historical scripts/prototypes
├── evk_sdk/                                     # Prophesee/Metavision SDK scripts and samples
├── haikang_sdk/                                 # Hikrobot/Haikang SDK bundles and samples
├── i18n/                                        # Translation directory (currently empty)
├── recordings/                                  # Runtime output (gitignored, created on use)
└── davis_output/                                # Runtime output for save_davis_tcp.py (gitignored)
```

## Prerequisites

### Hardware

- Hikrobot/Haikang frame camera (for frame workflows).
- EVK event camera and/or DAVIS event camera.

### OS

- Windows is the primary target for full frame-camera SDK integration and preview placement behavior.
- Linux/macOS may run parts of the event pipeline, but full parity is not guaranteed.

### Python

- Python 3.x.

### Python packages

Install core runtime dependencies in your active environment:

```bash
pip install numpy opencv-python dv-processing
```

For EVK workflows, install Prophesee Metavision Python packages available in your environment.

For Windows window-control behavior in GUI previews:

```bash
pip install pywin32
```

## Installation

1. Clone the repository.
2. Open a terminal in the repository root:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Create/activate your Python environment.
4. Install dependencies (see above).
5. Ensure required camera SDK runtimes/drivers are installed for your devices.

Assumption note: exact vendor driver/firmware version matrix is not fully documented in-repo yet; preserve your known-good local SDK setup.

## Usage

### 1) Unified frame + event GUI (recommended integrated workflow)

```bash
python DualCamera_separate_transform_davis+evk.py
```

What it provides:

- Auto-scan for frame and event devices at startup.
- Frame camera controls: connect, grab, preview, record, exposure/gain.
- Event camera controls: connect, capture, visualize, record.
- Unified controls: start/stop preview and recording for both sides together.
- Output directory + filename prefix controls in the GUI.

Default output behavior:

| Output | Pattern |
|---|---|
| Base directory | `recordings/` |
| Run folder | `<prefix>_<timestamp>/` |
| Frame files | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Event files (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Event files (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` on stop) |

### 2) Event-only GUI

```bash
python unified_event_gui.py
```

Default behavior:

- Output base directory: `recordings/`
- Default run prefix: `session`
- Device discovery:
  - DAVIS from `dv.io.camera.discover()`
  - EVK as `EVK:auto` when Metavision modules are available
- Record outputs:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` and `events.npz` (if buffered events exist)

### 3) DAVIS capture script (camera or DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Default key constants in the script:

| Constant | Default |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` for DV Viewer TCP) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

Output directory format:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- Typical files: `events.npz`, `frames.avi`, `output.aedat4`

## Configuration

### `save_davis_tcp.py`

Adjust the top-level uppercase constants to configure:

- input source (`INPUT_MODE`)
- network endpoint (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- capture duration (`CAPTURE_SECONDS`)
- output toggles (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- preview behavior (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

GUI-exposed runtime settings include:

- output folder and filename prefix
- frame transforms (vertical/horizontal flip, rotation)
- frame exposure and gain controls
- EVK bias controls (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) when supported

### `unified_event_gui.py`

Key defaults (editable in script):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## Examples

### Example A: Direct DAVIS camera capture for 10 seconds

Edit `save_davis_tcp.py`:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

Run:

```bash
python save_davis_tcp.py
```

### Example B: Receive DAVIS data from DV Viewer via TCP

Edit `save_davis_tcp.py`:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

Run:

```bash
python save_davis_tcp.py
```

### Example C: Event-only session with both EVK and DAVIS connected

```bash
python unified_event_gui.py
```

Then in GUI:

1. Click `Scan`.
2. Connect selected devices.
3. Set output folder/prefix.
4. Use `Record All` to start synchronized per-run output folders.

## Development Notes

- No build system or package metadata is currently defined (`pyproject.toml`, `requirements.txt`, etc. are absent).
- Scripts are launched directly with Python entrypoints.
- Configuration is mostly script constants and GUI controls, not CLI flags.
- Vendor SDK directories are intentionally kept in-repo:
  - `evk_sdk/`
  - `haikang_sdk/`
- Output/data artifacts are gitignored, including:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, etc.
- The dual-camera GUI includes preview placement logic designed to reduce preview pop-in and keep windows from obscuring the main controls, especially on Windows.

## Troubleshooting

| Symptom | Checks / Actions |
|---|---|
| `dv_processing` import errors | Install or repair `dv-processing` in the active environment. Direct DAVIS camera mode in `save_davis_tcp.py` requires `dv-processing`. |
| EVK import/module errors (`metavision_*`) | Confirm Metavision SDK/Python modules are installed and on your Python path. |
| Frame camera SDK import failures (`MvCameraControl_class`, etc.) | Verify Hikrobot/Haikang SDK files and runtime dependencies are present. Confirm local SDK paths used by scripts are valid. |
| No devices found | Check camera connection, power, and permissions. Re-run GUI `Scan` after reconnecting hardware. |
| DAVIS preview does not show events immediately | A preview window may open with a blank frame until event packets arrive. |
| Preview not always-on-top or not positioned as expected | On Windows, install `pywin32`; on non-Windows platforms, behavior is limited. |
| Recording files missing expected contents | Some files are finalized at stop; ensure recording is cleanly stopped before closing the app. |

## Roadmap

- Add pinned dependency files (`requirements.txt` or `pyproject.toml`).
- Add hardware-independent automated tests for utility logic.
- Expand docs for validated hardware/driver/version combinations.
- Add CLI arguments for currently hardcoded script constants.
- Add multilingual README files in `i18n/` and link them from the language-options line.

## Contributing

Contributions are welcome.

Suggested workflow:

1. Create a branch for your change.
2. Keep modifications focused and hardware-safe.
3. Validate by running relevant scripts against available devices.
4. Avoid committing large generated recordings/data.
5. Open a PR describing:
   - hardware/software environment
   - camera setup
   - ports/viewer settings (for network workflows)
   - sample output paths/logs

Repository convention note: commit messages are currently lightweight; use short imperative messages (for example: `Add DAVIS capture docs`).

## License

No explicit license file is currently present in this repository.

Assumption note: if this project is intended for redistribution, add a `LICENSE` file and update this section.

## Acknowledgements

- Prophesee Metavision ecosystem (`evk_sdk/` and related Python modules).
- iniVation/dv-processing ecosystem for DAVIS handling.
- Hikrobot/Haikang camera SDK resources bundled under `haikang_sdk/`.
