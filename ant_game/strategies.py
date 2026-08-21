"""Simple, legible policies for v0.3 automated playtests.

The bots are diagnostic instruments rather than an NPC difficulty system.
Each policy exposes a recognisable bias so dominant rules are easy to spot.
"""

from __future__ import annotations

import random
from collections import Counter

from .engine import InvalidDecision
from .models import ActionOption, CardRole, GameState, Size, TraitCard


class Strategy:
    name = "strategy"
    prosperity_weight = 1.0
    shield_weight = 1.0
    plays_per_round: int | None = 3

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def choose_size(self, state: GameState, engine) -> Size:
        return state.size

    def choose_retained(self, state: GameState, candidates: tuple[str, ...], engine) -> tuple[str, ...]:
        choices = list(candidates)
        limit = min(engine.retention_limit(state), engine.hand_limit - len(state.hand))
        ranked = sorted(
            choices,
            key=lambda item: (self.card_value(engine.traits[item], state, engine), item),
            reverse=True,
        )
        return tuple(
            item for item in ranked[:limit]
            if self.card_value(engine.traits[item], state, engine) > 0
        )

    def take_actions(self, state: GameState, engine) -> None:
        for column_index in range(len(state.columns)):
            self._activate_best(state, engine, column_index)

        plays = 0
        while state.hand and (self.plays_per_round is None or plays < self.plays_per_round):
            choice = self._best_hand_play(state, engine)
            if choice is None:
                break
            instance_id, column_index, as_support = choice
            try:
                if as_support:
                    engine.insert_support(state, instance_id, column_index)
                else:
                    engine.play_card(state, instance_id, column_index)
                    self._activate_best(state, engine, column_index)
            except InvalidDecision:
                break
            plays += 1

    def card_value(self, card: TraitCard, state: GameState, engine) -> float:
        option_value = max(
            (self.hold_option_value(option, state, engine) for option in card.options),
            default=0.0,
        )
        requirement_cost = 0.35 * sum(card.activation_requirements.values())
        return option_value + 0.3 * len(card.root_tags) - requirement_cost

    def option_value(self, option: ActionOption, state: GameState, engine) -> float:
        context = state.current_round
        applicable = 0
        if context:
            for shield in option.shields:
                existing = sum(
                    item.amount for item in context.shields
                    if item.hazard_tag == shield.hazard_tag
                )
                applicable += min(
                    shield.amount,
                    max(0, context.hazard_rolls.get(shield.hazard_tag, 0) - existing),
                )
        return (
            self.prosperity_weight * option.prosperity * max(1, state.size.prosperity_multiplier)
            + self.shield_weight * applicable
            + 0.7 * option.draw_cards
        )

    def hold_option_value(self, option: ActionOption, state: GameState, engine) -> float:
        applicable = sum(
            shield.amount for shield in option.shields
            if shield.hazard_tag in engine.current_disaster(state).hazard_tags
        )
        return (
            self.prosperity_weight * option.prosperity * max(1, state.size.prosperity_multiplier)
            + self.shield_weight * applicable
            + 0.7 * option.draw_cards
        )

    def _activate_best(self, state: GameState, engine, column_index: int) -> bool:
        column = state.columns[column_index]
        top = column.top
        if top is None:
            return False
        card = engine.traits[top.card_id]
        if card.role not in (CardRole.ACTION, CardRole.STARTER) or not card.options:
            return False
        choices = sorted(
            enumerate(card.options),
            key=lambda item: (self.option_value(item[1], state, engine), -item[0]),
            reverse=True,
        )
        for option_index, option in choices:
            if self.option_value(option, state, engine) <= 0:
                continue
            try:
                engine.activate(state, column_index, option_index)
                return True
            except InvalidDecision:
                return False
        return False

    def _best_hand_play(self, state: GameState, engine) -> tuple[str, int, bool] | None:
        options: list[tuple[float, str, int, bool]] = []
        for instance in state.hand:
            card = engine.traits[instance.card_id]
            if card.role is CardRole.STARTER:
                continue
            for column_index in range(len(state.columns)):
                tags = engine.column_tags(state, column_index)
                requirements_met = all(
                    tags[tag] >= count
                    for tag, count in card.activation_requirements.items()
                )
                if requirements_met:
                    options.append(
                        (self.card_value(card, state, engine), instance.instance_id, column_index, False)
                    )
                if state.columns[column_index].cards:
                    options.append(
                        (
                            self.support_value(card, state, engine, column_index),
                            instance.instance_id,
                            column_index,
                            True,
                        )
                    )
        if not options:
            return None
        value, instance_id, column_index, as_support = max(
            options, key=lambda item: (item[0], item[1], -item[2])
        )
        return (instance_id, column_index, as_support) if value > 0 else None

    def support_value(self, card: TraitCard, state: GameState, engine, column_index: int) -> float:
        top = state.columns[column_index].top
        if top is None:
            return -10.0
        top_card = engine.traits[top.card_id]
        before = engine.activation_tags(state, column_index)
        missing_before = sum(
            max(0, amount - before[tag])
            for tag, amount in top_card.activation_requirements.items()
        )
        after = before.copy()
        after.update(card.root_tags)
        missing_after = sum(
            max(0, amount - after[tag])
            for tag, amount in top_card.activation_requirements.items()
        )
        return 1.2 * (missing_before - missing_after) + 0.15 * len(card.root_tags)

    @staticmethod
    def step_toward(state: GameState, engine, target: Size) -> Size:
        return min(
            engine.legal_sizes(state),
            key=lambda item: (abs(int(item) - int(target)), -int(item)),
        )


