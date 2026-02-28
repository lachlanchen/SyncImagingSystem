[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## 개요

`SyncImagingSystem`은 프레임 카메라와 이벤트 카메라의 동기화 캡처를 위한 Python 작업공간입니다.

주요 활성 워크플로는 3가지입니다.

1. `DualCamera_separate_transform_davis+evk.py`: 프레임 + 이벤트 캡처를 위한 통합 GUI (Hikrobot/Haikang 프레임 카메라 + EVK 또는 DAVIS 이벤트 카메라)
2. `unified_event_gui.py`: EVK 및 DAVIS 장치를 위한 이벤트 전용 GUI
3. `save_davis_tcp.py`: 직접 카메라 모드와 DV Viewer TCP 네트워크 모드를 지원하는 DAVIS 캡처 스크립트

저장소에는 참고용 벤더 SDK/샘플 번들과 과거 프로토타입도 포함되어 있습니다.

## 주요 기능

| 영역 | 하이라이트 |
|---|---|
| 🎛️ 통합 GUI | 장치별 제어와 통합 시작/중지 제어를 갖춘 프레임 + 이벤트 통합 캡처 GUI |
| ⚡ 이벤트 GUI | 다중 장치 연결/미리보기/기록 작업을 지원하는 이벤트 전용 GUI |
| 📡 DAVIS 소스 | 직접 하드웨어(`INPUT_MODE = "camera"`) 또는 DV Viewer 네트워크 스트림(`INPUT_MODE = "network"`, 기본 포트 `7777/7778`)에서 DAVIS 캡처 |
| 💾 출력 형식 | 기록 출력은 `.avi`, `.raw`, `.aedat4`, 선택적 압축 `events.npz` 포함 |
| 🗂️ 런 구성 | `recordings/` 또는 `davis_output/` 하위에 타임스탬프 기반 런 폴더 자동 구성 |
| 🔧 제어 | 통합 GUI 워크플로에서 EVK bias 제어 지원 |
| 🪞 프레임 변환 | 듀얼 카메라 GUI에서 상하 반전, 좌우 반전, 90도 회전 지원 |
| 🖥️ 창 배치 | 다중 창 워크플로(특히 Windows)용 미리보기 창 배치 보조 기능 |

## 프로젝트 구조

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

## 사전 요구 사항

### 하드웨어

- Hikrobot/Haikang 프레임 카메라 (프레임 워크플로용)
- EVK 이벤트 카메라 및/또는 DAVIS 이벤트 카메라

### 운영체제

- 전체 프레임 카메라 SDK 통합 및 미리보기 배치 동작을 위해 Windows를 주요 대상으로 합니다.
- Linux/macOS에서도 이벤트 파이프라인 일부는 실행할 수 있으나, 완전한 동등성은 보장되지 않습니다.

### Python

- Python 3.x

### Python 패키지

활성 환경에 핵심 런타임 의존성을 설치하세요.

```bash
pip install numpy opencv-python dv-processing
```

EVK 워크플로를 위해서는, 환경에서 사용 가능한 Prophesee Metavision Python 패키지를 설치하세요.

GUI 미리보기의 Windows 창 제어 동작을 위해:

```bash
pip install pywin32
```

## 설치

1. 저장소를 클론합니다.
2. 저장소 루트에서 터미널을 엽니다.

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Python 환경을 생성/활성화합니다.
4. 의존성을 설치합니다(위 참고).
5. 장치에 필요한 카메라 SDK 런타임/드라이버가 설치되어 있는지 확인합니다.

가정 메모: 정확한 벤더 드라이버/펌웨어 버전 매트릭스는 아직 저장소 내에 완전히 문서화되어 있지 않으므로, 현재 검증된 로컬 SDK 구성을 유지하세요.

## 사용 방법

### 1) 통합 프레임 + 이벤트 GUI (권장 통합 워크플로)

```bash
python DualCamera_separate_transform_davis+evk.py
```

제공 기능:

- 시작 시 프레임/이벤트 장치를 자동 스캔
- 프레임 카메라 제어: 연결, 캡처, 미리보기, 기록, 노출/게인
- 이벤트 카메라 제어: 연결, 캡처, 시각화, 기록
- 통합 제어: 양쪽 미리보기 및 기록 동시 시작/중지
- GUI에서 출력 디렉터리 + 파일명 접두사 제어

기본 출력 동작:

| 출력 | 패턴 |
|---|---|
| 기본 디렉터리 | `recordings/` |
| 런 폴더 | `<prefix>_<timestamp>/` |
| 프레임 파일 | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| 이벤트 파일 (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| 이벤트 파일 (DAVIS) | `<event_device_label>/output.aedat4` (+ 중지 시 `events.npz`) |

### 2) 이벤트 전용 GUI

```bash
python unified_event_gui.py
```

기본 동작:

- 출력 기본 디렉터리: `recordings/`
- 기본 런 접두사: `session`
- 장치 탐색:
  - `dv.io.camera.discover()`에서 DAVIS 탐색
  - Metavision 모듈 사용 가능 시 EVK를 `EVK:auto`로 탐색
- 기록 출력:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` 및 `events.npz` (버퍼된 이벤트가 있을 경우)

### 3) DAVIS 캡처 스크립트 (카메라 또는 DV Viewer TCP)

```bash
python save_davis_tcp.py
```

스크립트의 기본 주요 상수:

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
- 일반 파일: `events.npz`, `frames.avi`, `output.aedat4`

## 설정

### `save_davis_tcp.py`

다음 항목은 상단의 대문자 상수를 조정해 설정합니다.

- 입력 소스 (`INPUT_MODE`)
- 네트워크 엔드포인트 (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- 캡처 시간 (`CAPTURE_SECONDS`)
- 출력 토글 (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- 미리보기 동작 (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

GUI에서 노출되는 런타임 설정:

- 출력 폴더와 파일명 접두사
- 프레임 변환 (상하/좌우 반전, 회전)
- 프레임 노출 및 게인 제어
- 지원 시 EVK bias 제어 (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`)

### `unified_event_gui.py`

핵심 기본값(스크립트에서 수정 가능):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 예시

### 예시 A: 직접 DAVIS 카메라를 10초간 캡처

`save_davis_tcp.py`를 수정:

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

### 예시 B: DV Viewer에서 TCP로 DAVIS 데이터 수신

`save_davis_tcp.py`를 수정:

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

### 예시 C: EVK와 DAVIS를 모두 연결한 이벤트 전용 세션

```bash
python unified_event_gui.py
```

그다음 GUI에서:

1. `Scan` 클릭
2. 선택한 장치 연결
3. 출력 폴더/접두사 설정
4. `Record All`로 동기화된 런별 출력 폴더 기록 시작

## 개발 노트

- 현재 빌드 시스템 또는 패키지 메타데이터가 정의되어 있지 않습니다(`pyproject.toml`, `requirements.txt` 등 없음).
- 스크립트는 Python 엔트리포인트로 직접 실행합니다.
- 설정은 CLI 플래그보다 스크립트 상수와 GUI 제어에 주로 의존합니다.
- 벤더 SDK 디렉터리는 의도적으로 저장소에 포함되어 있습니다.
  - `evk_sdk/`
  - `haikang_sdk/`
- 다음 출력/데이터 산출물은 gitignore로 제외됩니다.
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz` 등
- 듀얼 카메라 GUI에는 특히 Windows에서 미리보기 창이 갑자기 튀어나오는 현상을 줄이고 메인 제어를 가리지 않도록 설계된 창 배치 로직이 포함되어 있습니다.

## 문제 해결

| 증상 | 확인 / 조치 |
|---|---|
| `dv_processing` import 오류 | 활성 환경에 `dv-processing`을 설치 또는 복구하세요. `save_davis_tcp.py`의 직접 DAVIS 카메라 모드는 `dv-processing`이 필요합니다. |
| EVK import/모듈 오류 (`metavision_*`) | Metavision SDK/Python 모듈이 설치되어 있고 Python 경로에 포함되어 있는지 확인하세요. |
| 프레임 카메라 SDK import 실패 (`MvCameraControl_class` 등) | Hikrobot/Haikang SDK 파일과 런타임 의존성이 존재하는지 확인하세요. 스크립트가 사용하는 로컬 SDK 경로가 유효한지도 확인하세요. |
| 장치가 검색되지 않음 | 카메라 연결, 전원, 권한을 확인하세요. 하드웨어를 다시 연결한 뒤 GUI에서 `Scan`을 다시 실행하세요. |
| DAVIS 미리보기에 이벤트가 바로 표시되지 않음 | 이벤트 패킷이 도착할 때까지 빈 프레임으로 미리보기 창이 열릴 수 있습니다. |
| 미리보기가 항상 위로 고정되지 않거나 위치가 예상과 다름 | Windows에서는 `pywin32`를 설치하세요. 비 Windows 플랫폼에서는 동작이 제한될 수 있습니다. |
| 기록 파일에 예상한 내용이 없음 | 일부 파일은 중지 시점에 최종 처리됩니다. 앱을 종료하기 전에 기록이 정상적으로 중지되었는지 확인하세요. |

## 로드맵

- 고정 버전 의존성 파일 추가 (`requirements.txt` 또는 `pyproject.toml`)
- 유틸리티 로직에 대한 하드웨어 독립 자동 테스트 추가
- 검증된 하드웨어/드라이버/버전 조합 문서 확장
- 현재 하드코딩된 스크립트 상수에 대한 CLI 인자 추가
- `i18n/`에 다국어 README 파일을 추가하고 언어 옵션 줄에서 링크

## 기여

기여를 환영합니다.

권장 워크플로:

1. 변경 작업용 브랜치를 생성합니다.
2. 수정 범위를 좁게 유지하고 하드웨어 안전성을 고려합니다.
3. 사용 가능한 장치로 관련 스크립트를 실행해 검증합니다.
4. 대용량 생성 기록/데이터는 커밋하지 않습니다.
5. 다음 내용을 포함해 PR을 작성합니다.
   - 하드웨어/소프트웨어 환경
   - 카메라 설정
   - 포트/뷰어 설정(네트워크 워크플로의 경우)
   - 샘플 출력 경로/로그

저장소 관례 메모: 현재 커밋 메시지 규칙은 가벼운 편이므로, 짧은 명령형 메시지를 사용하세요(예: `Add DAVIS capture docs`).

## 라이선스

현재 이 저장소에는 명시적인 라이선스 파일이 없습니다.

가정 메모: 이 프로젝트를 재배포할 예정이라면 `LICENSE` 파일을 추가하고 이 섹션을 업데이트하세요.

## 감사의 말

- Prophesee Metavision 생태계 (`evk_sdk/` 및 관련 Python 모듈)
- DAVIS 처리를 위한 iniVation/dv-processing 생태계
- `haikang_sdk/`에 번들된 Hikrobot/Haikang 카메라 SDK 리소스
