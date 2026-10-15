[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem`는 EVK/DAVIS 및 Hikrobot/Haikang 카메라를 위한 실전형 동기화 프레임/이벤트 캡처 작업흐름을 중심으로 구성된 Python 워크스페이스입니다.

## 🧭 Quick Navigator

| Section | Link |
|---|---|
| Primary workflows | [Usage](#usage) |
| Project setup | [Installation](#installation) |
| Troubleshooting | [Troubleshooting](#troubleshooting) |
| Contribution details | [Contributing](#contributing) |
| Support | [❤️ Support](#-support) |

## 📌 Overview

`SyncImagingSystem`은 동기화된 프레임 카메라 및 이벤트 카메라 캡처를 위한 Python 워크스페이스입니다.

세 가지 주요 활성 워크플로우를 제공합니다:

| Script | Purpose | Notes |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | 통합 프레임 + 이벤트 GUI | Hikrobot/Haikang 프레임 카메라 + EVK 또는 DAVIS 이벤트 카메라 지원 |
| `unified_event_gui.py` | 이벤트 전용 GUI | EVK + DAVIS 자동 탐지 및 런별 기록 |
| `save_davis_tcp.py` | DAVIS 캡처 스크립트 | 직접 카메라 모드와 DV Viewer TCP 네트워크 모드 지원 |

저장소에는 벤더 SDK/샘플 번들과 참고용 과거 프로토타입도 포함되어 있습니다.

## 🚀 Features

| Area | Highlights |
|---|---|
| 🎛️ Unified GUI | 장치별 제어와 통합 시작/중지 제어가 가능한 통합 프레임 + 이벤트 캡처 GUI |
| ⚡ Event GUI | 다중 장치 connect/preview/record를 처리하는 이벤트 전용 GUI |
| 📡 DAVIS Sources | 직접 하드웨어(`INPUT_MODE = "camera"`) 또는 DV Viewer 네트워크 스트림(`INPUT_MODE = "network"`, 기본 포트 `7777/7778`)을 통한 DAVIS 캡처 |
| 💾 Output Formats | 기록 출력: `.avi`, `.raw`, `.aedat4`, 선택적 압축 `events.npz` |
| 🗂️ Run Organization | `recordings/` 또는 `davis_output/` 아래에 타임스탬프 기반 런 폴더를 자동 생성 |
| 🔧 Controls | 통합 GUI에서 EVK bias 제어 제공 |
| 🪞 Frame Transform | 듀얼 카메라 GUI의 상하 반전, 좌우 반전, 90도 회전 |
| 🖥️ Windowing | 다중 창 워크플로(특히 Windows)에서 미리보기 창 위치 제어 도우미 |

## 🧩 Project Structure

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
├── i18n/                                        # Translation directory
├── recordings/                                  # Runtime output (gitignored, created on use)
└── davis_output/                                # Runtime output for save_davis_tcp.py (gitignored)
```

## 🛠️ Prerequisites

### Hardware

- Hikrobot/Haikang 프레임 카메라(프레임 워크플로용)
- EVK 이벤트 카메라 및/또는 DAVIS 이벤트 카메라

### OS

- Windows는 전체 프레임 카메라 SDK 통합과 미리보기 창 배치 동작에 대해 주요 대상 OS입니다.
- Linux/macOS에서도 이벤트 파이프라인의 일부를 실행할 수 있지만, 전체 동등 동작은 보장되지 않습니다.

### Python

- Python 3.x

### Python packages

활성 환경에서 핵심 런타임 의존성을 설치하세요:

```bash
pip install numpy opencv-python dv-processing
```

EVK 워크플로의 경우, 사용 중인 환경에 맞는 Prophesee Metavision Python 패키지를 설치하세요.

Windows GUI 미리보기에서 창 제어 동작이 필요하면:

```bash
pip install pywin32
```

## 🧪 Installation

1. 저장소를 클론합니다.
2. 저장소 루트에서 터미널을 엽니다.

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Python 환경을 생성/활성화합니다.
4. 의존성을 설치합니다(위 참조).
5. 장치에 필요한 카메라 SDK 런타임/드라이버가 장착되어 있는지 확인합니다.

가정 참고: 정확한 벤더 드라이버/펌웨어 버전 행렬은 아직 저장소 내에 완전 문서화되어 있지 않습니다. 로컬에서 검증된 SDK 구성을 유지하세요.

## ▶️ Usage

### 1) Unified frame + event GUI (권장 통합 워크플로)

```bash
python DualCamera_separate_transform_davis+evk.py
```

제공 기능:

- 시작 시 프레임/이벤트 장치를 자동 탐지
- 프레임 카메라 제어: 연결, 수신, 미리보기, 기록, 노출/게인
- 이벤트 카메라 제어: 연결, 캡처, 시각화, 기록
- 통합 제어: 두 스트림의 미리보기 및 기록 시작/중지 동기화
- GUI에서 출력 디렉터리와 파일명 접두사 제어

기본 출력 동작:

| Output | Pattern |
|---|---|
| 기본 디렉터리 | `recordings/` |
| 런 폴더 | `<prefix>_<timestamp>/` |
| 프레임 파일 | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| 이벤트 파일 (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| 이벤트 파일 (DAVIS) | `<event_device_label>/output.aedat4` (`events.npz`는 중지 시 생성) |

### 2) Event-only GUI

```bash
python unified_event_gui.py
```

기본 동작:

- 출력 기본 디렉터리: `recordings/`
- 기본 런 접두사: `session`
- 장치 탐색:
  - DAVIS: `dv.io.camera.discover()`
  - EVK: Metavision 모듈 사용 가능 시 `EVK:auto`
- 기록 출력:
  - EVK: `.raw`
  - DAVIS: `output.aedat4`, `events.npz`(버퍼 이벤트 존재 시)

### 3) DAVIS capture script (camera or DV Viewer TCP)

```bash
python save_davis_tcp.py
```

스크립트 내 기본 상수:

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

출력 디렉터리 형식:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- 일반 출력 파일: `events.npz`, `frames.avi`, `output.aedat4`

## ⚙️ Configuration

### `save_davis_tcp.py`

스크립트 상단의 대문자 상수를 수정해 설정합니다:

- 입력 소스 (`INPUT_MODE`)
- 네트워크 엔드포인트 (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- 캡처 시간 (`CAPTURE_SECONDS`)
- 출력 토글 (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- 미리보기 동작 (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

GUI에서 노출 가능한 런타임 설정:

- 출력 폴더 및 파일명 접두사
- 프레임 변환(상하 반전/좌우 반전/회전)
- 프레임 노출과 게인 제어
- EVK bias 제어 (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) 지원 시 표시

### `unified_event_gui.py`

스크립트에서 편집 가능한 핵심 기본값:

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 💡 Examples

### Example A: Direct DAVIS camera capture for 10 seconds

`save_davis_tcp.py`를 수정합니다:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

실행:

```bash
python save_davis_tcp.py
```

### Example B: Receive DAVIS data from DV Viewer via TCP

`save_davis_tcp.py`를 수정합니다:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

실행:

```bash
python save_davis_tcp.py
```

### Example C: Event-only session with both EVK and DAVIS connected

```bash
python unified_event_gui.py
```

그다음 GUI에서:

1. `Scan` 클릭.
2. 선택한 장치 연결.
3. 출력 폴더/접두사 설정.
4. `Record All`로 동기화된 런별 출력 폴더 기록 시작.

## 🛠️ Development Notes

- 현재 빌드 시스템이나 패키지 메타데이터는 정의되어 있지 않습니다(`pyproject.toml`, `requirements.txt` 등 없음).
- 스크립트는 Python entrypoint로 직접 실행됩니다.
- 설정은 CLI 플래그보다 스크립트 상수와 GUI 제어에 의존합니다.
- 벤더 SDK 디렉터리를 의도적으로 저장소에 보관합니다:
  - `evk_sdk/`
  - `haikang_sdk/`
- 출력/데이터 산출물은 gitignore 처리되어 있습니다:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz` 등
- 듀얼 카메라 GUI는 미리보기 창이 갑자기 튀어나오는 현상을 줄이고 특히 Windows에서 메인 제어를 가리지 않도록 설계된 배치 로직이 포함되어 있습니다.

## 🧭 Troubleshooting

- 시작 시 장치가 검색되지 않음
  - 카메라 케이블, 전원, 벤더 드라이버를 확인하세요.
  - 장치 권한과 이벤트/프레임 런타임이 설치되었는지 확인하세요.
- 첫 프레임 미리보기에서 GUI가 멈추는 것처럼 보임
  - 프레임·이벤트 장치를 모두 분리한 뒤 재연결하고 다시 스캔하세요.
- DAVIS 네트워크 모드에서 데이터 수신 없음
  - DV Viewer의 스트림 포트가 `EVENTS_PORT`/`FRAMES_PORT`와 일치하는지 확인하세요.
  - 로컬 루프백 및 UDP/TCP 트래픽 방화벽 규칙을 확인하세요.
- `.npz` 또는 `.aedat4` 파일이 생성되지 않음
  - `save_davis_tcp.py`에서 저장 토글이 켜져 있는지 확인하세요.
  - 출력 폴더 쓰기 권한을 확인하세요.
- Windows에서 창 위치가 이동
  - `pywin32`가 설치되어 있고 Python 권한이 적절한지 확인하세요.

## 🗺️ Roadmap

저장소 내 문서와 사용성 개선 계획(아직 완성 전):

1. 고정 버전 의존성을 담은 requirements 파일로 통합.
2. 비 GUI 캡처 모드용 경량 CLI 대안 추가.
3. SDK 및 펌웨어 호환성 매트릭스 확장.
4. 상수 및 파일 레이아웃 로직에 대한 하드웨어 비의존적 테스트 추가.

## 👥 Contributing

기여를 환영합니다.

1. 카메라 경로 변경이 아닌 한 런타임 캡처 동작은 건드리지 마세요.
2. 변경 시 기존 카메라 스레드 생명주기와 출력 폴더 구성 규칙을 유지하세요.
3. 변경한 경로/스크립트는 최소 1회 로컬 전체 캡처 실행으로 검증하세요.
4. PR 설명에 가정 사항과 하드웨어 환경을 포함하세요.

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📩 Contact

특정 하드웨어 구성에서 통합 지원이 필요하면, 이슈 설명에 카메라 모델, OS, 정확한 오류 출력 로그를 함께 적어주세요.

## 📜 License

이 초안 작성 시점 기준으로 저장소 루트에 라이선스 파일이 없습니다. 공개 배포 전에 `LICENSE` 파일을 추가하세요.
