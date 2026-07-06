#!/usr/bin/env python3
"""덱 슬라이드 오버플로우/가장자리 침범 자동 탐지.
각 덱 PDF의 각 페이지를 렌더해 바깥 여백 밴드에 배경 아닌 콘텐츠 픽셀이 있으면 오버플로우로 플래그.
실행: python3 site/overflow_gate.py [S01 S02 ...]
"""
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "pdf"
# 배경색(프린트 슬라이드 #06070a, 캔버스 #010102) 근처는 '빈 공간'으로 간주
BG_MAX = 22           # 채널 평균이 이 이하이면 배경
MARGIN_X = 0.028      # 좌우 2.8% 밴드
MARGIN_TOP = 0.030
MARGIN_BOT = 0.045    # 하단은 HUD 없으니 여유
MIN_HITS = 40         # 밴드 내 콘텐츠 픽셀 수 임계(노이즈 무시)


def check_page(pm):
    w, h = pm.width, pm.height
    n = pm.n
    buf = pm.samples
    mx, mt, mb = int(w * MARGIN_X), int(h * MARGIN_TOP), int(h * MARGIN_BOT)

    def is_content(x, y):
        o = (y * w + x) * n
        return (buf[o] + buf[o + 1] + buf[o + 2]) / 3 > BG_MAX

    hits = {"left": 0, "right": 0, "top": 0, "bottom": 0}
    step = 2
    for y in range(0, h, step):
        for x in range(0, mx, step):
            if is_content(x, y):
                hits["left"] += 1
        for x in range(w - mx, w, step):
            if is_content(x, y):
                hits["right"] += 1
    for x in range(0, w, step):
        for y in range(0, mt, step):
            if is_content(x, y):
                hits["top"] += 1
        for y in range(h - mb, h, step):
            if is_content(x, y):
                hits["bottom"] += 1
    return {k: v for k, v in hits.items() if v > MIN_HITS}


def main():
    targets = sys.argv[1:] or [f"S{i:02d}" for i in range(1, 21)]
    flagged = []
    for sid in targets:
        p = PDF / f"{sid}.pdf"
        if not p.exists():
            continue
        d = fitz.open(p)
        for i in range(d.page_count):
            pm = d[i].get_pixmap(dpi=70)
            edges = check_page(pm)
            if edges:
                flagged.append((sid, i + 1, edges))
        d.close()
    if not flagged:
        print("오버플로우 없음 — 전 슬라이드 여백 안에 안착")
        return 0
    print(f"오버플로우 의심 {len(flagged)}건:")
    for sid, pg, e in flagged:
        print(f"  {sid} 슬라이드{pg}: {e}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
