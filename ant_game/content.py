"""Data-only v0.1 cards.

The engine deliberately owns all resolution rules.  This module only describes
the small starting card pool, so simulations can use the same definitions as a
human-facing inspector.  ``effect_id`` is reserved for the handful of effects
that cannot be represented by a flat mitigation/bonus value; the engine may
ignore an unknown effect id rather than making card data executable code.

The public API is:

``TRAITS`` / ``TRAIT_CARDS``
    A tuple of 15 :class:`~ant_game.models.TraitCard` objects (12 normal,
    including five high-load cards, and three latent cards).
``EVENTS`` / ``EVENT_CARDS``
    A tuple of six wave and two shock :class:`~ant_game.models.EventCard`
    objects.
``TRAIT_BY_ID`` / ``EVENT_BY_ID``
    Read-only lookup dictionaries useful to the engine and bots.

Tags are intentionally a small vocabulary.  They are descriptive hooks for
event and trait resolution, not a general matchup table.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from .models import EventCard, EventKind, Size, TraitCard


_WAVE_DAMAGE = {1: 0, 2: 4, 3: 10, 4: 2}


def _wave(
    card_id: str,
    name: str,
    tags: frozenset[str],
    text: str,
    *,
    size_damage: Mapping[Size, int] | None = None,
    peak_size_damage: Mapping[Size, int] | None = None,
    prosperity_modifier: int = 0,
    sequence_prev_tag: str | None = None,
    sequence_damage_bonus: int = 0,
    effect_id: str | None = None,
) -> EventCard:
    """Build a wave card with the common I/II/III/IV damage curve."""

    return EventCard(
        id=card_id,
        name=name,
        kind=EventKind.WAVE,
        tags=tags,
        stage_damage=_WAVE_DAMAGE.copy(),
        size_damage=size_damage or {},
        size_damage_min_stage=2,
        peak_size_damage=peak_size_damage or {},
        prosperity_modifier=prosperity_modifier,
        sequence_prev_tag=sequence_prev_tag,
        sequence_damage_bonus=sequence_damage_bonus,
        effect_id=effect_id,
        text=text,
    )


def _shock(
    card_id: str,
    name: str,
    tags: frozenset[str],
    damage: int,
    text: str,
    *,
    size_damage: Mapping[Size, int] | None = None,
    prosperity_modifier: int = 0,
    sequence_prev_tag: str | None = None,
    sequence_damage_bonus: int = 0,
    effect_id: str | None = None,
) -> EventCard:
    return EventCard(
        id=card_id,
        name=name,
        kind=EventKind.SHOCK,
        tags=tags,
        shock_damage=damage,
        size_damage=size_damage or {},
        prosperity_modifier=prosperity_modifier,
        sequence_prev_tag=sequence_prev_tag,
        sequence_damage_bonus=sequence_damage_bonus,
        effect_id=effect_id,
        text=text,
    )


# Five of the normal cards have load >= 2.  Their immediate power is useful,
# but retaining several of them makes future evolution draws noticeably worse.
TRAITS: tuple[TraitCard, ...] = (
    TraitCard(
        id="paraponera_poneratoxin",
        name="Paraponera Poneratoxin",
        evolution_load=2,
        play_cost=1,
        tags=frozenset({"weapon", "predator", "competition"}),
        mitigation_tags={"predator": 1, "competition": 1},
        prosperity_tags={"competition": 1},
        effect_id="stinging_weapon",
        text="Bullet-ant venom makes a costly but frightening weapon against hunters and rivals.",
    ),
    TraitCard(
        id="solenopsis_ark",
        name="Solenopsis Ark",
        evolution_load=1,
        play_cost=1,
        tags=frozenset({"flood", "swarm"}),
        mitigation_tags={"flood": 2},
        effect_id="living_raft",
        text="Fire-ant workers link their bodies into a raft; flooding costs prosperity but need not drown the colony.",
    ),
    TraitCard(
        id="cephalotes_aerialis",
        name="Cephalotes Aerialis",
        evolution_load=0,
        play_cost=1,
        tags=frozenset({"arboreal", "predator"}),
        mitigation_tags={"predator": 1},
        effect_id="directed_glide",
        text="Gliding turtle ants steer a fall back to the trunk, escaping a ground hunter instead of fighting it.",
    ),
    TraitCard(
        id="odontomachus_tension_lock",
        name="Odontomachus Tension Lock",
        evolution_load=1,
        play_cost=2,
        tags=frozenset({"weapon", "predator", "competition"}),
        mitigation_tags={"predator": 1, "competition": 2},
        prosperity_tags={"competition": 1},
        effect_id="trap_jaw_counter",
        text="A trap-jaw snap doubles as a rival-clearing strike or a desperate launch away from danger.",
    ),
    TraitCard(
        id="oecophylla_silkworks",
        name="Oecophylla Silkworks",
        evolution_load=1,
        play_cost=2,
        tags=frozenset({"arboreal", "forest", "competition"}),
        mitigation_tags={"predator": 2, "competition": 1},
        prosperity_tags={"competition": 1},
        effect_id="leaf_binder_nest",
        text="Weaver ants pull leaves together with larval silk, moving the colony above ground pressure.",
    ),
    TraitCard(
        id="myrmecocystus_reserve",
        name="Myrmecocystus Reserve",
        evolution_load=1,
        play_cost=2,
        tags=frozenset({"food", "dry"}),
        mitigation_tags={"dry": 1},
        prosperity_tags={"food": 1},
        effect_id="replete_storage",
        text="Repletes turn their abdomens into living storage jars: a good harvest can carry a dry season.",
    ),
    TraitCard(
        id="eciton_living_span",
        name="Eciton Living Span",
        evolution_load=1,
        play_cost=1,
        tags=frozenset({"swarm", "competition", "movement"}),
        mitigation_tags={"competition": 2},
        effect_id="worker_bridge",
        text="Army-ant workers form a living bridge, trading workers tied up now for a moving, hard-to-block colony.",
    ),
    TraitCard(
        id="cephalotes_living_gate",
        name="Cephalotes Living Gate",
        evolution_load=2,
        play_cost=2,
        tags=frozenset({"defense", "competition"}),
        mitigation_tags={"competition": 4},
        effect_id="door_head_blockade",
        text="A soldier turtle ant plugs a nest entrance with its disc-shaped head, denying an intruder the tunnel.",
    ),
    TraitCard(
        id="colobopsis_last_defense",
        name="Colobopsis Last Defense",
        evolution_load=3,
        play_cost=2,
        tags=frozenset({"defense", "competition"}),
        mitigation_tags={"competition": 5},
        consume_on_trigger=True,
        effect_id="explosive_sacrifice",
        text="Exploding ants rupture their own bodies to seal a breach: a huge defense that ends this card.",
    ),
    TraitCard(
        id="atta_fungus_garden",
        name="Atta Fungus Garden",
        evolution_load=1,
        play_cost=2,
        tags=frozenset({"food", "disease", "garden"}),
        mitigation_tags={"disease": 2},
        prosperity_tags={"food": 1},
        effect_id="cultivated_food",
        text="Leafcutter ants cultivate a crop; the garden feeds prosperity, but infection threatens the whole farm.",
    ),
    TraitCard(
        id="acromyrmex_leaf_barrier",
        name="Acromyrmex Leaf Barrier",
        evolution_load=2,
        play_cost=1,
        tags=frozenset({"garden", "dry", "defense"}),
        mitigation_tags={"dry": 1, "disease": 1},
        effect_id="mulch_microclimate",
        text="Acromyrmex workers layer leaf mulch over the nest, keeping its fungus cooler and less exposed.",
    ),
    TraitCard(
        id="formica_rufa_sunshield",
        name="Formica Rufa Sunshield",
        evolution_load=0,
        play_cost=1,
        tags=frozenset({"forest", "fire"}),
        mitigation_tags={"fire": 2},
        effect_id="resin_mound",
        text="Wood ants build a resin-scented mound in the forest litter, sheltering brood from a passing fire.",
    ),
    # Latent cards occupy a slot while inactive.  Their active behavior is
    # resolved by the engine after event reveal, before damage is applied.
    TraitCard(
        id="pheidole_ancestral_switch",
        name="Pheidole Ancestral Switch",
        evolution_load=1,
        play_cost=3,
        tags=frozenset({"latent", "defense", "predator", "competition"}),
        latent=True,
        trigger_tags=frozenset({"predator", "competition"}),
        trigger_min_stage=3,
        mitigation_tags={"predator": 5, "competition": 4},
        effect_id="super_soldier_emergence_load2",
        text="Pheidole workers can reveal a super-soldier caste when a stage-III threat appears; the caste then weighs on evolution.",
    ),
    TraitCard(
        id="cataglyphis_thermal_sprint",
        name="Cataglyphis Thermal Sprint",
        evolution_load=1,
        play_cost=3,
        tags=frozenset({"latent", "dry", "heat"}),
        latent=True,
        trigger_tags=frozenset({"dry", "fire"}),
        trigger_min_stage=3,
        mitigation_tags={"dry": 5, "fire": 3},
        effect_id="desert_forager_shift_load2",
        text="Saharan silver ants switch to a heat-running foraging mode only at the lethal peak of a dry wave.",
    ),
    TraitCard(
        id="camponotus_fire_refuge",
        name="Camponotus Fire Refuge",
        evolution_load=1,
        play_cost=2,
        tags=frozenset({"latent", "fire", "defense"}),
        latent=True,
        trigger_tags=frozenset({"fire"}),
        trigger_min_stage=1,
        mitigation_tags={"fire": 3},
        effect_id="deep_wood_refuge_load1",
        text="Carpenter ants open a deep wood refuge when flames appear; the colony emerges changed after the shock.",
    ),
)


EVENTS: tuple[EventCard, ...] = (
    _wave(
        "anteater_boom",
        "Anteater Boom",
        frozenset({"predator", "ground"}),
        "A predator population swells: ground colonies feel the pressure most at stage III.",
        size_damage={Size.SMALL: -4, Size.LARGE: 1, Size.HUGE: 2},
        peak_size_damage={Size.LARGE: 1, Size.HUGE: 1},
        effect_id="ground_predator_pressure",
    ),
    _wave(
        "parasitoid_fly_radiation",
        "Parasitoid Fly Radiation",
        frozenset({"disease", "prosperity_target"}),
        "Parasitoid flies spread through prosperous colonies; abundance paints a larger target.",
        size_damage={Size.MEDIUM: -3, Size.LARGE: 1, Size.HUGE: 2},
        peak_size_damage={Size.LARGE: 1, Size.HUGE: 1},
        effect_id="targets_prosperous",
    ),
    _wave(
        "fungal_infection_expansion",
        "Fungal Infection Expansion",
        frozenset({"disease", "wet"}),
        "A wet spell lets fungus spread through brood chambers and stored food.",
        size_damage={Size.SMALL: -4, Size.HUGE: 1},
        peak_size_damage={Size.LARGE: 1, Size.HUGE: 1},
        effect_id="wet_fungus_spread",
    ),
    _wave(
        "invasive_ant_incursion",
        "Invasive Ant Incursion",
        frozenset({"competition", "swarm"}),
        "A rival supercolony arrives; after floods, its bridges reach even sheltered nests.",
        size_damage={Size.TINY: 2, Size.SMALL: 1},
        sequence_prev_tag="flood",
        sequence_damage_bonus=2,
        effect_id="rival_supercolony",
    ),
    _wave(
        "long_drought",
        "Long Drought",
        frozenset({"dry", "food"}),
        "Foraging distance stretches and flowers fail; stored food changes the cost of waiting.",
        size_damage={Size.MEDIUM: -3, Size.LARGE: 1, Size.HUGE: 2},
        peak_size_damage={Size.LARGE: 1, Size.HUGE: 1},
        effect_id="forage_failure",
    ),
    _wave(
        "rain_cycle",
        "Rain Cycle",
        frozenset({"flood", "wet"}),
        "Repeated cloudbursts turn paths into rivers; raft-builders and tree nests take different risks.",
        size_damage={Size.HUGE: 1},
        effect_id="periodic_flood",
    ),
    _shock(
        "wildfire",
        "Wildfire",
        frozenset({"fire", "dry"}),
        8,
        "A fast-moving fire crosses the foraging ground. Dry conditions feed it.",
        size_damage={Size.HUGE: 2},
        sequence_prev_tag="dry",
        sequence_damage_bonus=2,
        effect_id="dry_fuel_fire",
    ),
    _shock(
        "insect_bloom",
        "Insect Bloom",
        frozenset({"food", "boom"}),
        0,
        "A sudden insect bloom feeds hunters and scavengers; the windfall rewards preparation.",
        prosperity_modifier=2,
        effect_id="seasonal_windfall",
    ),
)


TRAIT_BY_ID = MappingProxyType({card.id: card for card in TRAITS})
EVENT_BY_ID = MappingProxyType({card.id: card for card in EVENTS})

# More explicit aliases make the data convenient for either engine or tests.
TRAIT_CARDS = TRAITS
EVENT_CARDS = EVENTS


__all__ = [
    "EVENTS",
    "EVENT_CARDS",
    "EVENT_BY_ID",
    "TRAITS",
    "TRAIT_CARDS",
    "TRAIT_BY_ID",
]
