import copy
from dataclasses import fields

import pytest

from ant_game.engine import GameEngine, InvalidDecision
from ant_game.models import (
    ActionCommand,
    ActionOption,
    CardRole,
    DisasterCard,
    OptimizationRequirement,
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
        TraitCard("s_coop", "Foraging", frozenset({"Cooperation"}), CardRole.STARTER, options=(ActionOption(prosperity=1),)),
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
        frozenset({"Cooperation"}),
        CardRole.ACTION,
        {},
        (ActionOption(shields=(ShieldSpec("flood", 1),)),),
    )
    support = TraitCard("support", "Support", frozenset({"Chemistry"}), CardRole.SUPPORT)
    fillers = [
        TraitCard(f"f{i}", f"Filler {i}", frozenset({"Morphology"}), CardRole.ACTION, {}, (ActionOption(),))
        for i in range(8)
    ]
    return [*starters, action, shield, support, *fillers]


def optimization(required: dict[str, int] | None = None) -> OptimizationRequirement:
    return OptimizationRequirement("Test Optimization", required or {"Caste": 9})


def disasters(*, first_hazards=frozenset({"flood"}), first_requirement=None) -> list[DisasterCard]:
    result = [
        DisasterCard("d0", "Disaster 0", first_hazards, optimization(first_requirement)),
    ]
    result.extend(
        DisasterCard(f"d{i}", f"Disaster {i}", frozenset({"flood"}), optimization())
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


def test_five_unique_disasters_are_public_and_seed_reproducible():
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
            output.append(dict(state.current_round.hazard_rolls))
            engine_for_state.choose_size(state, state.size)
            engine_for_state.retain_cards(state, ())
            engine_for_state.resolve_environment(state)
    assert first_rolls == second_rolls
    assert all(1 <= roll <= 6 for row in first_rolls for roll in row.values())
    assert first.phase is second.phase is RoundPhase.COMPLETE
    assert first.round_number == second.round_number == 5


def test_at_least_five_disasters_are_required():
    with pytest.raises(ValueError, match="at least five"):
        GameEngine(cards(), disasters()[:4])


def test_shield_targets_exactly_one_nonempty_hazard():
    assert ShieldSpec("flood", 2).hazard_tag == "flood"
    with pytest.raises(ValueError):
        ShieldSpec("", 2)
    with pytest.raises(ValueError):
        ShieldSpec(frozenset({"flood"}), 2)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ShieldSpec("flood", 0)


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
        disasters(first_hazards=frozenset({"flood", "drought"})),
        seed=11,
    )
    state = game.new_game()
    force_first_disaster(game, state)
    state.prosperity = 100
    begin(game, state, size=Size.MEDIUM, retain=("shield",))
    state.current_round.hazard_rolls = {"drought": 2, "flood": 3}
    game.play_card(state, "shield", 0)
    game.activate(state, 0)
    state.current_round.prosperity_base += 2

    record = game.resolve_environment(state)

    assert record.prosperity_delta == 2
    assert record.score_after_prosperity == 102
    assert record.defense_by_hazard == {"drought": 0, "flood": 1}
    assert record.unblocked_by_hazard == {"drought": 2, "flood": 2}
    assert record.penalty_by_hazard == {"drought": 4, "flood": 4}
    assert record.hazard_penalty == 8
    assert record.score_after_hazard == 94
    assert record.optimization_met is False
    assert record.optimization_half_loss == 47
    assert record.total_prosperity == state.prosperity == 47


def test_fully_defended_hazard_has_zero_penalty_and_shields_expire():
    game = engine()
    state = game.new_game()
    force_first_disaster(game, state)
    state.prosperity = 20
    begin(game, state, retain=("shield",))
    state.current_round.hazard_rolls = {"flood": 1}
    game.play_card(state, "shield", 0)
    game.activate(state, 0)
    first = game.resolve_environment(state)
    assert first.unblocked_by_hazard["flood"] == 0
    assert first.penalty_by_hazard["flood"] == 0

    game.start_round(state)
    game.choose_size(state, state.size)
    game.retain_cards(state, ())
    state.current_round.hazard_rolls = {"flood": 1}
    second = game.resolve_environment(state)
    assert second.defense_by_hazard["flood"] == 0
    assert second.penalty_by_hazard["flood"] == 2


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
    state.current_round.hazard_rolls = {"flood": 1}
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
        state.current_round.hazard_rolls = {tag: 6 for tag in game.current_disaster(state).hazard_tags}
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
