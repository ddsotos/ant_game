import copy
from dataclasses import fields

import pytest

from ant_game.engine import GameEngine, InvalidDecision
from ant_game.engine import PROBLEM_IDS
from ant_game.models import (
    ActionCommand,
    ActionOption,
    CardInstance,
    CardRole,
    EnvironmentCard,
    OptimizationRequirement,
    PlayedCard,
    ProblemRollRule,
    RoundDecision,
    RoundPhase,
    ShieldSpec,
    Size,
    TraitCard,
)


def cards() -> list[TraitCard]:
    starters = [
        TraitCard("s_chem", "Trail", frozenset({"Chemistry"}), CardRole.STARTER, options=(ActionOption(draw_cards=1),)),
        TraitCard("s_nest", "Nest", frozenset({"Nesting"}), CardRole.STARTER, options=(ActionOption(prosperity=1),)),
        TraitCard("s_social", "Foraging", frozenset({"Sociality"}), CardRole.STARTER, options=(ActionOption(prosperity=1),)),
    ]
    action = TraitCard(
        "action",
        "Action",
        frozenset({"Chemistry"}),
        CardRole.ACTION,
        {"Chemistry": 1},
        (ActionOption(prosperity=2),),
    )
    shield = TraitCard(
        "shield",
        "Flood Shield",
        frozenset({"Sociality"}),
        CardRole.ACTION,
        {},
        (ActionOption(shields=(ShieldSpec("raid", 1),)),),
    )
    support = TraitCard("support", "Support", frozenset({"Chemistry"}), CardRole.SUPPORT)
    fillers = [
        TraitCard(f"f{i}", f"Filler {i}", frozenset({"Morphology"}), CardRole.ACTION, {}, (ActionOption(),))
        for i in range(8)
    ]
    return [*starters, action, shield, support, *fillers]


def optimization(required: dict[str, int] | None = None) -> OptimizationRequirement:
    return OptimizationRequirement("Test Optimization", required or {"Sociality": 9})


def disasters(*, first_requirement=None) -> list[EnvironmentCard]:
    result = [
        EnvironmentCard("d0", "Environment 0", (optimization(first_requirement),)),
    ]
    result.extend(
        EnvironmentCard(f"d{i}", f"Environment {i}", (optimization(),))
        for i in range(1, 8)
    )
    return result


def engine(**kwargs) -> GameEngine:
    return GameEngine(cards(), disasters(), seed=11, **kwargs)


def begin(game: GameEngine, state, *, size=None, retain=()):
    for card_id in reversed(retain):
        for index, item in enumerate(state.trait_deck):
            if item.card_id == card_id:
                state.trait_deck.append(state.trait_deck.pop(index))
                break
    game.start_round(state)
    game.choose_size(state, state.size if size is None else size)
    game.retain_cards(state, retain)


def force_first_disaster(game: GameEngine, state, disaster_id: str = "d0") -> None:
    remaining = tuple(item for item in state.disaster_ids if item != disaster_id)
    state.disaster_ids = (disaster_id, *remaining[:4])


def test_independent_problems_are_d4_and_seed_reproducible():
    first = engine().new_game()
    second = engine().new_game()
    assert len(first.disaster_ids) == len(set(first.disaster_ids)) == 5
    assert first.disaster_ids == second.disaster_ids

    first_rolls = []
    second_rolls = []
    for state, output in ((first, first_rolls), (second, second_rolls)):
        for _ in range(5):
            engine_for_state = engine()
            engine_for_state.start_round(state)
            output.append(dict(state.current_round.problem_rolls))
            engine_for_state.choose_size(state, state.size)
            engine_for_state.retain_cards(state, ())
            engine_for_state.resolve_environment(state)
    assert first_rolls == second_rolls
    assert all(1 <= roll <= 4 for row in first_rolls for roll in row.values())
    assert all(set(row) == set(PROBLEM_IDS) for row in first_rolls)
    assert first.phase is second.phase is RoundPhase.COMPLETE
    assert first.round_number == second.round_number == 5


def test_size_multipliers_have_a_nonzero_base_and_round_base_is_five():
    assert [size.prosperity_multiplier for size in Size] == [1, 2, 3, 4]
    game = engine()
    state = game.new_game()
    game.start_round(state)
    assert state.current_round.prosperity_base == 5
    game.choose_size(state, Size.SMALL)
    assert state.current_round.prosperity_base == 5


