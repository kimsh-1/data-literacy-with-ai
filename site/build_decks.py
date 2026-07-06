#!/usr/bin/env python3
"""build_decks.py — 덱 스펙 JSON(site/decks/S{nn}.json)을 Linear 스타일 발표 덱 HTML로 렌더.

- 입력: site/decks/S01.json ... S20.json  (슬라이드 스펙; build_decks_schema.md 참고)
- 출력: site/session/S01_deck.html ... S20_deck.html
- 16:9 풀뷰포트 슬라이드 · 키보드/스크롤 네비 · 진행바 · 자료로 돌아가기 · 프린트(PDF) 모드

실행: python3 site/build_decks.py           # 전체
      python3 site/build_decks.py S01 S02   # 일부
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECKS_DIR = ROOT / "decks"
OUT_DIR = ROOT / "session"

TOKENS = """
  --canvas:#010102; --surface-1:#0f1011; --surface-2:#141516; --surface-3:#18191a; --surface-4:#191a1b;
  --ink:#f7f8f8; --ink-muted:#d0d6e0; --ink-subtle:#8a8f98; --ink-tertiary:#62666d;
  --primary:#5e6ad2; --primary-hover:#828fff; --primary-focus:#5e69d1;
  --hairline:#23252a; --hairline-strong:#34343a; --hairline-tertiary:#3e3e44; --success:#27a644;
  --font-display:"PretendardDeck",-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,sans-serif;
  --font-text:"PretendardDeck",-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,sans-serif;
  --font-mono:ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,"PretendardDeck",monospace;
"""

CSS = r"""
@font-face{font-family:"PretendardDeck";
  src:url("../fonts/pretendard-deck-subset.woff2") format("woff2");
  font-weight:100 900;font-style:normal;font-display:swap;}
*,*::before,*::after{box-sizing:border-box;}
:root{__TOKENS__}
html,body{margin:0;background:var(--canvas);color:var(--ink);font-family:var(--font-text);
  -webkit-font-smoothing:antialiased;letter-spacing:-0.2px;}
a{color:inherit;text-decoration:none;}
.deck{scroll-snap-type:y mandatory;overflow-y:scroll;height:100vh;scroll-behavior:smooth;}
.slide{scroll-snap-align:start;min-height:100vh;display:flex;flex-direction:column;justify-content:center;
  padding:6vh 8vw;position:relative;background:var(--canvas);}
.slide::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 90% at 82% 8%,rgba(94,106,210,0.10),transparent 55%);}
.eyebrow{font-family:var(--font-mono);font-size:0.82rem;letter-spacing:1.4px;text-transform:uppercase;
  color:var(--primary-hover);margin-bottom:1.4rem;}
.slide h1{font-family:var(--font-display);font-weight:640;font-size:clamp(2.4rem,5.4vw,4.6rem);
  line-height:1.02;letter-spacing:-1.6px;margin:0 0 1.4rem;max-width:20ch;}
.slide h2{font-family:var(--font-display);font-weight:620;font-size:clamp(1.7rem,3.4vw,2.9rem);
  line-height:1.08;letter-spacing:-1px;margin:0 0 2rem;max-width:24ch;}
.subtitle{font-size:clamp(1.05rem,1.7vw,1.5rem);color:var(--ink-muted);max-width:44ch;line-height:1.5;}
.kicker{font-family:var(--font-mono);font-size:0.8rem;letter-spacing:1px;color:var(--ink-subtle);
  text-transform:uppercase;margin-bottom:0.9rem;}
.body{font-size:clamp(1.05rem,1.55vw,1.45rem);color:var(--ink-muted);max-width:52ch;line-height:1.62;margin-bottom:1.6rem;}
ul.bullets{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:1.05rem;max-width:60ch;}
ul.bullets>li{position:relative;padding-left:1.7rem;font-size:clamp(1.02rem,1.5vw,1.4rem);
  color:var(--ink);line-height:1.5;}
ul.bullets>li::before{content:"";position:absolute;left:0;top:0.62em;width:8px;height:8px;border-radius:2px;
  background:var(--primary);box-shadow:0 0 0 4px rgba(94,106,210,0.16);}
ul.bullets>li b{color:var(--ink);font-weight:640;}
.obj-grid{display:flex;flex-direction:column;gap:1.3rem;counter-reset:obj;max-width:58ch;}
.obj-grid>li{list-style:none;display:flex;gap:1.2rem;align-items:flex-start;
  font-size:clamp(1.05rem,1.55vw,1.45rem);color:var(--ink);line-height:1.45;}
.obj-grid>li::before{counter-increment:obj;content:counter(obj,decimal-leading-zero);
  font-family:var(--font-mono);font-size:0.95rem;color:var(--primary-hover);
  border:1px solid var(--hairline-strong);border-radius:8px;padding:0.35em 0.55em;flex:none;margin-top:0.1em;}
.mission-grid{display:flex;flex-direction:column;gap:1rem;max-width:64ch;}
.mission-card{border:1px solid var(--hairline);background:var(--surface-1);border-radius:14px;
  padding:1.3rem 1.5rem;}
