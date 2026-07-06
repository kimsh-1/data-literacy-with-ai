#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
차시 상세 페이지(S01~S20) 정적 생성기.

01_curriculum / 03_handouts / 04_scripts / 06_answers 의 마크다운 4종을
빌드 시점에 HTML로 변환해 site/session/S{nn}.html 에 정적으로 박는다.
클라이언트 마크다운 라이브러리·외부 CDN 없음, 완전 자체포함.

재실행: python3 site/build_sessions.py
"""
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent  # /mnt/d/ai-data-analysis-course
SITE = ROOT / "site"
SESSION_OUT = SITE / "session"
SESSION_OUT.mkdir(parents=True, exist_ok=True)

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]

# ---------------------------------------------------------------------------
# 세션 메타데이터 — index.html 커리큘럼 카드와 동일한 제목/난이도/파트로 통일
# ---------------------------------------------------------------------------
SESSIONS = {
    1:  dict(title="데이터 분석이란, AI 시대의 작업 흐름 + 환경 세팅", diff=1, part_eyebrow="오리엔테이션"),
    2:  dict(title="좋은 데이터의 모양: tidy 데이터와 척도", diff=1, part_eyebrow="PART 01 · 엑셀"),
    3:  dict(title="피벗테이블로 질문에 답하기", diff=2, part_eyebrow="PART 01 · 엑셀"),
    4:  dict(title="실무 함수: VLOOKUP·XLOOKUP과 조건부 집계", diff=2, part_eyebrow="PART 01 · 엑셀"),
    5:  dict(title="중심·산포·분포·박스플롯", diff=2, part_eyebrow="PART 02 · 통계"),
    6:  dict(title="상관 vs 인과, 심슨의 역설", diff=3, part_eyebrow="PART 02 · 통계"),
    7:  dict(title="엑셀을 AI에 올려 자연어로 분석", diff=2, part_eyebrow="PART 03 · AI"),
    8:  dict(title="좋은 분석 프롬프트 설계", diff=3, part_eyebrow="PART 03 · AI"),
    9:  dict(title="AI 답 검증하기: 환각과 계산 오류 잡기", diff=3, part_eyebrow="PART 03 · AI"),
    10: dict(title="Colab과 파이썬 기초", diff=3, part_eyebrow="PART 04 · 파이썬"),
    11: dict(title="Pandas 입문: Series, DataFrame과 필터", diff=3, part_eyebrow="PART 04 · 파이썬"),
    12: dict(title="데이터 정제: 결측, 이상치, 타입, 중복, 인코딩", diff=4, part_eyebrow="PART 04 · 파이썬"),
    13: dict(title="그룹화·집계·재구조화", diff=4, part_eyebrow="PART 04 · 파이썬"),
    14: dict(title="시각화 실전: matplotlib·seaborn과 BI 핸드오프", diff=4, part_eyebrow="PART 04 · 파이썬"),
    15: dict(title="Power BI 설치, 로드, 첫 차트", diff=3, part_eyebrow="PART 05 · BI"),
    16: dict(title="데이터 모델링: 관계, 스타 스키마, 날짜 차원", diff=4, part_eyebrow="PART 05 · BI"),
    17: dict(title="시각화·상호작용·DAX 기초", diff=4, part_eyebrow="PART 05 · BI"),
    18: dict(title="배포와 공유: Looker Studio, Power BI Copilot 선택", diff=4, part_eyebrow="PART 05 · BI"),
    19: dict(title="풀사이클 실습: AI 요약, 파이썬 그래프, BI 1페이지", diff=5, part_eyebrow="PART 06 · 캡스톤"),
    20: dict(title="인사이트 보고: 그래서 뭘 하나", diff=5, part_eyebrow="PART 06 · 캡스톤"),
}

DIFF_LABEL = {1: "입문", 2: "기초", 3: "중급", 4: "심화", 5: "실전"}

SOURCE_DIRS = {
    "curriculum": (ROOT / "01_curriculum", "커리큘럼"),
    "handout":    (ROOT / "03_handouts",   "핸드아웃"),
    "script":     (ROOT / "04_scripts",    "강사대본"),
    "answer":     (ROOT / "06_answers",    "모범답안"),
}


def sid(n: int) -> str:
    return f"S{n:02d}"


def dots_html(level: int) -> str:
    dots = "".join(
        f'<span class="dot{" filled" if i < level else ""}"></span>' for i in range(5)
    )
    return (
        f'<div class="difficulty" title="난이도 {level}">{dots}'
        f'<span class="difficulty-label">{DIFF_LABEL[level]}</span></div>'
    )


def render_markdown(md_text: str) -> str:
    body = markdown.markdown(md_text, extensions=MD_EXTENSIONS)
    # 표/코드블록은 자체 overflow-x:auto 컨테이너로 감싸 본문 가로스크롤 차단
    body = re.sub(r"<table>", '<div class="table-scroll"><table>', body)
    body = re.sub(r"</table>", "</table></div>", body)
    body = re.sub(r"<pre>", '<div class="code-scroll"><pre>', body)
    body = re.sub(r"</pre>", "</pre></div>", body)
    return body


def find_source(n: int, key: str) -> Path:
    dir_path, suffix = SOURCE_DIRS[key]
    candidate = dir_path / f"{sid(n)}_{suffix}.md"
    if not candidate.exists():
        raise FileNotFoundError(candidate)
    return candidate


PAGE_CSS = """
:root{
  --canvas: #010102;
  --surface-1: #0f1011;
  --surface-2: #141516;
  --surface-3: #18191a;
  --surface-4: #191a1b;
  --ink: #f7f8f8;
  --ink-muted: #d0d6e0;
  --ink-subtle: #8a8f98;
  --ink-tertiary: #62666d;
  --primary: #5e6ad2;
  --primary-hover: #828fff;
  --primary-focus: #5e69d1;
  --hairline: #23252a;
  --hairline-strong: #34343a;
  --hairline-tertiary: #3e3e44;
  --success: #27a644;

  --font-display: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-text: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;

  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  --space-xxs: 4px;
  --space-xs: 8px;
  --space-sm: 12px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-xxl: 48px;

  --container: 900px;
}

