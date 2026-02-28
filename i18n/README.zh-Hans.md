[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` 是一个面向 EVK/DAVIS 和 Hikrobot/Haikang 相机的同步帧相机与事件相机采集 Python 工作区，围绕可落地的实拍流程组织。

<a id="usage"></a>
## 🧭 快速导航

| 部分 | 链接 |
|---|---|
| 主要流程 | [使用说明](#usage) |
| 项目设置 | [安装](#installation) |
| 故障排查 | [故障排查](#troubleshooting) |
| 参与说明 | [贡献指南](#contributing) |
| 支持 | [❤️ Support](#-support) |

<a id="overview"></a>
## 📌 概览

`SyncImagingSystem` 是一个用于同步帧相机和事件相机采集的 Python 工作区。

它提供了三条主要的可用工作流：

| 脚本 | 用途 | 说明 |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | 统一帧 + 事件 GUI | 支持 Hikrobot/Haikang 的帧相机与 EVK 或 DAVIS 事件相机 |
| `unified_event_gui.py` | 事件独立 GUI | EVK + DAVIS 的自动检测与逐次运行记录 |
| `save_davis_tcp.py` | DAVIS 采集脚本 | 支持直接相机模式和 DV Viewer TCP 网络模式 |

仓库还包含供应商 SDK/示例集合，以及供参考的历史原型。

<a id="features"></a>
## 🚀 特性

| 模块 | 要点 |
|---|---|
| 🎛️ 统一 GUI | 带每设备控制与统一开始/停止的帧 + 事件统一采集界面 |
| ⚡ 事件 GUI | 支持多设备连接、预览与录制的事件独立界面 |
| 📡 DAVIS 数据源 | 支持直接硬件模式（`INPUT_MODE = "camera"`）或 DV Viewer 网络流模式（`INPUT_MODE = "network"`，默认端口 `7777/7778`） |
| 💾 输出格式 | 录制产物包括 `.avi`、`.raw`、`.aedat4`，以及可选压缩 `events.npz` |
| 🗂️ 运行目录 | 在 `recordings/` 或 `davis_output/` 下自动按时间戳创建运行目录 |
| 🔧 控制项 | 统一 GUI 中提供 EVK 的偏置控制 |
| 🪞 帧图像变换 | 双相机 GUI 中支持上下翻转、左右翻转和 90 度旋转 |
| 🖥️ 窗口 | 预览窗口布局助手，适配多窗口场景（尤其是 Windows） |

<a id="project-structure"></a>
## 🧩 项目结构

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
## 🛠️ 先决条件

### 硬件

- Hikrobot/Haikang 帧相机（用于帧采集流程）。
- EVK 事件相机和/或 DAVIS 事件相机。

### 系统

- Windows 是完整帧相机 SDK 集成与预览窗口摆放行为的主要目标环境。
- Linux/macOS 可运行部分事件链路，但完整功能一致性目前不能保证。

### Python

- Python 3.x。

### Python 依赖

在当前环境中安装核心运行时依赖：

```bash
pip install numpy opencv-python dv-processing
```

对于 EVK 流程，请安装环境中可用的 Prophesee Metavision Python 包。

为 GUI 预览在 Windows 下的窗口控制行为，安装：

```bash
pip install pywin32
```

<a id="installation"></a>
## 🧪 安装

1. 克隆仓库。
2. 在仓库根目录打开终端：

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. 创建并激活你的 Python 环境。
4. 安装依赖（见上文）。
5. 为你的设备安装对应的相机 SDK 运行时/驱动。

说明：仓库内尚未完整记录厂商驱动和固件版本矩阵；请保留你本地已验证可用的 SDK 环境。

<a id="usage"></a>
## ▶️ 使用说明

### 1) 统一帧 + 事件 GUI（推荐的集成流程）

```bash
python DualCamera_separate_transform_davis+evk.py
```

提供能力：

- 启动时自动扫描帧相机与事件相机设备。
- 帧相机控制：连接、抓帧、预览、录制、曝光/增益调节。
- 事件相机控制：连接、采集、可视化、录制。
- 统一控制：为两侧提供同步预览与录制开始/停止。
- 在 GUI 中控制输出目录和文件名前缀。

默认输出行为：

| 输出项 | 规则 |
|---|---|
| 基础目录 | `recordings/` |
| 运行目录 | `<prefix>_<timestamp>/` |
| 帧文件 | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| 事件文件（EVK） | `<event_device_label>/<prefix>_<timestamp>.raw` |
| 事件文件（DAVIS） | `<event_device_label>/output.aedat4`（停止时可附带 `events.npz`） |

### 2) 事件独立 GUI

```bash
python unified_event_gui.py
```

默认行为：

- 输出基础目录：`recordings/`
- 默认运行前缀：`session`
- 设备发现：
  - DAVIS 来自 `dv.io.camera.discover()`
  - EVK 当 Metavision 模块可用时显示为 `EVK:auto`
- 录制输出：
  - EVK：`.raw`
  - DAVIS：`output.aedat4` 与 `events.npz`（若缓冲事件存在）

### 3) DAVIS 采集脚本（相机模式或 DV Viewer TCP）

```bash
python save_davis_tcp.py
```

脚本默认关键常量：

| 常量 | 默认值 |
|---|---|
| `INPUT_MODE` | `"camera"`（DV Viewer TCP 为 `"network"`） |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

输出目录格式：

- `davis_output/<YYYYmmdd_HHMMSS>/`
- 常见文件：`events.npz`、`frames.avi`、`output.aedat4`

<a id="configuration"></a>
## ⚙️ 配置

### `save_davis_tcp.py`

调整脚本顶部的大写常量即可配置：

- 输入源（`INPUT_MODE`）
- 网络端点（`HOST`、`EVENTS_PORT`、`FRAMES_PORT`）
- 采集时长（`CAPTURE_SECONDS`）
- 输出开关（`SAVE_EVENTS_NPZ`、`SAVE_FRAMES_VIDEO`、`SAVE_AEDAT4`）
- 预览行为（`SHOW_EVENT_PREVIEW`、`PREVIEW_FPS`、`PREVIEW_WINDOW_NAME`）

### `DualCamera_separate_transform_davis+evk.py`

GUI 暴露的运行设置包括：

- 输出文件夹与文件名前缀
- 帧图像变换（上下/左右翻转、旋转）
- 帧曝光与增益控制
- 当支持时 EVK 偏置参数（`bias_diff`、`bias_diff_off`、`bias_diff_on`、`bias_fo`、`bias_hpf`、`bias_refr`）

### `unified_event_gui.py`

可编辑关键默认值（在脚本内）：

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

<a id="examples"></a>
## 💡 示例

### 示例 A：直接 DAVIS 相机采集 10 秒

编辑 `save_davis_tcp.py`：

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

运行：

```bash
python save_davis_tcp.py
```

### 示例 B：通过 TCP 从 DV Viewer 接收 DAVIS 数据

编辑 `save_davis_tcp.py`：

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

运行：

```bash
python save_davis_tcp.py
```

### 示例 C：同时连接 EVK 与 DAVIS 的事件独立会话

```bash
python unified_event_gui.py
```

然后在 GUI 中：

1. 点击 `Scan`。
2. 连接所选设备。
3. 设置输出文件夹与前缀。
4. 使用 `Record All` 启动每次运行的同步输出。

<a id="development-notes"></a>
## 🛠️ 开发说明

- 当前尚未定义构建系统或包元数据（`pyproject.toml`、`requirements.txt` 等文件缺失）。
- 脚本采用 Python 入口直接运行。
- 配置主要依赖脚本常量和 GUI 控件，不走 CLI 参数。
- SDK 目录按仓库内置方式保留：
  - `evk_sdk/`
  - `haikang_sdk/`
- 输出和数据制品已纳入 gitignore，包括：
  - `recordings/`、`davis_output/`、`data/`、`*.aedat4`、`*.raw`、`*.avi`、`*.npz` 等。
- 双相机 GUI 内置了预览窗口摆放逻辑，旨在减少预览窗口弹跳，并避免在 Windows 上遮挡主控界面。

<a id="troubleshooting"></a>
## 🧭 故障排查

- 启动时未检测到设备。
  - 检查相机线缆、供电与厂商驱动。
  - 确认设备权限，并且事件/帧处理运行时已安装。
- 首次帧预览时 GUI 卡死。
  - 先断开帧相机与事件相机后启动，再重新连接并重新扫描。
- DAVIS 网络模式无数据。
  - 确认 DV Viewer 的流端口与 `EVENTS_PORT`/`FRAMES_PORT` 一致。
  - 检查本地回环及 UDP/TCP 流量的防火墙规则。
- `.npz` 或 `.aedat4` 未生成。
  - 确认 `save_davis_tcp.py` 中的保存开关已启用。
  - 确认输出目录具有写权限。
- Windows 下窗口位置抖动。
  - 确认已安装 `pywin32`，并且 Python 具备必要权限。

<a id="roadmap"></a>
## 🗺️ 路线图

计划中的文档和可用性改进（仓库内暂未完全完成）：

1. 将依赖集中到固定版本的 requirements 文件。
2. 为非 GUI 采集模式增加轻量级 CLI 替代方案。
3. 扩展 SDK 与固件兼容性矩阵。
4. 增加与硬件解耦、稳定的常量与文件布局逻辑测试。

<a id="contributing"></a>
## 👥 贡献

欢迎参与贡献。

1. 将变更限定在脚本级流程，不要随意修改运行时采集行为，除非你确有意改变某条相机路径。
2. 除非 PR 中说明充分理由，保留现有相机线程生命周期和输出目录布局约定。
3. 至少使用一次完整的本地采集运行验证变更的路径/脚本。
4. 在 PR 描述中补充假设和硬件上下文信息。

## 📩 联系我们

如果你需要特定硬件组合的集成帮助，请在 issue 描述中提供你的相机型号、操作系统以及完整错误输出。

<a id="license"></a>
## 📜 许可

仓库当前版本在根目录没有许可证文件。请在公开分发前补充 `LICENSE` 文件。


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
