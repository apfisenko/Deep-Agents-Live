"""Tests for caption helpers."""

from __future__ import annotations

from app.rag.caption.image import resize_for_vlm
from app.rag.caption.pricing import estimate_vlm_cost_usd
from PIL import Image


def test_resize_for_vlm_scales_down_large_image() -> None:
    image = Image.new("RGB", (3000, 2000), color=(10, 20, 30))
    resized = resize_for_vlm(image, max_side=1536)
    assert max(resized.size) == 1536


def test_resize_for_vlm_keeps_small_image() -> None:
    image = Image.new("RGB", (800, 600), color=(10, 20, 30))
    resized = resize_for_vlm(image, max_side=1536)
    assert resized.size == (800, 600)


def test_estimate_vlm_cost_free_model() -> None:
    cost = estimate_vlm_cost_usd(
        "nvidia/nemotron-nano-12b-v2-vl:free",
        prompt_tokens=1000,
        completion_tokens=500,
    )
    assert cost == 0.0


def test_estimate_vlm_cost_gemini_flash() -> None:
    cost = estimate_vlm_cost_usd(
        "google/gemini-2.5-flash",
        prompt_tokens=1000,
        completion_tokens=500,
    )
    assert cost > 0.0
