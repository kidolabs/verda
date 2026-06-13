#!/usr/bin/env python3
"""Scanned PDFs can have pages out of order or missing, so PDF index != printed
page number. OCR the printed footer page number of every page (bottom strip),
batched, and build {letter}_pagemap.json = {printed_page: pdf_index_1based}.
Usage: footer_map.py <letter> <pdf>
"""
import sys, json, os, io
from pathlib import Path
import fitz
from PIL import Image
from google import genai
from google.genai import types

letter, pdf = sys.argv[1], sys.argv[2]
doc = fitz.open(pdf)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"
N = doc.page_count
BATCH = 12

def strip(pn):  # bottom 9% where the page number is printed (either corner)
    pix = doc[pn - 1].get_pixmap(dpi=130)
    im = Image.frombytes("RGB" if pix.n < 4 else "RGBA", [pix.width, pix.height], pix.samples).convert("RGB")
    crop = im.crop((0, int(im.height * 0.91), im.width, im.height))
    b = io.BytesIO(); crop.save(b, "JPEG", quality=80)
    return types.Part.from_bytes(data=b.getvalue(), mime_type="image/jpeg")

PROMPT = ("Each image is the bottom strip of a textbook page. Read the PRINTED page "
          "number (a number in a bottom corner; ignore words like 'Lesson'/'Unit'). "
          'Return ONLY a JSON array of objects {"seq":<1-based order I gave>,"page":<int or null>}.')

pagemap = {}; printed_by_index = {}
for start in range(1, N + 1, BATCH):
    idxs = list(range(start, min(start + BATCH, N + 1)))
    parts = [PROMPT + f"\n{len(idxs)} strips in order."] + [strip(p) for p in idxs]
    for attempt in range(3):
        try:
            r = client.models.generate_content(model=MODEL, contents=parts,
                config=types.GenerateContentConfig(response_mime_type="application/json"))
            arr = json.loads(r.text); break
        except Exception as e:
            print("  retry", str(e)[:50], flush=True); arr = []
    for o in arr:
        seq = o.get("seq"); pg = o.get("page")
        if seq and 1 <= seq <= len(idxs):
            idx = idxs[seq - 1]; printed_by_index[idx] = pg
            if pg is not None and str(pg) not in pagemap:
                pagemap[str(pg)] = idx
    print(f"  pages {idxs[0]}-{idxs[-1]} done", flush=True)

Path(f"{letter}_pagemap.json").write_text(json.dumps(
    {"by_printed": pagemap, "by_index": printed_by_index}, ensure_ascii=False, indent=2))
# report anomalies: where printed != index
drift = [(i, printed_by_index.get(i)) for i in range(1, N + 1) if printed_by_index.get(i) not in (i, None)]
print(f"[{letter}] mapped {len(pagemap)} printed pages; drift (index!=printed): {drift[:20]}")
