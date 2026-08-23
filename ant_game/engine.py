"""Deterministic, UI-independent rules engine."""

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
    EnvironmentCard,
    GameState,
    PlayedCard,
    RoundContext,
    RoundDecision,
    RoundPhase,
    RoundRecord,
    ProblemRollRule,
    Size,
    TraitCard,
)


# These problems are present every round, independently of the forecast
# environment card.  Their ids are also the ids printed on typed shields.
PROBLEM_IDS: tuple[str, ...] = ("raid", "sanitation")


class InvalidDecision(ValueError):
    """Raised when a command is not legal in the current phase/state."""


class GameEngine:
    """Five-round game using five public, non-repeating environments."""

    def __init__(
        self,
        traits: Iterable[TraitCard],
        disasters: Iterable[EnvironmentCard],
        seed: int = 0,
        *,
        columns: int = 3,
        column_capacity: int | None = None,
        retention_curve: str | dict[Size, int] = "aggressive",
        hand_limit: int = 8,
        rounds: int = 5,
        starter_ids: Sequence[str] | None = None,
    ) -> None:
        if columns not in (3, 4):
            raise ValueError("columns must be 3 or 4")
        if rounds != 5:
            raise ValueError("the prototype is fixed at five rounds")
        if hand_limit < 0:
            raise ValueError("hand_limit must be non-negative")
        self.seed = seed
        self.rounds = rounds
        self.column_count = columns
        self.column_capacity = column_capacity if column_capacity is not None else (5 if columns == 3 else 4)
        if self.column_capacity < 1:
            raise ValueError("column_capacity must be positive")
        self.hand_limit = hand_limit

        cards = list(traits)
        disaster_list = list(disasters)
        self.traits = {card.id: card for card in cards}
        self.disasters = {card.id: card for card in disaster_list}
        if not self.traits:
            raise ValueError("at least one trait is required")
        if len(disaster_list) < self.rounds:
            raise ValueError("at least five disasters are required")
        if len(self.traits) != len(cards) or len(self.disasters) != len(disaster_list):
            raise ValueError("trait and disaster ids must be unique")
        self.standard_disaster_ids = tuple(card.id for card in disaster_list if card.deck == "standard")
        self.finale_disaster_ids = tuple(card.id for card in disaster_list if card.deck == "finale")
        if self.finale_disaster_ids and len(self.standard_disaster_ids) < self.rounds - 1:
            raise ValueError("a finale set requires at least four standard environments")

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

        self.normal_ids = tuple(card.id for card in cards if card.id not in self.starter_ids)
        if len(self.normal_ids) < 6:
            raise ValueError("at least six normal non-starter cards are required")

    # ------------------------------------------------------------------ setup
    def new_game(self) -> GameState:
        rng = random.Random(self.seed)
        if self.finale_disaster_ids:
            # Keep the finale physically last.  Sampling the two decks in a
            # fixed order makes the complete forecast reproducible from seed.
            standard_ids = tuple(rng.sample(self.standard_disaster_ids, self.rounds - 1))
            finale_id = rng.choice(self.finale_disaster_ids)
            disaster_ids = (*standard_ids, finale_id)
        else:
            # Backwards-compatible path for small test fixtures and callers
            # that predate the standard/finale split.
            disaster_ids = tuple(rng.sample(tuple(self.disasters), self.rounds))
        deck = [CardInstance(card_id, card_id) for card_id in self.normal_ids]
        rng.shuffle(deck)
        columns = [ColumnState() for _ in range(self.column_count)]
        for index, card_id in enumerate(self.starter_ids):
            columns[index].cards.append(PlayedCard(instance_id=card_id, card_id=card_id))
        return GameState(
            seed=self.seed,
            size=Size.SMALL,
            columns=columns,
            disaster_ids=disaster_ids,
            trait_deck=deck,
            rng_state=rng.getstate(),
        )

    def is_finished(self, state: GameState) -> bool:
        return state.finished

    def legal_sizes(self, state: GameState) -> tuple[Size, ...]:
        value = int(state.size)
        return tuple(Size(index) for index in range(max(0, value - 1), min(3, value + 1) + 1))

    def current_disaster(self, state: GameState) -> EnvironmentCard:
        if state.current_round is not None:
            disaster_id = state.current_round.disaster_id
        elif state.disaster_ids:
            disaster_id = state.disaster_ids[min(state.round_number, self.rounds - 1)]
        else:
            raise InvalidDecision("state has no disaster forecast")
        try:
            return self.disasters[disaster_id]
        except KeyError as exc:
            raise InvalidDecision("state has no valid current disaster") from exc

    def retention_limit(self, state: GameState) -> int:
        return self.retention_curve[state.size] + state.pending_retention_bonus

    # ------------------------------------------------------------- round flow
    def start_round(self, state: GameState) -> EnvironmentCard:
        self._require_phase(state, RoundPhase.IDLE)
        if state.round_number >= self.rounds:
            state.phase = RoundPhase.COMPLETE
            raise InvalidDecision("the game is already finished")
        disaster = self.disasters[state.disaster_ids[state.round_number]]
        rng = random.Random()
        rng.setstate(state.rng_state)
        # Independent problems are d4 by default.  An environment may make a
        # problem more severe by rolling several d4s (keep the highest by
        # default, or sum them for a finale) or by adding a fixed bonus.
        # Preserve every part of this calculation for the UI/replay instead
        # of only keeping the final number.
        rules = {
            problem: disaster.problem_roll_rules.get(problem, ProblemRollRule())
            for problem in PROBLEM_IDS
        }
        raw_rolls: dict[str, tuple[int, ...]] = {}
        selected_rolls: dict[str, int] = {}
        modifiers: dict[str, int] = {}
        problem_rolls: dict[str, int] = {}
        roll_sources: dict[str, str] = {}
        roll_combines: dict[str, str] = {}
        previous = state.history[-1].problem_rolls if state.history else {}
        for problem, rule in rules.items():
            roll_combines[problem] = rule.combine
            if rule.previous_round_bonus is not None and problem in previous:
                # Forecasted carry-over is deterministic and consumes no RNG.
                raw_rolls[problem] = ()
                selected_rolls[problem] = previous[problem]
                modifiers[problem] = rule.previous_round_bonus
                problem_rolls[problem] = previous[problem] + rule.previous_round_bonus
                roll_sources[problem] = "previous_round"
                continue
            count = 1 if rule.previous_round_bonus is not None else rule.rolls
            raw = tuple(rng.randint(1, 4) for _ in range(count))
            raw_rolls[problem] = raw
            selected_rolls[problem] = sum(raw) if rule.combine == "sum" else max(raw)
            modifiers[problem] = rule.previous_round_bonus if rule.previous_round_bonus is not None else rule.bonus
            problem_rolls[problem] = selected_rolls[problem] + modifiers[problem]
            roll_sources[problem] = "d4_first_round" if rule.previous_round_bonus is not None else "dice"
        state.rng_state = rng.getstate()
        state.current_round = RoundContext(
            round_number=state.round_number + 1,
            disaster_id=disaster.id,
            problem_rolls=problem_rolls,
            problem_raw_rolls=raw_rolls,
            problem_selected_rolls=selected_rolls,
            problem_modifiers=modifiers,
            problem_roll_sources=roll_sources,
            problem_roll_combines=roll_combines,
            size_before=state.size,
            base_prosperity=5,
            prosperity_base=5,
        )
        # Stored cards start paying only from the round after they are
        # attached, so income is booked when this round opens.
        self._add_prosperity(state, self.storage_income(state), source="storage")
        state.phase = RoundPhase.SIZE
        return disaster

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
        candidate_bonus = state.pending_candidate_bonus
        state.pending_candidate_bonus = 0
        draw_count = 6 + candidate_bonus
        candidates = self._draw_candidates(state, draw_count)
        state.current_round.candidate_ids = tuple(item.instance_id for item in candidates)
        state.current_round.candidate_instances = list(candidates)
        state.current_round.candidate_draw_count = len(candidates)
        state.phase = RoundPhase.RETAIN
        return state.current_round.candidate_ids

    def retain_cards(self, state: GameState, card_ids: Sequence[str] = ()) -> tuple[str, ...]:
        self._require_phase(state, RoundPhase.RETAIN)
        assert state.current_round is not None
        requested = tuple(card_ids)
        if len(set(requested)) != len(requested):
            raise InvalidDecision("a card may only be retained once")
        candidates = set(state.current_round.candidate_ids)
        if any(card_id not in candidates for card_id in requested):
            raise InvalidDecision("retained cards must be current candidates")
        limit = min(self.retention_limit(state), self.hand_limit - len(state.hand))
        if len(requested) > limit:
            raise InvalidDecision("retained cards exceed the size or hand limit")

        candidate_instances = {item.instance_id: item for item in self._current_candidate_instances(state)}
        state.hand.extend(candidate_instances[instance_id] for instance_id in requested)
        kept = set(requested)
        state.trait_discard.extend(
            item for item in self._current_candidate_instances(state) if item.instance_id not in kept
        )
        state.current_round.retained_ids = requested
        # A retention bonus is deliberately a one-shot effect.  Once this
        # round's hand choice is made it cannot leak into later rounds.
        state.pending_retention_bonus = 0
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
        column.cards.append(PlayedCard(instance_id=instance.instance_id, card_id=instance.card_id))
        if len(column.cards) > self.column_capacity:
            pushed_card = column.cards.pop(0)
            pushed.append(pushed_card.instance_id)
            state.trait_discard.append(CardInstance(pushed_card.instance_id, pushed_card.card_id))
            state.trait_discard.extend(pushed_card.stored_cards)
        self._on_play(card, state)
        self._log_action(
            state,
            {"kind": "play", "card_id": card_id, "column": column_index, "pushed_out": tuple(pushed)},
        )
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
        column.cards.insert(
            len(column.cards) - 1,
            PlayedCard(instance_id=instance.instance_id, card_id=instance.card_id, is_support=True),
        )
        pushed = None
        if len(column.cards) > self.column_capacity:
            pushed = column.cards.pop(0)
            state.trait_discard.append(CardInstance(pushed.instance_id, pushed.card_id))
            state.trait_discard.extend(pushed.stored_cards)
        self._log_action(
            state,
            {
                "kind": "support",
                "card_id": card_id,
                "column": column_index,
                "pushed_out": pushed.instance_id if pushed else None,
            },
        )

    def activate(
        self,
        state: GameState,
        column_index: int,
        option_index: int = 0,
        target_card_id: str | None = None,
    ) -> ActionOption:
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
        requirements_met = self._activation_requirements_met(state, column_index, card.activation_requirements)
        tier = "strong"
        options = card.options
        if not requirements_met:
            if not card.fallback_options:
                raise InvalidDecision("the other cards in the column do not meet the activation requirements")
            options = card.fallback_options
            tier = "fallback"
        if not 0 <= option_index < len(options):
            raise InvalidDecision("action option index is out of range")
        option = options[option_index]
        target_required = option.store_hand_card or option.recover_lower_card
        if target_required and target_card_id is None:
            raise InvalidDecision("this effect requires a target card")
        if not target_required and target_card_id is not None:
            raise InvalidDecision("this effect does not accept a target card")
        if option.store_hand_card:
            target = self._find_hand_instance(state, target_card_id)
            if target.instance_id == top.instance_id:
                raise InvalidDecision("a card cannot store itself")
            target = self._take_hand_instance(state, target.instance_id)
            top.stored_cards.append(target)
            top.storage_income_per_card = option.storage_income_per_card
        elif option.recover_lower_card:
            if state.current_round.recovered_lower_card_id is not None:
                raise InvalidDecision("only one lower card may be recovered per round")
            self._recover_lower_card(state, column_index, target_card_id)
            state.current_round.recovered_lower_card_id = target_card_id
        top.activated_round = state.current_round.round_number
        prosperity = self._apply_option(option, state)
        self._log_action(
            state,
            {
                "kind": "activate",
                "card_id": top.instance_id,
                "column": column_index,
                "option_index": option_index,
                "tier": tier,
                "prosperity": prosperity,
                "shields": tuple(option.shields),
                "retention_bonus": option.retention_bonus,
                "next_candidate_bonus": option.next_candidate_bonus,
                "tag_prosperity": tuple(option.tag_prosperity),
                "target_card_id": target_card_id,
                "recover_lower_card": option.recover_lower_card,
            },
        )
        return option

    def resolve_environment(self, state: GameState) -> RoundRecord:
        """Resolve prosperity, recurring problems, then optimization."""

        self._require_phase(state, RoundPhase.ACTIONS)
        assert state.current_round is not None
        context = state.current_round
        disaster = self.current_disaster(state)
        defense_by_problem: dict[str, int] = {}
        unblocked_by_problem: dict[str, int] = {}
        penalty_by_problem: dict[str, int] = {}
        for problem in PROBLEM_IDS:
            defense = sum(shield.amount for shield in context.shields if shield.problem_id == problem)
            unblocked = max(0, context.problem_rolls[problem] - defense)
            penalty = 0 if unblocked == 0 else 2 ** unblocked
            defense_by_problem[problem] = defense
            unblocked_by_problem[problem] = unblocked
            penalty_by_problem[problem] = penalty
        problem_penalty = sum(penalty_by_problem.values())
        # Problems tax this round's unmultiplied prosperity pool first.  Only
        # the surviving pool is then amplified by colony size; a disaster
        # cannot erase prosperity earned in earlier rounds.
        score_before = state.prosperity
        prosperity_pool_before = context.prosperity_base
        prosperity_pool_after = max(0, prosperity_pool_before - problem_penalty)
        prosperity_delta = prosperity_pool_after * state.size.prosperity_multiplier
        context.problem_penalty = problem_penalty
        context.prosperity_pool_before_problems = prosperity_pool_before
        context.prosperity_pool_after_problems = prosperity_pool_after
        context.prosperity_delta = prosperity_delta
        state.prosperity += prosperity_delta
        score_after_prosperity = state.prosperity
        # Kept as a named record field for clients that used the old audit
        # shape.  Problems have already been applied to the round pool above.
        score_after_problems = state.prosperity

        actual_tags = self.board_tags(state)
        optimization_requirements = tuple(
            dict(optimization.required_root_tags)
            for optimization in disaster.optimizations
        )
        optimization_results = tuple(
            all(actual_tags[tag] >= amount for tag, amount in requirements.items())
            for requirements in optimization_requirements
        )
        # An environment without an optimization is intentionally a pressure
        # card, not an automatic score-halving trap.
        optimization_met = not optimization_results or any(optimization_results)
        optimization_half_loss = 0
        if not optimization_met:
            score_before_half = state.prosperity
            state.prosperity //= 2
            optimization_half_loss = score_before_half - state.prosperity

        state.round_number += 1
        state.phase = RoundPhase.COMPLETE if state.round_number >= self.rounds else RoundPhase.IDLE
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
            disaster_id=context.disaster_id,
            size_before=context.size_before,
            size=state.size,
            candidates=context.candidate_ids,
            retained=context.retained_ids,
            actions=tuple(context.action_log),
            pushed_out=pushed_out,
            problem_rolls=dict(context.problem_rolls),
            problem_raw_rolls=dict(context.problem_raw_rolls),
            problem_selected_rolls=dict(context.problem_selected_rolls),
            problem_modifiers=dict(context.problem_modifiers),
            problem_roll_sources=dict(context.problem_roll_sources),
            problem_roll_combines=dict(context.problem_roll_combines),
            defense_by_problem=defense_by_problem,
            unblocked_by_problem=unblocked_by_problem,
            penalty_by_problem=penalty_by_problem,
            problem_penalty=problem_penalty,
            base_prosperity=context.base_prosperity,
            activation_prosperity=context.activation_prosperity,
            card_prosperity=context.card_prosperity,
            storage_prosperity=context.storage_prosperity,
            tag_prosperity=context.tag_prosperity,
            prosperity_base=context.prosperity_base,
            prosperity_pool_before_problems=prosperity_pool_before,
            prosperity_pool_after_problems=prosperity_pool_after,
            prosperity_delta=prosperity_delta,
            score_before=score_before,
            score_after_prosperity=score_after_prosperity,
            score_after_problems=score_after_problems,
            optimization_met=optimization_met,
            optimization_requirements=optimization_requirements,
            optimization_results=optimization_results,
            optimization_actual_tags=dict(actual_tags),
            optimization_half_loss=optimization_half_loss,
            total_prosperity=state.prosperity,
            hand_after=tuple(item.instance_id for item in state.hand),
            columns_after=columns_after,
        )
        state.history.append(record)
        state.current_round = None
        return record

    def resolve_round(self, state: GameState, decision: RoundDecision) -> RoundRecord:
        """Atomic convenience API for deterministic callers."""

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
            retained = policy.choose_retained(state, candidates, self) if hasattr(policy, "choose_retained") else ()
            self.retain_cards(state, retained)
            if hasattr(policy, "take_actions"):
                policy.take_actions(state, self)
            elif hasattr(policy, "choose_actions"):
                for action in policy.choose_actions(state, self):
                    self._apply_command(state, action)
            self.resolve_environment(state)
        return state

    # -------------------------------------------------------------- inspectors
    def column_tags(self, state: GameState, column_index: int) -> Counter[str]:
        self._validate_column(column_index)
        tags: Counter[str] = Counter()
        for played in state.columns[column_index].cards:
            tags.update(self.traits[played.card_id].counted_root_tags)
        return tags

    def activation_tags(self, state: GameState, column_index: int) -> Counter[str]:
        """Tags supplied to the top card, excluding that physical card itself."""

        self._validate_column(column_index)
        tags: Counter[str] = Counter()
        for played in state.columns[column_index].cards[:-1]:
            tags.update(self.traits[played.card_id].counted_root_tags)
        return tags

    def board_tags(self, state: GameState) -> Counter[str]:
        tags: Counter[str] = Counter()
        for index in range(len(state.columns)):
            tags.update(self.column_tags(state, index))
        return tags

    def storage_income(self, state: GameState) -> int:
        """Income generated by face-down cards stored on the board."""

        return sum(
            len(played.stored_cards) * played.storage_income_per_card
            for column in state.columns
            for played in column.cards
        )

    def _recover_lower_card(self, state: GameState, column_index: int, target_card_id: str) -> CardInstance:
        if len(state.hand) >= self.hand_limit:
            raise InvalidDecision("hand is full")
        assert state.current_round is not None
        column = state.columns[column_index]
        for index, played in enumerate(column.cards[:-1]):
            if played.instance_id != target_card_id and played.card_id != target_card_id:
                continue
            if played.is_support or self.traits[played.card_id].role is CardRole.STARTER:
                raise InvalidDecision("support and starter cards cannot be recovered")
            if played.stored_cards:
                raise InvalidDecision("a stored host cannot be recovered")
            if played.activated_round == state.current_round.round_number:
                raise InvalidDecision("an activated card cannot be recovered this round")
            column.cards.pop(index)
            recovered = CardInstance(played.instance_id, played.card_id)
            state.hand.append(recovered)
            return recovered
        raise InvalidDecision("target must be an eligible lower card in this column")

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
        if state.current_round.candidate_instances:
            return list(state.current_round.candidate_instances)
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

    def _activation_requirements_met(
        self, state: GameState, column_index: int, requirements: dict[str, int] | Any
    ) -> bool:
        tags = self.activation_tags(state, column_index)
        return all(tags[tag] >= amount for tag, amount in requirements.items())

    def _on_play(self, card: TraitCard, state: GameState) -> None:
        if card.role is not CardRole.ON_PLAY or not card.options:
            return
        assert state.current_round is not None
        self._apply_option(card.options[0], state, source="card")

    def _add_prosperity(self, state: GameState, amount: int, *, source: str) -> None:
        assert state.current_round is not None
        if amount <= 0:
            return
        state.current_round.prosperity_base += amount
        if source == "activation":
            state.current_round.activation_prosperity += amount
        elif source == "card":
            state.current_round.card_prosperity += amount
        elif source == "storage":
            state.current_round.storage_prosperity += amount
        elif source == "tag":
            state.current_round.tag_prosperity += amount
        else:
            raise ValueError(f"unknown prosperity source: {source}")

    def _apply_option(self, option: ActionOption, state: GameState, *, source: str = "activation") -> int:
        """Apply an option and return its resolved prosperity contribution.

        Tag-scaled prosperity is evaluated against the complete board at the
        moment of activation, while retention is explicitly deferred to the
        next round's retain step.
        """

        assert state.current_round is not None
        tag_total = sum(
            self.board_tags(state).get(tag, 0) * coefficient
            for tag, coefficient in option.tag_prosperity
        )
        tag_bonus = tag_total // option.tag_prosperity_divisor
        if option.tag_prosperity_cap is not None:
            tag_bonus = min(tag_bonus, option.tag_prosperity_cap)
        self._add_prosperity(state, option.prosperity, source=source)
        self._add_prosperity(state, tag_bonus, source="tag")
        prosperity = option.prosperity + tag_bonus
        state.current_round.shields.extend(option.shields)
        state.current_round.bonus_draws += option.draw_cards
        state.pending_retention_bonus = min(2, state.pending_retention_bonus + option.retention_bonus)
        state.pending_candidate_bonus = min(2, state.pending_candidate_bonus + option.next_candidate_bonus)
        if option.draw_cards:
            self._draw_to_hand(state, option.draw_cards)
        return prosperity

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
            self.activate(state, action.column_index, action.option_index, action.target_card_id)
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


__all__ = ["GameEngine", "InvalidDecision", "PROBLEM_IDS"]