*, *::before, *::after{ box-sizing: border-box; }
html{ background: var(--canvas); }
body{
  margin:0;
  background: var(--canvas);
  color: var(--ink);
  font-family: var(--font-text);
  font-size: 16px;
  line-height: 1.5;
  letter-spacing: -0.05px;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}
a{ color: inherit; text-decoration: none; }
ul, ol{ margin:0; padding:0; }
h1,h2,h3,h4,p{ margin:0; }

.container{
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 clamp(20px, 5vw, 48px);
}

.eyebrow{
  display:inline-flex;
  align-items:center;
  gap:8px;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.4px;
  color: var(--primary-hover);
}
.eyebrow::before{
  content:"";
  width:6px; height:6px;
  background: var(--primary);
  border-radius: 1px;
  flex-shrink:0;
}

/* ---------- top nav ---------- */
.top-nav{
  position: sticky;
  top: 0;
  z-index: 100;
  height: 64px;
  display:flex;
  align-items:center;
  background: rgba(1,1,2,0.82);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--hairline);
}
.top-nav .container{ display:flex; align-items:center; justify-content:space-between; gap: 24px; max-width: 1280px; }
.brand{ display:flex; align-items:center; gap:10px; font-family: var(--font-display); font-weight:600; font-size:15px; letter-spacing:-0.01em; }
.brand-mark{ width:20px; height:20px; border-radius: 6px; background: var(--primary); flex-shrink:0; position:relative; }
.brand-mark::after{ content:""; position:absolute; inset:6px; border-radius:2px; background: rgba(255,255,255,0.85); }
.back-link{ font-size:14px; color: var(--ink-subtle); display:inline-flex; align-items:center; gap:6px; transition: color .15s ease; }
.back-link:hover{ color: var(--ink); }

/* ---------- session header ---------- */
.session-header{
  padding: var(--space-xxl) 0 var(--space-xl);
  background:
    radial-gradient(ellipse 60% 50% at 82% 0%, rgba(94,106,210,0.16), transparent 60%),
    var(--canvas);
  border-bottom: 1px solid var(--hairline);
}
.session-header-top{
  display:flex;
  align-items:center;
  gap: var(--space-md);
  margin: var(--space-md) 0 var(--space-md);
}
.session-num-badge{
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--primary-hover);
  border: 1px solid var(--hairline-strong);
  border-radius: var(--radius-xs);
  padding: 4px 10px;
}
.difficulty{ display:flex; gap:4px; align-items:center; }
.difficulty .dot{ width:6px; height:6px; border-radius:50%; background: var(--hairline-strong); }
.difficulty .dot.filled{ background: var(--primary); }
.difficulty-label{ font-size:12px; color: var(--ink-tertiary); margin-left:6px; }
.session-header h1{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: clamp(26px, 4vw, 38px);
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--ink);
}

/* ---------- tabs ---------- */
.tabs-bar{
  display:flex;
  gap: 4px;
  padding-top: var(--space-lg);
  border-bottom: 1px solid var(--hairline);
  overflow-x: auto;
}
.tab-btn{
  appearance: none;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--ink-subtle);
  font-family: var(--font-text);
  font-size: 14px;
  font-weight: 500;
  padding: 12px 16px;
  cursor: pointer;
  white-space: nowrap;
  transition: color .15s ease, border-color .15s ease;
}
.tab-btn:hover{ color: var(--ink); }
.tab-btn.active{ color: var(--ink); border-bottom-color: var(--primary); }

