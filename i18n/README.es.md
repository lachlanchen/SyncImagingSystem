[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` es un workspace de Python para captura sincronizada de cámara de frames y de eventos, organizado alrededor de flujos de trabajo prácticos para cámaras EVK/DAVIS y Hikrobot/Haikang.

<a id="quick-navigator"></a>
## 🧭 Navegador rápido

| Sección | Enlace |
|---|---|
| Flujos principales | [Uso](#usage) |
| Configuración del proyecto | [Instalación](#installation) |
| Solución de problemas | [Solución de problemas](#troubleshooting) |
| Detalles de contribución | [Contribución](#contributing) |
| Soporte | [❤️ Support](#-support) |

<a id="overview"></a>
## 📌 Descripción general

`SyncImagingSystem` es un espacio de trabajo en Python para captura sincronizada de cámara de frames y cámara de eventos.

Proporciona tres flujos de trabajo principales activos:

| Script | Propósito | Notas |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | GUI unificada de frame + evento | Soporta cámara frame Hikrobot/Haikang + cámara de eventos EVK o DAVIS |
| `unified_event_gui.py` | GUI solo de eventos | Captura EVK + DAVIS con auto-detección y grabación por ejecución |
| `save_davis_tcp.py` | Script de captura DAVIS | Soporta modo de cámara directa y modo de red DV Viewer TCP (`INPUT_MODE = "network"`) |

El repositorio también incluye paquetes de SDK de proveedores, ejemplos y prototipos históricos para consulta.

<a id="features"></a>
## 🚀 Características

| Área | Puntos clave |
|---|---|
| 🎛️ GUI unificada | GUI integrada de captura frame + eventos con controles por dispositivo y controles de inicio/parada unificados. |
| ⚡ GUI de eventos | GUI solo de eventos con operaciones de conectar/previsualizar/grabar en múltiples dispositivos. |
| 📡 Orígenes DAVIS | Captura DAVIS desde hardware directo (`INPUT_MODE = "camera"`) o desde streaming de red de DV Viewer (`INPUT_MODE = "network"`, puertos por defecto `7777/7778`). |
| 💾 Formatos de salida | Las grabaciones incluyen `.avi`, `.raw`, `.aedat4` y `events.npz` comprimido opcional. |
| 🗂️ Organización por ejecución | Carpetas de ejecución con timestamp en `recordings/` o `davis_output/`. |
| 🔧 Controles | Controles de bias EVK en los flujos de la GUI unificada. |
| 🪞 Transformación de frame | Flip vertical, flip horizontal y rotación de 90 grados en la GUI dual. |
| 🖥️ Disposición de ventanas | Helpers de posicionamiento de ventanas de preview para flujos multiventana (especialmente en Windows). |

<a id="project-structure"></a>
## 🧩 Estructura del proyecto

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # GUI principal unificada de frame+evento (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Variante integrada antigua de GUI frame+EVK
├── unified_event_gui.py                         # GUI solo de eventos para EVK + DAVIS
├── save_davis_tcp.py                            # Captura DAVIS (cámara o DV Viewer TCP)
├── code-legacy/                                 # Scripts/prototipos históricos
├── evk_sdk/                                     # Muestras y scripts del SDK Prophesee/Metavision
├── haikang_sdk/                                 # Paquetes y muestras del SDK Hikrobot/Haikang
├── i18n/                                        # Directorio de traducciones
├── recordings/                                  # Salida en tiempo de ejecución (gitignored, creado al usar)
└── davis_output/                                # Salida en tiempo de ejecución para save_davis_tcp.py (gitignored)
```

<a id="installation"></a>
## 🛠️ Requisitos previos

### Hardware

- Cámara frame Hikrobot/Haikang (para flujos frame).
- Cámara de eventos EVK y/o cámara de eventos DAVIS.

### Sistema operativo

- Windows es el objetivo principal para la integración completa del SDK de cámara frame y el comportamiento de colocación de previews.
- Linux/macOS puede ejecutar partes de la tubería de eventos, pero no se garantiza paridad total.

### Python

- Python 3.x.

### Paquetes de Python

Instala dependencias runtime básicas en tu entorno activo:

```bash
pip install numpy opencv-python dv-processing
```

Para flujos EVK, instala los paquetes de Prophesee Metavision disponibles en tu entorno.

Para el comportamiento de control de ventanas en vistas previas de GUI en Windows:

```bash
pip install pywin32
```

<a id="usage"></a>
## 🧪 Instalación

1. Clona el repositorio.
2. Abre una terminal en la raíz del repositorio:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Crea/activa tu entorno de Python.
4. Instala dependencias (ver arriba).
5. Asegúrate de tener instalados los runtimes/drivers de cámara requeridos para tus dispositivos.

Nota de supuesto: la matriz exacta de versiones de driver/firmware de los proveedores no está documentada por completo dentro del repositorio; conserva tu configuración de SDK conocida como estable.

<a id="usage"></a>
## ▶️ Uso

### 1) GUI unificada frame + evento (flujo integrado recomendado)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Lo que aporta:

- Escaneo automático de dispositivos frame y de eventos al inicio.
- Controles de cámara frame: conectar, capturar, previsualizar, grabar, exposición/ganancia.
- Controles de cámara de eventos: conectar, capturar, visualizar, grabar.
- Controles unificados: iniciar/detener vista previa y grabación de ambos lados juntos.
- Controles de directorio de salida y prefijo de nombre de archivo desde la GUI.

Comportamiento de salida por defecto:

| Salida | Patrón |
|---|---|
| Directorio base | `recordings/` |
| Carpeta por ejecución | `<prefix>_<timestamp>/` |
| Archivos frame | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Archivos de evento (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Archivos de evento (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` al detener) |

### 2) GUI solo de eventos

```bash
python unified_event_gui.py
```

Comportamiento por defecto:

- Directorio base de salida: `recordings/`
- Prefijo de ejecución por defecto: `session`
- Descubrimiento de dispositivos:
  - DAVIS desde `dv.io.camera.discover()`
  - EVK como `EVK:auto` cuando los módulos de Metavision están disponibles
- Salidas de grabación:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` y `events.npz` (si existen eventos en búfer)

### 3) Script de captura DAVIS (cámara o DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Constantes clave por defecto en el script:

| Constante | Valor por defecto |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` para DV Viewer TCP) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

Formato del directorio de salida:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- Archivos típicos: `events.npz`, `frames.avi`, `output.aedat4`

<a id="configuration"></a>
## ⚙️ Configuración

### `save_davis_tcp.py`

Ajusta las constantes mayúsculas de nivel superior para configurar:

- fuente de entrada (`INPUT_MODE`)
- endpoint de red (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- duración de captura (`CAPTURE_SECONDS`)
- alternativas de salida (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- comportamiento de preview (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Ajustes expuestos en runtime desde la GUI:

- carpeta y prefijo de salida
- transformaciones de frame (flip vertical/horizontal, rotación)
- controles de exposición y ganancia de frame
- controles de sesgo EVK (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) cuando están soportados

### `unified_event_gui.py`

Valores por defecto (editables en el script):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

<a id="examples"></a>
## 💡 Ejemplos

### Ejemplo A: Captura directa con cámara DAVIS por 10 segundos

Edita `save_davis_tcp.py`:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

Ejecuta:

```bash
python save_davis_tcp.py
```

### Ejemplo B: Recibir datos DAVIS de DV Viewer por TCP

Edita `save_davis_tcp.py`:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

Ejecuta:

```bash
python save_davis_tcp.py
```

### Ejemplo C: Sesión solo de eventos con EVK y DAVIS conectados

```bash
python unified_event_gui.py
```

Luego, en la GUI:

1. Haz clic en `Scan`.
2. Conecta los dispositivos seleccionados.
3. Configura carpeta/prefijo de salida.
4. Usa `Record All` para iniciar carpetas de salida sincronizadas por ejecución.

<a id="development-notes"></a>
## 🛠️ Notas de desarrollo

- No existe un sistema de compilación ni metadatos de paquete definidos actualmente (`pyproject.toml`, `requirements.txt`, etc. no están presentes).
- Los scripts se lanzan directamente con entrypoints de Python.
- La configuración está orientada principalmente a constantes de script y controles de GUI, no a flags de CLI.
- Los directorios del SDK del proveedor se mantienen deliberadamente dentro del repositorio:
  - `evk_sdk/`
  - `haikang_sdk/`
- Los artefactos de salida/datos están en gitignore, incluyendo:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, etc.
- La GUI de doble cámara incluye lógica de posicionamiento de preview para reducir el pop-in de ventanas y evitar que las previews oculten controles principales, especialmente en Windows.

<a id="troubleshooting"></a>
## 🧭 Solución de problemas

- No se encuentran dispositivos al iniciar.
  - Verifica cables, alimentación y drivers del fabricante.
  - Confirma permisos y que los runtimes frame/event estén instalados.
- Bloqueo parcial de la GUI en el primer preview de frame.
  - Inicia con cámaras frame y event desconectadas, luego vuelve a conectarlas y reescanea.
- En modo red de DAVIS no llegan datos.
  - Confirma que los puertos del DV Viewer coincidan con `EVENTS_PORT`/`FRAMES_PORT`.
  - Verifica reglas de firewall para loopback local y tráfico UDP/TCP según tu configuración.
- No se crea el archivo `.npz` o `.aedat4` de eventos.
  - Verifica que los toggles de guardado en `save_davis_tcp.py` estén habilitados.
  - Confirma permisos de escritura en el directorio de salida.
- La posición de la ventana salta en Windows.
  - Asegúrate de que `pywin32` esté instalado y Python tenga permisos.

<a id="roadmap"></a>
## 🗺️ Hoja de ruta

Mejoras planificadas centradas en documentación y usabilidad (aún no completadas en el repositorio):

1. Centralizar dependencias en un archivo `requirements` con versiones fijadas.
2. Añadir alternativas CLI ligeras para modos de captura sin GUI.
3. Expandir la matriz de compatibilidad de SDK y firmware.
4. Añadir pruebas simples independientes de hardware para constantes del proyecto y diseño de rutas de archivos.

<a id="contributing"></a>
## 👥 Contribución

Las contribuciones son bienvenidas.

1. Mantén los cambios acotados a flujos de trabajo a nivel de script y evita alterar la lógica de captura runtime salvo que se cambie intencionalmente un camino de cámara.
2. Conserva la vida útil de hilos de cámara y la convención de organización de carpetas de salida, salvo que la PR lo justifique explícitamente.
3. Valida los paths/scripts modificados con al menos una sesión de captura completa en entorno local.
4. Incluye supuestos y contexto de hardware en la descripción de la PR.

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📩 Contacto

Si necesitas ayuda de integración para una configuración de hardware específica, incluye el modelo de cámara, sistema operativo y la salida de error exacta en la descripción de tu issue.

<a id="license"></a>
## 📜 Licencia

No hay un archivo de licencia en la raíz del repositorio en este borrador. Añade un archivo `LICENSE` antes de distribuir públicamente.