.mission-card .m-label{font-weight:640;font-size:clamp(1.05rem,1.5vw,1.4rem);margin-bottom:0.4rem;}
.mission-card .m-desc{color:var(--ink-subtle);font-size:clamp(0.95rem,1.3vw,1.15rem);line-height:1.5;}
table.deck-table{border-collapse:collapse;width:100%;max-width:76ch;font-size:clamp(0.92rem,1.3vw,1.2rem);}
table.deck-table th,table.deck-table td{border-bottom:1px solid var(--hairline);
  padding:0.85rem 1.1rem;text-align:left;vertical-align:top;line-height:1.45;}
table.deck-table th{color:var(--ink-subtle);font-weight:560;font-family:var(--font-mono);
  font-size:0.82em;letter-spacing:0.4px;text-transform:uppercase;border-bottom:1px solid var(--hairline-strong);}
table.deck-table td{color:var(--ink-muted);}
table.deck-table td:first-child{color:var(--ink);font-weight:560;}
.note{color:var(--ink-tertiary);font-size:0.95rem;margin-top:1.2rem;max-width:60ch;line-height:1.5;}
.quote{font-family:var(--font-display);font-weight:560;font-size:clamp(1.5rem,3vw,2.6rem);
  line-height:1.28;letter-spacing:-0.8px;max-width:26ch;color:var(--ink);}
.quote::before{content:"\201C";color:var(--primary);}
.quote::after{content:"\201D";color:var(--primary);}
.attribution{margin-top:1.6rem;color:var(--ink-subtle);font-size:1.05rem;font-family:var(--font-mono);}
.closing .next{margin-top:2rem;padding-top:1.4rem;border-top:1px solid var(--hairline);
  color:var(--ink-subtle);font-size:clamp(1rem,1.4vw,1.25rem);}
.closing .next b{color:var(--primary-hover);}
/* chrome */
.progress{position:fixed;top:0;left:0;height:3px;background:var(--primary);width:0;z-index:40;transition:width .2s;}
.hud{position:fixed;bottom:22px;right:26px;z-index:40;font-family:var(--font-mono);font-size:0.85rem;
  color:var(--ink-subtle);display:flex;gap:14px;align-items:center;}
.hud .counter{color:var(--ink-muted);}
.hud a.back{border:1px solid var(--hairline-strong);border-radius:8px;padding:6px 12px;color:var(--ink-muted);
  background:rgba(15,16,17,0.7);backdrop-filter:blur(6px);transition:border-color .15s,color .15s;}
.hud a.back:hover{border-color:var(--primary);color:var(--ink);}
.brand{position:fixed;top:20px;left:26px;z-index:40;font-family:var(--font-mono);font-size:0.78rem;
  letter-spacing:0.6px;color:var(--ink-tertiary);}
.nav-hint{position:fixed;bottom:22px;left:26px;z-index:40;font-family:var(--font-mono);font-size:0.78rem;
  color:var(--ink-tertiary);}
