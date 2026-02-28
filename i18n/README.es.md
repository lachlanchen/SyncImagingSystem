[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## Resumen

`SyncImagingSystem` es un espacio de trabajo en Python para captura sincronizada con cámaras de frames y cámaras de eventos.

Proporciona tres flujos de trabajo activos principales:

1. `DualCamera_separate_transform_davis+evk.py`: GUI unificada para captura de frame + eventos (cámara de frame Hikrobot/Haikang + cámara de eventos EVK o DAVIS).
2. `unified_event_gui.py`: GUI solo de eventos para dispositivos EVK y DAVIS.
3. `save_davis_tcp.py`: script de captura DAVIS compatible con modo de cámara directa y modo de red TCP de DV Viewer.

El repositorio también incluye paquetes de SDK/muestras de proveedores y prototipos históricos como referencia.

## Características

| Área | Destacados |
|---|---|
| 🎛️ GUI unificada | GUI unificada de captura frame + eventos, con controles por dispositivo y controles de inicio/parada unificados. |
| ⚡ GUI de eventos | GUI solo de eventos con operaciones multi-dispositivo de conexión/preview/grabación. |
| 📡 Fuentes DAVIS | Captura DAVIS desde hardware directo (`INPUT_MODE = "camera"`) o stream de red de DV Viewer (`INPUT_MODE = "network"`, puertos por defecto `7777/7778`). |
| 💾 Formatos de salida | Las salidas de grabación incluyen `.avi`, `.raw`, `.aedat4` y `events.npz` comprimido opcional. |
| 🗂️ Organización por ejecución | Organización automática de carpetas por ejecución con timestamp bajo `recordings/` o `davis_output/`. |
| 🔧 Controles | Controles de bias de EVK en los flujos de GUI unificada. |
| 🪞 Transformación de frame | Flip vertical, flip horizontal y rotación de 90 grados en la GUI de doble cámara. |
| 🖥️ Ventanas | Ayudas de posicionamiento de ventanas de preview para flujos multi-ventana (especialmente en Windows). |

## Estructura del proyecto

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # GUI principal unificada frame+evento (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Variante antigua de GUI integrada frame+EVK
├── unified_event_gui.py                         # GUI solo de eventos para EVK + DAVIS
├── save_davis_tcp.py                            # Captura DAVIS (cámara o DV Viewer TCP)
├── code-legacy/                                 # Scripts/prototipos históricos
├── evk_sdk/                                     # Scripts y muestras del SDK Prophesee/Metavision
├── haikang_sdk/                                 # Paquetes y muestras del SDK Hikrobot/Haikang
├── i18n/                                        # Directorio de traducciones README
├── recordings/                                  # Salida en ejecución (gitignored, creada al usar)
└── davis_output/                                # Salida en ejecución para save_davis_tcp.py (gitignored)
```

## Requisitos previos

### Hardware

- Cámara de frame Hikrobot/Haikang (para flujos de frame).
- Cámara de eventos EVK y/o cámara de eventos DAVIS.

### SO

- Windows es el objetivo principal para integración completa con SDK de cámara de frame y comportamiento de posicionamiento de previews.
- Linux/macOS pueden ejecutar partes del pipeline de eventos, pero no se garantiza paridad completa.

### Python

- Python 3.x.

### Paquetes de Python

Instala las dependencias base de ejecución en tu entorno activo:

```bash
pip install numpy opencv-python dv-processing
```

Para flujos EVK, instala los paquetes Python de Prophesee Metavision disponibles en tu entorno.

Para el comportamiento de control de ventanas en Windows en previews GUI:

```bash
pip install pywin32
```

## Instalación

1. Clona el repositorio.
2. Abre una terminal en la raíz del repositorio:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Crea/activa tu entorno de Python.
4. Instala dependencias (ver arriba).
5. Asegura que los runtimes/drivers requeridos de SDK de cámara estén instalados para tus dispositivos.

Nota de supuesto: la matriz exacta de versiones driver/firmware de proveedores todavía no está completamente documentada dentro del repositorio; conserva tu configuración local de SDK conocida como estable.

## Uso

### 1) GUI unificada frame + eventos (flujo integrado recomendado)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Qué ofrece:

- Autoescaneo de dispositivos de frame y eventos al iniciar.
- Controles de cámara de frame: conectar, capturar, preview, grabar, exposición/ganancia.
- Controles de cámara de eventos: conectar, capturar, visualizar, grabar.
- Controles unificados: iniciar/detener preview y grabación de ambos lados juntos.
- Controles en GUI para directorio de salida + prefijo de nombre de archivo.

Comportamiento de salida por defecto:

| Salida | Patrón |
|---|---|
| Directorio base | `recordings/` |
| Carpeta de ejecución | `<prefix>_<timestamp>/` |
| Archivos de frame | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Archivos de eventos (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Archivos de eventos (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` al detener) |

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

