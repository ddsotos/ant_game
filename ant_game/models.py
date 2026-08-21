"""Data models for the v0.3 Daybreak-style ant evolution prototype."""

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
    EXTINCT = "extinct"


@dataclass(frozen=True, slots=True)
class ShieldSpec:
    hazard_tags: frozenset[str] = frozenset()
    amount: int = 0


@dataclass(frozen=True, slots=True)
class ActionOption:
    """One selectable result of an ACTION card."""

    prosperity: int = 0
    shields: tuple[ShieldSpec, ...] = ()
    draw_cards: int = 0
    retain_bonus: int = 0
    text: str = ""


@dataclass(frozen=True, slots=True)
class TraitCard:
    id: str
    name: str
    root_tags: frozenset[str] = frozenset()
    role: CardRole = CardRole.ACTION
    activation_requirements: Mapping[str, int] = field(default_factory=dict)
    options: tuple[ActionOption, ...] = ()
    source_taxon: str = ""
    biology_basis: str = ""
    biology_source: str = ""
    design_role: str = "Foundation"
    text: str = ""

    @property
    def tags(self) -> frozenset[str]:
        return self.root_tags


@dataclass(frozen=True, slots=True)
class ExtremeAdaptation:
    id: str
    name: str
    root_tags: frozenset[str] = frozenset()
    role: CardRole = CardRole.ACTION
    activation_requirements: Mapping[str, int] = field(default_factory=dict)
    options: tuple[ActionOption, ...] = ()
    required_root_tags: Mapping[str, int] = field(default_factory=dict)
    unlock_stage: int = 1
    source_taxon: str = ""
    biology_basis: str = ""
    biology_source: str = ""
    text: str = ""

    def as_trait(self) -> TraitCard:
        return TraitCard(
            id=self.id,
            name=self.name,
            root_tags=self.root_tags,
            role=self.role,
            activation_requirements=self.activation_requirements,
            options=self.options,
            source_taxon=self.source_taxon,
            biology_basis=self.biology_basis,
            biology_source=self.biology_source,
            design_role="Extreme",
            text=self.text,
        )


class EventKind(str, Enum):
    ENVIRONMENT = "environment"


@dataclass(frozen=True, slots=True)
class EventCard:
    id: str
    name: str
    hazard_tags: frozenset[str] = frozenset()
    stage_damage: Mapping[int, int] = field(default_factory=dict)
    extreme_adaptations: tuple[str | ExtremeAdaptation, ...] = ()
    text: str = ""

    @property
    def tags(self) -> frozenset[str]:
        return self.hazard_tags


@dataclass(slots=True)
class CardInstance:
    instance_id: str
    card_id: str
    origin_event_id: str | None = None


@dataclass(slots=True)
class PlayedCard:
    instance_id: str
    card_id: str
    origin_event_id: str | None = None
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
    stage: int
    environment_id: str
    size_before: Size = Size.SMALL
    candidate_ids: tuple[str, ...] = ()
    candidate_instances: list[CardInstance] = field(default_factory=list)
    retained_ids: tuple[str, ...] = ()
    action_log: list[dict[str, Any]] = field(default_factory=list)
    prosperity_base: int = 0
    shields: list[ShieldSpec] = field(default_factory=list)
    bonus_draws: int = 0
    retention_bonus: int = 0


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
    stage: int
    environment_id: str
    size_before: Size
    size: Size
    candidates: tuple[str, ...]
    retained: tuple[str, ...]
    actions: tuple[dict[str, Any], ...]
    pushed_out: tuple[str, ...]
    raw_damage: int
    shield_amount: int
    shield_details: tuple[ShieldSpec, ...]
    damage: int
    prosperity_base: int
    prosperity_delta: int
    total_prosperity: int
    cumulative_damage: int
    extinct: bool
    hand_after: tuple[str, ...]
    columns_after: tuple[tuple[str, ...], ...]


@dataclass(slots=True)
class GameState:
    seed: int
    round_number: int = 0
    size: Size = Size.SMALL
    prosperity: int = 0
    cumulative_damage: int = 0
    hand: list[CardInstance] = field(default_factory=list)
    columns: list[ColumnState] = field(default_factory=list)
    environment_id: str = ""
    claimed_extreme_ids: set[str] = field(default_factory=set)
    trait_deck: list[CardInstance] = field(default_factory=list)
    trait_discard: list[CardInstance] = field(default_factory=list)
    history: list[RoundRecord] = field(default_factory=list)
    phase: RoundPhase = RoundPhase.IDLE
    current_round: RoundContext | None = None
    rng_state: Any = None
    next_retention_bonus: int = 0

    @property
    def finished(self) -> bool:
        return self.phase in (RoundPhase.COMPLETE, RoundPhase.EXTINCT)
