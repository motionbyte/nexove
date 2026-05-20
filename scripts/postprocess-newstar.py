#!/usr/bin/env python3
"""Build transparent Sun texture from a white-on-black master or qlmanage export."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

OUT_SIZE = 1024
# Master PNG: white logo on black (designer export).
MASTER_INK = 30
MASTER_FADE = 8
# qlmanage export on injected black SVG background.
EXPORT_INK = 18
EXPORT_FADE = 8


def _fit_center_rgba(crop: np.ndarray, size: int) -> np.ndarray:
    h, w = crop.shape[:2]
    scale = min(size / w, size / h)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    resized = np.array(
        Image.fromarray(crop).resize((nw, nh), Image.Resampling.LANCZOS),
        dtype=np.uint8,
    )
    canvas = np.zeros((size, size, 4), dtype=np.uint8)
    x0 = (size - nw) // 2
    y0 = (size - nh) // 2
    canvas[y0 : y0 + nh, x0 : x0 + nw] = resized
    return canvas


def _crop_bbox(lum: np.ndarray, ink: float) -> tuple[int, int, int, int]:
    mask = lum > ink
    if not mask.any():
        raise RuntimeError("no logo pixels found")
    ys, xs = np.where(mask)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


def _build_rgba(lum: np.ndarray, ink: float, fade: float) -> np.ndarray:
    alpha = np.clip((lum - fade) * 3, 0, 255)
    alpha = np.maximum(alpha, np.clip((lum - ink) / max(ink - fade, 1) * 255, 0, 255))
    alpha = np.clip(alpha, 0, 255)

    out = np.zeros((*lum.shape, 4), dtype=np.uint8)
    visible = alpha > 8
    out[visible, 0] = 255
    out[visible, 1] = 255
    out[visible, 2] = 255
    out[..., 3] = alpha.astype(np.uint8)
    return out


def postprocess_master(src: Path, dst: Path, size: int = OUT_SIZE) -> None:
    arr = np.array(Image.open(src).convert("RGBA"), dtype=np.float32)
    lum = arr[..., 0] * 0.299 + arr[..., 1] * 0.587 + arr[..., 2] * 0.114
    y0, y1, x0, x1 = _crop_bbox(lum, MASTER_INK)
    lum_crop = lum[y0:y1, x0:x1]
    out = _build_rgba(lum_crop, MASTER_INK, MASTER_FADE)
    Image.fromarray(_fit_center_rgba(out, size)).save(dst)


def postprocess_export(src: Path, dst: Path, size: int = OUT_SIZE) -> None:
    arr = np.array(Image.open(src).convert("RGBA"), dtype=np.float32)
    lum = arr[..., 0] * 0.299 + arr[..., 1] * 0.587 + arr[..., 2] * 0.114
    y0, y1, x0, x1 = _crop_bbox(lum, EXPORT_INK)
    lum_crop = lum[y0:y1, x0:x1]
    out = _build_rgba(lum_crop, EXPORT_INK, EXPORT_FADE)
    Image.fromarray(_fit_center_rgba(out, size)).save(dst)


def postprocess(src: Path, dst: Path, size: int = OUT_SIZE, *, master: bool = False) -> None:
    if master:
        postprocess_master(src, dst, size)
    else:
        postprocess_export(src, dst, size)


def main() -> int:
    if len(sys.argv) < 3:
        print(
            f"usage: {sys.argv[0]} <input.png> <output.png> [size] [--master]",
            file=sys.stderr,
        )
        return 1
    args = sys.argv[1:]
    master = False
    if args[-1] == "--master":
        master = True
        args = args[:-1]
    out_size = int(args[2]) if len(args) == 3 else OUT_SIZE
    postprocess(Path(args[0]), Path(args[1]), out_size, master=master)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