def test_root_tag_multiplicity_counts_for_columns_and_optimizations():
    specialist = TraitCard(
        "specialist", "Specialist", frozenset({"Chemistry"}), CardRole.ACTION,
        root_tag_counts={"Chemistry": 2},
    )
    game = GameEngine(cards() + [specialist], disasters(), seed=11)
    state = game.new_game()
    state.columns[0].cards.append(PlayedCard("specialist", "specialist"))
    assert game.column_tags(state, 0)["Chemistry"] == 3  # starter 1 + specialist 2
    assert game.board_tags(state)["Chemistry"] == 3


def test_retention_bonus_is_consumed_by_the_next_round_only():
    bonus_card = TraitCard(
        "retention", "Retention", frozenset({"Resource Ecology"}),
        CardRole.ACTION, {}, (ActionOption(retention_bonus=2),),
    )
    game = GameEngine(cards() + [bonus_card], disasters(), seed=11)
    state = game.new_game()
    begin(game, state, retain=("retention",))
    game.play_card(state, "retention", 0)
    game.activate(state, 0)
    assert state.pending_retention_bonus == 2
    game.resolve_environment(state)
    game.start_round(state)
    game.choose_size(state, Size.SMALL)
    assert game.retention_limit(state) == 6
    game.retain_cards(state, ())
    assert state.pending_retention_bonus == 0
    game.resolve_environment(state)
    game.start_round(state)
    game.choose_size(state, Size.SMALL)
    assert game.retention_limit(state) == 4


def test_storage_card_pays_from_next_round_and_is_discarded_with_host():
    storage = TraitCard(
        "storage", "Storage", frozenset({"Resource Ecology"}),
        CardRole.ACTION, {}, (ActionOption(store_hand_card=True, storage_income_per_card=2),),
    )
    game = GameEngine(cards() + [storage], disasters(), seed=11, column_capacity=1)
    state = game.new_game()
    begin(game, state, retain=("storage", "f0"))
    game.play_card(state, "storage", 0)
    game.activate(state, 0, target_card_id="f0")
    assert len(state.columns[0].top.stored_cards) == 1
    game.resolve_environment(state)
    game.start_round(state)
    assert state.current_round.prosperity_base == 7
    assert state.current_round.storage_prosperity == 2
    game.choose_size(state, Size.SMALL)
    game.retain_cards(state, ())
    state.hand.append(CardInstance("f1", "f1"))
    game.play_card(state, "f1", 0)
    assert any(item.card_id == "f0" for item in state.trait_discard)


def test_recovery_returns_one_eligible_lower_card_and_is_one_per_round():
    recovery = TraitCard(
        "recovery", "Recovery", frozenset({"Sociality"}), CardRole.ACTION, {},
        (ActionOption(recover_lower_card=True),),
    )
    game = GameEngine(cards() + [recovery], disasters(), seed=11)
    state = game.new_game()
    begin(game, state, retain=("f0", "recovery"))
    game.play_card(state, "f0", 0)
    game.play_card(state, "recovery", 0)
    game.activate(state, 0, target_card_id="f0")
    assert all(item.instance_id != "f0" for item in state.columns[0].cards)
    assert any(item.instance_id == "f0" for item in state.hand)


def test_next_candidate_bonus_is_one_shot_and_does_not_change_retention():
    bonus = TraitCard(
        "candidate_bonus", "Candidate Bonus", frozenset({"Resource Ecology"}), CardRole.ACTION, {},
        (ActionOption(next_candidate_bonus=2),),
    )
    game = GameEngine(cards() + [bonus], disasters(), seed=11)
    state = game.new_game()
    begin(game, state, retain=("candidate_bonus",))
    game.play_card(state, "candidate_bonus", 0)
    game.activate(state, 0)
    assert state.pending_candidate_bonus == 2
    game.resolve_environment(state)
    game.start_round(state)
    game.choose_size(state, Size.SMALL)
    assert state.current_round.candidate_draw_count == 8
    assert state.pending_candidate_bonus == 0
    assert game.retention_limit(state) == 4


