[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://lazying.art)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

`SyncImagingSystem` est un espace de travail Python pour la capture synchronisée de caméra image et caméra événementielle, structuré autour de flux de travail pratiques pour EVK/DAVIS et les caméras Hikrobot/Haikang.

## 🧭 Navigateur rapide

| Section | Lien |
|---|---|
| Flux de travail principal | [Utilisation](#utilisation) |
| Installation | [Configuration](#installation) |
| Dépannage | [Dépannage](#depannage) |
| Détails de contribution | [Contribuer](#contribuer) |
| Support | [❤️ Support](#-support) |

## 📌 Vue d'ensemble

`SyncImagingSystem` est un espace de travail Python pour la capture synchronisée de caméra image et caméra événementielle.

Il propose trois flux de travail principaux :

| Script | Objectif | Remarques |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | Interface unifiée image + événements | Prend en charge la caméra image Hikrobot/Haikang + la caméra événementielle EVK ou DAVIS |
| `unified_event_gui.py` | Interface événements uniquement | Capture EVK + DAVIS avec auto-détection et enregistrement par exécution |
| `save_davis_tcp.py` | Script de capture DAVIS | Prend en charge le mode caméra directe et le mode réseau DV Viewer TCP |

Le dépôt contient aussi des bundles SDK fournis par les fabricants et des prototypes historiques pour référence.

## 🚀 Fonctionnalités

| Domaine | Points forts |
|---|---|
| 🎛️ Interface unifiée | Interface image + événements unifiée avec contrôles par appareil et commandes de démarrage/arrêt globales. |
| ⚡ Interface événements | Interface événements seuls avec opérations de connexion/aperçu/enregistrement multi-appareils. |
| 📡 Sources DAVIS | Capture DAVIS depuis le matériel directement (`INPUT_MODE = "camera"`) ou via flux réseau DV Viewer (`INPUT_MODE = "network"`, ports par défaut `7777/7778`). |
| 💾 Formats de sortie | Les sorties d’enregistrement incluent `.avi`, `.raw`, `.aedat4` et `events.npz` compressé en option. |
| 🗂️ Organisation des sessions | Organisation automatique par dossiers horodatés sous `recordings/` ou `davis_output/`. |
| 🔧 Contrôles | Contrôles de bias EVK dans les interfaces unifiées. |
| 🪞 Transformations d’image | Retournement vertical, retournement horizontal et rotation de 90° dans la GUI bi-caméra. |
| 🖥️ Fenêtrage | Utilitaires de placement des fenêtres d’aperçu pour les flux multi-fenêtres (surtout sous Windows). |

## 🧩 Structure du projet

```text
SyncImagingSystem/
├── README.md
├── AGENTS.md
├── DualCamera_separate_transform_davis+evk.py   # GUI principale image+événements unifiée (EVK + DAVIS)
├── DualCamera_separate_transform.py             # Ancienne variante intégrée GUI image+EVK
├── unified_event_gui.py                         # GUI événements uniquement pour EVK + DAVIS
├── save_davis_tcp.py                            # Capture DAVIS (caméra ou DV Viewer TCP)
├── code-legacy/                                 # Scripts/prototypes historiques
├── evk_sdk/                                     # Scripts et exemples Prophesee/Metavision SDK
├── haikang_sdk/                                 # Bundles et exemples SDK Hikrobot/Haikang
├── i18n/                                        # Répertoire des traductions
├── recordings/                                  # Sortie d’exécution (ignorée par git, créée à l’usage)
└── davis_output/                                # Sortie d’exécution pour save_davis_tcp.py (ignorée par git)
```

## 🛠️ Prérequis

### Matériel

- Caméra image Hikrobot/Haikang (pour les flux image).
- Caméra événementielle EVK et/ou caméra événementielle DAVIS.

### Système d’exploitation

- Windows est la cible principale pour l’intégration complète des SDK de caméra image et le comportement de placement des aperçus.
- Linux/macOS peuvent exécuter certaines parties du pipeline événements, mais la parité fonctionnelle complète n’est pas garantie.

### Python

- Python 3.x.

### Paquets Python

Installez les dépendances runtime principales dans votre environnement actif :

```bash
pip install numpy opencv-python dv-processing
```

Pour les workflows EVK, installez les paquets Python Prophesee Metavision disponibles dans votre environnement.

Pour le comportement de contrôle de fenêtres sous Windows dans les aperçus GUI :

```bash
pip install pywin32
```

## 🧪 Installation

1. Clonez le dépôt.
2. Ouvrez un terminal à la racine du dépôt :

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. Créez/activez votre environnement Python.
4. Installez les dépendances (voir ci-dessus).
5. Assurez-vous que les runtimes/drivers SDK requis par vos appareils sont installés.

Note d’hypothèse : la matrice exacte versions driver/firmware des fournisseurs n’est pas encore entièrement documentée dans le dépôt ; conservez votre configuration SDK locale opérationnelle.

## ▶️ Utilisation

### 1) Interface unifiée image + événements (workflow intégré recommandé)

```bash
python DualCamera_separate_transform_davis+evk.py
```

Ce qu’elle propose :

- Auto-scan des dispositifs image et événements au démarrage.
- Contrôles caméra image : connexion, capture, aperçu, enregistrement, exposition/gain.
- Contrôles caméra événements : connexion, capture, visualisation, enregistrement.
- Contrôles unifiés : démarrage et arrêt synchronisés de l’aperçu et de l’enregistrement pour les deux côtés.
- Contrôles du répertoire de sortie et du préfixe de nommage dans l’interface.

Comportement de sortie par défaut :

| Sortie | Motif |
|---|---|
| Répertoire de base | `recordings/` |
| Dossier d’exécution | `<prefix>_<timestamp>/` |
| Fichiers image | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| Fichiers événements (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| Fichiers événements (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` à l’arrêt) |

### 2) Interface événements uniquement

```bash
python unified_event_gui.py
```

Comportement par défaut :

- Répertoire de base : `recordings/`
- Préfixe de session par défaut : `session`
- Découverte des appareils :
  - DAVIS via `dv.io.camera.discover()`
  - EVK comme `EVK:auto` lorsque les modules Metavision sont disponibles
- Sorties d’enregistrement :
  - EVK : `.raw`
  - DAVIS : `output.aedat4` et `events.npz` (si des événements tamponnés existent)

### 3) Script de capture DAVIS (caméra ou DV Viewer TCP)

```bash
python save_davis_tcp.py
```

Constantes clés par défaut dans le script :

| Constante | Valeur par défaut |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` pour DV Viewer TCP) |
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

## ⚙️ Configuration

### `save_davis_tcp.py`

Ajustez les constantes majuscules de haut niveau pour configurer :

- la source d’entrée (`INPUT_MODE`)
- le point de terminaison réseau (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- la durée de capture (`CAPTURE_SECONDS`)
- les bascules de sortie (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- le comportement de l’aperçu (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

Les paramètres exposés en runtime dans l’interface incluent :

- dossier de sortie et préfixe de nom de fichier
- transformations d’image (retournement vertical/horizontal, rotation)
- contrôles d’exposition et de gain image
- contrôles de bias EVK (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) lorsqu’ils sont pris en charge

### `unified_event_gui.py`

Constantes clés (modifiables dans le script) :

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 💡 Exemples

### Exemple A : capture DAVIS directe pendant 10 secondes

Modifier `save_davis_tcp.py` :

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

Exécuter :

```bash
python save_davis_tcp.py
```

### Exemple B : recevoir les données DAVIS depuis DV Viewer via TCP

Modifier `save_davis_tcp.py` :

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

Exécuter :

```bash
python save_davis_tcp.py
```

### Exemple C : session événements avec EVK et DAVIS connectés

```bash
python unified_event_gui.py
```

Puis, dans l’interface :

1. Cliquer sur `Scan`.
2. Connecter les appareils sélectionnés.
3. Définir le dossier/préfixe de sortie.
4. Utiliser `Record All` pour démarrer les dossiers d’exécution synchronisés.

## 🛠️ Notes de développement

- Aucun système de build ni métadonnées de package ne sont définis pour l’instant (`pyproject.toml`, `requirements.txt`, etc. sont absents).
- Les scripts sont lancés directement via des points d’entrée Python.
- La configuration repose principalement sur des constantes de script et des contrôles GUI, pas sur des options CLI.
- Les répertoires SDK fournisseurs sont volontairement conservés dans le dépôt :
  - `evk_sdk/`
  - `haikang_sdk/`
- Les artefacts de sortie/données sont ignorés par Git, notamment :
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, etc.
- L’interface bi-caméra inclut une logique de placement d’aperçu conçue pour réduire le pop-in des fenêtres et éviter qu’elles ne masquent les contrôles principaux, surtout sous Windows.

## 🧭 Dépannage

- Aucun appareil détecté au démarrage.
  - Vérifiez les câbles, l’alimentation et les pilotes du fournisseur.
  - Confirmez les permissions des appareils et que les runtimes image/événement sont installés.
- Gel de la GUI sur le premier aperçu image.
  - Démarrez avec les appareils image et événements déconnectés, puis reconnectez-les et relancez la détection.
- Le mode réseau DAVIS ne reçoit aucune donnée.
  - Vérifiez que les ports DV Viewer correspondent à `EVENTS_PORT`/`FRAMES_PORT`.
  - Vérifiez les règles de pare-feu pour le loopback local et le trafic UDP/TCP configuré.
- Les fichiers `.npz` ou `.aedat4` d’événements ne sont pas créés.
  - Vérifiez que les bascules de sauvegarde dans `save_davis_tcp.py` sont activées.
  - Confirmez les droits d’écriture dans le dossier de sortie.
- La position des fenêtres saute sous Windows.
  - Assurez-vous que `pywin32` est installé et que Python dispose des permissions requises.

## 🗺️ Feuille de route

Améliorations prévues axées documentation et ergonomie (non encore finalisées dans le dépôt) :

1. Centraliser les dépendances dans un fichier de requirements verrouillé.
2. Ajouter des alternatives CLI légères pour les modes de capture sans GUI.
3. Étendre la matrice de compatibilité SDK et firmware.
4. Ajouter des tests sûrs et indépendants du matériel pour les constantes du projet et la logique de structure de fichiers.

## 👥 Contribuer

Les contributions sont bienvenues.

1. Limitez les changements aux workflows au niveau script et évitez de modifier le comportement de capture runtime sauf si vous changez volontairement un chemin caméra.
2. Préservez le cycle de vie des threads caméra existants et la convention d’organisation des dossiers de sortie, sauf justification claire dans la PR.
3. Validez les scripts/dossiers modifiés avec au moins une capture locale complète.
4. Incluez vos hypothèses et le contexte matériel dans la description de votre PR.

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📩 Contact

Si vous avez besoin d’aide pour intégrer une configuration matérielle spécifique, indiquez le modèle de votre caméra, le système d’exploitation et la sortie d’erreur exacte dans la description de votre ticket.

## 📜 License

Aucun fichier de licence n’est présent à la racine du dépôt à ce stade. Ajoutez un fichier `LICENSE` avant une redistribution publique.
