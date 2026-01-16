#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Optimización avanzada de imágenes para web (pensado para PageSpeed):

- Recorre la carpeta del script (y subcarpetas si RECURSIVE=True).
- Convierte JPG/PNG/BMP/TIFF/GIF a WebP (quality=82, method=6).
- Corrige orientación EXIF (no animadas).
- Redimensiona si exceden MAX_WIDTH / MAX_HEIGHT.
- Elimina metadatos recreando la imagen desde los píxeles.
- Guarda backup de originales en _backup_originals/.
- Opcionalmente borra los originales tras generar el WebP.

Uso:
    Coloca este archivo en la carpeta raíz de tus imágenes y ejecuta:

        python optimize_images.py
"""

import os
import sys
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps, UnidentifiedImageError

# ==========================
# CONFIGURACIÓN
# ==========================

# Calidad WebP (balance calidad/peso recomendado)
WEBP_QUALITY = 82
WEBP_METHOD = 6  # 0-6 (6 = más compresión, más lento)

# Redimensión máxima (lado mayor). None = no limitar.
MAX_WIDTH: Optional[int] = 1920
MAX_HEIGHT: Optional[int] = 1920

# ¿Procesar subcarpetas?
RECURSIVE = True

# ¿Borrar originales después de crear el .webp?
DELETE_ORIGINALS = True

# ¿Crear copia de seguridad de originales?
MAKE_BACKUP = True
BACKUP_FOLDER_NAME = "_backup_originals"

# Extensiones de entrada (no incluimos .webp para no reprocesar)
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".gif"}

# ==========================
# UTILIDADES
# ==========================

def print_status(message, status="INFO"):
    """Mensajes bonitos en consola."""
    colors = {
        "SUCCESS": "\033[92m",  # Verde
        "WARNING": "\033[93m",  # Amarillo
        "ERROR": "\033[91m",    # Rojo
        "INFO": "\033[94m",     # Azul
        "END": "\033[0m",       # Reset
    }

    prefix = f"[{status}]"
    if os.name != "nt":  # ANSI colores en Unix / terminales modernas
        prefix = f"{colors.get(status, '')}[{status}]{colors['END']}"

    print(f"{prefix} {message}")


def iter_image_files(root: Path):
    """Itera sobre todos los archivos de imagen desde root."""
    if RECURSIVE:
        it = root.rglob("*")
    else:
        it = root.glob("*")

    for path in it:
        if not path.is_file():
            continue
        # Evitar procesar la carpeta de backups
        if BACKUP_FOLDER_NAME in path.parts:
            continue
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def ensure_backup_folder(root: Path) -> Path:
    backup_root = root / BACKUP_FOLDER_NAME
    backup_root.mkdir(exist_ok=True)
    return backup_root


def backup_original(root: Path, backup_root: Path, file_path: Path):
    """Crea una copia del archivo original en la carpeta de backups, conservando estructura."""
    if not MAKE_BACKUP:
        return

    rel = file_path.relative_to(root)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    if not dest.exists():
        dest.write_bytes(file_path.read_bytes())
        print_status(f"Backup: {rel}", "INFO")
    else:
        print_status(f"Backup ya existía: {rel}", "INFO")


def optimize_image(file_path: Path, root: Path, backup_root: Optional[Path]):
    """
    Convierte una imagen a WebP optimizado:
    - Limpia metadatos
    - Corrige orientación EXIF (si aplica)
    - Redimensiona si excede límites
    - Crea backup y borra original (opcional)
    """
    output_path = file_path.with_suffix(".webp")

    # Si ya hay webp, no reprocesar
    if output_path.exists():
        print_status(f"Saltando {file_path}, ya existe .webp", "WARNING")
        return

    try:
        with Image.open(file_path) as img:
            print_status(f"Procesando: {file_path}", "INFO")

            is_animated = getattr(img, "is_animated", False)

            # Para imágenes NO animadas: corregir orientación y limpiar metadatos
            if not is_animated:
                # Corregir orientación según EXIF
                img = ImageOps.exif_transpose(img)

                # Redimensionar si excede límites
                if MAX_WIDTH is not None and MAX_HEIGHT is not None:
                    width, height = img.size
                    scale = min(MAX_WIDTH / width, MAX_HEIGHT / height, 1.0)
                    if scale < 1.0:
                        new_size = (int(width * scale), int(height * scale))
                        img = img.resize(new_size, Image.LANCZOS)
                        print_status(f"  Redimensionado a {new_size[0]}x{new_size[1]}", "INFO")

                # Eliminar metadatos: recrear imagen desde los píxeles
                data = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(data)
                img_to_save = clean_img
            else:
                # Para animaciones, usamos la imagen original
                img_to_save = img
                print_status(f"  Animación detectada (GIF/PNG animado): {file_path.name}", "INFO")

            # Normalizar modo de color
            if img_to_save.mode not in ("RGB", "RGBA", "P"):
                img_to_save = img_to_save.convert("RGB")

            save_kwargs = {
                "format": "WEBP",
                "quality": WEBP_QUALITY,
                "method": WEBP_METHOD,
                "optimize": True,
            }

            if is_animated:
                # Mantener animación
                save_kwargs["save_all"] = True
                save_kwargs["loop"] = 0

            # Backup antes de tocar el archivo
            if backup_root is not None:
                backup_original(root, backup_root, file_path)

            # Guardar WebP
            img_to_save.save(output_path, **save_kwargs)

        # Verificación y borrado del original
        if output_path.exists() and output_path.stat().st_size > 0:
            old_size = file_path.stat().st_size
            new_size = output_path.stat().st_size
            savings_pct = ((old_size - new_size) / old_size) * 100
            print_status(
                f"✅ Optimizado: {file_path.name} → {output_path.name} "
                f"(Ahorro: {savings_pct:.1f}%)",
                "SUCCESS",
            )

            if DELETE_ORIGINALS and file_path != output_path:
                try:
                    file_path.unlink()
                    print_status(f"  Original eliminado: {file_path.name}", "INFO")
                except OSError as e:
                    print_status(f"No se pudo borrar {file_path.name}: {e}", "ERROR")
        else:
            print_status(f"Error al generar WebP para {file_path.name}", "ERROR")

    except UnidentifiedImageError:
        print_status(f"No se pudo identificar la imagen: {file_path}", "ERROR")
    except Exception as e:
        print_status(f"Error inesperado procesando {file_path}: {e}", "ERROR")


def main():
    # Carpeta donde está el script (no el cwd, por seguridad)
    root = Path(__file__).resolve().parent

    print_status("------------------------------------------------", "INFO")
    print_status("INICIANDO OPTIMIZACIÓN AVANZADA DE IMÁGENES", "INFO")
    print_status(f"Carpeta raíz: {root}", "INFO")
    print_status(
        f"Estrategia: convertir a WebP (Q={WEBP_QUALITY}, method={WEBP_METHOD}), "
        f"redimensionar a máx {MAX_WIDTH}x{MAX_HEIGHT}, limpiar metadatos.",
        "INFO",
    )
    if DELETE_ORIGINALS:
        print_status(
            "⚠️  ADVERTENCIA: Los archivos originales (JPG, PNG, etc.) "
            "podrán ser BORRADOS tras generar el WebP.",
            "WARNING",
        )
    if MAKE_BACKUP:
        print_status(
            f"Se guardarán copias en la carpeta '{BACKUP_FOLDER_NAME}/'.", "INFO"
        )
    print_status("------------------------------------------------\n", "INFO")

    if DELETE_ORIGINALS:
        confirm = input("Escribe 'SI' y presiona Enter para confirmar el reemplazo de archivos: ")
        if confirm.strip().upper() != "SI":
            print_status("Operación cancelada por el usuario.", "ERROR")
            return

    backup_root = ensure_backup_folder(root) if MAKE_BACKUP else None

    count = 0
    for file_path in iter_image_files(root):
        optimize_image(file_path, root, backup_root)
        count += 1

    if count == 0:
        print_status("No se encontraron imágenes compatibles para optimizar.", "WARNING")
    else:
        print_status(f"\nProceso finalizado. {count} imágenes procesadas.", "SUCCESS")
        print_status(
            "Recuerda que tus <img> deben apuntar ahora a archivos .webp "
            "o usar <picture> con <source type='image/webp'>.",
            "INFO",
        )


if __name__ == "__main__":
    # Verificar que Pillow esté instalado
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("Error crítico: la librería 'Pillow' no está instalada.")
        print("Instala con: pip install Pillow")
        sys.exit(1)

    main()
