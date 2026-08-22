"""Content invariants for the six-tag environmental-change ruleset."""

from ant_game.content import DISASTERS, NORMAL_TRAITS, ROOT_TAGS, STARTERS, TRAITS
from ant_game.localization_ja import EVENT_NAMES, OPTIMIZATION_NAMES, TAG_COLORS, TAG_NAMES, TAG_SYMBOLS
from ant_game.models import CardRole, DisasterCard, TraitCard


ENVIRONMENT_SHAPES = {
    "flood": {"Sociality": 3, "Morphology": 1, "Movement": 3, "Nesting": 1, "Resource Ecology": 1},
    "desert_heat_wave": {"Morphology": 3, "Chemistry": 2},
    "prolonged_drought": {"Nesting": 3, "Resource Ecology": 2},
    "habitat_instability": {"Sociality": 2, "Movement": 2, "Nesting": 1},
    "landmark_loss": {"Movement": 3, "Resource Ecology": 1},
}


def test_pool_counts_and_unique_ids() -> None:
    assert len(STARTERS) == 3
    assert len(NORMAL_TRAITS) == 30
    assert len(TRAITS) == 33
    assert len(DISASTERS) == 5
    assert len({card.id for card in TRAITS}) == len(TRAITS)
    assert len({environment.id for environment in DISASTERS}) == len(DISASTERS)


def test_cards_are_actions_and_starters_are_immediately_usable() -> None:
    assert all(isinstance(card, TraitCard) and card.role is CardRole.ACTION for card in NORMAL_TRAITS)
    assert all(card.role is CardRole.STARTER and not card.activation_requirements for card in STARTERS)
    assert not any(any(option.draw_cards for option in card.options) for card in STARTERS)


def test_six_tags_and_sociality_replacement() -> None:
    used = set().union(*(card.root_tags for card in TRAITS))
    assert used == set(ROOT_TAGS)
    assert ROOT_TAGS == {"Morphology", "Chemistry", "Sociality", "Nesting", "Movement", "Resource Ecology"}
    assert "Cooperation" not in used and "Caste" not in used
    assert set(TAG_NAMES) == set(TAG_COLORS) == set(TAG_SYMBOLS) == set(ROOT_TAGS)
    assert len(set(TAG_COLORS.values())) == len(set(TAG_SYMBOLS.values())) == 6
    cards = {card.id: card for card in TRAITS}
    assert cards["pheidole_seed_miller"].root_tags == {"Sociality", "Morphology", "Resource Ecology"}


def test_provenance_is_present() -> None:
    assert all(card.source_taxon and card.biology_basis and card.biology_source.startswith("http") for card in TRAITS)
    assert all(environment.optimization.source_taxon and environment.optimization.biology_basis for environment in DISASTERS)
    assert all(environment.optimization.biology_source.startswith("http") for environment in DISASTERS)


def test_draws_are_few_and_gated() -> None:
    draw_cards = [card for card in TRAITS if any(option.draw_cards for option in card.options)]
    assert len(draw_cards) == 6
    assert all(card.activation_requirements for card in draw_cards)


def test_shields_use_only_recurring_problems_and_strong_shields_are_gated() -> None:
    problem_ids = {shield.problem_id for card in TRAITS for option in card.options for shield in option.shields}
    assert problem_ids == {"raid", "fungal", "nest_damage"}
    for card in TRAITS:
        maximum = max((shield.amount for option in card.options for shield in option.shields), default=0)
        if maximum >= 3:
            assert card.activation_requirements


def test_environments_have_unique_optimizations_and_no_problem_classification() -> None:
    assert all(isinstance(environment, DisasterCard) for environment in DISASTERS)
    assert set(EVENT_NAMES) == set(ENVIRONMENT_SHAPES)
    assert set(OPTIMIZATION_NAMES) == set(ENVIRONMENT_SHAPES)
    assert len({environment.optimization.name for environment in DISASTERS}) == 5
    for environment in DISASTERS:
        assert dict(environment.optimization.required_root_tags) == ENVIRONMENT_SHAPES[environment.id]
        assert not hasattr(environment, "hazard_tags")


def test_storage_cards_do_not_grant_shields() -> None:
    storage_ids = {"myrmecocystus_reserve", "pogonomyrmex_granary", "solenopsis_dry_store", "atta_leaf_cache"}
    cards = {card.id: card for card in TRAITS}
    assert all(not any(option.shields for option in cards[card_id].options) for card_id in storage_ids)
