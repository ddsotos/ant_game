"""Content invariants for the v0.7 two-problem environmental ruleset."""

from ant_game.content import DISASTERS, NORMAL_TRAITS, ROOT_TAGS, STARTERS, TRAITS
from ant_game.localization_ja import CARD_NAMES, CARD_TEXTS, EVENT_NAMES, TAG_COLORS, TAG_NAMES, TAG_SYMBOLS
from ant_game.models import CardRole, EnvironmentCard, TraitCard

EXPECTED_PROBLEMS = {"raid", "sanitation"}
NEW_CARD_IDS = {
    "lasius_sealed_foundation", "diacamma_gemma_inheritance", "platythyrea_clone_watch",
    "ooceraea_synchronized_brood", "mycocepurus_clonal_garden", "cardiocondyla_dual_males",
    "vollenhovia_three_lineage", "pristomyrmex_worker_queens", "formica_resin_pharmacy",
    "myrmica_funeral_workers",
    "myrmecia_antimicrobial_gland", "crematogaster_sticky_gland", "oecophylla_venom_spray", "formica_acid_resin",
    "polyrhachis_polarized_eye", "odontomachus_night_vision", "pseudomyrmex_slender_legs", "myrmecia_visual_hunt",
    "lasius_trophallaxis", "azteca_domatia", "formica_self_medication", "atta_acid_pharmacy", "camponotus_saliva_care",
    "acromyrmex_phenylacetic_acid", "atta_hard_mandible", "pheidole_bite_muscle", "melophorus_ocelli",
    "temnothorax_worker_size", "pogonomyrmex_seed_sorting", "camponotus_amputation",
    "melissotarsus_living_wood_galleries", "allomerus_fungal_trap_gallery",
    "formica_thatch_thermostat", "atta_large_colony_worker_polymorphism",
}
SHORT_GAME_SPECIES_IDS = {
    "lasius_sealed_foundation", "platythyrea_clone_watch", "ooceraea_synchronized_brood",
    "mycocepurus_clonal_garden", "cardiocondyla_dual_males", "formica_resin_pharmacy",
}
FINALE_IDS = {"army_ant_march", "fungus_garden_collapse", "extreme_heat_peak", "great_flood"}


def test_pool_counts_and_unique_ids() -> None:
    assert len(STARTERS) == 3
    assert len(NORMAL_TRAITS) == 64
    assert len(TRAITS) == 67
    assert len(DISASTERS) == 12
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


def test_printed_tags_and_payoff_fallbacks_are_compact() -> None:
    cards = {card.id: card for card in TRAITS}
    assert all(sum(card.counted_root_tags.values()) <= 2 for card in NORMAL_TRAITS)
    assert all(card.fallback_options for card in NORMAL_TRAITS if card.design_role == "Payoff")
    assert all(not (set(card.root_tags) & set(card.activation_requirements)) for card in NORMAL_TRAITS if card.design_role == "Payoff")


def test_draws_are_few_and_gated() -> None:
    draw_cards = [card for card in TRAITS if any(option.draw_cards for option in card.options)]
    assert len(draw_cards) == 4
    assert all(card.activation_requirements for card in draw_cards)


def test_strong_shields_are_gated() -> None:
    for card in TRAITS:
        maximum = max((shield.amount for option in card.options for shield in option.shields), default=0)
        if maximum >= 3:
            assert card.activation_requirements


def test_v016_balance_snapshot_effects_are_preserved() -> None:
    cards = {card.id: card for card in TRAITS}
    expected_two = {
        "pheidole_supermajor_program": "raid",
        "megaponera_field_medicine": "sanitation",
        "colobopsis_last_defense": "raid",
        "acromyrmex_antibiotic_garden": "sanitation",
    }
    for card_id, problem in expected_two.items():
        option = cards[card_id].options[0]
        assert option.prosperity == 3
        assert [(item.problem_id, item.amount) for item in option.shields] == [(problem, 2)]

    paraponera = cards["paraponera_poneratoxin"]
    assert sum(paraponera.activation_requirements.values()) == 3
    assert max(item.amount for option in paraponera.options for item in option.shields) == 3

    bite = cards["pheidole_bite_muscle"].options[0]
    assert bite.prosperity == 3
    assert [(item.problem_id, item.amount) for item in bite.shields] == [("raid", 3)]
    for card_id in {"melissotarsus_living_wood_galleries", "formica_thatch_thermostat"}:
        option = cards[card_id].options[0]
        assert option.prosperity == 5
        assert option.environment_prosperity_loss_reduction == 2
    allomerus = cards["allomerus_fungal_trap_gallery"].options[0]
    assert allomerus.prosperity == 5
    assert [(item.problem_id, item.amount) for item in allomerus.shields] == [("raid", 2)]
    atta = cards["atta_large_colony_worker_polymorphism"]
    assert atta.counted_root_tags["Morphology"] == 2
    assert atta.options[0].prosperity == 4
    assert [(item.problem_id, item.amount) for item in atta.options[0].vulnerabilities] == [("sanitation", 1)]


