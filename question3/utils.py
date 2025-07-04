import base64
import io
from pathlib import Path
from typing import Dict

import requests
from PIL import Image

MAX_DIM  = (320, 568)          # thumbnail target
MAX_SIZE = 10 * 1024 * 1024    # 10 MiB limit


def fetch_bytes(url: str, timeout: int = 15) -> bytes:
    """Download URL → bytes; hard-fail if non-200 or >MAX_SIZE."""
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()

    buf, size = io.BytesIO(), 0
    for chunk in r.iter_content(8192):
        size += len(chunk)
        if size > MAX_SIZE:
            raise ValueError("image exceeds 10 MiB limit")
        buf.write(chunk)
    return buf.getvalue()


def process_url(url: str) -> Dict:
    """Return metadata + base64 original/thumbnail, or error."""
    rec = {"image_url": url}
    try:
        data = fetch_bytes(url)
        rec["original_size"] = len(data)

        img = Image.open(io.BytesIO(data))
        rec["original_format"]     = img.format
        rec["original_resolution"] = f"{img.width}x{img.height}"
        rec["original_base64"]     = base64.b64encode(data).decode()

        thumb = img.copy()
        thumb.thumbnail(MAX_DIM, Image.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format=img.format)
        tb = buf.getvalue()

        rec["thumb_size"]       = len(tb)
        rec["thumb_resolution"] = f"{thumb.width}x{thumb.height}"
        rec["thumb_base64"]     = base64.b64encode(tb).decode()
        rec["status"] = "success"
    except Exception as exc:
        rec["status"] = "error"
        rec["error"]  = str(exc)
    return rec
