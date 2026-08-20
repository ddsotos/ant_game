"""Minimal interactive CLI for playing the headless v0.1 rules."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from .content import EVENTS, TRAITS
from .engine import GameEngine
from .models import EvolutionChoice, GameState, Size


class HumanPolicy:
    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.ask = input_fn
        self.say = output_fn

    def _show_last_round(self, state: GameState) -> None:
        if not state.history:
            return
        row = state.history[-1]
        stage = "shock" if row.event_stage is None else str(row.event_stage)
        self.say(
            f"R{row.round_number}: {row.event_name} [{stage}]  size={row.size.name} "
            f"damage={row.damage} growth={row.growth_cost} delta={row.actual_prosperity_delta:+d} "
            f"score={row.total_prosperity} draw={row.evolution_draw_count}"
        )

    def choose_size(self, state: GameState, engine: GameEngine) -> Size:
        self._show_last_round(state)
        self.say(f"\nChoose size (score={state.prosperity}, load={engine.evolution_load(state)}):")
        legal = engine.legal_sizes(state)
        for size in legal:
            growth = engine.growth_cost_per_step if size > state.size else 0
            draw = engine.draw_count(state, size)
            self.say(
                f"  {size.name.lower():6} prosperity={size.prosperity} "
                f"draw={draw} growth_cost={growth}"
            )
        names = {size.name.lower(): size for size in legal}
        while True:
            answer = self.ask("size> ").strip().lower()
            if answer in names:
                return names[answer]
            self.say(f"Choose one of: {', '.join(names)}")

    def choose_latents(self, state, event, stage, engine):
        label = "shock" if stage is None else str(stage)
        self.say(f"Event revealed: {event.name} [{label}]")
        eligible = [
            held.card_id
            for held in state.traits
            if engine.can_activate(state, held.card_id, event, stage)
        ]
        if not eligible:
            return ()
        self.say("Eligible latent traits: " + ", ".join(eligible))
        while True:
            raw = self.ask("activate comma-separated ids (blank=none)> ").strip()
            chosen = tuple(item.strip() for item in raw.split(",") if item.strip())
            if len(chosen) == len(set(chosen)) and set(chosen) <= set(eligible):
                return chosen
            self.say("Choose only eligible ids, without duplicates.")

    def choose_evolution(self, state, candidates, budget, engine):
        self.say(f"After event: score={state.prosperity}; evolution budget={budget}")
        for card_id in candidates:
            card = engine.traits[card_id]
            latent = " latent" if card.latent else ""
            self.say(
                f"  {card_id}: {card.name} cost={card.play_cost} "
                f"load={card.evolution_load}{latent} — {card.text}"
            )
        while True:
            raw = self.ask("acquire up to 2 comma-separated ids (blank=none)> ").strip()
            chosen = tuple(item.strip() for item in raw.split(",") if item.strip())
            valid = (
                len(chosen) <= 2
                and len(chosen) == len(set(chosen))
                and set(chosen) <= set(candidates)
                and sum(engine.traits[item].play_cost for item in chosen) <= budget
            )
            if valid:
                break
            self.say("Invalid ids, duplicate choice, card limit, or total play cost.")
        needed = max(0, len(state.traits) + len(chosen) - engine.trait_slots)
        if not needed:
            return EvolutionChoice(chosen, ())
        held_ids = {held.card_id for held in state.traits}
        self.say("Held traits: " + ", ".join(sorted(held_ids)))
        while True:
            raw = self.ask(f"discard exactly {needed} comma-separated held ids> ").strip()
            discarded = tuple(item.strip() for item in raw.split(",") if item.strip())
            if len(discarded) == needed and len(set(discarded)) == needed and set(discarded) <= held_ids:
                return EvolutionChoice(chosen, discarded)
            self.say("Discard the exact required number of distinct held traits.")

    def choose_shed(self, state, engine):
        self.say(f"After event: score={state.prosperity}; evolution draw is zero.")
        held = {item.card_id for item in state.traits}
        if not held:
            return None
        self.say("Held traits: " + ", ".join(sorted(held)))
        while True:
            answer = self.ask("shed one trait to reduce future load (blank=none)> ").strip()
            if not answer:
                return None
            if answer in held:
                return answer
            self.say("Choose a held trait id or leave blank.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    engine = GameEngine(TRAITS, EVENTS, seed=args.seed)
    policy = HumanPolicy()
    print(f"Ant evolution v0.1 — seed {args.seed}, {engine.rounds} rounds")
    state = engine.run(policy)
    policy._show_last_round(state)
    print(f"\nFinal prosperity: {state.prosperity}")
    print("Final traits: " + (", ".join(item.card_id for item in state.traits) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
