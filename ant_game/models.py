"""Data models for the five-round ant adaptation prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Mapping


class Size(IntEnum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2
    GIANT = 3

    @property
    def prosperity_multiplier(self) -> int:
        return int(self)

    @property
    def retention(self) -> int:
        return (4, 3, 2, 1)[int(self)]


class CardRole(str, Enum):
    ACTION = "action"
    SUPPORT = "support"
    STARTER = "starter"
    ON_PLAY = "on_play"


class RoundPhase(str, Enum):
    IDLE = "idle"
    SIZE = "size"
    RETAIN = "retain"
    ACTIONS = "actions"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class ShieldSpec:
    """A one-round defense against exactly one recurring problem."""

    problem_id: str
    amount: int

    def __post_init__(self) -> None:
        if not isinstance(self.problem_id, str) or not self.problem_id:
            raise ValueError("a shield must name exactly one problem")
        if self.amount <= 0:
            raise ValueError("shield amount must be positive")


@dataclass(frozen=True, slots=True)
class ActionOption:
    """One selectable result of an ACTION card."""

    prosperity: int = 0
    shields: tuple[ShieldSpec, ...] = ()
    draw_cards: int = 0
    text: str = ""


@dataclass(frozen=True, slots=True)
class TraitCard:
    id: str
    name: str
    root_tags: frozenset[str] = frozenset()
    role: CardRole = CardRole.ACTION
    activation_requirements: Mapping[str, int] = field(default_factory=dict)
    options: tuple[ActionOption, ...] = ()
    # Optional weak effects used when a payoff's activation requirements are
    # not met.  The card remains playable, but the player does not get the
    # full payoff.  This is deliberately data rather than a new effect type.
    fallback_options: tuple[ActionOption, ...] = ()
    source_taxon: str = ""
    biology_basis: str = ""
    biology_source: str = ""
    design_role: str = "Foundation"
    text: str = ""

    @property
    def tags(self) -> frozenset[str]:
        return self.root_tags


@dataclass(frozen=True, slots=True)
class OptimizationRequirement:
    """An environment-specific board target, printed on the environment card."""

    name: str
    required_root_tags: Mapping[str, int] = field(default_factory=dict)
    source_taxon: str = ""
    biology_basis: str = ""
    biology_source: str = ""
    text: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("optimization must have a name")
        if not self.required_root_tags:
            raise ValueError("optimization must require at least one root tag")
        if any(not tag or amount <= 0 for tag, amount in self.required_root_tags.items()):
            raise ValueError("optimization tag requirements must be positive")


@dataclass(frozen=True, slots=True)
class ProblemRollRule:
    """How one independent ecological problem is rolled for a round."""

    rolls: int = 1
    bonus: int = 0

    def __post_init__(self) -> None:
        if self.rolls < 1:
            raise ValueError("problem roll count must be positive")
        if self.bonus < 0:
            raise ValueError("problem roll bonus must not be negative")


@dataclass(frozen=True, slots=True)
class EnvironmentCard:
    id: str
    name: str
    optimizations: tuple[OptimizationRequirement, ...] = ()
    problem_roll_rules: Mapping[str, ProblemRollRule] = field(default_factory=dict)
    text: str = ""

    def __post_init__(self) -> None:
        if not self.id or not self.name:
            raise ValueError("environment must have an id and name")
        if not isinstance(self.optimizations, tuple):
            object.__setattr__(self, "optimizations", tuple(self.optimizations))
        if not isinstance(self.problem_roll_rules, dict):
            object.__setattr__(self, "problem_roll_rules", dict(self.problem_roll_rules))
        if len(self.optimizations) > 2:
            raise ValueError("an environment may have at most two optimizations")
        if any(not isinstance(item, OptimizationRequirement) for item in self.optimizations):
            raise TypeError("optimizations must contain OptimizationRequirement values")
        if any(not isinstance(problem, str) or not problem for problem in self.problem_roll_rules):
            raise ValueError("problem roll rule ids must be non-empty strings")
        if any(not isinstance(rule, ProblemRollRule) for rule in self.problem_roll_rules.values()):
            raise TypeError("problem roll rules must contain ProblemRollRule values")

# The old public name is kept while callers migrate from disaster cards to
# environment cards.  Environment cards deliberately have no hazard/problem
# classification; recurring problems are rolled independently each round.
DisasterCard = EnvironmentCard


@dataclass(slots=True)
class CardInstance:
    instance_id: str
    card_id: str


@dataclass(slots=True)
class PlayedCard:
    instance_id: str
    card_id: str
    is_support: bool = False
    activated_round: int | None = None


@dataclass(slots=True)
class ColumnState:
    cards: list[PlayedCard] = field(default_factory=list)

    @property
    def top(self) -> PlayedCard | None:
        return self.cards[-1] if self.cards else None


@dataclass(slots=True)
class RoundContext:
    round_number: int
    disaster_id: str
    # problem_rolls is the effective value used by resolution.  The other
    # mappings preserve the complete die audit trail for UI and replays.
    problem_rolls: dict[str, int] = field(default_factory=dict)
    problem_raw_rolls: dict[str, tuple[int, ...]] = field(default_factory=dict)
    problem_selected_rolls: dict[str, int] = field(default_factory=dict)
    problem_modifiers: dict[str, int] = field(default_factory=dict)
    size_before: Size = Size.SMALL
    candidate_ids: tuple[str, ...] = ()
    candidate_instances: list[CardInstance] = field(default_factory=list)
    retained_ids: tuple[str, ...] = ()
    action_log: list[dict[str, Any]] = field(default_factory=list)
    prosperity_base: int = 0
    shields: list[ShieldSpec] = field(default_factory=list)
    bonus_draws: int = 0


@dataclass(frozen=True, slots=True)
class ActionCommand:
    kind: str
    column_index: int | None = None
    card_id: str | None = None
    option_index: int = 0


@dataclass(frozen=True, slots=True)
class RoundDecision:
    size: Size
    retain_card_ids: tuple[str, ...] = ()
    actions: tuple[ActionCommand, ...] = ()


@dataclass(frozen=True, slots=True)
class RoundRecord:
    round_number: int
    disaster_id: str
    size_before: Size
    size: Size
    candidates: tuple[str, ...]
    retained: tuple[str, ...]
    actions: tuple[dict[str, Any], ...]
    pushed_out: tuple[str, ...]
    problem_rolls: Mapping[str, int]
    problem_raw_rolls: Mapping[str, tuple[int, ...]]
    problem_selected_rolls: Mapping[str, int]
    problem_modifiers: Mapping[str, int]
    defense_by_problem: Mapping[str, int]
    unblocked_by_problem: Mapping[str, int]
    penalty_by_problem: Mapping[str, int]
    problem_penalty: int
    prosperity_base: int
    prosperity_delta: int
    score_before: int
    score_after_prosperity: int
    score_after_problems: int
    optimization_met: bool
    optimization_requirements: tuple[Mapping[str, int], ...]
    optimization_results: tuple[bool, ...]
    optimization_actual_tags: Mapping[str, int]
    optimization_half_loss: int
    total_prosperity: int
    hand_after: tuple[str, ...]
    columns_after: tuple[tuple[str, ...], ...]


@dataclass(slots=True)
class GameState:
    seed: int
    round_number: int = 0
    size: Size = Size.SMALL
    prosperity: int = 0
    hand: list[CardInstance] = field(default_factory=list)
    columns: list[ColumnState] = field(default_factory=list)
    disaster_ids: tuple[str, ...] = ()
    trait_deck: list[CardInstance] = field(default_factory=list)
    trait_discard: list[CardInstance] = field(default_factory=list)
    history: list[RoundRecord] = field(default_factory=list)
    phase: RoundPhase = RoundPhase.IDLE
    current_round: RoundContext | None = None
    rng_state: Any = None

    @property
    def finished(self) -> bool:
        return self.phase is RoundPhase.COMPLETE