@media (max-width:640px){.slide{padding:8vh 7vw;}.nav-hint{display:none;}}
@media print{
  @page{size:1280px 720px;margin:0;}
  html,body{height:auto;}
  .deck{height:auto;overflow:visible;scroll-snap-type:none;}
  .slide{height:720px;min-height:720px;page-break-after:always;break-after:page;background:#06070a;}
  .progress,.hud,.nav-hint,.brand{display:none;}
  /* 배포 PDF 경량화: 페이지마다 래스터화되는 그라디언트 글로우 제거 -> 텍스트 벡터만 남겨 용량 최소화 */
  .slide::after{display:none;}
  ul.bullets>li::before{box-shadow:none;}
}
""".replace("__TOKENS__", TOKENS)

JS = r"""
const deck=document.querySelector('.deck');
const slides=[...document.querySelectorAll('.slide')];
const prog=document.querySelector('.progress');
const counter=document.querySelector('.counter .cur');
function cur(){let i=0,best=1e9;slides.forEach((s,k)=>{const d=Math.abs(s.getBoundingClientRect().top);if(d<best){best=d;i=k;}});return i;}
function upd(){const i=cur();prog.style.width=((i+1)/slides.length*100)+'%';if(counter)counter.textContent=i+1;}
function go(n){const i=Math.max(0,Math.min(slides.length-1,n));slides[i].scrollIntoView({behavior:'smooth'});}
deck.addEventListener('scroll',()=>{window.requestAnimationFrame(upd);},{passive:true});
window.addEventListener('keydown',e=>{
  if(['ArrowDown','ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(cur()+1);}
  else if(['ArrowUp','ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(cur()-1);}
  else if(e.key==='Home'){e.preventDefault();go(0);}
  else if(e.key==='End'){e.preventDefault();go(slides.length-1);}
  else if(e.key==='f'){if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen();}
});
upd();
"""


def esc(s):
    return html.escape(str(s), quote=True)


def render_inline(s):
    """굵게: **텍스트** -> <b>. 그 외는 이스케이프."""
    import re
    out, last = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*", str(s)):
        out.append(esc(s[last:m.start()]))
        out.append("<b>" + esc(m.group(1)) + "</b>")
        last = m.end()
    out.append(esc(s[last:]))
    return "".join(out)


def slide_title(sd):
    parts = []
    if sd.get("eyebrow"):
        parts.append(f'<div class="eyebrow">{esc(sd["eyebrow"])}</div>')
    parts.append(f'<h1>{render_inline(sd["title"])}</h1>')
    if sd.get("subtitle"):
        parts.append(f'<p class="subtitle">{render_inline(sd["subtitle"])}</p>')
    return "\n".join(parts)


def slide_objectives(sd):
    lis = "\n".join(f"<li>{render_inline(x)}</li>" for x in sd.get("items", []))
    return f'<h2>{esc(sd.get("heading","학습 목표"))}</h2>\n<ul class="obj-grid">{lis}</ul>'


def slide_concept(sd):
    p = []
    if sd.get("kicker"):
        p.append(f'<div class="kicker">{esc(sd["kicker"])}</div>')
    p.append(f'<h2>{render_inline(sd["heading"])}</h2>')
    if sd.get("body"):
        p.append(f'<p class="body">{render_inline(sd["body"])}</p>')
    if sd.get("bullets"):
        lis = "\n".join(f"<li>{render_inline(x)}</li>" for x in sd["bullets"])
        p.append(f'<ul class="bullets">{lis}</ul>')
    return "\n".join(p)


def slide_table(sd):
    cols = sd.get("columns", [])
    thead = "".join(f"<th>{esc(c)}</th>" for c in cols)
    rows = []
    for r in sd.get("rows", []):
        rows.append("<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in r) + "</tr>")
    p = [f'<h2>{render_inline(sd["heading"])}</h2>']
    p.append(f'<table class="deck-table"><thead><tr>{thead}</tr></thead><tbody>{"".join(rows)}</tbody></table>')
    if sd.get("note"):
        p.append(f'<p class="note">{render_inline(sd["note"])}</p>')
    return "\n".join(p)


def slide_quote(sd):
    p = [f'<blockquote class="quote">{render_inline(sd["text"])}</blockquote>']
    if sd.get("attribution"):
        p.append(f'<div class="attribution">{esc(sd["attribution"])}</div>')
    return "\n".join(p)


def slide_mission(sd):
    cards = []
    for it in sd.get("items", []):
        if isinstance(it, dict):
            cards.append(
                f'<div class="mission-card"><div class="m-label">{render_inline(it.get("label",""))}</div>'
                f'<div class="m-desc">{render_inline(it.get("desc",""))}</div></div>'
            )
        else:
            cards.append(f'<div class="mission-card"><div class="m-label">{render_inline(it)}</div></div>')
    return f'<h2>{esc(sd.get("heading","오늘의 미션"))}</h2>\n<div class="mission-grid">{"".join(cards)}</div>'


def slide_closing(sd):
    p = [f'<h2>{esc(sd.get("heading","정리"))}</h2>']
    if sd.get("bullets"):
        lis = "\n".join(f"<li>{render_inline(x)}</li>" for x in sd["bullets"])
        p.append(f'<ul class="bullets">{lis}</ul>')
    if sd.get("next"):
        p.append(f'<div class="next">{render_inline(sd["next"])}</div>')
    return "\n".join(p)


RENDERERS = {
    "title": slide_title, "objectives": slide_objectives, "concept": slide_concept,
    "table": slide_table, "quote": slide_quote, "mission": slide_mission, "closing": slide_closing,
}


def build(spec):
    sid = spec["session"]
    slides_html = []
    for i, sd in enumerate(spec["slides"], 1):
        t = sd.get("type", "concept")
        inner = RENDERERS.get(t, slide_concept)(sd)
        extra = " closing" if t == "closing" else ""
        slides_html.append(f'<section id="s{i}" class="slide slide-{t}{extra}"><div class="slide-inner">{inner}</div></section>')
    body = "\n".join(slides_html)
    title = f'{sid} · {spec["title"]}'
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — 발표 덱</title>
<style>{CSS}</style>
</head>
<body>
<div class="progress"></div>
<div class="brand">데이터 리터러시 with AI</div>
<div class="hud">
  <span class="counter"><span class="cur">1</span> / {len(spec["slides"])}</span>
  <a class="back" href="./{sid}.html">자료로 돌아가기</a>
</div>
<div class="nav-hint">화살표 · 스페이스로 이동 · F 전체화면</div>
<main class="deck">
{body}
</main>
<script>{JS}</script>
</body>
</html>"""


def main():
    targets = sys.argv[1:]
    files = sorted(DECKS_DIR.glob("S*.json"))
    if targets:
        files = [DECKS_DIR / f"{t}.json" for t in targets]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in files:
        if not f.exists():
            print(f"[skip] {f.name} 없음")
            continue
        spec = json.loads(f.read_text(encoding="utf-8"))
        out = OUT_DIR / f'{spec["session"]}_deck.html'
        out.write_text(build(spec), encoding="utf-8")
        print(f"[ok] {out.name}  ({len(spec['slides'])} slides)")
        n += 1
    print(f"=== {n} decks rendered ===")


if __name__ == "__main__":
    main()
