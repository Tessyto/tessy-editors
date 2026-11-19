"""Tessy's Skin Editor
Uso: python skin_editor.py
"""
import sys
import os
import math
import json
import random
import urllib.request
import urllib.parse
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

def scale_color(c, factor):
    """Escala brillo de un QColor manteniendo el alpha."""
    return QColor(min(255, int(c.red() * factor)),
                  min(255, int(c.green() * factor)),
                  min(255, int(c.blue() * factor)),
                  c.alpha())

def vary_color(c, amount):
    """Variacion de tono aleatoria (porcentaje). 0 = sin cambio."""
    if amount <= 0:
        return QColor(c)
    return scale_color(c, 1 + random.uniform(-amount, amount) / 100.0)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- rueda del mouse ---
class WheelGuard(QObject):
    GUARDED = (QComboBox, QAbstractSpinBox, QSlider)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._armed = set()

    @staticmethod
    def _wheel_step(obj, angle):
        factor = max(1, abs(angle) // 120)
        sign = 1 if angle > 0 else -1
        if isinstance(obj, QComboBox):
            i = obj.currentIndex() + (1 if angle < 0 else -1)
            i = max(0, min(obj.count() - 1, i))
            if i != obj.currentIndex():
                obj.setCurrentIndex(i)
            return
        if isinstance(obj, QAbstractSlider):
            step = max(obj.singleStep(), max(1, (obj.maximum() - obj.minimum()) // 20))
            obj.setValue(obj.value() + sign * step * factor)
            return
        if isinstance(obj, QAbstractSpinBox):
            obj.stepBy(sign * factor)

    def eventFilter(self, obj, event):
        t = event.type()
        if isinstance(obj, QWidget) and isinstance(obj, self.GUARDED):
            if t == QEvent.Type.MouseButtonPress:
                # Click sobre el control: queda armado (y solo él)
                self._armed = {obj}
                return False
            if t == QEvent.Type.FocusOut:
                self._armed.discard(obj)
                return False
            if t == QEvent.Type.Wheel:
                if obj in self._armed:
                    # El control fue clickeado: la rueda lo controla.
                    self._wheel_step(obj, event.angleDelta().y())
                    return True
                # Sin armar: la rueda desplaza el panel, no cambia el valor.
                self._scroll_parent(obj, event.angleDelta().y())
                return True
            return False

        # Click en cualquier otro sitio: desarma los controles
        if t == QEvent.Type.MouseButtonPress:
            self._armed.clear()
        return False

    @staticmethod
    def _scroll_parent(obj, angle):
        # Redirigir la rueda al ancestro desplazable más cercano, si lo hay.
        area = None
        p = obj.parentWidget()
        while p is not None:
            if isinstance(p, QAbstractScrollArea):
                area = p
                break
            p = p.parentWidget()
        if area is not None:
            bar = area.verticalScrollBar()
            delta = angle
            if delta:
                step = max(1, bar.singleStep() * 3)
                bar.setValue(bar.value() - (step if delta > 0 else -step))


APP_VERSION = "0.0.1"

# --- i18n (es/en) ---
LANG = "es"
LAYOUT_VERSION = 0   # sube cada vez que cambia el layout (Steve/Alex); invalida cachés

I18N = {
    "es": {
        # barra superior
        "undo": "↩ Deshacer", "redo": "↪ Rehacer",
        "grid": "⊞ Cuadrícula", "guides": "▦ Guías",
        "language": "Idioma",
        # zoom
        "zoom_lbl": "Zoom:", "fit": "⤢ Ajustar",
        "zoom_in_tip": "Acercar (Ctrl++)", "zoom_out_tip": "Alejar (Ctrl+-)",
        "fit_tip": "Ajustar a la ventana (Ctrl+0)",
        # herramientas
        "tools_group": "Herramientas",
        "brushes_group": "Pinceles",
        "brush_shape": "Forma:", "brush_size": "Tamaño:", "brush_strength": "Intensidad:",
        "brush_dot": "• Punto", "brush_square": "▦ Cuadrado", "brush_circle": "● Círculo",
        "brush_spray": "✳ Aerosol", "brush_soft": "◌ Suave",
        "variation": "Variación de tono (ruido)",
        "variation_tip": "Cada píxel pintado cambia un poco de brillo. 0 = color plano.",
        "tool_pencil": "✎ Lápiz", "tool_eraser": "⌫ Borrador", "tool_bucket": "▣ Cubeta",
        "tool_picker": "⌖ Gotero", "tool_replace": "↹ Reemplazar", "tool_line": "／ Línea",
        "tool_rect": "▭ Rectángulo", "mirror": "🪞 Modo Espejo",
        # color
        "color_group": "Color y Opacidad", "alpha": "Alfa (Opacidad)",
        "pick_color": "Seleccionar Color",
        # zonas
        "zones_group": "Zonas Activas",
        # archivo
        "file_group": "Archivo", "open_png": "Abrir PNG", "save_png": "Guardar PNG",
        "import_mojang": "⤓ Importar Mojang",
        # visor 3D
        "viewer_group": "Vista Previa 3D (Rotable)",
        "pose_idle": "Estático", "pose_walk": "Caminar", "pose_run": "Correr",
        "reset_view": "⟲ Restablecer vista",
        "viewer_tip": "Arrastra para rotar · Rueda para zoom · Doble clic para restablecer",
        # estado
        "hint": "Rueda: zoom · Espacio / Alt / Clic central + arrastrar: mover · Clic derecho: borrar",
        "free": "Libre",
        "nothing_undo": "Nada que deshacer", "nothing_redo": "Nada que rehacer",
        "undone": "Deshecho", "redone": "Rehecho",
        # partes y caras
        "part_head": "Cabeza", "part_body": "Cuerpo", "part_rarm": "Brazo D", "part_larm": "Brazo I",
        "part_rleg": "Pierna D", "part_lleg": "Pierna I",
        "part_hat": "Cabeza (capa ext.)", "part_jacket": "Cuerpo (capa ext.)",
        "part_rsleeve": "Brazo D (capa ext.)", "part_lsleeve": "Brazo I (capa ext.)",
        "part_rpants": "Pierna D (capa ext.)", "part_lpants": "Pierna I (capa ext.)",
        "face_front": "frente", "face_back": "espalda", "face_right": "derecha",
        "face_left": "izquierda", "face_top": "arriba", "face_bottom": "abajo",
        # diálogos
        "dlg_open": "Abrir Skin", "dlg_save": "Guardar Skin", "png_filter": "Archivos PNG (*.png)",
        "invalid_size_title": "Tamaño no válido",
        "invalid_size_msg": "La imagen debe ser cuadrada de 32, 64, 128 o 256 píxeles (o el formato antiguo 2:1, como 64x32).",
        "saved": "Guardado: {path}", "save_failed": "No se pudo guardar el archivo",
        "mojang_title": "Importar de Mojang", "mojang_prompt": "Nombre de usuario:",
        "mojang_searching": "Buscando skin...", "mojang_ok": "Skin importada correctamente",
        "error": "Error", "mojang_err": "No se pudo importar:\n{err}",
        "mojang_err_status": "Error al importar",
        "mojang_not_found": "No se encontró el jugador «{name}».",
        "mojang_rate": "Mojang está limitando las peticiones (HTTP 429).\nEspera unos minutos e inténtalo de nuevo.",
        "recover_title": "Recuperar trabajo",
        "recover_msg": "Se encontró una skin sin guardar de tu última sesión.\n¿Quieres recuperarla?",
        "recovered": "Trabajo recuperado",
        "model_group": "Modelo y resolución",
        "body_type": "Tipo de cuerpo:", "body_default": "Normal (4 px)", "body_slim": "Slim (3 px)",
        "resolution": "Resolución:",
        "res_shrink_title": "Reducir resolución",
        "res_shrink_msg": "Pasar a {size}×{size} reduce el detalle de la skin.\n(Puedes deshacerlo con Ctrl+Z.)\n¿Continuar?",
        "copy_image": "📋 Copiar skin",
        "copied": "Skin copiada al portapapeles",
        "import_url": "🔗 Importar URL",
        "import_url_prompt": "URL de la imagen (PNG):",
        "url_failed": "No se pudo descargar:\n{err}",
        "presets_group": "Skins de partida",
        "preset_steve": "Steve", "preset_alex": "Alex", "preset_wraith": "Espectro", "preset_zombie": "Zombie",
        "about_btn": "❓ Acerca de",
        "about_title": "Acerca de Tessy's Skin Editor",
        "about_text": "Tessy's Skin Editor v{version}\nEditor de skins para fans de Minecraft (modelos Steve, Alex y Slim).\nHerramienta hecha por fans; NO es un producto oficial de Mojang.\n\n\"Minecraft\" es una marca de Mojang Synergies AB / Microsoft. Este programa NO está afiliado a ni respaldado por Mojang o Microsoft. Los assets de skins de Mojang/Microsoft se cargan desde los servicios públicos de Mojang para tu uso local.\n\nAtajos:\n  P/E/G/I/C/L/R  Herramientas (Lápiz, Borrador, Cubeta, Gotero, Reemplazar, Línea, Rectángulo)\n  M  Modo espejo · Ctrl+G  Cuadrícula · Ctrl+0  Ajustar a la ventana · Rueda  Zoom\n  Ctrl+S  Guardar · Ctrl+O  Abrir · Ctrl+Z  Deshacer · Ctrl+Y / Ctrl+Shift+Z  Rehacer\n  Ctrl+Shift+C  Copiar skin al portapapeles\n\nHecho con PyQt6 · Recuperación automática ante cierres inesperados.\nHerramienta de fans · no oficial (Mojang Usage Guidelines).",
    },
    "en": {
        "undo": "↩ Undo", "redo": "↪ Redo",
        "grid": "⊞ Grid", "guides": "▦ Guides",
        "language": "Language",
        "zoom_lbl": "Zoom:", "fit": "⤢ Fit",
        "zoom_in_tip": "Zoom in (Ctrl++)", "zoom_out_tip": "Zoom out (Ctrl+-)",
        "fit_tip": "Fit to window (Ctrl+0)",
        "tools_group": "Tools",
        "brushes_group": "Brushes",
        "brush_shape": "Shape:", "brush_size": "Size:", "brush_strength": "Strength:",
        "brush_dot": "• Dot", "brush_square": "▦ Square", "brush_circle": "● Circle",
        "brush_spray": "✳ Spray", "brush_soft": "◌ Soft",
        "variation": "Tone variation (noise)",
        "variation_tip": "Each painted pixel gets a slightly different brightness. 0 = flat color.",
        "tool_pencil": "✎ Pencil", "tool_eraser": "⌫ Eraser", "tool_bucket": "▣ Fill",
        "tool_picker": "⌖ Picker", "tool_replace": "↹ Replace", "tool_line": "／ Line",
        "tool_rect": "▭ Rectangle", "mirror": "🪞 Mirror Mode",
        "color_group": "Color & Opacity", "alpha": "Alpha (Opacity)",
        "pick_color": "Select Color",
        "zones_group": "Active Zones",
        "file_group": "File", "open_png": "Open PNG", "save_png": "Save PNG",
        "import_mojang": "⤓ Import from Mojang",
        "viewer_group": "3D Preview (Drag to rotate)",
        "pose_idle": "Idle", "pose_walk": "Walk", "pose_run": "Run",
        "reset_view": "⟲ Reset view",
        "viewer_tip": "Drag to rotate · Wheel to zoom · Double-click to reset",
        "hint": "Wheel: zoom · Space / Alt / Middle-click + drag: pan · Right-click: erase",
        "free": "Free",
        "nothing_undo": "Nothing to undo", "nothing_redo": "Nothing to redo",
        "undone": "Undone", "redone": "Redone",
        "part_head": "Head", "part_body": "Body", "part_rarm": "R. Arm", "part_larm": "L. Arm",
        "part_rleg": "R. Leg", "part_lleg": "L. Leg",
        "part_hat": "Head (outer layer)", "part_jacket": "Body (outer layer)",
        "part_rsleeve": "R. Arm (outer layer)", "part_lsleeve": "L. Arm (outer layer)",
        "part_rpants": "R. Leg (outer layer)", "part_lpants": "L. Leg (outer layer)",
        "face_front": "front", "face_back": "back", "face_right": "right",
        "face_left": "left", "face_top": "top", "face_bottom": "bottom",
        "dlg_open": "Open Skin", "dlg_save": "Save Skin", "png_filter": "PNG Files (*.png)",
        "invalid_size_title": "Invalid size",
        "invalid_size_msg": "The image must be square at 32, 64, 128 or 256 pixels (or the old 2:1 format, e.g. 64x32).",
        "saved": "Saved: {path}", "save_failed": "Could not save the file",
        "mojang_title": "Import from Mojang", "mojang_prompt": "Username:",
        "mojang_searching": "Looking for skin...", "mojang_ok": "Skin imported successfully",
        "error": "Error", "mojang_err": "Could not import:\n{err}",
        "mojang_err_status": "Import failed",
        "mojang_not_found": "Player “{name}” was not found.",
        "mojang_rate": "Mojang is rate-limiting requests (HTTP 429).\nWait a few minutes and try again.",
        "recover_title": "Recover work",
        "recover_msg": "An unsaved skin from your last session was found.\nDo you want to recover it?",
        "recovered": "Work recovered",
        "model_group": "Model & resolution",
        "body_type": "Body type:", "body_default": "Default (4 px)", "body_slim": "Slim (3 px)",
        "resolution": "Resolution:",
        "res_shrink_title": "Lower resolution",
        "res_shrink_msg": "Switching to {size}×{size} reduces the skin's detail.\n(You can undo it with Ctrl+Z.)\nContinue?",
        "copy_image": "📋 Copy skin",
        "copied": "Skin copied to clipboard",
        "import_url": "🔗 Import from URL",
        "import_url_prompt": "Image URL (PNG):",
        "url_failed": "Could not download:\n{err}",
        "presets_group": "Starter skins",
        "preset_steve": "Steve", "preset_alex": "Alex", "preset_wraith": "Wraith", "preset_zombie": "Zombie",
        "about_btn": "❓ About",
        "about_title": "About Tessy's Skin Editor",
        "about_text": "Tessy's Skin Editor v{version}\nSkin editor built for Minecraft fans (Steve, Alex and Slim models).\nFan-made tool; NOT an official Mojang product.\n\n\"Minecraft\" is a trademark of Mojang Synergies AB / Microsoft. This program is NOT affiliated with or endorsed by Mojang or Microsoft. Mojang/Microsoft skin assets are fetched from Mojang's public services for your local use.\n\nShortcuts:\n  P/E/G/I/C/L/R  Tools (Pencil, Eraser, Fill, Picker, Replace, Line, Rectangle)\n  M  Mirror mode · Ctrl+G  Grid · Ctrl+0  Fit to window · Wheel  Zoom\n  Ctrl+S  Save · Ctrl+O  Open · Ctrl+Z  Undo · Ctrl+Y / Ctrl+Shift+Z  Redo\n  Ctrl+Shift+C  Copy skin to clipboard\n\nMade with PyQt6 · Automatic crash recovery.\nFan tool · not official (Mojang Usage Guidelines).",
    },
}

def set_language(code):
    global LANG
    if code in I18N:
        LANG = code

def system_language():
    """Idioma de la app según el idioma de la interfaz del sistema operativo."""
    locales = QLocale.system().uiLanguages() or [QLocale.system().name()]
    for loc in locales:
        code = str(loc).split("-")[0].split("_")[0].lower()
        if code in I18N:
            return code
    return "en"

def T(key, **kw):
    text = I18N.get(LANG, {}).get(key)
    if text is None:
        text = I18N["es"].get(key, key)
    return text.format(**kw) if kw else text


# --- datos de layout ---
RESOLUTIONS = (32, 64, 128, 256)   # lados de textura soportados (la referencia de Minecraft es 64)
SIZE = 64                          # lado actual de la textura, en píxeles
FACE_AT = [[None] * SIZE for _ in range(SIZE)]
FACE_RECTS = []

def _sc(v):
    """Convierte una coordenada de la rejilla de referencia (64) a la resolución actual."""
    return int(math.floor(v * SIZE / 64 + 0.5))

def scaled_rect(x, y, w, h):
    """Rectángulo de la rejilla de 64 -> (x, y, w, h) en la resolución actual.
    Se escalan los BORDES (no el ancho), así dos caras vecinas nunca se solapan ni dejan huecos."""
    x0, y0, x1, y1 = _sc(x), _sc(y), _sc(x + w), _sc(y + h)
    return x0, y0, max(1, x1 - x0), max(1, y1 - y0)

def build_layout(skin_type="steve", size=None):
    global FACE_AT, FACE_RECTS, LAYOUT_VERSION, SIZE
    if size:
        SIZE = int(size)
    LAYOUT_VERSION += 1
    w_arm = 3 if skin_type == "alex" else 4
    parts = [
        ("head", 0, 0, 8, 8, 8, False), ("body", 16, 16, 8, 12, 4, False),
        ("rarm", 40, 16, w_arm, 12, 4, False), ("rleg", 0, 16, 4, 12, 4, False),
        ("larm", 32, 48, w_arm, 12, 4, False), ("lleg", 16, 48, 4, 12, 4, False),
        ("hat", 32, 0, 8, 8, 8, True), ("jacket", 16, 32, 8, 12, 4, True),
        ("rsleeve", 40, 32, w_arm, 12, 4, True), ("rpants", 0, 32, 4, 12, 4, True),
        ("lsleeve", 48, 48, w_arm, 12, 4, True), ("lpants", 0, 48, 4, 12, 4, True),
    ]
    FACE_AT = [[None] * SIZE for _ in range(SIZE)]
    FACE_RECTS = []
    def pf(u, v, w, h, d):
        return {
            "top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d),
            "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
            "left": (u + d + w, v + d, d, h), "back": (u + 2 * d + w, v + d, w, h),
        }
    for n, u, v, w, h, d, ov in parts:
        for f, rect in pf(u, v, w, h, d).items():
            x, y, fw, fh = scaled_rect(*rect)
            FACE_RECTS.append((n, f, x, y, fw, fh, ov))
            for j in range(fh):
                for i in range(fw):
                    FACE_AT[y + j][x + i] = (n, f, i, j, ov)

build_layout("steve")

FACE_TINT = {
    False: {"top": QColor(191, 227, 255), "bottom": QColor(201, 201, 214), "right": QColor(217, 198, 240), "front": QColor(191, 238, 192), "left": QColor(240, 198, 230), "back": QColor(255, 217, 168)},
    True: {"top": QColor(140, 200, 255), "bottom": QColor(160, 160, 184), "right": QColor(192, 154, 232), "front": QColor(143, 224, 144), "left": QColor(232, 154, 210), "back": QColor(255, 189, 110)},
}

def get_zone(part):
    if part in ("head", "hat"): return "head"
    if part in ("body", "jacket"): return "body"
    if part in ("rarm", "rsleeve"): return "rarm"
    if part in ("larm", "lsleeve"): return "larm"
    if part in ("rleg", "rpants"): return "rleg"
    if part in ("lleg", "lpants"): return "lleg"
    return None

def get_uvs(u, v, w, h, d):
    """Rectángulos de textura de cada cara (en la resolución actual) para el visor 3D."""
    def R(x, y, ww, hh):
        return QRect(*scaled_rect(x, y, ww, hh))
    return {
        "top": R(u + d, v, w, d), "bottom": R(u + d + w, v, w, d),
        "right": R(u, v + d, d, h), "front": R(u + d, v + d, w, h),
        "left": R(u + d + w, v + d, d, h), "back": R(u + 2 * d + w, v + d, w, h)
    }

def get_mirrored_pos(x, y):
    info = FACE_AT[y][x]
    if not info: return None
    part, face, lx, ly, ov = info
    for p, f, fx, fy, fw, fh, fov in FACE_RECTS:
        if p == part and f == face and fov == ov:
            return fx + (fw - 1 - lx), fy + ly
    return None

def normalize_skin(img):
    """Devuelve la skin como imagen cuadrada RGBA (32/64/128/256 px), o None si el tamaño no es válido.
    También acepta el formato antiguo 2:1 (64x32, 128x64...) y lo convierte al formato moderno."""
    if img is None or img.isNull():
        return None
    w, h = img.width(), img.height()
    if w in RESOLUTIONS and h == w:
        return img.convertToFormat(QImage.Format.Format_RGBA8888)
    if w in RESOLUTIONS and h == w // 2:
        src = img.convertToFormat(QImage.Format.Format_ARGB32)
        out = QImage(w, w, QImage.Format.Format_ARGB32)
        out.fill(Qt.GlobalColor.transparent)
        k = w / 64
        pt = QPainter(out)
        pt.drawImage(0, 0, src)
        def cp(sx, sy, sw, sh, dx, dy):
            pt.drawImage(QPoint(int(dx * k), int(dy * k)), src,
                         QRect(int(sx * k), int(sy * k), int(sw * k), int(sh * k)))
        cp(40, 16, 16, 16, 32, 48)   # brazo derecho -> izquierdo
        cp(0, 16, 16, 16, 16, 48)    # pierna derecha -> izquierda
        pt.end()
        return out.convertToFormat(QImage.Format.Format_RGBA8888)
    return None

class SkinEditorState:
    def __init__(self):
        self.image = QImage(64, 64, QImage.Format.Format_RGBA8888)
        self.image.fill(Qt.GlobalColor.transparent)

# --- worker mojang ---
import time
import urllib.error
import base64

_MOJANG_CACHE = {}
_MOJANG_UA = {
    "User-Agent": "Tessy's-Skin-Editor/1.0 (+https://github.com/; fan-made tool)",
    "Accept": "application/json",
}


def _get_json(url, retries=2):
    """GET JSON con reintento ante HTTP 429 (rate limit de Mojang) y backoff."""
    delay = 1.0
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=_MOJANG_UA)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(delay)
                delay *= 2.5
                continue
            raise


def mojang_lookup_uuid(username):
    """Resuelve nombre -> (uuid sin guiones, nombre oficial). Con caché en memoria."""
    key = username.strip().lower()
    if not key:
        raise ValueError("nombre vacío")
    if key in _MOJANG_CACHE:
        return _MOJANG_CACHE[key]

    quoted = urllib.parse.quote(key)
    sources = [
        f"https://api.minecraftservices.com/minecraft/profile/lookup/name/{quoted}",  # oficial actual
        f"https://api.mojang.com/users/profiles/minecraft/{quoted}",                  # legacy
    ]
    last_err = None
    uid = None
    official = username
    for url in sources:
        try:
            data = _get_json(url)
            uid = data.get("id")
            if uid:
                official = data.get("name", username)
                break
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (400, 404):
                raise   # el jugador no existe o el nombre es inválido: no hay nada más que probar
        except Exception as e:
            last_err = e

    if not uid:
        # Último recurso: archivo comunitario (playerdb), sin límite agresivo
        try:
            data = _get_json(f"https://api.playerdb.co/api/player/minecraft/{quoted}")
            player = data.get("data", {}).get("player", {})
            uid = (player.get("id") or player.get("raw_id") or "").replace("-", "")
            official = player.get("username", username) if uid else official
        except Exception as e:
            if last_err is None:
                last_err = e

    if not uid:
        raise last_err or RuntimeError("no se pudo resolver el nombre")
    _MOJANG_CACHE[key] = (uid, official)
    return _MOJANG_CACHE[key]


class MojangWorker(QThread):
    finished = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username

    def _http_error_message(self, e):
        code = getattr(e, "code", None)
        if code in (400, 404):
            return T("mojang_not_found", name=self.username)
        if code == 429:
            return T("mojang_rate")
        if code is not None:
            return f"HTTP {code}"
        return str(e)

    def run(self):
        try:
            uuid, _official = mojang_lookup_uuid(self.username)

            prof = _get_json(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
            textures = None
            for p in prof.get("properties", []):
                if p.get("name") == "textures":
                    textures = json.loads(base64.b64decode(p["value"]).decode("utf-8"))
                    break
            if not textures:
                raise ValueError("el perfil no tiene texturas")
            url = textures.get("textures", {}).get("SKIN", {}).get("url")
            if not url:
                raise ValueError("el perfil no tiene skin")

            req = urllib.request.Request(url, headers=_MOJANG_UA)
            img_data = None
            for attempt in range(2):
                try:
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        img_data = resp.read()
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 429 and attempt == 0:
                        time.sleep(1.0)
                        continue
                    raise
            img = QImage()
            if not img.loadFromData(img_data):
                raise ValueError("la skin descargada no es una imagen válida")
            self.finished.emit(img)
        except urllib.error.HTTPError as e:
            self.error.emit(self._http_error_message(e))
        except Exception as e:
            self.error.emit(str(e))

# --- worker para descargar skins por URL ---
class UrlDownloadWorker(QThread):
    finished = pyqtSignal(QImage)
    error = pyqtSignal(str)

    MAX_BYTES = 8 * 1024 * 1024

    def __init__(self, url):
        super().__init__()
        self.url = url.strip()

    def run(self):
        try:
            if not self.url.lower().startswith(("http://", "https://")):
                raise ValueError("la URL debe empezar por http:// o https://")
            req = urllib.request.Request(self.url, headers={
                "User-Agent": "SkEditor/1.0 (+https://github.com/; skin import)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                img_data = resp.read(self.MAX_BYTES + 1)
            if len(img_data) > self.MAX_BYTES:
                raise ValueError("la imagen supera los 8 MB")
            img = QImage()
            if not img.loadFromData(img_data):
                raise ValueError("el archivo descargado no es una imagen válida")
            self.finished.emit(img)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                self.error.emit(T("mojang_rate"))
            elif e.code in (400, 404):
                self.error.emit(T("mojang_not_found", name="URL"))
            else:
                self.error.emit(f"HTTP {e.code}")
        except Exception as e:
            self.error.emit(str(e))


# --- visor 3D ---
class Viewer3D(QWidget):
    DEFAULT_ROT_X, DEFAULT_ROT_Y, DEFAULT_ZOOM = 20, -30, 1.0

    # Sombreado por cara. Se aplica SOBRE LA TEXTURA (solo en píxeles opacos),
    # no como un polígono encima, para no teñir las zonas transparentes de la capa exterior.
    FACE_SHADE = {
        "top": QColor(255, 255, 255, 50), "bottom": QColor(0, 0, 0, 60),
        "right": QColor(0, 0, 0, 30), "left": QColor(0, 0, 0, 10),
        "back": QColor(0, 0, 0, 20),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.skin = None
        self.slim = False   # True = brazos de 3 px (Alex)
        self.rot_x = self.DEFAULT_ROT_X
        self.rot_y = self.DEFAULT_ROT_Y
        self.zoom = self.DEFAULT_ZOOM
        self.last_mouse = None
        self.active_zones = {z: True for z in ["head", "body", "rarm", "larm", "rleg", "lleg"]}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
        self.time = 0
        self.pose = "idle"
        self.setMinimumSize(260, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def set_skin(self, skin):
        self.skin = skin
        self.update()

    def set_slim(self, slim):
        self.slim = bool(slim)
        self.update()

    def reset_view(self):
        self.rot_x = self.DEFAULT_ROT_X
        self.rot_y = self.DEFAULT_ROT_Y
        self.zoom = self.DEFAULT_ZOOM
        self.update()

    def animate(self):
        if self.pose in ("walk", "run"):
            self.time += 1
            self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.last_mouse = e.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, e):
        if self.last_mouse:
            dx = e.position().x() - self.last_mouse.x()
            dy = e.position().y() - self.last_mouse.y()
            self.rot_y += dx * 0.5
            self.rot_x += dy * 0.5
            self.rot_x = max(-89, min(89, self.rot_x))
            self.last_mouse = e.position()
            self.update()

    def mouseReleaseEvent(self, e):
        self.last_mouse = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseDoubleClickEvent(self, e):
        self.reset_view()

    def wheelEvent(self, e):
        self.zoom += e.angleDelta().y() * 0.002
        self.zoom = max(0.4, min(3.0, self.zoom))
        self.update()

    def _make_camera(self):
        """Devuelve (rotate, to_screen, base). El tamaño se adapta al widget:
        'base' son los píxeles por unidad del modelo (el personaje mide 32 unidades)."""
        # rot_x positivo = cámara por encima del personaje
        rx, ry = math.radians(-self.rot_x), math.radians(self.rot_y)
        cos_x, sin_x = math.cos(rx), math.sin(rx)
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        cx, cy = self.width() / 2, self.height() / 2
        base = min(self.height() * 0.74 / 32.0, self.width() * 0.80 / 24.0) * self.zoom
        cam_dist = 110.0

        def rotate(v):
            vx, vy, vz = v
            vy -= 16
            vx1 = vx * cos_y - vz * sin_y
            vz1 = vx * sin_y + vz * cos_y
            vy1 = vy * cos_x - vz1 * sin_x
            vz2 = vy * sin_x + vz1 * cos_x
            return vx1, vy1, vz2

        def to_screen(r):
            vx, vy, vz = r
            s = base * cam_dist / max(1.0, vz + cam_dist)
            return QPointF(cx + vx * s, cy - vy * s)

        return rotate, to_screen, base

    def add_box(self, faces_out, cam, part, x, y, z, w, h, d, uvs, anim_angle=0, pivot=None, overlay=False):
        """Calcula las caras visibles de una caja y las agrega a faces_out (sin dibujar).
        El dibujo se hace después, con TODAS las caras ordenadas por profundidad."""
        if not self.active_zones.get(part, True): return
        rotate, to_screen = cam

        # Convención: x a la derecha, y arriba, z hacia el fondo (la cámara mira hacia +z).
        # El FRENTE del personaje está en z mínimo (mira hacia la cámara).
        verts = [
            (x, y, z), (x+w, y, z), (x+w, y+h, z), (x, y+h, z),
            (x, y, z+d), (x+w, y, z+d), (x+w, y+h, z+d), (x, y+h, z+d)
        ]

        if anim_angle != 0 and pivot:
            px, py, pz = pivot
            rad = math.radians(anim_angle)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            new_verts = []
            for vx, vy, vz in verts:
                tx, ty, tz = vx - px, vy - py, vz - pz
                ny = ty * cos_a - tz * sin_a
                nz = ty * sin_a + tz * cos_a
                new_verts.append((tx + px, ny + py, nz + pz))
            verts = new_verts

        r_verts = [rotate(v) for v in verts]
        p_verts = [to_screen(r) for r in r_verts]

        # Cada cara: vértices en el orden (arriba-izq, arriba-der, abajo-der, abajo-izq)
        # tal como se ve la cara DESDE AFUERA, para que la textura no salga espejada.
        face_defs = [
            ((3, 2, 1, 0), uvs["front"],  "front"),
            ((6, 7, 4, 5), uvs["back"],   "back"),
            ((7, 3, 0, 4), uvs["right"],  "right"),   # lado x mínimo
            ((2, 6, 5, 1), uvs["left"],   "left"),    # lado x máximo
            ((7, 6, 2, 3), uvs["top"],    "top"),
            ((0, 1, 5, 4), uvs["bottom"], "bottom"),
        ]

        for v_idx, uv_rect, name in face_defs:
            pts = [p_verts[i] for i in v_idx]
            # Back-face culling por orientación (signo del área) en pantalla:
            # con el orden de arriba, una cara que mira a la cámara tiene área > 0.
            area = 0.0
            for i in range(4):
                a, b = pts[i], pts[(i + 1) % 4]
                area += a.x() * b.y() - b.x() * a.y()
            if area <= 0:
                continue
            depth = sum(r_verts[i][2] for i in v_idx) / 4.0
            if overlay:
                depth -= 0.6   # la capa exterior se dibuja justo encima de la interior
            faces_out.append((depth, QPolygonF(pts), uv_rect, name))

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#181818"))

        if not self.skin: return

        rotate, to_screen, base = self._make_camera()
        cam = (rotate, to_screen)

        # Sombra en el suelo (bajo los pies)
        feet = to_screen(rotate((0, 0, 0)))
        rx_px = 10 * base
        ry_px = rx_px * max(0.15, abs(math.sin(math.radians(self.rot_x))))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(feet, rx_px, ry_px)
        # Sin antialiasing para las caras (evita costuras y mantiene el pixel-art nítido)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        t = self.time * 0.15
        arm_angle = 0
        leg_angle = 0
        if self.pose == "walk":
            arm_angle, leg_angle = math.sin(t) * 30, math.sin(t) * 30
        elif self.pose == "run":
            arm_angle, leg_angle = math.sin(t) * 45, math.sin(t) * 45

        aw = 3 if self.slim else 4          # ancho del brazo
        rpiv, lpiv = (-(4 + aw / 2), 24, 0), (4 + aw / 2, 24, 0)

        faces = []
        def A(*args, **kw):
            self.add_box(faces, cam, *args, **kw)

        # Capa base (pivotes en hombros Y=24 y caderas Y=12)
        A("head", -4, 24, -4, 8, 8, 8, get_uvs(0, 0, 8, 8, 8))
        A("body", -4, 12, -2, 8, 12, 4, get_uvs(16, 16, 8, 12, 4))
        A("rarm", -4 - aw, 12, -2, aw, 12, 4, get_uvs(40, 16, aw, 12, 4), arm_angle, rpiv)
        A("larm", 4, 12, -2, aw, 12, 4, get_uvs(32, 48, aw, 12, 4), -arm_angle, lpiv)
        A("rleg", -4, 0, -2, 4, 12, 4, get_uvs(0, 16, 4, 12, 4), -leg_angle, (-2, 12, 0))
        A("lleg", 0, 0, -2, 4, 12, 4, get_uvs(16, 48, 4, 12, 4), leg_angle, (2, 12, 0))
        # Capa exterior
        A("head", -4.2, 23.8, -4.2, 8.4, 8.4, 8.4, get_uvs(32, 0, 8, 8, 8), overlay=True)
        A("body", -4.2, 11.8, -2.2, 8.4, 12.4, 4.4, get_uvs(16, 32, 8, 12, 4), overlay=True)
        A("rarm", -4 - aw - 0.2, 11.8, -2.2, aw + 0.4, 12.4, 4.4, get_uvs(40, 32, aw, 12, 4), arm_angle, rpiv, overlay=True)
        A("larm", 3.8, 11.8, -2.2, aw + 0.4, 12.4, 4.4, get_uvs(48, 48, aw, 12, 4), -arm_angle, lpiv, overlay=True)
        A("rleg", -4.2, -0.2, -2.2, 4.4, 12.4, 4.4, get_uvs(0, 32, 4, 12, 4), -leg_angle, (-2, 12, 0), overlay=True)
        A("lleg", -0.2, -0.2, -2.2, 4.4, 12.4, 4.4, get_uvs(0, 48, 4, 12, 4), leg_angle, (2, 12, 0), overlay=True)

        # Orden global por profundidad (más lejos primero): así brazos/piernas/cuerpo
        # se tapan bien entre sí desde cualquier ángulo.
        faces.sort(key=lambda f: f[0], reverse=True)

        for depth, poly, uv_rect, name in faces:
            tex = self.skin.image.copy(uv_rect).convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
            shade = self.FACE_SHADE.get(name)
            if shade:
                sp = QPainter(tex)
                sp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
                sp.fillRect(tex.rect(), shade)
                sp.end()

            src_poly = QPolygonF([QPointF(0, 0), QPointF(uv_rect.width(), 0),
                                  QPointF(uv_rect.width(), uv_rect.height()), QPointF(0, uv_rect.height())])
            tf = QTransform()
            painter.save()
            if QTransform.quadToQuad(src_poly, poly, tf):
                painter.setTransform(tf)
                painter.drawImage(0, 0, tex)
            else:
                painter.setBrush(QColor(100, 100, 100))
                painter.drawPolygon(poly)
            painter.restore()

# --- lienzo 2D ---
class Canvas2D(QWidget):
    MIN_ZOOM, MAX_ZOOM = 1, 48

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.zoom = 10
        self._bg_cache = None
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.fit_mode = True        # mientras sea True, el lienzo se ajusta solo al tamaño de la ventana
        self.last_pos = None
        self.drawing = False
        self.panning = False
        self.space_down = False
        self.show_grid = True
        self.show_layout = True
        self.hover = None
        self._cache = None
        self.start_pos = None
        self.preview_pixels = []

        self.setMouseTracking(True)
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.CrossCursor)

    # vista
    def _notify_zoom(self):
        self.main.on_canvas_zoom_changed(self.zoom)

    def fit_to_view(self):
        margin = 12
        avail = min(self.width(), self.height()) - 2 * margin
        self.zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, avail // SIZE))
        self.fit_mode = True
        self.offset_x = (self.width() - SIZE * self.zoom) / 2
        self.offset_y = (self.height() - SIZE * self.zoom) / 2
        self._notify_zoom()
        self.update()

    def clamp_offsets(self):
        """Mantiene la imagen dentro de la vista (centrable si es pequeña, desplazable si es grande)."""
        size = SIZE * self.zoom
        lo, hi = sorted((self.width() - size, 0))
        self.offset_x = max(lo, min(hi, self.offset_x))
        lo, hi = sorted((self.height() - size, 0))
        self.offset_y = max(lo, min(hi, self.offset_y))

    def set_zoom(self, new_zoom, anchor=None):
        """Cambia el zoom manteniendo fijo el punto 'anchor' (por defecto el centro de la vista)."""
        new_zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(new_zoom)))
        if new_zoom == self.zoom:
            return
        ax = anchor.x() if anchor is not None else self.width() / 2
        ay = anchor.y() if anchor is not None else self.height() / 2
        u = (ax - self.offset_x) / self.zoom
        v = (ay - self.offset_y) / self.zoom
        self.zoom = new_zoom
        self.offset_x = ax - u * new_zoom
        self.offset_y = ay - v * new_zoom
        self.fit_mode = False
        self.clamp_offsets()
        self._notify_zoom()
        self.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.fit_mode:
            self.fit_to_view()
        else:
            self.clamp_offsets()

    # dibujo
    def get_canvas_image(self):
        """Imagen del lienzo con caché: solo se regenera si cambió la skin, las zonas o el layout."""
        zones = tuple(sorted(self.main.active_zones.items()))
        key = (self.main.skin.image.cacheKey(), zones, LAYOUT_VERSION)
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        img = self.generate_canvas_image()
        self._cache = (key, img)
        return img

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        z = self.zoom
        ox, oy = int(self.offset_x), int(self.offset_y)
        size = SIZE * z

        painter.drawImage(QRect(ox, oy, size, size), self.get_canvas_image())

        if self.show_grid and z >= 4:
            painter.setPen(QColor(255, 255, 255, 20))
            for i in range(SIZE + 1):
                painter.drawLine(ox + i * z, oy, ox + i * z, oy + size)
                painter.drawLine(ox, oy + i * z, ox + size, oy + i * z)

        if self.show_layout:
            painter.setPen(QColor(0, 0, 0, 150))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for part, face, x, y, w, h, ov in FACE_RECTS:
                painter.drawRect(ox + x * z, oy + y * z, w * z, h * z)

        # Marco de la imagen
        painter.setPen(QColor("#3a3a3a"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(ox - 1, oy - 1, size + 1, size + 1)

        # Previsualización de formas
        if self.preview_pixels:
            painter.setPen(QColor(255, 230, 0, 150))
            painter.setBrush(QColor(255, 230, 0, 50))
            for px, py in self.preview_pixels:
                if self.main.tool == "line" or self.main.tool == "rect":
                    painter.drawRect(ox + px * z, oy + py * z, z, z)

        # Píxel bajo el cursor
        if self.hover and not self.panning:
            hx, hy = self.hover
            painter.setPen(QColor(255, 255, 255, 220))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(ox + hx * z, oy + hy * z, z, z)

    def _background_image(self):
        """Fondo del lienzo (tintes por cara, damero y zonas desactivadas). Solo se rehace si cambia el layout o las zonas."""
        zones = tuple(sorted(self.main.active_zones.items()))
        key = (zones, LAYOUT_VERSION, SIZE)
        if self._bg_cache is not None and self._bg_cache[0] == key:
            return self._bg_cache[1]
        bg = QImage(SIZE, SIZE, QImage.Format.Format_ARGB32_Premultiplied)
        tints = {ov: {f: (c.darker(110), c) for f, c in d.items()} for ov, d in FACE_TINT.items()}
        off_a, off_b = QColor(40, 20, 20), QColor(30, 15, 15)
        out_a, out_b = QColor(45, 45, 45), QColor(35, 35, 35)
        for y in range(SIZE):
            row = FACE_AT[y]
            for x in range(SIZE):
                even = (x + y) % 2 == 0
                info = row[x]
                if info:
                    part, face, lx, ly, ov = info
                    if not self.main.active_zones.get(get_zone(part), True):
                        c = off_a if even else off_b
                    else:
                        dark, normal = tints[ov][face]
                        c = dark if even else normal
                else:
                    c = out_a if even else out_b
                bg.setPixelColor(x, y, c)
        self._bg_cache = (key, bg)
        return bg

    def generate_canvas_image(self):
        """Fondo + skin dibujada encima (rápido incluso a 256 px). Las zonas desactivadas se vuelven a tapar."""
        bg = self._background_image()
        img = bg.copy()
        pt = QPainter(img)
        pt.drawImage(0, 0, self.main.skin.image)
        for part, face, x, y, w, h, ov in FACE_RECTS:
            if not self.main.active_zones.get(get_zone(part), True):
                pt.drawImage(x, y, bg, x, y, w, h)
        pt.end()
        return img

    def get_cell(self, pos):
        return int((pos.x() - self.offset_x) // self.zoom), int((pos.y() - self.offset_y) // self.zoom)

    # ratón
    def mousePressEvent(self, e):
        btn = e.button()
        alt = bool(e.modifiers() & Qt.KeyboardModifier.AltModifier)
        if btn == Qt.MouseButton.MiddleButton or (btn == Qt.MouseButton.LeftButton and (alt or self.space_down)):
            self.panning = True
            self.last_pos = e.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        if btn in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            px, py = self.get_cell(e.position())
            if not (0 <= px < SIZE and 0 <= py < SIZE):
                return
            self.drawing = True
            self.main.start_draw()

            if self.main.tool in ("line", "rect"):
                self.start_pos = (px, py)
            else:
                self.handle_draw(e.position(), btn == Qt.MouseButton.RightButton)

    def mouseMoveEvent(self, e):
        if self.panning:
            delta = e.position() - self.last_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_pos = e.position()
            self.fit_mode = False
            self.clamp_offsets()
            self.update()
            return

        px, py = self.get_cell(e.position())
        self.hover = (px, py) if (0 <= px < SIZE and 0 <= py < SIZE) else None
        if self.drawing:
            if self.main.tool in ("line", "rect") and self.start_pos:
                self.update_preview_shape(self.start_pos, (px, py))
            else:
                self.handle_draw(e.position(), e.buttons() == Qt.MouseButton.RightButton)

        self.main.update_status(px, py)
        self.update()

    def mouseReleaseEvent(self, e):
        if self.panning and e.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):
            self.panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor if self.space_down else Qt.CursorShape.CrossCursor)
            return

        if e.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton) and self.drawing:
            self.drawing = False
            if self.main.tool in ("line", "rect") and self.start_pos:
                self.preview_pixels = []
                px, py = self.get_cell(e.position())
                self.commit_shape(self.start_pos, (px, py), e.button() == Qt.MouseButton.RightButton)
                self.start_pos = None
            self.main.end_draw()
            self.update()

    def wheelEvent(self, e):
        """La rueda hace zoom hacia el cursor."""
        delta = e.angleDelta().y()
        if delta == 0:
            return
        z = self.zoom
        new = max(z + 1, round(z * 1.15)) if delta > 0 else min(z - 1, round(z / 1.15))
        self.set_zoom(new, e.position())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space:
            if not e.isAutoRepeat():
                self.space_down = True
                if not self.panning:
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
            return
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Space:
            if not e.isAutoRepeat():
                self.space_down = False
                if not self.panning:
                    self.setCursor(Qt.CursorShape.CrossCursor)
            return
        super().keyReleaseEvent(e)

    def focusOutEvent(self, e):
        self.space_down = False
        if not self.panning:
            self.setCursor(Qt.CursorShape.CrossCursor)
        super().focusOutEvent(e)

    def enterEvent(self, e):
        self.setFocus()   # para que Espacio (mover) funcione sin hacer clic antes
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.hover = None
        self.main.update_status(-1, -1)
        self.update()
        super().leaveEvent(e)

    def update_preview_shape(self, a, b):
        self.preview_pixels = []
        x0, y0 = a
        x1, y1 = b
        if self.main.tool == "line":
            # Bresenham
            dx, dy = abs(x1 - x0), -abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx + dy
            while True:
                self.preview_pixels.append((x0, y0))
                if x0 == x1 and y0 == y1: break
                e2 = 2 * err
                if e2 >= dy: err += dy; x0 += sx
                if e2 <= dx: err += dx; y0 += sy
        else:
            lx, hx = min(x0, x1), max(x0, x1)
            ly, hy = min(y0, y1), max(y0, y1)
            for yy in range(ly, hy + 1):
                for xx in range(lx, hx + 1):
                    self.preview_pixels.append((xx, yy))
        self.update()

    def commit_shape(self, a, b, is_erase):
        x0, y0 = a
        x1, y1 = b
        cells = []
        if self.main.tool == "line":
            dx, dy = abs(x1 - x0), -abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx + dy
            while True:
                cells.append((x0, y0))
                if x0 == x1 and y0 == y1: break
                e2 = 2 * err
                if e2 >= dy: err += dy; x0 += sx
                if e2 <= dx: err += dx; y0 += sy
        else:
            lx, hx = min(x0, x1), max(x0, x1)
            ly, hy = min(y0, y1), max(y0, y1)
            for yy in range(ly, hy + 1):
                for xx in range(lx, hx + 1):
                    cells.append((xx, yy))
                    
        for px, py in cells:
            self.main.draw_pixel(px, py, is_erase)
        self.update()

    def handle_draw(self, pos, is_erase):
        px, py = self.get_cell(pos)
        if 0 <= px < SIZE and 0 <= py < SIZE:
            self.main.draw_pixel(px, py, is_erase)
            self.update()

# --- ventana principal ---
TOOL_ORDER = ["pencil", "eraser", "bucket", "picker", "replace", "line", "rect"]
TOOL_KEYS = {"pencil": "P", "eraser": "E", "bucket": "G", "picker": "I", "replace": "C", "line": "L", "rect": "R"}

class SkinEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("TeEditorS", "TeEditor")
        saved = str(self.settings.value("lang", ""))
        set_language(saved if saved in I18N else system_language())
        self.setWindowIcon(QIcon(resource_path("tessskin_ico.ico")))

        self.setWindowTitle("Tessy's Skin Editor")
        self.setMinimumSize(900, 600)
        geo = QApplication.primaryScreen().availableGeometry()
        self.resize(min(1300, geo.width() - 40), min(850, geo.height() - 60))

        self.skin = SkinEditorState()
        self.color = QColor(200, 30, 30)
        self.tool = "pencil"
        self.body_type = "steve"   # "steve" = normal (brazos 4 px), "alex" = slim (brazos 3 px)
        self.active_zones = {z: True for z in ["head", "body", "rarm", "larm", "rleg", "lleg"]}
        self.undo_stack = []
        self.redo_stack = []
        self._stroke_before = None
        self._i18n = []
        self._retr_hooks = []
        self.dirty = False            # hay cambios sin guardar en un archivo
        self._clean_image = None      # última versión guardada/abierta (para saber si hay cambios)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(1500)
        self.autosave_timer.timeout.connect(self.write_recovery)

        # La rueda solo controla un control si fue clickeado (queda "armado");
        # si no, la rueda desplaza el panel en lugar de cambiar el valor.
        self._wheel_guard = WheelGuard(self)
        QApplication.instance().installEventFilter(self._wheel_guard)

        self.init_ui()

        # Instalar el filtro también a nivel de cada control (la forma fiable).
        for cls in self._wheel_guard.GUARDED:
            for w in self.findChildren(cls):
                w.installEventFilter(self._wheel_guard)

        self.apply_style()
        self.base_title = self.windowTitle()
        self._update_title()
        self.load_base("steve", record=False)
        self._clean_image = self.skin.image.copy()
        self.update_history_actions()

    # idiomas
    def bind(self, setter, key):
        """Asocia un texto de la interfaz a una clave de traducción (str) o a una función que devuelve el texto."""
        self._i18n.append((setter, key))
        setter(key() if callable(key) else T(key))

    def refresh_brush_texts(self):
        for i in range(self.brush_combo.count()):
            self.brush_combo.setItemText(i, T(self.brush_combo.itemData(i)))

    def retranslate(self):
        for setter, key in self._i18n:
            setter(key() if callable(key) else T(key))
        for fn in self._retr_hooks:
            fn()
        self.coord_label.setText("")

    def on_language_changed(self, index):
        code = self.lang_combo.itemData(index)
        set_language(code)
        self.settings.setValue("lang", code)
        self.retranslate()

    def add_shortcut(self, seq, fn):
        sc = QShortcut(QKeySequence(seq), self)
        sc.activated.connect(fn)
        return sc

    # interfaz
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- TOP TOOLBAR ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.act_undo = QAction(self)
        self.act_undo.setShortcut(QKeySequence("Ctrl+Z"))
        self.act_undo.triggered.connect(self.undo)
        toolbar.addAction(self.act_undo)
        self.bind(self.act_undo.setText, "undo")

        self.act_redo = QAction(self)
        self.act_redo.setShortcuts([QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")])
        self.act_redo.triggered.connect(self.redo)
        toolbar.addAction(self.act_redo)
        self.bind(self.act_redo.setText, "redo")
        toolbar.addSeparator()

        self.grid_action = QAction(self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.setShortcut(QKeySequence("Ctrl+G"))
        self.grid_action.triggered.connect(self.toggle_grid)
        toolbar.addAction(self.grid_action)
        self.bind(self.grid_action.setText, "grid")

        self.layout_action = QAction(self)
        self.layout_action.setCheckable(True)
        self.layout_action.setChecked(True)
        self.layout_action.triggered.connect(self.toggle_layout)
        toolbar.addAction(self.layout_action)
        self.bind(self.layout_action.setText, "guides")

        # selector de idioma (a la derecha)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        toolbar.addWidget(QLabel("🌐 "))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(max(0, self.lang_combo.findData(LANG)))
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        toolbar.addWidget(self.lang_combo)
        self.bind(self.lang_combo.setToolTip, "language")

        self.act_about = QAction(self)
        self.act_about.triggered.connect(self.show_about)
        toolbar.addAction(self.act_about)
        self.bind(self.act_about.setText, "about_btn")

        # --- SPLITTER ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # panel izquierdo
        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setContentsMargins(12, 12, 12, 12)

        tools_group = QGroupBox()
        self.bind(tools_group.setTitle, "tools_group")
        tools_layout = QGridLayout(tools_group)
        self.tool_buttons = {}
        for i, name in enumerate(TOOL_ORDER):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=name: self.set_tool(t))
            tools_layout.addWidget(btn, i // 2, i % 2)
            self.tool_buttons[name] = btn
            self.bind(btn.setText, "tool_" + name)
            self.bind(btn.setToolTip, lambda n=name: f"{T('tool_' + n)}  [{TOOL_KEYS[n]}]")
        self.tool_buttons["pencil"].setChecked(True)

        self.mirror_check = QCheckBox()
        self.bind(self.mirror_check.setText, "mirror")
        tools_layout.addWidget(self.mirror_check, (len(TOOL_ORDER) + 1) // 2, 0, 1, 2)
        left_layout.addWidget(tools_group)

        # --- pinceles ---
        brushes_group = QGroupBox()
        self.bind(brushes_group.setTitle, "brushes_group")
        brushes_layout = QGridLayout(brushes_group)
        shape_lbl = QLabel(); self.bind(shape_lbl.setText, "brush_shape")
        brushes_layout.addWidget(shape_lbl, 0, 0)
        self.brush_combo = QComboBox()
        for key in ("brush_dot", "brush_square", "brush_circle", "brush_spray", "brush_soft"):
            self.brush_combo.addItem(key, key)   # data = clave de i18n
        self._retr_hooks.append(self.refresh_brush_texts)
        self.refresh_brush_texts()
        brushes_layout.addWidget(self.brush_combo, 0, 1)
        size_lbl = QLabel(); self.bind(size_lbl.setText, "brush_size")
        brushes_layout.addWidget(size_lbl, 1, 0)
        self.brush_size = QSlider(Qt.Orientation.Horizontal)
        self.brush_size.setRange(1, 8)
        self.brush_size.setValue(1)
        self.brush_size_value = QLabel("1")
        self.brush_size_value.setMinimumWidth(20)
        self.brush_size.valueChanged.connect(lambda v: self.brush_size_value.setText(str(v)))
        brushes_layout.addWidget(self.brush_size, 1, 1)
        brushes_layout.addWidget(self.brush_size_value, 1, 2)
        strength_lbl = QLabel(); self.bind(strength_lbl.setText, "brush_strength")
        brushes_layout.addWidget(strength_lbl, 2, 0)
        self.brush_strength = QSlider(Qt.Orientation.Horizontal)
        self.brush_strength.setRange(5, 100)
        self.brush_strength.setValue(100)
        self.brush_strength_value = QLabel("100%")
        self.brush_strength_value.setMinimumWidth(38)
        self.brush_strength.valueChanged.connect(lambda v: self.brush_strength_value.setText(f"{v}%"))
        brushes_layout.addWidget(self.brush_strength, 2, 1)
        brushes_layout.addWidget(self.brush_strength_value, 2, 2)
        left_layout.addWidget(brushes_group)

        color_group = QGroupBox()
        self.bind(color_group.setTitle, "color_group")
        color_layout = QVBoxLayout(color_group)
        row = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 30)
        self.color_btn.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #555; border-radius: 4px;")
        self.color_btn.clicked.connect(self.pick_color)
        self.hex_input = QLineEdit(self.color.name().upper())
        self.hex_input.setFixedWidth(80)
        self.hex_input.returnPressed.connect(self.apply_hex)
        row.addWidget(self.color_btn)
        row.addWidget(self.hex_input)
        row.addStretch()
        color_layout.addLayout(row)

        alpha_lbl = QLabel()
        self.bind(alpha_lbl.setText, "alpha")
        color_layout.addWidget(alpha_lbl)
        alpha_row = QHBoxLayout()
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(255)
        self.alpha_value = QLabel("100%")
        self.alpha_value.setMinimumWidth(40)
        self.alpha_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.alpha_slider.valueChanged.connect(lambda v: self.alpha_value.setText(f"{round(v / 255 * 100)}%"))
        alpha_row.addWidget(self.alpha_slider)
        alpha_row.addWidget(self.alpha_value)
        color_layout.addLayout(alpha_row)

        var_lbl = QLabel(); self.bind(var_lbl.setText, "variation")
        self.bind(var_lbl.setToolTip, "variation_tip")
        color_layout.addWidget(var_lbl)
        var_row = QHBoxLayout()
        self.var_slider = QSlider(Qt.Orientation.Horizontal)
        self.var_slider.setRange(0, 50)
        self.var_slider.setValue(0)
        self.bind(self.var_slider.setToolTip, "variation_tip")
        self.var_value = QLabel("0%")
        self.var_value.setMinimumWidth(40)
        self.var_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.var_slider.valueChanged.connect(lambda v: self.var_value.setText(f"{v}%"))
        var_row.addWidget(self.var_slider)
        var_row.addWidget(self.var_value)
        color_layout.addLayout(var_row)
        left_layout.addWidget(color_group)

        model_group = QGroupBox()
        self.bind(model_group.setTitle, "model_group")
        model_layout = QVBoxLayout(model_group)
        body_lbl = QLabel()
        self.bind(body_lbl.setText, "body_type")
        model_layout.addWidget(body_lbl)
        body_row = QHBoxLayout()
        self.body_buttons = {}
        for key, tkey in (("steve", "body_default"), ("alex", "body_slim")):
            b = QPushButton()
            b.setCheckable(True)
            b.clicked.connect(lambda checked, k=key: self.set_body_type(k))
            self.bind(b.setText, tkey)
            body_row.addWidget(b)
            self.body_buttons[key] = b
        model_layout.addLayout(body_row)
        res_lbl = QLabel()
        self.bind(res_lbl.setText, "resolution")
        model_layout.addWidget(res_lbl)
        self.res_combo = QComboBox()
        for r in RESOLUTIONS:
            self.res_combo.addItem(f"{r} × {r}", r)
        self.res_combo.setCurrentIndex(RESOLUTIONS.index(SIZE))
        self.res_combo.currentIndexChanged.connect(self.on_resolution_changed)
        model_layout.addWidget(self.res_combo)
        left_layout.addWidget(model_group)

        zones_group = QGroupBox()
        self.bind(zones_group.setTitle, "zones_group")
        zones_layout = QGridLayout(zones_group)
        self.zone_checkboxes = {}
        for i, zone in enumerate(["head", "body", "rarm", "larm", "rleg", "lleg"]):
            cb = QCheckBox()
            cb.setChecked(True)
            cb.stateChanged.connect(lambda state, z=zone: self.toggle_zone(z, state))
            zones_layout.addWidget(cb, i // 2, i % 2)
            self.zone_checkboxes[zone] = cb
            self.bind(cb.setText, "part_" + zone)
        left_layout.addWidget(zones_group)

        file_group = QGroupBox()
        self.bind(file_group.setTitle, "file_group")
        file_layout = QGridLayout(file_group)
        btn_open = QPushButton()
        btn_save = QPushButton()
        btn_mojang = QPushButton()
        btn_url = QPushButton()
        btn_copy = QPushButton()
        btn_open.clicked.connect(self.open_file)
        btn_save.clicked.connect(self.save_file)
        btn_mojang.clicked.connect(self.import_mojang)
        btn_url.clicked.connect(self.import_url)
        btn_copy.clicked.connect(self.copy_image_to_clipboard)
        file_layout.addWidget(btn_open, 0, 0)
        file_layout.addWidget(btn_save, 0, 1)
        file_layout.addWidget(btn_mojang, 1, 0, 1, 2)
        file_layout.addWidget(btn_url, 2, 0, 1, 2)
        file_layout.addWidget(btn_copy, 3, 0, 1, 2)
        self.bind(btn_open.setText, "open_png")
        self.bind(btn_save.setText, "save_png")
        self.bind(btn_mojang.setText, "import_mojang")
        self.bind(btn_url.setText, "import_url")
        self.bind(btn_copy.setText, "copy_image")
        btn_open.setToolTip("Ctrl+O")
        btn_save.setToolTip("Ctrl+S")
        btn_copy.setToolTip("Ctrl+Shift+C")
        left_layout.addWidget(file_group)

        presets_group = QGroupBox()
        self.bind(presets_group.setTitle, "presets_group")
        presets_layout = QGridLayout(presets_group)
        for i, preset in enumerate(("steve", "alex", "wraith", "zombie")):
            b = QPushButton()
            b.clicked.connect(lambda checked=False, p=preset: self.load_base(p))
            self.bind(b.setText, "preset_" + preset)
            presets_layout.addWidget(b, i // 2, i % 2)
        left_layout.addWidget(presets_group)
        left_layout.addStretch()

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setWidget(left_content)
        left_scroll.setMinimumWidth(270)
        left_scroll.setMaximumWidth(340)

        # centro
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        self.canvas = Canvas2D(self)
        center_layout.addWidget(self.canvas, 1)

        zoom_bar = QWidget()
        zb = QHBoxLayout(zoom_bar)
        zb.setContentsMargins(10, 6, 10, 6)
        zoom_lbl = QLabel()
        self.bind(zoom_lbl.setText, "zoom_lbl")
        self.btn_zoom_out = QPushButton("－")
        self.btn_zoom_out.setFixedSize(32, 28)
        self.btn_zoom_in = QPushButton("＋")
        self.btn_zoom_in.setFixedSize(32, 28)
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(Canvas2D.MIN_ZOOM, Canvas2D.MAX_ZOOM)
        self.zoom_slider.setValue(self.canvas.zoom)
        self.zoom_value = QLabel(f"{self.canvas.zoom}×")
        self.zoom_value.setMinimumWidth(36)
        self.btn_fit = QPushButton()
        self.bind(self.btn_fit.setText, "fit")
        self.bind(self.btn_fit.setToolTip, "fit_tip")
        self.bind(self.btn_zoom_in.setToolTip, "zoom_in_tip")
        self.bind(self.btn_zoom_out.setToolTip, "zoom_out_tip")
        self.btn_zoom_out.clicked.connect(lambda: self.zoom_step(-1))
        self.btn_zoom_in.clicked.connect(lambda: self.zoom_step(1))
        self.btn_fit.clicked.connect(self.canvas.fit_to_view)
        self.zoom_slider.valueChanged.connect(self.set_zoom_from_slider)
        zb.addWidget(zoom_lbl)
        zb.addWidget(self.btn_zoom_out)
        zb.addWidget(self.zoom_slider, 1)
        zb.addWidget(self.btn_zoom_in)
        zb.addWidget(self.zoom_value)
        zb.addWidget(self.btn_fit)
        center_layout.addWidget(zoom_bar)

        # panel derecho
        right_panel = QWidget()
        right_panel.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)

        viewer_group = QGroupBox()
        self.bind(viewer_group.setTitle, "viewer_group")
        viewer_layout = QVBoxLayout(viewer_group)
        self.viewer = Viewer3D()
        self.viewer.active_zones = self.active_zones   # comparten el mismo diccionario
        self.viewer.set_skin(self.skin)
        self.bind(self.viewer.setToolTip, "viewer_tip")
        viewer_layout.addWidget(self.viewer, 1)

        pose_layout = QHBoxLayout()
        self.pose_buttons = {}
        for pose in ["idle", "walk", "run"]:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, p=pose: self.set_pose(p))
            pose_layout.addWidget(btn)
            self.pose_buttons[pose] = btn
            self.bind(btn.setText, "pose_" + pose)
        self.pose_buttons["idle"].setChecked(True)
        viewer_layout.addLayout(pose_layout)

        btn_reset_view = QPushButton()
        btn_reset_view.clicked.connect(self.viewer.reset_view)
        self.bind(btn_reset_view.setText, "reset_view")
        viewer_layout.addWidget(btn_reset_view)
        right_layout.addWidget(viewer_group, 1)

        splitter.addWidget(left_scroll)
        splitter.addWidget(center)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([300, 640, 360])

        main_layout.addWidget(splitter)

        # barra de estado
        self.hint_label = QLabel()
        self.hint_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.statusBar().addWidget(self.hint_label, 1)
        self.bind(self.hint_label.setText, "hint")
        self.coord_label = QLabel("")
        self.statusBar().addPermanentWidget(self.coord_label)

        # atajos
        for name, key in TOOL_KEYS.items():
            self.add_shortcut(key, lambda t=name: self.set_tool(t))
        self.add_shortcut("M", self.mirror_check.toggle)
        self.add_shortcut("Ctrl+S", self.save_file)
        self.add_shortcut("Ctrl+O", self.open_file)
        self.add_shortcut("Ctrl+0", self.canvas.fit_to_view)
        for seq in ("Ctrl++", "Ctrl+="):
            self.add_shortcut(seq, lambda: self.zoom_step(1))
        self.add_shortcut("Ctrl+-", lambda: self.zoom_step(-1))
        self.add_shortcut("Ctrl+Shift+C", self.copy_image_to_clipboard)

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QWidget { color: #e0e0e0; background-color: #1a1a1a; font-family: "Segoe UI", Arial; font-size: 13px; }
            QGroupBox { border: 1px solid #3a3a3a; border-radius: 6px; margin-top: 12px; padding-top: 6px; font-weight: bold; color: #4f8cff; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; left: 8px; }
            QPushButton { background-color: #2b2b2b; border: 1px solid #3a3a3a; border-radius: 4px; padding: 6px 4px; }
            QPushButton:hover { background-color: #3a3a3a; }
            QPushButton:pressed { background-color: #4a4a4a; }
            QPushButton:checked { background-color: #4f8cff; color: white; border-color: #4f8cff; }
            QPushButton:disabled { color: #666; }
            QLineEdit { background-color: #111; border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px; color: white; }
            QComboBox { background-color: #2b2b2b; border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px 8px; min-width: 90px; }
            QComboBox QAbstractItemView { background-color: #2b2b2b; selection-background-color: #4f8cff; color: #e0e0e0; }
            QSlider::groove:horizontal { height: 4px; background: #3a3a3a; border-radius: 2px; }
            QSlider::handle:horizontal { background: #4f8cff; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
            QCheckBox { spacing: 6px; }
            QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #555; border-radius: 3px; background: #2b2b2b; }
            QCheckBox::indicator:checked { background: #4f8cff; border-color: #4f8cff; }
            QScrollArea { border: none; }
            QScrollBar:vertical { background: #1a1a1a; width: 10px; margin: 0; }
            QScrollBar::handle:vertical { background: #3a3a3a; border-radius: 5px; min-height: 24px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QSplitter::handle { background: #252525; }
            QSplitter::handle:hover { background: #4f8cff; }
            QStatusBar { background-color: #252525; color: #888; }
            QStatusBar QLabel { background-color: transparent; color: #888; }
            QToolBar { background-color: #252525; border-bottom: 1px solid #1a1a1a; spacing: 10px; padding: 4px; }
            QToolBar QWidget { background-color: transparent; }
            QToolButton { color: white; padding: 5px; border-radius: 4px; }
            QToolButton:hover { background-color: #3a3a3a; }
            QToolButton:checked { background-color: #31456b; }
            QToolButton:disabled { color: #666; }
            QToolTip { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #4f8cff; padding: 4px; }
        """)

    # vistas
    def toggle_grid(self, state):
        self.canvas.show_grid = state
        self.canvas.update()

    def toggle_layout(self, state):
        self.canvas.show_layout = state
        self.canvas.update()

    def set_zoom_from_slider(self, val):
        self.canvas.set_zoom(val)

    def on_canvas_zoom_changed(self, z):
        """El lienzo cambió su zoom (rueda, ajustar, etc.): sincroniza la barra de zoom."""
        if not hasattr(self, "zoom_slider"):
            return
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(z)
        self.zoom_slider.blockSignals(False)
        self.zoom_value.setText(f"{z}×")

    def zoom_step(self, direction):
        z = self.canvas.zoom
        new = max(z + 1, round(z * 1.25)) if direction > 0 else min(z - 1, round(z / 1.25))
        self.canvas.set_zoom(new)

    def set_tool(self, tool):
        self.tool = tool
        for t, btn in self.tool_buttons.items():
            btn.setChecked(t == tool)

    def set_pose(self, pose):
        self.viewer.pose = pose
        for p, btn in self.pose_buttons.items():
            btn.setChecked(p == pose)
        self.viewer.update()

    def toggle_zone(self, zone, state):
        self.active_zones[zone] = (state == Qt.CheckState.Checked.value)
        self.canvas.update()
        self.viewer.update()

    def update_status(self, x, y):
        if 0 <= x < SIZE and 0 <= y < SIZE:
            info = FACE_AT[y][x]
            if info:
                self.coord_label.setText(f"X: {x}  Y: {y}  |  {T('part_' + info[0])} ({T('face_' + info[1])})")
            else:
                self.coord_label.setText(f"X: {x}  Y: {y}  |  {T('free')}")
        else:
            self.coord_label.setText("")

    # dibujo e undo
    def start_draw(self):
        # Guardamos cómo estaba la imagen; solo entra al historial si el trazo cambió algo.
        self._stroke_before = self.skin.image.copy()

    def end_draw(self):
        before, self._stroke_before = self._stroke_before, None
        if before is not None and before != self.skin.image:
            self.push_undo(before)
            self.mark_dirty()
        self.canvas.update()
        self.viewer.update()

    def push_undo(self, snapshot):
        self.undo_stack.append(snapshot)
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.update_history_actions()

    def update_history_actions(self):
        self.act_undo.setEnabled(bool(self.undo_stack))
        self.act_redo.setEnabled(bool(self.redo_stack))

    def paint_color(self):
        c = QColor(self.color)
        c.setAlpha(self.alpha_slider.value())
        return vary_color(c, self.var_slider.value())

    def paint_brush(self, cx, cy, is_erase):
        shape = self.brush_combo.currentData()
        size = self.brush_size.value()
        strength = self.brush_strength.value() / 100.0
        R = size - 1
        base = self.paint_color()
        for dy in range(-R, R + 1):
            for dx in range(-R, R + 1):
                if shape == "brush_circle" and dx*dx + dy*dy > R*R + R:
                    continue
                if shape == "brush_spray" and random.random() > 0.35 * strength:
                    continue
                px, py = cx + dx, cy + dy
                if not (0 <= px < SIZE and 0 <= py < SIZE):
                    continue
                info = FACE_AT[py][px]
                if info and not self.active_zones.get(get_zone(info[0]), True):
                    continue
                if is_erase:
                    self.skin.image.setPixelColor(px, py, Qt.GlobalColor.transparent)
                elif shape == "brush_soft":
                    old = self.skin.image.pixelColor(px, py)
                    a = strength
                    c = QColor(int(old.red()*(1-a) + base.red()*a),
                               int(old.green()*(1-a) + base.green()*a),
                               int(old.blue()*(1-a) + base.blue()*a),
                               int(old.alpha()*(1-a) + base.alpha()*a))
                    self.skin.image.setPixelColor(px, py, c)
                else:
                    self.skin.image.setPixelColor(px, py, base)

    def draw_pixel(self, x, y, is_erase):
        if not (0 <= x < SIZE and 0 <= y < SIZE): return
        info = FACE_AT[y][x]
        if info and not self.active_zones.get(get_zone(info[0]), True): return
            
        if self.tool == "picker":
            c = self.skin.image.pixelColor(x, y)
            if c.alpha() > 0: self.set_color(c)
            return
        if self.tool == "bucket":
            self.flood_fill(x, y, is_erase)
            return
        if self.tool == "replace":
            self.replace_color(x, y, is_erase)
            return
            
        pixels_to_draw = [(x, y)]
        if self.mirror_check.isChecked():
            mx = get_mirrored_pos(x, y)
            if mx: pixels_to_draw.append(mx)
            
        for px, py in pixels_to_draw:
            self.paint_brush(px, py, is_erase or self.tool == "eraser")
        self.viewer.update()

    def flood_fill(self, x, y, is_erase):
        target = self.skin.image.pixelColor(x, y)
        fill_color = QColor(Qt.GlobalColor.transparent) if is_erase else QColor(self.color)
        if not is_erase: fill_color.setAlpha(self.alpha_slider.value())
        if target == fill_color: return
        origin = FACE_AT[y][x]
        if not origin: return
        stack = [(x, y)]
        visited = set()
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited or not (0 <= cx < SIZE and 0 <= cy < SIZE): continue
            visited.add((cx, cy))
            info = FACE_AT[cy][cx]
            if not info or (info[0], info[1], info[4]) != (origin[0], origin[1], origin[4]): continue
            if not self.active_zones.get(get_zone(info[0]), True): continue
            if self.skin.image.pixelColor(cx, cy) != target: continue
            self.skin.image.setPixelColor(cx, cy, fill_color)
            stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
        self.viewer.update()

    def replace_color(self, x, y, is_erase):
        target = self.skin.image.pixelColor(x, y)
        fill_color = QColor(Qt.GlobalColor.transparent) if is_erase else QColor(self.color)
        if not is_erase: fill_color.setAlpha(self.alpha_slider.value())
        if target == fill_color: return
        for cy in range(SIZE):
            for cx in range(SIZE):
                info = FACE_AT[cy][cx]
                if info and not self.active_zones.get(get_zone(info[0]), True): continue
                if self.skin.image.pixelColor(cx, cy) == target:
                    self.skin.image.setPixelColor(cx, cy, fill_color)
        self.viewer.update()

    def undo(self):
        if not self.undo_stack:
            self.statusBar().showMessage(T("nothing_undo"), 1500)
            return
        self.redo_stack.append(self.skin.image.copy())
        self.skin.image = self.undo_stack.pop()
        self.sync_size_from_image()
        self.update_history_actions()
        self.canvas.update()
        self.viewer.update()
        self.mark_dirty()
        self.statusBar().showMessage(T("undone"), 1200)

    def redo(self):
        if not self.redo_stack:
            self.statusBar().showMessage(T("nothing_redo"), 1500)
            return
        self.undo_stack.append(self.skin.image.copy())
        self.skin.image = self.redo_stack.pop()
        self.sync_size_from_image()
        self.update_history_actions()
        self.canvas.update()
        self.viewer.update()
        self.mark_dirty()
        self.statusBar().showMessage(T("redone"), 1200)

    def set_color(self, c):
        self.color = c
        self.color_btn.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #555; border-radius: 4px;")
        self.hex_input.setText(self.color.name().upper())

    def pick_color(self):
        c = QColorDialog.getColor(self.color, self, T("pick_color"))
        if c.isValid(): self.set_color(c)

    def apply_hex(self):
        c = QColor(self.hex_input.text())
        if c.isValid(): self.set_color(c)

    STARTER_PRESETS = {
        "steve":  ("steve", ((198, 142, 106), (74, 50, 32),  (35, 170, 170), (60, 58, 154),  (110, 110, 110), (255, 255, 255), (80, 60, 170),  (170, 115, 85), (140, 90, 70))),
        "alex":   ("alex",  ((250, 200, 160), (210, 130, 40), (80, 180, 80),  (100, 70, 50),  (60, 60, 60),    (255, 255, 255), (40, 130, 60),  (220, 160, 120), (180, 100, 100))),
        "wraith": ("steve", ((191, 190, 182), (32, 32, 46),   (26, 46, 54),   (30, 24, 44),   (20, 20, 30),    (240, 240, 235), (16, 16, 24),   (32, 32, 46),   (20, 20, 30))),
        "zombie": ("steve", ((96, 140, 88),   (44, 44, 44),   (62, 90, 85),   (45, 45, 63),   (32, 34, 44),    (184, 184, 168), (42, 42, 26),   (60, 90, 70),   (30, 44, 30))),
    }

    def load_base(self, skin_type, record=True):
        target = SIZE                        # resolución actual: la base se dibuja a 64 y se escala
        body_type, (SK_, HR_, SH_, PA_, SN_, WH_, IR_, NO_, MO_) = self.STARTER_PRESETS.get(
            skin_type, self.STARTER_PRESETS["steve"])
        build_layout(body_type, 64)
        if record:
            self.push_undo(self.skin.image.copy())
        self.skin.image.fill(Qt.GlobalColor.transparent)

        SK = QColor(*SK_); HR = QColor(*HR_); SH = QColor(*SH_); PA = QColor(*PA_)
        SN = QColor(*SN_); WH = QColor(*WH_); IR = QColor(*IR_); NO = QColor(*NO_); MO = QColor(*MO_)

        img = QImage(64, 64, QImage.Format.Format_RGBA8888)
        img.fill(Qt.GlobalColor.transparent)
        for part, face, x, y, w, h, ov in FACE_RECTS:
            if ov: continue
            for j in range(h):
                for i in range(w):
                    c = None
                    if part == "head":
                        if face in ("top", "back"): c = HR
                        elif face == "bottom": c = SK
                        elif face in ("right", "left"): c = HR if j < 3 else SK
                        else:
                            if j < 2 or (j < 4 and i in (0, 7)): c = HR
                            elif j == 4 and i in (1, 6): c = WH
                            elif j == 4 and i in (2, 5): c = IR
                            elif j == 5 and i in (3, 4): c = NO
                            elif j == 6 and i in (3, 4): c = MO
                            else: c = SK
                    elif part == "body": c = SH
                    elif part.endswith("arm"):
                        if face == "top": c = SH
                        elif face == "bottom": c = SK
                        else: c = SH if j < 10 else SK
                    elif part.endswith("leg"):
                        if face == "top": c = PA
                        elif face == "bottom": c = SN
                        else: c = PA if j < 9 else SN
                    if c: img.setPixelColor(x + i, y + j, c)
        # Detalle adicional solo para el preset Wraith: gafas ámbar con montura dorada
        if skin_type == "wraith":
            hx, hy = next((x, y) for p, f, x, y, w, h, o in FACE_RECTS
                          if p == "head" and f == "front" and not o)
            gf = QColor(217, 185, 74)           # montura
            lens = QColor(226, 182, 96)          # cristal
            for i in (1, 2, 5, 6):
                img.setPixelColor(hx + i, hy + 3, gf)
                img.setPixelColor(hx + i, hy + 5, gf)
            img.setPixelColor(hx + 0, hy + 4, gf)
            img.setPixelColor(hx + 3, hy + 4, gf)
            img.setPixelColor(hx + 4, hy + 4, gf)
            img.setPixelColor(hx + 7, hy + 4, gf)
            for i in (1, 2, 5, 6):
                img.setPixelColor(hx + i, hy + 4, lens)
        if target != 64:
            img = img.scaled(target, target, Qt.AspectRatioMode.IgnoreAspectRatio,
                             Qt.TransformationMode.FastTransformation).convertToFormat(QImage.Format.Format_RGBA8888)
        self.skin.image = img
        self.apply_layout(body_type=body_type, size=target, fit=False)
        if record:
            self.mark_dirty()

    # modelo y resolución
    def sync_model_controls(self):
        for k, b in self.body_buttons.items():
            b.setChecked(k == self.body_type)
        self.res_combo.blockSignals(True)
        self.res_combo.setCurrentIndex(RESOLUTIONS.index(SIZE))
        self.res_combo.blockSignals(False)

    def apply_layout(self, body_type=None, size=None, fit=True):
        """Reconstruye el layout para un tipo de cuerpo y/o resolución, sin tocar los píxeles."""
        if body_type:
            self.body_type = body_type
        build_layout(self.body_type, size or SIZE)
        self.viewer.set_slim(self.body_type == "alex")
        self.sync_model_controls()
        if fit:
            self.canvas.fit_to_view()
        self.canvas.update()
        self.viewer.update()

    def sync_size_from_image(self):
        """Tras deshacer/rehacer: si la imagen restaurada tiene otra resolución, ajusta el layout."""
        w = self.skin.image.width()
        if w != SIZE and w in RESOLUTIONS:
            self.apply_layout(size=w)

    def set_body_type(self, body_type):
        if body_type != self.body_type:
            self.apply_layout(body_type=body_type, fit=False)
            if self.dirty:
                self.autosave_timer.start()   # que el respaldo guarde también el nuevo tipo de cuerpo
        else:
            self.sync_model_controls()

    def on_resolution_changed(self, index):
        self.change_resolution(self.res_combo.itemData(index))

    def change_resolution(self, size):
        if size == SIZE:
            return
        if size < SIZE:
            ans = QMessageBox.question(
                self, T("res_shrink_title"), T("res_shrink_msg", size=size),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ans != QMessageBox.StandardButton.Yes:
                self.sync_model_controls()
                return
        self.push_undo(self.skin.image.copy())
        scaled = self.skin.image.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
                                        Qt.TransformationMode.FastTransformation)
        self.skin.image = scaled.convertToFormat(QImage.Format.Format_RGBA8888)
        self.apply_layout(size=size)
        self.mark_dirty()

    # recuperar trabajo
    def _recovery_paths(self):
        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not base:
            base = os.path.join(os.path.expanduser("~"), ".tessy_skin_editor")
        d = os.path.join(base, "TeEditor", "recovery")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "recovery.png"), os.path.join(d, "recovery.json")

    def clear_recovery(self):
        try:
            for f in self._recovery_paths():
                if os.path.exists(f):
                    os.remove(f)
        except OSError:
            pass

    def _update_title(self):
        self.setWindowTitle(self.base_title + (" •" if self.dirty else ""))

    def set_clean(self):
        """La skin actual coincide con un archivo en disco: ya no hay nada que recuperar."""
        self._clean_image = self.skin.image.copy()
        self.dirty = False
        self.autosave_timer.stop()
        self.clear_recovery()
        self._update_title()

    def mark_dirty(self):
        """Llamar tras cualquier cambio en la skin: programa un autoguardado en segundo plano."""
        self.dirty = self.skin.image != self._clean_image
        if self.dirty:
            self.autosave_timer.start()      # reinicia el temporizador (agrupa trazos seguidos)
        else:
            self.autosave_timer.stop()
            self.clear_recovery()
        self._update_title()

    def write_recovery(self):
        if not self.dirty:
            self.clear_recovery()
            return
        try:
            png, meta = self._recovery_paths()
            tmp_png, tmp_meta = png + ".tmp", meta + ".tmp"
            if not self.skin.image.save(tmp_png, "PNG"):
                return
            data = {
                "version": 1,
                "slim": bool(self.viewer.slim),
                "color": self.color.name(),
                "alpha": self.alpha_slider.value(),
                "tool": self.tool,
                "mirror": self.mirror_check.isChecked(),
                "brush": self.brush_combo.currentData(),
                "brush_size": self.brush_size.value(),
                "brush_strength": self.brush_strength.value(),
                "variation": self.var_slider.value(),
            }
            with open(tmp_meta, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            os.replace(tmp_png, png)         # reemplazo atómico: nunca queda un archivo a medias
            os.replace(tmp_meta, meta)
        except OSError:
            pass

    def offer_recovery(self):
        try:
            png, meta = self._recovery_paths()
            if not (os.path.exists(png) and os.path.exists(meta)):
                return
            img = QImage(png)
            with open(meta, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if int(data.get("version", 1)) > 1:
                raise ValueError("recovery de una versión más nueva")
            if img.isNull() or img.width() != img.height() or img.width() not in RESOLUTIONS:
                raise ValueError("recovery inválido")
        except (OSError, ValueError):
            self.clear_recovery()
            return

        ans = QMessageBox.question(
            self, T("recover_title"), T("recover_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        if ans != QMessageBox.StandardButton.Yes:
            self.clear_recovery()
            return

        slim = bool(data.get("slim", False))
        self.skin.image = img.convertToFormat(QImage.Format.Format_RGBA8888)
        self.apply_layout(body_type="alex" if slim else "steve", size=img.width())
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_history_actions()

        c = QColor(str(data.get("color", "")))
        if c.isValid():
            self.set_color(c)
        self.alpha_slider.setValue(int(data.get("alpha", 255)))
        self.mirror_check.setChecked(bool(data.get("mirror", False)))
        tool = data.get("tool")
        if tool in self.tool_buttons:
            self.set_tool(tool)
        brush = data.get("brush")
        if brush:
            i = self.brush_combo.findData(brush)
            if i >= 0:
                self.brush_combo.setCurrentIndex(i)
        self.brush_size.setValue(int(data.get("brush_size", 1)))
        self.brush_strength.setValue(int(data.get("brush_strength", 100)))
        self.var_slider.setValue(int(data.get("variation", 0)))

        self.dirty = True                    # sigue sin guardar: se conserva la recuperación
        self.canvas.update()
        self.viewer.update()
        self.statusBar().showMessage(T("recovered"), 4000)

    def closeEvent(self, e):
        self.autosave_timer.stop()
        self.write_recovery()                # si hay cambios sin guardar, quedan para la próxima vez
        e.accept()

    # archivos
    def _last_dir(self, key):
        return str(self.settings.value("last_dir_" + key, ""))

    def _set_last_dir(self, key, path):
        if path:
            self.settings.setValue("last_dir_" + key, os.path.dirname(path))

    def save_file(self):
        default = os.path.join(self._last_dir("skin") or "", "skin.png")
        path, _ = QFileDialog.getSaveFileName(self, T("dlg_save"), default, T("png_filter"))
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            if self.skin.image.save(path, "PNG"):
                self._set_last_dir("skin", path)
                self.set_clean()
                self.statusBar().showMessage(T("saved", path=path), 4000)
            else:
                QMessageBox.critical(self, T("error"), T("save_failed"))

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, T("dlg_open"), self._last_dir("skin"), T("png_filter"))
        if not path:
            return
        converted = normalize_skin(QImage(path))
        if converted is None:
            QMessageBox.warning(self, T("invalid_size_title"), T("invalid_size_msg"))
            return
        self.push_undo(self.skin.image.copy())
        self.skin.image = converted
        self.apply_layout(size=converted.width())
        self._set_last_dir("skin", path)
        self.set_clean()   # el archivo abierto ya existe en disco

    def copy_image_to_clipboard(self):
        QApplication.clipboard().setImage(self.skin.image)
        self.statusBar().showMessage(T("copied"), 2000)

    def show_about(self, *_):
        QMessageBox.about(self, T("about_title"), T("about_text", version=APP_VERSION))

    def import_url(self):
        url, ok = QInputDialog.getText(self, T("import_url"), T("import_url_prompt"))
        if ok and url.strip():
            self.statusBar().showMessage(T("mojang_searching"))
            self._url_worker = UrlDownloadWorker(url.strip())
            self._url_worker.finished.connect(self.on_mojang_success)
            self._url_worker.error.connect(self.on_url_error)
            self._url_worker.start()

    def on_url_error(self, err):
        QMessageBox.critical(self, T("error"), T("url_failed", err=err))
        self.statusBar().showMessage(T("mojang_err_status"), 3000)

    def import_mojang(self):
        username, ok = QInputDialog.getText(self, T("mojang_title"), T("mojang_prompt"))
        if ok and username:
            self.statusBar().showMessage(T("mojang_searching"))
            self.worker = MojangWorker(username)
            self.worker.finished.connect(self.on_mojang_success)
            self.worker.error.connect(self.on_mojang_error)
            self.worker.start()

    def on_mojang_success(self, img):
        converted = normalize_skin(img)
        if converted is None:
            QMessageBox.warning(self, T("invalid_size_title"), T("invalid_size_msg"))
            return
        self.push_undo(self.skin.image.copy())
        self.skin.image = converted
        self.apply_layout(size=converted.width())
        self.mark_dirty()
        self.statusBar().showMessage(T("mojang_ok"), 3000)

    def on_mojang_error(self, err):
        QMessageBox.critical(self, T("error"), T("mojang_err", err=err))
        self.statusBar().showMessage(T("mojang_err_status"), 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = SkinEditor()
    window.show()
    QTimer.singleShot(0, window.offer_recovery)
    sys.exit(app.exec())
