[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## 概覽

`SyncImagingSystem` 是一個用於同步幀相機（frame camera）與事件相機（event camera）擷取的 Python 工作區。

目前提供三個主要的活躍工作流程：

1. `DualCamera_separate_transform_davis+evk.py`：幀 + 事件擷取的整合 GUI（Hikrobot/Haikang 幀相機 + EVK 或 DAVIS 事件相機）。
2. `unified_event_gui.py`：適用於 EVK 與 DAVIS 裝置的純事件 GUI。
3. `save_davis_tcp.py`：DAVIS 擷取腳本，支援直接相機模式與 DV Viewer TCP 網路模式。

此儲存庫也包含廠商 SDK/範例套件與歷史原型供參考。

## 功能

| 區域 | 重點 |
|---|---|
| 🎛️ 整合 GUI | 提供整合的幀 + 事件擷取 GUI，具備每裝置控制與統一開始/停止控制。 |
| ⚡ 事件 GUI | 純事件 GUI，支援多裝置連線/預覽/錄製操作。 |
| 📡 DAVIS 來源 | DAVIS 可由直接硬體（`INPUT_MODE = "camera"`）或 DV Viewer 網路串流（`INPUT_MODE = "network"`，預設埠 `7777/7778`）擷取。 |
| 💾 輸出格式 | 錄製輸出包含 `.avi`、`.raw`、`.aedat4`，以及可選的壓縮 `events.npz`。 |
| 🗂️ 執行資料夾組織 | 在 `recordings/` 或 `davis_output/` 下自動建立帶時間戳的執行資料夾。 |
| 🔧 控制項 | 在整合 GUI 工作流程中提供 EVK bias 控制。 |
| 🪞 幀變換 | 在雙相機 GUI 中支援垂直翻轉、水平翻轉與 90 度旋轉。 |
| 🖥️ 視窗管理 | 為多視窗流程提供預覽視窗定位輔助（特別是 Windows）。 |

## 專案結構

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # 主要整合幀+事件 GUI（EVK + DAVIS）
├── DualCamera_separate_transform.py             # 較舊的整合幀+EVK GUI 變體
├── unified_event_gui.py                         # EVK + DAVIS 的純事件 GUI
├── save_davis_tcp.py                            # DAVIS 擷取（相機或 DV Viewer TCP）
├── code-legacy/                                 # 歷史腳本/原型
├── evk_sdk/                                     # Prophesee/Metavision SDK 腳本與範例
├── haikang_sdk/                                 # Hikrobot/Haikang SDK 套件與範例
├── i18n/                                        # 翻譯目錄（目前已有多語檔案）
├── recordings/                                  # 執行期輸出（gitignore，使用時建立）
└── davis_output/                                # save_davis_tcp.py 的執行期輸出（gitignore）
```

## 先決條件

### 硬體

- Hikrobot/Haikang 幀相機（用於幀工作流程）。
- EVK 事件相機與/或 DAVIS 事件相機。

### 作業系統

- Windows 是完整幀相機 SDK 整合與預覽視窗定位行為的主要目標平台。
- Linux/macOS 可執行部分事件流程，但不保證完全一致。

### Python

- Python 3.x。

### Python 套件

在你目前使用的環境中安裝核心執行相依套件：

```bash
pip install numpy opencv-python dv-processing
```

若要使用 EVK 工作流程，請安裝你環境中可用的 Prophesee Metavision Python 套件。

若要在 GUI 預覽中使用 Windows 視窗控制行為：

```bash
pip install pywin32
```

## 安裝

1. 複製（clone）此儲存庫。
2. 在儲存庫根目錄開啟終端機：

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. 建立/啟用你的 Python 環境。
4. 安裝相依套件（見上方）。
5. 確認你的裝置所需的相機 SDK 執行環境/驅動已安裝。

假設說明：目前儲存庫內尚未完整記錄精確的廠商驅動/韌體版本對應，請保留你本機已驗證可用的 SDK 設定。

## 使用方式

### 1) 整合幀 + 事件 GUI（建議的整合流程）

```bash
python DualCamera_separate_transform_davis+evk.py
```

提供內容：

- 啟動時自動掃描幀與事件裝置。
- 幀相機控制：連線、抓取、預覽、錄製、曝光/增益。
- 事件相機控制：連線、擷取、可視化、錄製。
- 統一控制：可同時啟動/停止雙方預覽與錄製。
- GUI 內提供輸出目錄與檔名前綴控制。

預設輸出行為：

| 輸出 | 樣式 |
|---|---|
| 基底目錄 | `recordings/` |
| 執行資料夾 | `<prefix>_<timestamp>/` |
| 幀檔案 | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| 事件檔案（EVK） | `<event_device_label>/<prefix>_<timestamp>.raw` |
| 事件檔案（DAVIS） | `<event_device_label>/output.aedat4`（停止時另產生 `events.npz`） |

### 2) 純事件 GUI

```bash
python unified_event_gui.py
```

預設行為：

- 輸出基底目錄：`recordings/`
- 預設執行前綴：`session`
- 裝置探索：
  - DAVIS 來自 `dv.io.camera.discover()`
  - 若可用 Metavision 模組，EVK 顯示為 `EVK:auto`
- 錄製輸出：
  - EVK：`.raw`
  - DAVIS：`output.aedat4` 與 `events.npz`（若有緩衝事件資料）

### 3) DAVIS 擷取腳本（相機或 DV Viewer TCP）

```bash
python save_davis_tcp.py
```

腳本中的預設關鍵常數：

| 常數 | 預設值 |
|---|---|
| `INPUT_MODE` | `"camera"`（DV Viewer TCP 使用 `"network"`） |
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

## 設定

### `save_davis_tcp.py`

可透過頂層大寫常數調整：

- 輸入來源（`INPUT_MODE`）
- 網路端點（`HOST`、`EVENTS_PORT`、`FRAMES_PORT`）
- 擷取時間（`CAPTURE_SECONDS`）
- 輸出開關（`SAVE_EVENTS_NPZ`、`SAVE_FRAMES_VIDEO`、`SAVE_AEDAT4`）
- 預覽行為（`SHOW_EVENT_PREVIEW`、`PREVIEW_FPS`、`PREVIEW_WINDOW_NAME`）

### `DualCamera_separate_transform_davis+evk.py`

GUI 可調的執行期設定包含：

- 輸出資料夾與檔名前綴
- 幀變換（垂直/水平翻轉、旋轉）
- 幀曝光與增益控制
- 支援時的 EVK bias 控制（`bias_diff`、`bias_diff_off`、`bias_diff_on`、`bias_fo`、`bias_hpf`、`bias_refr`）

### `unified_event_gui.py`

關鍵預設值（可在腳本中修改）：

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 範例

### 範例 A：直接擷取 DAVIS 相機 10 秒

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

### 範例 C：同時連接 EVK 與 DAVIS 的純事件工作階段

```bash
python unified_event_gui.py
```

接著在 GUI 中：

1. 點擊 `Scan`。
2. 連接選定裝置。
3. 設定輸出資料夾/前綴。
4. 使用 `Record All` 開始同步且每次執行分資料夾的輸出。

## 開發備註

- 目前尚未定義建置系統或套件中繼資料（缺少 `pyproject.toml`、`requirements.txt` 等）。
- 腳本以 Python 入口點直接啟動。
- 設定大多為腳本常數與 GUI 控制，而非 CLI 旗標。
- 廠商 SDK 目錄刻意保留於儲存庫中：
  - `evk_sdk/`
  - `haikang_sdk/`
- 輸出/資料產物已加入 gitignore，包括：
  - `recordings/`、`davis_output/`、`data/`、`*.aedat4`、`*.raw`、`*.avi`、`*.npz` 等。
- 雙相機 GUI 包含預覽定位邏輯，旨在減少預覽視窗彈出抖動，並避免遮擋主控制項，尤其在 Windows。

## 疑難排解

| 症狀 | 檢查 / 處置 |
|---|---|
| `dv_processing` 匯入錯誤 | 在目前環境安裝或修復 `dv-processing`。`save_davis_tcp.py` 的 DAVIS 直接相機模式需要 `dv-processing`。 |
| EVK 匯入/模組錯誤（`metavision_*`） | 確認 Metavision SDK/Python 模組已安裝，且可由目前 Python 路徑找到。 |
| 幀相機 SDK 匯入失敗（`MvCameraControl_class` 等） | 驗證 Hikrobot/Haikang SDK 檔案與執行期相依已存在，並確認腳本使用的本機 SDK 路徑有效。 |
| 找不到任何裝置 | 檢查相機連線、供電與權限。重新連接硬體後，再次於 GUI 點擊 `Scan`。 |
| DAVIS 預覽未立即顯示事件 | 在事件封包到達前，預覽視窗可能先顯示空白畫面。 |
| 預覽未保持最上層或位置不如預期 | 在 Windows 安裝 `pywin32`；非 Windows 平台行為受限。 |
| 錄製檔案缺少預期內容 | 部分檔案會在停止時才完成寫入；關閉應用前請先正常停止錄製。 |

## 路線圖

- 新增固定版本相依檔（`requirements.txt` 或 `pyproject.toml`）。
- 為工具邏輯新增硬體無關的自動化測試。
- 擴充已驗證硬體/驅動/版本組合的文件。
- 為目前寫死於腳本的常數新增 CLI 參數。
- 在 `i18n/` 新增多語 README，並由語言選項列連結。

## 貢獻

歡迎貢獻。

建議流程：

1. 為你的變更建立分支。
2. 讓修改聚焦且對硬體安全。
3. 在可用裝置上執行相關腳本進行驗證。
4. 避免提交大型錄製輸出/資料檔。
5. 開啟 PR 並說明：
   - 硬體/軟體環境
   - 相機設定
   - 埠號/檢視器設定（網路流程）
   - 範例輸出路徑/日誌

儲存庫慣例說明：目前提交訊息風格較精簡；請使用簡短祈使句（例如：`Add DAVIS capture docs`）。

## 授權

此儲存庫目前沒有明確的授權檔案。

假設說明：若此專案預期可再散佈，請新增 `LICENSE` 檔並更新本節。

## 致謝

- Prophesee Metavision 生態系（`evk_sdk/` 與相關 Python 模組）。
- 用於 DAVIS 處理的 iniVation/dv-processing 生態系。
- `haikang_sdk/` 內打包的 Hikrobot/Haikang 相機 SDK 資源。
