"""Invariants for the v0.1 data pool.

These tests intentionally check shape and design constraints, not balance.  The
simulation and engine tests are the right place to evaluate numerical tuning.
"""

from ant_game.content import EVENTS, TRAITS
from ant_game.models import EventKind, Size


def test_trait_pool_has_expected_shape_and_unique_ids() -> None:
    assert len(TRAITS) == 15
    assert len({card.id for card in TRAITS}) == len(TRAITS)
    assert len({card.name for card in TRAITS}) == len(TRAITS)
    assert sum(card.latent for card in TRAITS) == 3
    assert sum(not card.latent for card in TRAITS) == 12


def test_five_normal_traits_carry_high_evolution_load() -> None:
    normal = [card for card in TRAITS if not card.latent]
    assert 4 <= sum(card.evolution_load >= 2 for card in normal) <= 6
    assert all(card.evolution_load >= 0 for card in TRAITS)
    assert all(card.latent or card.trigger_tags == frozenset() for card in TRAITS)


def test_latent_cards_have_explicit_triggers_and_occupy_a_slot() -> None:
    latent = [card for card in TRAITS if card.latent]
    assert all(card.trigger_tags for card in latent)
    assert all(card.trigger_min_stage >= 1 for card in latent)
    assert all("latent" in card.tags for card in latent)


def test_stage_three_latent_insurance_has_peak_scale_mitigation() -> None:
    by_id = {card.id: card for card in TRAITS}
    assert by_id["pheidole_ancestral_switch"].mitigation_tags["predator"] == 5
    assert by_id["cataglyphis_thermal_sprint"].mitigation_tags["dry"] == 5


def test_event_pool_has_six_waves_two_shocks_and_unique_ids() -> None:
    assert len(EVENTS) == 8
    assert len({card.id for card in EVENTS}) == len(EVENTS)
    assert sum(card.kind is EventKind.WAVE for card in EVENTS) == 6
    assert sum(card.kind is EventKind.SHOCK for card in EVENTS) == 2


def test_wave_damage_curve_is_the_shared_v01_baseline() -> None:
    waves = [card for card in EVENTS if card.kind is EventKind.WAVE]
    for card in waves:
        assert dict(card.stage_damage) == {1: 0, 2: 4, 3: 10, 4: 2}
        assert card.size_damage_min_stage == 2
    assert all(card.shock_damage == 0 for card in waves)


def test_exactly_two_event_order_interactions() -> None:
    interactions = [card for card in EVENTS if card.sequence_prev_tag is not None]
    assert len(interactions) == 2
    assert all(card.sequence_damage_bonus > 0 for card in interactions)
    assert len({card.sequence_prev_tag for card in interactions}) == 2


def test_pool_contains_size_context_and_positive_event_hooks() -> None:
    assert any(card.size_damage for card in EVENTS)
    assert any(card.prosperity_modifier > 0 for card in EVENTS)
    assert any("prosperity_target" in card.tags for card in EVENTS)
    assert any(card.effect_id for card in TRAITS)
    assert all(card.text and "." in card.text for card in TRAITS + EVENTS)


def test_small_relief_is_event_specific() -> None:
    by_id = {card.id: card for card in EVENTS}
    small_relief = {card.id for card in EVENTS if card.size_damage.get(Size.SMALL) == -4}
    medium_relief = {card.id for card in EVENTS if card.size_damage.get(Size.MEDIUM) == -3}
    assert small_relief == {"anteater_boom", "fungal_infection_expansion"}
    assert medium_relief == {"parasitoid_fly_radiation", "long_drought"}
    assert by_id["rain_cycle"].size_damage.get(Size.SMALL, 0) == 0
    assert by_id["invasive_ant_incursion"].size_damage[Size.SMALL] == 1


def test_one_shot_last_defense_is_stronger_than_persistent_gate() -> None:
    by_id = {card.id: card for card in TRAITS}
    assert by_id["eciton_living_span"].evolution_load == 1
    assert by_id["cephalotes_living_gate"].mitigation_tags["competition"] == 4
    assert by_id["colobopsis_last_defense"].mitigation_tags["competition"] == 5


def test_latent_insurance_has_dormant_load() -> None:
    latent = [card for card in TRAITS if card.latent]
    assert all(card.evolution_load == 1 for card in latent)
    by_id = {card.id: card for card in TRAITS}
    assert by_id["cephalotes_living_gate"].mitigation_tags["competition"] == 4
