#!/usr/bin/env python3
"""Render ALL pages of a book's source.pdf (whole-book reader), enhanced for
readability (whiten paper, contrast, colour, sharpen). 300dpi, quality 92.
Usage: render_all.py <book-dir> [dpi]
"""
import sys
from pathlib import Path
import fitz
from PIL import Image, ImageEnhance

bdir = Path(sys.argv[1]); DPI = int(sys.argv[2]) if len(sys.argv) > 2 else 300
pages = bdir / "pages"; pages.mkdir(parents=True, exist_ok=True)
for f in pages.glob("p*.*"): f.unlink()

def whiten(img, lo=14, hi=244):
    s = 255.0 / (hi - lo)
    return img.point([max(0, min(255, int((v - lo) * s))) for v in range(256)] * 3)

doc = fitz.open(str(bdir / "source.pdf"))
for i in range(doc.page_count):
    pix = doc[i].get_pixmap(dpi=DPI)
    im = Image.frombytes("RGB" if pix.n < 4 else "RGBA", [pix.width, pix.height], pix.samples).convert("RGB")
    im = whiten(im)
    im = ImageEnhance.Color(im).enhance(1.10)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = ImageEnhance.Sharpness(im).enhance(1.6)
    im.save(pages / f"p{i+1:03d}.jpg", "JPEG", quality=92, optimize=True)
print(f"{bdir.name}: rendered {doc.page_count} pages @ {DPI}dpi", flush=True)
sz = sum(f.stat().st_size for f in pages.glob('*.jpg'))
print(f"total {sz//1024//1024}MB", flush=True)
