[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` は、同期フレームカメラとイベントカメラのキャプチャに対応した Python ワークスペースで、EVK/DAVIS と Hikrobot/Haikang カメラ向けの実運用ワークフローを中心に構成されたプロジェクトです。

## 🧭 Quick Navigator

| Section | Link |
|---|---|
| Primary workflows | [Usage](#usage) |
| Project setup | [Installation](#installation) |
| Troubleshooting | [Troubleshooting](#troubleshooting) |
| Contribution details | [Contributing](#contributing) |
| Support | [❤️ Support](#-support) |

## 📌 Overview

`SyncImagingSystem` は、フレームカメラとイベントカメラを同期してキャプチャするための Python ワークスペースです。

以下の 3 つの主要なアクティブワークフローを提供します。

| Script | Purpose | Notes |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | Unified frame + event GUI | Hikrobot/Haikang フレームカメラ + EVK または DAVIS イベントカメラをサポート |
| `unified_event_gui.py` | Event-only GUI | EVK + DAVIS を自動検出で接続し、実行ごとの保存を行う |
| `save_davis_tcp.py` | DAVIS capture script | 直接カメラ接続モードと DV Viewer TCP ネットワークモードをサポート |

リポジトリには、参照用のベンダー SDK/サンプル群と履歴的なプロトタイプも含まれています。

## 🚀 Features

| Area | Highlights |
|---|---|
| 🎛️ Unified GUI | デバイス別コントロールと統一した開始/停止制御を持つ、フレーム + イベント統合 GUI |
| ⚡ Event GUI | 複数デバイスの接続・プレビュー・録画操作に対応したイベント専用 GUI |
| 📡 DAVIS Sources | 直接ハードウェア (`INPUT_MODE = "camera"`) か DV Viewer ネットワークストリーム (`INPUT_MODE = "network"`, デフォルトポート `7777/7778`) から DAVIS を取得 |
| 💾 Output Formats | 録画出力は `.avi`、`.raw`、`.aedat4`、および任意の圧縮 `events.npz` |
| 🗂️ Run Organization | `recordings/` または `davis_output/` 配下にタイムスタンプ付き実行フォルダを自動整理 |
| 🔧 Controls | 統合 GUI ワークフローで EVK バイアス制御を提供 |
| 🪞 Frame Transform | デュアルカメラ GUI で上下反転・左右反転・90 度回転に対応 |
| 🖥️ Windowing | 複数ウィンドウの運用向けにプレビュー配置の調整支援（主に Windows） |

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

- Hikrobot/Haikang フレームカメラ（フレーム系ワークフロー用）。
- EVK イベントカメラと/または DAVIS イベントカメラ。

### OS

- Windows は、フレームカメラ SDK 統合とプレビュー配置挙動の完全対象です。
- Linux/macOS はイベント系の一部で動作する可能性がありますが、完全互換は保証されません。

### Python

- Python 3.x.

### Python packages

実行環境に必要な主要依存をインストールします。

```bash
pip install numpy opencv-python dv-processing
```

EVK ワークフローでは、環境で利用可能な Prophesee Metavision Python パッケージをインストールしてください。

GUI プレビューの Windows ウィンドウ制御挙動のために:

```bash
pip install pywin32
```

## 🧪 Installation

1. リポジトリをクローンします。
2. リポジトリルートで端末を開きます。

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Python 環境を作成/有効化します。
4. 依存関係をインストールします（前述参照）。
5. 使用デバイス向けのカメラ SDK ランタイム/ドライバをインストール済みにします。

補足: ベンダー側のドライバ/ファームウェアの厳密なバージョン対応表はまだリポジトリ内で完全に文書化されていません。ローカルで動作確認済みの SDK 構成は維持してください。

## ▶️ Usage

### 1) Unified frame + event GUI (recommended integrated workflow)

```bash
python DualCamera_separate_transform_davis+evk.py
```

提供機能:

- 起動時にフレーム／イベントデバイスを自動スキャン。
- フレームカメラ制御: 接続、取得、プレビュー、録画、露出/ゲイン。
- イベントカメラ制御: 接続、キャプチャ、可視化、録画。
- 統合制御: 両系統を同時にプレビュー開始/停止および録画開始/停止。
- GUI での出力フォルダとファイル名接頭辞の制御。

既定の出力動作:

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

既定動作:

- 出力ベースディレクトリ: `recordings/`
- 既定実行接頭辞: `session`
- デバイス検出:
  - DAVIS: `dv.io.camera.discover()`
  - EVK: Metavision モジュールが利用可能な場合 `EVK:auto`
- 録画出力:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` と `events.npz`（バッファ済みイベントがある場合）

### 3) DAVIS capture script (camera or DV Viewer TCP)

```bash
python save_davis_tcp.py
```

スクリプト内の既定定数:

| Constant | Default |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` は DV Viewer TCP 用) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

出力ディレクトリ形式:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- 一般的なファイル: `events.npz`, `frames.avi`, `output.aedat4`

## ⚙️ Configuration

### `save_davis_tcp.py`

トップレベルの大文字定数を調整して以下を設定します。

- 入力ソース (`INPUT_MODE`)
- ネットワークエンドポイント (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- キャプチャ時間 (`CAPTURE_SECONDS`)
- 出力トグル (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- プレビュー設定 (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

GUI から変更可能な実行時設定:

- 出力フォルダとファイル名接頭辞
- フレーム変換（上下反転/左右反転、90 度回転）
- フレーム露出とゲインの制御
- 対応時の EVK バイアス制御 (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`)

