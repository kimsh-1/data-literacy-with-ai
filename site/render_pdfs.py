#!/usr/bin/env python3
"""덱 HTML -> 경량 PDF 렌더. site/session/S{nn}_deck.html -> site/pdf/S{nn}.pdf

- chrome-headless-shell로 print-to-pdf (프린트 CSS가 그라디언트 글로우 제거 -> 벡터 텍스트만)
- PyMuPDF로 재저장(garbage collect + deflate)해 추가 압축
실행: python3 site/render_pdfs.py [S01 S02 ...]
"""
import os
import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent
SESS = ROOT / "session"
PDF = ROOT / "pdf"


def _find_chrome():
    import glob
    cache = Path.home() / ".cache/ms-playwright"
    for pat in ("chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
                "chromium-*/chrome-linux/chrome"):
        hits = sorted(glob.glob(str(cache / pat)))
        if hits:
            return hits[-1]
    for p in ("/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
              "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"):
        if Path(p).exists():
            return p
    raise FileNotFoundError("헤드리스 크롬을 찾지 못함 — npx playwright install chromium-headless-shell 필요")


BIN = _find_chrome()


def render(sid):
    src = SESS / f"{sid}_deck.html"
    if not src.exists():
        return None, "html 없음"
    raw = PDF / f".{sid}.raw.pdf"
    out = PDF / f"{sid}.pdf"
    cmd = [str(BIN), "--headless", "--no-sandbox", "--disable-gpu",
           "--no-pdf-header-footer", f"--print-to-pdf={raw}", src.as_uri()]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    if not raw.exists():
        return None, f"렌더 실패(rc={r.returncode})"
    raw_kb = raw.stat().st_size / 1024
    d = fitz.open(raw)
    d.save(out, garbage=4, deflate=True, deflate_images=True, clean=True)
    d.close()
    raw.unlink(missing_ok=True)
    return (out.stat().st_size / 1024, raw_kb), None


def main():
    PDF.mkdir(parents=True, exist_ok=True)
    targets = sys.argv[1:] or [f"S{i:02d}" for i in range(1, 21)]
    total = 0.0
    rows = []
    for sid in targets:
        res, err = render(sid)
        if err:
            rows.append(f"  {sid}: {err}")
            continue
        final_kb, raw_kb = res
        total += final_kb
        rows.append(f"  {sid}: {final_kb:6.0f} KB  (raw {raw_kb:5.0f} -> deflate)")
    print("\n".join(rows))
    print(f"=== 합계 {total/1024:.2f} MB / {len([t for t in targets])} decks ===")


if __name__ == "__main__":
    main()
