# Repository Guidelines

## Project Structure & Module Organization
This repository is a collection of Python scripts for camera capture and processing, plus vendor SDK bundles.
- Top-level scripts are for active workflows; for example `save_davis_tcp.py` captures DAVIS events/frames from DV Viewer over TCP.
- `code-legacy/` holds older capture and experiment scripts (`DualCamera_*.py`, `frame_record*.py`, etc.).
- `evk_sdk/` and `haikang_sdk/` contain vendor SDKs, samples, and binaries.
- Generated recordings go in `davis_output/` (gitignored). Use `data/` for datasets or intermediate results you want to keep.

## Build, Test, and Development Commands
There is no build system; run scripts directly with Python.
- `python save_davis_tcp.py` — captures events and frames into `davis_output/<timestamp>/`, including `output.aedat4`. Set `INPUT_MODE = "camera"` for direct hardware or `"network"` for DV Viewer TCP.
- Set `SHOW_EVENT_PREVIEW = True` in `save_davis_tcp.py` to open a live event preview window (press `q` or `Esc` to quit).
- Dependencies are installed per your environment (e.g., `pip install dv-processing`, plus `opencv-python` and `numpy`).

## Coding Style & Naming Conventions
- Python, 4-space indentation; prefer PEP 8 formatting.
- Use `snake_case` for files/functions and `PascalCase` for classes.
- Keep configuration in uppercase constants at the top of scripts (e.g., `EVENTS_PORT`, `CAPTURE_SECONDS`).

## Testing Guidelines
- No automated test suite is configured. Validate changes by running the relevant script and verifying outputs.
- If you add tests, use `tests/` with `test_*.py` naming (pytest-style), and keep them hardware-independent when possible.

## Commit & Pull Request Guidelines
- Git history is minimal (initial commit only), so no strict convention exists. Use short, imperative messages (e.g., “Add DAVIS capture script”).
- Always commit and push after changes unless explicitly told not to. Use `git status`, `git add -A`, `git commit -m "Describe change"`, then `git push`.
- PRs should describe the hardware/software setup, ports, and any required viewer settings; include sample outputs when applicable.

## Configuration & Data Hygiene
- Do not commit large recordings; keep outputs in `davis_output/` and rely on `.gitignore`.
- When documenting capture settings, include DV Viewer options (TCP host, ports, compression).
- AEDAT4 output is enabled by default in `save_davis_tcp.py` (requires `dv-processing`).