### `unified_event_gui.py`

主要な既定値（スクリプト内で編集可能）:

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 💡 Examples

### Example A: Direct DAVIS camera capture for 10 seconds

`save_davis_tcp.py` を編集:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

実行:

```bash
python save_davis_tcp.py
```

### Example B: Receive DAVIS data from DV Viewer via TCP

`save_davis_tcp.py` を編集:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

実行:

```bash
python save_davis_tcp.py
```

### Example C: Event-only session with both EVK and DAVIS connected

```bash
python unified_event_gui.py
```

その後 GUI で:

1. `Scan` をクリック。
2. 選択したデバイスを接続。
3. 出力フォルダ/接頭辞を設定。
4. `Record All` を使って実行ごとの同期出力を開始。

## 🛠️ Development Notes

- 現時点でビルドシステムやパッケージメタデータは未定義です（`pyproject.toml`、`requirements.txt` などは未配置）。
- スクリプトは Python のエントリポイントで直接起動します。
- 設定は主にスクリプト定数と GUI コントロールで管理され、CLI フラグ中心ではありません。
- ベンダー SDK ディレクトリは意図的にリポジトリ内へ同梱されています。
  - `evk_sdk/`
  - `haikang_sdk/`
- 出力・データ生成物は `gitignore` されます。
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz` など
- デュアルカメラ GUI には、特に Windows 上でプレビューのポップインを抑え、メイン操作部を隠しにくくするためのウィンドウ配置ロジックが含まれます。

## 🧭 Troubleshooting

- 起動時にデバイスが見つからない
  - カメラのケーブル、電源、ベンダー側ドライバを確認してください。
  - デバイス権限とイベント/フレーム実行環境がインストール済みか確認してください。
- GUI が起動直後にフリーズする
  - フレーム／イベントデバイスをいったんすべて切断した状態で起動し、再接続後に再スキャンしてください。
- DAVIS ネットワークモードでデータが受信されない
  - DV Viewer のストリームポートが `EVENTS_PORT`/`FRAMES_PORT` と一致しているか確認してください。
  - ローカルループバックと UDP/TCP 通信に対するファイアウォール設定を確認してください。
- `.npz` または `.aedat4` ファイルが作成されない
  - `save_davis_tcp.py` の保存トグルが有効になっているか確認してください。
  - 出力先ディレクトリの書き込み権限を確認してください。
- Windows でウィンドウ位置が跳ねる
  - `pywin32` がインストール済みで、Python に必要な権限があることを確認してください。

## 🗺️ Roadmap

リポジトリ内でまだ未完了の、ドキュメント主導/使いやすさ向上項目:

1. 依存関係を固定した要件ファイルの導入。
2. 非 GUI キャプチャ向けの軽量 CLI を追加。
3. SDK とファームウェアの互換性表を拡充。
4. 定数とファイル構成ロジックを検証する、ハードウェア非依存の安全テストを追加。

## 👥 Contributing

コントリビューションは歓迎します。

1. 変更は対象スクリプトレベルのワークフローに限定し、意図しないカメラパスの実行動作変更は避けてください。
2. PR で正当な理由がない場合、既存のカメラスレッドのライフサイクルと出力フォルダ構成は維持してください。
3. 変更したパス／スクリプトは、少なくとも 1 回のローカルでの実機キャプチャで検証してください。
4. PR 説明に前提条件とハードウェア構成を記載してください。

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📩 Contact

特定のハードウェア構成向けに統合のサポートが必要な場合は、Issue にカメラモデル、OS、エラー全文を記載してください。

## 📜 License

本ドラフト作成時点では、リポジトリルートにライセンスファイルはありません。再配布を想定する場合は、`LICENSE` ファイルを追加してください。