def test_previous_round_bonus_reuses_prior_problem_roll_without_a_new_die():
    first = EnvironmentCard(
        "d0", "Carry-over", (optimization(),),
        {"raid": ProblemRollRule(previous_round_bonus=2)},
    )
    custom_disasters = [first, *disasters()[1:]]
    game = GameEngine(cards(), custom_disasters, seed=11)
    state = game.new_game()
    state.disaster_ids = ("d0", "d0", "d0", "d0", "d0")
    game.start_round(state)
    first_roll = state.current_round.problem_rolls["raid"]
    assert state.current_round.problem_roll_sources["raid"] == "d4_first_round"
    assert len(state.current_round.problem_raw_rolls["raid"]) == 1
    game.choose_size(state, Size.SMALL)
    game.retain_cards(state, ())
    game.resolve_environment(state)
    game.start_round(state)
    assert state.current_round.problem_roll_sources["raid"] == "previous_round"
    assert state.current_round.problem_raw_rolls["raid"] == ()
    assert state.current_round.problem_selected_rolls["raid"] == first_roll
    assert state.current_round.problem_rolls["raid"] == first_roll + 2


def test_at_least_five_environments_are_required():
    with pytest.raises(ValueError, match="at least five"):
        GameEngine(cards(), disasters()[:4])


def test_shield_targets_exactly_one_nonempty_problem():
    assert ShieldSpec("raid", 2).problem_id == "raid"
    with pytest.raises(ValueError):
        ShieldSpec("", 2)
    with pytest.raises(ValueError):
        ShieldSpec(frozenset({"raid"}), 2)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ShieldSpec("raid", 0)


def test_activation_excludes_top_cards_own_tags_but_counts_support_below_it():
    game = engine()
    state = game.new_game()
    begin(game, state, retain=("action", "support"))
    game.play_card(state, "action", 1)  # Nesting starter supplies no Chemistry.
    with pytest.raises(InvalidDecision, match="other cards"):
        game.activate(state, 1)

    game.insert_support(state, "support", 1)
    game.activate(state, 1)
    assert state.current_round.prosperity_base == 7
    assert state.current_round.base_prosperity == 5
    assert state.current_round.activation_prosperity == 2
    assert state.current_round.card_prosperity == 0
    assert state.current_round.storage_prosperity == 0
    assert state.current_round.tag_prosperity == 0


def test_activation_requirements_do_not_use_other_columns():
    game = engine()
    state = game.new_game()
    begin(game, state, retain=("action",))
    game.play_card(state, "action", 1)
    assert game.board_tags(state)["Chemistry"] >= 2
    with pytest.raises(InvalidDecision):
        game.activate(state, 1)


def test_starters_remain_immediately_activatable_and_draw_is_immediate():
    game = engine()
    state = game.new_game()
    begin(game, state)
    before = len(state.hand)
    game.activate(state, 0)
    assert len(state.hand) == before + 1
    assert state.columns[0].top.activated_round == 1
    assert "retention_bonus" in {item.name for item in fields(ActionOption)}


def test_resolve_order_is_problem_penalty_then_size_multiplier_then_floor_half():
    game = GameEngine(
        cards(),
        disasters(),
        seed=11,
    )
    state = game.new_game()
    force_first_disaster(game, state)
    state.prosperity = 100
    begin(game, state, size=Size.MEDIUM, retain=("shield",))
    state.current_round.problem_rolls = {"raid": 3, "sanitation": 2}
    game.play_card(state, "shield", 0)
    game.activate(state, 0)
    state.current_round.prosperity_base += 2

    record = game.resolve_environment(state)

    assert record.prosperity_delta == 0
    assert record.score_after_prosperity == 100
    assert record.defense_by_problem == {"raid": 1, "sanitation": 0}
    assert record.unblocked_by_problem == {"raid": 2, "sanitation": 2}
    assert record.penalty_by_problem == {"raid": 4, "sanitation": 4}
    assert record.problem_penalty == 8
    assert record.score_after_problems == 100
    assert record.optimization_met is False
    assert record.optimization_half_loss == 50
    assert record.total_prosperity == state.prosperity == 50
    assert record.prosperity_pool_before_problems == 7
    assert record.prosperity_pool_after_problems == 0


def test_fully_defended_problem_has_zero_penalty_and_shields_expire():
    game = engine()
    state = game.new_game()
    force_first_disaster(game, state)
    state.prosperity = 20
    begin(game, state, retain=("shield",))
    state.current_round.problem_rolls = {"raid": 1, "sanitation": 1}
    game.play_card(state, "shield", 0)
    game.activate(state, 0)
    first = game.resolve_environment(state)
    assert first.unblocked_by_problem["raid"] == 0
    assert first.penalty_by_problem["raid"] == 0

    game.start_round(state)
    game.choose_size(state, state.size)
    game.retain_cards(state, ())
    state.current_round.problem_rolls = {"raid": 1, "sanitation": 1}
    second = game.resolve_environment(state)
    assert second.defense_by_problem["raid"] == 0
    assert second.penalty_by_problem["raid"] == 2


