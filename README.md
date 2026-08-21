# Ant evolution v0.3 prototype

This repository contains a deterministic, headless prototype about balancing
immediate prosperity, evolutionary flexibility, specialization, and preparation
for a forecast ecological disaster.

The current experiment lasts five rounds. Every size sees six trait cards, but
larger species retain fewer of them. Cards build Daybreak-style evolutionary
columns: covered cards keep their tags, while only the top card can activate.
Most actions generate prosperity, a one-round disaster shield, or card flow.

## Play

```powershell
python -m ant_game.cli --seed 42
```

The disaster is selected from the seed. To list or fix it explicitly:

```powershell
python -m ant_game.cli --list-environments
python -m ant_game.cli --seed 42 --environment desert_heat_wave
```

Commands during the action phase are:

```text
play CARD COLUMN
support CARD COLUMN
activate COLUMN [OPTION]
card CARD
status
help
done
```

Columns are numbered from 1. Playing a card as support permanently gives up its
action in exchange for its tags. The CLI also accepts the Japanese command
aliases `置く`, `支援`, `起動`, `カード`, `状態`, and `終了`. Press Enter at the
retention prompt to keep no cards.

## Simulate and inspect

```powershell
python -m ant_game.simulation --games 1000 --include-exploits
python -m ant_game.simulation --history reactive --history-seed 42
python -m pytest -q
```

`GAME_DESIGN.md` is the current source of truth. Historical v0.1 rules are
archived under `docs/archive/`; experiment results and accepted decisions are
recorded in `PLAYTEST_LOG.md` and `DECISIONS.md`.
