#!/usr/bin/env python3
"""Extract text from PDFs into sources/extracted/."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / "sources" / "originals"
OUT = ROOT / "sources" / "extracted"
OUT.mkdir(parents=True, exist_ok=True)

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("Install pypdf: pip install pypdf")
        sys.exit(2)


def extract_one(pdf: Path) -> None:
    target = OUT / (pdf.stem + ".txt")
    print(f"Extracting {pdf.name} -> {target.name}")
    reader = PdfReader(str(pdf))
    buf = []
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception as e:
            txt = f"[page {i+1} error: {e}]"
        buf.append(f"\n===== PAGE {i+1} =====\n{txt}")
    target.write_text("".join(buf), encoding="utf-8")
    print(f"  pages: {len(reader.pages)} chars: {sum(len(b) for b in buf)}")


def main() -> int:
    pdfs = sorted(ORIG.glob("*.pdf")) + sorted(ORIG.glob("*.PDF"))
    if not pdfs:
        print(f"No PDFs in {ORIG}")
        return 1
    for p in pdfs:
        extract_one(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())