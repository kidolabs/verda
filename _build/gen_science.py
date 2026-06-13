#!/usr/bin/env python3
"""Generate a whole-book reader for the American Textbook Reading series.
Shows ALL pages in order; at each lesson's start page it inserts a heading + the
lesson's audio buttons (Part 1 / Part 2 / Workbook) that feed one sticky bottom
player. Hamburger nav grouped by Part. Includes access gate + inspection guard.
Reads {dir}/science_spec.json. Usage: gen_science.py <book-dir> "<title>"
"""
import sys, json, html as _html
from pathlib import Path

bdir = Path(sys.argv[1]); title = sys.argv[2]
spec = json.loads((bdir / "science_spec.json").read_text())
def esc(s): return _html.escape(str(s), quote=True)

pages_dir = bdir / "pages"
all_pages = sorted(int(f.stem[1:]) for f in pages_dir.glob("p*.jpg"))
def pfile(pn): return f"pages/{next(pages_dir.glob(f'p{pn:03d}.*')).name}"

lessons = spec["lessons"]

# parts in order for nav
parts = []
for L in lessons:
    if not parts or parts[-1]["name"] != L["part"]:
        parts.append({"name": L["part"], "lessons": []})
    parts[-1]["lessons"].append(L)

# nav (hamburger) grouped by part
menu = []
for pi, p in enumerate(parts, 1):
    menu.append(f'<div class="mpart">Part {pi} · {esc(p["name"])}</div>')
    for L in p["lessons"]:
        menu.append(f'<a href="#lesson-{L["lesson"]}">Lesson {L["lesson"]} · {esc(L["title"])}</a>')

# body: only each lesson's reading pages, grouped by Part
body = []
cur_part = None
for L in lessons:
    if L["part"] != cur_part:
        cur_part = L["part"]
        pi = [p["name"] for p in parts].index(cur_part) + 1
        body.append(f'<h2 class="parth"><span class="pnum">PART {pi}</span>{esc(cur_part)}</h2>')
    btns = "".join(
        f'<button class="nghe" data-src="audio/{esc(mp3)}" '
        f'data-unit="Lesson {L["lesson"]} · {esc(L["part"])}" '
        f'data-title="Lesson {L["lesson"]} · {esc(L["title"])} — {esc(kind)}">'
        f'<span class="ic">🔊</span> {esc(kind)}</button>'
        for kind, mp3 in L["audio"].items())
    imgs = "".join(f'<img loading="lazy" src="{pfile(p)}" alt="page {p}">' for p in L["pages"])
    body.append(f'<section class="lesson" id="lesson-{L["lesson"]}">'
                f'<h3><span class="lnum">Lesson {L["lesson"]}</span>{esc(L["title"])}</h3>'
                f'<div class="aud">{btns}</div>{imgs}</section>')

