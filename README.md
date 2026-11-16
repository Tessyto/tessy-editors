# Tessy's Editors

Dos editores gratuitos (gratis y sin cuentas) pensados para fans de Minecraft.
Ambos disponibles en Español e Inglés (se elige solo el idioma del sistema).

Free editors made by fans of Minecraft, without requiring an account.
English and Spanish included (picks your OS language automatically).

**Estos programas son herramientas hechas por fans. NO son productos oficiales de Mojang/Microsoft.**

**These programs are fan-made tools. They are NOT official Mojang/Microsoft products.**

"Minecraft" es una marca de Mojang Synergies AB / Microsoft.
"Minecraft" is a trademark of Mojang Synergies AB / Microsoft.

## Tessy's Texture Editor

- Editor de texturas para fans de Minecraft (bloques, items y texturas libres).
- Botón **Nueva textura…** para crear el lienzo exacto que quieras (16×16, 16×32, 32×64… items, banners, skins por partes, cualquier cosa).
- Botón **Nuevo item…** con nombre: la app recuerda el nombre y lo propone como archivo al guardar (`tu_nombre.png`).
- Vista previa 3D de cómo se ve el bloque y cómo tilea la textura 3×3 (detección de costuras).
- Vista previa del item como en un cuadradito de inventario (referencia visual de slot; la app no incluye assets vanilla para dibujar).
- Lienzo en blanco (sin texturas vanilla incluidas) para que puedas dibujar y diseñar tus propios assets.
- Herramientas: Lápiz, Borrador, Cubeta, Gotero, Reemplazar, Línea, Rectángulo, simetría (horizontal, vertical, ambas) y variación tonal para un look artesanal.
- Patrones base (ruido, ladrillos, tablones, damero) — generados con el color actual.
- Exporta caras por separado y texturas animadas `.mcmeta` (tiras verticales).
- Paleta de colores recientes + guardar/cargar paletas `.pal`.
- Apertura/guardado con recovery automático ante cierres inesperados.

Descripción del programa: editor de texturas para crear/modificar assets de fans para el juego Minecraft. No es un producto de Mojang/Microsoft.

## Tessy's Skin Editor

Descripción del programa: editor de skins de fans para el juego Minecraft (modelos Steve, Alex y Slim). No es un producto de Mojang/Microsoft.

- Pintor de skins para fans de Minecraft (modelos Steve y Alex).
- Importar desde la API de Mojang por nombre de usuario, o desde una URL de imagen.
- 4 skins de partida: Steve, Alex, Espectro, Zombie.
- Visor 3D con poses (estática, caminar, correr) y gestión de zonas activas (cabeza, cuerpo, brazos, piernas).
- Grilla (32/64/128/256) con guías y espejo.

## Uso

Descarga el `.exe` de tu editor (carpeta `dist/` incluida en este repo) y listo, no hace falta instalar nada.

Nota: Windows puede mostrar **"Windows protegió tu PC"** (SmartScreen) porque el ejecutable no está firmado digitalmente. Es normal para apps independientes: pulsa "Más información" → "Ejecutar de todas formas".

If Windows shows the "Windows protected your PC" (SmartScreen) popup, it means the app is unsigned — tap "More info" → "Run anyway".

## Ejecutar desde el código (opcional)

```bash
pip install PyQt6
python texture_editor.py    # para el editor de texturas
python skin_editor.py       # para el editor de skins
```

## Construir los .exe (Windows)

```bash
pip install pyinstaller
python -m PyInstaller "Tessy's Texture Editor.spec"
python -m PyInstaller "Tessy's Skin Editor.spec"
```

Los ejecutables quedan en `dist/`.

## Atajos comunes

| Atajo | Textura | Skin |
|---|---|---|
| V / P / E / G / I / C / L / R | V=Seleccionar, P=Lápiz, E=Borrador, G=Cubeta, I=Gotero, C=Reemplazar, L=Línea, R=Rectángulo | P=Lápiz, E=Borrador, G=Cubeta, I=Gotero, C=Reemplazar, L=Línea, R=Rectángulo |
| Ctrl+S / Ctrl+O / Ctrl+0 | Guardar / Abrir / Ajustar | Guardar / Abrir / Ajustar |
| Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z | Deshacer / Rehacer | Deshacer / Rehacer |
| Ctrl+G / Rueda | Cuadrícula / Zoom | Cuadrícula / Zoom |
| Ctrl+Shift+C | Copiar imagen | Copiar skin |

## Créditos y atribuciones

- **Tessy** — creador/a de ambas aplicaciones.
- **"Minecraft" es una marca de Mojang Synergies AB / Microsoft**. Este proyecto es una herramienta hecha por fans, no es oficial ni está avalada por los propietarios de la marca.
- **Este repo no incluye assets vanilla de Minecraft.** Tus plantillas son lienzos en blanco; si quieres usar texturas de Mojang, cárgalas con el botón "Cargar referencia…" (los assets vanilla vienen en el `client.jar` de tu instalación; la propiedad de esos assets es de Mojang/Microsoft).
- **PyQt6** — PyQt6 se distribuye bajo licencia **GPLv3** (o licencia comercial de Riverbank Computing Ltd.). Por utilizar PyQt6, este software se publica también bajo **GPLv3**. El código fuente completo está disponible en este repositorio.
- **Qt 6** — Qt se distribuye bajo licencia **LGPLv3**. PyQt6 actúa como bindings sobre Qt.
- **Ui integrados:** QImage/QPainter de Qt para el renderizado de texturas y skins.
- **APIs de Mojang**: el editor de skins usa el servicio público de perfiles de Mojang (`sessionserver.mojang.com`) y `api.minecraftservices.com`, y como respaldo `api.playerdb.co` (archivador comunitario). Estas APIs son propiedad de Mojang/Microsoft y se usan conforme a sus políticas de uso público.

## Tienda

Puedes conseguir los ejecutables de ambos editores aqui: https://tessyowo.itch.io/
Get the executables from both editors here: https://tessyowo.itch.io/

## Licencia

**GPLv3** por dependencia de PyQt6. Puedes usar, modificar y distribuir libremente este software, siempre que los derivados incluyan su código fuente bajo la misma licencia.

**GPLv3** as required by PyQt6. You may use, modify and redistribute this software freely, provided derived works ship their source under the same license.

"Minecraft" is a trademark of Mojang Synergies AB / Microsoft.
This software is **not** an official Mojang/Microsoft product.
