# Current trait-card data

The Python engine under `ant_game/` is the preserved v0.1 prototype and does not yet implement the current five-tag / 3×5 tableau rules. Do not silently translate this data back into the legacy v0.1 model.

Current card-design snapshot:

- `TRAIT_CARD_PATCH_v0.16_BALANCE.json` — human-readable delta from v0.15.
- `TRAIT_CARD_DATA_v0.16_COMPLETE.json.gz.b64.part01` … `part05` — lossless compressed representation of the complete 108-card v0.16 JSON.
- `restore_trait_data_v0.16.py` — restores `TRAIT_CARD_DATA_v0.16_COMPLETE.json` exactly.

Restore with:

```bash
python data/trait_cards_v0.16/restore_trait_data_v0.16.py
```

The balance rationale and verification notes are in `docs/CURRENT_CARD_DATA.md`.