CSS = """
  :root{--accent:#2e8b57;--bg:#f4f7f5;--bar:#1e2a24;--red:#e0533d}
  *{box-sizing:border-box}
  html{scroll-behavior:smooth;scroll-padding-top:64px}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:#222}
  header.top{position:sticky;top:0;z-index:30;background:#fff;border-bottom:2px solid var(--accent);box-shadow:0 2px 6px rgba(0,0,0,.08)}
  .bar{display:flex;align-items:center;gap:12px;padding:10px 14px}
  .burger{border:none;background:var(--accent);color:#fff;width:40px;height:40px;border-radius:10px;font-size:19px;cursor:pointer;flex:none}
  .htxt{min-width:0}
  .htxt .bk{font-size:12px;color:#6a7d70;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .htxt .cur{font-size:16px;font-weight:800;color:var(--accent);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .menu{display:none;border-top:1px solid #e6ece8;max-height:64vh;overflow:auto;background:#fff;padding:6px}
  .menu.open{display:block}
  .menu .mpart{font-size:12px;font-weight:800;letter-spacing:.05em;color:#6a7d70;padding:10px 10px 4px;text-transform:uppercase}
  .menu a{display:block;padding:9px 14px;border-radius:8px;text-decoration:none;color:#243;font-weight:600;font-size:14px}
  .menu a:hover{background:var(--accent);color:#fff}
  #barToggle{position:fixed;top:8px;right:10px;z-index:40;border:none;background:var(--accent);color:#fff;width:32px;height:32px;border-radius:50%;font-size:14px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.25);opacity:.85}
  main{max-width:900px;margin:0 auto;padding:14px 12px 150px}
  main>img{width:100%;height:auto;display:block;border-radius:8px;margin:8px 0;border:1px solid #e3e9e5}
  .parth{font-size:22px;color:var(--accent);background:#d8efe0;border-radius:10px;padding:12px 16px;margin:30px 0 14px}
  .parth .pnum{display:inline-block;font-size:13px;font-weight:800;letter-spacing:.08em;background:var(--accent);color:#fff;padding:2px 10px;border-radius:8px;margin-right:10px;vertical-align:middle}
  .lesson{margin:22px 0 6px;scroll-margin-top:64px}
  .lesson h3{font-size:19px;background:#e8f3ec;border-left:5px solid var(--accent);border-radius:8px;padding:10px 14px;margin:0 0 10px}
  .lesson h3 .lnum{display:inline-block;font-size:12px;font-weight:800;letter-spacing:.06em;background:var(--accent);color:#fff;padding:2px 10px;border-radius:8px;margin-right:10px;vertical-align:middle}
  .aud{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
  button.nghe{display:inline-flex;align-items:center;gap:7px;font-size:14px;font-weight:700;color:#fff;background:var(--accent);border:none;border-radius:10px;padding:9px 15px;cursor:pointer}
  button.nghe:hover{filter:brightness(1.08)}
  button.nghe.playing{background:var(--red)}
  /* bottom player */
  #player{position:fixed;left:0;right:0;bottom:0;z-index:35;background:var(--bar);color:#fff;display:none;padding:10px 16px;border-top:3px solid var(--red);box-shadow:0 -2px 12px rgba(0,0,0,.3)}
  #player.show{display:block}
  #player .ptop{display:flex;align-items:center;gap:14px}
  #player .pinfo{flex:1;min-width:0}
  #player .punit{color:var(--red);font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  #player .ptitle{font-size:16px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  #player .pctrl{display:flex;align-items:center;gap:16px;flex:none}
  #player .pctrl button{background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1}
  #player .pplay{width:48px;height:48px;border-radius:50%;background:var(--red)!important;font-size:21px;display:flex;align-items:center;justify-content:center}
  #player .pright{display:flex;align-items:center;gap:8px;flex:none}
  #player .pright button{background:#33453c;border:none;color:#fff;border-radius:8px;padding:7px 11px;font-size:13px;cursor:pointer}
  #player .pseek{display:flex;align-items:center;gap:10px;font-size:12px;color:#aebfb4;margin-top:8px}
  #player .pseek input{flex:1;accent-color:var(--red)}
  @media(max-width:820px){#player .ptop{flex-wrap:wrap}#player .pinfo{flex:1 0 100%;order:-1;margin-bottom:6px}#player .ptitle{font-size:17px;white-space:normal}#player .pctrl{flex:1;justify-content:center}}
  #gate{position:fixed;inset:0;z-index:100;background:linear-gradient(135deg,#2e8b57,#163a28);display:none;align-items:center;justify-content:center;padding:20px}
  #gate .gbox{background:#fff;border-radius:16px;padding:30px 26px;width:min(340px,92vw);text-align:center;box-shadow:0 12px 40px rgba(0,0,0,.35)}
  #gate h2{margin:0 0 16px;font-size:20px;color:#2e8b57}
  #gate input{width:100%;font-size:22px;text-align:center;letter-spacing:6px;padding:12px;border:2px solid #cfe6d8;border-radius:10px;outline:none}
  #gate button{width:100%;margin-top:14px;font-size:16px;font-weight:700;color:#fff;background:#2e8b57;border:none;border-radius:10px;padding:12px;cursor:pointer}
  #gate .gerr{color:#e0533d;font-size:13px;height:16px;margin-top:8px}
"""

