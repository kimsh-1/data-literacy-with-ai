#!/usr/bin/env python3
"""덱 JSON들에서 실제 사용된 문자만 모아 Pretendard를 초경량 서브셋한다.
-> site/fonts/pretendard-deck-subset.woff2  (덱 전체가 공유, PDF 임베딩 용량 최소화)
실행: python3 site/subset_font.py
"""
import json
from pathlib import Path

from fontTools import subset

ROOT = Path(__file__).resolve().parent
DECKS = ROOT / "decks"
SRC = ROOT.parent / "assets/video-project/assets/fonts/PretendardVariable.woff2"
OUTDIR = ROOT / "fonts"


def collect_chars():
    chars = set()
    for f in sorted(DECKS.glob("S*.json")):
        chars |= set(f.read_text(encoding="utf-8"))
    # 덱 UI 고정 문자열(브랜드/힌트/카운터) + 안전 여유(ASCII, 기본 구두점)
    chars |= set("데이터 리터러시 with AI자료로 돌아가기화살표스페이스이동전체화면정리다음 차시난이도")
    chars |= set("0123456789")
    for c in range(0x20, 0x7F):
        chars.add(chr(c))
    chars |= set("·—–…“”‘’→←")
    return "".join(sorted(chars))


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    text = collect_chars()
    out = OUTDIR / "pretendard-deck-subset.woff2"
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.layout_features = ["*"]
    opts.name_IDs = []
    opts.notdef_outline = True
    opts.recalc_bounds = True
    font = subset.load_font(str(SRC), opts)
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(text=text)
    subsetter.subset(font)
    subset.save_font(font, str(out), opts)
    kb = out.stat().st_size / 1024
    print(f"글리프 {len(set(text))}자 -> {out.name}  {kb:.0f} KB (원본 {SRC.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
