import copy
from dataclasses import fields

import pytest

from ant_game.engine import GameEngine, InvalidDecision
from ant_game.engine import PROBLEM_IDS
from ant_game.models import (
    ActionCommand,
    ActionOption,
    CardRole,
    EnvironmentCard,
    OptimizationRequirement,
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
    assert state.current_round.prosperity_base == 2


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
    assert "retain_bonus" not in {item.name for item in fields(ActionOption)}


def test_resolve_order_is_prosperity_then_exponential_penalty_then_floor_half():
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

    assert record.prosperity_delta == 2
    assert record.score_after_prosperity == 102
    assert record.defense_by_problem == {"raid": 1, "sanitation": 0}
    assert record.unblocked_by_problem == {"raid": 2, "sanitation": 2}
    assert record.penalty_by_problem == {"raid": 4, "sanitation": 4}
    assert record.problem_penalty == 8
    assert record.score_after_problems == 94
    assert record.optimization_met is False
    assert record.optimization_half_loss == 47
    assert record.total_prosperity == state.prosperity == 47


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
