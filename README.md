# Ant evolution v0.1 prototype

This repository contains a deterministic, headless game prototype focused on the tension between immediate prosperity and evolutionary flexibility.

The current code implements the archived v0.1 loop, which was rated **promising** after three consecutive independent reviews. `GAME_DESIGN.md` now defines the next, substantially revised prototype—hands, prosperity-power multipliers, extinction damage, and a hidden mass-extinction deadline—and is not implemented or validated yet.

## Play

```powershell
python -m ant_game.cli --seed 42
```

The CLI is intentionally plain. Enter size names and card IDs shown by each prompt.

## Simulate and inspect

```powershell
python -m ant_game.simulation --games 1000 --include-exploits
python -m ant_game.simulation --history warning_perimeter_selective_latent --history-seed 42
python -m pytest -q
```

The current design source of truth is `GAME_DESIGN.md`. `CULMINATION_TRAITS_EXPERIMENTS.md` is an incorporated experiment brief for future high-impact trait comparisons, not an implemented rule. The rules implemented by this CLI are archived in `docs/archive/2026-08-20-v0.1-promising/GAME_DESIGN.md`; accepted historical changes are in `DECISIONS.md`, and measured iterations are in `PLAYTEST_LOG.md`.
