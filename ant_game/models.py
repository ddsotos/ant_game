"""Data models shared by content, the engine, bots, and inspection tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Mapping


class Size(IntEnum):
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    HUGE = 4

    @property
    def prosperity(self) -> int:
        return (1, 2, 3, 5, 6)[int(self)]

    @property
    def evolution_draw(self) -> int:
        return (6, 5, 4, 3, 2)[int(self)]


class EventKind(str, Enum):
    WAVE = "wave"
    SHOCK = "shock"


@dataclass(frozen=True, slots=True)
class TraitCard:
    id: str
    name: str
    evolution_load: int = 0
    tags: frozenset[str] = frozenset()
    mitigation_tags: Mapping[str, int] = field(default_factory=dict)
    mitigation_flat: int = 0
    prosperity_bonus: int = 0
    prosperity_tags: Mapping[str, int] = field(default_factory=dict)
    latent: bool = False
    trigger_tags: frozenset[str] = frozenset()
    trigger_min_stage: int = 1
    activated_evolution_load: int | None = None
    consume_on_trigger: bool = False
    effect_id: str | None = None
    text: str = ""
    # One-round evolution capacity consumed when this card is acquired.
    # This is deliberately distinct from persistent evolution_load.
    play_cost: int = 1


@dataclass(frozen=True, slots=True)
class EventCard:
    id: str
    name: str
    kind: EventKind = EventKind.WAVE
    tags: frozenset[str] = frozenset()
    stage_damage: Mapping[int, int] = field(
        default_factory=lambda: {1: 0, 2: 4, 3: 10, 4: 2}
    )
    shock_damage: int = 0
    # Signed size-specific modifier; negative values represent avoidance/relief.
    size_damage: Mapping[Size, int] = field(default_factory=dict)
    size_damage_min_stage: int = 1
    peak_size_damage: Mapping[Size, int] = field(default_factory=dict)
    prosperity_modifier: int = 0
    sequence_prev_tag: str | None = None
    sequence_damage_bonus: int = 0
    effect_id: str | None = None
    text: str = ""


@dataclass(slots=True)
class TraitState:
    card_id: str
    active: bool = True


@dataclass(frozen=True, slots=True)
class EvolutionChoice:
    """A complete evolution action for one round.

    ``acquire_trait_ids`` are drawn candidates to keep.  If the five-slot
    limit is exceeded, exactly the corresponding number of held traits must
    be listed in ``discard_trait_ids``.  Unused evolution capacity is lost.
    """

    acquire_trait_ids: tuple[str, ...] = ()
    discard_trait_ids: tuple[str, ...] = ()
    shed_trait_id: str | None = None


@dataclass(frozen=True, slots=True)
class RoundDecision:
    size: Size
    activate_latent_ids: tuple[str, ...] = ()
    acquire_trait_id: str | None = None
    acquire_index: int | None = None
    discard_trait_id: str | None = None
    # Voluntary evolution action when this round produced no candidates.
    # Unlike ``discard_trait_id``, this is not an acquire/exchange action.
    shed_trait_id: str | None = None
    # New multi-card API.  The singular fields above remain for v0.1 callers.
    acquire_trait_ids: tuple[str, ...] = ()
    discard_trait_ids: tuple[str, ...] = ()
    evolution: EvolutionChoice | None = None
    # Alias accepted by callers that prefer an explicit field name.
    evolution_choice: EvolutionChoice | None = None


@dataclass(frozen=True, slots=True)
class RoundRecord:
    round_number: int
    size_before: Size
    size: Size
    event_id: str
    event_name: str
    event_kind: EventKind
    event_stage: int | None
    previous_event_id: str | None
    sequence_triggered: bool
    traits_before: tuple[str, ...]
    latent_activated: tuple[str, ...]
    latent_consumed: tuple[str, ...]
    raw_damage: int
    mitigation: int
    damage: int
    base_prosperity: int
    prosperity_modifier: int
    growth_cost: int
    raw_prosperity_delta: int
    actual_prosperity_delta: int
    # Backwards-compatible display name; this now may be negative.
    prosperity_gained: int
    total_prosperity: int
    evolution_load: int
    evolution_draw_count: int
    trait_candidates: tuple[str, ...]
    acquired_trait_id: str | None
    discarded_trait_id: str | None
    acquired_trait_ids: tuple[str, ...]
    discarded_trait_ids: tuple[str, ...]
    shed_trait_id: str | None
    evolution_budget: int
    evolution_budget_spent: int
    evolution_budget_utilization: float
    traits_after: tuple[str, ...]


@dataclass(slots=True)
class GameState:
    seed: int
    round_number: int = 0
    size: Size = Size.MEDIUM
    prosperity: int = 0
    traits: list[TraitState] = field(default_factory=list)
    event_stages: dict[str, int] = field(default_factory=dict)
    event_deck: list[str] = field(default_factory=list)
    event_discard: list[str] = field(default_factory=list)
    removed_events: list[str] = field(default_factory=list)
    trait_deck: list[str] = field(default_factory=list)
    trait_discard: list[str] = field(default_factory=list)
    previous_event_id: str | None = None
    history: list[RoundRecord] = field(default_factory=list)
    rng_state: Any = None
    event_reshuffles: int = 0
    trait_reshuffles: int = 0

    @property
    def finished(self) -> bool:
        return self.round_number >= 18
