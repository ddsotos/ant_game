"""Small, intentionally legible policies for automated v0.1 playtests.

These bots are measuring instruments, not opponents.  Each one isolates a
recognisable bias so a batch comparison can expose trivial or dominant rules.
"""

from __future__ import annotations

import random
from itertools import combinations
from collections.abc import Iterable

from .models import EventCard, EvolutionChoice, GameState, Size, TraitCard


THREAT_TAGS = frozenset({"predator", "competition", "disease", "dry", "fire", "flood", "wet"})


class Strategy:
    name = "strategy"

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def choose_size(self, state: GameState, engine) -> Size:
        return state.size

    def choose_latents(self, state: GameState, event: EventCard, stage: int | None, engine) -> tuple[str, ...]:
        result = []
        raw = event.shock_damage if stage is None else event.stage_damage.get(stage, 0)
        raw += event.size_damage.get(state.size, 0)
        for held in state.traits:
            if engine.can_activate(state, held.card_id, event, stage):
                card = engine.traits[held.card_id]
                mitigation = max((v for tag, v in card.mitigation_tags.items() if tag == "*" or tag in event.tags), default=0)
                if raw >= 2 and mitigation:
                    result.append(held.card_id)
        return tuple(result)

    def choose_trait(self, state: GameState, candidates: tuple[str, ...], engine):
        if not candidates:
            return None
        scored = [(self.trait_value(engine.traits[card_id], state, engine), card_id) for card_id in candidates]
        value, choice = max(scored, key=lambda item: (item[0], item[1]))
        if value <= 0:
            return None
        if len(state.traits) < engine.trait_slots:
            return choice
        held = [(self.trait_value(engine.traits[item.card_id], state, engine), item.card_id) for item in state.traits]
        held_value, discard = min(held, key=lambda item: (item[0], item[1]))
        return (choice, discard) if value > held_value else None

    def choose_evolution(self, state: GameState, candidates: tuple[str, ...], budget: int, engine):
        """Choose the best legal set of at most two candidates.

        This is intentionally a tiny exhaustive optimizer: the candidate
        reveal is small, and enumerating combinations makes every bot obey the
        same cost/slot rules while retaining its distinct trait valuation.
        """
        options: list[tuple[float, tuple[str, ...], tuple[str, ...]]] = [(0.0, (), ())]
        held_values = sorted(
            ((self.trait_value(engine.traits[item.card_id], state, engine), item.card_id)
             for item in state.traits),
            key=lambda item: (item[0], item[1]),
        )
        for count in (1, 2):
            for ids in combinations(candidates, count):
                cost = sum(engine.traits[card_id].play_cost for card_id in ids)
                if cost > budget:
                    continue
                needed = max(0, len(state.traits) + count - engine.trait_slots)
                if needed > len(held_values):
                    continue
                discards = tuple(card_id for _, card_id in held_values[:needed])
                value = sum(self.trait_value(engine.traits[card_id], state, engine) for card_id in ids)
                value -= sum(value for value, _ in held_values[:needed])
                options.append((value, tuple(ids), discards))
        best = max(options, key=lambda item: (item[0], len(item[1]), tuple(item[1])))
        if best[0] <= 0:
            return EvolutionChoice()
        return EvolutionChoice(best[1], best[2])

    def choose_shed(self, state: GameState, engine) -> str | None:
        """Shed one loaded, low-value trait only when it can restore a draw.

        A bot should not throw away a trait merely because the deck happens to
        be empty: shedding is an evolution action, and its purpose is to
        recover future flexibility.
        """
        if not state.traits or engine.draw_count(state) > 0:
            return None
        current_load = engine.evolution_load(state)
        options = []
        for held in state.traits:
            card = engine.traits[held.card_id]
            contribution = engine.evolution_load(GameState(seed=state.seed, traits=[held]))
            recovered = max(0, state.size.evolution_draw - (current_load - contribution))
            if recovered > 0:
                options.append((self.trait_value(card, state, engine), -contribution, held.card_id))
        if not options:
            return None
        return min(options)[2]

    def trait_value(self, card: TraitCard, state: GameState, engine) -> float:
        mitigation = card.mitigation_flat + sum(card.mitigation_tags.values())
        prosperity = card.prosperity_bonus + sum(card.prosperity_tags.values())
        return mitigation + prosperity - 0.75 * card.evolution_load + (0.5 if card.latent else 0)

    @staticmethod
    def _step_toward(state: GameState, engine, target: Size) -> Size:
        return min(engine.legal_sizes(state), key=lambda size: (abs(int(size) - int(target)), int(size)))

    @staticmethod
    def _urgent_tags(state: GameState, engine) -> set[str]:
        tags: set[str] = set()
        for event_id, stage in state.event_stages.items():
            if stage >= 2:
                tags.update(engine.events[event_id].tags & THREAT_TAGS)
        return tags


