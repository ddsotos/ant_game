"""Content invariants for the v0.7 two-problem environmental ruleset."""

from ant_game.content import DISASTERS, NORMAL_TRAITS, ROOT_TAGS, STARTERS, TRAITS
from ant_game.localization_ja import CARD_NAMES, EVENT_NAMES, TAG_COLORS, TAG_NAMES, TAG_SYMBOLS
from ant_game.models import CardRole, EnvironmentCard, TraitCard

EXPECTED_PROBLEMS = {"raid", "sanitation"}
NEW_CARD_IDS = {
    "lasius_sealed_foundation", "diacamma_gemma_inheritance", "platythyrea_clone_watch",
    "ooceraea_synchronized_brood", "mycocepurus_clonal_garden", "cardiocondyla_dual_males",
    "vollenhovia_three_lineage", "pristomyrmex_worker_queens", "formica_resin_pharmacy",
    "myrmica_funeral_workers",
}
SHORT_GAME_SPECIES_IDS = {
    "lasius_sealed_foundation", "platythyrea_clone_watch", "ooceraea_synchronized_brood",
    "mycocepurus_clonal_garden", "cardiocondyla_dual_males", "formica_resin_pharmacy",
}
FOUR_TAG_CARDS = {
    "cephalotes_living_gate", "pheidole_supermajor_program", "pheidole_seed_miller",
    "megaponera_field_medicine", "colobopsis_last_defense", "paraponera_poneratoxin",
    "acromyrmex_antibiotic_garden", "pheidole_raid_wall", "pogonomyrmex_granary",
    "solenopsis_dry_store",
}


def test_pool_counts_and_unique_ids() -> None:
    assert len(STARTERS) == 3
    assert len(NORMAL_TRAITS) == 40
    assert len(TRAITS) == 43
    assert len(DISASTERS) == 8
    assert len({card.id for card in TRAITS}) == len(TRAITS)
    assert len({environment.id for environment in DISASTERS}) == len(DISASTERS)


def test_cards_are_actions_and_starters_are_immediately_usable() -> None:
    assert all(isinstance(card, TraitCard) and card.role is CardRole.ACTION for card in NORMAL_TRAITS)
    assert all(card.role is CardRole.STARTER and not card.activation_requirements for card in STARTERS)
    assert not any(any(option.draw_cards for option in card.options) for card in STARTERS)


def test_five_tags_and_no_movement() -> None:
    used = set().union(*(card.root_tags for card in TRAITS))
    assert used == set(ROOT_TAGS)
    assert ROOT_TAGS == {"Morphology", "Chemistry", "Sociality", "Nesting", "Resource Ecology"}
    assert set(TAG_NAMES) == set(TAG_COLORS) == set(TAG_SYMBOLS) == set(ROOT_TAGS)
    assert len(set(TAG_COLORS.values())) == len(set(TAG_SYMBOLS.values())) == 5
    assert all("Movement" not in card.root_tags and "Movement" not in card.activation_requirements for card in TRAITS)
    assert all("Movement" not in requirement.required_root_tags for environment in DISASTERS for requirement in environment.optimizations)


def test_provenance_is_present_for_cards_and_optimizations() -> None:
    assert all(card.source_taxon and card.biology_basis and card.biology_source.startswith("http") for card in TRAITS)
    assert all(
        requirement.source_taxon and requirement.biology_basis and requirement.biology_source.startswith("http")
        for environment in DISASTERS for requirement in environment.optimizations
    )


def test_only_two_recurring_problems_are_used() -> None:
    problem_ids = {
        shield.problem_id
        for card in TRAITS
        for option in (*card.options, *card.fallback_options)
        for shield in option.shields
    }
    assert problem_ids == EXPECTED_PROBLEMS


def test_four_tag_cards_have_weak_fallbacks() -> None:
    cards = {card.id: card for card in TRAITS}
    assert all(sum(cards[card_id].activation_requirements.values()) == 4 for card_id in FOUR_TAG_CARDS)
    assert all(cards[card_id].fallback_options for card_id in FOUR_TAG_CARDS)


def test_draws_are_few_and_gated() -> None:
    draw_cards = [card for card in TRAITS if any(option.draw_cards for option in card.options)]
    assert len(draw_cards) == 4
    assert all(card.activation_requirements for card in draw_cards)