.tab-panels{ padding: var(--space-xxl) 0 var(--space-xxl); }
.tab-panel{ display:none; }
.tab-panel.active{ display:block; }

/* ---------- markdown body ---------- */
.markdown-body{ color: var(--ink-muted); font-size: 15.5px; line-height: 1.75; letter-spacing: -0.05px; overflow-wrap: anywhere; word-break: break-word; }
.markdown-body h1{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 26px;
  letter-spacing: -0.015em;
  color: var(--ink);
  margin: 0 0 var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--hairline);
}
.markdown-body h2{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 21px;
  letter-spacing: -0.01em;
  color: var(--ink);
  margin: var(--space-xl) 0 var(--space-sm);
}
.markdown-body h3{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 17px;
  color: var(--ink);
  margin: var(--space-lg) 0 var(--space-xs);
}
.markdown-body h4{
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  margin: var(--space-md) 0 var(--space-xs);
}
.markdown-body p{ margin: 0 0 var(--space-md); }
.markdown-body ul, .markdown-body ol{ margin: 0 0 var(--space-md); padding-left: 1.4em; }
.markdown-body li{ margin-bottom: 6px; }
.markdown-body ul{ list-style: disc; }
.markdown-body ol{ list-style: decimal; }
.markdown-body strong{ color: var(--ink); font-weight: 600; }
.markdown-body em{ color: var(--ink-muted); }
.markdown-body a{ color: var(--primary-hover); text-decoration: underline; text-underline-offset: 2px; }
.markdown-body hr{ border:none; border-top: 1px solid var(--hairline); margin: var(--space-xl) 0; }
.markdown-body blockquote{
  margin: 0 0 var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-left: 2px solid var(--primary);
  background: var(--surface-1);
  color: var(--ink-subtle);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.markdown-body code{
  font-family: var(--font-mono);
  font-size: 0.88em;
  background: var(--surface-2);
  border: 1px solid var(--hairline);
  border-radius: 4px;
  padding: 1px 6px;
  color: var(--primary-hover);
  overflow-wrap: anywhere;
  word-break: break-word;
}
.markdown-body .code-scroll{
  overflow-x: auto;
  margin: 0 0 var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--hairline);
  background: var(--surface-2);
}
.markdown-body pre{
  margin: 0;
  padding: var(--space-md);
  background: transparent;
  border: none;
}
.markdown-body pre code{
  background: none;
  border: none;
  padding: 0;
  color: var(--ink-muted);
  font-size: 13px;
  line-height: 1.6;
  white-space: pre;
}
.markdown-body .table-scroll{
  overflow-x: auto;
  margin: 0 0 var(--space-lg);
  border: 1px solid var(--hairline);
  border-radius: var(--radius-md);
}
.markdown-body table{
  border-collapse: collapse;
  width: 100%;
  min-width: 460px;
  font-size: 13.5px;
}
.markdown-body th, .markdown-body td{
  padding: 10px 14px;
  border-bottom: 1px solid var(--hairline);
  text-align: left;
  white-space: nowrap;
}
.markdown-body thead th{
  background: var(--surface-1);
  color: var(--ink);
  font-weight: 600;
  font-family: var(--font-text);
  font-size: 12.5px;
  letter-spacing: 0.02em;
}
.markdown-body tbody tr:last-child td{ border-bottom: none; }
.markdown-body tbody tr:hover{ background: var(--surface-1); }

/* ---------- pager ---------- */
.session-pager{
  display:flex;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-xl) 0 var(--space-xxl);
  border-top: 1px solid var(--hairline);
  flex-wrap: wrap;
}
.pager-link{
  display:flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--space-md) var(--space-lg);
  border: 1px solid var(--hairline);
  border-radius: var(--radius-lg);
  background: var(--surface-1);
  max-width: 46%;
  transition: border-color .2s ease, background-color .2s ease;
}
.pager-link:hover{ border-color: var(--primary); background: var(--surface-2); }
.pager-link.next{ margin-left: auto; text-align: right; align-items: flex-end; }
.pager-direction{ font-size: 12px; color: var(--ink-tertiary); font-family: var(--font-mono); }
.pager-title{ font-size: 14px; color: var(--ink); font-weight: 500; }
.pager-spacer{ flex: 1; }

footer.site-footer{
  border-top: 1px solid var(--hairline);
  padding: var(--space-xl) 0;
}
footer.site-footer .container{
  display:flex;
  justify-content: space-between;
  align-items:center;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--ink-tertiary);
  font-size: 12px;
}
footer.site-footer a:hover{ color: var(--ink-subtle); }

