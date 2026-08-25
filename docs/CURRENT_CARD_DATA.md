# Current card data snapshot

Updated: 2026-08-25

This repository's Python engine still implements the preserved v0.1 prototype. The current card-design data for the next implementation is stored separately under `data/` and should not be reconstructed from `ant_game/content.py`.

## Authoritative content files for the current card pass

- `data/trait_cards_v0.16/TRAIT_CARD_DATA_v0.16_COMPLETE.json` — current 108-card trait deck after running the restore script.
- `data/trait_cards_v0.16/TRAIT_CARD_PATCH_v0.16_BALANCE.json` — delta from v0.15 to v0.16.

## v0.16 balance decisions

### Requirement-3 + shield-3 completed cards

The default balance rule is now:

- requirement total 3 + shield 3 is too efficient;
- reduce the completed shield to 2 while keeping prosperity 3;
- exception: a completed card requiring `形態3` may keep shield 3 because early Morphology supply is intentionally thinner.

Applied changes:

- `pheidole_supermajor_program`: prosperity 3 + raid shield 2.
- `megaponera_field_medicine`: prosperity 3 + sanitation shield 2.
- `colobopsis_last_defense`: prosperity 3 + raid shield 2.
- `acromyrmex_antibiotic_garden`: prosperity 3 + sanitation shield 2.
- `paraponera_poneratoxin`: Morphology-3 exception; prosperity 3 + raid shield 3 option remains unchanged.

### Completed forms must do more than score

A completed-form card should not end at a flat prosperity number. It should have a biologically grounded secondary effect, or remain deferred until such an effect is found.

The four remaining prosperity-only completed forms were changed:

- `pheidole_bite_muscle`: Chemistry 2 + Sociality 2 -> prosperity 3 + raid shield 3.
- `melissotarsus_living_wood_galleries`: Nesting 2 + Morphology 2 -> prosperity 5 + reduce direct environment prosperity loss by 2.
- `allomerus_fungal_trap_gallery`: Nesting 3 + Sociality 2 -> prosperity 5 + raid shield 2.
- `formica_thatch_thermostat`: Nesting 3 -> prosperity 5 + reduce direct environment prosperity loss by 2.

The Melissotarsus payoff is intentionally above the ordinary requirement-4 baseline because it contains a Morphology requirement.

### Morphology baseline

`atta_large_colony_worker_polymorphism` remains an unconditional foundation card with:

- Morphology 2;
- no requirement;
- prosperity 4;
- sanitation vulnerability 1.

This is intentionally strong to prevent the stable choice from becoming "never activate it" and to supply early Morphology, which has no initial trait card.

## Verification after the pass

- Trait card count: 108.
- The only requirement-total-3 completed option that still has shield 3 is the intended `形態3` Paraponera exception.
- No completed-form card in v0.16 has only a flat prosperity effect with no secondary mechanic.

## Implementation note

Do not silently translate these JSON cards back into the legacy v0.1 tag/evolution-load model. The current card schema includes five design tags, completion requirements, raid/sanitation shields, size-dependent effects, push-out effects, environment prosperity-loss reduction, and sanitation vulnerabilities. The next engine pass should consume or faithfully model this data explicitly.
