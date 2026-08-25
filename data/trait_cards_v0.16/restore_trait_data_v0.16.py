#!/usr/bin/env python3
"""Restore the current v0.16 trait-card JSON from repository-safe text parts."""
from __future__ import annotations

import base64
import gzip
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTS = [HERE / f"TRAIT_CARD_DATA_v0.16_COMPLETE.json.gz.b64.part{i:02d}" for i in range(1, 6)]
OUTPUT = HERE / "TRAIT_CARD_DATA_v0.16_COMPLETE.json"

payload = "".join(part.read_text(encoding="ascii").strip() for part in PARTS)
raw = gzip.decompress(base64.b64decode(payload))
OUTPUT.write_bytes(raw)
print(OUTPUT)