def test_strong_shields_are_gated() -> None:
    for card in TRAITS:
        maximum = max((shield.amount for option in card.options for shield in option.shields), default=0)
        if maximum >= 3:
            assert card.activation_requirements


def test_environments_have_two_or_zero_optimizations_and_problem_rules() -> None:
    assert all(isinstance(environment, EnvironmentCard) for environment in DISASTERS)
    assert set(EVENT_NAMES) >= {environment.id for environment in DISASTERS}
    assert all(not environment.problem_roll_rules for environment in DISASTERS[:5])
    assert all(set(environment.problem_roll_rules) == EXPECTED_PROBLEMS for environment in DISASTERS[5:])
    assert all(len(environment.optimizations) == 2 for environment in DISASTERS[:5])
    assert all(not environment.optimizations for environment in DISASTERS[5:])
    assert DISASTERS[5].problem_roll_rules["raid"].rolls == 2
    assert DISASTERS[6].problem_roll_rules["sanitation"].bonus == 2
    assert all(DISASTERS[7].problem_roll_rules[problem].bonus == 1 for problem in EXPECTED_PROBLEMS)


def test_new_cards_have_japanese_species_style_names() -> None:
    cards = {card.id: card for card in TRAITS}
    assert set(CARD_NAMES) >= NEW_CARD_IDS
    for card_id in NEW_CARD_IDS:
        display_name = CARD_NAMES[card_id]
        assert "の" in display_name
        species, trait = display_name.split("の", 1)
        assert species and trait
        if card_id in SHORT_GAME_SPECIES_IDS:
            assert len(species) <= 5
        assert all(token not in display_name for token in cards[card_id].source_taxon.split())


def test_new_card_sources_match_the_researched_ant_topics() -> None:
    cards = {card.id: card for card in TRAITS}
    expected_sources = {
        "lasius_sealed_foundation": "7342048",
        "diacamma_gemma_inheritance": "15647944",
        "platythyrea_clone_watch": "PMC240705",
        "ooceraea_synchronized_brood": "PMC8244912",
        "mycocepurus_clonal_garden": "PMC2686657",
        "cardiocondyla_dual_males": "PMC3066177",
        "vollenhovia_three_lineage": "PMC1686177",
        "pristomyrmex_worker_queens": "PMC2664351",
        "formica_resin_pharmacy": "PMC2275180",
        "myrmica_funeral_workers": "PMC11632371",
    }
    assert all(marker in cards[card_id].biology_source for card_id, marker in expected_sources.items())


def test_storage_cards_do_not_grant_shields() -> None:
    storage_ids = {"myrmecocystus_reserve", "pogonomyrmex_granary", "solenopsis_dry_store", "atta_leaf_cache"}
    cards = {card.id: card for card in TRAITS}
    assert all(not any(option.shields for option in cards[card_id].options) for card_id in storage_ids)
    assert all(
        any(getattr(option, "store_hand_card", False) and getattr(option, "storage_income_per_card", 0) == 1 for option in cards[card_id].options)
        for card_id in storage_ids
    )


def test_payoff_values_and_biology_riders_are_distinct_from_foundations() -> None:
    cards = {card.id: card for card in TRAITS}
    strong_payoffs = {
        "cephalotes_living_gate", "pheidole_supermajor_program", "megaponera_field_medicine",
        "colobopsis_last_defense", "acromyrmex_antibiotic_garden", "pheidole_raid_wall",
        "oecophylla_living_chain", "cataglyphis_sky_compass", "diacamma_gemma_inheritance",
        "ooceraea_synchronized_brood", "mycocepurus_clonal_garden", "cardiocondyla_dual_males",
        "pristomyrmex_worker_queens",
    }
    assert all(max(option.prosperity for option in cards[card_id].options) >= 5 for card_id in strong_payoffs)
    assert cards["pheidole_seed_miller"].options[0].tag_prosperity
    assert cards["mycocepurus_clonal_garden"].options[0].tag_prosperity
    assert cards["diacamma_gemma_inheritance"].options[0].retention_bonus == 1


def test_optimization_names_are_player_facing_japanese() -> None:
    assert all(
        all(requirement.name and not any(char.isascii() and char.isalpha() for char in requirement.name) for requirement in environment.optimizations)
        for environment in DISASTERS
    )