class ProsperityFirst(Strategy):
    name = "prosperity_first"

    def choose_size(self, state, engine):
        return self._step_toward(state, engine, Size.LARGE)

    def trait_value(self, card, state, engine):
        return 3 * (card.prosperity_bonus + sum(card.prosperity_tags.values())) + sum(card.mitigation_tags.values()) - 0.25 * card.evolution_load


class AdaptabilityFirst(Strategy):
    name = "adaptability_first"

    def choose_size(self, state, engine):
        return self._step_toward(state, engine, Size.SMALL)

    def trait_value(self, card, state, engine):
        return sum(card.mitigation_tags.values()) + sum(card.prosperity_tags.values()) - 2.25 * card.evolution_load + (1 if card.latent else 0)


class Reactive(Strategy):
    name = "reactive"

    def choose_size(self, state, engine):
        urgent = any(stage >= 2 for stage in state.event_stages.values())
        target = Size.SMALL if urgent else Size.LARGE
        return self._step_toward(state, engine, target)

    def trait_value(self, card, state, engine):
        urgent = self._urgent_tags(state, engine)
        relevant = sum(value for tag, value in card.mitigation_tags.items() if tag == "*" or tag in urgent)
        return 3 * relevant + sum(card.prosperity_tags.values()) + (1 if card.latent else 0) - card.evolution_load


class Specialist(Strategy):
    name = "specialist"

    def __init__(self, seed: int = 0, focus: str = "competition") -> None:
        super().__init__(seed)
        self.focus = focus

    def choose_size(self, state, engine):
        threatened = any(self.focus in engine.events[event_id].tags and stage >= 2 for event_id, stage in state.event_stages.items())
        return self._step_toward(state, engine, Size.MEDIUM if threatened else Size.LARGE)

    def trait_value(self, card, state, engine):
        focused = card.mitigation_tags.get(self.focus, 0) + card.prosperity_tags.get(self.focus, 0)
        return 4 * focused + (1 if self.focus in card.tags else 0) - 0.6 * card.evolution_load


class Generalist(Strategy):
    name = "generalist"

    def choose_size(self, state, engine):
        return self._step_toward(state, engine, Size.MEDIUM)

    def trait_value(self, card, state, engine):
        covered = set()
        for held in state.traits:
            covered.update(engine.traits[held.card_id].mitigation_tags)
        new_tags = (set(card.mitigation_tags) & THREAT_TAGS) - covered
        return 2.5 * len(new_tags) + sum(card.mitigation_tags.values()) + sum(card.prosperity_tags.values()) - card.evolution_load


class RandomStrategy(Strategy):
    name = "random"

    def choose_size(self, state, engine):
        return self.rng.choice(engine.legal_sizes(state))

    def choose_latents(self, state, event, stage, engine):
        legal = [held.card_id for held in state.traits if engine.can_activate(state, held.card_id, event, stage)]
        return tuple(card_id for card_id in legal if self.rng.random() < 0.5)

    def choose_trait(self, state, candidates, engine):
        if not candidates or self.rng.random() < 0.2:
            return None
        choice = self.rng.choice(candidates)
        if len(state.traits) < engine.trait_slots:
            return choice
        return choice, self.rng.choice(state.traits).card_id

    def choose_evolution(self, state, candidates, budget, engine):
        legal = [()] 
        for count in (1, 2):
            legal.extend(
                ids for ids in combinations(candidates, count)
                if sum(engine.traits[card_id].play_cost for card_id in ids) <= budget
            )
        ids = self.rng.choice(legal)
        needed = max(0, len(state.traits) + len(ids) - engine.trait_slots)
        if needed:
            discard_ids = tuple(item.card_id for item in self.rng.sample(state.traits, needed))
        else:
            discard_ids = ()
        return EvolutionChoice(tuple(ids), discard_ids)


