#!/usr/bin/env python3
"""Fetch a wcbooks 'american-textbook-reading' media page, solve the slowAES CUPID
cookie, and extract per-lesson data: title, youtube id, Part 1 / Part 2 mp3.
Writes {code}_media.json. Usage: fetch_atr_media.py <code> <url>
  e.g. fetch_atr_media.py sc2 https://wcbooks.cafe24.com/media/american-textbook-reading-sc2.html
"""
import sys, re, json, subprocess, urllib.request

code, url = sys.argv[1], sys.argv[2]
UA = "Mozilla/5.0"

def get(u, cookie=None):
    req = urllib.request.Request(u, headers={"User-Agent": UA, **({"Cookie": cookie} if cookie else {})})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")

html = get(url)
cookie = None
if "slowAES" in html:
    nums = re.findall(r'toNumbers\("([0-9a-f]{32})"\)', html)
    key, iv, ct = nums[0], nums[1], nums[2]
    p = subprocess.run(f'printf {ct} | xxd -r -p | openssl enc -aes-128-cbc -d -K {key} -iv {iv} -nopad | xxd -p',
                       shell=True, capture_output=True, text=True)
    cookie = "CUPID=" + p.stdout.strip().replace("\n", "")
    html = get(url + "?ckattempt=1", cookie=cookie)

base = re.search(r"mp3/(atr-[a-z0-9-]+)/", html).group(1)   # e.g. atr-sc-2
lessons = {}
for m in re.finditer(r"number:\s*(\d+),\s*title:\s*'([^']+)',\s*youtubeUs:\s*'https://youtu\.be/([A-Za-z0-9_-]{11})'.*?tracks:\s*\[(.*?)\]\s*\}", html, re.S):
    n = int(m.group(1)); title = m.group(2).strip(); yid = m.group(3); tr = m.group(4)
    parts = dict((lab, mp3) for lab, mp3 in re.findall(r"\['Lesson \d+ — ([^']+)','mp3/[^/]+/([^']+)'\]", tr))
    lessons[str(n)] = {"title": title, "youtube": yid,
                       "Part 1": parts.get("Part 1"), "Part 2": parts.get("Part 2"),
                       "Workbook": parts.get("Workbook")}
out = {"code": code, "url": url, "mp3_dir": base, "cookie": cookie, "n_lessons": len(lessons), "lessons": lessons}
open(f"{code}_media.json", "w").write(json.dumps(out, ensure_ascii=False, indent=2))
print(f"[{code}] {len(lessons)} lessons, mp3 dir={base}")
for n in list(lessons)[:2] + [str(len(lessons))]:
    L = lessons.get(n, {})
    print(f"  L{n}: {L.get('title')} | yt={L.get('youtube')} | {L.get('Part 1')}/{L.get('Part 2')}")
