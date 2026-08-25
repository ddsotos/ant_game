#!/usr/bin/env python3
"""Restore and verify the current v0.16 trait-card JSON snapshot."""
from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTS = [HERE / f"TRAIT_CARD_DATA_v0.16_COMPLETE.json.gz.b64.part{i:02d}" for i in range(1, 6)]
OUTPUT = HERE / "TRAIT_CARD_DATA_v0.16_COMPLETE.json"
EXPECTED_SHA256 = "7d63c54845081860df9493992938407720230059b6641c3f4653baa8428f82d4"

chunks = [part.read_text(encoding="ascii").strip() for part in PARTS]
# part01 and part03 carry one repository transport sentinel at the boundary.
chunks[0] = chunks[0][:-1]
chunks[2] = chunks[2][:-1]
payload = "".join(chunks)
raw = gzip.decompress(base64.b64decode(payload))
actual = hashlib.sha256(raw).hexdigest()
if actual != EXPECTED_SHA256:
    raise SystemExit(f"trait data checksum mismatch: {actual}")
OUTPUT.write_bytes(raw)
print(OUTPUT)