class AlwaysGiant(ProsperityFirst):
    name = "always_giant"

    def choose_size(self, state, engine):
        return self._step_toward(state, engine, Size.HUGE)


class AlwaysTiny(AdaptabilityFirst):
    name = "always_tiny"

    def choose_size(self, state, engine):
        return self._step_toward(state, engine, Size.TINY)


class IgnoreEvents(ProsperityFirst):
    name = "ignore_events"

    def choose_size(self, state, engine):
        return self._step_toward(state, engine, Size.HUGE)

    def choose_latents(self, state, event, stage, engine):
        return ()

    def trait_value(self, card, state, engine):
        return 3 * (card.prosperity_bonus + sum(card.prosperity_tags.values())) - card.evolution_load


class LatentFirst(Reactive):
    name = "latent_first"

    def trait_value(self, card, state, engine):
        return super().trait_value(card, state, engine) + (8 if card.latent else 0)

    def choose_latents(self, state, event, stage, engine):
        return tuple(held.card_id for held in state.traits if engine.can_activate(state, held.card_id, event, stage))


class PeakAdaptive(Reactive):
    """Exploit probe: prepare for unresolved II/III waves, then regrow."""

    name = "peak_adaptive"

    def choose_size(self, state, engine):
        live_threats = [
            engine.events[event_id]
            for event_id, stage in state.event_stages.items()
            if stage in (2, 3) and event_id not in state.removed_events
        ]
        if not live_threats:
            target = Size.HUGE
        elif any(event.size_damage.get(Size.HUGE, 0) > 0 for event in live_threats):
            target = Size.MEDIUM
        elif any(event.size_damage.get(Size.TINY, 0) > 0 for event in live_threats):
            target = Size.LARGE
        else:
            target = Size.MEDIUM
        return self._step_toward(state, engine, target)


class TinyRushThenHuge(ProsperityFirst):
    """Exploit probe: bank flexibility early, then sprint for prosperity."""

    name = "tiny_rush_then_huge"

    def choose_size(self, state, engine):
        target = Size.TINY if state.round_number < 7 else Size.HUGE
        return self._step_toward(state, engine, target)


class Load0Stack(AdaptabilityFirst):
    """Exploit probe: prefer zero-load cards and test whether they stack safely."""

    name = "load0_stack"

    def trait_value(self, card, state, engine):
        return (12 if card.evolution_load == 0 else -4 * card.evolution_load) + super().trait_value(card, state, engine)


class StageSmall(ProsperityFirst):
    """Exploit probe: shrink whenever a relieved wave is visibly at II or III."""

    name = "stage_small"

    def choose_size(self, state, engine):
        threatened = any(
            stage in (2, 3)
            and event_id not in state.removed_events
            and engine.events[event_id].size_damage.get(Size.SMALL, 0) < 0
            for event_id, stage in state.event_stages.items()
        )
        return self._step_toward(state, engine, Size.SMALL if threatened else Size.HUGE)


class StageSafe(ProsperityFirst):
    """Exploit probe: use public stage-II warnings to approach each event's safest size."""

    name = "stage_safe"

    def choose_size(self, state, engine):
        impending_peaks = [
            engine.events[event_id]
            for event_id, stage in state.event_stages.items()
            if stage == 2 and event_id not in state.removed_events
        ]
        if not impending_peaks:
            target = Size.HUGE
        else:
            def forecast_value(size):
                size_pressure = sum(event.size_damage.get(size, 0) for event in impending_peaks)
                return size.prosperity + 0.5 * size.evolution_draw - size_pressure

            target = max(Size, key=lambda size: (forecast_value(size), int(size)))
        return self._step_toward(state, engine, target)


