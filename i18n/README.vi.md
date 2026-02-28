[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## Tổng quan

`SyncImagingSystem` là một workspace Python cho thu nhận đồng bộ camera khung hình và camera sự kiện.

Nó cung cấp ba quy trình làm việc chính đang hoạt động:

1. `DualCamera_separate_transform_davis+evk.py`: GUI hợp nhất cho thu nhận frame + event (camera khung hình Hikrobot/Haikang + camera sự kiện EVK hoặc DAVIS).
2. `unified_event_gui.py`: GUI chỉ sự kiện cho thiết bị EVK và DAVIS.
3. `save_davis_tcp.py`: script thu nhận DAVIS hỗ trợ chế độ camera trực tiếp và chế độ mạng TCP của DV Viewer.

Repository cũng chứa các gói SDK/sample của nhà cung cấp và các nguyên mẫu lịch sử để tham khảo.

## Tính năng

| Khu vực | Điểm nổi bật |
|---|---|
| 🎛️ GUI hợp nhất | GUI thu nhận frame + event hợp nhất với điều khiển theo từng thiết bị và điều khiển start/stop hợp nhất. |
| ⚡ Event GUI | GUI chỉ sự kiện với thao tác kết nối/xem trước/ghi cho nhiều thiết bị. |
| 📡 Nguồn DAVIS | Thu nhận DAVIS từ phần cứng trực tiếp (`INPUT_MODE = "camera"`) hoặc luồng mạng DV Viewer (`INPUT_MODE = "network"`, cổng mặc định `7777/7778`). |
| 💾 Định dạng đầu ra | Đầu ra ghi bao gồm `.avi`, `.raw`, `.aedat4`, và `events.npz` nén tùy chọn. |
| 🗂️ Tổ chức phiên chạy | Tự động tổ chức thư mục theo timestamp dưới `recordings/` hoặc `davis_output/`. |
| 🔧 Điều khiển | Điều khiển bias EVK trong các quy trình GUI hợp nhất. |
| 🪞 Biến đổi khung hình | Lật dọc, lật ngang và xoay 90 độ trong GUI dual-camera. |
| 🖥️ Cửa sổ | Trợ giúp bố trí cửa sổ preview cho quy trình nhiều cửa sổ (đặc biệt trên Windows). |

## Cấu trúc dự án

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # GUI chính frame+event hợp nhất (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Biến thể GUI frame+EVK tích hợp cũ hơn
├── unified_event_gui.py                         # GUI chỉ sự kiện cho EVK + DAVIS
├── save_davis_tcp.py                            # Thu nhận DAVIS (camera hoặc DV Viewer TCP)
├── code-legacy/                                 # Script/nguyên mẫu lịch sử
├── evk_sdk/                                     # Script và mẫu SDK Prophesee/Metavision
├── haikang_sdk/                                 # Gói và mẫu SDK Hikrobot/Haikang
├── i18n/                                        # Thư mục bản dịch
├── recordings/                                  # Đầu ra runtime (gitignored, tạo khi dùng)
└── davis_output/                                # Đầu ra runtime cho save_davis_tcp.py (gitignored)
```

## Điều kiện tiên quyết

### Phần cứng

- Camera khung hình Hikrobot/Haikang (cho các quy trình frame).
- Camera sự kiện EVK và/hoặc camera sự kiện DAVIS.

### Hệ điều hành

- Windows là mục tiêu chính để có tích hợp đầy đủ SDK camera khung hình và hành vi bố trí preview.
- Linux/macOS có thể chạy một phần pipeline sự kiện, nhưng không đảm bảo tương đương đầy đủ.

### Python

- Python 3.x.

### Gói Python

Cài các phụ thuộc runtime cốt lõi trong môi trường đang dùng:

```bash
pip install numpy opencv-python dv-processing
```

Với các quy trình EVK, cài các gói Python Prophesee Metavision có sẵn trong môi trường của bạn.

Với hành vi điều khiển cửa sổ trên Windows trong preview GUI:

```bash
pip install pywin32
```

## Cài đặt

1. Clone repository.
2. Mở terminal tại thư mục gốc repository:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Tạo/kích hoạt môi trường Python của bạn.
4. Cài phụ thuộc (xem ở trên).
5. Đảm bảo runtime/driver SDK camera cần thiết đã được cài cho thiết bị của bạn.

Lưu ý giả định: ma trận phiên bản driver/firmware nhà cung cấp chính xác hiện chưa được tài liệu hóa đầy đủ trong repository; hãy giữ nguyên cấu hình SDK cục bộ đã hoạt động ổn định của bạn.

## Cách sử dụng

### 1) GUI frame + event hợp nhất (quy trình tích hợp được khuyến nghị)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Nội dung cung cấp:

- Tự động quét thiết bị frame và event khi khởi động.
- Điều khiển camera frame: connect, grab, preview, record, exposure/gain.
- Điều khiển camera event: connect, capture, visualize, record.
- Điều khiển hợp nhất: start/stop preview và recording cho cả hai phía cùng lúc.
- Điều khiển thư mục output + tiền tố tên file trong GUI.

Hành vi đầu ra mặc định:

| Đầu ra | Mẫu |
|---|---|
| Thư mục gốc | `recordings/` |
| Thư mục phiên chạy | `<prefix>_<timestamp>/` |
| File frame | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| File event (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| File event (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` khi dừng) |

### 2) GUI chỉ sự kiện

```bash
python unified_event_gui.py
```

Hành vi mặc định:

- Thư mục gốc đầu ra: `recordings/`
- Tiền tố phiên chạy mặc định: `session`
- Phát hiện thiết bị:
  - DAVIS từ `dv.io.camera.discover()`
  - EVK dưới dạng `EVK:auto` khi có sẵn module Metavision
