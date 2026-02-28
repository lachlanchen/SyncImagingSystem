[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## 概要

`SyncImagingSystem` は、フレームカメラとイベントカメラの同期キャプチャを行うための Python ワークスペースです。

主に次の 3 つのアクティブなワークフローを提供します。

1. `DualCamera_separate_transform_davis+evk.py`: フレーム + イベント統合GUI（Hikrobot/Haikang フレームカメラ + EVK または DAVIS イベントカメラ）。
2. `unified_event_gui.py`: EVK と DAVIS デバイス向けのイベント専用GUI。
3. `save_davis_tcp.py`: DAVIS キャプチャスクリプト。カメラ直結モードと DV Viewer TCP ネットワークモードの両方に対応。

このリポジトリには、参照用としてベンダーSDK/サンプル一式や過去のプロトタイプも含まれています。

## 機能

| 項目 | 主な内容 |
|---|---|
| 🎛️ 統合GUI | デバイスごとの操作と共通の開始/停止操作を備えた、フレーム + イベント統合キャプチャGUI。 |
| ⚡ イベントGUI | 複数デバイスの接続/プレビュー/録画に対応したイベント専用GUI。 |
| 📡 DAVIS 入力ソース | DAVIS の入力元として、ハードウェア直結（`INPUT_MODE = "camera"`）または DV Viewer ネットワークストリーム（`INPUT_MODE = "network"`、既定ポート `7777/7778`）を選択可能。 |
| 💾 出力形式 | 録画出力は `.avi`、`.raw`、`.aedat4`、および任意で圧縮 `events.npz` に対応。 |
| 🗂️ 実行フォルダ管理 | `recordings/` または `davis_output/` 配下にタイムスタンプ付き実行フォルダを自動作成。 |
| 🔧 コントロール | 統合GUIワークフローで EVK バイアス制御に対応。 |
| 🪞 フレーム変換 | デュアルカメラGUIで上下反転・左右反転・90度回転に対応。 |
| 🖥️ ウィンドウ配置 | 複数ウィンドウ運用向けのプレビュー配置ヘルパー（特に Windows で有効）。 |

## プロジェクト構成

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # フレーム+イベント統合メインGUI (EVK + DAVIS)
├── DualCamera_separate_transform.py             # 旧式のフレーム+EVK統合GUIバリアント
├── unified_event_gui.py                         # EVK + DAVIS 向けイベント専用GUI
├── save_davis_tcp.py                            # DAVIS キャプチャ（カメラ直結または DV Viewer TCP）
├── code-legacy/                                 # 過去スクリプト/プロトタイプ
├── evk_sdk/                                     # Prophesee/Metavision SDK のスクリプトとサンプル
├── haikang_sdk/                                 # Hikrobot/Haikang SDK バンドルとサンプル
├── i18n/                                        # 翻訳ディレクトリ
├── recordings/                                  # 実行時出力（gitignore、実行時に作成）
└── davis_output/                                # save_davis_tcp.py 用の実行時出力（gitignore）
```

## 前提条件

### ハードウェア

- Hikrobot/Haikang フレームカメラ（フレーム系ワークフロー向け）。
- EVK イベントカメラおよび/または DAVIS イベントカメラ。

### OS

- フレームカメラSDK統合やプレビュー配置動作を含め、主対象は Windows です。
- Linux/macOS でもイベント系パイプラインの一部は動作する可能性がありますが、完全な同等性は保証されません。

### Python

- Python 3.x。

### Python パッケージ

使用中の環境に、コア実行時依存関係をインストールしてください。

```bash
pip install numpy opencv-python dv-processing
```

EVK ワークフローでは、環境で利用可能な Prophesee Metavision の Python パッケージをインストールしてください。

GUI プレビューの Windows ウィンドウ制御動作には次が必要です。

```bash
pip install pywin32
```

## インストール

1. リポジトリをクローンします。
2. リポジトリルートでターミナルを開きます。

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Python 環境を作成/有効化します。
4. 依存関係をインストールします（上記参照）。
5. 使用デバイスに必要なカメラSDKランタイム/ドライバがインストールされていることを確認します。

補足（前提）: ベンダードライバ/ファームウェアの正確な対応バージョン表は、まだリポジトリ内で完全には文書化されていません。ローカルで動作確認済みの SDK 構成を保持してください。

## 使い方

### 1) フレーム + イベント統合GUI（推奨の統合ワークフロー）

```bash
python DualCamera_separate_transform_davis+evk.py
```

提供内容:

- 起動時にフレーム/イベントデバイスを自動スキャン。
- フレームカメラ制御: 接続、取得、プレビュー、録画、露出/ゲイン。
- イベントカメラ制御: 接続、キャプチャ、可視化、録画。
- 共通制御: 両側のプレビューと録画を同時に開始/停止。
- GUI 上で出力ディレクトリとファイル名プレフィックスを設定可能。

既定の出力動作:

| 出力 | パターン |
|---|---|
| ベースディレクトリ | `recordings/` |
| 実行フォルダ | `<prefix>_<timestamp>/` |
| フレームファイル | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| イベントファイル (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| イベントファイル (DAVIS) | `<event_device_label>/output.aedat4` (+ 停止時に `events.npz`) |

### 2) イベント専用GUI

```bash
python unified_event_gui.py
```

既定動作:

- 出力ベースディレクトリ: `recordings/`
- 既定の実行プレフィックス: `session`
- デバイス検出:
  - DAVIS: `dv.io.camera.discover()`
  - EVK: Metavision モジュールが利用可能な場合 `EVK:auto`
- 録画出力:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` と `events.npz`（イベントバッファが存在する場合）

### 3) DAVIS キャプチャスクリプト（カメラ直結または DV Viewer TCP）

```bash
python save_davis_tcp.py
```

スクリプト内の主要な既定定数:

| 定数 | 既定値 |
|---|---|
| `INPUT_MODE` | `"camera"`（DV Viewer TCP は `"network"`） |
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
- 一般的なファイル: `events.npz`、`frames.avi`、`output.aedat4`

## 設定

### `save_davis_tcp.py`

トップレベルの大文字定数を調整して次を設定します。

- 入力ソース（`INPUT_MODE`）
- ネットワークエンドポイント（`HOST`, `EVENTS_PORT`, `FRAMES_PORT`）
- キャプチャ時間（`CAPTURE_SECONDS`）
- 出力トグル（`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`）
- プレビュー動作（`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`）

### `DualCamera_separate_transform_davis+evk.py`

GUI から操作可能な実行時設定:

- 出力フォルダとファイル名プレフィックス
- フレーム変換（上下/左右反転、回転）
- フレーム露出とゲイン制御
- 対応時の EVK バイアス制御（`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`）

### `unified_event_gui.py`

主要な既定値（スクリプトで編集可能）:

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 例

### 例 A: DAVIS カメラ直結で 10 秒間キャプチャ

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

### 例 B: DV Viewer から TCP 経由で DAVIS データを受信

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

### 例 C: EVK と DAVIS の両方を接続したイベント専用セッション

```bash
python unified_event_gui.py
```

その後 GUI で:

1. `Scan` をクリック。
2. 選択したデバイスを接続。
3. 出力フォルダ/プレフィックスを設定。
4. `Record All` で同期された実行フォルダ出力を開始。

## 開発メモ

- 現時点ではビルドシステムやパッケージメタデータは未定義です（`pyproject.toml`、`requirements.txt` などは未配置）。
- スクリプトは Python エントリポイントを直接実行します。
- 設定は主にスクリプト定数と GUI 制御で、CLI フラグ中心ではありません。
- ベンダーSDKディレクトリは意図的にリポジトリ内に保持しています。
  - `evk_sdk/`
  - `haikang_sdk/`
- 出力/データ生成物は `gitignore` 済みです。
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz` など
- デュアルカメラGUIには、特に Windows 上でプレビュー表示時のポップインを抑え、メイン操作部を隠しにくくするためのウィンドウ配置ロジックが含まれています。

## トラブルシューティング

| 症状 | 確認事項 / 対処 |
|---|---|
| `dv_processing` の import エラー | 使用中の環境で `dv-processing` をインストールまたは修復してください。`save_davis_tcp.py` の DAVIS カメラ直結モードには `dv-processing` が必要です。 |
| EVK の import/モジュールエラー（`metavision_*`） | Metavision SDK/Python モジュールがインストールされ、Python パス上にあることを確認してください。 |
| フレームカメラSDKの import 失敗（`MvCameraControl_class` など） | Hikrobot/Haikang SDK ファイルとランタイム依存関係が揃っているか確認してください。スクリプトで使用しているローカル SDK パスが有効かも確認してください。 |
| デバイスが見つからない | カメラ接続・電源・権限を確認してください。ハードウェア再接続後に GUI の `Scan` を再実行してください。 |
| DAVIS プレビューにすぐイベントが表示されない | イベントパケット到着まで、プレビューウィンドウが空フレームで開く場合があります。 |
| プレビューが常に最前面にならない/期待位置に出ない | Windows では `pywin32` をインストールしてください。非 Windows では動作に制限があります。 |
| 録画ファイルに期待した内容がない | 停止時に確定されるファイルがあります。アプリ終了前に録画を正常停止してください。 |

## ロードマップ

- 依存関係固定ファイル（`requirements.txt` または `pyproject.toml`）を追加。
- ユーティリティロジック向けに、ハードウェア非依存の自動テストを追加。
- 検証済みハードウェア/ドライバ/バージョン組み合わせのドキュメントを拡充。
- 現在スクリプト内にハードコードされている定数へ CLI 引数対応を追加。
- `i18n/` に多言語READMEを追加し、言語オプション行からリンク。

## コントリビュート

コントリビューションを歓迎します。

推奨ワークフロー:

1. 変更用ブランチを作成します。
2. 変更は焦点を絞り、ハードウェア安全性を意識します。
3. 利用可能なデバイスで対象スクリプトを実行して検証します。
4. 大きな生成録画/データのコミットは避けます。
5. PR には次を記載してください。
   - ハードウェア/ソフトウェア環境
   - カメラ構成
   - ポート/ビューア設定（ネットワークワークフローの場合）
   - 出力パス/ログ例

リポジトリ慣例メモ: 現在のコミットメッセージ規約は軽量です。短い命令形メッセージを使用してください（例: `Add DAVIS capture docs`）。

## ライセンス

このリポジトリには、現時点で明示的なライセンスファイルが存在しません。

補足（前提）: 再配布を意図する場合は、`LICENSE` ファイルを追加し、このセクションを更新してください。

## 謝辞

- Prophesee Metavision エコシステム（`evk_sdk/` および関連 Python モジュール）。
- DAVIS 取り扱いのための iniVation/dv-processing エコシステム。
- `haikang_sdk/` 配下に同梱されている Hikrobot/Haikang カメラSDKリソース。
