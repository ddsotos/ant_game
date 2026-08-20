"""Deterministic, UI-independent resolution for the v0.1 rules."""

from __future__ import annotations

import random
import re
from collections.abc import Iterable, Sequence
from typing import Any

from .models import (
    EventCard,
    EventKind,
    EvolutionChoice,
    GameState,
    RoundDecision,
    RoundRecord,
    Size,
    TraitCard,
    TraitState,
)


class InvalidDecision(ValueError):
    pass


class GameEngine:
    """Rules engine. Card definitions are injected by ``content.py``."""

    trait_slots = 5

    def __init__(
        self,
        traits: Iterable[TraitCard],
        events: Iterable[EventCard],
        seed: int = 0,
        rounds: int = 18,
        growth_cost_per_step: int = 2,
    ) -> None:
        trait_cards = list(traits)
        event_cards = list(events)
        self.traits = {card.id: card for card in trait_cards}
        self.events = {card.id: card for card in event_cards}
        if len(self.traits) == 0 or len(self.events) == 0:
            raise ValueError("at least one trait and event are required")
        if len(self.traits) != len(trait_cards) or len(self.events) != len(event_cards):
            raise ValueError("card ids must be unique")
        if any(card.play_cost not in (1, 2, 3) for card in trait_cards):
            raise ValueError("trait play_cost must be 1, 2, or 3")
        self.seed = seed
        self.rounds = rounds
        if growth_cost_per_step < 0:
            raise ValueError("growth_cost_per_step must be non-negative")
        self.growth_cost_per_step = growth_cost_per_step

    def new_game(self) -> GameState:
        rng = random.Random(self.seed)
        event_deck = list(self.events)
        trait_deck = list(self.traits)
        rng.shuffle(event_deck)
        rng.shuffle(trait_deck)
        return GameState(
            seed=self.seed,
            event_deck=event_deck,
            trait_deck=trait_deck,
            rng_state=rng.getstate(),
        )

    def is_finished(self, state: GameState) -> bool:
        return state.round_number >= self.rounds

    def evolution_load(self, state: GameState) -> int:
        total = 0
        for held in state.traits:
            card = self.traits[held.card_id]
            if not held.active and card.latent:
                total += card.evolution_load
                continue
            if card.latent and card.activated_evolution_load is not None:
                total += card.activated_evolution_load
            elif card.latent and card.effect_id:
                # Compatibility for compact content effect ids such as
                # ``super_soldier_emergence_load2``.
                match = re.search(r"_load(\d+)$", card.effect_id)
                total += int(match.group(1)) if match else card.evolution_load
            else:
                total += card.evolution_load
        return total

    def draw_count(self, state: GameState, size: Size | None = None) -> int:
        chosen_size = state.size if size is None else size
        return max(0, chosen_size.evolution_draw - self.evolution_load(state))

    def legal_sizes(self, state: GameState) -> tuple[Size, ...]:
        return tuple(
            Size(value)
            for value in range(max(0, int(state.size) - 1), min(4, int(state.size) + 1) + 1)
        )

    def can_activate(self, state: GameState, trait_id: str, event: EventCard, stage: int | None) -> bool:
        held = next((item for item in state.traits if item.card_id == trait_id), None)
        if held is None or held.active:
            return False
        card = self.traits[trait_id]
        tag_match = not card.trigger_tags or bool(card.trigger_tags & event.tags)
        return tag_match and (stage or 1) >= card.trigger_min_stage

    def resolve_round(
        self, state: GameState, decision: RoundDecision, policy: Any | None = None
    ) -> RoundRecord:
        if self.is_finished(state):
            raise InvalidDecision("the game is already finished")
        if decision.size not in self.legal_sizes(state):
            raise InvalidDecision("size may change by at most one step")

        rng = random.Random()
        rng.setstate(state.rng_state)
        size_before = state.size
        traits_before = tuple(item.card_id for item in state.traits)
        load_at_round_start = self.evolution_load(state)
        state.size = decision.size

        event = self._draw_event(state, rng)
        previous_id = state.previous_event_id
        stage = self._advance_event(state, event)
        activated: list[str] = []
        consumed: list[str] = []
        activation_ids = decision.activate_latent_ids
        if policy is not None and hasattr(policy, "choose_latents"):
            activation_ids = tuple(policy.choose_latents(state, event, stage, self))
        requested = set(activation_ids)
        if len(requested) != len(activation_ids):
            raise InvalidDecision("a latent trait may only be activated once")
        for trait_id in requested:
            if not self.can_activate(state, trait_id, event, stage):
                raise InvalidDecision(f"latent trait cannot activate now: {trait_id}")
            held = next(item for item in state.traits if item.card_id == trait_id)
            held.active = True
            activated.append(trait_id)

        sequence_triggered = self._sequence_triggered(event, previous_id)
        raw_damage = self._raw_damage(event, stage, state.size, sequence_triggered)
        mitigation_by_trait = {
            t.card_id: self._trait_mitigation(self.traits[t.card_id], event)
            for t in state.traits
            if t.active
        }
        mitigation = sum(mitigation_by_trait.values())
        damage = max(0, raw_damage - mitigation)
        prosperity_modifier = event.prosperity_modifier + sum(
            self._trait_prosperity(self.traits[t.card_id], event) for t in state.traits if t.active
        )
        growth_cost = self.growth_cost_per_step * max(0, int(state.size) - int(size_before))
        raw_prosperity_delta = state.size.prosperity + prosperity_modifier - damage - growth_cost
        old_prosperity = state.prosperity
        state.prosperity = max(0, old_prosperity + raw_prosperity_delta)
        actual_prosperity_delta = state.prosperity - old_prosperity

        for trait_id in activated:
            card = self.traits[trait_id]
            if card.consume_on_trigger:
                state.traits = [item for item in state.traits if item.card_id != trait_id]
                state.trait_discard.append(trait_id)
                consumed.append(trait_id)
        for held in tuple(state.traits):
            card = self.traits[held.card_id]
            if card.consume_on_trigger and mitigation_by_trait.get(held.card_id, 0) > 0:
                state.traits.remove(held)
                state.trait_discard.append(held.card_id)
                consumed.append(held.card_id)

        draw_count = max(0, state.size.evolution_draw - load_at_round_start)
        candidates = self._draw_traits(state, rng, draw_count)
        trait_decision = decision
        if candidates and policy is not None and (hasattr(policy, "choose_evolution") or hasattr(policy, "choose_trait")):
            # New policies may spend this round's evolution capacity on up to
            # two cards.  Keep choose_trait as a compatibility fallback for
            # existing policies and external callers.
            if hasattr(policy, "choose_evolution"):
                choice = policy.choose_evolution(state, tuple(candidates), draw_count, self)
            else:
                choice = policy.choose_trait(state, tuple(candidates), self)
            trait_decision = self._decision_from_evolution_choice(state.size, choice)
        elif not candidates and policy is not None and hasattr(policy, "choose_shed"):
            shed_id = policy.choose_shed(state, self)
            trait_decision = RoundDecision(state.size, shed_trait_id=shed_id)
        acquired, discarded, shed, spent = self._resolve_trait_choice(
            state, candidates, trait_decision, allow_shed=draw_count == 0
        )
        self._discard_event(state, event)
        state.previous_event_id = event.id
        state.round_number += 1
        state.rng_state = rng.getstate()

        record = RoundRecord(
            round_number=state.round_number,
            size_before=size_before,
            size=state.size,
            event_id=event.id,
            event_name=event.name,
            event_kind=event.kind,
            event_stage=stage,
            previous_event_id=previous_id,
            sequence_triggered=sequence_triggered,
            traits_before=traits_before,
            latent_activated=tuple(sorted(activated)),
            latent_consumed=tuple(sorted(consumed)),
            raw_damage=raw_damage,
            mitigation=mitigation,
            damage=damage,
            base_prosperity=state.size.prosperity,
            prosperity_modifier=prosperity_modifier,
            growth_cost=growth_cost,
            raw_prosperity_delta=raw_prosperity_delta,
            actual_prosperity_delta=actual_prosperity_delta,
            prosperity_gained=actual_prosperity_delta,
            total_prosperity=state.prosperity,
            evolution_load=load_at_round_start,
            evolution_draw_count=draw_count,
            trait_candidates=tuple(candidates),
            acquired_trait_id=acquired[0] if acquired else None,
            discarded_trait_id=discarded[0] if discarded else None,
            acquired_trait_ids=acquired,
            discarded_trait_ids=discarded,
            shed_trait_id=shed,
            evolution_budget=draw_count,
            evolution_budget_spent=spent,
            evolution_budget_utilization=(spent / draw_count if draw_count else 0.0),
            traits_after=tuple(item.card_id for item in state.traits),
        )
        state.history.append(record)
        return record

    def play_round(self, state: GameState, policy: Any) -> RoundRecord:
        size = policy.choose_size(state, self)
        return self.resolve_round(state, RoundDecision(size=size), policy=policy)

    def run(self, policy: Any, state: GameState | None = None) -> GameState:
        state = state or self.new_game()
        while not self.is_finished(state):
            self.play_round(state, policy)
        return state

    def _draw_event(self, state: GameState, rng: random.Random) -> EventCard:
        if not state.event_deck:
            if not state.event_discard:
                raise RuntimeError("all events were removed before the game ended")
            state.event_deck = state.event_discard
            state.event_discard = []
            rng.shuffle(state.event_deck)
            state.event_reshuffles += 1
        return self.events[state.event_deck.pop()]

    def _advance_event(self, state: GameState, event: EventCard) -> int | None:
        if event.kind == EventKind.SHOCK:
            return None
        stage = state.event_stages.get(event.id, 0) + 1
        state.event_stages[event.id] = stage
        return stage

    def _discard_event(self, state: GameState, event: EventCard) -> None:
        stage = state.event_stages.get(event.id)
        if event.kind == EventKind.SHOCK or stage == 4:
            state.removed_events.append(event.id)
        else:
            state.event_discard.append(event.id)

    def _sequence_triggered(self, event: EventCard, previous_id: str | None) -> bool:
        if not event.sequence_prev_tag or previous_id is None:
            return False
        return event.sequence_prev_tag in self.events[previous_id].tags

    @staticmethod
    def _raw_damage(event: EventCard, stage: int | None, size: Size, sequence: bool) -> int:
        base = event.shock_damage if stage is None else event.stage_damage.get(stage, 0)
        size_damage = (
            event.size_damage.get(size, 0)
            if stage is None or stage >= event.size_damage_min_stage
            else 0
        )
        peak_damage = event.peak_size_damage.get(size, 0) if stage == 3 else 0
        return max(0, base + size_damage + peak_damage + (event.sequence_damage_bonus if sequence else 0))

    @staticmethod
    def _trait_mitigation(card: TraitCard, event: EventCard) -> int:
        matching = [amount for tag, amount in card.mitigation_tags.items() if tag == "*" or tag in event.tags]
        return card.mitigation_flat + (max(matching) if matching else 0)

    @staticmethod
    def _trait_prosperity(card: TraitCard, event: EventCard) -> int:
        matching = [amount for tag, amount in card.prosperity_tags.items() if tag == "*" or tag in event.tags]
        return card.prosperity_bonus + (max(matching) if matching else 0)

    def _draw_traits(self, state: GameState, rng: random.Random, count: int) -> list[str]:
        result: list[str] = []
        while len(result) < count:
            if not state.trait_deck:
                if not state.trait_discard:
                    break
                state.trait_deck = state.trait_discard
                state.trait_discard = []
                rng.shuffle(state.trait_deck)
                state.trait_reshuffles += 1
            result.append(state.trait_deck.pop())
        return result

    def _resolve_trait_choice(
        self, state: GameState, candidates: list[str], decision: RoundDecision,
        *, allow_shed: bool = False,
    ) -> tuple[tuple[str, ...], tuple[str, ...], str | None, int]:
        choice = decision.evolution or decision.evolution_choice
        if decision.evolution is not None and decision.evolution_choice is not None:
            raise InvalidDecision("specify only one evolution choice field")
        if choice is not None:
            if any((decision.acquire_trait_id, decision.acquire_index, decision.discard_trait_id,
                    decision.shed_trait_id, decision.acquire_trait_ids, decision.discard_trait_ids)):
                raise InvalidDecision("use evolution or legacy evolution fields, not both")
            acquire_ids = tuple(choice.acquire_trait_ids)
            discard_ids = tuple(choice.discard_trait_ids)
            shed_id = choice.shed_trait_id
        else:
            acquire_ids = tuple(decision.acquire_trait_ids)
            discard_ids = tuple(decision.discard_trait_ids)
            shed_id = decision.shed_trait_id
            if decision.acquire_trait_id is not None:
                if acquire_ids:
                    raise InvalidDecision("use singular or plural acquisition fields, not both")
                acquire_ids = (decision.acquire_trait_id,)
            elif decision.acquire_index is not None:
                if acquire_ids:
                    raise InvalidDecision("use acquire_index or plural acquisition fields, not both")
                if not 0 <= decision.acquire_index < len(candidates):
                    raise InvalidDecision("trait candidate index is out of range")
                acquire_ids = (candidates[decision.acquire_index],)
            if decision.discard_trait_id is not None:
                if discard_ids:
                    raise InvalidDecision("use singular or plural discard fields, not both")
                discard_ids = (decision.discard_trait_id,)

        if shed_id is not None:
            if not allow_shed:
                raise InvalidDecision("a trait may only be shed when no evolution candidates were drawn")
            if acquire_ids or discard_ids:
                raise InvalidDecision("shedding and acquiring cannot happen in the same round")
            shed = shed_id
            if shed not in {item.card_id for item in state.traits}:
                raise InvalidDecision("the shed trait must be held")
            state.traits = [item for item in state.traits if item.card_id != shed]
            state.trait_discard.append(shed)
            for trait_id in candidates:
                state.trait_discard.append(trait_id)
            return (), (), shed, 0

        if len(acquire_ids) != len(set(acquire_ids)):
            raise InvalidDecision("a candidate may only be acquired once")
        if len(acquire_ids) > 2:
            raise InvalidDecision("at most two traits may be acquired in one round")
        if any(trait_id not in candidates for trait_id in acquire_ids):
            raise InvalidDecision("every acquired trait must be a drawn candidate")
        spent = sum(self.traits[trait_id].play_cost for trait_id in acquire_ids)
        budget = max(0, len(candidates))
        if spent > budget:
            raise InvalidDecision("trait play costs exceed this round's evolution budget")
        required_discards = max(0, len(state.traits) + len(acquire_ids) - self.trait_slots)
        if len(discard_ids) != len(set(discard_ids)):
            raise InvalidDecision("a held trait may only be discarded once")
        held_ids = {item.card_id for item in state.traits}
        if len(discard_ids) != required_discards:
            raise InvalidDecision("discard exactly one held trait per full-slot exchange")
        if any(trait_id not in held_ids for trait_id in discard_ids):
            raise InvalidDecision("discarded traits must be held")
        if required_discards:
            state.traits = [item for item in state.traits if item.card_id not in discard_ids]
            for trait_id in discard_ids:
                state.trait_discard.append(trait_id)
        elif discard_ids:
            raise InvalidDecision("discarding is only allowed when acquisition exceeds slots")

        for trait_id in candidates:
            if trait_id not in acquire_ids:
                state.trait_discard.append(trait_id)
        for trait_id in acquire_ids:
            card = self.traits[trait_id]
            state.traits.append(TraitState(trait_id, active=not card.latent))
        return acquire_ids, discard_ids, None, spent

    @staticmethod
    def _decision_from_evolution_choice(size: Size, choice: Any) -> RoundDecision:
        """Normalize new and legacy policy return values into RoundDecision."""
        if isinstance(choice, RoundDecision):
            return choice
        if isinstance(choice, EvolutionChoice):
            return RoundDecision(size=size, evolution=choice)
        if choice is None:
            return RoundDecision(size=size)
        if isinstance(choice, int):
            return RoundDecision(size=size, acquire_index=choice)
        if isinstance(choice, str):
            return RoundDecision(size=size, acquire_trait_id=choice)
        if isinstance(choice, tuple):
            # Old API returned (acquire_id, discard_id).  Also accept a tuple
            # of ids as a new acquire-only shorthand.
            if len(choice) == 2 and all(item is None or isinstance(item, str) for item in choice):
                acquire, discard = choice
                return RoundDecision(size=size, acquire_trait_id=acquire, discard_trait_id=discard)
            return RoundDecision(size=size, acquire_trait_ids=tuple(choice))
        raise InvalidDecision("policy returned an unsupported evolution choice")