- Đầu ra ghi:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` và `events.npz` (nếu có sự kiện trong bộ đệm)

### 3) Script thu nhận DAVIS (camera hoặc DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Các hằng số mặc định chính trong script:

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
- File điển hình: `events.npz`, `frames.avi`, `output.aedat4`

## Cấu hình

### `save_davis_tcp.py`

Điều chỉnh các hằng số viết hoa cấp cao nhất để cấu hình:

- nguồn đầu vào (`INPUT_MODE`)
- endpoint mạng (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- thời lượng thu (`CAPTURE_SECONDS`)
- công tắc đầu ra (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- hành vi preview (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Thiết lập runtime lộ ra trong GUI bao gồm:

- thư mục đầu ra và tiền tố tên file
- biến đổi frame (lật dọc/lật ngang, xoay)
- điều khiển exposure và gain cho frame
- điều khiển bias EVK (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) khi được hỗ trợ

### `unified_event_gui.py`

Mặc định chính (có thể sửa trong script):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## Ví dụ

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

### Ví dụ C: Phiên chỉ sự kiện với cả EVK và DAVIS cùng kết nối

```bash
python unified_event_gui.py
```

Sau đó trong GUI:

1. Nhấp `Scan`.
2. Kết nối các thiết bị đã chọn.
3. Đặt thư mục đầu ra/tiền tố.
4. Dùng `Record All` để bắt đầu các thư mục đầu ra theo phiên chạy được đồng bộ.

## Ghi chú phát triển

- Hiện chưa có hệ thống build hoặc metadata package (`pyproject.toml`, `requirements.txt`, v.v. chưa có).
- Script được khởi chạy trực tiếp bằng Python entrypoint.
- Cấu hình chủ yếu là hằng số trong script và điều khiển GUI, không phải cờ CLI.
- Các thư mục SDK nhà cung cấp được giữ trong repository một cách có chủ đích:
  - `evk_sdk/`
  - `haikang_sdk/`
- Các artifact đầu ra/dữ liệu được gitignore, bao gồm:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, v.v.
- GUI dual-camera bao gồm logic bố trí preview để giảm hiện tượng pop-in và tránh che các điều khiển chính, đặc biệt trên Windows.

## Khắc phục sự cố

| Triệu chứng | Kiểm tra / Hành động |
|---|---|
| Lỗi import `dv_processing` | Cài hoặc sửa `dv-processing` trong môi trường đang hoạt động. Chế độ camera DAVIS trực tiếp trong `save_davis_tcp.py` yêu cầu `dv-processing`. |
| Lỗi import/module EVK (`metavision_*`) | Xác nhận SDK Metavision/module Python đã được cài và nằm trên Python path của bạn. |
| Lỗi import SDK camera frame (`MvCameraControl_class`, v.v.) | Xác minh file SDK Hikrobot/Haikang và phụ thuộc runtime có sẵn. Xác nhận các đường dẫn SDK cục bộ mà script dùng là hợp lệ. |
| Không tìm thấy thiết bị | Kiểm tra kết nối camera, nguồn điện và quyền truy cập. Chạy lại `Scan` trong GUI sau khi kết nối lại phần cứng. |
| DAVIS preview chưa hiển thị sự kiện ngay | Cửa sổ preview có thể mở với khung hình trống cho đến khi gói sự kiện đến. |
| Preview không luôn-on-top hoặc không đúng vị trí như mong đợi | Trên Windows, cài `pywin32`; trên nền tảng không phải Windows, hành vi bị giới hạn. |
| File ghi thiếu nội dung kỳ vọng | Một số file chỉ hoàn tất khi dừng; hãy đảm bảo dừng recording đúng cách trước khi đóng ứng dụng. |

## Lộ trình

- Thêm file phụ thuộc được ghim phiên bản (`requirements.txt` hoặc `pyproject.toml`).
- Thêm test tự động không phụ thuộc phần cứng cho logic tiện ích.
- Mở rộng tài liệu cho các tổ hợp phần cứng/driver/phiên bản đã được xác thực.
- Thêm tham số CLI cho các hằng số script hiện đang hardcode.
- Thêm các README đa ngôn ngữ trong `i18n/` và liên kết chúng từ dòng language-options.

## Đóng góp

Hoan nghênh đóng góp.

Quy trình đề xuất:

1. Tạo một nhánh cho thay đổi của bạn.
2. Giữ sửa đổi tập trung và an toàn với phần cứng.
3. Xác thực bằng cách chạy script liên quan trên các thiết bị sẵn có.
4. Tránh commit dữ liệu/recording sinh ra có kích thước lớn.
5. Mở PR mô tả:
   - môi trường phần cứng/phần mềm
   - thiết lập camera
   - cổng/cài đặt viewer (cho quy trình mạng)
   - đường dẫn output/log mẫu

Lưu ý quy ước repository: thông điệp commit hiện còn đơn giản; hãy dùng câu ngắn dạng mệnh lệnh (ví dụ: `Add DAVIS capture docs`).

## Giấy phép

Hiện chưa có file giấy phép rõ ràng trong repository này.

Lưu ý giả định: nếu dự án này hướng đến phân phối lại, hãy thêm file `LICENSE` và cập nhật mục này.

## Lời cảm ơn

- Hệ sinh thái Prophesee Metavision (`evk_sdk/` và các module Python liên quan).
- Hệ sinh thái iniVation/dv-processing cho xử lý DAVIS.
- Tài nguyên SDK camera Hikrobot/Haikang được đóng gói trong `haikang_sdk/`.
