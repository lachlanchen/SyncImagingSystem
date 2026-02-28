[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# SyncImagingSystem


![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## Aperçu

`SyncImagingSystem` est un espace de travail Python pour la capture synchronisée de caméras d’images (frame) et de caméras événementielles.

Il fournit trois workflows actifs principaux :

1. `DualCamera_separate_transform_davis+evk.py` : interface GUI unifiée pour la capture frame + event (caméra frame Hikrobot/Haikang + caméra événementielle EVK ou DAVIS).
2. `unified_event_gui.py` : GUI event-only pour les appareils EVK et DAVIS.
3. `save_davis_tcp.py` : script de capture DAVIS prenant en charge le mode caméra direct et le mode réseau TCP DV Viewer.

Le dépôt contient également des bundles SDK/exemples fournisseurs et des prototypes historiques pour référence.

## Fonctionnalités

| Domaine | Points clés |
|---|---|
| 🎛️ GUI unifiée | Interface de capture frame + event unifiée avec contrôles par appareil et contrôles start/stop communs. |
| ⚡ GUI Event | GUI event-only avec opérations multi-appareils de connexion/aperçu/enregistrement. |
| 📡 Sources DAVIS | Capture DAVIS depuis le matériel direct (`INPUT_MODE = "camera"`) ou via flux réseau DV Viewer (`INPUT_MODE = "network"`, ports par défaut `7777/7778`). |
| 💾 Formats de sortie | Les sorties d’enregistrement incluent `.avi`, `.raw`, `.aedat4` et `events.npz` compressé optionnel. |
| 🗂️ Organisation des sessions | Organisation automatique par dossier horodaté sous `recordings/` ou `davis_output/`. |
| 🔧 Contrôles | Contrôles de bias EVK dans les workflows de GUI unifiée. |
| 🪞 Transformation Frame | Retour vertical, retour horizontal et rotation à 90 degrés dans la GUI double caméra. |
| 🖥️ Fenêtrage | Aides au placement des fenêtres d’aperçu pour les workflows multi-fenêtres (notamment sous Windows). |

## Structure du projet

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
├── i18n/                                        # Translation directory (currently empty)
├── recordings/                                  # Runtime output (gitignored, created on use)
└── davis_output/                                # Runtime output for save_davis_tcp.py (gitignored)
```

## Prérequis

### Matériel

- Caméra frame Hikrobot/Haikang (pour les workflows frame).
- Caméra événementielle EVK et/ou caméra événementielle DAVIS.

### OS

- Windows est la cible principale pour l’intégration complète du SDK de caméra frame et le comportement de placement des aperçus.
- Linux/macOS peuvent exécuter une partie du pipeline événementiel, mais une parité complète n’est pas garantie.

### Python

- Python 3.x.

### Paquets Python

Installez les dépendances d’exécution principales dans votre environnement actif :

```bash
pip install numpy opencv-python dv-processing
```

Pour les workflows EVK, installez les paquets Python Prophesee Metavision disponibles dans votre environnement.

Pour le comportement de contrôle des fenêtres sous Windows dans les aperçus GUI :

```bash
pip install pywin32
```

## Installation

1. Clonez le dépôt.
2. Ouvrez un terminal à la racine du dépôt :

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Créez/activez votre environnement Python.
4. Installez les dépendances (voir ci-dessus).
5. Assurez-vous que les runtimes/drivers SDK requis pour vos appareils sont installés.

Note d’hypothèse : la matrice exacte des versions de drivers/firmwares fournisseurs n’est pas encore entièrement documentée dans le dépôt ; conservez votre configuration SDK locale validée.

## Utilisation

### 1) GUI frame + event unifiée (workflow intégré recommandé)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Ce que cela fournit :

- Scan automatique des appareils frame et event au démarrage.
- Contrôles caméra frame : connexion, acquisition, aperçu, enregistrement, exposition/gain.
- Contrôles caméra événementielle : connexion, capture, visualisation, enregistrement.
- Contrôles unifiés : démarrage/arrêt de l’aperçu et de l’enregistrement pour les deux côtés simultanément.
- Contrôles du dossier de sortie + préfixe de nom de fichier dans la GUI.

Comportement de sortie par défaut :

| Sortie | Modèle |
|---|---|
| Répertoire de base | `recordings/` |
| Dossier de session | `<prefix>_<timestamp>/` |
| Fichiers frame | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Fichiers event (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Fichiers event (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` à l’arrêt) |

### 2) GUI event-only

```bash
python unified_event_gui.py
```

Comportement par défaut :

- Répertoire de sortie de base : `recordings/`
- Préfixe de session par défaut : `session`
- Détection d’appareils :
  - DAVIS depuis `dv.io.camera.discover()`
  - EVK comme `EVK:auto` lorsque les modules Metavision sont disponibles
- Sorties d’enregistrement :
  - EVK : `.raw`
  - DAVIS : `output.aedat4` et `events.npz` (si des événements en mémoire tampon existent)

### 3) Script de capture DAVIS (caméra ou TCP DV Viewer)

```bash
python save_davis_tcp.py
```

Constantes clés par défaut dans le script :

| Constante | Valeur par défaut |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` pour TCP DV Viewer) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

Format du répertoire de sortie :

- `davis_output/<YYYYmmdd_HHMMSS>/`
- Fichiers typiques : `events.npz`, `frames.avi`, `output.aedat4`

## Configuration

### `save_davis_tcp.py`

Ajustez les constantes globales en majuscules pour configurer :

- source d’entrée (`INPUT_MODE`)
- endpoint réseau (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- durée de capture (`CAPTURE_SECONDS`)
- options de sortie (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- comportement de prévisualisation (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Les paramètres d’exécution exposés dans la GUI incluent :

- dossier de sortie et préfixe de nom de fichier
- transformations frame (retournement vertical/horizontal, rotation)
- contrôles d’exposition et de gain frame
- contrôles de bias EVK (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) lorsque pris en charge

### `unified_event_gui.py`

Valeurs par défaut clés (modifiables dans le script) :

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## Exemples

### Exemple A : capture caméra DAVIS directe pendant 10 secondes

Modifiez `save_davis_tcp.py` :

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

Exécutez :

```bash
python save_davis_tcp.py
```

### Exemple B : réception des données DAVIS depuis DV Viewer via TCP

Modifiez `save_davis_tcp.py` :

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

Exécutez :

```bash
python save_davis_tcp.py
```

### Exemple C : session event-only avec EVK et DAVIS connectés

```bash
python unified_event_gui.py
```

Ensuite dans la GUI :

1. Cliquez `Scan`.
2. Connectez les appareils sélectionnés.
3. Définissez le dossier de sortie/préfixe.
4. Utilisez `Record All` pour démarrer des dossiers de sortie synchronisés par session.

## Notes de développement

- Aucun système de build ni métadonnées de package n’est actuellement défini (`pyproject.toml`, `requirements.txt`, etc. sont absents).
- Les scripts sont lancés directement avec des points d’entrée Python.
- La configuration repose surtout sur des constantes de script et des contrôles GUI, pas sur des flags CLI.
- Les répertoires SDK fournisseurs sont volontairement conservés dans le dépôt :
  - `evk_sdk/`
  - `haikang_sdk/`
- Les artefacts de sortie/données sont gitignored, notamment :
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, etc.
- La GUI double caméra inclut une logique de placement des aperçus conçue pour réduire le pop-in et éviter que les fenêtres masquent les contrôles principaux, en particulier sous Windows.

## Dépannage

| Symptôme | Vérifications / Actions |
|---|---|
| Erreurs d’import `dv_processing` | Installez ou réparez `dv-processing` dans l’environnement actif. Le mode caméra DAVIS direct dans `save_davis_tcp.py` requiert `dv-processing`. |
| Erreurs d’import/module EVK (`metavision_*`) | Vérifiez que le SDK/modules Python Metavision sont installés et présents dans le Python path. |
| Échecs d’import du SDK caméra frame (`MvCameraControl_class`, etc.) | Vérifiez que les fichiers SDK Hikrobot/Haikang et leurs dépendances runtime sont présents. Confirmez que les chemins SDK locaux utilisés par les scripts sont valides. |
| Aucun appareil détecté | Vérifiez la connexion caméra, l’alimentation et les permissions. Relancez le `Scan` GUI après reconnexion du matériel. |
| L’aperçu DAVIS n’affiche pas d’événements immédiatement | Une fenêtre d’aperçu peut s’ouvrir avec une frame vide jusqu’à l’arrivée de paquets d’événements. |
| Aperçu non toujours au premier plan ou mal positionné | Sous Windows, installez `pywin32`; sur les plateformes non Windows, le comportement est limité. |
| Les fichiers d’enregistrement n’ont pas le contenu attendu | Certains fichiers sont finalisés à l’arrêt ; assurez-vous d’arrêter proprement l’enregistrement avant de fermer l’application. |

## Feuille de route

- Ajouter des fichiers de dépendances figés (`requirements.txt` ou `pyproject.toml`).
- Ajouter des tests automatisés indépendants du matériel pour la logique utilitaire.
- Étendre la documentation des combinaisons matériel/driver/version validées.
- Ajouter des arguments CLI pour les constantes de scripts actuellement codées en dur.
- Ajouter des README multilingues dans `i18n/` et les lier depuis la ligne d’options de langue.

## Contribution

Les contributions sont bienvenues.

Workflow suggéré :

1. Créez une branche pour votre changement.
2. Gardez les modifications ciblées et sûres côté matériel.
3. Validez en exécutant les scripts pertinents avec les appareils disponibles.
4. Évitez de commit de gros enregistrements/données générés.
5. Ouvrez une PR décrivant :
   - environnement matériel/logiciel
   - configuration caméra
   - ports/paramètres viewer (pour les workflows réseau)
   - exemples de chemins/logs de sortie

Note de convention du dépôt : les messages de commit sont actuellement légers ; utilisez des messages impératifs courts (par exemple : `Add DAVIS capture docs`).

## Licence

Aucun fichier de licence explicite n’est actuellement présent dans ce dépôt.

Note d’hypothèse : si ce projet est destiné à la redistribution, ajoutez un fichier `LICENSE` et mettez à jour cette section.

## Remerciements

- Écosystème Prophesee Metavision (`evk_sdk/` et modules Python associés).
- Écosystème iniVation/dv-processing pour la gestion DAVIS.
- Ressources SDK caméra Hikrobot/Haikang regroupées sous `haikang_sdk/`.
