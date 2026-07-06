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

FONT = "PretendardDeck, -apple-system, BlinkMacSystemFont, sans-serif"

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
ul.bullets{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0.8rem;max-width:62ch;}
ul.bullets>li{position:relative;padding-left:1.6rem;font-size:clamp(1rem,1.35vw,1.24rem);
  color:var(--ink);line-height:1.42;}
ul.bullets>li::before{content:"";position:absolute;left:0;top:0.58em;width:7px;height:7px;border-radius:2px;
  background:var(--primary);box-shadow:0 0 0 4px rgba(94,106,210,0.16);}
ul.bullets>li b{color:var(--ink);font-weight:640;}
.obj-grid{display:flex;flex-direction:column;gap:1rem;counter-reset:obj;max-width:58ch;}
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
table.deck-table{border-collapse:collapse;width:100%;max-width:76ch;font-size:clamp(0.92rem,1.3vw,1.18rem);}
table.deck-table th,table.deck-table td{border-bottom:1px solid var(--hairline);
  padding:0.72rem 1.1rem;text-align:left;vertical-align:top;line-height:1.4;}
table.deck-table.compact{font-size:clamp(0.8rem,1.05vw,0.98rem);}
table.deck-table.compact th,table.deck-table.compact td{padding:0.42rem 0.8rem;line-height:1.32;}
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
/* --- visual slides --- */
.viz{margin-top:1rem;width:100%;max-width:78ch;}
.viz svg{width:100%;height:auto;display:block;overflow:visible;}
.viz-cap{margin-top:1rem;color:var(--ink-tertiary);font-size:0.92rem;font-family:var(--font-mono);}
.result-line{margin-top:1.4rem;padding:0.9rem 1.2rem;border-left:3px solid var(--primary);
  background:var(--surface-1);border-radius:0 10px 10px 0;color:var(--ink);
  font-size:clamp(1rem,1.4vw,1.3rem);line-height:1.5;max-width:62ch;}
.result-line b{color:var(--primary-hover);}
.result-line .lead{font-family:var(--font-mono);font-size:0.78rem;letter-spacing:1px;
  text-transform:uppercase;color:var(--ink-subtle);display:block;margin-bottom:0.3rem;}
.xform{display:flex;align-items:stretch;gap:0;max-width:80ch;margin-top:0.6rem;}
.xform-card{flex:1;border:1px solid var(--hairline);background:var(--surface-1);border-radius:14px;padding:1.2rem 1.3rem;}
.xform-card .xf-label{font-family:var(--font-mono);font-size:0.8rem;letter-spacing:0.6px;
  color:var(--ink-subtle);text-transform:uppercase;margin-bottom:0.9rem;}
.xform-arrow{display:flex;align-items:center;padding:0 1.1rem;color:var(--primary-hover);font-size:2rem;flex:none;}
.xf-row{display:flex;justify-content:space-between;gap:1rem;padding:0.55rem 0.6rem;
  font-size:clamp(0.92rem,1.25vw,1.12rem);border-radius:8px;}
.xf-row .k{color:var(--ink-subtle);font-family:var(--font-mono);font-size:0.9em;}
.xf-row .v{color:var(--ink);text-align:right;}
.xf-row.changed{background:rgba(94,106,210,0.14);outline:1.5px solid var(--primary);}
.xf-row.changed .v{color:var(--primary-hover);font-weight:640;}
.img-wrap{position:relative;width:100%;max-width:80ch;margin-top:0.6rem;
  border:1px solid var(--hairline);border-radius:16px;overflow:hidden;background:var(--surface-1);}
.img-wrap img{width:100%;display:block;}
.img-box{position:absolute;border:2px solid var(--primary-hover);border-radius:6px;
  box-shadow:0 0 0 3px rgba(94,106,210,0.18);}
.img-box .lbl{position:absolute;top:-1.9em;left:-2px;white-space:nowrap;
  background:var(--primary);color:#fff;font-size:0.8rem;font-weight:600;
  padding:2px 8px;border-radius:6px;}
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
    cls = "deck-table compact" if len(sd.get("rows", [])) >= 6 else "deck-table"
    p.append(f'<table class="{cls}"><thead><tr>{thead}</tr></thead><tbody>{"".join(rows)}</tbody></table>')
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


# ---------------- SVG 차트 엔진 (실데이터를 직접 그림) ----------------
C_PRIMARY, C_HOVER, C_INK, C_SUB, C_HAIR, C_SURF, C_MUT = (
    "#5e6ad2", "#828fff", "#f7f8f8", "#8a8f98", "#2b2d33", "#1b1c1e", "#d0d6e0")


