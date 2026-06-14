#!/usr/bin/env python3
"""Build {dir}/science_spec.json for an American Textbook Reading book.
Reads {code}_toc.json (list of {lesson,part,title,start}) + {code}_media.json
(per-lesson Part 1 / Part 2 / youtube). Keeps the 3 reading pages per lesson
(Vocabulary=S, Visual Summary=S+1, Reading=S+4); audio Part 1 on the Vocabulary
page, Part 2 on the Reading page; youtube id per lesson.
Optional {code}_pagemap.json (by_printed) remaps printed->pdf index if the scan drifts.
Usage: build_atr_spec.py <code> <book-dir> "<title>"
"""
import sys, json
from pathlib import Path

code, bdir, title = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
toc = json.loads(Path(f"{code}_toc.json").read_text())
media = json.loads(Path(f"{code}_media.json").read_text())["lessons"]
pm = None
pmf = Path(f"{code}_pagemap.json")
if pmf.exists():
    pm = json.loads(pmf.read_text())["by_printed"]

def idx(printed):
    return pm.get(str(printed), printed) if pm else printed

lessons = []
for L in toc:
    n = L["lesson"]; s = L["start"]; m = media[str(n)]
    vocab, summary, reading = idx(s), idx(s + 1), idx(s + 4)
    lessons.append({
        "lesson": n, "part": L["part"], "title": L["title"],
        "pages": [vocab, summary, reading],
        "audio_on": {str(vocab): {"label": "Part 1 · Vocabulary", "mp3": m["Part 1"]},
                     str(reading): {"label": "Part 2 · Reading", "mp3": m["Part 2"]}},
        "youtube": m["youtube"],
    })
(bdir / "science_spec.json").write_text(json.dumps({"title": title, "lessons": lessons}, ensure_ascii=False, indent=2))
# title cross-check vs media
import re
def norm(x): return re.sub(r'[^a-z0-9]', '', x.lower())
mism = [(L["lesson"], L["title"], media[str(L["lesson"])]["title"])
        for L in toc if norm(L["title"]) != norm(media[str(L["lesson"])]["title"])]
print(f"{bdir.name}: {len(lessons)} lessons, {len({p for L in lessons for p in L['pages']})} pages")
print("  title mismatches vs media:", mism or "none")
