[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` là workspace Python cho việc thu thập đồng bộ giữa camera frame và camera sự kiện, được tổ chức quanh các workflow thực tế cho EVK/DAVIS và Hikrobot/Haikang.

## 🧭 Điều hướng nhanh

| Mục | Liên kết |
|---|---|
| Quy trình làm việc chính | [Sử dụng](#usage) |
| Thiết lập dự án | [Cài đặt](#installation) |
| Khắc phục sự cố | [Khắc phục sự cố](#troubleshooting) |
| Chi tiết đóng góp | [Đóng góp](#contributing) |
| Hỗ trợ | [❤️ Support](#support) |

## 📌 Tổng quan

`SyncImagingSystem` là workspace Python cho thu thập frame-camera và event-camera đồng bộ.

Nó cung cấp ba workflow hoạt động chính:

| Tập lệnh | Mục đích | Ghi chú |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | GUI hợp nhất frame + event | Hỗ trợ camera frame Hikrobot/Haikang + event camera EVK hoặc DAVIS |
| `unified_event_gui.py` | GUI chỉ event | Thu thập EVK + DAVIS với auto-detect và ghi theo từng phiên |
| `save_davis_tcp.py` | Script thu thập DAVIS | Hỗ trợ chế độ camera trực tiếp và chế độ mạng DV Viewer TCP |

Kho lưu trữ cũng chứa các gói SDK mẫu của nhà cung cấp và các bản prototype lịch sử để tham khảo.

## 🚀 Tính năng

| Khu vực | Điểm nổi bật |
|---|---|
| 🎛️ GUI hợp nhất | GUI thu thập frame + event hợp nhất với điều khiển riêng theo từng thiết bị và nút start/stop thống nhất. |
| ⚡ GUI Event | GUI chỉ event với thao tác connect/preview/record đa thiết bị. |
| 📡 Nguồn DAVIS | Thu thập DAVIS từ phần cứng trực tiếp (`INPUT_MODE = "camera"`) hoặc luồng DV Viewer qua mạng (`INPUT_MODE = "network"`, cổng mặc định `7777/7778`). |
| 💾 Định dạng đầu ra | Kết quả ghi bao gồm `.avi`, `.raw`, `.aedat4`, và `events.npz` nén tùy chọn. |
| 🗂️ Tổ chức phiên | Tự động tạo thư mục phiên theo timestamp trong `recordings/` hoặc `davis_output/`. |
| 🔧 Điều khiển | Điều khiển bias EVK trong các workflow GUI hợp nhất. |
| 🪞 Biến đổi frame | Lật dọc, lật ngang và xoay 90 độ trong GUI dual-camera. |
| 🖥️ Sắp xếp cửa sổ | Trợ giúp đặt cửa sổ preview cho workflows nhiều cửa sổ (đặc biệt trên Windows). |

## 🧩 Cấu trúc dự án

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # GUI frame+event hợp nhất chính (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Phiên bản GUI frame+EVK tích hợp cũ hơn
├── unified_event_gui.py                         # GUI chỉ event cho EVK + DAVIS
├── save_davis_tcp.py                            # Thu thập DAVIS (camera hoặc DV Viewer TCP)
├── code-legacy/                                 # Script/prototype lịch sử
├── evk_sdk/                                     # SDK/phần mẫu Prophesee/Metavision
├── haikang_sdk/                                 # Gói SDK và mẫu Hikrobot/Haikang
├── i18n/                                        # Thư mục bản dịch
├── recordings/                                  # Kết quả runtime (gitignored, tạo khi sử dụng)
└── davis_output/                                # Kết quả runtime cho save_davis_tcp.py (gitignored)
```

## 🛠️ Điều kiện tiên quyết

### Phần cứng

- Camera frame Hikrobot/Haikang (cho các workflow frame).
- Camera event EVK và/hoặc camera event DAVIS.

### Hệ điều hành

- Windows là mục tiêu chính cho tích hợp đầy đủ SDK camera frame và hành vi đặt preview.
- Linux/macOS có thể chạy một phần pipeline event, nhưng chưa đảm bảo độ tương đương đầy đủ.

### Python

- Python 3.x.

### Gói Python

Cài các dependency runtime cốt lõi trong môi trường đang dùng:

```bash
pip install numpy opencv-python dv-processing
```

Đối với EVK, cài đặt gói Python Prophesee Metavision phù hợp trong môi trường của bạn.

Đối với hành vi điều khiển cửa sổ Win32 trong preview GUI:

```bash
pip install pywin32
```

## 🧪 Cài đặt

1. Clone repository.
2. Mở terminal ở thư mục gốc:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Tạo/kích hoạt môi trường Python của bạn.
4. Cài dependency (xem phần trên).
5. Đảm bảo đã cài runtime/driver SDK camera phù hợp cho thiết bị của bạn.

Ghi chú giả định: ma trận phiên bản driver/firmware nhà cung cấp chưa được mô tả đầy đủ trong repo; giữ nguyên cấu hình SDK local đã kiểm chứng của bạn.

<a id="usage"></a>
## ▶️ Sử dụng

### 1) GUI frame + event hợp nhất (workflow tích hợp được khuyến nghị)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Những gì nó cung cấp:

- Tự động quét device frame và event khi khởi động.
- Điều khiển camera frame: connect, grab, preview, record, exposure/gain.
- Điều khiển camera event: connect, capture, visualize, record.
- Điều khiển hợp nhất: start/stop preview và ghi cho cả hai bên cùng lúc.
- Điều khiển thư mục đầu ra + tiền tố tên file trong GUI.

Hành vi đầu ra mặc định:

| Đầu ra | Mẫu |
|---|---|
| Thư mục gốc | `recordings/` |
| Thư mục phiên | `<prefix>_<timestamp>/` |
| File frame | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| File event (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| File event (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` khi stop) |

### 2) GUI chỉ event

```bash
python unified_event_gui.py
```

Hành vi mặc định:

- Thư mục gốc đầu ra: `recordings/`
- Tiền tố phiên mặc định: `session`
- Phát hiện thiết bị:
  - DAVIS từ `dv.io.camera.discover()`
  - EVK dưới dạng `EVK:auto` khi module Metavision sẵn sàng
- Kết quả ghi:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` và `events.npz` (nếu có event trong buffer)

### 3) Script thu thập DAVIS (camera hoặc DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Các hằng số mặc định trong script:

| Hằng số | Mặc định |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` cho DV Viewer TCP) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

Định dạng thư mục đầu ra:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- Các file điển hình: `events.npz`, `frames.avi`, `output.aedat4`

## ⚙️ Cấu hình

### `save_davis_tcp.py`

Điều chỉnh các hằng số cấp cao kiểu viết hoa để cấu hình:

- nguồn vào (`INPUT_MODE`)
- endpoint mạng (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- thời lượng ghi (`CAPTURE_SECONDS`)
- cờ đầu ra (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- hành vi preview (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Các tùy chọn runtime được expose trong GUI gồm:

- thư mục đầu ra và tiền tố tên file
- biến đổi frame (lật dọc/lật ngang, xoay)
- điều khiển exposure và gain
- điều khiển bias EVK (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) khi có hỗ trợ

### `unified_event_gui.py`

Các giá trị mặc định chính (có thể chỉnh trong script):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 💡 Ví dụ

### Ví dụ A: Thu trực tiếp camera DAVIS trong 10 giây

Sửa `save_davis_tcp.py`:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

Chạy:

```bash
python save_davis_tcp.py
```

### Ví dụ B: Nhận dữ liệu DAVIS từ DV Viewer qua TCP

Sửa `save_davis_tcp.py`:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

Chạy:

```bash
python save_davis_tcp.py
```

### Ví dụ C: Phiên chỉ event với EVK và DAVIS cùng kết nối

```bash
python unified_event_gui.py
```

Sau đó trong GUI:

1. Nhấn `Scan`.
2. Kết nối các thiết bị đã chọn.
3. Đặt thư mục đầu ra/tiền tố.
4. Dùng `Record All` để bắt đầu xuất dữ liệu theo thư mục phiên đồng bộ.

## 🛠️ Ghi chú phát triển

- Hiện chưa có build system hoặc metadata package (`pyproject.toml`, `requirements.txt`, ... không có).
- Scripts được chạy trực tiếp bằng entrypoint Python.
- Cấu hình chủ yếu bằng hằng số trong script và điều khiển GUI, không phải CLI flags.
- Thư mục SDK nhà cung cấp được giữ cố ý trong repo:
  - `evk_sdk/`
  - `haikang_sdk/`
- Kết quả đầu ra/dữ liệu được gitignore, bao gồm:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, v.v.
- GUI dual-camera có logic đặt cửa sổ preview để giảm hiện tượng pop-in và giữ window không che khuất controls chính, đặc biệt trên Windows.

<a id="troubleshooting"></a>
## 🧭 Khắc phục sự cố

- Không tìm thấy thiết bị khi khởi động.
  - Kiểm tra cáp camera, nguồn và driver của nhà cung cấp.
  - Xác nhận quyền truy cập thiết bị và runtime frame/event đã được cài đặt.
- GUI bị đóng băng khi xem preview khung đầu tiên.
  - Bắt đầu khi frame và event camera chưa cắm, sau đó nối lại và quét lại.
- Chế độ mạng DAVIS không nhận được dữ liệu.
  - Kiểm tra cổng stream DV Viewer khớp với `EVENTS_PORT`/`FRAMES_PORT`.
  - Kiểm tra rules tường lửa cho loopback nội bộ và UDP/TCP theo cấu hình.
- File `.npz` hoặc `.aedat4` event không được tạo.
  - Kiểm tra các cờ lưu trong `save_davis_tcp.py` đã bật.
  - Xác nhận quyền ghi tới thư mục đầu ra.
- Vị trí cửa sổ nhảy trên Windows.
  - Đảm bảo đã cài `pywin32` và Python có đủ quyền.

## 🗺️ Lộ trình

Các cải tiến định hướng tài liệu/UX dự kiến (chưa hoàn tất trong repo):

1. Chuẩn hóa dependencies trong file requirements pin version.
2. Thêm CLI nhẹ cho các chế độ thu không cần GUI.
3. Mở rộng ma trận tương thích SDK và firmware.
4. Thêm test an toàn, không phụ thuộc phần cứng cho hằng số và logic bố cục file.

<a id="contributing"></a>
## 👥 Đóng góp

Các đóng góp đều được chào đón.

1. Giữ thay đổi tập trung vào workflow-level scripts và tránh chỉnh sửa hành vi thu thập runtime nếu không phải thay đổi đường đi camera có chủ đích.
2. Giữ nguyên lifecycle thread camera và quy ước bố cục thư mục đầu ra nếu không có lý do hợp lệ trong PR.
3. Xác thực các thay đổi path/script bằng ít nhất một lần chạy capture cục bộ đầy đủ.
4. Bao gồm giả định và ngữ cảnh phần cứng trong mô tả PR.

## 📩 Liên hệ

Nếu bạn cần hỗ trợ tích hợp cho một thiết lập phần cứng cụ thể, hãy ghi rõ model camera, hệ điều hành và log lỗi đầy đủ trong mô tả issue.

## 📜 Giấy phép

Không có file license trong repository root tại thời điểm biên soạn này. Hãy thêm file `LICENSE` trước khi phân phối rộng rãi.


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
