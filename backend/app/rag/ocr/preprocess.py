"""Image preprocessing for dark-theme presentation slides."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, ImageStat


def preprocess_image(image: Image.Image, *, profile: str = "dark_theme") -> Image.Image:
    rgb = image.convert("RGB")
    if profile == "dark_theme":
        grayscale = rgb.convert("L")
        if ImageStat.Stat(grayscale).mean[0] < 128:
            rgb = ImageOps.invert(rgb)
        width, height = rgb.size
        rgb = rgb.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    return rgb


def load_preprocessed_image(path: Path, *, profile: str = "dark_theme") -> Image.Image:
    with Image.open(path) as image:
        return preprocess_image(image, profile=profile)
