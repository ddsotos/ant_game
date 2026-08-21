"""Shape, rules, and provenance invariants for evolution content."""

from ant_game.content import DISASTERS, NORMAL_TRAITS, ROOT_TAGS, STARTERS, TRAITS
from ant_game.localization_ja import EVENT_NAMES, OPTIMIZATION_NAMES, TAG_COLORS, TAG_NAMES, TAG_SYMBOLS
from ant_game.models import CardRole, DisasterCard, TraitCard


PAYOFF_REQUIREMENTS = {
    "cephalotes_living_gate": {"Caste": 3, "Nesting": 1},
    "odontomachus_tension_lock": {"Morphology": 2, "Movement": 2},
    "pheidole_supermajor_program": {"Caste": 3, "Cooperation": 1},
    "pheidole_seed_miller": {"Caste": 2, "Resource Ecology": 2},
    "megaponera_field_medicine": {"Movement": 3, "Chemistry": 1},
    "colobopsis_last_defense": {"Nesting": 3, "Chemistry": 1},
    "paraponera_poneratoxin": {"Morphology": 3, "Chemistry": 1},
    "acromyrmex_antibiotic_garden": {"Nesting": 3, "Chemistry": 1},
    "cataglyphis_silver_hair": {"Movement": 3, "Morphology": 1},
    "pheidole_raid_wall": {"Nesting": 3, "Morphology": 1},
    "solenopsis_dry_store": {"Cooperation": 3, "Resource Ecology": 1},
    "cataglyphis_heatshock_proteins": {"Movement": 3, "Chemistry": 1},
    "megaponera_termite_raid": {"Movement": 3, "Cooperation": 1},
    "temnothorax_emergency_emigration": {"Cooperation": 3, "Movement": 1},
}

DISASTER_SHAPES = {
    "flood_torrent": ({"flood"}, {"Cooperation": 3, "Morphology": 1}),
    "canopy_fragmentation": ({"flood"}, {"Movement": 3, "Nesting": 1, "Resource Ecology": 1}),
    "desert_heat_wave": ({"heat", "drought"}, {"Morphology": 4, "Chemistry": 1}),
    "prolonged_drought": ({"drought"}, {"Nesting": 3, "Resource Ecology": 2}),
    "garden_epidemic": ({"fungal"}, {"Chemistry": 3, "Resource Ecology": 2}),
    "spore_contamination": ({"fungal"}, {"Morphology": 3, "Chemistry": 2}),
    "army_ant_raid": ({"raid"}, {"Caste": 3, "Morphology": 1, "Nesting": 1}),
    "post_raid_injuries": ({"raid"}, {"Cooperation": 4, "Movement": 1}),
}


def test_pool_counts_and_unique_ids() -> None:
    assert len(STARTERS) == 3
    assert len(NORMAL_TRAITS) == 30
    assert len(TRAITS) == 33
    assert len(DISASTERS) == 8
    assert len({card.id for card in TRAITS}) == len(TRAITS)
    assert len({disaster.id for disaster in DISASTERS}) == len(DISASTERS)


def test_normal_cards_are_actions_and_starters_are_immediately_usable() -> None:
    assert all(isinstance(card, TraitCard) and card.role is CardRole.ACTION for card in NORMAL_TRAITS)
    assert all(card.role is CardRole.STARTER for card in STARTERS)
    assert all(not card.activation_requirements and card.options for card in STARTERS)


def test_foundation_and_bridge_are_ungated_and_payoffs_use_explicit_requirements() -> None:
    assert {card.id for card in NORMAL_TRAITS if card.design_role == "Payoff"} == set(PAYOFF_REQUIREMENTS)
    for card in NORMAL_TRAITS:
        assert dict(card.activation_requirements) == PAYOFF_REQUIREMENTS.get(card.id, {})


def test_cards_use_one_two_and_three_tags_as_biology_demands() -> None:
    cards = {card.id: card for card in TRAITS}
    assert cards["paraponera_poneratoxin"].root_tags == {"Chemistry"}
    assert cards["atta_fungus_garden"].root_tags == {"Resource Ecology"}
    assert cards["cataglyphis_silver_hair"].root_tags == {"Morphology"}
    assert cards["solenopsis_dry_store"].root_tags == {"Resource Ecology"}
    assert cards["atta_leaf_cache"].root_tags == {"Resource Ecology"}
    assert cards["cataglyphis_heatshock_proteins"].root_tags == {"Chemistry"}
    assert cards["pheidole_seed_miller"].root_tags == {"Caste", "Morphology", "Resource Ecology"}
    assert cards["attine_infrabuccal_pocket"].root_tags == {"Chemistry", "Morphology"}
    assert cards["solenopsis_raft_cycling"].root_tags == {"Cooperation", "Movement"}
    assert {len(card.root_tags) for card in TRAITS} == {1, 2, 3}


def test_only_seven_root_tags_are_used_and_localized_visually() -> None:
    used = set().union(*(card.root_tags for card in TRAITS))
    assert used == set(ROOT_TAGS)
    assert set(TAG_NAMES) == set(TAG_COLORS) == set(TAG_SYMBOLS) == set(ROOT_TAGS)
    assert len(set(TAG_COLORS.values())) == len(set(TAG_SYMBOLS.values())) == 7


def test_all_formal_content_has_biology_provenance() -> None:
    assert all(card.source_taxon and card.biology_basis for card in TRAITS)
    assert all(card.biology_source.startswith("http") for card in TRAITS)
    assert all(disaster.optimization.source_taxon and disaster.optimization.biology_basis for disaster in DISASTERS)
    assert all(disaster.optimization.biology_source.startswith("http") for disaster in DISASTERS)


def test_all_options_are_native_and_retention_bonus_is_gone() -> None:
    draw_replacements = {
        "earthwork_nest", "myrmecocystus_reserve", "cataglyphis_sky_compass",
        "pogonomyrmex_granary", "solenopsis_dry_store", "atta_leaf_cache",
    }
    cards = {card.id: card for card in TRAITS}
    assert all(any(option.draw_cards for option in cards[card_id].options) for card_id in draw_replacements)
    for card in TRAITS:
        assert card.options
        assert all(option.text and option.prosperity >= 0 and option.draw_cards >= 0 for option in card.options)
        assert all(shield.amount > 0 and shield.hazard_tag for option in card.options for shield in option.shields)


def test_disasters_have_unique_printed_optimizations() -> None:
    assert all(isinstance(disaster, DisasterCard) for disaster in DISASTERS)
    assert set(EVENT_NAMES) == set(DISASTER_SHAPES)
    assert set(OPTIMIZATION_NAMES) == set(DISASTER_SHAPES)
    assert len({disaster.optimization.name for disaster in DISASTERS}) == 8
    for disaster in DISASTERS:
        hazards, requirements = DISASTER_SHAPES[disaster.id]
        assert disaster.hazard_tags == hazards
        assert dict(disaster.optimization.required_root_tags) == requirements


def test_hazard_tags_are_separate_from_root_tags() -> None:
    hazards = set().union(*(disaster.hazard_tags for disaster in DISASTERS))
    shield_hazards = {
        shield.hazard_tag
        for card in TRAITS
        for option in card.options
        for shield in option.shields
    }
    assert not hazards & set(ROOT_TAGS)
    assert shield_hazards <= hazards
    assert hazards <= shield_hazards
