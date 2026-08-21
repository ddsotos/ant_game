"""Deterministic, UI-independent v0.3 Daybreak-style rules engine."""

from __future__ import annotations

import copy
import random
from collections import Counter
from collections.abc import Iterable, Sequence
from typing import Any

from .models import (
    ActionCommand,
    ActionOption,
    CardInstance,
    CardRole,
    ColumnState,
    EventCard,
    ExtremeAdaptation,
    GameState,
    PlayedCard,
    RoundContext,
    RoundDecision,
    RoundPhase,
    RoundRecord,
    ShieldSpec,
    Size,
    TraitCard,
)


class InvalidDecision(ValueError):
    """Raised when a command is not legal in the current phase/state."""


class GameEngine:
    STAGES = (1, 1, 2, 3, 4)

    def __init__(
        self,
        traits: Iterable[TraitCard],
        events: Iterable[EventCard],
        seed: int = 0,
        *,
        columns: int = 3,
        column_capacity: int | None = None,
        retention_curve: str | dict[Size, int] = "aggressive",
        hand_limit: int = 8,
        rounds: int = 5,
        extinction_threshold: int = 6,
        starter_ids: Sequence[str] | None = None,
        extremes: Iterable[ExtremeAdaptation] = (),
    ) -> None:
        if columns not in (3, 4):
            raise ValueError("columns must be 3 or 4")
        if rounds != 5:
            raise ValueError("the v0.3 prototype is fixed at five rounds")
        if hand_limit < 0 or extinction_threshold <= 0:
            raise ValueError("hand_limit must be non-negative and threshold positive")
        self.seed = seed
        self.rounds = rounds
        self.column_count = columns
        self.column_capacity = column_capacity if column_capacity is not None else (5 if columns == 3 else 4)
        if self.column_capacity < 1:
            raise ValueError("column_capacity must be positive")
        self.hand_limit = hand_limit
        self.extinction_threshold = extinction_threshold

        cards = list(traits)
        events_list = list(events)
        self.traits = {card.id: card for card in cards}
        self.events = {event.id: event for event in events_list}
        if not self.traits or not self.events:
            raise ValueError("at least one trait and event are required")
        if len(self.traits) != len(cards) or len(self.events) != len(events_list):
            raise ValueError("card ids and event ids must be unique")

        embedded: list[ExtremeAdaptation] = list(extremes)
        for event in events_list:
            for item in event.extreme_adaptations:
                if isinstance(item, ExtremeAdaptation):
                    embedded.append(item)
        self.extremes = {item.id: item for item in embedded}
        if len(self.extremes) != len(embedded):
            raise ValueError("extreme adaptation ids must be unique")
        for item in self.extremes.values():
            self.traits.setdefault(item.id, item.as_trait())
        for event in events_list:
            for attached in event.extreme_adaptations:
                attached_id = attached.id if isinstance(attached, ExtremeAdaptation) else attached
                if attached_id not in self.extremes:
                    raise ValueError(f"environment references unknown extreme adaptation: {attached_id}")

        if retention_curve == "aggressive":
            self.retention_curve = {size: size.retention for size in Size}
        elif retention_curve == "soft":
            self.retention_curve = {Size.SMALL: 4, Size.MEDIUM: 3, Size.LARGE: 3, Size.GIANT: 2}
        elif isinstance(retention_curve, dict):
            self.retention_curve = {size: int(retention_curve[size]) for size in Size}
        else:
            raise ValueError("retention_curve must be aggressive, soft, or a Size mapping")
        if any(value < 0 for value in self.retention_curve.values()):
            raise ValueError("retention values must be non-negative")

        starter_candidates = [card.id for card in cards if card.role is CardRole.STARTER]
        self.starter_ids = tuple(starter_ids or starter_candidates[:3])
        if len(self.starter_ids) != 3 or len(set(self.starter_ids)) != 3:
            raise ValueError("exactly three distinct starter ids are required")
        if any(card_id not in self.traits for card_id in self.starter_ids):
            raise ValueError("starter ids must refer to trait cards")

        self.normal_ids = tuple(
            card.id for card in cards
            if card.id not in self.starter_ids and card.id not in self.extremes
        )
        if len(self.normal_ids) < 6:
            raise ValueError("at least six normal non-starter cards are required")

    # ------------------------------------------------------------------ setup
    def new_game(self, *, environment_id: str | None = None) -> GameState:
        rng = random.Random(self.seed)
        event_ids = list(self.events)
        rng.shuffle(event_ids)
        chosen = environment_id or event_ids[0]
        if chosen not in self.events:
            raise InvalidDecision(f"unknown environment: {chosen}")

        deck = [CardInstance(card_id, card_id) for card_id in self.normal_ids]
        rng.shuffle(deck)
        columns = [ColumnState() for _ in range(self.column_count)]
        for index, card_id in enumerate(self.starter_ids):
            columns[index].cards.append(
                PlayedCard(instance_id=card_id, card_id=card_id)
            )
        return GameState(
            seed=self.seed,
            size=Size.SMALL,
            columns=columns,
            environment_id=chosen,
            trait_deck=deck,
            rng_state=rng.getstate(),
        )

    def is_finished(self, state: GameState) -> bool:
        return state.finished

    def legal_sizes(self, state: GameState) -> tuple[Size, ...]:
        value = int(state.size)
        return tuple(Size(index) for index in range(max(0, value - 1), min(3, value + 1) + 1))

    def current_event(self, state: GameState) -> EventCard:
        try:
            return self.events[state.environment_id]
        except KeyError as exc:
            raise InvalidDecision("state has no valid environment") from exc

    def current_stage(self, state: GameState) -> int:
        if state.round_number >= self.rounds:
            return self.STAGES[-1]
        return self.STAGES[state.round_number]

    def retention_limit(self, state: GameState) -> int:
        bonus = state.current_round.retention_bonus if state.current_round is not None else 0
        return self.retention_curve[state.size] + bonus

    # ------------------------------------------------------------- round flow
    def start_round(self, state: GameState) -> EventCard:
        self._require_phase(state, RoundPhase.IDLE)
        if state.round_number >= self.rounds:
            state.phase = RoundPhase.COMPLETE
            raise InvalidDecision("the game is already finished")
        state.current_round = RoundContext(
            round_number=state.round_number + 1,
            stage=self.STAGES[state.round_number],
            environment_id=state.environment_id,
            size_before=state.size,
            retention_bonus=state.next_retention_bonus,
        )
        state.next_retention_bonus = 0
        state.phase = RoundPhase.SIZE
        return self.current_event(state)

    def choose_size(self, state: GameState, size: Size) -> tuple[str, ...]:
        self._require_phase(state, RoundPhase.SIZE)
        if not isinstance(size, Size):
            try:
                size = Size(size)
            except (TypeError, ValueError) as exc:
                raise InvalidDecision("invalid size") from exc
        if size not in self.legal_sizes(state):
            raise InvalidDecision("size may change by at most one step")
        assert state.current_round is not None
        state.size = size
        candidates = self._draw_candidates(state, 6)
        state.current_round.candidate_ids = tuple(item.instance_id for item in candidates)
        state.current_round.candidate_instances = list(candidates)
        state.phase = RoundPhase.RETAIN
        return state.current_round.candidate_ids

    def retain_cards(self, state: GameState, card_ids: Sequence[str] = ()) -> tuple[str, ...]:
        self._require_phase(state, RoundPhase.RETAIN)
        assert state.current_round is not None
        requested = tuple(card_ids)
        if len(set(requested)) != len(requested):
            raise InvalidDecision("a card may only be retained once")
        candidates = set(state.current_round.candidate_ids)
        valid_extremes = {item.id for item in self.eligible_extremes(state)}
        if any(card_id not in candidates and card_id not in valid_extremes for card_id in requested):
            raise InvalidDecision("retained cards must be current candidates or eligible extremes")
        limit = min(self.retention_limit(state), self.hand_limit - len(state.hand))
        if len(requested) > limit:
            raise InvalidDecision("retained cards exceed the size or hand limit")

        candidate_instances = {item.instance_id: item for item in self._current_candidate_instances(state)}
        retained_instances: list[CardInstance] = []
        for instance_id in requested:
            if instance_id in candidate_instances:
                retained_instances.append(candidate_instances[instance_id])
            else:
                retained_instances.append(CardInstance(instance_id, instance_id, state.environment_id))
                state.claimed_extreme_ids.add(instance_id)
        state.hand.extend(retained_instances)
        kept = set(requested)
        remaining = [item for item in self._current_candidate_instances(state) if item.instance_id not in kept]
        state.trait_discard.extend(remaining)
        state.current_round.retained_ids = requested
        state.phase = RoundPhase.ACTIONS
        return requested

    def play_card(self, state: GameState, card_id: str, column_index: int) -> tuple[str, ...]:
        self._require_phase(state, RoundPhase.ACTIONS)
        self._validate_column(column_index)
        instance = self._find_hand_instance(state, card_id)
        card = self.traits[instance.card_id]
        if card.role is CardRole.SUPPORT:
            raise InvalidDecision("support cards must use insert_support")
        if card.role is CardRole.STARTER:
            raise InvalidDecision("starter cards cannot be played from hand")
        instance = self._take_hand_instance(state, instance.instance_id)
        column = state.columns[column_index]
        pushed: list[str] = []
        column.cards.append(
            PlayedCard(
                instance_id=instance.instance_id,
                card_id=instance.card_id,
                origin_event_id=instance.origin_event_id,
            )
        )
        if len(column.cards) > self.column_capacity:
            pushed_card = column.cards.pop(0)
            pushed.append(pushed_card.instance_id)
            state.trait_discard.append(
                CardInstance(pushed_card.instance_id, pushed_card.card_id, pushed_card.origin_event_id)
            )
        self._on_play(card, state)
        self._log_action(state, {"kind": "play", "card_id": card_id, "column": column_index, "pushed_out": tuple(pushed)})
        return tuple(pushed)

    def insert_support(self, state: GameState, card_id: str, column_index: int) -> None:
        self._require_phase(state, RoundPhase.ACTIONS)
        self._validate_column(column_index)
        column = state.columns[column_index]
        if not column.cards:
            raise InvalidDecision("support cards cannot be placed into an empty column")
        if len(column.cards) == 1 and self.column_capacity == 1:
            raise InvalidDecision("support would evict the current top")
        instance = self._find_hand_instance(state, card_id)
        card = self.traits[instance.card_id]
        if card.role is CardRole.STARTER:
            raise InvalidDecision("starter cards cannot be inserted as support")
        instance = self._take_hand_instance(state, instance.instance_id)
        # Cards are oldest -> newest.  Insert immediately below the top.
        column.cards.insert(
            len(column.cards) - 1,
            PlayedCard(
                instance_id=instance.instance_id,
                card_id=instance.card_id,
                origin_event_id=instance.origin_event_id,
                is_support=True,
            ),
        )
        pushed = None
        if len(column.cards) > self.column_capacity:
            pushed = column.cards.pop(0)
            state.trait_discard.append(
                CardInstance(pushed.instance_id, pushed.card_id, pushed.origin_event_id)
            )
        self._log_action(state, {"kind": "support", "card_id": card_id, "column": column_index,
                                 "pushed_out": pushed.instance_id if pushed else None})

    def activate(self, state: GameState, column_index: int, option_index: int = 0) -> ActionOption:
        self._require_phase(state, RoundPhase.ACTIONS)
        self._validate_column(column_index)
        column = state.columns[column_index]
        top = column.top
        if top is None:
            raise InvalidDecision("cannot activate an empty column")
        card = self.traits[top.card_id]
        if card.role not in (CardRole.ACTION, CardRole.STARTER):
            raise InvalidDecision("only an ACTION or starter card can be activated")
        assert state.current_round is not None
        if top.activated_round == state.current_round.round_number:
            raise InvalidDecision("a physical card may activate only once per round")
        if not self._requirements_met(state, column_index, card.activation_requirements):
            raise InvalidDecision("the column does not meet the activation requirements")
        if not 0 <= option_index < len(card.options):
            raise InvalidDecision("action option index is out of range")
        option = card.options[option_index]
        # All validation above is complete before state changes.
        top.activated_round = state.current_round.round_number
        state.current_round.prosperity_base += option.prosperity
        state.current_round.shields.extend(option.shields)
        state.current_round.bonus_draws += option.draw_cards
        state.next_retention_bonus += option.retain_bonus
        if option.draw_cards:
            self._draw_to_hand(state, option.draw_cards)
        self._log_action(state, {"kind": "activate", "card_id": top.instance_id,
                                 "column": column_index, "option_index": option_index,
                                 "prosperity": option.prosperity,
                                 "shields": tuple(option.shields)})
        return option

    def resolve_environment(self, state: GameState) -> RoundRecord:
        self._require_phase(state, RoundPhase.ACTIONS)
        assert state.current_round is not None
        context = state.current_round
        event = self.current_event(state)
        raw_damage = max(0, int(event.stage_damage.get(context.stage, 0)))
        applicable = tuple(shield for shield in context.shields if shield.hazard_tags & event.hazard_tags)
        shield_amount = sum(shield.amount for shield in applicable)
        damage = max(0, raw_damage - shield_amount)
        state.cumulative_damage += damage
        extinct = state.cumulative_damage >= self.extinction_threshold
        prosperity_delta = 0 if extinct else context.prosperity_base * state.size.prosperity_multiplier
        if not extinct:
            state.prosperity += prosperity_delta
        state.round_number += 1
        state.phase = RoundPhase.EXTINCT if extinct else (RoundPhase.COMPLETE if state.round_number >= self.rounds else RoundPhase.IDLE)
        columns_after = tuple(tuple(item.instance_id for item in column.cards) for column in state.columns)
        pushed_out = tuple(
            pushed
            for action in context.action_log
            for pushed in (
                action.get("pushed_out", ())
                if isinstance(action.get("pushed_out", ()), tuple)
                else ((action["pushed_out"],) if action.get("pushed_out") else ())
            )
        )
        record = RoundRecord(
            round_number=context.round_number,
            stage=context.stage,
            environment_id=context.environment_id,
            size_before=context.size_before,
            size=state.size,
            candidates=context.candidate_ids,
            retained=context.retained_ids,
            actions=tuple(context.action_log),
            pushed_out=pushed_out,
            raw_damage=raw_damage,
            shield_amount=shield_amount,
            shield_details=applicable,
            damage=damage,
            prosperity_base=context.prosperity_base,
            prosperity_delta=prosperity_delta,
            total_prosperity=state.prosperity,
            cumulative_damage=state.cumulative_damage,
            extinct=extinct,
            hand_after=tuple(item.instance_id for item in state.hand),
            columns_after=columns_after,
        )
        state.history.append(record)
        state.current_round = None
        return record

    def resolve_round(self, state: GameState, decision: RoundDecision) -> RoundRecord:
        """Atomic convenience API for bots and deterministic tests."""

        working = copy.deepcopy(state)
        self.start_round(working)
        self.choose_size(working, decision.size)
        self.retain_cards(working, decision.retain_card_ids)
        for action in decision.actions:
            self._apply_command(working, action)
        record = self.resolve_environment(working)
        self._commit(state, working)
        return record

    def run(self, policy: Any, state: GameState | None = None) -> GameState:
        state = state or self.new_game()
        while not self.is_finished(state):
            self.start_round(state)
            size = policy.choose_size(state, self) if hasattr(policy, "choose_size") else state.size
            self.choose_size(state, size)
            candidates = tuple(state.current_round.candidate_ids) if state.current_round else ()
            retained = (
                policy.choose_retained(state, candidates, self)
                if hasattr(policy, "choose_retained") else ()
            )
            self.retain_cards(state, retained)
            if hasattr(policy, "take_actions"):
                policy.take_actions(state, self)
            elif hasattr(policy, "choose_actions"):
                for action in policy.choose_actions(state, self):
                    self._apply_command(state, action)
            self.resolve_environment(state)
        return state

    # -------------------------------------------------------------- inspectors
    def eligible_extremes(self, state: GameState) -> tuple[ExtremeAdaptation, ...]:
        stage = self.current_stage(state)
        result = []
        for item in self.public_extremes(state):
            if item.id in state.claimed_extreme_ids or item.unlock_stage > stage:
                continue
            if any(self._requirements_met(state, index, item.required_root_tags) for index in range(len(state.columns))):
                result.append(item)
        return tuple(result)

    def public_extremes(self, state: GameState) -> tuple[ExtremeAdaptation, ...]:
        """All environment-attached routes, including currently locked ones."""

        result = []
        for attached in self.current_event(state).extreme_adaptations:
            item = attached if isinstance(attached, ExtremeAdaptation) else self.extremes.get(attached)
            if item is not None and item.id not in state.claimed_extreme_ids:
                result.append(item)
        return tuple(result)

    def column_tags(self, state: GameState, column_index: int) -> Counter[str]:
        self._validate_column(column_index)
        tags: Counter[str] = Counter()
        for played in state.columns[column_index].cards:
            tags.update(self.traits[played.card_id].root_tags)
        return tags

    # --------------------------------------------------------------- internals
    def _draw_candidates(self, state: GameState, count: int) -> list[CardInstance]:
        rng = random.Random()
        rng.setstate(state.rng_state)
        result: list[CardInstance] = []
        while len(result) < count:
            if not state.trait_deck:
                if not state.trait_discard:
                    break
                state.trait_deck = state.trait_discard
                state.trait_discard = []
                rng.shuffle(state.trait_deck)
            result.append(state.trait_deck.pop())
        state.rng_state = rng.getstate()
        return result

    def _current_candidate_instances(self, state: GameState) -> list[CardInstance]:
        assert state.current_round is not None
        by_id = {item.instance_id: item for item in state.trait_deck}
        by_id.update({item.instance_id: item for item in state.trait_discard})
        # Candidates have already been popped from the deck.  Keep their
        # objects in a private transient list on the context for exact identity.
        if state.current_round.candidate_instances:
            return list(state.current_round.candidate_instances)
        # Fallback for serialized contexts: candidate ids are normal ids.
        return [CardInstance(item_id, item_id) for item_id in state.current_round.candidate_ids]

    def _draw_to_hand(self, state: GameState, count: int) -> None:
        for item in self._draw_candidates(state, count):
            if len(state.hand) >= self.hand_limit:
                state.trait_discard.append(item)
            else:
                state.hand.append(item)

    def _take_hand_instance(self, state: GameState, card_id: str) -> CardInstance:
        for index, item in enumerate(state.hand):
            if item.instance_id == card_id or item.card_id == card_id:
                return state.hand.pop(index)
        raise InvalidDecision(f"card is not in hand: {card_id}")

    def _find_hand_instance(self, state: GameState, card_id: str) -> CardInstance:
        for item in state.hand:
            if item.instance_id == card_id or item.card_id == card_id:
                return item
        raise InvalidDecision(f"card is not in hand: {card_id}")

    def _requirements_met(self, state: GameState, column_index: int, requirements: dict[str, int] | Any) -> bool:
        tags = self.column_tags(state, column_index)
        return all(tags[tag] >= amount for tag, amount in requirements.items())

    def _on_play(self, card: TraitCard, state: GameState) -> None:
        if card.role is not CardRole.ON_PLAY or not card.options:
            return
        assert state.current_round is not None
        option = card.options[0]
        state.current_round.prosperity_base += option.prosperity
        state.current_round.shields.extend(option.shields)
        self._draw_to_hand(state, option.draw_cards)
        state.next_retention_bonus += option.retain_bonus

    def _apply_command(self, state: GameState, action: ActionCommand) -> None:
        if action.kind == "play":
            if action.card_id is None or action.column_index is None:
                raise InvalidDecision("play requires card_id and column_index")
            self.play_card(state, action.card_id, action.column_index)
        elif action.kind == "support":
            if action.card_id is None or action.column_index is None:
                raise InvalidDecision("support requires card_id and column_index")
            self.insert_support(state, action.card_id, action.column_index)
        elif action.kind == "activate":
            if action.column_index is None:
                raise InvalidDecision("activate requires column_index")
            self.activate(state, action.column_index, action.option_index)
        else:
            raise InvalidDecision(f"unknown action kind: {action.kind}")

    def _log_action(self, state: GameState, action: dict[str, Any]) -> None:
        assert state.current_round is not None
        state.current_round.action_log.append(action)

    def _validate_column(self, column_index: int) -> None:
        if not 0 <= column_index < self.column_count:
            raise InvalidDecision("column index is out of range")

    @staticmethod
    def _require_phase(state: GameState, phase: RoundPhase) -> None:
        if state.phase is not phase:
            raise InvalidDecision(f"operation requires phase {phase.value}, got {state.phase.value}")

    @staticmethod
    def _commit(target: GameState, source: GameState) -> None:
        target.__dict__.clear()
        target.__dict__.update(source.__dict__)

__all__ = ["GameEngine", "InvalidDecision"]
