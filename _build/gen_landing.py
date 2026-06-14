#!/usr/bin/env python3
"""Generate the American Textbook Reading library landing page (index.html) listing
all books, grouped by series, with cover thumbnails + access gate + inspection guard."""
import json, html as _html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
def esc(s): return _html.escape(str(s), quote=True)

SERIES = [
    ("Science", [f"science-{i}" for i in range(1, 5)]),
    ("Social Studies", [f"social-studies-{i}" for i in range(1, 5)]),
]

def card(slug):
    spec = json.loads((ROOT / slug / "science_spec.json").read_text())
    lessons = spec["lessons"]
    parts = []
    for L in lessons:
        if not parts or parts[-1] != L["part"]:
            parts.append(L["part"])
    name = spec["title"].split("—")[-1].strip()
    units = " · ".join(parts)
    return (f'<a class="card" href="{slug}/index.html">'
            f'<div class="cov"><img src="covers/{slug}.jpg" alt="{esc(name)}"></div>'
            f'<div class="meta"><span class="lvl">{esc(name).upper()}</span>'
            f'<h2>{esc(name)}</h2><div class="units">{esc(units)}</div>'
            f'<div class="stat">{len(parts)} parts · {len(lessons)} lessons · reading + audio + video</div>'
            f'</div></a>')

sections = ""
for series, slugs in SERIES:
    cards = "".join(card(s) for s in slugs if (ROOT / s / "science_spec.json").exists())
    sections += f'<h2 class="series">{esc(series)}</h2><div class="grid">{cards}</div>'

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>American Textbook Reading — Library</title>
<style>
  :root{{--accent:#2e8b57;--bg:#eef4f0}}
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:#1c2922}}
  header{{background:linear-gradient(135deg,#2e8b57,#1c5e3a);color:#fff;padding:34px 20px 28px;text-align:center}}
  header h1{{margin:0 0 6px;font-size:28px}}
  header p{{margin:0;opacity:.92;font-size:15px}}
  main{{max-width:1100px;margin:0 auto;padding:30px 18px 70px}}
  .series{{font-size:20px;color:#2e8b57;border-bottom:2px solid #cfe3d7;padding-bottom:6px;margin:28px 0 16px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:22px}}
  .card{{background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 3px 12px rgba(0,0,0,.1);text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:transform .15s,box-shadow .15s}}
  .card:hover{{transform:translateY(-4px);box-shadow:0 8px 22px rgba(0,0,0,.16)}}
  .card .cov{{aspect-ratio:420/594;background:#f3f6f4;overflow:hidden;border-bottom:1px solid #eef1ef}}
  .card .cov img{{width:100%;height:100%;object-fit:cover}}
  .card .meta{{padding:13px 15px 16px}}
  .card .lvl{{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.05em;color:#fff;background:var(--accent);padding:3px 11px;border-radius:8px;margin-bottom:8px}}
  .card h2{{margin:0 0 6px;font-size:17px}}
  .card .units{{font-size:12px;color:#5a6b62;line-height:1.5}}
  .card .stat{{margin-top:9px;font-size:11px;color:#84938b}}
  footer{{text-align:center;color:#84938b;font-size:12px;padding:0 20px 40px}}
  #gate{{position:fixed;inset:0;z-index:100;background:linear-gradient(135deg,#2e8b57,#163a28);display:none;align-items:center;justify-content:center;padding:20px}}
  #gate .gbox{{background:#fff;border-radius:16px;padding:30px 26px;width:min(340px,92vw);text-align:center;box-shadow:0 12px 40px rgba(0,0,0,.35)}}
  #gate h2{{margin:0 0 16px;font-size:20px;color:#2e8b57}}
  #gate input{{width:100%;font-size:22px;text-align:center;letter-spacing:6px;padding:12px;border:2px solid #cfe6d8;border-radius:10px;outline:none}}
  #gate button{{width:100%;margin-top:14px;font-size:16px;font-weight:700;color:#fff;background:#2e8b57;border:none;border-radius:10px;padding:12px;cursor:pointer}}
  #gate .gerr{{color:#e0533d;font-size:13px;height:16px;margin-top:8px}}
</style></head>
<body>
<header><h1>📚 American Textbook Reading</h1><p>WorldCom Edu · Science &amp; Social Studies — choose a book to read, listen &amp; watch</p></header>
<main>{sections}</main>
<footer>Reading pages only (exercises removed), with the publisher's original audio &amp; video — read, listen &amp; watch.</footer>
<div id="gate"><div class="gbox"><h2>🔒 Enter code</h2>
  <input id="gpin" type="password" inputmode="numeric" autocomplete="off" placeholder="••••••">
  <button id="gbtn">Enter</button><div class="gerr" id="gerr"></div></div></div>
<script>
  (function(){{function bye(){{location.replace('https://www.google.com');}}
    document.addEventListener('keydown',function(e){{var k=(e.key||'').toUpperCase();
      if(e.keyCode===123||((e.ctrlKey||e.metaKey)&&e.shiftKey&&(k==='I'||k==='J'||k==='C'))||((e.ctrlKey||e.metaKey)&&k==='U')){{e.preventDefault();bye();}}}});
    document.addEventListener('contextmenu',function(e){{e.preventDefault();}});
    if(matchMedia('(pointer:fine)').matches){{setInterval(function(){{if(window.outerWidth-window.innerWidth>220||window.outerHeight-window.innerHeight>220)bye();}},1000);}}}})();
  (function(){{var K='atr_ok',g=document.getElementById('gate'),i=document.getElementById('gpin'),e=document.getElementById('gerr');
    if(localStorage.getItem(K)==='1')return;
    g.style.display='flex';document.body.style.overflow='hidden';i.focus();
    function go(){{if(i.value===atob('MTYwOTI1')){{localStorage.setItem(K,'1');g.style.display='none';document.body.style.overflow='';}}else{{e.textContent='Wrong code';i.value='';i.focus();}}}}
    document.getElementById('gbtn').onclick=go;i.addEventListener('keydown',function(ev){{if(ev.key==='Enter')go();}});}})();
</script>
</body></html>"""
(ROOT / "index.html").write_text(html, encoding="utf-8")
print("wrote index.html with", sum(len(s) for _, s in SERIES), "book slots")