JS = """
  (function(){function bye(){location.replace('https://www.google.com');}
    document.addEventListener('keydown',function(e){var k=(e.key||'').toUpperCase();
      if(e.keyCode===123||((e.ctrlKey||e.metaKey)&&e.shiftKey&&(k==='I'||k==='J'||k==='C'))||((e.ctrlKey||e.metaKey)&&k==='U')){e.preventDefault();bye();}});
    document.addEventListener('contextmenu',function(e){e.preventDefault();});
    setInterval(function(){if(window.outerWidth-window.innerWidth>220||window.outerHeight-window.innerHeight>220)bye();},1000);})();
  (function(){var K='atr_ok',g=document.getElementById('gate'),i=document.getElementById('gpin'),e=document.getElementById('gerr');
    if(localStorage.getItem(K)==='1')return;
    g.style.display='flex';document.body.style.overflow='hidden';i.focus();
    function go(){if(i.value===atob('MTYwOTI1')){localStorage.setItem(K,'1');g.style.display='none';document.body.style.overflow='';}else{e.textContent='Wrong code';i.value='';i.focus();}}
    document.getElementById('gbtn').onclick=go;i.addEventListener('keydown',function(ev){if(ev.key==='Enter')go();});})();
  var au=new Audio(), btns=[].slice.call(document.querySelectorAll('button.nghe')),
      P=document.getElementById('player'), cur=-1, speeds=[1,1.25,1.5,0.75], si=0;
  var elPlay=P.querySelector('.pplay'),elUnit=P.querySelector('.punit'),elTitle=P.querySelector('.ptitle'),
      elCur=P.querySelector('.cur2'),elRem=P.querySelector('.rem'),elSeek=P.querySelector('.pseek input'),elSpeed=P.querySelector('.pspeed');
  function fmt(t){t=Math.max(0,t|0);return (t/60|0)+':'+('0'+(t%60)).slice(-2);}
  function mark(){btns.forEach(function(b,i){var on=(i===cur&&!au.paused);b.classList.toggle('playing',on);b.querySelector('.ic').textContent=on?'⏸':'🔊';});elPlay.textContent=au.paused?'▶':'⏸';}
  function load(i){if(i<0||i>=btns.length)return;cur=i;var b=btns[i];au.src=b.dataset.src;au.playbackRate=speeds[si];elUnit.textContent=b.dataset.unit;elTitle.textContent=b.dataset.title;P.classList.add('show');au.play();}
  btns.forEach(function(b,i){b.addEventListener('click',function(){if(i===cur&&!au.paused){au.pause();P.classList.remove('show');}else{load(i);}});});
  elPlay.onclick=function(){au.paused?au.play():au.pause();};
  P.querySelector('.pprev').onclick=function(){load(cur-1);};
  P.querySelector('.pnext').onclick=function(){load(cur+1);};
  P.querySelector('.pclose').onclick=function(){au.pause();P.classList.remove('show');cur=-1;mark();};
  elSpeed.onclick=function(){si=(si+1)%speeds.length;au.playbackRate=speeds[si];elSpeed.textContent=speeds[si]+'x';};
  P.querySelector('.plist').onclick=function(){if(cur>=0)btns[cur].scrollIntoView({block:'center'});};
  au.addEventListener('play',mark);au.addEventListener('pause',mark);
  au.addEventListener('ended',function(){if(cur+1<btns.length)load(cur+1);else mark();});
  au.addEventListener('timeupdate',function(){if(au.duration){elSeek.value=au.currentTime/au.duration*100;elCur.textContent=fmt(au.currentTime);elRem.textContent='-'+fmt(au.duration-au.currentTime);}});
  elSeek.addEventListener('input',function(){if(au.duration)au.currentTime=elSeek.value/100*au.duration;});
  var mb=document.getElementById('menuBtn'),menu=document.getElementById('menu');
  mb.onclick=function(){menu.classList.toggle('open');};
  menu.querySelectorAll('a').forEach(function(a){a.onclick=function(){menu.classList.remove('open');};});
  var curEl=document.getElementById('curUnit'),mlinks=[].slice.call(menu.querySelectorAll('a')),secs=[].slice.call(document.querySelectorAll('.lesson'));
  function onScroll(){var y=80,best=null;for(var i=0;i<secs.length;i++){if(secs[i].getBoundingClientRect().top<=y)best=secs[i];}
    if(best){curEl.textContent=best.querySelector('h3').textContent;var id=best.id;mlinks.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+id);});}}
  window.addEventListener('scroll',onScroll,{passive:true});window.addEventListener('load',onScroll);onScroll();
  var hdr=document.querySelector('header.top'),tg=document.getElementById('barToggle');
  function pad(){document.documentElement.style.scrollPaddingTop=(hdr.classList.contains('hidden')?52:hdr.querySelector('.bar').offsetHeight+10)+'px';}
  tg.onclick=function(){hdr.classList.toggle('hidden');tg.textContent=hdr.classList.contains('hidden')?'▼':'▲';pad();};
  window.addEventListener('resize',pad);window.addEventListener('load',pad);pad();
"""

PLAYER = """<div id="player"><div class="ptop">
  <div class="pinfo"><div class="punit"></div><div class="ptitle"></div></div>
  <div class="pctrl"><button class="pprev">⏮</button><button class="pplay">▶</button><button class="pnext">⏭</button></div>
  <div class="pright"><button class="pspeed">1x</button><button class="plist">☰</button><button class="pclose">✕</button></div>
  </div><div class="pseek"><span class="cur2">0:00</span><input type="range" min="0" max="100" value="0"><span class="rem">0:00</span></div></div>"""

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style></head>
<body>
<div id="gate"><div class="gbox"><h2>🔒 Enter code</h2>
  <input id="gpin" type="password" inputmode="numeric" autocomplete="off" placeholder="••••••">
  <button id="gbtn">Enter</button><div class="gerr" id="gerr"></div></div></div>
<button id="barToggle" title="Hide/show top bar">▲</button>
<header class="top"><div class="bar">
  <button id="menuBtn" class="burger">☰</button>
  <div class="htxt"><div class="bk"><a href="../index.html" style="color:inherit;text-decoration:none">← {esc(title)}</a></div><div class="cur" id="curUnit"></div></div>
</div><nav id="menu" class="menu">{''.join(menu)}</nav></header>
<main>{''.join(body)}</main>
{PLAYER}
<script>{JS}</script>
</body></html>"""
(bdir / "index.html").write_text(doc, encoding="utf-8")
print(f"{bdir.name}: wrote index.html ({len(lessons)} lessons, {len(all_pages)} pages)")