class WarningPerimeter(ProsperityFirst):
    """Exploit probe: stay at the largest size with no visible positive size penalty."""

    name = "warning_perimeter"

    def choose_size(self, state, engine):
        live_warnings = [
            engine.events[event_id]
            for event_id, stage in state.event_stages.items()
            if stage >= 2 and event_id not in state.removed_events
        ]

        def positive_pressure(size):
            return sum(max(0, event.size_damage.get(size, 0)) for event in live_warnings)

        target = min(Size, key=lambda size: (positive_pressure(size), -int(size)))
        return self._step_toward(state, engine, target)


class WarningPerimeterNoLatent(WarningPerimeter):
    """Isolation probe: use WarningPerimeter sizing while rejecting latent insurance."""

    name = "warning_perimeter_no_latent"

    def trait_value(self, card, state, engine):
        if card.latent:
            return float("-inf")
        return super().trait_value(card, state, engine)


class WarningPerimeterSelectiveLatent(WarningPerimeter):
    """Isolation probe: buy insurance only when a matching threat is already visible."""

    name = "warning_perimeter_selective_latent"

    def trait_value(self, card, state, engine):
        if not card.latent:
            return super().trait_value(card, state, engine)
        visible_stage = max(
            (
                stage
                for event_id, stage in state.event_stages.items()
                if event_id not in state.removed_events
                and card.trigger_tags & engine.events[event_id].tags
            ),
            default=0,
        )
        if visible_stage == 0:
            return float("-inf")
        urgency_bonus = 4 if visible_stage >= 2 else 0
        return super().trait_value(card, state, engine) + urgency_bonus


class LateProsperityRush(WarningPerimeterSelectiveLatent):
    """Exploit probe: use warning cover early, then lock Huge for the endgame."""

    name = "late_prosperity_rush"

    def choose_size(self, state, engine):
        if state.round_number >= 11:
            return self._step_toward(state, engine, Size.HUGE)
        return super().choose_size(state, engine)


class MidgameLargeLock(WarningPerimeterSelectiveLatent):
    """Exploit probe: adapt early, then lock Large from round nine."""

    name = "midgame_large_lock"

    def choose_size(self, state, engine):
        if state.round_number >= 8:
            return self._step_toward(state, engine, Size.LARGE)
        return super().choose_size(state, engine)


STRATEGY_TYPES = {
    cls.name: cls
    for cls in (ProsperityFirst, AdaptabilityFirst, Reactive, Specialist, Generalist, RandomStrategy,
                AlwaysGiant, AlwaysTiny, IgnoreEvents, LatentFirst, PeakAdaptive,
                TinyRushThenHuge, Load0Stack, StageSmall, StageSafe,
                WarningPerimeter, WarningPerimeterNoLatent,
                WarningPerimeterSelectiveLatent, LateProsperityRush,
                MidgameLargeLock)
}


def make_strategy(name: str, seed: int = 0) -> Strategy:
    """Create a fresh policy; fresh instances prevent state leaking between games."""
    try:
        return STRATEGY_TYPES[name](seed=seed)
    except KeyError as exc:
        raise ValueError(f"unknown strategy {name!r}; choose from {', '.join(STRATEGY_TYPES)}") from exc


def strategy_names(*, include_exploits: bool = False) -> tuple[str, ...]:
    core = ("prosperity_first", "adaptability_first", "reactive", "specialist", "generalist", "random")
    return core + (("always_giant", "always_tiny", "ignore_events", "latent_first", "peak_adaptive",
                    "tiny_rush_then_huge", "load0_stack", "stage_small", "stage_safe",
                    "warning_perimeter", "warning_perimeter_no_latent",
                    "warning_perimeter_selective_latent", "late_prosperity_rush",
                    "midgame_large_lock") if include_exploits else ())


__all__ = ["Strategy", "STRATEGY_TYPES", "make_strategy", "strategy_names"]
