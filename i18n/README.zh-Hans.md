[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## 概览

`SyncImagingSystem` 是一个用于同步采集帧相机与事件相机数据的 Python 工作区。

它提供三个主要的在用工作流：

1. `DualCamera_separate_transform_davis+evk.py`：用于帧 + 事件采集的统一 GUI（Hikrobot/Haikang 帧相机 + EVK 或 DAVIS 事件相机）。
2. `unified_event_gui.py`：面向 EVK 与 DAVIS 设备的纯事件 GUI。
3. `save_davis_tcp.py`：DAVIS 采集脚本，支持相机直连模式与 DV Viewer TCP 网络模式。

仓库中还包含厂商 SDK/示例包以及历史原型脚本供参考。

## 功能特性

| 区域 | 亮点 |
|---|---|
| 🎛️ 统一 GUI | 统一的帧 + 事件采集 GUI，支持按设备控制与统一启动/停止控制。 |
| ⚡ 事件 GUI | 纯事件 GUI，支持多设备连接/预览/录制操作。 |
| 📡 DAVIS 数据源 | DAVIS 可从直连硬件采集（`INPUT_MODE = "camera"`），也可从 DV Viewer 网络流采集（`INPUT_MODE = "network"`，默认端口 `7777/7778`）。 |
| 💾 输出格式 | 录制输出包含 `.avi`、`.raw`、`.aedat4`，以及可选压缩 `events.npz`。 |
| 🗂️ 运行组织 | 在 `recordings/` 或 `davis_output/` 下自动按时间戳创建运行目录。 |
| 🔧 控制项 | 在统一 GUI 工作流中提供 EVK bias 控制。 |
| 🪞 帧变换 | 双相机 GUI 支持垂直翻转、水平翻转和 90 度旋转。 |
| 🖥️ 窗口管理 | 为多窗口工作流提供预览窗口定位辅助（尤其在 Windows 上）。 |

## 项目结构

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
├── i18n/                                        # Translation directory (multilingual READMEs)
├── recordings/                                  # Runtime output (gitignored, created on use)
└── davis_output/                                # Runtime output for save_davis_tcp.py (gitignored)
```

## 先决条件

### 硬件

- Hikrobot/Haikang 帧相机（用于帧工作流）。
- EVK 事件相机和/或 DAVIS 事件相机。

### 操作系统

- Windows 是完整帧相机 SDK 集成与预览窗口定位行为的主要目标平台。
- Linux/macOS 可能可运行部分事件管线，但不保证完全一致的功能表现。

### Python

- Python 3.x。

### Python 包

在当前激活环境中安装核心运行时依赖：

```bash
pip install numpy opencv-python dv-processing
```

对于 EVK 工作流，请安装环境中可用的 Prophesee Metavision Python 包。

对于 GUI 预览中的 Windows 窗口控制行为：

```bash
pip install pywin32
```

## 安装

1. 克隆仓库。
2. 在仓库根目录打开终端：

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. 创建并激活你的 Python 环境。
4. 安装依赖（见上文）。
5. 确认已为设备安装所需的相机 SDK 运行时/驱动。

假设说明：仓库内尚未完整记录厂商驱动/固件的精确版本矩阵；请保留你本地已验证可用的 SDK 配置。

## 使用方法

### 1) 统一帧 + 事件 GUI（推荐的一体化工作流）

```bash
python DualCamera_separate_transform_davis+evk.py
```

提供内容：

- 启动时自动扫描帧设备与事件设备。
- 帧相机控制：连接、抓取、预览、录制、曝光/增益。
- 事件相机控制：连接、采集、可视化、录制。
- 统一控制：同时启动/停止两侧预览与录制。
- GUI 中可设置输出目录与文件名前缀。

默认输出行为：

| 输出 | 模式 |
|---|---|
| 基础目录 | `recordings/` |
| 运行目录 | `<prefix>_<timestamp>/` |
| 帧文件 | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| 事件文件（EVK） | `<event_device_label>/<prefix>_<timestamp>.raw` |
| 事件文件（DAVIS） | `<event_device_label>/output.aedat4`（停止时额外生成 `events.npz`） |

### 2) 纯事件 GUI

```bash
python unified_event_gui.py
```

默认行为：

- 输出基础目录：`recordings/`
- 默认运行前缀：`session`
- 设备发现：
  - DAVIS 来自 `dv.io.camera.discover()`
  - 若 Metavision 模块可用，EVK 显示为 `EVK:auto`
- 录制输出：
  - EVK：`.raw`
  - DAVIS：`output.aedat4` 与 `events.npz`（若存在缓冲事件）

### 3) DAVIS 采集脚本（相机直连或 DV Viewer TCP）

```bash
python save_davis_tcp.py
```

脚本中的默认关键常量：

| 常量 | 默认值 |
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

输出目录格式：

- `davis_output/<YYYYmmdd_HHMMSS>/`
- 典型文件：`events.npz`、`frames.avi`、`output.aedat4`

## 配置

### `save_davis_tcp.py`

可通过顶部大写常量进行配置：

- 输入源（`INPUT_MODE`）
- 网络端点（`HOST`、`EVENTS_PORT`、`FRAMES_PORT`）
- 采集时长（`CAPTURE_SECONDS`）
- 输出开关（`SAVE_EVENTS_NPZ`、`SAVE_FRAMES_VIDEO`、`SAVE_AEDAT4`）
- 预览行为（`SHOW_EVENT_PREVIEW`、`PREVIEW_FPS`、`PREVIEW_WINDOW_NAME`）

### `DualCamera_separate_transform_davis+evk.py`

GUI 可在运行时设置：

- 输出文件夹与文件名前缀
- 帧变换（垂直/水平翻转、旋转）
- 帧曝光与增益控制
- 支持时的 EVK bias 控制（`bias_diff`、`bias_diff_off`、`bias_diff_on`、`bias_fo`、`bias_hpf`、`bias_refr`）

### `unified_event_gui.py`

关键默认值（可在脚本中编辑）：

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 示例

### 示例 A：直连 DAVIS 相机采集 10 秒

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

### 示例 C：同时连接 EVK 与 DAVIS 的纯事件会话

```bash
python unified_event_gui.py
```

然后在 GUI 中：

1. 点击 `Scan`。
2. 连接所选设备。
3. 设置输出文件夹/前缀。
4. 使用 `Record All` 启动同步的按次运行输出目录。

## 开发说明

- 当前尚未定义构建系统或包元数据（缺少 `pyproject.toml`、`requirements.txt` 等）。
- 脚本通过 Python 入口直接启动。
- 配置主要通过脚本常量和 GUI 控件完成，而非 CLI 参数。
- 厂商 SDK 目录有意保留在仓库中：
  - `evk_sdk/`
  - `haikang_sdk/`
- 输出/数据产物已加入 gitignore，包括：
  - `recordings/`、`davis_output/`、`data/`、`*.aedat4`、`*.raw`、`*.avi`、`*.npz` 等。
- 双相机 GUI 包含预览窗口定位逻辑，目的是减少预览窗口弹出抖动，并避免遮挡主控件，尤其在 Windows 上。

## 故障排查

| 症状 | 检查 / 处理 |
|---|---|
| `dv_processing` 导入错误 | 在当前环境中安装或修复 `dv-processing`。`save_davis_tcp.py` 的 DAVIS 相机直连模式依赖 `dv-processing`。 |
| EVK 导入/模块错误（`metavision_*`） | 确认 Metavision SDK/Python 模块已安装，并位于 Python 路径中。 |
| 帧相机 SDK 导入失败（`MvCameraControl_class` 等） | 检查 Hikrobot/Haikang SDK 文件与运行时依赖是否齐全。确认脚本使用的本地 SDK 路径有效。 |
| 未发现设备 | 检查相机连接、电源与权限。硬件重连后在 GUI 中再次执行 `Scan`。 |
| DAVIS 预览未立即显示事件 | 在事件包到达前，预览窗口可能会先显示空白帧。 |
| 预览窗口未保持置顶或位置不符合预期 | 在 Windows 上安装 `pywin32`；在非 Windows 平台上该行为能力有限。 |
| 录制文件缺少预期内容 | 部分文件在停止时才会最终写入；关闭应用前请先正常停止录制。 |

## 路线图

- 增加固定依赖文件（`requirements.txt` 或 `pyproject.toml`）。
- 为通用工具逻辑增加硬件无关的自动化测试。
- 扩展经过验证的硬件/驱动/版本组合文档。
- 为当前硬编码的脚本常量增加 CLI 参数。
- 在 `i18n/` 中补充多语言 README，并在语言选项行中链接。

## 贡献

欢迎贡献。

建议工作流：

1. 为你的修改创建分支。
2. 保持修改聚焦且对硬件安全。
3. 使用可用设备运行相关脚本进行验证。
4. 避免提交体积较大的录制数据/生成数据。
5. 提交 PR 时说明：
   - 硬件/软件环境
   - 相机配置
   - 端口/查看器设置（网络工作流）
   - 示例输出路径/日志

仓库约定说明：当前提交信息风格较轻量；建议使用简短祈使句（例如：`Add DAVIS capture docs`）。

## 许可证

该仓库当前没有明确的许可证文件。

假设说明：如果项目计划用于再分发，请添加 `LICENSE` 文件并更新本节。

## 致谢

- Prophesee Metavision 生态（`evk_sdk/` 及相关 Python 模块）。
- 用于 DAVIS 处理的 iniVation/dv-processing 生态。
- `haikang_sdk/` 下打包的 Hikrobot/Haikang 相机 SDK 资源。
