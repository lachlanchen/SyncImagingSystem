[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` — это рабочее пространство Python для синхронизированного захвата с кадровых и event-камер, собранное вокруг практических сценариев для EVK/DAVIS и камер Hikrobot/Haikang.

## 🧭 Быстрый навигатор

| Раздел | Ссылка |
|---|---|
| Основные сценарии | [Использование](#usage) |
| Подготовка проекта | [Установка](#installation) |
| Решение проблем | [Устранение неполадок](#troubleshooting) |
| Как помочь развитию | [Участие](#contributing) |
| Поддержка | [❤️ Support](#-support) |

## 📌 Обзор

`SyncImagingSystem` — это рабочее пространство Python для синхронизированного захвата кадровых и event-камер.

В репозитории реализованы три основных рабочих сценария:

| Скрипт | Назначение | Примечания |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | Единый GUI для кадр + event | Поддерживает камерy кадров Hikrobot/Haikang и event-камеру EVK или DAVIS |
| `unified_event_gui.py` | GUI только для event | Захват EVK + DAVIS с автопоиском устройств и записью на каждый запуск |
| `save_davis_tcp.py` | Скрипт для захвата DAVIS | Поддерживает прямой режим камеры и сетевой режим DV Viewer TCP |

В репозитории также есть пакеты SDK поставщиков, примеры и исторические прототипы для справки.

## 🚀 Возможности

| Область | Ключевые моменты |
|---|---|
| 🎛️ Единый GUI | Единый GUI для кадр + event с управлением для каждого устройства и общими кнопками запуска/остановки |
| ⚡ GUI для event | GUI только для event с возможностью подключения, предпросмотра и записи для нескольких устройств |
| 📡 Источники DAVIS | Захват DAVIS с камеры (`INPUT_MODE = "camera"`) или из сетевого потока DV Viewer (`INPUT_MODE = "network"`, порты по умолчанию `7777/7778`). |
| 💾 Форматы вывода | Записываемые форматы: `.avi`, `.raw`, `.aedat4`, а также необязательный сжатый `events.npz`. |
| 🗂️ Организация запусков | Автоматическое создание папок с временной меткой в `recordings/` или `davis_output/`. |
| 🔧 Управление | Настройка смещения (bias) EVK в рабочих сценариях единого GUI. |
| 🪞 Преобразование кадров | Вертикальный и горизонтальный переворот, поворот на 90° в GUI двойной камеры. |
| 🖥️ Окна | Помощники размещения окон предпросмотра для работы с несколькими окнами (особенно в Windows). |

## 🧩 Структура проекта

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

## 🛠️ Требования

### Аппаратное обеспечение

- Кадровая камера Hikrobot/Haikang (для потоков с кадрами).
- Event-камера EVK и/или DAVIS.

### ОС

- Windows является целевой платформой для полной интеграции кадрового SDK и поведения размещения предпросмотровых окон.
- На Linux/macOS можно запускать отдельные части event-пайплайна, но полной паритетной совместимости не гарантируется.

### Python

- Python 3.x.

### Пакеты Python

Установите основные зависимости в вашем активном окружении:

```bash
pip install numpy opencv-python dv-processing
```

Для EVK-потоков установите пакеты Prophesee Metavision Python, доступные в вашей среде.

Для управления окнами GUI в Windows:

```bash
pip install pywin32
```

## <a id="installation"></a> 🧪 Установка

1. Клонируйте репозиторий.
2. Откройте терминал в корне репозитория:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Создайте/активируйте ваше Python-окружение.
4. Установите зависимости (см. выше).
5. Проверьте, что установлены нужные runtime/драйверы SDK для ваших устройств.

Примечание: точная матрица версий драйверов/прошивок поставщика на данный момент полностью не задокументирована в репозитории; используйте проверенную локальную конфигурацию SDK.

## <a id="usage"></a> ▶️ Использование

### 1) Единый GUI для кадр + event (рекомендуемый интегрированный сценарий)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Что он предоставляет:

- Автопоиск кадровых и event-устройств при запуске.
- Управление кадровой камерой: подключение, захват, предпросмотр, запись, выдержка/усиление.
- Управление event-камерой: подключение, захват, визуализация, запись.
- Единое управление: одновременный старт/стоп предпросмотра и записи для обоих потоков.
- В GUI доступны настройки базовой директории и префикса имени файла.

Поведение по умолчанию:

| Вывод | Шаблон |
|---|---|
| Базовая директория | `recordings/` |
| Папка запуска | `<prefix>_<timestamp>/` |
| Кадровые файлы | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Event-файлы (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Event-файлы (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` при остановке) |

### 2) GUI только для event

```bash
python unified_event_gui.py
```

Поведение по умолчанию:

- Базовая директория вывода: `recordings/`
- Префикс запуска по умолчанию: `session`
- Обнаружение устройств:
  - DAVIS из `dv.io.camera.discover()`
  - EVK как `EVK:auto`, если доступны модули Metavision