def _fmt(v):
    if isinstance(v, (int, float)) and float(v).is_integer():
        return f"{int(v):,}"
    return str(v)


def _axis(x0, y0, x1, y1):
    return f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{C_HAIR}" stroke-width="1.5"/>'


def svg_bar(data, highlight, unit, ann):
    W, H, pl, pr, pt, pb = 1000, 470, 40, 20, 46, 72
    hi = set(highlight or [])
    vals = [float(d.get("value", 0)) for d in data]
    maxv = max(vals + [1])
    n = len(data)
    span = W - pl - pr
    bw = min(150, span / n * 0.6)
    step = span / n
    plot_h = H - pt - pb
    out = [f'<svg viewBox="0 0 {W} {H}" role="img">']
    out.append(_axis(pl, H - pb, W - pr, H - pb))
    for i, d in enumerate(data):
        cx = pl + step * i + step / 2
        bh = (vals[i] / maxv) * plot_h
        x = cx - bw / 2
        y = H - pb - bh
        fill = C_HOVER if i in hi else C_SURF
        stroke = C_HOVER if i in hi else C_HAIR
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="6" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        vlabel = _fmt(d.get("value")) + (unit or "")
        out.append(f'<text x="{cx:.0f}" y="{y-12:.0f}" text-anchor="middle" fill="{C_INK if i in hi else C_MUT}" '
                   f'font-size="26" font-weight="600" font-family="{FONT}">{esc(vlabel)}</text>')
        out.append(f'<text x="{cx:.0f}" y="{H-pb+34:.0f}" text-anchor="middle" fill="{C_SUB}" '
                   f'font-size="24" font-family="{FONT}">{esc(d.get("label",""))}</text>')
    if ann and ann.get("text") is not None:
        ti = int(ann.get("target", (list(hi)[0] if hi else 0)))
        cx = pl + step * ti + step / 2
        y = H - pb - (vals[ti] / maxv) * plot_h
        tw = 20 + len(str(ann["text"])) * 15
        # 막대 반대편 상단 여백에 콜아웃 박스를 띄우고 막대 꼭대기로 연결선
        bx = (W - pr - tw - 8) if ti < n / 2 else (pl + 8)
        by = pt
        lx = bx + tw / 2
        out.append(f'<line x1="{lx:.0f}" y1="{by+42:.0f}" x2="{cx:.0f}" y2="{y-6:.0f}" '
                   f'stroke="{C_HOVER}" stroke-width="1.5" stroke-dasharray="4 4" opacity="0.7"/>')
        out.append(f'<circle cx="{cx:.0f}" cy="{y-6:.0f}" r="4" fill="{C_HOVER}"/>')
        out.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{tw}" height="42" rx="9" '
                   f'fill="{C_SURF}" stroke="{C_HOVER}" stroke-width="2"/>')
        out.append(f'<text x="{lx:.0f}" y="{by+28:.0f}" text-anchor="middle" fill="{C_HOVER}" '
                   f'font-size="24" font-weight="700" font-family="{FONT}">{esc(ann["text"])}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_line(data, unit, ann):
    W, H, pl, pr, pt, pb = 1000, 470, 56, 24, 46, 72
    vals = [float(d.get("value", 0)) for d in data]
    maxv, minv = max(vals + [1]), min(vals + [0])
    rng = (maxv - minv) or 1
    n = len(data)
    span = W - pl - pr
    step = span / max(n - 1, 1)
    plot_h = H - pt - pb

    def px(i):
        return pl + step * i

    def py(v):
        return H - pb - (v - minv) / rng * plot_h
    out = [f'<svg viewBox="0 0 {W} {H}" role="img">', _axis(pl, H - pb, W - pr, H - pb)]
    pts = " ".join(f"{px(i):.0f},{py(v):.0f}" for i, v in enumerate(vals))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C_HOVER}" stroke-width="3"/>')
    for i, v in enumerate(vals):
        out.append(f'<circle cx="{px(i):.0f}" cy="{py(v):.0f}" r="6" fill="{C_HOVER}"/>')
        out.append(f'<text x="{px(i):.0f}" y="{H-pb+34:.0f}" text-anchor="middle" fill="{C_SUB}" '
                   f'font-size="22" font-family="{FONT}">{esc(data[i].get("label",""))}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_scatter(points, trend, ann, axes):
    W, H, pl, pr, pt, pb = 1000, 480, 64, 24, 40, 66
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    xr, yr = (xmax - xmin) or 1, (ymax - ymin) or 1

    def px(x):
        return pl + (x - xmin) / xr * (W - pl - pr)

    def py(y):
        return H - pb - (y - ymin) / yr * (H - pt - pb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img">',
           _axis(pl, H - pb, W - pr, H - pb), _axis(pl, pt, pl, H - pb)]
    if trend and len(points) >= 2:
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs) or 1
        b = num / den
        a = my - b * mx
        out.append(f'<line x1="{px(xmin):.0f}" y1="{py(a+b*xmin):.0f}" x2="{px(xmax):.0f}" '
                   f'y2="{py(a+b*xmax):.0f}" stroke="{C_HOVER}" stroke-width="2.5" opacity="0.9"/>')
    for x, y in points:
        out.append(f'<circle cx="{px(x):.0f}" cy="{py(y):.0f}" r="7" fill="{C_PRIMARY}" opacity="0.85"/>')
    if axes:
        out.append(f'<text x="{W-pr:.0f}" y="{H-pb+40:.0f}" text-anchor="end" fill="{C_SUB}" '
                   f'font-size="22" font-family="{FONT}">{esc(axes[0])} &#8594;</text>')
        out.append(f'<text x="{pl-14:.0f}" y="{pt+4:.0f}" text-anchor="start" fill="{C_SUB}" '
                   f'font-size="22" font-family="{FONT}">&#8593; {esc(axes[1])}</text>')
    if ann and ann.get("text"):
        out.append(f'<text x="{W*0.5:.0f}" y="{pt+40:.0f}" text-anchor="middle" fill="{C_HOVER}" '
                   f'font-size="34" font-weight="700" font-family="{FONT}">{esc(ann["text"])}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_hist(bins, curve, highlight):
    W, H, pl, pr, pt, pb = 1000, 470, 40, 20, 40, 60
    hi = set(highlight or [])
    maxv = max(bins + [1])
    n = len(bins)
    span = W - pl - pr
    bw = span / n
    plot_h = H - pt - pb
    out = [f'<svg viewBox="0 0 {W} {H}" role="img">', _axis(pl, H - pb, W - pr, H - pb)]
    for i, v in enumerate(bins):
        x = pl + bw * i
        bh = (v / maxv) * plot_h
        fill = C_HOVER if i in hi else C_SURF
        out.append(f'<rect x="{x+3:.0f}" y="{H-pb-bh:.0f}" width="{bw-6:.0f}" height="{bh:.0f}" '
                   f'fill="{fill}" stroke="{C_HAIR}" stroke-width="1"/>')
    if curve:
        import math
        mid = (n - 1) / 2
        sig = n / 5 or 1
        cps = []
        for t in range(0, n * 10 + 1):
            xi = t / 10
            g = math.exp(-((xi - mid) ** 2) / (2 * sig ** 2))
            cps.append(f"{pl+bw*(xi+0.5):.0f},{H-pb-g*plot_h:.0f}")
        out.append(f'<polyline points="{" ".join(cps)}" fill="none" stroke="{C_HOVER}" stroke-width="3"/>')
    out.append("</svg>")
    return "".join(out)


def svg_box(st):
    W, H, pl, pr = 1000, 300, 60, 60
    lo, q1, med, q3, hi = (float(st[k]) for k in ("min", "q1", "med", "q3", "max"))
    dmin, dmax = lo, hi
    for o in st.get("outliers", []):
        dmin, dmax = min(dmin, float(o)), max(dmax, float(o))
    rng = (dmax - dmin) or 1
    cy = 150

    def px(v):
        return pl + (v - dmin) / rng * (W - pl - pr)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img">']
    out.append(f'<line x1="{px(lo):.0f}" y1="{cy}" x2="{px(hi):.0f}" y2="{cy}" stroke="{C_SUB}" stroke-width="2"/>')
    for v in (lo, hi):
        out.append(f'<line x1="{px(v):.0f}" y1="{cy-26}" x2="{px(v):.0f}" y2="{cy+26}" stroke="{C_SUB}" stroke-width="2"/>')
    out.append(f'<rect x="{px(q1):.0f}" y="{cy-42}" width="{px(q3)-px(q1):.0f}" height="84" rx="6" '
               f'fill="{C_SURF}" stroke="{C_HOVER}" stroke-width="2.5"/>')
    out.append(f'<line x1="{px(med):.0f}" y1="{cy-42}" x2="{px(med):.0f}" y2="{cy+42}" stroke="{C_HOVER}" stroke-width="3"/>')
    for o in st.get("outliers", []):
        out.append(f'<circle cx="{px(float(o)):.0f}" cy="{cy}" r="7" fill="none" stroke="{C_SUB}" stroke-width="2"/>')
    labels = [("최솟값", lo), ("Q1", q1), ("중앙값", med), ("Q3", q3), ("최댓값", hi)]
    for name, v in labels:
        out.append(f'<text x="{px(v):.0f}" y="{cy-56}" text-anchor="middle" fill="{C_SUB}" '
                   f'font-size="20" font-family="{FONT}">{esc(name)}</text>')
    out.append("</svg>")
    return "".join(out)


def slide_chart(sd):
    ct = sd.get("chartType", "bar")
    ann = sd.get("annotation")
    if ct == "bar":
        svg = svg_bar(sd.get("data", []), sd.get("highlight"), sd.get("unit", ""), ann)
    elif ct == "line":
        svg = svg_line(sd.get("data", []), sd.get("unit", ""), ann)
    elif ct == "scatter":
        svg = svg_scatter(sd.get("points", []), sd.get("trend", True), ann, sd.get("axes"))
    elif ct == "hist":
        svg = svg_hist(sd.get("bins", []), sd.get("curve", False), sd.get("highlight"))
    elif ct == "box":
        svg = svg_box(sd.get("stats", {}))
    else:
        svg = ""
    p = [f'<h2>{render_inline(sd["heading"])}</h2>', f'<div class="viz">{svg}</div>']
    if sd.get("result"):
        p.append(f'<div class="result-line"><span class="lead">결과</span>{render_inline(sd["result"])}</div>')
    elif sd.get("caption"):
        p.append(f'<div class="viz-cap">{render_inline(sd["caption"])}</div>')
    return "\n".join(p)


def _xf_card(panel):
    rows = []
    for r in panel.get("rows", []):
        cls = " changed" if (len(r) > 2 and r[2]) else ""
        rows.append(f'<div class="xf-row{cls}"><span class="k">{render_inline(r[0])}</span>'
                    f'<span class="v">{render_inline(r[1])}</span></div>')
    return (f'<div class="xform-card"><div class="xf-label">{esc(panel.get("label",""))}</div>{"".join(rows)}</div>')


def slide_transform(sd):
    p = [f'<h2>{render_inline(sd["heading"])}</h2>']
    p.append(f'<div class="xform">{_xf_card(sd["before"])}'
             f'<div class="xform-arrow" aria-hidden="true">&#8594;</div>{_xf_card(sd["after"])}</div>')
    if sd.get("result"):
        p.append(f'<div class="result-line"><span class="lead">결과</span>{render_inline(sd["result"])}</div>')
    return "\n".join(p)


def _deck_img(src):
    # 덱/PDF 용량을 위해 축소·최적화된 deck 변형본을 쓴다(../images/X.png -> ../images/deck/X.png)
    import re as _re
    m = _re.match(r"^(\.\./images/)([\w-]+\.png)$", str(src))
    if m and (ROOT / "images/deck" / m.group(2)).exists():
        return m.group(1) + "deck/" + m.group(2)
    return src


def slide_image(sd):
    boxes = ""
    for b in sd.get("boxes", []):
        style = f'left:{b["x"]}%;top:{b["y"]}%;width:{b["w"]}%;height:{b["h"]}%'
        lbl = f'<span class="lbl">{esc(b["label"])}</span>' if b.get("label") else ""
        boxes += f'<div class="img-box" style="{style}">{lbl}</div>'
    p = []
    if sd.get("heading"):
        p.append(f'<h2>{render_inline(sd["heading"])}</h2>')
    p.append(f'<div class="img-wrap"><img src="{esc(_deck_img(sd["src"]))}" alt="{esc(sd.get("alt",""))}"/>{boxes}</div>')
    if sd.get("caption"):
        p.append(f'<div class="viz-cap">{render_inline(sd["caption"])}</div>')
    return "\n".join(p)


RENDERERS = {
    "title": slide_title, "objectives": slide_objectives, "concept": slide_concept,
    "table": slide_table, "quote": slide_quote, "mission": slide_mission, "closing": slide_closing,
    "chart": slide_chart, "transform": slide_transform, "image": slide_image,
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
