#!/usr/bin/env python3
"""오버플로우 자동 분할 — 넘치는 슬라이드를 다음 장으로 나눈다(자르지 않음).
슬라이드를 하나씩 자연 높이로 렌더해 720px를 넘으면 분할, 반복 수렴.
실행: python3 site/paginate.py [S01 ...]
"""
import copy
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
DECKS = ROOT / "decks"
sys.path.insert(0, str(ROOT))
import build_decks as bd  # noqa: E402
from render_pdfs import BIN  # noqa: E402  (자동탐색된 크롬 경로)

PAGE_H = 720
TOL = 14            # 허용 여유(px)
MAX_ITERS = 40


def slide_height(sd):
    """단일 슬라이드를 큰 창에 렌더해 콘텐츠 실제 높이(px)를 측정."""
    html = bd.standalone_slide(sd)
    with tempfile.TemporaryDirectory() as td:
        h = Path(td) / "s.html"
        png = Path(td) / "s.png"
        h.write_text(html, encoding="utf-8")
        subprocess.run([str(BIN), "--headless", "--no-sandbox", "--disable-gpu",
                        "--hide-scrollbars", "--window-size=1280,4000",
                        f"--screenshot={png}", h.as_uri()],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        if not png.exists():
            return 0
        im = Image.open(png).convert("L")
        w, ht = im.size
        px = im.load()
        # 바닥에서 위로 스캔, 배경(어두움) 아닌 첫 행 = 콘텐츠 높이
        for y in range(ht - 1, -1, -1):
            row_has = any(px[x, y] > 22 for x in range(0, w, 6))
            if row_has:
                return y + 1
        return 0


def as_list(x):
    return x if isinstance(x, list) else ([x] if x else [])


def split_slide(s):
    t = s.get("type")
    rows = s.get("rows")
    exl = as_list(s.get("explain"))
    if t == "table" and rows and len(rows) > 3:
        h = math.ceil(len(rows) / 2)
        a = copy.deepcopy(s); a["rows"] = rows[:h]
        b = copy.deepcopy(s); b["rows"] = rows[h:]
        b["heading"] = (s.get("heading", "") + " (이어서)").strip(); b.pop("explain", None); b.pop("note", None)
        return [a, b]
    if len(exl) >= 2:
        h = math.ceil(len(exl) / 2)
        a = copy.deepcopy(s); a["explain"] = exl[:h]
        b = {"type": "note", "heading": s.get("heading", ""), "cont": True, "explain": exl[h:]}
        return [a, b]
    if len(exl) == 1 and len(str(exl[0])) > 120:
        sents = re.split(r"(?<=다\.)\s+", str(exl[0]))
        if len(sents) >= 2:
            h = math.ceil(len(sents) / 2)
            a = copy.deepcopy(s); a["explain"] = [" ".join(sents[:h])]
            b = {"type": "note", "heading": s.get("heading", ""), "cont": True, "explain": [" ".join(sents[h:])]}
            return [a, b]
    bl = s.get("bullets")
    if bl and len(bl) > 2:
        h = math.ceil(len(bl) / 2)
        a = copy.deepcopy(s); a["bullets"] = bl[:h]
        b = copy.deepcopy(s); b["bullets"] = bl[h:]; b.pop("body", None); b.pop("explain", None)
        b["heading"] = (s.get("heading", "") + " (이어서)").strip()
        return [a, b]
    if t == "objectives" and s.get("items") and len(s["items"]) > 3:
        items = s["items"]; h = math.ceil(len(items) / 2)
        a = copy.deepcopy(s); a["items"] = items[:h]
        b = copy.deepcopy(s); b["items"] = items[h:]
        b["heading"] = (s.get("heading", "") + " (이어서)").strip()
        return [a, b]
    return None


def paginate(sid):
    jf = DECKS / f"{sid}.json"
    spec = json.loads(jf.read_text(encoding="utf-8"))
    splits, stuck = 0, []
    for _ in range(MAX_ITERS):
        heights = [slide_height(s) for s in spec["slides"]]
        over = [i for i, h in enumerate(heights) if h > PAGE_H + TOL]
        over = [i for i in over if i not in stuck]
        if not over:
            break
        idx = over[0]
        parts = split_slide(spec["slides"][idx])
        if not parts:
            stuck.append(idx)
            continue
        spec["slides"] = spec["slides"][:idx] + parts + spec["slides"][idx + 1:]
        splits += 1
    jf.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return splits, sorted(stuck)


def main():
    targets = sys.argv[1:] or sorted(p.stem for p in DECKS.glob("S*.json"))
    grand = 0
    for sid in targets:
        n, stuck = paginate(sid)
        grand += n
        msg = f"[{sid}] 분할 {n}회"
        if stuck:
            msg += f" · 미해결 {stuck}"
        print(msg, flush=True)
    print(f"=== 총 {grand}회 분할 ===")


if __name__ == "__main__":
    main()
