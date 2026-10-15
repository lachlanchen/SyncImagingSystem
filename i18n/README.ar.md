[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

# SyncImagingSystem

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20focused-0078D6)
![Tests](https://img.shields.io/badge/Tests-Manual-F39C12)
![Capture](https://img.shields.io/badge/Capture-Frame%20%2B%20Event-16A085)
![Repository](https://img.shields.io/badge/Scope-Camera%20Capture%20Workflows-6F42C1)
![Status](https://img.shields.io/badge/README-Enhanced-2ECC71)

## 🧭 دليل سريع

| القسم | الرابط |
|---|---|
| سير العمل الرئيسي | [الاستخدام](#usage) |
| إعداد المشروع | [التثبيت](#installation) |
| استكشاف الأخطاء | [استكشاف الأخطاء](#troubleshooting) |
| مساهمات | [المساهمة](#contributing) |
| الدعم | [الدعم](#support) |

## 📌 نظرة عامة

`SyncImagingSystem` هي مساحة عمل Python لالتقاط متزامن بين كاميرا الإطارات وكاميرا الأحداث.

يوفّر النظام ثلاثة مسارات عمل رئيسية فعالة:

| النص البرمجي | الهدف | الملاحظات |
|---|---|---|
| `DualCamera_separate_transform_davis+evk.py` | واجهة موحدة للـ GUI الخاصة بالإطار + الحدث | تدعم كاميرا الإطار Hikrobot/Haikang مع كاميرا أحداث EVK أو DAVIS |
| `unified_event_gui.py` | واجهة GUI للحدث فقط | التقاط EVK + DAVIS مع الاكتشاف التلقائي وتسجيل لكل تشغيل |
| `save_davis_tcp.py` | سكربت التقاط DAVIS | يدعم وضع الكاميرا المباشر ووضع الشبكة عبر DV Viewer TCP |

يتضمن المستودع أيضًا حزم SDK/نماذج العروض البرمجية ومشاريع مرجعية تاريخية.

## 🚀 المزايا

| المجال | أبرز النقاط |
|---|---|
| 🎛️ واجهة موحدة | واجهة GUI موحدة لالتقاط الإطار + الحدث مع عناصر تحكم لكل جهاز وتحكم موحد للبداية/الإيقاف. |
| ⚡ واجهة الأحداث | واجهة مخصصة للأحداث مع عمليات اتصال/معاينة/تسجيل لعدة أجهزة. |
| 📡 مصادر DAVIS | التقاط DAVIS عبر العتاد مباشرة (`INPUT_MODE = "camera"`) أو عبر بث DV Viewer الشبكي (`INPUT_MODE = "network"`، المنافذ الافتراضية `7777/7778`). |
| 💾 صيغ الإخراج | تشمل مخرجات التسجيل `.avi` و`.raw` و`.aedat4` وملف `events.npz` المضغوط الاختياريًا. |
| 🗂️ تنظيم التشغيل | إنشاء مجلد تشغيل تلقائي مبني على الطابع الزمني داخل `recordings/` أو `davis_output/`. |
| 🔧 التحكم | ضبط معايرات EVK في تدفقات عمل الواجهة الموحدة. |
| 🪞 تحويل الإطار | قلب عمودي، قلب أفقي، وتدوير بمقدار 90 درجة في واجهة الكاميرتين المزدوجة. |
| 🖥️ إدارة النوافذ | أدوات لموقع نوافذ المعاينة ضمن سير عمل متعدد النوافذ (خصوصًا على Windows). |

## 🧩 هيكل المشروع

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

## 🛠️ المتطلبات المسبقة

### الأجهزة

- كاميرا إطار Hikrobot/Haikang (لمسارات الإطار).
- كاميرا أحداث EVK و/أو DAVIS.

### نظام التشغيل

- Windows هو الهدف الرئيسي لتحقيق تكامل كامل مع SDK كاميرا الإطار وسلوك تموضع معاينة النوافذ.
- قد تعمل Linux/macOS لبعض أجزاء مسار الأحداث، لكن التكافؤ الكامل غير مضمون.

### Python

- Python 3.x.

### حزم Python

ثبت التبعيات الأساسية في البيئة النشطة:

```bash
pip install numpy opencv-python dv-processing
```

لتدفقات EVK، ثبّت حزم Prophesee Metavision المتاحة في بيئتك.

لسلوك تحكم نافذة Windows في معاينات واجهة المستخدم:

```bash
pip install pywin32
```

## 🧪 التثبيت

1. انسخ المستودع (Clone).
2. افتح طرفية في جذر المستودع:

```bash
cd /home/lachlan/ProjectsLFS/SyncImagingSystem
```

3. أنشئ/فعّل بيئة Python الخاصة بك.
4. ثبّت التبعيات (راجع الأعلى).
5. تأكد من تثبيت وتشغيل runtimes/drivers الخاصة بكاميرا جهازك.

ملاحظة افتراضية: مصفوفة الإصدارات الدقيقة لبرامج/تعريفات المزود غير موثّقة بالكامل داخل المستودع بعد، لذا احتفظ بإعداد SDK المحلي المثبت لديك.

<a id="usage"></a>
## ▶️ الاستخدام

### 1) واجهة GUI موحدة للإطار + الحدث (المسار الموصى به)

```bash
python DualCamera_separate_transform_davis+evk.py
```

ما يتيحه المسار:

- فحص تلقائي لأجهزة الإطار والأحداث عند بدء التشغيل.
- تحكم كاميرا الإطار: اتصال، سحب، معاينة، تسجيل، تعريض/تضخيم.
- تحكم كاميرا الحدث: اتصال، التقاط، تصور، تسجيل.
- تحكّم موحد: بدء/إيقاف المعاينة والتسجيل لكلا الجانبين معًا.
- التحكم في مجلد الإخراج وبادئة اسم الملف عبر الواجهة.

سلوك الإخراج الافتراضي:

| الإخراج | النمط |
|---|---|
| مجلد أساسي | `recordings/` |
| مجلد التشغيل | `<prefix>_<timestamp>/` |
| ملفات الإطار | `<frame_device_label>/<prefix>_frame_<timestamp>.avi` |
| ملفات الحدث (EVK) | `<event_device_label>/<prefix>_<timestamp>.raw` |
| ملفات الحدث (DAVIS) | `<event_device_label>/output.aedat4` (+ `events.npz` عند الإيقاف) |

### 2) واجهة الأحداث فقط

```bash
python unified_event_gui.py
```

السلوك الافتراضي:

- مجلد الإخراج الأساسي: `recordings/`
- بادئة التشغيل الافتراضية: `session`
- اكتشاف الأجهزة:
  - DAVIS عبر `dv.io.camera.discover()`
  - EVK كـ `EVK:auto` عندما تتوافر وحدات Metavision
- مخرجات التسجيل:
  - EVK: `.raw`
  - DAVIS: `output.aedat4` و `events.npz` (إذا كانت الأحداث المخزنة مؤقتًا متاحة)

### 3) سكربت التقاط DAVIS (الكميرا أو DV Viewer TCP)

```bash
python save_davis_tcp.py
```

الثوابت الأساسية الافتراضية داخل السكربت:

| الثابت | القيمة الافتراضية |
|---|---|
| `INPUT_MODE` | `"camera"` (`"network"` لـ DV Viewer TCP) |
| `HOST` | `"127.0.0.1"` |
| `EVENTS_PORT` | `7777` |
| `FRAMES_PORT` | `7778` |
| `CAPTURE_SECONDS` | `3.0` |
| `SAVE_EVENTS_NPZ` | `True` |
| `SAVE_FRAMES_VIDEO` | `True` |
| `SAVE_AEDAT4` | `True` |
| `SHOW_EVENT_PREVIEW` | `True` |

صيغة مجلد الإخراج:

- `davis_output/<YYYYmmdd_HHMMSS>/`
- الملفات النموذجية: `events.npz`, `frames.avi`, `output.aedat4`

<a id="installation"></a>
## ⚙️ الإعداد

### `save_davis_tcp.py`

اضبط الثوابت المكتوبة بأحرف كبيرة أعلى الملف لتكوين:

- مصدر الإدخال (`INPUT_MODE`)
- نقطة نهاية الشبكة (`HOST`, `EVENTS_PORT`, `FRAMES_PORT`)
- مدة الالتقاط (`CAPTURE_SECONDS`)
- مفاتيح الإخراج (`SAVE_EVENTS_NPZ`, `SAVE_FRAMES_VIDEO`, `SAVE_AEDAT4`)
- سلوك المعاينة (`SHOW_EVENT_PREVIEW`, `PREVIEW_FPS`, `PREVIEW_WINDOW_NAME`)

### `DualCamera_separate_transform_davis+evk.py`

إعدادات وقت التشغيل المعروضة في الواجهة تتضمن:

- مجلد الإخراج وبادئة اسم الملف
- تحويلات الإطار (قلب عمودي، قلب أفقي، تدوير)
- التحكم بالتعرض والكسب للإطار
- إعدادات معايرات EVK (`bias_diff`, `bias_diff_off`, `bias_diff_on`, `bias_fo`, `bias_hpf`, `bias_refr`) عند الدعم

### `unified_event_gui.py`

القيم الافتراضية الرئيسية (قابلة للتعديل داخل السكربت):

- `DEFAULT_OUTPUT_DIR = "recordings"`
- `DEFAULT_PREFIX = "session"`
- `PREVIEW_FPS = 30.0`

## 💡 أمثلة

### مثال A: التقاط مباشر لكاميرا DAVIS لمدة 10 ثوانٍ

عدّل `save_davis_tcp.py`:

```python
INPUT_MODE = "camera"
CAPTURE_SECONDS = 10.0
SAVE_AEDAT4 = True
SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
```

ثم نفّذ:

```bash
python save_davis_tcp.py
```

### مثال B: استقبال بيانات DAVIS من DV Viewer عبر TCP

عدّل `save_davis_tcp.py`:

```python
INPUT_MODE = "network"
HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778
```

ثم نفّذ:

```bash
python save_davis_tcp.py
```

### مثال C: جلسة أحداث فقط مع اتصال EVK وDAVIS معًا

```bash
python unified_event_gui.py
```

ثم في الواجهة:

1. اضغط `Scan`.
2. وصّل الأجهزة المختارة.
3. عيّن مجلد الإخراج/البادئة.
4. استخدم `Record All` لبدء مجلدات تشغيل متزامنة لكل جلسة.

## 🛠️ ملاحظات التطوير

- لا يوجد نظام بناء أو تعريف حزمة معرف حالياً (`pyproject.toml`, `requirements.txt`، وما إلى ذلك غير موجودة).
- تُشغّل السكربتات مباشرة عبر نقاط دخول Python.
- الإعداد يعتمد غالبًا على ثوابت السكربتات والتحكم داخل الواجهة، وليس على خيارات سطر الأوامر.
- مجلدات SDK للمورّدين محفوظة عمدًا داخل المستودع:
  - `evk_sdk/`
  - `haikang_sdk/`
- عناصر الإخراج/البيانات أثناء التشغيل مدرجة في `.gitignore` بما في ذلك:
  - `recordings/`, `davis_output/`, `data/`, `*.aedat4`, `*.raw`, `*.avi`, `*.npz`, إلخ.
- واجهة الكاميرتين المزدوجتين تضمّ منطق تموضع المعاينات مصمم لتقليل رجوع النوافذ المفاجئ والحفاظ على عدم حجب عناصر التحكم الأساسية، خاصةً على Windows.

<a id="troubleshooting"></a>
## 🧭 استكشاف الأخطاء وإصلاحها

- لم يتم العثور على أجهزة عند بدء التشغيل.
  - تحقق من الكابلات، الطاقة، وسائقات المزود.
  - تأكد من صلاحيات الأجهزة وأن runtimes للأحداث/الإطارات مَثبّتة.
- واجهة GUI تتوقف عن الاستجابة عند أول معاينة للإطار.
  - ابدأ بأجهزة الإطار والحدث غير موصولة، ثم أعد الاتصال وإعادة المسح (re-scan).
- وضع شبكة DAVIS لا يستقبل أي بيانات.
  - تأكد من تطابق منافذ بث DV Viewer مع `EVENTS_PORT`/`FRAMES_PORT`.
  - تحقق من إعدادات جدار الحماية لحركة UDP/TCP على حلقة التراجع المحلية (loopback).
- ملف `.npz` أو `.aedat4` الخاص بالأحداث لا يتم إنشاؤه.
  - تحقق من تفعيل مفاتيح الحفظ في `save_davis_tcp.py`.
  - تأكد من صلاحيات الكتابة لمجلد الإخراج.
- موضع النوافذ يقفز على Windows.
  - تأكد من تثبيت `pywin32` ومن أن Python لديه الصلاحيات المطلوبة.

## 🗺️ خارطة الطريق

تحسينات مستقبلية موجّهة للوثائق وقابلية الاستخدام (لم تكتمل بعد داخل المستودع):

1. توحيد التبعيات في ملف requirements مثبت الإصدارات.
2. إضافة بدائل CLI خفيفة لمسارات الالتقاط غير المعتمدة على GUI.
3. توسيع مصفوفة توافق الـ SDK والإصدارات الثابتة.
4. إضافة اختبارات آمنة وغير متصلة بالعتاد لمنطق الثوابت وتنسيق الملفات.

<a id="contributing"></a>
## 👥 المساهمة

المساهمات مرحّب بها.

1. ابقِ التعديلات ضمن سير عمل السكربتات، وتجنب تعديل سلوك الالتقاط التشغيلي ما لم يكن المقصود تغيير خط أنابيب الكاميرا.
2. احرص على الحفاظ على دورة حياة خيوط الكاميرا وتقسيم مجلدات الإخراج كما هو، ما لم تُبرّر في PR.
3. تحقق من المسارات/السكربتات عبر تشغيل التقاط محلي واحد على الأقل.
4. أدرج الافتراضات وسياق العتاد ضمن وصف PR.

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📩 Contact

إذا كنت تحتاج مساعدة في دمج إعدادات عتاد معيّن، أضف نموذج الكاميرا ونظام التشغيل ونص الخطأ الكامل في وصف المشكلة.

## 📜 License

لا يوجد ملف ترخيص في جذر المستودع حاليًا. أضف ملف `LICENSE` قبل نشر المشروع علنًا.
