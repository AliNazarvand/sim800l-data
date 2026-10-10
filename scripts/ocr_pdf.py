#!/usr/bin/env python3
"""OCR wrapper using tesseract."""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / "sources" / "originals"
OUT = ROOT / "sources" / "extracted" / "ocr"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    if not shutil.which("tesseract"):
        print("tesseract not found in PATH.")
        return 2
    pdfs = sorted(ORIG.glob("*.pdf")) + sorted(ORIG.glob("*.PDF"))
    if not pdfs:
        print(f"No PDFs in {ORIG}")
        return 1
    for pdf in pdfs:
        out_base = OUT / (pdf.stem + ".ocr")
        print(f"OCR {pdf.name}")
        try:
            subprocess.run(["tesseract", str(pdf), str(out_base), "-l", "eng"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"  OCR failed: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())