"""Shape and provenance invariants for the v0.3 data pool."""

from ant_game.content import (
    EVENTS,
    EXTREMES,
    NORMAL_TRAITS,
    PAYOFF_REQUIREMENT_BONUS,
    ROOT_TAGS,
    STAGE_DAMAGE,
    STARTERS,
    TRAITS,
)
from ant_game.models import CardRole, EventCard, ExtremeAdaptation, TraitCard


def test_pool_counts_and_unique_ids() -> None:
    assert len(STARTERS) == 3
    assert len(NORMAL_TRAITS) == 30
    assert len(TRAITS) == 33
    assert len(EVENTS) == 4
    assert len(EXTREMES) == 8
    assert len({card.id for card in TRAITS}) == len(TRAITS)
    assert len({card.id for card in EXTREMES}) == len(EXTREMES)
    assert len({event.id for event in EVENTS}) == len(EVENTS)


def test_normal_cards_are_action_and_starters_are_explicit() -> None:
    assert all(card.role is CardRole.ACTION for card in NORMAL_TRAITS)
    assert all(card.role is CardRole.STARTER for card in STARTERS)
    assert all(card.role is CardRole.ACTION for card in EXTREMES)
    assert not (set(card.id for card in NORMAL_TRAITS) & {item.id for item in EXTREMES})


def test_only_seven_root_tags_are_used_and_all_are_represented() -> None:
    used = set().union(*(card.root_tags for card in TRAITS + EXTREMES))
    assert used == set(ROOT_TAGS)
    assert all(card.root_tags <= ROOT_TAGS for card in TRAITS)
    assert all(card.root_tags <= ROOT_TAGS for card in EXTREMES)


def test_all_formal_cards_have_biology_provenance() -> None:
    formal = (*TRAITS, *EXTREMES)
    assert all(card.source_taxon for card in formal)
    assert all(card.biology_basis for card in formal)
    assert all(card.biology_source.startswith("http") for card in formal)
    assert all(card.design_role in {"Foundation", "Bridge", "Payoff"} for card in NORMAL_TRAITS)


def test_action_options_are_engine_native() -> None:
    for card in (*NORMAL_TRAITS, *EXTREMES):
        assert card.options
        assert all(option.text for option in card.options)
        assert all(option.prosperity >= 0 for option in card.options)
        assert all(option.draw_cards >= 0 and option.retain_bonus >= 0 for option in card.options)
        assert all(shield.amount > 0 and shield.hazard_tags for option in card.options for shield in option.shields)
        assert set(card.activation_requirements) <= ROOT_TAGS


def test_payoff_requirements_receive_uniform_plus_two_experiment() -> None:
    assert PAYOFF_REQUIREMENT_BONUS == 2
    payoffs = [card for card in NORMAL_TRAITS if card.design_role == "Payoff"]
    non_payoffs = [card for card in NORMAL_TRAITS if card.design_role != "Payoff"]
    assert payoffs
    assert all(card.activation_requirements for card in payoffs)
    assert all(min(card.activation_requirements.values()) == 3 for card in payoffs)
    assert all(max(card.activation_requirements.values()) <= 1 for card in non_payoffs)


def test_every_environment_has_two_attached_extremes_and_five_round_curve() -> None:
    assert STAGE_DAMAGE == {1: 0, 2: 2, 3: 4, 4: 2}
    extreme_ids = {card.id for card in EXTREMES}
    attached_ids: set[str] = set()
    for event in EVENTS:
        assert isinstance(event, EventCard)
        assert dict(event.stage_damage) == STAGE_DAMAGE
        assert len(event.extreme_adaptations) == 2
        assert all(isinstance(item, ExtremeAdaptation) for item in event.extreme_adaptations)
        ids = {item.id for item in event.extreme_adaptations}
        assert not attached_ids & ids
        attached_ids |= ids
    assert attached_ids == extreme_ids


def test_hazard_tags_are_not_root_tags() -> None:
    hazards = set().union(*(event.hazard_tags for event in EVENTS))
    shield_hazards = {
        hazard
        for card in (*NORMAL_TRAITS, *EXTREMES)
        for option in card.options
        for shield in option.shields
        for hazard in shield.hazard_tags
    }
    assert not hazards & set(ROOT_TAGS)
    assert not shield_hazards & set(ROOT_TAGS)
