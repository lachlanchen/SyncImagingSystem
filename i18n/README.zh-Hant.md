[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` 是一個以 EVK/DAVIS 與 Hikrobot/Haikang 相機為核心的同步「幀相機＋事件相機」擷取 Python 工作區，圍繞可直接落地的 EVK/DAVIS 與影像流程設計。

<a id="usage"></a>
## 🧭 快速導覽

| 區段 | 連結 |
|---|---|
| 主要流程 | [使用方式](#usage) |
| 專案設定 | [安裝](#installation) |
| 問題排查 | [疑難排解](#troubleshooting) |
| 貢獻方式 | [參與貢獻](#contributing) |
| 支持 | [❤️ Support](#-support) |

<a id="overview"></a>
## 📌 概覽

`SyncImagingSystem` 是一個用於同步幀相機與事件相機擷取的 Python 工作區。

目前提供三個主要且可直接使用的流程：

| 檔案 | 用途 | 備註 |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | 統一式幀 + 事件 GUI | 支援 Hikrobot/Haikang 幀相機與 EVK 或 DAVIS 事件相機 |
| `unified_event_gui.py` | 僅事件 GUI | 提供 EVK + DAVIS 的自動偵測與逐次執行錄製 |
| `save_davis_tcp.py` | DAVIS 擷取腳本 | 支援直接相機模式及 DV Viewer TCP 網路模式 |

此外，倉庫亦保留廠商 SDK/範例套件與歷史原型作為參考。

<a id="features"></a>
## 🚀 功能特點

| 項目 | 重點 |
|---|---|
| 🎛️ 統一 GUI | 每個裝置皆可在同一介面控制，並以統一開始／停止邏輯進行同時擷取 |
| ⚡ 事件 GUI | 提供多裝置連線、預覽與錄製的事件專用介面 |
| 📡 DAVIS 來源 | 支援直接硬體模式（`INPUT_MODE = "camera"`）與 DV Viewer 網路串流模式（`INPUT_MODE = "network"`，預設埠 `7777/7778`） |
| 💾 輸出格式 | 錄製輸出包含 `.avi`、`.raw`、`.aedat4`，以及可選壓縮 `events.npz` |
| 🗂️ 執行目錄 | 自動於 `recordings/` 或 `davis_output/` 依時間戳建立執行資料夾 |
| 🔧 控制項 | 統一 GUI 中可調整 EVK 偏壓 |
| 🪞 幀畫面變換 | 雙攝影機 GUI 提供上下翻轉、左右翻轉與 90 度旋轉 |
| 🖥️ 視窗管理 | 預覽視窗定位輔助，可降低多視窗切換抖動（特別在 Windows） |

<a id="project-structure"></a>
## 🧩 專案結構

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

<a id="prerequisites"></a>
## 🛠️ 前置條件

### 硬體

- Hikrobot/Haikang 幀相機（用於幀流程）。
- EVK 事件相機與/或 DAVIS 事件相機。

### 作業系統

- Windows 為完整整合幀相機 SDK 與預覽定位行為的主要目標。
- Linux/macOS 可執行部分事件流程，但目前無法保證完整功能一致。

### Python

- Python 3.x。

### Python 套件

在你的執行環境安裝核心相依套件：

```bash
pip install numpy opencv-python dv-processing
```

若使用 EVK 流程，請安裝你環境內可用的 Prophesee Metavision Python 套件。

若於 Windows 預覽介面需要視窗控制行為，請安裝：

```bash
pip install pywin32
```

<a id="installation"></a>
## 🧪 安裝

1. Clone 倉庫。
2. 在倉庫根目錄開啟終端：

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. 建立並啟用 Python 環境。
4. 安裝相依套件（見上文）。
5. 安裝對應相機的廠商 SDK 執行環境與驅動。

注意：目前倉庫尚未完整記錄各廠商驅動與韌體版本矩陣；請保留你本機可用、已驗證的 SDK 組態。

## ▶️ 使用方式

### 1) 統一式幀 + 事件 GUI（建議的整合流程）

```bash
python DualCamera_separate_transform_davis+evk.py
```

功能重點：

- 啟動時自動掃描幀相機與事件相機。
- 幀相機控制：連線、擷取、預覽、錄製、曝光/增益。
- 事件相機控制：連線、擷取、可視化、錄製。
- 統一控制：兩側可同時預覽與錄製，並支援同步啟停。
- 在 GUI 中控制輸出資料夾與檔名前綴。

預設輸出行為：

| 輸出項目 | 規則 |
|---|---|
| 基礎目錄 | `recordings/` |
| 執行資料夾 | `<prefix>_<timestamp>/` |
| 幀影像檔 | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| 事件檔（EVK） | `<event_device_label>/<prefix>_<timestamp>.raw` |
| 事件檔（DAVIS） | `<event_device_label>/output.aedat4`（停止時可附加 `events.npz`） |

### 2) 僅事件 GUI

```bash
python unified_event_gui.py
```

預設行為：

- 輸出基礎目錄：`recordings/`
- 預設執行前綴：`session`
- 裝置發現：
  - DAVIS 由 `dv.io.camera.discover()` 提供
  - EVK 若 Metavision 模組可用，顯示為 `EVK:auto`
- 錄製輸出：
  - EVK：`.raw`
  - DAVIS：`output.aedat4` 與 `events.npz`（若有緩衝事件）

### 3) DAVIS 擷取腳本（相機模式或 DV Viewer TCP）

```bash
python save_davis_tcp.py
```

腳本預設主要常數：

| 常數 | 預設值 |
|---|---|
| `INPUT_MODE` | `"camera"`（DV Viewer TCP 改為 `"network"`） |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

輸出目錄格式：

- `davis_output/<YYYYmmdd_HHMMSS>/`
- 常見檔案：`events.npz`、`frames.avi`、`output.aedat4`

<a id="configuration"></a>
## ⚙️ 設定

### `save_davis_tcp.py`

調整腳本開頭的全大寫常數即可控制：

- 輸入來源（`INPUT_MODE`）
- 網路端點（`HOST`、`EVENTS_PORT`、`FRAMES_PORT`）
- 擷取長度（`CAPTURE_SECONDS`）
- 輸出開關（`SAVE_EVENTS_NPZ`、`SAVE_FRAMES_VIDEO`、`SAVE_AEDAT4`）
- 預覽行為（`SHOW_EVENT_PREVIEW`、`PREVIEW_FPS`、`PREVIEW_WINDOW_NAME`）

### `DualCamera_separate_transform_davis+evk.py`

GUI 中可調整的執行參數包含：

- 輸出資料夾與檔名前綴
- 幀影像變換（上下翻轉、左右翻轉、旋轉）
- 幀曝光與增益控制
- 若支援，EVK 偏壓控制（`bias_diff`、`bias_diff_off`、`bias_diff_on`、`bias_fo`、`bias_hpf`、`bias_refr`）

### `unified_event_gui.py`

可編輯的預設值（在腳本內）：

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

<a id="examples"></a>
## 💡 範例

### 範例 A：直接以 DAVIS 相機擷取 10 秒

編輯 `save_davis_tcp.py`：

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

執行：

```bash
python save_davis_tcp.py
```

### 範例 B：透過 TCP 從 DV Viewer 接收 DAVIS 資料

編輯 `save_davis_tcp.py`：

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

執行：

```bash
python save_davis_tcp.py
```

### 範例 C：EVK 與 DAVIS 同時連線的僅事件會話

```bash
python unified_event_gui.py
```

接著在 GUI 中：

1. 點選 `Scan`。
2. 連線已選裝置。
3. 設定輸出資料夾與前綴。
4. 使用 `Record All` 啟動逐次同步輸出。

<a id="development-notes"></a>
## 🛠️ 開發備註

- 目前沒有定義建置系統或套件描述檔（`pyproject.toml`、`requirements.txt` 等檔案目前不存在）。
- 腳本直接使用 Python 進入點執行。
- 設定主要來自腳本常數與 GUI 控件，並非 CLI 參數。
- 廠商 SDK 目錄故意保留在倉庫內：
  - `evk_sdk/`
  - `haikang_sdk/`
- 輸出與資料產物皆在 `.gitignore` 管控，例如：
  - `recordings/`、`davis_output/`、`data/`、`*.aedat4`、`*.raw`、`*.avi`、`*.npz` 等。
- 雙攝影機 GUI 含有預覽視窗定位邏輯，目的是降低預覽彈跳，並避免在 Windows 上蓋住主控制介面。

<a id="troubleshooting"></a>
## 🧭 問題排查

- 啟動時找不到裝置。
  - 檢查相機線材、供電與廠商驅動。
  - 確認設備權限，並確認事件／幀處理運行時已安裝。
- 首次幀預覽導致 GUI 凍結。
  - 先將幀相機與事件相機拔除連線，重開啟再重連並重新掃描。
- DAVIS 網路模式沒有收到資料。
  - 確認 DV Viewer 串流連接埠符合 `EVENTS_PORT` 與 `FRAMES_PORT`。
  - 確認本機環回與 UDP/TCP 流量的防火牆規則。
- `.npz` 或 `.aedat4` 檔案未建立。
  - 確認 `save_davis_tcp.py` 的儲存開關已啟用。
  - 確認輸出目錄具備寫入權限。
- Windows 下視窗位置跳動。
  - 確認已安裝 `pywin32`，且 Python 擁有必要權限。

<a id="roadmap"></a>
## 🗺️ 路線圖

規劃中的文件與可用性改進（目前倉庫內尚未完成）：

1. 將相依項目集中到一個定版的 requirements 檔案。
2. 為非 GUI 擷取流程增加輕量 CLI 替代方案。
3. 擴充 SDK 與韌體相容性矩陣。
4. 增加不依賴硬體的常數與檔案結構邏輯測試。

<a id="contributing"></a>
## 👥 參與貢獻

歡迎協作。

1. 請將修改限制在腳本層流程，不要任意改變執行時擷取行為，除非你有明確且必要的相機流程調整。
2. 除非在 PR 中有明確理由，請保留既有相機執行緒生命週期與輸出目錄慣例。
3. 以至少一次完整的本地擷取流程驗證變更過的路徑／腳本。
4. 在 PR 說明中補上你的前提條件與硬體環境。

## 📩 聯絡我們

若你需要特定硬體組合的整合協助，請在 issue 描述中提供相機型號、作業系統與完整錯誤輸出。

<a id="license"></a>
## 📜 授權

目前版本的倉庫根目錄尚未放置授權檔。公開散佈前請先新增 `LICENSE` 檔案。


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
