"""Image helpers for VLM captioning."""

from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image


def resize_for_vlm(image: Image.Image, *, max_side: int) -> Image.Image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    longest = max(width, height)
    if longest <= max_side:
        return rgb
    scale = max_side / longest
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return rgb.resize(new_size, Image.Resampling.LANCZOS)


def image_to_data_url(path: Path, *, max_side: int = 1536) -> str:
    with Image.open(path) as image:
        resized = resize_for_vlm(image, max_side=max_side)
        buffer = io.BytesIO()
        resized.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