| Constante | Por defecto |
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

## Configuración

### `save_davis_tcp.py`

Ajusta las constantes en mayúsculas de nivel superior para configurar:

- fuente de entrada (`INPUT_MODE`)
- endpoint de red (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- duración de captura (`CAPTURE_SECONDS`)
- toggles de salida (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- comportamiento de preview (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Los ajustes de ejecución expuestos en GUI incluyen:

- carpeta de salida y prefijo de nombre de archivo
- transformaciones de frame (flip vertical/horizontal, rotación)
- controles de exposición y ganancia de frame
- controles de bias EVK (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) cuando son compatibles

### `unified_event_gui.py`

Valores clave por defecto (editables en el script):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## Ejemplos

### Ejemplo A: Captura directa con cámara DAVIS durante 10 segundos

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

### Ejemplo B: Recibir datos DAVIS desde DV Viewer por TCP

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

## Notas de desarrollo

- Actualmente no hay un sistema de build ni metadatos de paquete definidos (`pyproject.toml`, `requirements.txt`, etc. no están presentes).
- Los scripts se lanzan directamente con entrypoints de Python.
- La configuración es principalmente mediante constantes de script y controles de GUI, no flags de CLI.
- Los directorios de SDK de proveedores se mantienen intencionalmente en el repositorio:
  - `evk_sdk/`
  - `haikang_sdk/`
- Los artefactos de salida/datos están en gitignore, incluyendo:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, etc.
- La GUI de doble cámara incluye lógica de posicionamiento de preview diseñada para reducir el pop-in de ventanas y evitar que las previews oculten los controles principales, especialmente en Windows.

## Resolución de problemas

| Síntoma | Verificaciones / Acciones |
|---|---|
| Errores de importación `dv_processing` | Instala o repara `dv-processing` en el entorno activo. El modo de cámara DAVIS directa en `save_davis_tcp.py` requiere `dv-processing`. |
| Errores de importación/módulo EVK (`metavision_*`) | Confirma que el SDK de Metavision y los módulos de Python estén instalados y en tu Python path. |
| Fallos de importación del SDK de cámara de frame (`MvCameraControl_class`, etc.) | Verifica que los archivos del SDK Hikrobot/Haikang y dependencias de runtime estén presentes. Confirma que las rutas locales de SDK usadas por los scripts sean válidas. |
| No se encuentran dispositivos | Verifica conexión, alimentación y permisos de las cámaras. Vuelve a ejecutar `Scan` en la GUI después de reconectar el hardware. |
| La preview de DAVIS no muestra eventos de inmediato | Puede abrirse una ventana de preview con frame en blanco hasta que lleguen paquetes de eventos. |
| La preview no permanece siempre encima o no se posiciona como se espera | En Windows, instala `pywin32`; en plataformas no Windows, el comportamiento es limitado. |
| Los archivos de grabación no contienen el contenido esperado | Algunos archivos se finalizan al detener; asegúrate de detener limpiamente la grabación antes de cerrar la app. |

## Hoja de ruta

- Agregar archivos de dependencias fijadas (`requirements.txt` o `pyproject.toml`).
- Agregar tests automatizados independientes de hardware para lógica utilitaria.
- Ampliar la documentación de combinaciones validadas de hardware/driver/versiones.
- Agregar argumentos CLI para constantes de script actualmente hardcodeadas.
- Agregar archivos README multilingües en `i18n/` y enlazarlos desde la línea de opciones de idioma.

## Contribuciones

Las contribuciones son bienvenidas.

Flujo de trabajo sugerido:

1. Crea una rama para tu cambio.
2. Mantén las modificaciones enfocadas y seguras para hardware.
3. Valida ejecutando los scripts relevantes con los dispositivos disponibles.
4. Evita commitear grabaciones/datos generados grandes.
5. Abre un PR describiendo:
   - entorno de hardware/software
   - configuración de cámaras
   - puertos/configuración del viewer (para flujos de red)
   - rutas/logs de salida de ejemplo

Nota de convención del repositorio: los mensajes de commit son actualmente ligeros; usa mensajes cortos en imperativo (por ejemplo: `Add DAVIS capture docs`).

## Licencia

Actualmente no hay un archivo de licencia explícito en este repositorio.

Nota de supuesto: si este proyecto está destinado a redistribución, agrega un archivo `LICENSE` y actualiza esta sección.

## Agradecimientos

- Ecosistema Prophesee Metavision (`evk_sdk/` y módulos Python relacionados).
- Ecosistema iniVation/dv-processing para manejo de DAVIS.
- Recursos del SDK de cámaras Hikrobot/Haikang incluidos en `haikang_sdk/`.
