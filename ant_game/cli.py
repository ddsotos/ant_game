"""Minimal interactive CLI for the five-round v0.3 prototype."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from .content import EVENTS, TRAITS
from .engine import GameEngine, InvalidDecision
from .models import GameState, Size


class HumanPolicy:
    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.ask = input_fn
        self.say = output_fn

    def choose_size(self, state: GameState, engine: GameEngine) -> Size:
        context = state.current_round
        assert context is not None
        event = engine.current_event(state)
        self.say(
            f"\nR{context.round_number}/5  {event.name} stage {context.stage}  "
            f"raw damage={event.stage_damage.get(context.stage, 0)}"
        )
        self.say(
            f"score={state.prosperity} cumulative_damage={state.cumulative_damage}/"
            f"{engine.extinction_threshold} hand={len(state.hand)}/{engine.hand_limit}"
        )
        eligible = {item.id for item in engine.eligible_extremes(state)}
        self.say("public environment adaptations:")
        for item in engine.public_extremes(state):
            status = "eligible" if item.id in eligible else "locked"
            self.say(
                f"  {item.id}: {item.name} [{status}; "
                f"{self._requirements(item.required_root_tags)}] — {item.text}"
            )
        legal = engine.legal_sizes(state)
        for size in legal:
            self.say(
                f"  {size.name.lower():6} multiplier=x{size.prosperity_multiplier} "
                f"retention={engine.retention_curve[size]}"
            )
        by_name = {size.name.lower(): size for size in legal}
        while True:
            answer = self.ask("size> ").strip().lower()
            if answer in by_name:
                return by_name[answer]
            self.say("choose: " + ", ".join(by_name))

    def choose_retained(
        self,
        state: GameState,
        candidates: tuple[str, ...],
        engine: GameEngine,
    ) -> tuple[str, ...]:
        self.say("normal candidates:")
        for instance_id in candidates:
            card = engine.traits[instance_id]
            requirements = self._requirements(card.activation_requirements)
            self.say(
                f"  {instance_id}: {card.name} [{', '.join(sorted(card.root_tags))}] "
                f"requires {requirements} — {card.text}"
            )
        extremes = engine.eligible_extremes(state)
        if extremes:
            self.say("environment adaptations available (use normal retention):")
            for item in extremes:
                self.say(
                    f"  {item.id}: {item.name} requires "
                    f"{self._requirements(item.required_root_tags)} — {item.text}"
                )
        available = set(candidates) | {item.id for item in extremes}
        limit = min(engine.retention_limit(state), engine.hand_limit - len(state.hand))
        while True:
            raw = self.ask(f"keep up to {limit} comma-separated ids (blank=none)> ").strip()
            chosen = tuple(item.strip() for item in raw.split(",") if item.strip())
            if len(chosen) <= limit and len(chosen) == len(set(chosen)) and set(chosen) <= available:
                return chosen
            self.say("invalid, duplicate, unavailable, or too many card ids")

    def take_actions(self, state: GameState, engine: GameEngine) -> None:
        self.say("actions: play CARD COLUMN | support CARD COLUMN | activate COLUMN [OPTION] | status | done")
        self.show_status(state, engine)
        while True:
            parts = self.ask("action> ").strip().lower().split()
            if not parts:
                continue
            try:
                if parts[0] == "done":
                    return
                if parts[0] == "status":
                    self.show_status(state, engine)
                elif parts[0] == "play" and len(parts) == 3:
                    engine.play_card(state, parts[1], int(parts[2]) - 1)
                elif parts[0] == "support" and len(parts) == 3:
                    engine.insert_support(state, parts[1], int(parts[2]) - 1)
                elif parts[0] == "activate" and len(parts) in (2, 3):
                    option = int(parts[2]) - 1 if len(parts) == 3 else 0
                    engine.activate(state, int(parts[1]) - 1, option)
                else:
                    self.say("unknown command")
                    continue
                self.show_status(state, engine)
            except (InvalidDecision, ValueError) as exc:
                self.say(f"invalid action: {exc}")

    def show_status(self, state: GameState, engine: GameEngine) -> None:
        context = state.current_round
        shield = sum(item.amount for item in context.shields) if context else 0
        prosperity = context.prosperity_base if context else 0
        self.say(
            f"hand: {', '.join(item.instance_id for item in state.hand) or '-'}  "
            f"round prosperity={prosperity} shield={shield}"
        )
        for index, column in enumerate(state.columns, start=1):
            cards = " > ".join(item.instance_id for item in column.cards) or "empty"
            tags = engine.column_tags(state, index - 1)
            tag_text = ", ".join(f"{tag}:{count}" for tag, count in sorted(tags.items())) or "none"
            top = column.top
            options = ""
            if top:
                card = engine.traits[top.card_id]
                options = " | ".join(
                    f"{option_index + 1}:{option.text or self._option_summary(option)}"
                    for option_index, option in enumerate(card.options)
                )
            self.say(f"  C{index} {cards}  tags[{tag_text}]  options[{options or '-'}]")

    @staticmethod
    def _requirements(requirements) -> str:
        return ", ".join(f"{tag} {amount}" for tag, amount in sorted(requirements.items())) or "none"

    @staticmethod
    def _option_summary(option) -> str:
        shields = sum(item.amount for item in option.shields)
        return (
            f"prosperity {option.prosperity}, shield {shields}, "
            f"draw {option.draw_cards}, next-retain {option.retain_bonus}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--environment", choices=tuple(event.id for event in EVENTS))
    args = parser.parse_args(argv)
    engine = GameEngine(TRAITS, EVENTS, seed=args.seed)
    state = engine.new_game(environment_id=args.environment)
    engine.run(HumanPolicy(), state)
    print(
        f"\nFinal: score={state.prosperity} damage={state.cumulative_damage} "
        f"status={'extinct' if state.history[-1].extinct else 'survived'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["HumanPolicy", "main"]
