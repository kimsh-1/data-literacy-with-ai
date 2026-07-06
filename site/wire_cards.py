#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
index.html의 커리큘럼 카드(S01 배너 + S02~S20 session-card)를
./session/S{nn}.html 로 가는 <a> 링크로 배선한다. 카드 레이아웃(클래스·자식
구조)은 그대로 유지하고 바깥 태그만 div -> a 로 바꾼다.

재실행: python3 site/wire_cards.py
"""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
INDEX = SITE / "index.html"


def wrap_block(text: str, open_tag: str, extract_id, href_fmt) -> str:
    """text 안의 모든 open_tag 발생 지점을 찾아, 중첩 <div>/</div> 깊이를
    추적해 매칭되는 닫는 </div>를 찾고, 열고/닫는 태그를 <a ...>/</a> 로
    치환한다."""
    out = []
    pos = 0
    while True:
        start = text.find(open_tag, pos)
        if start == -1:
            out.append(text[pos:])
            break
        out.append(text[pos:start])

        # 이 블록의 매칭되는 닫는 </div> 찾기 (open_tag 자체가 depth=1)
        depth = 1
        cursor = start + len(open_tag)
        tag_re = re.compile(r"<div\b|</div>")
        close_start = close_end = None
        for m in tag_re.finditer(text, cursor):
            if m.group() == "</div>":
                depth -= 1
                if depth == 0:
                    close_start, close_end = m.start(), m.end()
                    break
            else:
                depth += 1
        if close_start is None:
            raise RuntimeError(f"매칭되는 닫는 태그를 찾지 못함: {open_tag} at {start}")

        block = text[start:close_end]
        block_id = extract_id(block)
        href = href_fmt(block_id)

        # 블록 내부: open_tag(<div ...>) -> <a ...href...>, 마지막 </div> -> </a>
        inner_open_len = len(open_tag)
        assert open_tag.startswith("<div")
        new_open = "<a" + open_tag[len("<div"):-1] + f' href="{href}">'
        new_block = new_open + block[inner_open_len:-len("</div>")] + "</a>"
        out.append(new_block)

        pos = close_end

    return "".join(out)


def extract_session_num(block: str) -> str:
    m = re.search(r'<span class="session-num">S(\d\d)</span>', block)
    if not m:
        raise RuntimeError("session-num을 찾지 못함")
    return m.group(1)


def main():
    text = INDEX.read_text(encoding="utf-8")
    before = text

    # S01: curriculum-intro-banner (한 번만 등장, div 태그 개수 1개: 자기 자신)
    text = wrap_block(
        text,
        '<div class="curriculum-intro-banner reveal">',
        extract_id=lambda block: "01",
        href_fmt=lambda nn: f"./session/S{nn}.html",
    )

    # S02~S20: session-card
    text = wrap_block(
        text,
        '<div class="session-card reveal">',
        extract_id=extract_session_num,
        href_fmt=lambda nn: f"./session/S{nn}.html",
    )

    if text == before:
        raise RuntimeError("변경 사항 없음 — 배선 실패")

    INDEX.write_text(text, encoding="utf-8")
    n_links = text.count('href="./session/S')
    print(f"wired {n_links} card links into {INDEX}")


if __name__ == "__main__":
    main()