@media (max-width: 640px){
  .session-header{ padding: var(--space-xl) 0 var(--space-lg); }
  .pager-link{ max-width: 100%; }
  .session-pager{ flex-direction: column; }
  .pager-link.next{ margin-left: 0; text-align: left; align-items: flex-start; }
}
""".strip()

PAGE_JS = """
(function(){
  var tabs = document.querySelectorAll('.tab-btn');
  var panels = document.querySelectorAll('.tab-panel');
  function activate(key, updateHash){
    tabs.forEach(function(btn){
      var on = btn.getAttribute('data-tab') === key;
      btn.classList.toggle('active', on);
    });
    panels.forEach(function(panel){
      var on = panel.getAttribute('data-panel') === key;
      panel.classList.toggle('active', on);
    });
    if (updateHash && history.replaceState){
      history.replaceState(null, '', '#' + key);
    }
  }
  tabs.forEach(function(btn){
    btn.addEventListener('click', function(){
      activate(btn.getAttribute('data-tab'), true);
    });
  });
  var initial = (location.hash || '').replace('#', '');
  var valid = ['curriculum', 'handout', 'script', 'answer'];
  if (valid.indexOf(initial) !== -1){
    activate(initial, false);
  }
})();
""".strip()

TAB_ORDER = [
    ("curriculum", "커리큘럼"),
    ("handout", "핸드아웃"),
    ("script", "강사대본"),
    ("answer", "모범답안"),
]


def build_page(n: int) -> str:
    meta = SESSIONS[n]
    title = meta["title"]
    diff = meta["diff"]
    part_eyebrow = meta["part_eyebrow"]
    sess_id = sid(n)

    rendered = {}
    for key, _ in TAB_ORDER:
        src = find_source(n, key)
        md_text = src.read_text(encoding="utf-8")
        rendered[key] = render_markdown(md_text)

    tab_buttons = "\n".join(
        f'<button class="tab-btn{" active" if i == 0 else ""}" data-tab="{key}" '
        f'role="tab" aria-selected="{"true" if i == 0 else "false"}">{label}</button>'
        for i, (key, label) in enumerate(TAB_ORDER)
    )
    tab_panels = "\n".join(
        f'<section class="tab-panel markdown-body{" active" if i == 0 else ""}" '
        f'data-panel="{key}" aria-label="{label}">\n{rendered[key]}\n</section>'
        for i, (key, label) in enumerate(TAB_ORDER)
    )

    prev_n, next_n = n - 1, n + 1
    prev_html = ""
    next_html = ""
    if prev_n in SESSIONS:
        prev_html = (
            f'<a class="pager-link prev" href="./{sid(prev_n)}.html">'
            f'<span class="pager-direction">&larr; 이전 차시</span>'
            f'<span class="pager-title">{sid(prev_n)} · {html.escape(SESSIONS[prev_n]["title"])}</span></a>'
        )
    if next_n in SESSIONS:
        next_html = (
            f'<a class="pager-link next" href="./{sid(next_n)}.html">'
            f'<span class="pager-direction">다음 차시 &rarr;</span>'
            f'<span class="pager-title">{sid(next_n)} · {html.escape(SESSIONS[next_n]["title"])}</span></a>'
        )
    if not prev_html:
        prev_html = '<span class="pager-spacer"></span>'
    if not next_html:
        next_html = '<span class="pager-spacer"></span>'

    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{sess_id}. {html.escape(title)} · 데이터 리터러시 with AI</title>
<meta name="description" content="{sess_id}차시: {html.escape(title)} — 커리큘럼·핸드아웃·강사대본·모범답안." />
<style>
{PAGE_CSS}
</style>
</head>
<body>

<nav class="top-nav">
  <div class="container">
    <div class="brand"><span class="brand-mark"></span>데이터 리터러시 with AI</div>
    <a class="back-link" href="../index.html#curriculum">&larr; 커리큘럼으로</a>
  </div>
</nav>

<header class="session-header">
  <div class="container">
    <div class="eyebrow">{part_eyebrow}</div>
    <div class="session-header-top">
      <span class="session-num-badge">{sess_id}</span>
      {dots_html(diff)}
    </div>
    <h1>{html.escape(title)}</h1>
  </div>
  <div class="container">
    <div class="tabs-bar" role="tablist">
{tab_buttons}
    </div>
  </div>
</header>

<main>
  <div class="tab-panels container">
{tab_panels}
  </div>

  <nav class="session-pager container">
    {prev_html}
    {next_html}
  </nav>
</main>

<footer class="site-footer">
  <div class="container">
    <span>데이터 리터러시 with AI · {sess_id} 차시</span>
    <a href="../index.html#curriculum">전체 커리큘럼으로</a>
  </div>
</footer>

<script>
{PAGE_JS}
</script>

</body>
</html>
"""
    return page


def main():
    for n in range(1, 21):
        out_path = SESSION_OUT / f"{sid(n)}.html"
        out_path.write_text(build_page(n), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
