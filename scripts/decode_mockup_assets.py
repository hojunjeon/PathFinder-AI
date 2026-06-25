from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "mockups" / "assets" / "_incoming"
OUT = ROOT / "docs" / "mockups" / "assets"

for source in BASE.glob("*.b64"):
    target = OUT / source.stem
    target.write_bytes(base64.b64decode(source.read_text(encoding="ascii")))
    print(target.relative_to(ROOT))
