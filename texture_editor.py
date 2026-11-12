"""Tessy's Texture Editor
Editor de texturas para texturas de bloques y texturas libres.
Uso: python texture_editor.py
"""
import sys
import os
import re
import math
import json
import random
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


APP_VERSION = "0.0.1"

# --- i18n ---
LANG = "es"
I18N = {
    "es": {
        "undo": "↩ Deshacer", "redo": "↪ Rehacer",
        "grid": "⊞ Cuadrícula", "guides": "▦ Guías", "language": "Idioma",
        "zoom_lbl": "Zoom:", "fit": "⤢ Ajustar",
        "zoom_in_tip": "Acercar (Ctrl++)", "zoom_out_tip": "Alejar (Ctrl+-)",
        "fit_tip": "Ajustar a la ventana (Ctrl+0)",
        "mode_group": "Modo de edición",
        "mode_block": "Bloque", "mode_free": "Libre",
        "tools_group": "Herramientas",
        "tool_select": "➤ Seleccionar", "tool_pencil": "✎ Lápiz", "tool_eraser": "⌫ Borrador",
        "tool_bucket": "▣ Cubeta", "tool_picker": "⌖ Gotero", "tool_replace": "↹ Reemplazar",
        "tool_line": "／ Línea", "tool_rect": "▭ Rectángulo",
        "symmetry": "Simetría:",
        "sym_none": "Ninguna", "sym_h": "Horizontal ↔", "sym_v": "Vertical ↕", "sym_both": "Ambas ✛",
        "color_group": "Color y Opacidad", "alpha": "Alfa (Opacidad)",
        "variation": "Variación de tono (ruido)",
        "variation_tip": "Cada píxel pintado cambia un poco de brillo. 0 = color plano.",
        "pick_color": "Seleccionar Color",
        "template_group": "Plantilla de bloque",
        "template_lbl": "Plantilla:", "tile_size_lbl": "Resolución por cara:",
        "atlas_info": "Lienzo: {w}×{h} px · {n} cara(s)",
        "tpl_single": "Bloque simple (1 textura)",
        "tpl_column": "Columna / tronco (extremo + lateral)",
        "tpl_tsb": "Superior · Lateral · Inferior",
        "tpl_furnace": "Horno (superior · frontal · lateral)",
        "tpl_strip6": "Tira de 6 caras",
        "tpl_cross": "Cruz desplegada (6 caras)",
        "tpl_atlas2": "Atlas libre 2×2",
        "tpl_atlas4": "Atlas libre 4×4",
        "zones_group": "Caras activas (desmarcar = bloquear)",
        "tile_all": "Todas las caras", "tile_top": "Superior", "tile_bottom": "Inferior",
        "tile_front": "Frontal", "tile_back": "Trasera", "tile_right": "Derecha",
        "tile_left": "Izquierda", "tile_side": "Lateral", "tile_end": "Extremos (arriba/abajo)",
        "tile_n": "Tile {n}", "tile_free": "Lienzo",
        "tile_locked": "Esa cara está bloqueada.",
        "tile_ops_group": "Cara activa",
        "op_flip_h": "↔ Voltear", "op_flip_v": "↕ Voltear", "op_rot": "⟳ Rotar 90°",
        "op_half": "⊞ Mitad (revisar costuras)", "op_copy_all": "⧉ Copiar a todas", "op_clear": "✕ Vaciar",
        "op_shift_tip": "Desplazar 1 px (con envoltura)",
        "op_half_tip": "Desplaza media cara en X e Y con envoltura",
        "patterns_group": "Patrones base (cara activa)",
        "pat_noise": "Ruido", "pat_bricks": "Ladrillos", "pat_planks": "Tablones", "pat_checker": "Damero",
        "guides_group": "Guías y referencia",
        "subdiv_lbl": "Subdivisión:", "subdiv_none": "Ninguna",
        "ref_load": "Cargar referencia…", "ref_show": "Mostrar referencia",
        "ref_opacity": "Opacidad de la referencia", "ref_clear": "Quitar",
        "file_group": "Archivo", "new_texture": "Nueva textura…", "open_png": "Abrir PNG", "save_png": "Guardar PNG",
        "nt_title": "Nueva textura", "nt_w": "Ancho (px):", "nt_h": "Alto (px):",
        "nt_create": "Crear", "nt_cancel": "Cancelar",
        "nt_p16": "16×16", "nt_p32": "32×32", "nt_p64": "64×64", "nt_p128": "128×128", "nt_p1632": "16×32", "nt_p3264": "32×64",
        "presets_lbl": "Presets",
        "item_preview_group": "Vista de item",
        "item_preview_tip": "Así se ve la textura como icono de inventario (slot de item de Minecraft).",
        "export_faces": "⤒ Exportar caras por separado",
        "viewer_group": "Vista previa 3D (click = elegir cara)",
        "view_block": "1 bloque", "view_floor": "Suelo 3×3",
        "reset_view": "⟲ Restablecer vista",
        "viewer_tip": "Arrastra para rotar · Rueda para zoom · Click en una cara para elegirla · Doble click: restablecer",
        "preview_group": "Mosaico 3×3 · {tile}",
        "preview_tip": "Así se repite la textura: busca costuras visibles en los bordes.",
        "hint": "Rueda: zoom · Espacio/Alt/Click central: mover · Botón derecho: borrar",
        "free": "Fuera de la plantilla",
        "nothing_undo": "Nada que deshacer", "nothing_redo": "Nada que rehacer",
        "undone": "Deshecho", "redone": "Rehecho",
        "dlg_open": "Abrir Textura", "dlg_save": "Guardar Textura", "dlg_ref": "Imagen de referencia",
        "png_filter": "Archivos PNG (*.png)", "img_filter": "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)",
        "invalid_size_title": "Tamaño no válido",
        "invalid_size_msg": "La imagen no coincide con ninguna plantilla.\nUsa caras cuadradas de 8, 16, 32, 64 o 128 px.\nO cambia a modo Libre para aceptar cualquier tamaño.",
        "saved": "Guardado: {path}", "save_failed": "No se pudo guardar el archivo",
        "opened_as": "Abierto como «{tpl}» ({size} px por cara)",
        "opened_free": "Imagen abierta: {w}×{h} px",
        "export_title": "Exportar caras", "export_prompt": "Nombre base de los archivos:",
        "export_overwrite_title": "Archivos existentes",
        "export_overwrite_msg": "Algunos archivos ya existen en esa carpeta.\n¿Sobrescribirlos?",
        "exported": "Exportadas {n} textura(s) en {dir}",
        "error": "Error",
        "recover_title": "Recuperar trabajo",
        "recover_msg": "Se encontró una textura sin guardar de tu última sesión.\n¿Quieres recuperarla?",
        "recovered": "Trabajo recuperado",
        "res_shrink_title": "Reducir resolución",
        "res_shrink_msg": "Pasar a {size}×{size} por cara reduce el detalle.\n(Puedes deshacerlo con Ctrl+Z.)\n¿Continuar?",
        "export_anim": "⤒ Exportar textura animada (.mcmeta)",
        "anim_frametime": "Frametime (ticks por frame):",
        "anim_saved": "Textura animada exportada: {path}",
        "anim_not_strip": "La textura debe ser una tira vertical (altura = múltiplo del ancho).",
        "copy_image": "📋 Copiar imagen",
        "copied": "Imagen copiada al portapapeles",
        "recent_colors": "Recientes",
        "save_palette": "Guardar paleta…",
        "load_palette": "Cargar paleta…",
        "palette_filter": "Paleta (*.pal *.txt)",
        "palette_saved": "Paleta guardada: {path}",
        "palette_loaded": "Paleta cargada ({n} colores)",
        "about_btn": "❓ Acerca de",
        "new_item": "Nuevo item…",
        "new_item_title": "Nuevo item",
        "new_item_name": "Nombre del item (ej: mi_espada):",
        "new_item_size": "Tamaño:",
        "item_pending": "Nombre de la próxima imagen: {name}.png",
        "about_title": "Acerca de Tessy's Texture Editor",
        "about_text": "Tessy's Texture Editor v{version}\nEditor de texturas pensado para fans de Minecraft (bloques y texturas libres).\nHerramienta hecha por fans; NO es un producto oficial de Mojang.\n\n\"Minecraft\" es una marca de Mojang Synergies AB / Microsoft. Este programa NO está afiliado a ni respaldado por Mojang o Microsoft.\n\nAtajos:\n  V/P/E/G/I/C/L/R  Herramientas (Seleccionar, Lápiz, Borrador, Cubeta, Gotero, Reemplazar, Línea, Rectángulo)\n  Ctrl+S  Guardar · Ctrl+O  Abrir · Ctrl+0  Ajustar a la ventana\n  Ctrl+Z  Deshacer · Ctrl+Y / Ctrl+Shift+Z  Rehacer · Ctrl+G  Cuadrícula\n  Ctrl+Shift+C  Copiar imagen al portapapeles\n\nHecho con PyQt6 · Recuperación automática ante cierres inesperados.\nHerramienta de fans · no oficial (Mojang Usage Guidelines).",
    },
    "en": {
        "undo": "↩ Undo", "redo": "↪ Redo",
        "grid": "⊞ Grid", "guides": "▦ Guides", "language": "Language",
        "zoom_lbl": "Zoom:", "fit": "⤢ Fit",
        "zoom_in_tip": "Zoom in (Ctrl++)", "zoom_out_tip": "Zoom out (Ctrl+-)",
        "fit_tip": "Fit to window (Ctrl+0)",
        "mode_group": "Edit mode",
        "mode_block": "Block", "mode_free": "Free",
        "tools_group": "Tools",
        "tool_select": "➤ Select", "tool_pencil": "✎ Pencil", "tool_eraser": "⌫ Eraser",
        "tool_bucket": "▣ Fill", "tool_picker": "⌖ Picker", "tool_replace": "↹ Replace",
        "tool_line": "／ Line", "tool_rect": "▭ Rectangle",
        "symmetry": "Symmetry:",
        "sym_none": "None", "sym_h": "Horizontal ↔", "sym_v": "Vertical ↕", "sym_both": "Both ✛",
        "color_group": "Color & Opacity", "alpha": "Alpha (Opacity)",
        "variation": "Tone variation (noise)",
        "variation_tip": "Each painted pixel gets a slightly different brightness. 0 = flat color.",
        "pick_color": "Select Color",
        "template_group": "Block template",
        "template_lbl": "Template:", "tile_size_lbl": "Resolution per face:",
        "atlas_info": "Canvas: {w}×{h} px · {n} face(s)",
        "tpl_single": "Single block (1 texture)",
        "tpl_column": "Column / log (end + side)",
        "tpl_tsb": "Top · Side · Bottom",
        "tpl_furnace": "Furnace (top · front · side)",
        "tpl_strip6": "6-face strip",
        "tpl_cross": "Unfolded cross (6 faces)",
        "tpl_atlas2": "Free atlas 2×2",
        "tpl_atlas4": "Free atlas 4×4",
        "zones_group": "Active faces (uncheck = lock)",
        "tile_all": "All faces", "tile_top": "Top", "tile_bottom": "Bottom",
        "tile_front": "Front", "tile_back": "Back", "tile_right": "Right",
        "tile_left": "Left", "tile_side": "Side", "tile_end": "Ends (top/bottom)",
        "tile_n": "Tile {n}", "tile_free": "Canvas",
        "tile_locked": "That face is locked.",
        "tile_ops_group": "Active face",
        "op_flip_h": "↔ Flip", "op_flip_v": "↕ Flip", "op_rot": "⟳ Rotate 90°",
        "op_half": "⊞ Half (check seams)", "op_copy_all": "⧉ Copy to all", "op_clear": "✕ Clear",
        "op_shift_tip": "Shift 1 px (wraps around)",
        "op_half_tip": "Shifts half a face in X and Y with wrap-around",
        "patterns_group": "Base patterns (active face)",
        "pat_noise": "Noise", "pat_bricks": "Bricks", "pat_planks": "Planks", "pat_checker": "Checker",
        "guides_group": "Guides & reference",
        "subdiv_lbl": "Subdivision:", "subdiv_none": "None",
        "ref_load": "Load reference…", "ref_show": "Show reference",
        "ref_opacity": "Reference opacity", "ref_clear": "Remove",
        "file_group": "File", "new_texture": "New texture…", "open_png": "Open PNG", "save_png": "Save PNG",
        "nt_title": "New texture", "nt_w": "Width (px):", "nt_h": "Height (px):",
        "nt_create": "Create", "nt_cancel": "Cancel",
        "nt_p16": "16×16", "nt_p32": "32×32", "nt_p64": "64×64", "nt_p128": "128×128", "nt_p1632": "16×32", "nt_p3264": "32×64",
        "presets_lbl": "Presets",
        "item_preview_group": "Item preview",
        "item_preview_tip": "See the texture as an inventory item icon (Minecraft item slot).",
        "export_faces": "⤒ Export faces separately",
        "viewer_group": "3D Preview (click = pick face)",
        "view_block": "1 block", "view_floor": "3×3 floor",
        "reset_view": "⟲ Reset view",
        "viewer_tip": "Drag to rotate · Wheel to zoom · Click a face to pick it · Double-click: reset view",
        "preview_group": "3×3 tiling · {tile}",
        "preview_tip": "This is how the texture repeats. Look for visible seams on the edges.",
        "hint": "Wheel: zoom · Space/Alt/Middle-click: pan · Right-click: erase",
        "free": "Outside the template",
        "nothing_undo": "Nothing to undo", "nothing_redo": "Nothing to redo",
        "undone": "Undone", "redone": "Redone",
        "dlg_open": "Open Texture", "dlg_save": "Save Texture", "dlg_ref": "Reference image",
        "png_filter": "PNG Files (*.png)", "img_filter": "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
        "invalid_size_title": "Invalid size",
        "invalid_size_msg": "The image doesn't match any template.\nUse square faces of 8, 16, 32, 64 or 128 px.\nOr switch to Free mode to accept any size.",
        "saved": "Saved: {path}", "save_failed": "Could not save the file",
        "opened_as": "Opened as “{tpl}” ({size} px per face)",
        "opened_free": "Image opened: {w}×{h} px",
        "export_title": "Export faces", "export_prompt": "Base name for the files:",
        "export_overwrite_title": "Existing files",
        "export_overwrite_msg": "Some files already exist in that folder.\nOverwrite them?",
        "exported": "Exported {n} texture(s) to {dir}",
        "error": "Error",
        "recover_title": "Recover work",
        "recover_msg": "An unsaved texture from your last session was found.\nDo you want to recover it?",
        "recovered": "Work recovered",
        "res_shrink_title": "Lower resolution",
        "res_shrink_msg": "Switching to {size}×{size} per face reduces detail.\nContinue?",
        "export_anim": "⤒ Export animated texture (.mcmeta)",
        "anim_frametime": "Frametime (ticks per frame):",
        "anim_saved": "Animated texture exported: {path}",
        "anim_not_strip": "The texture must be a vertical strip (height = multiple of width).",
        "copy_image": "📋 Copy image",
        "copied": "Image copied to clipboard",
        "recent_colors": "Recent",
        "save_palette": "Save palette…",
        "load_palette": "Load palette…",
        "palette_filter": "Palette (*.pal *.txt)",
        "palette_saved": "Palette saved: {path}",
        "palette_loaded": "Palette loaded ({n} colors)",
        "about_btn": "❓ About",
        "new_item": "New item…",
        "new_item_title": "New item",
        "new_item_name": "Item name (e.g. my_sword):",
        "new_item_size": "Size:",
        "item_pending": "Next save will use: {name}.png",
        "about_title": "About Tessy's Texture Editor",
        "about_text": "Tessy's Texture Editor v{version}\nTexture editor built for Minecraft fans (block and freeform textures).\nFan-made tool; NOT an official Mojang product.\n\n\"Minecraft\" is a trademark of Mojang Synergies AB / Microsoft. This program is NOT affiliated with or endorsed by Mojang or Microsoft.\n\nShortcuts:\n  V/P/E/G/I/C/L/R  Tools (Select, Pencil, Eraser, Fill, Picker, Replace, Line, Rectangle)\n  Ctrl+S  Save · Ctrl+O  Open · Ctrl+0  Fit to window\n  Ctrl+Z  Undo · Ctrl+Y / Ctrl+Shift+Z  Redo · Ctrl+G  Grid\n  Ctrl+Shift+C  Copy image to clipboard\n\nMade with PyQt6 · Automatic crash recovery.\nFan tool · not official (Mojang Usage Guidelines).",
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


# --- plantillas ---
FACE_NAMES = ("top", "bottom", "front", "back", "right", "left")
TILE_SIZES = (8, 16, 32, 64, 128)
DEFAULT_TILE = 16

def _faces(top, bottom, front, back, right, left):
    return {"top": top, "bottom": bottom, "front": front, "back": back, "right": right, "left": left}

def _atlas(n):
    return [(f"t{i}", i % n, i // n) for i in range(n * n)]

TEMPLATES = {
    "single": {"cols": 1, "rows": 1, "tiles": [("all", 0, 0)], "faces": _faces(*["all"]*6)},
    "column": {"cols": 2, "rows": 1, "tiles": [("end", 0, 0), ("side", 1, 0)],
               "faces": _faces("end", "end", "side", "side", "side", "side")},
    "tsb": {"cols": 3, "rows": 1, "tiles": [("top", 0, 0), ("side", 1, 0), ("bottom", 2, 0)],
            "faces": _faces("top", "bottom", "side", "side", "side", "side")},
    "furnace": {"cols": 3, "rows": 1, "tiles": [("top", 0, 0), ("front", 1, 0), ("side", 2, 0)],
                "faces": _faces("top", "top", "front", "side", "side", "side")},
    "strip6": {"cols": 6, "rows": 1, "tiles": [(f, i, 0) for i, f in enumerate(FACE_NAMES)],
               "faces": _faces(*FACE_NAMES)},
    "cross": {"cols": 4, "rows": 3,
              "tiles": [("top", 1, 0), ("left", 0, 1), ("front", 1, 1), ("right", 2, 1),
                        ("back", 3, 1), ("bottom", 1, 2)],
              "faces": _faces(*FACE_NAMES)},
    "atlas2": {"cols": 2, "rows": 2, "tiles": _atlas(2), "faces": None},
    "atlas4": {"cols": 4, "rows": 4, "tiles": _atlas(4), "faces": None},
}
TEMPLATE_ORDER = list(TEMPLATES)

TILE_TINT = {
    "all": QColor(214, 214, 224), "top": QColor(191, 227, 255), "bottom": QColor(201, 201, 214),
    "right": QColor(217, 198, 240), "front": QColor(191, 238, 192), "left": QColor(240, 198, 230),
    "back": QColor(255, 217, 168), "side": QColor(200, 232, 190), "end": QColor(186, 214, 240),
}
ATLAS_TINTS = [QColor(191, 227, 255), QColor(191, 238, 192), QColor(255, 217, 168), QColor(240, 198, 230)]

def tile_tint(key):
    if key.startswith("t") and key[1:].isdigit():
        return ATLAS_TINTS[int(key[1:]) % len(ATLAS_TINTS)]
    return TILE_TINT.get(key, QColor(214, 214, 224))

def tile_label(key):
    if key.startswith("t") and key[1:].isdigit():
        return T("tile_n", n=int(key[1:]) + 1)
    return T("tile_" + key)

FALLBACK = {
    "all": ("side", "front", "top", "end"),
    "top": ("end", "all", "side"), "bottom": ("top", "end", "all", "side"),
    "end": ("top", "bottom", "all", "side"),
    "side": ("front", "right", "left", "back", "all"),
    "front": ("side", "all"), "back": ("side", "front", "all"),
    "right": ("side", "front", "all"), "left": ("side", "front", "all"),
}

_layout_counter = 0
def _next_layout_uid():
    global _layout_counter
    _layout_counter += 1
    return _layout_counter


class TexLayout:
    def __init__(self, key, tile):
        self.uid = _next_layout_uid()
        self.key, self.tile = key, int(tile)
        tpl = TEMPLATES[key]
        self.cols, self.rows = tpl["cols"], tpl["rows"]
        self.faces = tpl["faces"]
        self.order = [t[0] for t in tpl["tiles"]]
        self.pos = {k: (c, r) for k, c, r in tpl["tiles"]}
        self.cell = {(c, r): k for k, c, r in tpl["tiles"]}
        self.w, self.h = self.cols * self.tile, self.rows * self.tile

    def rect(self, key):
        c, r = self.pos[key]
        return QRect(c * self.tile, r * self.tile, self.tile, self.tile)

    def key_at(self, x, y):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return None
        return self.cell.get((x // self.tile, y // self.tile))

    def face_tile(self, face, active):
        return self.faces[face] if self.faces else active


class FreeLayout:
    def __init__(self, w, h):
        self.uid = _next_layout_uid()
        self.key = "free"
        self.tile = 0
        self.cols, self.rows = 1, 1
        self.faces = None
        self.order = ["all"]
        self.pos = {"all": (0, 0)}
        self.cell = {(0, 0): "all"}
        self.w, self.h = max(1, int(w)), max(1, int(h))

    def rect(self, key):
        return QRect(0, 0, self.w, self.h)

    def key_at(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return "all"
        return None

    def face_tile(self, face, active):
        return "all"


# --- caras 3D ---
FACE_NORMALS = {
    "front": (0, 0, 1), "back": (0, 0, -1), "right": (1, 0, 0),
    "left": (-1, 0, 0), "top": (0, 1, 0), "bottom": (0, -1, 0),
}

FACE_SHADE = {
    "bottom": QColor(0, 0, 0, 110), "front": QColor(0, 0, 0, 40), "back": QColor(0, 0, 0, 40),
    "right": QColor(0, 0, 0, 80), "left": QColor(0, 0, 0, 80),
}


def new_image(layout):
    img = QImage(layout.w, layout.h, QImage.Format.Format_RGBA8888)
    img.fill(Qt.GlobalColor.transparent)
    return img

def convert_image(old_img, old, new):
    out = new_image(new)
    pt = QPainter(out)
    for k in new.order:
        src = None
        for cand in (k,) + FALLBACK.get(k, ()):
            if cand in old.pos:
                src = cand
                break
        if src is None:
            src = old.order[0]
        pt.drawImage(new.rect(k), old_img, old.rect(src))
    pt.end()
    return out

def guess_layout(w, h, current_key):
    for k in [current_key] + [t for t in TEMPLATE_ORDER if t != current_key]:
        t = TEMPLATES[k]
        if w % t["cols"] == 0 and h % t["rows"] == 0:
            ts = w // t["cols"]
            if ts == h // t["rows"] and ts in TILE_SIZES:
                return k, ts
    return None


def extract_texture(image, rect):
    w = max(1, rect.width())
    h = max(1, rect.height())
    out = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    out.fill(Qt.GlobalColor.transparent)
    src = rect.intersected(image.rect())
    if src.isValid() and src.width() > 0 and src.height() > 0:
        p = QPainter(out)
        p.drawImage(src.left() - rect.left(), src.top() - rect.top(),
                    image, src.left(), src.top(), src.width(), src.height())
        p.end()
    return out


# --- lienzo 2D ---
class Canvas2D(QWidget):
    MIN_ZOOM, MAX_ZOOM = 1, 64

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.zoom = 10
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.fit_mode = True
        self.last_pos = None
        self.drawing = False
        self.panning = False
        self.space_down = False
        self.show_grid = True
        self.show_layout = True
        self.subdiv = 1
        self.ref_image = None
        self.ref_visible = True
        self.ref_opacity = 0.5
        self.hover = None
        self._cache = None
        self._bg_cache = None
        self.start_pos = None
        self.preview_pixels = []

        self.setMouseTracking(True)
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def _notify_zoom(self):
        self.main.on_canvas_zoom_changed(self.zoom)

    def max_zoom(self):
        L = self.main.lay
        return max(self.MIN_ZOOM, min(self.MAX_ZOOM, 16000 // max(L.w, L.h)))

    def fit_to_view(self):
        L = self.main.lay
        margin = 12
        availw, availh = self.width() - 2 * margin, self.height() - 2 * margin
        self.zoom = max(self.MIN_ZOOM, min(self.max_zoom(), int(min(availw // L.w, availh // L.h))))
        self.fit_mode = True
        self.offset_x = (self.width() - L.w * self.zoom) / 2
        self.offset_y = (self.height() - L.h * self.zoom) / 2
        self._notify_zoom()
        self.update()

    def clamp_offsets(self):
        L = self.main.lay
        lo, hi = sorted((self.width() - L.w * self.zoom, 0))
        self.offset_x = max(lo, min(hi, self.offset_x))
        lo, hi = sorted((self.height() - L.h * self.zoom, 0))
        self.offset_y = max(lo, min(hi, self.offset_y))

    def set_zoom(self, new_zoom, anchor=None):
        new_zoom = max(self.MIN_ZOOM, min(self.max_zoom(), int(new_zoom)))
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

    @staticmethod
    def _checker_brush(a, b):
        px = QImage(2, 2, QImage.Format.Format_ARGB32)
        px.setPixelColor(0, 0, a)
        px.setPixelColor(1, 1, a)
        px.setPixelColor(1, 0, b)
        px.setPixelColor(0, 1, b)
        return QBrush(px)

    def _background_image(self):
        m = self.main
        L = m.lay
        if L.tile <= 0:
            key = (L.uid,)
            if self._bg_cache is not None and self._bg_cache[0] == key:
                return self._bg_cache[1]
            bg = QImage(L.w, L.h, QImage.Format.Format_ARGB32_Premultiplied)
            pt = QPainter(bg)
            pt.fillRect(bg.rect(), self._checker_brush(QColor(45, 45, 45), QColor(35, 35, 35)))
            pt.end()
            self._bg_cache = (key, bg)
            return bg
        key = (L.uid, tuple(sorted(m.locked)))
        if self._bg_cache is not None and self._bg_cache[0] == key:
            return self._bg_cache[1]
        bg = QImage(L.w, L.h, QImage.Format.Format_ARGB32_Premultiplied)
        pt = QPainter(bg)
        pt.fillRect(bg.rect(), self._checker_brush(QColor(45, 45, 45), QColor(35, 35, 35)))
        for k in L.order:
            if k in m.locked:
                brush = self._checker_brush(QColor(40, 20, 20), QColor(30, 15, 15))
            else:
                t = tile_tint(k)
                brush = self._checker_brush(t.darker(110), t)
            pt.fillRect(L.rect(k), brush)
        pt.end()
        self._bg_cache = (key, bg)
        return bg

    def get_canvas_image(self):
        m = self.main
        key = (m.image.cacheKey(), tuple(sorted(m.locked)), m.lay.uid)
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        img = self._background_image().copy()
        pt = QPainter(img)
        pt.drawImage(0, 0, m.image)
        if m.lay.tile > 0:
            for k in m.lay.order:
                if k in m.locked:
                    pt.fillRect(m.lay.rect(k), QColor(0, 0, 0, 110))
        pt.end()
        self._cache = (key, img)
        return img

    def paintEvent(self, e):
        L = self.main.lay
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        z = self.zoom
        ox, oy = int(self.offset_x), int(self.offset_y)
        W, H = L.w * z, L.h * z
        target = QRect(ox, oy, W, H)

        painter.drawImage(target, self.get_canvas_image())

        if self.ref_image is not None and self.ref_visible:
            painter.setOpacity(self.ref_opacity)
            painter.drawImage(target, self.ref_image)
            painter.setOpacity(1.0)

        if self.show_grid and z >= 4:
            painter.setPen(QColor(255, 255, 255, 20))
            for i in range(L.w + 1):
                painter.drawLine(ox + i * z, oy, ox + i * z, oy + H)
            for j in range(L.h + 1):
                painter.drawLine(ox, oy + j * z, ox + W, oy + j * z)

        if self.subdiv > 1 and L.tile > 0:
            pen = QPen(QColor(255, 255, 255, 110))
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            step = L.tile / self.subdiv
            for k in L.order:
                r = L.rect(k)
                for i in range(1, self.subdiv):
                    p = int(round(i * step))
                    painter.drawLine(ox + (r.x() + p) * z, oy + r.y() * z,
                                     ox + (r.x() + p) * z, oy + (r.y() + r.height()) * z)
                    painter.drawLine(ox + r.x() * z, oy + (r.y() + p) * z,
                                     ox + (r.x() + r.width()) * z, oy + (r.y() + p) * z)

        if self.show_layout and L.tile > 0:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor(0, 0, 0, 170))
            for k in L.order:
                r = L.rect(k)
                painter.drawRect(ox + r.x() * z, oy + r.y() * z, r.width() * z, r.height() * z)
            r = L.rect(self.main.active)
            painter.setPen(QPen(QColor("#4f8cff"), 2))
            painter.drawRect(ox + r.x() * z, oy + r.y() * z, r.width() * z, r.height() * z)
            if L.tile * z >= 56:
                f = QFont("Noto Sans", 8)
                f.setBold(True)
                painter.setFont(f)
                for k in L.order:
                    r = L.rect(k)
                    tx, ty = ox + r.x() * z + 6, oy + r.y() * z + 16
                    painter.setPen(QColor(0, 0, 0, 200))
                    painter.drawText(tx + 1, ty + 1, tile_label(k))
                    painter.setPen(QColor(255, 255, 255, 235))
                    painter.drawText(tx, ty, tile_label(k))

        painter.setPen(QColor("#3a3a3a"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(ox - 1, oy - 1, W + 1, H + 1)

        if self.preview_pixels:
            painter.setPen(QColor(255, 230, 0, 150))
            painter.setBrush(QColor(255, 230, 0, 50))
            for px, py in self.preview_pixels:
                painter.drawRect(ox + px * z, oy + py * z, z, z)

        if self.hover and not self.panning:
            hx, hy = self.hover
            painter.setPen(QColor(255, 255, 255, 220))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(ox + hx * z, oy + hy * z, z, z)

    def get_cell(self, pos):
        return int((pos.x() - self.offset_x) // self.zoom), int((pos.y() - self.offset_y) // self.zoom)

    def _inside(self, px, py):
        L = self.main.lay
        return 0 <= px < L.w and 0 <= py < L.h

    def _track_active(self, px, py):
        k = self.main.lay.key_at(px, py)
        if k:
            self.main.set_active_tile(k)

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
            if not self._inside(px, py):
                return

            self._track_active(px, py)
            if self.main.tool == "select":
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

        self.hover = (px, py) if self._inside(px, py) else None

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
        self.setFocus()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.hover = None
        self.main.update_status(-1, -1)
        self.update()
        super().leaveEvent(e)

    @staticmethod
    def shape_cells(tool, a, b):
        x0, y0 = a
        x1, y1 = b
        cells = []
        if tool == "line":
            dx, dy = abs(x1 - x0), -abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx + dy
            while True:
                cells.append((x0, y0))
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x0 += sx
                if e2 <= dx:
                    err += dx
                    y0 += sy
        else:
            for yy in range(min(y0, y1), max(y0, y1) + 1):
                for xx in range(min(x0, x1), max(x0, x1) + 1):
                    cells.append((xx, yy))
        return cells

    def update_preview_shape(self, a, b):
        self.preview_pixels = self.shape_cells(self.main.tool, a, b)
        self.update()

    def commit_shape(self, a, b, is_erase):
        for px, py in self.shape_cells(self.main.tool, a, b):
            self.main.draw_pixel(px, py, is_erase)
        self.update()

    def handle_draw(self, pos, is_erase):
        px, py = self.get_cell(pos)
        if self._inside(px, py):
            self.main.draw_pixel(px, py, is_erase)
            self.update()


def quad_transform(src, dst):
    tf = QTransform()
    try:
        res = QTransform.quadToQuad(src, dst, tf)
    except TypeError:
        res = QTransform.quadToQuad(src, dst)
    if isinstance(res, tuple):
        ok, tf = res
        return tf if ok else None
    if isinstance(res, QTransform):
        return res
    return tf if res else None


# --- visor 3D (bloque) ---
class BlockViewer(QWidget):
    DEFAULT_ROT_X, DEFAULT_ROT_Y, DEFAULT_ZOOM = 25, -35, 1.0
    HALF = 8.0
    CAM_DIST = 150.0

    FACE_VERTS = {
        "front":  [(-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1)],
        "back":   [(1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1)],
        "right":  [(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1)],
        "left":   [(-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)],
        "top":    [(-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)],
        "bottom": [(-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)],
    }
    NEIGHBOR = {"front": (0, 1), "back": (0, -1), "right": (1, 0), "left": (-1, 0)}

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.mode = "block"
        self.rot_x = self.DEFAULT_ROT_X
        self.rot_y = self.DEFAULT_ROT_Y
        self.zoom = self.DEFAULT_ZOOM
        self.last_mouse = None
        self.press_pos = None
        self.hover_face = None
        self._last_items = []
        self._cache = None
        self.setMouseTracking(True)
        self.setMinimumSize(260, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def set_mode(self, mode):
        self.mode = mode
        self.update()

    def reset_view(self):
        self.rot_x, self.rot_y, self.zoom = self.DEFAULT_ROT_X, self.DEFAULT_ROT_Y, self.DEFAULT_ZOOM
        self.hover_face = None
        self.update()

    def _hit_face(self, pos):
        for _depth, face, poly in reversed(self._last_items):
            if poly.containsPoint(pos, Qt.FillRule.OddEvenFill):
                return face
        return None

    def _select_face(self, face):
        m = self.main
        if m.lay.tile <= 0:
            return
        key = m.lay.face_tile(face, m.active)
        if key and key != m.active:
            m.set_active_tile(key)
            self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.last_mouse = e.position()
            self.press_pos = e.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, e):
        if self.last_mouse:
            dx = e.position().x() - self.last_mouse.x()
            dy = e.position().y() - self.last_mouse.y()
            self.rot_y += dx * 0.5
            self.rot_x = max(-89, min(89, self.rot_x + dy * 0.5))
            self.last_mouse = e.position()
            if self.hover_face is not None:
                self.hover_face = None
            self.update()
            return
        face = self._hit_face(e.position())
        if face != self.hover_face:
            self.hover_face = face
            pickable = face is not None and self.main.lay.tile > 0
            self.setCursor(Qt.CursorShape.PointingHandCursor if pickable else Qt.CursorShape.OpenHandCursor)
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.press_pos is not None:
            if (e.position() - self.press_pos).manhattanLength() < 5:
                face = self._hit_face(e.position())
                if face:
                    self._select_face(face)
        self.press_pos = None
        self.last_mouse = None
        pickable = self.hover_face is not None and self.main.lay.tile > 0
        self.setCursor(Qt.CursorShape.PointingHandCursor if pickable else Qt.CursorShape.OpenHandCursor)

    def leaveEvent(self, e):
        if self.hover_face is not None:
            self.hover_face = None
            self.update()
        super().leaveEvent(e)

    def mouseDoubleClickEvent(self, e):
        self.reset_view()

    def wheelEvent(self, e):
        self.zoom = max(0.4, min(3.0, self.zoom + e.angleDelta().y() * 0.002))
        self.update()

    def face_images(self):
        m = self.main
        L = m.lay
        key = (m.image.cacheKey(), L.uid, m.active if L.faces is None else None)
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        out = {}
        for face in FACE_NAMES:
            img = extract_texture(m.image, L.rect(L.face_tile(face, m.active)))
            shade = FACE_SHADE.get(face)
            if shade is not None:
                p = QPainter(img)
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
                p.fillRect(img.rect(), shade)
                p.end()
            out[face] = img
        self._cache = (key, out)
        return out

    def paintEvent(self, e):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#2a303c"))
        grad.setColorAt(1, QColor("#16181d"))
        painter.fillRect(self.rect(), grad)

        imgs = self.face_images()
        ry, rx = math.radians(self.rot_y), math.radians(self.rot_x)
        cy, sy, cx, sx = math.cos(ry), math.sin(ry), math.cos(rx), math.sin(rx)

        def rot(v):
            x, y, z = v
            x1 = x * cy + z * sy
            z1 = -x * sy + z * cy
            return x1, y * cx - z1 * sx, y * sx + z1 * cx

        if self.mode == "floor":
            offsets = [(i, k) for k in (-1, 0, 1) for i in (-1, 0, 1)]
            radius = 36.0
        else:
            offsets = [(0, 0)]
            radius = 14.0
        occupied = set(offsets)
        base = min(self.width(), self.height()) * 0.42 / radius * self.zoom
        D = self.CAM_DIST
        mx, my = self.width() / 2, self.height() / 2
        s = 2 * self.HALF

        items = []
        for (i, k) in offsets:
            for face, verts in self.FACE_VERTS.items():
                if face in self.NEIGHBOR:
                    dx, dz = self.NEIGHBOR[face]
                    if (i + dx, k + dz) in occupied:
                        continue
                pts = [rot((i * s + vx * self.HALF, vy * self.HALF, k * s + vz * self.HALF))
                       for vx, vy, vz in verts]
                n = rot(FACE_NORMALS[face])
                c = (sum(p[0] for p in pts) / 4, sum(p[1] for p in pts) / 4, sum(p[2] for p in pts) / 4)
                if n[0] * (-c[0]) + n[1] * (-c[1]) + n[2] * (D - c[2]) <= 0:
                    continue
                poly = QPolygonF([QPointF(mx + x * base * D / (D - z), my - y * base * D / (D - z))
                                  for x, y, z in pts])
                items.append((c[2], face, poly))
        items.sort(key=lambda t: t[0])
        self._last_items = items

        m = self.main
        L = m.lay
        active_face = None
        if L.tile > 0:
            for f in FACE_NAMES:
                if L.face_tile(f, m.active) == m.active:
                    active_face = f
                    break

        for _, face, poly in items:
            img = imgs[face]
            t = img.width()
            src = QPolygonF([QPointF(0, 0), QPointF(t, 0), QPointF(t, t), QPointF(0, t)])
            tf = quad_transform(src, poly)
            if tf is not None:
                painter.save()
                painter.setTransform(tf)
                painter.drawImage(0, 0, img)
                painter.restore()
            painter.setPen(QColor(0, 0, 0, 45))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolygon(poly)
            if face == active_face:
                painter.setPen(QPen(QColor("#4f8cff"), 2))
                painter.drawPolygon(poly)
            if face == self.hover_face:
                painter.setPen(QPen(QColor(255, 255, 255, 170), 1, Qt.PenStyle.DashLine))
                painter.drawPolygon(poly)


# --- rueda del mouse ---
class WheelGuard(QObject):
    """Impide que la rueda del mouse cambie el valor de combos, spinboxes y
    sliders. Un control solo reacciona a la rueda si fue clickeado (queda
    "armado"); de lo contrario la rueda desplaza el panel."""

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


# --- combo con rueda protegida ---
class GuardedComboBox(QComboBox):
    """Desplegable que solo reacciona a la rueda del mouse si fue clickeado
    (queda 'armado') o si tiene foco. Si no, la rueda desplaza el panel."""

    wheel_guard = None

    def wheelEvent(self, event):
        guard = GuardedComboBox.wheel_guard
        if guard is not None:
            if self in guard._armed:
                guard._wheel_step(self, event.angleDelta().y())
            else:
                guard._scroll_parent(self, event.angleDelta().y())
            event.accept()
            return
        super().wheelEvent(event)


# --- diálogo nuevo item ---
class NewItemDialog(QDialog):
    """Diálogo para nombrar un item nuevo y elegir su tamaño."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("new_item_title"))
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(T("new_item_name")))
        self.name_edit = QLineEdit("mi_item")
        self.name_edit.setMinimumWidth(240)
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel(T("new_item_size")))
        self.size_combo = QComboBox()
        for label, size in (("nt_p16", (16, 16)), ("nt_p1632", (16, 32)),
                            ("nt_p3264", (32, 64)), ("nt_p32", (32, 32)), ("nt_p64", (64, 64))):
            self.size_combo.addItem(T(label), size)
        layout.addWidget(self.size_combo)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(T("nt_create"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(T("nt_cancel"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def values(self):
        name = re.sub(r"[^A-Za-z0-9_\-]", "_", self.name_edit.text().strip())
        return name, *self.size_combo.currentData()


# --- diálogo nueva textura ---
class NewTextureDialog(QDialog):
    """Diálogo para crear una textura en blanco de cualquier tamaño (modo Libre)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("nt_title"))
        self.setModal(True)
        self.resize(280, 200)

        layout = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)
        w_lbl = QLabel()
        h_lbl = QLabel()
        w_lbl.setText(T("nt_w")); h_lbl.setText(T("nt_h"))
        grid.addWidget(w_lbl, 0, 0)
        grid.addWidget(h_lbl, 1, 0)
        self.w_spin = QSpinBox()
        self.w_spin.setRange(1, 512); self.w_spin.setValue(16)
        grid.addWidget(self.w_spin, 0, 1)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(1, 512); self.h_spin.setValue(16)
        grid.addWidget(self.h_spin, 1, 1)
        layout.addLayout(grid)

        presets_label = QLabel(T("presets_lbl"))
        layout.addWidget(presets_label)
        row = QHBoxLayout()
        presets = [("nt_p16", 16, 16), ("nt_p32", 32, 32), ("nt_p64", 64, 64),
                   ("nt_p128", 128, 128), ("nt_p1632", 16, 32), ("nt_p3264", 32, 64)]
        for key, a, c in presets:
            b = QPushButton(T(key))
            b.setFixedHeight(26)
            b.clicked.connect(lambda checked=False, w=a, h=c: self._set(w, h))
            row.addWidget(b)
        layout.addLayout(row)
        layout.addStretch()

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_btn = btns.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = btns.button(QDialogButtonBox.StandardButton.Cancel)
        ok_btn.setText(T("nt_create"))
        cancel_btn.setText(T("nt_cancel"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _set(self, w, h):
        self.w_spin.setValue(w)
        self.h_spin.setValue(h)

    def values(self):
        return self.w_spin.value(), self.h_spin.value()


# --- preview de item ---
class ItemSlotPreview(QWidget):
    """La textura como se vería dentro de un cuadradito de inventario de Minecraft."""

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setMinimumHeight(90)
        self.setMaximumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#252527"))
        side = min(self.width(), self.height()) - 8
        if side <= 0:
            return
        x0, y0 = (self.width() - side) // 2, (self.height() - side) // 2
        slot = QRect(x0, y0, side, side)
        p.fillRect(slot, QColor(139, 139, 139))
        p.setPen(QColor(0, 0, 0, 130))
        p.drawRect(slot.adjusted(0, 0, -1, -1))
        inner = slot.adjusted(2, 2, -3, -3)
        p.setPen(QColor(255, 255, 255, 100))
        p.drawLine(inner.topLeft(), inner.topRight())
        p.drawLine(inner.topLeft(), inner.bottomLeft())
        p.setPen(QColor(0, 0, 0, 100))
        p.drawLine(inner.bottomLeft(), inner.bottomRight())
        p.drawLine(inner.topRight(), inner.bottomRight())
        margin = max(4, side // 6)
        target = slot.adjusted(margin, margin, -margin, -margin)
        img = self.main.image
        if not img.isNull():
            sw, sh = img.width(), img.height()
            longest = max(sw, sh)
            tw = max(1, round(sw / longest * target.width()))
            th = max(1, round(sh / longest * target.height()))
            dx = target.x() + (target.width() - tw) // 2
            dy = target.y() + (target.height() - th) // 2
            p.drawImage(QRect(dx, dy, tw, th), img)


# --- mosaico 3×3 ---
class TilePreview(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, e):
        m = self.main
        L = m.lay
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        p.fillRect(self.rect(), QColor("#111111"))
        side = min(self.width(), self.height()) - 8
        if side <= 0:
            return
        if L.tile > 0:
            tile = extract_texture(m.image, L.rect(m.active))
            cell = max(1, side // 3)
            if cell >= L.tile:
                cell = (cell // L.tile) * L.tile
            total = cell * 3
            x0, y0 = (self.width() - total) // 2, (self.height() - total) // 2
            for j in range(3):
                for i in range(3):
                    p.drawImage(QRect(x0 + i * cell, y0 + j * cell, cell, cell), tile)
            return
        # Modo Libre: repetir el lienzo completo conservando la relación de aspecto,
        # sin huecos, para poder detectar costuras en los bordes.
        src = m.image
        sw, sh = src.width(), src.height()
        longest = max(sw, sh)
        if longest <= 0:
            return
        unit = side / 3.0 / longest
        dw, dh = max(1, round(sw * unit)), max(1, round(sh * unit))
        total_w, total_h = dw * 3, dh * 3
        x0, y0 = (self.width() - total_w) // 2, (self.height() - total_h) // 2
        for j in range(3):
            for i in range(3):
                p.drawImage(QRect(x0 + i * dw, y0 + j * dh, dw, dh), src)


# --- color ---
def _clamp(v):
    return max(0, min(255, int(v)))

def scale_color(c, f):
    return QColor(_clamp(c.red() * f), _clamp(c.green() * f), _clamp(c.blue() * f), c.alpha())

def vary_color(c, amount):
    if amount <= 0:
        return QColor(c)
    return scale_color(c, 1 + random.uniform(-amount, amount) / 100.0)


# --- ventana principal ---
TOOL_ORDER = ["select", "pencil", "eraser", "bucket", "picker", "replace", "line", "rect"]
TOOL_KEYS = {"select": "V", "pencil": "P", "eraser": "E", "bucket": "G",
             "picker": "I", "replace": "C", "line": "L", "rect": "R"}
class TextureEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("TeEditorS", "TeTextureEditor")
        self.setWindowIcon(QIcon(resource_path("texture_icon.ico")))
        saved = str(self.settings.value("lang", ""))
        set_language(saved if saved in I18N else system_language())

        self.setWindowTitle("Tessy's Texture Editor")
        self.setMinimumSize(1150, 700)
        geo = QApplication.primaryScreen().availableGeometry()
        self.resize(min(1500, geo.width() - 40), min(900, geo.height() - 60))

        self.mode = "block"
        self.lay = TexLayout("single", DEFAULT_TILE)
        self.image = new_image(self.lay)
        self.active = self.lay.order[0]
        self.locked = set()
        self.color = QColor(124, 124, 124)
        self.tool = "select"
        self.recent_colors = self._load_recent_colors()
        self.pending_item_name = None
        self.undo_stack = []
        self.redo_stack = []
        self._stroke_before = None
        self._i18n = []
        self._retr_hooks = []
        self.dirty = False
        self._clean_state = None
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(1500)
        self.autosave_timer.timeout.connect(self.write_recovery)

        # La rueda solo controla un control si fue clickeado (queda "armado");
        # si no, la rueda desplaza el panel en lugar de cambiar el valor.
        self._wheel_guard = WheelGuard(self)
        QApplication.instance().installEventFilter(self._wheel_guard)
        GuardedComboBox.wheel_guard = self._wheel_guard

        self.init_ui()

        # Instalar el filtro también a nivel de cada control: garantiza que
        # la rueda se procese antes que el propio control (la forma fiable).
        for cls in self._wheel_guard.GUARDED:
            for w in self.findChildren(cls):
                w.installEventFilter(self._wheel_guard)
        self.apply_style()
        self.rebuild_zone_checks()
        self.sync_controls()
        self.update_mode_visibility()
        self._clean_state = self.snapshot()
        self.update_history_actions()
        self.base_title = self.windowTitle()
        self._update_title()

    # idiomas
    def bind(self, setter, key):
        self._i18n.append((setter, key))
        setter(key() if callable(key) else T(key))

    def retranslate(self):
        for setter, key in self._i18n:
            setter(key() if callable(key) else T(key))
        for fn in self._retr_hooks:
            fn()
        self.rebuild_zone_checks()
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

    def make_group(self, title_key, layout_cls=QVBoxLayout):
        g = QGroupBox()
        self.bind(g.setTitle, title_key)
        return g, layout_cls(g)

    def make_button(self, text_key, slot, tip=None):
        b = QPushButton()
        self.bind(b.setText, text_key)
        if tip:
            self.bind(b.setToolTip, tip)
        b.clicked.connect(lambda checked=False: slot())
        return b

    # interfaz
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

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

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        toolbar.addWidget(QLabel("🌐 "))
        self.lang_combo = GuardedComboBox()
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

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # panel izquierdo
        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setContentsMargins(12, 12, 12, 12)

        mode_group, mode_layout = self.make_group("mode_group", QHBoxLayout)
        self.mode_buttons = {}
        for m in ("block", "free"):
            b = QPushButton()
            b.setCheckable(True)
            b.clicked.connect(lambda checked, mm=m: self.set_mode(mm))
            self.bind(b.setText, "mode_" + m)
            mode_layout.addWidget(b)
            self.mode_buttons[m] = b
        self.mode_buttons["block"].setChecked(True)
        left_layout.addWidget(mode_group)

        tools_group, tools_layout = self.make_group("tools_group", QGridLayout)
        self.tool_buttons = {}
        for i, name in enumerate(TOOL_ORDER):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=name: self.set_tool(t))
            tools_layout.addWidget(btn, i // 2, i % 2)
            self.tool_buttons[name] = btn
            self.bind(btn.setText, "tool_" + name)
            self.bind(btn.setToolTip, lambda n=name: f"{T('tool_' + n)}  [{TOOL_KEYS[n]}]")
        self.tool_buttons[self.tool].setChecked(True)
        row = (len(TOOL_ORDER) + 1) // 2
        sym_lbl = QLabel()
        self.bind(sym_lbl.setText, "symmetry")
        tools_layout.addWidget(sym_lbl, row, 0, 1, 2)
        self.sym_combo = GuardedComboBox()
        for mode in range(4):
            self.sym_combo.addItem("", mode)
        tools_layout.addWidget(self.sym_combo, row + 1, 0, 1, 2)
        self._retr_hooks.append(self.refresh_combo_texts)
        left_layout.addWidget(tools_group)

        color_group, color_layout = self.make_group("color_group")
        crow = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 30)
        self.color_btn.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #555; border-radius: 4px;")
        self.color_btn.clicked.connect(self.pick_color)
        self.hex_input = QLineEdit(self.color.name().upper())
        self.hex_input.setFixedWidth(80)
        self.hex_input.returnPressed.connect(self.apply_hex)
        crow.addWidget(self.color_btn)
        crow.addWidget(self.hex_input)
        crow.addStretch()
        color_layout.addLayout(crow)

        alpha_lbl = QLabel()
        self.bind(alpha_lbl.setText, "alpha")
        color_layout.addWidget(alpha_lbl)
        arow = QHBoxLayout()
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(255)
        self.alpha_value = QLabel("100%")
        self.alpha_value.setMinimumWidth(40)
        self.alpha_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.alpha_slider.valueChanged.connect(lambda v: self.alpha_value.setText(f"{round(v / 255 * 100)}%"))
        arow.addWidget(self.alpha_slider)
        arow.addWidget(self.alpha_value)
        color_layout.addLayout(arow)

        var_lbl = QLabel()
        self.bind(var_lbl.setText, "variation")
        self.bind(var_lbl.setToolTip, "variation_tip")
        color_layout.addWidget(var_lbl)
        vrow = QHBoxLayout()
        self.var_slider = QSlider(Qt.Orientation.Horizontal)
        self.var_slider.setRange(0, 50)
        self.var_slider.setValue(0)
        self.bind(self.var_slider.setToolTip, "variation_tip")
        self.var_value = QLabel("0%")
        self.var_value.setMinimumWidth(40)
        self.var_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.var_slider.valueChanged.connect(lambda v: self.var_value.setText(f"{v}%"))
        vrow.addWidget(self.var_slider)
        vrow.addWidget(self.var_value)
        color_layout.addLayout(vrow)

        rc_lbl = QLabel()
        self.bind(rc_lbl.setText, "recent_colors")
        color_layout.addWidget(rc_lbl)
        rc_row = QHBoxLayout()
        self.recent_colors_widget = QWidget()
        self.recent_colors_layout = QHBoxLayout(self.recent_colors_widget)
        self.recent_colors_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_colors_layout.setSpacing(4)
        self.recent_colors_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        rc_row.addWidget(self.recent_colors_widget)
        self.btn_save_pal = QPushButton("💾")
        self.bind(self.btn_save_pal.setToolTip, "save_palette")
        self.btn_save_pal.setFixedWidth(32)
        self.btn_save_pal.clicked.connect(self.save_palette)
        rc_row.addWidget(self.btn_save_pal)
        self.btn_load_pal = QPushButton("📂")
        self.bind(self.btn_load_pal.setToolTip, "load_palette")
        self.btn_load_pal.setFixedWidth(32)
        self.btn_load_pal.clicked.connect(self.load_palette)
        rc_row.addWidget(self.btn_load_pal)
        color_layout.addLayout(rc_row)
        left_layout.addWidget(color_group)

        self.tpl_group, tpl_layout = self.make_group("template_group")
        tl = QLabel()
        self.bind(tl.setText, "template_lbl")
        tpl_layout.addWidget(tl)
        self.tpl_combo = GuardedComboBox()
        for k in TEMPLATE_ORDER:
            self.tpl_combo.addItem("", k)
        self.tpl_combo.currentIndexChanged.connect(self.on_template_changed)
        tpl_layout.addWidget(self.tpl_combo)
        rl = QLabel()
        self.bind(rl.setText, "tile_size_lbl")
        tpl_layout.addWidget(rl)
        self.tile_combo = GuardedComboBox()
        for r in TILE_SIZES:
            self.tile_combo.addItem(f"{r} × {r}", r)
        self.tile_combo.currentIndexChanged.connect(self.on_tile_size_changed)
        tpl_layout.addWidget(self.tile_combo)
        self.atlas_info = QLabel()
        self.atlas_info.setStyleSheet("color: #888;")
        tpl_layout.addWidget(self.atlas_info)
        left_layout.addWidget(self.tpl_group)

        self.zones_group, self.zones_layout = self.make_group("zones_group", QGridLayout)
        self.zone_checks = {}
        left_layout.addWidget(self.zones_group)

        ops_group, ops_layout = self.make_group("tile_ops_group", QGridLayout)
        ops_layout.addWidget(self.make_button("op_flip_h", lambda: self.op_flip(True, False)), 0, 0)
        ops_layout.addWidget(self.make_button("op_flip_v", lambda: self.op_flip(False, True)), 0, 1)
        ops_layout.addWidget(self.make_button("op_rot", self.op_rotate), 1, 0, 1, 2)
        shift_row = QHBoxLayout()
        for arrow, dx, dy in (("←", -1, 0), ("→", 1, 0), ("↑", 0, -1), ("↓", 0, 1)):
            b = QPushButton(arrow)
            self.bind(b.setToolTip, "op_shift_tip")
            b.clicked.connect(lambda checked=False, a=dx, c=dy: self.op_shift(a, c))
            shift_row.addWidget(b)
        ops_layout.addLayout(shift_row, 2, 0, 1, 2)
        ops_layout.addWidget(self.make_button("op_half",
                            lambda: self.op_shift(max(1, self.lay.rect(self.active).width() // 2),
                                                   max(1, self.lay.rect(self.active).height() // 2)),
                            "op_half_tip"), 3, 0, 1, 2)
        ops_layout.addWidget(self.make_button("op_copy_all", self.op_copy_all), 4, 0)
        ops_layout.addWidget(self.make_button("op_clear", self.op_clear), 4, 1)
        left_layout.addWidget(ops_group)

        pat_group, pat_layout = self.make_group("patterns_group", QGridLayout)
        for i, name in enumerate(("noise", "bricks", "planks", "checker")):
            pat_layout.addWidget(self.make_button("pat_" + name, lambda n=name: self.apply_pattern(n)),
                                 i // 2, i % 2)
        left_layout.addWidget(pat_group)

        guides_group, guides_layout = self.make_group("guides_group")
        sl = QLabel(); self.bind(sl.setText, "subdiv_lbl")
        guides_layout.addWidget(sl)
        self.subdiv_combo = GuardedComboBox()
        for v in (1, 2, 4, 8):
            self.subdiv_combo.addItem("", v)
        self.subdiv_combo.currentIndexChanged.connect(self.on_subdiv_changed)
        guides_layout.addWidget(self.subdiv_combo)
        ref_row = QHBoxLayout()
        ref_row.addWidget(self.make_button("ref_load", self.load_reference))
        ref_row.addWidget(self.make_button("ref_clear", self.clear_reference))
        guides_layout.addLayout(ref_row)
        self.ref_check = QCheckBox()
        self.ref_check.setChecked(True)
        self.ref_check.toggled.connect(self.on_ref_toggled)
        self.bind(self.ref_check.setText, "ref_show")
        guides_layout.addWidget(self.ref_check)
        ol = QLabel(); self.bind(ol.setText, "ref_opacity")
        guides_layout.addWidget(ol)
        self.ref_slider = QSlider(Qt.Orientation.Horizontal)
        self.ref_slider.setRange(5, 100)
        self.ref_slider.setValue(50)
        self.ref_slider.valueChanged.connect(self.on_ref_opacity)
        guides_layout.addWidget(self.ref_slider)
        left_layout.addWidget(guides_group)

        file_group, file_layout = self.make_group("file_group", QGridLayout)
        file_layout.addWidget(self.make_button("open_png", self.open_file), 0, 0)
        file_layout.addWidget(self.make_button("save_png", self.save_file), 0, 1)
        self.btn_copy = self.make_button("copy_image", self.copy_image_to_clipboard)
        self.btn_copy.setToolTip("Ctrl+Shift+C")
        file_layout.addWidget(self.btn_copy, 1, 0)
        self.btn_export_anim = self.make_button("export_anim", self.export_anim)
        file_layout.addWidget(self.btn_export_anim, 1, 1)
        self.btn_export = self.make_button("export_faces", self.export_faces)
        file_layout.addWidget(self.btn_export, 2, 0, 1, 2)
        file_layout.addWidget(self.make_button("new_texture", self.new_texture), 3, 0, 1, 2)
        file_layout.addWidget(self.make_button("new_item", self.new_item), 4, 0, 1, 2)
        left_layout.addWidget(file_group)
        left_layout.addStretch()

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(left_content)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setMinimumWidth(340)

        # centro
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        self.canvas = Canvas2D(self)
        center_layout.addWidget(self.canvas, 1)

        zoom_bar = QWidget()
        zb = QHBoxLayout(zoom_bar)
        zb.setContentsMargins(8, 4, 8, 4)
        zl = QLabel(); self.bind(zl.setText, "zoom_lbl")
        self.btn_zoom_out = QPushButton("−"); self.btn_zoom_out.setFixedWidth(30)
        self.btn_zoom_out.clicked.connect(lambda: self.zoom_step(-1))
        self.bind(self.btn_zoom_out.setToolTip, "zoom_out_tip")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(Canvas2D.MIN_ZOOM, Canvas2D.MAX_ZOOM)
        self.zoom_slider.setValue(self.canvas.zoom)
        self.zoom_slider.valueChanged.connect(self.canvas.set_zoom)
        self.btn_zoom_in = QPushButton("+"); self.btn_zoom_in.setFixedWidth(30)
        self.btn_zoom_in.clicked.connect(lambda: self.zoom_step(1))
        self.bind(self.btn_zoom_in.setToolTip, "zoom_in_tip")
        self.zoom_value = QLabel(f"{self.canvas.zoom}×")
        self.zoom_value.setMinimumWidth(40)
        self.btn_fit = QPushButton()
        self.btn_fit.clicked.connect(self.canvas.fit_to_view)
        self.bind(self.btn_fit.setText, "fit")
        self.bind(self.btn_fit.setToolTip, "fit_tip")
        zb.addWidget(zl); zb.addWidget(self.btn_zoom_out)
        zb.addWidget(self.zoom_slider, 1)
        zb.addWidget(self.btn_zoom_in); zb.addWidget(self.zoom_value); zb.addWidget(self.btn_fit)
        center_layout.addWidget(zoom_bar)

        # panel derecho
        right_panel = QWidget()
        right_panel.setMinimumWidth(320)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)

        self.viewer_group, viewer_layout = self.make_group("viewer_group")
        self.block_viewer = BlockViewer(self)
        self.bind(self.block_viewer.setToolTip, "viewer_tip")
        viewer_layout.addWidget(self.block_viewer, 1)

        self.block_viewer_controls = QWidget()
        bvc = QVBoxLayout(self.block_viewer_controls)
        bvc.setContentsMargins(0, 0, 0, 0)
        mode_row = QHBoxLayout()
        self.view_mode_buttons = {}
        for mode, key in (("block", "view_block"), ("floor", "view_floor")):
            b = QPushButton(); b.setCheckable(True)
            b.clicked.connect(lambda checked, m=mode: self.set_view_mode(m))
            self.bind(b.setText, key)
            mode_row.addWidget(b)
            self.view_mode_buttons[mode] = b
        self.view_mode_buttons["block"].setChecked(True)
        bvc.addLayout(mode_row)
        self.btn_reset_block = self.make_button("reset_view", self.block_viewer.reset_view)
        bvc.addWidget(self.btn_reset_block)
        viewer_layout.addWidget(self.block_viewer_controls)

        right_layout.addWidget(self.viewer_group, 3)

        self.preview_group = QGroupBox()
        prev_layout = QHBoxLayout(self.preview_group)
        self.preview = TilePreview(self)
        self.bind(self.preview.setToolTip, "preview_tip")
        prev_layout.addWidget(self.preview, 3)
        slot_box = QWidget()
        slot_layout = QVBoxLayout(slot_box)
        slot_layout.setContentsMargins(0, 0, 0, 0)
        self.item_slot = ItemSlotPreview(self)
        self.bind(self.item_slot.setToolTip, "item_preview_tip")
        slot_layout.addWidget(self.item_slot)
        slot_label = QLabel()
        slot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slot_label.setStyleSheet("color: #888; font-size: 11px;")
        self.bind(slot_label.setText, "item_preview_group")
        slot_layout.addWidget(slot_label)
        prev_layout.addWidget(slot_box, 1)
        self._retr_hooks.append(self.update_preview_title)
        right_layout.addWidget(self.preview_group, 2)

        splitter.addWidget(left_scroll)
        splitter.addWidget(center)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([350, 640, 400])
        main_layout.addWidget(splitter)

        self.hint_label = QLabel()
        self.hint_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.statusBar().addWidget(self.hint_label, 1)
        self.bind(self.hint_label.setText, "hint")
        self.coord_label = QLabel("")
        self.statusBar().addPermanentWidget(self.coord_label)

        for name, key in TOOL_KEYS.items():
            self.add_shortcut(key, lambda t=name: self.set_tool(t))
        self.add_shortcut("Ctrl+S", self.save_file)
        self.add_shortcut("Ctrl+O", self.open_file)
        self.add_shortcut("Ctrl+0", self.canvas.fit_to_view)
        for seq in ("Ctrl++", "Ctrl+="):
            self.add_shortcut(seq, lambda: self.zoom_step(1))
        self.add_shortcut("Ctrl+-", lambda: self.zoom_step(-1))
        self.add_shortcut("Ctrl+Shift+C", self.copy_image_to_clipboard)
        self.refresh_recent_colors()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QWidget { color: #e0e0e0; background-color: #1a1a1a; font-family: "Noto Sans", "DejaVu Sans", Arial; font-size: 13px; }
            QGroupBox { border: 1px solid #3a3a3a; border-radius: 6px; margin-top: 12px; padding-top: 6px; font-weight: bold; color: #4f8cff; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; left: 8px; }
            QPushButton { background-color: #2b2b2b; border: 1px solid #3a3a3a; border-radius: 4px; padding: 6px 4px; }
            QPushButton:hover { background-color: #3a3a3a; }
            QPushButton:pressed { background-color: #4a4a4a; }
            QPushButton:checked { background-color: #4f8cff; color: white; border-color: #4f8cff; }
            QPushButton:disabled { color: #666; }
            QLineEdit, QSpinBox, QDoubleSpinBox { background-color: #111; border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px; color: white; }
            QComboBox { background-color: #2b2b2b; border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px 8px; min-width: 90px; }
            QComboBox QAbstractItemView { background-color: #2b2b2b; selection-background-color: #4f8cff; color: #e0e0e0; }
            QListWidget { background-color: #111; border: 1px solid #3a3a3a; border-radius: 4px; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #4f8cff; color: white; }
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
            QToolTip { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #4f8cff; padding: 4px; }
        """)

    # modos
    def set_mode(self, mode):
        if mode == self.mode:
            return
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_history_actions()

        if mode == "block":
            guess = guess_layout(self.image.width(), self.image.height(),
                                 self.lay.key if self.lay.tile > 0 else "single")
            if guess is None:
                target = 16
                for s in reversed(TILE_SIZES):
                    if s <= max(self.image.width(), self.image.height()):
                        target = s
                        break
                self.image = self.image.scaled(target, target,
                    Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                guess = ("single", target)
            key, ts = guess
            self.lay = TexLayout(key, ts)
            if self.active not in self.lay.pos:
                self.active = self.lay.order[0]
        else:
            self.lay = FreeLayout(self.image.width(), self.image.height())

        self.mode = mode
        for m, b in self.mode_buttons.items():
            b.setChecked(m == mode)
        self.update_mode_visibility()
        self.sync_controls()
        self.canvas.fit_to_view()
        self.refresh_all()
        self.mark_dirty()

    def update_mode_visibility(self):
        is_block = self.mode == "block"

        self.tpl_group.setVisible(is_block)
        self.zones_group.setVisible(is_block and 2 <= len(self.lay.order) <= 6)
        # El preview 3D y el mosaico 3×3 están disponibles en ambos modos.
        self.viewer_group.setVisible(True)
        self.preview_group.setVisible(True)
        self.block_viewer_controls.setVisible(True)
        self.btn_export.setVisible(is_block)
        self.subdiv_combo.setEnabled(is_block)

    # sincronización
    def refresh_combo_texts(self):
        for i, k in enumerate(TEMPLATE_ORDER):
            self.tpl_combo.setItemText(i, T("tpl_" + k))
        for i, key in enumerate(("sym_none", "sym_h", "sym_v", "sym_both")):
            self.sym_combo.setItemText(i, T(key))
        for i, v in enumerate((1, 2, 4, 8)):
            self.subdiv_combo.setItemText(i, T("subdiv_none") if v == 1 else f"{v} × {v}")

    def sync_controls(self):
        if self.lay.tile > 0:
            for combo, data in ((self.tpl_combo, self.lay.key), (self.tile_combo, self.lay.tile)):
                combo.blockSignals(True)
                combo.setCurrentIndex(max(0, combo.findData(data)))
                combo.blockSignals(False)
        self.refresh_combo_texts()
        self.atlas_info.setText(T("atlas_info", w=self.lay.w, h=self.lay.h, n=len(self.lay.order)))
        self.update_preview_title()

    def update_preview_title(self):
        if self.lay.tile > 0:
            self.preview_group.setTitle(T("preview_group", tile=tile_label(self.active)))
        else:
            self.preview_group.setTitle(T("preview_group", tile=T("tile_free")))
        self.atlas_info.setText(T("atlas_info", w=self.lay.w, h=self.lay.h, n=len(self.lay.order)))

    def rebuild_zone_checks(self):
        while self.zones_layout.count():
            item = self.zones_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.zone_checks = {}
        order = self.lay.order
        self.zones_group.setVisible(self.mode == "block" and 2 <= len(order) <= 6)
        if not (self.mode == "block" and 2 <= len(order) <= 6):
            return
        for i, k in enumerate(order):
            cb = QCheckBox(tile_label(k))
            cb.setChecked(k not in self.locked)
            cb.toggled.connect(lambda state, key=k: self.toggle_lock(key, state))
            self.zones_layout.addWidget(cb, i // 2, i % 2)
            self.zone_checks[k] = cb

    def toggle_lock(self, key, editable):
        if editable:
            self.locked.discard(key)
        else:
            self.locked.add(key)
        self.canvas.update()

    # layout
    def set_layout(self, new_layout, fit=True):
        self.lay = new_layout
        if self.lay.tile > 0:
            self.locked &= set(new_layout.order)
            if self.active not in new_layout.pos:
                self.active = new_layout.order[0]
        else:
            self.active = "all"
        self.rebuild_zone_checks()
        self.sync_controls()
        self.update_mode_visibility()
        if fit:
            self.canvas.fit_to_view()
        self.refresh_all()

    def change_layout(self, key, tile):
        new = TexLayout(key, tile)
        self.push_undo(self.snapshot())
        self.image = convert_image(self.image, self.lay, new)
        self.set_layout(new)
        self.mark_dirty()

    def on_template_changed(self, index):
        key = self.tpl_combo.itemData(index)
        if self.mode == "block" and key != self.lay.key:
            self.change_layout(key, self.lay.tile)

    def on_tile_size_changed(self, index):
        size = self.tile_combo.itemData(index)
        if self.mode != "block" or size == self.lay.tile:
            return
        if size < self.lay.tile:
            ans = QMessageBox.question(
                self, T("res_shrink_title"), T("res_shrink_msg", size=size),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ans != QMessageBox.StandardButton.Yes:
                self.sync_controls()
                return
        self.change_layout(self.lay.key, size)

    def set_active_tile(self, key):
        if self.lay.tile <= 0 or key == self.active or key not in self.lay.pos:
            return
        self.active = key
        self.update_preview_title()
        self.canvas.update()
        self.block_viewer.update()
        self.preview.update()

    # vistas
    def refresh_side(self):
        self.block_viewer.update()
        if hasattr(self, "item_slot"):
            self.item_slot.update()
        self.preview.update()

    def refresh_all(self):
        self.canvas.update()
        self.refresh_side()

    def toggle_grid(self, state):
        self.canvas.show_grid = state
        self.canvas.update()

    def toggle_layout(self, state):
        self.canvas.show_layout = state
        self.canvas.update()

    def on_subdiv_changed(self, index):
        self.canvas.subdiv = self.subdiv_combo.itemData(index)
        self.canvas.update()

    def set_view_mode(self, mode):
        for m, b in self.view_mode_buttons.items():
            b.setChecked(m == mode)
        self.block_viewer.set_mode(mode)

    def on_canvas_zoom_changed(self, z):
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
        if hasattr(self, "hint_label"):
            self.hint_label.setText(T("hint"))

    def update_status(self, x, y):
        L = self.lay
        if not (0 <= x < L.w and 0 <= y < L.h):
            self.coord_label.setText("")
            return
        k = L.key_at(x, y)
        if k:
            r = L.rect(k)
            self.coord_label.setText(f"X: {x}  Y: {y}  |  {tile_label(k)} ({x - r.x()}, {y - r.y()})")
        else:
            self.coord_label.setText(f"X: {x}  Y: {y}  |  {T('free')}")

    # referencia
    def load_reference(self):
        path, _ = QFileDialog.getOpenFileName(self, T("dlg_ref"), self._last_dir("files"), T("img_filter"))
        if not path:
            return
        img = QImage(path)
        if img.isNull():
            return
        self._set_last_dir("files", path)
        self.canvas.ref_image = img.convertToFormat(QImage.Format.Format_ARGB32)
        self.ref_check.setChecked(True)
        self.canvas.ref_visible = True
        self.canvas.update()

    def clear_reference(self):
        self.canvas.ref_image = None
        self.canvas.update()

    def on_ref_toggled(self, state):
        self.canvas.ref_visible = state
        self.canvas.update()

    def on_ref_opacity(self, v):
        self.canvas.ref_opacity = v / 100.0
        self.canvas.update()

    # historial
    def snapshot(self):
        return (self.image.copy(), self.lay.key, self.lay.tile, self.mode)

    def start_draw(self):
        self._stroke_before = self.snapshot()

    def end_draw(self):
        before, self._stroke_before = self._stroke_before, None
        if before is not None:
            current = self.snapshot()
            changed = (before[0] != current[0]
                       or before[1] != current[1]
                       or before[2] != current[2]
                       or before[3] != current[3])
            if changed:
                self.push_undo(before)
                self.mark_dirty()
        self.canvas.update()
        self.refresh_side()

    def push_undo(self, snap):
        self.undo_stack.append(snap)
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.update_history_actions()

    def update_history_actions(self):
        self.act_undo.setEnabled(bool(self.undo_stack))
        self.act_redo.setEnabled(bool(self.redo_stack))

    def restore(self, snap):
        img, key, tile, mode = snap
        self.image = img
        if mode != self.mode:
            self.mode = mode
            for m, b in self.mode_buttons.items():
                b.setChecked(m == mode)
        if mode == "block":
            if (key, tile) != (self.lay.key, self.lay.tile):
                self.set_layout(TexLayout(key, tile))
        else:
            if not isinstance(self.lay, FreeLayout) or (self.lay.w, self.lay.h) != (img.width(), img.height()):
                self.set_layout(FreeLayout(img.width(), img.height()))
        self.update_mode_visibility()
        self.refresh_all()

    def undo(self):
        if not self.undo_stack:
            self.statusBar().showMessage(T("nothing_undo"), 1500)
            return
        self.redo_stack.append(self.snapshot())
        self.restore(self.undo_stack.pop())
        self.update_history_actions()
        self.mark_dirty()
        self.statusBar().showMessage(T("undone"), 1200)

    def redo(self):
        if not self.redo_stack:
            self.statusBar().showMessage(T("nothing_redo"), 1500)
            return
        self.undo_stack.append(self.snapshot())
        self.restore(self.redo_stack.pop())
        self.update_history_actions()
        self.mark_dirty()
        self.statusBar().showMessage(T("redone"), 1200)

    def set_color(self, c):
        self.color = QColor(c)
        self._add_recent_color(self.color)
        self.color_btn.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #555; border-radius: 4px;")
        self.hex_input.setText(self.color.name().upper())

    def _add_recent_color(self, c):
        c = QColor(c)
        if not c.isValid():
            return
        for i, x in enumerate(self.recent_colors):
            if x.rgb() == c.rgb():
                del self.recent_colors[i]
                break
        self.recent_colors.append(c)
        if len(self.recent_colors) > 12:
            self.recent_colors.pop(0)
        self.refresh_recent_colors()
        self._save_recent_colors()

    def _save_recent_colors(self):
        try:
            self.settings.setValue("recent_colors",
                                   ",".join(c.name().upper() for c in self.recent_colors))
        except Exception:
            pass

    def refresh_recent_colors(self):
        if not hasattr(self, "recent_colors_layout"):
            return
        while self.recent_colors_layout.count():
            item = self.recent_colors_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for c in self.recent_colors:
            b = QPushButton()
            b.setFixedSize(18, 18)
            b.setStyleSheet(f"background-color: {c.name()}; border: 1px solid #555; border-radius: 3px;")
            b.setToolTip(c.name().upper())
            b.clicked.connect(lambda checked=False, cc=QColor(c): self.set_color(cc))
            self.recent_colors_layout.addWidget(b)

    def save_palette(self):
        path, _ = QFileDialog.getSaveFileName(
            self, T("save_palette"),
            os.path.join(self._last_dir("palette") or "", "palette.pal"),
            T("palette_filter"))
        if not path:
            return
        if not path.lower().endswith((".pal", ".txt")):
            path += ".pal"
        try:
            with open(path, "w", encoding="utf-8") as fh:
                for c in self.recent_colors:
                    fh.write(c.name().upper() + "\n")
        except OSError:
            QMessageBox.critical(self, T("error"), T("save_failed"))
            return
        self._set_last_dir("palette", path)
        self.statusBar().showMessage(T("palette_saved", path=path), 3000)

    def load_palette(self):
        path, _ = QFileDialog.getOpenFileName(self, T("load_palette"),
                                              self._last_dir("palette"), T("palette_filter"))
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                data = fh.read()
        except OSError:
            QMessageBox.critical(self, T("error"), T("save_failed"))
            return
        colors = [QColor(m.group(0)) for m in re.finditer(r"#[0-9A-Fa-f]{6}\b", data)]
        seen = []
        for c in colors:
            if c.isValid() and all(x.rgb() != c.rgb() for x in seen):
                seen.append(c)
        self.recent_colors = seen[-12:]
        self.refresh_recent_colors()
        self._save_recent_colors()
        self._set_last_dir("palette", path)
        self.statusBar().showMessage(T("palette_loaded", n=len(self.recent_colors)), 3000)

    def _load_recent_colors(self):
        raw = str(self.settings.value("recent_colors", ""))
        out = []
        for tok in raw.split(","):
            tok = tok.strip()
            c = QColor(tok)
            if tok.startswith("#") and c.isValid():
                out.append(c)
        return out[-12:]

    def _last_dir(self, key):
        return str(self.settings.value("last_dir_" + key, ""))

    def _set_last_dir(self, key, path):
        if path:
            self.settings.setValue("last_dir_" + key, os.path.dirname(path))

    def _update_title(self):
        if hasattr(self, "base_title"):
            self.setWindowTitle(self.base_title + (" •" if self.dirty else ""))

    def copy_image_to_clipboard(self):
        QApplication.clipboard().setImage(self.image)
        self.statusBar().showMessage(T("copied"), 2000)

    def show_about(self, *_):
        QMessageBox.about(self, T("about_title"), T("about_text", version=APP_VERSION))

    def export_anim(self):
        img = self.image
        w, h = img.width(), img.height()
        if w <= 0 or h <= w or h % w != 0:
            QMessageBox.warning(self, T("export_anim"), T("anim_not_strip"))
            return
        frames = h // w
        frm, ok = QInputDialog.getInt(self, T("export_anim"), T("anim_frametime"), 2, 1, 256)
        if not ok:
            return
        default_name = (self.pending_item_name or "animated") + ".png"
        default = os.path.join(self._last_dir("anim") or "", default_name)
        path, _ = QFileDialog.getSaveFileName(self, T("export_anim"), default, T("png_filter"))
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        overwrite = False
        if os.path.exists(path) or os.path.exists(path + ".mcmeta"):
            ans = QMessageBox.question(self, T("export_overwrite_title"), T("export_overwrite_msg"),
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            overwrite = ans == QMessageBox.StandardButton.Yes
            if not overwrite:
                return
        if not img.save(path, "PNG"):
            QMessageBox.critical(self, T("error"), T("save_failed"))
            return
        try:
            with open(path + ".mcmeta", "w", encoding="utf-8") as fh:
                json.dump({"animation": {"frametime": int(frm)}}, fh)
        except OSError:
            QMessageBox.critical(self, T("error"), T("save_failed"))
            return
        self._set_last_dir("anim", path)
        self.statusBar().showMessage(T("anim_saved", path=path), 4000)

    def pick_color(self):
        c = QColorDialog.getColor(self.color, self, T("pick_color"))
        if c.isValid():
            self.set_color(c)

    def apply_hex(self):
        c = QColor(self.hex_input.text())
        if c.isValid():
            self.set_color(c)

    # dibujo
    def paint_color(self):
        c = QColor(self.color)
        c.setAlpha(self.alpha_slider.value())
        return vary_color(c, self.var_slider.value())

    def can_edit(self, x, y):
        k = self.lay.key_at(x, y)
        return k is not None and k not in self.locked

    def symmetric_points(self, x, y):
        pts = [(x, y)]
        mode = self.sym_combo.currentData()
        if not mode:
            return pts
        if self.lay.tile > 0:
            ts = self.lay.tile
            tx, ty = (x // ts) * ts, (y // ts) * ts
            mx, my = tx + ts - 1 - (x - tx), ty + ts - 1 - (y - ty)
        else:
            # Modo Libre: simetría a lo largo de todo el lienzo
            mx, my = self.image.width() - 1 - x, self.image.height() - 1 - y
        if mode in (1, 3):
            pts.append((mx, y))
        if mode in (2, 3):
            pts.append((x, my))
        if mode == 3:
            pts.append((mx, my))
        return pts

    def draw_pixel(self, x, y, is_erase):
        if self.tool == "select":
            return
        if not self.can_edit(x, y):
            return
        if self.tool == "picker":
            c = self.image.pixelColor(x, y)
            if c.alpha() > 0:
                self.set_color(c)
            return
        if self.tool == "bucket":
            self.flood_fill(x, y, is_erase)
            return
        if self.tool == "replace":
            self.replace_color(x, y, is_erase)
            return
        for px, py in self.symmetric_points(x, y):
            if is_erase or self.tool == "eraser":
                self.image.setPixelColor(px, py, Qt.GlobalColor.transparent)
            else:
                self.image.setPixelColor(px, py, self.paint_color())
        self.refresh_side()

    def flood_fill(self, x, y, is_erase):
        key = self.lay.key_at(x, y)
        if key is None or key in self.locked:
            return
        r = self.lay.rect(key)
        target = self.image.pixelColor(x, y)
        fill_color = QColor(Qt.GlobalColor.transparent) if is_erase else QColor(self.color)
        if not is_erase:
            fill_color.setAlpha(self.alpha_slider.value())
        if target == fill_color:
            return
        if is_erase and target.alpha() == 0:
            return
        seen = set()
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in seen:
                continue
            if not (r.left() <= cx <= r.right() and r.top() <= cy <= r.bottom()):
                continue
            seen.add((cx, cy))
            if self.image.pixelColor(cx, cy) != target:
                continue
            self.image.setPixelColor(cx, cy, fill_color)
            stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
        self.refresh_side()

    def replace_color(self, x, y, is_erase):
        target = self.image.pixelColor(x, y)
        fill_color = QColor(Qt.GlobalColor.transparent) if is_erase else QColor(self.color)
        if not is_erase:
            fill_color.setAlpha(self.alpha_slider.value())
        if target == fill_color:
            return
        if is_erase and target.alpha() == 0:
            return
        for k in self.lay.order:
            if k in self.locked:
                continue
            r = self.lay.rect(k)
            for cy in range(r.top(), r.bottom() + 1):
                for cx in range(r.left(), r.right() + 1):
                    if self.image.pixelColor(cx, cy) == target:
                        self.image.setPixelColor(cx, cy, fill_color)
        self.refresh_side()

    # operaciones
    def put_tile(self, key, img):
        p = QPainter(self.image)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        p.drawImage(self.lay.rect(key).topLeft(), img)
        p.end()

    def after_edit(self):
        self.canvas.update()
        self.refresh_side()
        self.mark_dirty()

    def tile_op(self, fn):
        if self.lay.tile > 0:
            k = self.active
            if k in self.locked:
                self.statusBar().showMessage(T("tile_locked"), 2500)
                return
            self.push_undo(self.snapshot())
            self.put_tile(k, fn(extract_texture(self.image, self.lay.rect(k))))
        else:
            # Modo Libre: la operación se aplica a todo el lienzo
            self.push_undo(self.snapshot())
            result = fn(self.image.copy())
            if result.size() == self.image.size():
                p = QPainter(self.image)
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
                p.drawImage(0, 0, result)
                p.end()
            else:
                # El tamaño cambió (p. ej. rotar 90° en un lienzo no cuadrado)
                self.image = result
                self.set_layout(FreeLayout(result.width(), result.height()), fit=False)
                self.canvas.fit_to_view()
        self.after_edit()

    def op_flip(self, horizontal, vertical):
        self.tile_op(lambda img: img.mirrored(horizontal, vertical))

    def op_rotate(self):
        self.tile_op(lambda img: img.transformed(QTransform().rotate(90)))

    def op_shift(self, dx, dy):
        def fn(img):
            w, h = img.width(), img.height()
            out = QImage(w, h, QImage.Format.Format_RGBA8888)
            out.fill(Qt.GlobalColor.transparent)
            p = QPainter(out)
            for ox in (-w, 0, w):
                for oy in (-h, 0, h):
                    p.drawImage(dx + ox, dy + oy, img)
            p.end()
            return out
        self.tile_op(fn)

    def op_clear(self):
        def fn(img):
            img.fill(Qt.GlobalColor.transparent)
            return img
        self.tile_op(fn)

    def op_copy_all(self):
        if self.lay.tile <= 0:
            return
        src = extract_texture(self.image, self.lay.rect(self.active))
        targets = [k for k in self.lay.order if k != self.active and k not in self.locked]
        if not targets:
            return
        self.push_undo(self.snapshot())
        for k in targets:
            self.put_tile(k, src)
        self.after_edit()

    # patrones
    def make_pattern(self, name):
        if self.lay.tile > 0:
            w = h = max(1, self.lay.tile)
        else:
            # Modo Libre: el patrón rellena todo el lienzo
            w, h = self.image.width(), self.image.height()
        img = QImage(w, h, QImage.Format.Format_RGBA8888)
        img.fill(Qt.GlobalColor.transparent)
        base = QColor(self.color)
        base.setAlpha(self.alpha_slider.value())
        var = self.var_slider.value()
        if name == "noise":
            amount = var if var else 12
            for y in range(h):
                for x in range(w):
                    img.setPixelColor(x, y, vary_color(base, amount))
        elif name == "checker":
            cell = max(1, min(w, h) // 8)
            light = scale_color(base, 1.25)
            for y in range(h):
                for x in range(w):
                    c = base if ((x // cell + y // cell) % 2 == 0) else light
                    img.setPixelColor(x, y, vary_color(c, var))
        elif name == "bricks":
            bh, bw = max(2, h // 4), max(4, w // 2)
            mortar = QColor(176, 172, 166, base.alpha())
            tones = {}
            for y in range(h):
                j = y // bh
                shift = (j % 2) * (bw // 2)
                for x in range(w):
                    xs = (x - shift) % w
                    if y % bh == bh - 1 or xs % bw == bw - 1:
                        c = vary_color(mortar, 4)
                    else:
                        tone = tones.setdefault((j, xs // bw), random.uniform(0.9, 1.1))
                        c = vary_color(scale_color(base, tone), var if var else 5)
                    img.setPixelColor(x, y, c)
        elif name == "planks":
            ph = max(2, h // 4)
            tones = {}
            for y in range(h):
                j = y // ph
                tone = tones.setdefault(j, random.uniform(0.88, 1.08))
                bx = (j * 5 + 3) % w
                for x in range(w):
                    c = scale_color(base, tone)
                    if y % ph == ph - 1:
                        c = scale_color(c, 0.6)
                    elif x == bx:
                        c = scale_color(c, 0.78)
                    img.setPixelColor(x, y, vary_color(c, var if var else 4))
        return img

    def apply_pattern(self, name):
        self.tile_op(lambda _img: self.make_pattern(name))

    # recuperar trabajo
    def _recovery_paths(self):
        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not base:
            base = os.path.join(os.path.expanduser("~"), ".tessy_texture_editor")
        d = os.path.join(base, "TeEditor", "recovery_tex")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "recovery.png"), os.path.join(d, "recovery.json")

    def clear_recovery(self):
        try:
            for f in self._recovery_paths():
                if os.path.exists(f):
                    os.remove(f)
        except OSError:
            pass

    def set_clean(self):
        self._clean_state = self.snapshot()
        self.dirty = False
        self.autosave_timer.stop()
        self.clear_recovery()
        self._update_title()

    def mark_dirty(self):
        current = self.snapshot()
        same = (current[0] == self._clean_state[0] and
                current[1] == self._clean_state[1] and
                current[2] == self._clean_state[2] and
                current[3] == self._clean_state[3])
        self.dirty = not same
        if self.dirty:
            self.autosave_timer.start()
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
            if not self.image.save(tmp_png, "PNG"):
                return
            data = {
                "version": 1,
                "mode": self.mode,
                "tpl": self.lay.key if self.lay.tile > 0 else "free",
                "tile": self.lay.tile if self.lay.tile > 0 else 0,
                "w": self.image.width(), "h": self.image.height(),
                "color": self.color.name(),
                "alpha": self.alpha_slider.value(),
                "tool": self.tool,
            }
            with open(tmp_meta, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            os.replace(tmp_png, png)
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
            if img.isNull():
                raise ValueError("recovery inválido")
            mode = data.get("mode", "block")
            if mode == "block":
                key = data.get("tpl"); tile = int(data.get("tile", 0))
                if key not in TEMPLATES or tile not in TILE_SIZES:
                    raise ValueError("recovery inválido")
                lay = TexLayout(key, tile)
                if (img.width(), img.height()) != (lay.w, lay.h):
                    raise ValueError("recovery inválido")
            elif mode in ("free", "model"):  # "model" venía de versiones anteriores: se abre como Libre
                mode = "free"
                lay = FreeLayout(img.width(), img.height())
            else:
                raise ValueError("recovery inválido")
        except (OSError, ValueError, TypeError):
            self.clear_recovery()
            return

        ans = QMessageBox.question(
            self, T("recover_title"), T("recover_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        if ans != QMessageBox.StandardButton.Yes:
            self.clear_recovery()
            return

        self.image = img.convertToFormat(QImage.Format.Format_RGBA8888)
        self.mode = mode
        for m, b in self.mode_buttons.items():
            b.setChecked(m == mode)
        self.set_layout(lay)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_history_actions()

        c = QColor(str(data.get("color", "")))
        if c.isValid():
            self.set_color(c)
        self.alpha_slider.setValue(int(data.get("alpha", 255)))
        if data.get("tool") in self.tool_buttons:
            self.set_tool(data["tool"])

        self.dirty = True
        self.refresh_all()
        self.statusBar().showMessage(T("recovered"), 4000)

    def closeEvent(self, e):
        self.autosave_timer.stop()
        self.write_recovery()
        e.accept()

    # archivos
    def new_texture(self):
        dlg = NewTextureDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        w, h = dlg.values()
        self.push_undo(self.snapshot())
        self.pending_item_name = None
        img = QImage(w, h, QImage.Format.Format_RGBA8888)
        img.fill(Qt.GlobalColor.transparent)
        self.image = img
        if self.mode != "free":
            self.mode = "free"
            for m, b in self.mode_buttons.items():
                b.setChecked(m == "free")
        self.active = "all"
        self.set_layout(FreeLayout(w, h))
        self.after_edit()

    def new_item(self):
        dlg = NewItemDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name, w, h = dlg.values()
        if not name:
            return
        self.push_undo(self.snapshot())
        self.pending_item_name = name
        img = QImage(w, h, QImage.Format.Format_RGBA8888)
        img.fill(Qt.GlobalColor.transparent)
        self.image = img
        if self.mode != "free":
            self.mode = "free"
            for m, b in self.mode_buttons.items():
                b.setChecked(m == "free")
        self.active = "all"
        self.set_layout(FreeLayout(w, h))
        self.after_edit()
        self.statusBar().showMessage(T("item_pending", name=name), 4000)

    def save_file(self):
        default_name = (self.pending_item_name or "texture") + ".png"
        default = os.path.join(self._last_dir("files") or "", default_name)
        path, _ = QFileDialog.getSaveFileName(self, T("dlg_save"), default, T("png_filter"))
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            if self.image.save(path, "PNG"):
                self.pending_item_name = None
                self._set_last_dir("files", path)
                self.set_clean()
                self.statusBar().showMessage(T("saved", path=path), 4000)
            else:
                QMessageBox.critical(self, T("error"), T("save_failed"))

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, T("dlg_open"), self._last_dir("files"), T("png_filter"))
        if not path:
            return
        self.pending_item_name = None
        img = QImage(path)
        if img.isNull():
            QMessageBox.warning(self, T("invalid_size_title"), "No se pudo cargar la imagen")
            return

        if self.mode == "block":
            guess = guess_layout(img.width(), img.height(), self.lay.key if self.lay.tile > 0 else "single")
            if guess is None:
                QMessageBox.warning(self, T("invalid_size_title"), T("invalid_size_msg"))
                return
            key, ts = guess
            self.push_undo(self.snapshot())
            self.image = img.convertToFormat(QImage.Format.Format_RGBA8888)
            self.set_layout(TexLayout(key, ts))
            self._set_last_dir("files", path)
            self.statusBar().showMessage(T("opened_as", tpl=T("tpl_" + key), size=ts), 5000)
        else:
            self.push_undo(self.snapshot())
            self.image = img.convertToFormat(QImage.Format.Format_RGBA8888)
            self.set_layout(FreeLayout(img.width(), img.height()))
            self._set_last_dir("files", path)
            self.statusBar().showMessage(T("opened_free", w=img.width(), h=img.height()), 5000)
        self.set_clean()

    def export_faces(self):
        if self.mode != "block":
            return
        folder = QFileDialog.getExistingDirectory(self, T("export_title"), self._last_dir("files"))
        if not folder:
            return
        base, ok = QInputDialog.getText(self, T("export_title"), T("export_prompt"), text="block")
        base = re.sub(r"[^A-Za-z0-9_\-]", "_", base.strip()) if ok else ""
        if not base:
            return
        files = []
        for i, k in enumerate(self.lay.order):
            if self.lay.key == "single":
                name = f"{base}.png"
            elif k.startswith("t") and k[1:].isdigit():
                name = f"{base}_{i + 1}.png"
            else:
                name = f"{base}_{k}.png"
            files.append((k, os.path.join(folder, name)))
        if any(os.path.exists(p) for _, p in files):
            ans = QMessageBox.question(
                self, T("export_overwrite_title"), T("export_overwrite_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ans != QMessageBox.StandardButton.Yes:
                return
        saved = 0
        for k, path in files:
            if extract_texture(self.image, self.lay.rect(k)).save(path, "PNG"):
                saved += 1
        self._set_last_dir("files", os.path.join(folder, "base.png"))   # recordar la carpeta
        self.statusBar().showMessage(T("exported", n=saved, dir=folder), 5000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Noto Sans", 10))
    window = TextureEditor()
    window.show()
    QTimer.singleShot(0, window.offer_recovery)
    sys.exit(app.exec())