def test_environments_have_two_or_zero_optimizations_and_problem_rules() -> None:
    assert all(isinstance(environment, EnvironmentCard) for environment in DISASTERS)
    assert set(EVENT_NAMES) >= {environment.id for environment in DISASTERS}
    assert all(not environment.problem_roll_rules for environment in DISASTERS[:5])
    assert all(set(environment.problem_roll_rules) == EXPECTED_PROBLEMS for environment in DISASTERS[5:8])
    assert all(len(environment.optimizations) == 2 for environment in DISASTERS[:5])
    assert all(not environment.optimizations for environment in DISASTERS[5:8])
    assert {environment.id for environment in DISASTERS[8:]} == FINALE_IDS
    assert all(environment.deck == "finale" and len(environment.optimizations) == 2 for environment in DISASTERS[8:])
    assert all(set(environment.problem_roll_rules) == EXPECTED_PROBLEMS for environment in DISASTERS[8:])
    finale = {environment.id: environment for environment in DISASTERS[8:]}
    assert finale["fungus_garden_collapse"].problem_roll_rules["sanitation"].combine == "sum"
    assert finale["great_flood"].problem_roll_rules["raid"].combine == "sum"
    assert DISASTERS[5].problem_roll_rules["raid"].previous_round_bonus == 2
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
        any(getattr(option, "store_hand_card", False) and getattr(option, "storage_income_per_card", 0) == 2 for option in cards[card_id].options)
        for card_id in storage_ids
    )
    assert all(any(not option.store_hand_card for option in cards[card_id].options) for card_id in storage_ids)


def test_v010_special_effects_and_payoff_roots() -> None:
    cards = {card.id: card for card in TRAITS}
    assert all(len(card.root_tags) == 1 for card in NORMAL_TRAITS if card.design_role == "Payoff")
    assert any(option.recover_lower_card for option in cards["harpegnathos_gamergate"].options)
    preview_ids = {
        "cephalotes_aerialis",
        "temnothorax_quorum_nest",
        "solenopsis_raft_cycling",
        "temnothorax_emergency_emigration",
    }
    assert all(any(option.next_candidate_bonus == 1 for option in cards[card_id].options) for card_id in preview_ids)
    draw_cards = {card.id for card in NORMAL_TRAITS if any(option.draw_cards for option in card.options)}
    retention_cards = {card.id for card in NORMAL_TRAITS if any(option.retention_bonus for option in card.options)}
    assert abs(len(draw_cards) - len(retention_cards)) <= 1


def test_payoff_values_and_biology_riders_are_distinct_from_foundations() -> None:
    cards = {card.id: card for card in TRAITS}
    four_requirement_payoffs = {
        "cephalotes_living_gate", "pheidole_supermajor_program", "megaponera_field_medicine",
        "colobopsis_last_defense", "acromyrmex_antibiotic_garden", "pheidole_raid_wall",
        "pheidole_seed_miller", "paraponera_poneratoxin", "pogonomyrmex_granary",
        "solenopsis_dry_store",
    }
    two_requirement_payoffs = {
        card.id for card in TRAITS
        if card.design_role == "Payoff" and sum(card.activation_requirements.values()) == 2
    }
    v016_rebalanced = {
        "pheidole_supermajor_program", "megaponera_field_medicine",
        "colobopsis_last_defense", "acromyrmex_antibiotic_garden",
        "paraponera_poneratoxin",
    }
    unchanged = {
        "cephalotes_living_gate", "pheidole_raid_wall", "pheidole_seed_miller",
        "pogonomyrmex_granary", "solenopsis_dry_store",
    }
    assert all(max(option.prosperity for option in cards[card_id].options) == 3 for card_id in v016_rebalanced)
    assert all(max(option.prosperity for option in cards[card_id].options) == 5 for card_id in unchanged)
    assert all(max(option.prosperity for option in cards[card_id].options) in {2, 3, 5} for card_id in two_requirement_payoffs)
    assert cards["pheidole_seed_miller"].options[0].tag_prosperity
    assert cards["mycocepurus_clonal_garden"].options[0].tag_prosperity
    assert cards["diacamma_gemma_inheritance"].options[0].retention_bonus == 1


def test_specialized_foundations_can_supply_two_copies_of_one_root() -> None:
    cards = {card.id: card for card in TRAITS}
    expected = {
        "atta_fungus_garden": ("Resource Ecology", 2),
        "cataglyphis_silver_hair": ("Morphology", 2),
        "cataglyphis_heatshock_proteins": ("Chemistry", 2),
        "platythyrea_clone_watch": ("Sociality", 2),
    }
    for card_id, (tag, count) in expected.items():
        assert cards[card_id].counted_root_tags[tag] == count


def test_optimization_names_are_player_facing_japanese() -> None:
    assert all(
        all(
            requirement.name
            and "の" in requirement.name
            and not any(char.isascii() and char.isalpha() for char in requirement.name)
            for requirement in environment.optimizations
        )
        for environment in DISASTERS
    )


def test_wikipedia_confirmed_and_corrected_japanese_ant_names() -> None:
    assert CARD_NAMES["polyrhachis_polarized_eye"] == "ウミトゲアリの偏光眼"
    assert CARD_NAMES["atta_acid_pharmacy"] == "ケファロテスハキリアリの抗菌酸"
    # クロヤマアリ is Formica japonica, not the Lasius niger source taxon.
    assert CARD_NAMES["lasius_trophallaxis"] == "黒庭アリの口移し"


def test_card_texts_describe_biology_not_game_operations() -> None:
    forbidden = ("繁栄", "手札", "保持", "候補", "ラウンド", "タグ", "ドロー", "シールド")
    assert set(CARD_TEXTS) >= {card.id for card in TRAITS}
    assert all(not any(word in text for word in forbidden) for text in CARD_TEXTS.values())
