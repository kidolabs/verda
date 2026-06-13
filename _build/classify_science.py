#!/usr/bin/env python3
"""Classify every page of an American Textbook Reading book by its header/type so
we can keep only the reading/content pages and drop exercises. Batched Gemini.
Types: VOCABULARY (Key/More Vocabulary), SUMMARY (Visual Summary/Up Close),
READING (Reading passage), SECTION/TRANSFER/COMPREHENSION/CRITICAL/REVIEW/WORKBOOK
(exercise), DIVIDER (Part divider), FRONT (cover/contents), OTHER.
Writes {dir}/page_types.json = {page: type}. Usage: classify_science.py <dir>
"""
import sys, json, os, io
from pathlib import Path
import fitz
from PIL import Image
from google import genai
from google.genai import types

bdir = Path(sys.argv[1])
doc = fitz.open(str(bdir / "source.pdf"))
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"; N = doc.page_count; BATCH = 8

def part(pn):
    pix = doc[pn - 1].get_pixmap(dpi=120)
    im = Image.frombytes("RGB" if pix.n < 4 else "RGBA", [pix.width, pix.height], pix.samples).convert("RGB")
    b = io.BytesIO(); im.save(b, "JPEG", quality=70)
    return types.Part.from_bytes(data=b.getvalue(), mime_type="image/jpeg")

PROMPT = (
    "Each image is a page from a Science textbook. Classify EACH page by its main "
    "header/role into ONE label:\n"
    "VOCABULARY (Key Vocabulary / More Vocabulary word lists),\n"
    "SUMMARY (Visual Summary / Up Close diagram),\n"
    "READING (a reading passage titled 'Reading' with prose paragraphs),\n"
    "SECTION (Section 1/2 practice), TRANSFER (Transfer practice), "
    "COMPREHENSION (Comprehension questions), CRITICAL (Critical Thinking), "
    "REVIEW (unit/part review), WORKBOOK (workbook/answer pages), "
    "DIVIDER (a Part section-divider page), FRONT (cover/contents/credits), OTHER.\n"
    'Return ONLY a JSON array: [{"seq":<1-based order>,"type":"..."}].')

result = {}
for start in range(1, N + 1, BATCH):
    idxs = list(range(start, min(start + BATCH, N + 1)))
    parts = [PROMPT + f"\n{len(idxs)} pages in order."] + [part(p) for p in idxs]
    arr = None
    for attempt in range(3):
        try:
            r = client.models.generate_content(model=MODEL, contents=parts,
                config=types.GenerateContentConfig(response_mime_type="application/json"))
            arr = json.loads(r.text); break
        except Exception as e:
            print("  retry", str(e)[:50], flush=True)
    if not arr:
        for p in idxs: result[str(p)] = "OTHER"
        continue
    for o in arr:
        s = o.get("seq")
        if s and 1 <= s <= len(idxs):
            result[str(idxs[s - 1])] = o.get("type", "OTHER")
    print(f"  {idxs[0]}-{idxs[-1]} done", flush=True)

(bdir / "page_types.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
keep = {"VOCABULARY", "SUMMARY", "READING"}
kept = sorted(int(p) for p, t in result.items() if t in keep)
print(f"classified {len(result)} pages; KEEP (reading) = {len(kept)} pages", flush=True)
print("kept:", kept, flush=True)