class ProsperityFirst(Strategy):
    name = "prosperity_first"
    prosperity_weight = 3.0
    shield_weight = 0.25
    plays_per_round = None

    def choose_size(self, state, engine):
        return self.step_toward(state, engine, Size.LARGE)


class AdaptabilityFirst(Strategy):
    name = "adaptability_first"
    prosperity_weight = 0.8
    shield_weight = 1.1
    plays_per_round = 2

    def choose_size(self, state, engine):
        round_number = state.current_round.round_number if state.current_round else 1
        target = Size.SMALL if round_number <= 2 else Size.MEDIUM
        return self.step_toward(state, engine, target)

    def support_value(self, card, state, engine, column_index):
        return super().support_value(card, state, engine, column_index) + 0.6 * len(card.root_tags)


class Reactive(Strategy):
    name = "reactive"
    prosperity_weight = 1.0
    shield_weight = 3.0
    plays_per_round = None

    def choose_size(self, state, engine):
        context = state.current_round
        pressure = sum(context.hazard_rolls.values()) if context else 0
        target = Size.SMALL if pressure >= 5 else Size.LARGE
        return self.step_toward(state, engine, target)


class Specialist(Strategy):
    name = "specialist"
    plays_per_round = None

    def __init__(self, seed: int = 0) -> None:
        super().__init__(seed)
        self.focus: str | None = None

    def card_value(self, card, state, engine):
        if self.focus is None and card.root_tags:
            self.focus = sorted(card.root_tags)[0]
        return super().card_value(card, state, engine) + (
            2.5 if self.focus in card.root_tags else -0.4
        )

    def choose_size(self, state, engine):
        return self.step_toward(state, engine, Size.LARGE)


class Generalist(Strategy):
    name = "generalist"
    plays_per_round = 3

    def card_value(self, card, state, engine):
        existing = Counter()
        for index in range(len(state.columns)):
            existing.update(engine.column_tags(state, index))
        novelty = sum(1 / (1 + existing[tag]) for tag in card.root_tags)
        return super().card_value(card, state, engine) + 1.5 * novelty

    def choose_size(self, state, engine):
        return self.step_toward(state, engine, Size.LARGE)


class RandomStrategy(Strategy):
    name = "random"
    plays_per_round = None

    def choose_size(self, state, engine):
        return self.rng.choice(engine.legal_sizes(state))

    def choose_retained(self, state, candidates, engine):
        choices = list(candidates)
        self.rng.shuffle(choices)
        limit = min(engine.retention_limit(state), engine.hand_limit - len(state.hand))
        return tuple(choices[: self.rng.randint(0, min(limit, len(choices)))])

    def take_actions(self, state, engine):
        for _ in range(len(state.hand)):
            if not state.hand or self.rng.random() < 0.25:
                break
            instance = self.rng.choice(state.hand)
            column = self.rng.randrange(len(state.columns))
            try:
                if state.columns[column].cards and self.rng.random() < 0.3:
                    engine.insert_support(state, instance.instance_id, column)
                else:
                    engine.play_card(state, instance.instance_id, column)
                    card = engine.traits[state.columns[column].top.card_id]
                    if card.options and self.rng.random() < 0.75:
                        engine.activate(state, column, self.rng.randrange(len(card.options)))
            except InvalidDecision:
                continue


class AlwaysSmall(AdaptabilityFirst):
    name = "always_small"

    def choose_size(self, state, engine):
        return self.step_toward(state, engine, Size.SMALL)


class AlwaysGiant(ProsperityFirst):
    name = "always_giant"

    def choose_size(self, state, engine):
        return self.step_toward(state, engine, Size.GIANT)


class IgnoreEnvironment(ProsperityFirst):
    name = "ignore_environment"
    shield_weight = 0.0


class ShieldOnly(Reactive):
    name = "shield_only"
    prosperity_weight = 0.0


class DumpHand(ProsperityFirst):
    name = "dump_hand"

    def _best_hand_play(self, state, engine):
        choice = super()._best_hand_play(state, engine)
        if choice is not None:
            return choice
        if not state.hand:
            return None
        instance = state.hand[0]
        return instance.instance_id, 0, bool(state.columns[0].cards)


class ExtremeBeeline(Reactive):
    name = "extreme_beeline"

    def card_value(self, card, state, engine):
        return super().card_value(card, state, engine)


class FinalTurnGiant(Reactive):
    name = "final_turn_giant"

    def choose_size(self, state, engine):
        if state.current_round and state.current_round.round_number >= 4:
            return self.step_toward(state, engine, Size.GIANT)
        return super().choose_size(state, engine)


STRATEGY_TYPES = {
    cls.name: cls
    for cls in (
        ProsperityFirst,
        AdaptabilityFirst,
        Reactive,
        Specialist,
        Generalist,
        RandomStrategy,
        AlwaysSmall,
        AlwaysGiant,
        IgnoreEnvironment,
        ShieldOnly,
        DumpHand,
        ExtremeBeeline,
        FinalTurnGiant,
    )
}


def make_strategy(name: str, seed: int = 0) -> Strategy:
    try:
        return STRATEGY_TYPES[name](seed=seed)
    except KeyError as exc:
        raise ValueError(f"unknown strategy: {name}") from exc


def strategy_names(*, include_exploits: bool = False) -> tuple[str, ...]:
    core = (
        "prosperity_first",
        "adaptability_first",
        "reactive",
        "specialist",
        "generalist",
        "random",
    )
    exploits = (
        "always_small",
        "always_giant",
        "ignore_environment",
        "shield_only",
        "dump_hand",
        "extreme_beeline",
        "final_turn_giant",
    )
    return core + (exploits if include_exploits else ())


__all__ = ["Strategy", "STRATEGY_TYPES", "make_strategy", "strategy_names"]