def test_optimization_counts_every_card_across_all_columns():
    game = GameEngine(
        cards(),
        disasters(first_requirement={"Chemistry": 2, "Nesting": 1}),
        seed=11,
    )
    state = game.new_game()
    force_first_disaster(game, state)
    begin(game, state, retain=("support",))
    game.insert_support(state, "support", 2)
    state.current_round.problem_rolls = {"raid": 1, "sanitation": 1}
    record = game.resolve_environment(state)
    assert record.optimization_met is True
    assert record.optimization_actual_tags["Chemistry"] == 2
    assert record.optimization_actual_tags["Nesting"] == 1
    assert record.optimization_half_loss == 0


def test_score_floors_at_zero_and_failure_never_causes_extinction():
    game = engine()
    state = game.new_game()
    for _ in range(5):
        game.start_round(state)
        game.choose_size(state, state.size)
        game.retain_cards(state, ())
        state.current_round.problem_rolls = {problem: 6 for problem in PROBLEM_IDS}
        record = game.resolve_environment(state)
        assert record.total_prosperity == 0
    assert state.finished
    assert state.phase is RoundPhase.COMPLETE
    assert len(state.history) == 5


def test_activate_cover_activate_chain_and_physical_once_per_round():
    game = engine()
    state = game.new_game()
    begin(game, state, retain=("shield", "f0"))
    game.play_card(state, "shield", 0)
    game.activate(state, 0)
    game.play_card(state, "f0", 0)
    game.activate(state, 0)
    with pytest.raises(InvalidDecision):
        game.activate(state, 0)


def test_invalid_atomic_round_does_not_mutate_state():
    game = engine()
    state = game.new_game()
    before = copy.deepcopy(state)
    with pytest.raises(InvalidDecision):
        game.resolve_round(
            state,
            RoundDecision(
                Size.SMALL,
                actions=(ActionCommand("play", column_index=0, card_id="not-in-hand"),),
            ),
        )
    assert state == before


def test_environment_roll_rule_preserves_raw_selected_and_modified_values():
    special = EnvironmentCard(
        "d0",
        "Severe Environment",
        (optimization(),),
        {"raid": ProblemRollRule(rolls=2, bonus=2)},
    )
    game = GameEngine(
        cards(),
        [special, *disasters()[1:]],
        seed=11,
    )
    state = game.new_game()
    force_first_disaster(game, state)
    game.start_round(state)
    context = state.current_round
    assert context is not None
    assert len(context.problem_raw_rolls["raid"]) == 2
    assert context.problem_selected_rolls["raid"] == max(context.problem_raw_rolls["raid"])
    assert context.problem_modifiers["raid"] == 2
    assert context.problem_rolls["raid"] == context.problem_selected_rolls["raid"] + 2


def test_two_optimizations_use_or_and_empty_optimization_skips_half_loss():
    first = EnvironmentCard(
        "d0",
        "Two Paths",
        (
            OptimizationRequirement("Impossible", {"Morphology": 99}),
            OptimizationRequirement("Starter Path", {"Chemistry": 1}),
        ),
    )
    no_optimization = EnvironmentCard("d0", "Pressure Only")
    for environment in (first, no_optimization):
        game = GameEngine(cards(), [environment, *disasters()[1:]], seed=11)
        state = game.new_game()
        force_first_disaster(game, state)
        state.prosperity = 20
        begin(game, state)
        record = game.resolve_environment(state)
        assert record.optimization_met is True
        assert record.optimization_half_loss == 0
        if environment is first:
            assert record.optimization_results == (False, True)
        else:
            assert record.optimization_results == ()


def test_unmet_requirements_use_fallback_effect_and_log_tier():
    fallback = TraitCard(
        "fallback",
        "Fallback",
        frozenset({"Morphology"}),
        CardRole.ACTION,
        {"Morphology": 3},
        (ActionOption(prosperity=3),),
        fallback_options=(ActionOption(prosperity=1),),
    )
    game = GameEngine(cards() + [fallback], disasters(), seed=11)
    state = game.new_game()
    begin(game, state, retain=("fallback",))
    game.play_card(state, "fallback", 0)
    option = game.activate(state, 0)
    assert option.prosperity == 1
    assert state.current_round is not None
    assert state.current_round.action_log[-1]["tier"] == "fallback"
