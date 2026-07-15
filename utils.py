import os
import tempfile
from pathlib import Path

from PIL import Image

MAX_IMAGE_SIZE = 1080
TEMP_DIR = Path(tempfile.gettempdir()) / "tg_social_publisher"
TEMP_DIR.mkdir(exist_ok=True)


async def download_image(file_id, bot):
    file = await bot.get_file(file_id)
    ext = "jpg"
    if file.file_path:
        ext = file.file_path.rsplit(".", 1)[-1].split("?")[0]
        if ext not in ("jpg", "jpeg", "png", "gif"):
            ext = "jpg"
    dest = TEMP_DIR / f"{file_id}.{ext}"
    await file.download_to_drive(dest)
    return str(dest)


def resize_image(path):
    img = Image.open(path)
    width, height = img.size
    if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        if width > height:
            new_w = MAX_IMAGE_SIZE
            new_h = int(height * MAX_IMAGE_SIZE / width)
        else:
            new_h = MAX_IMAGE_SIZE
            new_w = int(width * MAX_IMAGE_SIZE / height)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    out_path = path.replace(".", "_resized.")
    img.save(out_path, "JPEG", quality=95)
    return out_path


def cleanup_temp(paths):
    for p in paths:
        try:
            os.remove(p)
            resized = p.replace(".", "_resized.")
            if os.path.exists(resized):
                os.remove(resized)
        except OSError:
            pass