- Запись выходных данных:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` и `events.npz` (если есть буферизированные события)

### 3) Скрипт захвата DAVIS (камера или DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Ключевые константы по умолчанию в скрипте:

| Константа | Значение по умолчанию |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` для DV Viewer TCP) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

Формат каталога вывода:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- Типичные файлы: `events.npz`, `frames.avi`, `output.aedat4`

## ⚙️ Конфигурация

### `save_davis_tcp.py`

Изменяйте верхнеуровневые константы в формате `UPPER_CASE` для конфигурации:

- источник входного сигнала (`INPUT_MODE`)
- сетевой endpoint (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- продолжительность захвата (`CAPTURE_SECONDS`)
- параметры записи (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- поведение предпросмотра (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

В GUI доступны для настройки во время работы:

- папка вывода и префикс имени файла
- преобразования кадров (вертикальный/горизонтальный поворот, вращение)
- контроль выдержки и усиления кадра
- настройки EVK bias (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) при поддержке устройства

### `unified_event_gui.py`

Ключевые значения по умолчанию (редактируются в скрипте):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 💡 Примеры

### Пример A: Прямой захват с камеры DAVIS в течение 10 секунд

Измените `save_davis_tcp.py`:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

Запустите:

```bash
python save_davis_tcp.py
```

### Пример B: Получение данных DAVIS из DV Viewer по TCP

Измените `save_davis_tcp.py`:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

Запустите:

```bash
python save_davis_tcp.py
```

### Пример C: Сеанс только для event с подключенными EVK и DAVIS

```bash
python unified_event_gui.py
```

Затем в GUI:

1. Нажмите `Scan`.
2. Подключите выбранные устройства.
3. Укажите папку вывода и префикс.
4. Используйте `Record All` для запуска синхронизированных выходных папок на каждом запуске.

## 🛠️ Заметки по разработке

- Сейчас не используется система сборки или метаданные пакета (`pyproject.toml`, `requirements.txt` и т.д. отсутствуют).
- Скрипты запускаются напрямую через точки входа Python.
- Конфигурация в основном хранится в константах скриптов и настройках GUI, а не в CLI-флагах.
- Каталоги SDK поставщиков сохранены в репозитории намеренно:
  - `evk_sdk/`
  - `haikang_sdk/`
- Артефакты вывода и данных исключаются из git:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz` и т.д.
- GUI двойной камеры содержит логику размещения окон предпросмотра для снижения «всплытия» и чтобы окна не перекрывали основные элементы управления, особенно в Windows.

## <a id="troubleshooting"></a> 🧭 Устранение неполадок

- Устройства не обнаружены при запуске.
  - Проверьте кабели камеры, питание и драйверы производителя.
  - Убедитесь, что есть нужные разрешения на устройства и установлены event/frame runtime.
- Заморозка GUI на первом предпросмотре кадра.
  - Запустите с отключенными кадровой и event-камерами, затем переподключите и выполните сканирование снова.
- В сетевом режиме DAVIS нет данных.
  - Убедитесь, что порты DV Viewer соответствуют `EVENTS_PORT`/`FRAMES_PORT`.
  - Проверьте правила брандмауэра для локальной петли и UDP/TCP трафика согласно конфигурации.
- Файл `.npz` или `.aedat4` не создаётся.
  - Убедитесь, что переключатели сохранения в `save_davis_tcp.py` включены.
  - Проверьте права на запись в каталог вывода.
- Положение окна прыгает в Windows.
  - Убедитесь, что установлен `pywin32` и Python имеет необходимые разрешения.

## 🗺️ Дорожная карта

Планируемые улучшения по документации и usability (ещё не закрыты в репозитории):

1. Централизация зависимостей в закреплённом `requirements` файле.
2. Добавление лёгких CLI-альтернатив для безGUI-режимов захвата.
3. Расширение матрицы совместимости SDK и прошивок.
4. Добавление безопасных, независимых от оборудования тестов для констант проекта и логики структуры файлов.

## <a id="contributing"></a> 👥 Участие

Приветствуется вклад в проект.

1. Ограничивайте изменения рабочими сценариями скриптов и не меняйте поведение захвата без необходимости.
2. Сохраняйте существующий цикл жизни потоков камеры и соглашение по структуре выходных папок, если только это не обосновано в PR.
3. Проверяйте изменённые пути/скрипты хотя бы одним полным локальным прогоном захвата.
4. В описании PR указывайте допущения и контекст используемого оборудования.

## 📩 Контакты

Если вам нужна помощь с интеграцией под конкретную конфигурацию оборудования, укажите модель камеры, ОС и точный текст ошибки в описании issue.

## 📜 Лицензия

На момент этой версии в корне репозитория отсутствует файл лицензии. Добавьте `LICENSE` перед публичным распространением.


## ❤️ Support

<!-- support:start -->
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)
[![LazyingArt Support](https://img.shields.io/badge/LazyingArt-Support-0EA5E9?style=for-the-badge)](https://chat.lazying.art/donate)
[![PayPal Support](https://img.shields.io/badge/PayPal-Support-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen)
[![Stripe Support](https://img.shields.io/badge/Stripe-Support-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
<!-- support:end -->
