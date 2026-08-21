import copy

import pytest

from ant_game.engine import GameEngine, InvalidDecision
from ant_game.models import (
    ActionCommand,
    ActionOption,
    CardRole,
    EventCard,
    ExtremeAdaptation,
    RoundDecision,
    RoundPhase,
    ShieldSpec,
    Size,
    TraitCard,
)


def cards():
    starters = [
        TraitCard("s_chem", "Trail Pheromone", frozenset({"Chemistry"}), CardRole.STARTER),
        TraitCard("s_nest", "Earthwork Nest", frozenset({"Nesting"}), CardRole.STARTER),
        TraitCard("s_coop", "Collective Foraging", frozenset({"Cooperation"}), CardRole.STARTER),
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
        {"Cooperation": 1},
        (ActionOption(shields=(ShieldSpec(frozenset({"flood"}), 3),)),),
    )
    support = TraitCard("support", "Support", frozenset({"Nesting"}), CardRole.SUPPORT)
    fillers = [TraitCard(f"f{i}", f"Filler {i}", frozenset({"Morphology"}), CardRole.ACTION, {}, (ActionOption(),)) for i in range(6)]
    return starters + [action, shield, support, *fillers]


def event(*, damage=0, extremes=()):
    return EventCard("flood", "Flood", frozenset({"flood"}), {1: damage, 2: damage, 3: damage, 4: damage}, extremes)


def engine(**kwargs):
    return GameEngine(cards(), [event(damage=2)], seed=11, **kwargs)


def begin(engine, state, *, size=None, retain=()):
    # Put requested normal cards in the deterministic six-card offer.
    for card_id in reversed(retain):
        for index, item in enumerate(state.trait_deck):
            if item.card_id == card_id:
                state.trait_deck.append(state.trait_deck.pop(index))
                break
    engine.start_round(state)
    engine.choose_size(state, state.size if size is None else size)
    engine.retain_cards(state, retain)


def test_five_round_stage_schedule_and_small_start():
    game = GameEngine(cards(), [event(damage=0)], seed=11)
    state = game.new_game()
    assert state.size is Size.SMALL
    stages = []
    for _ in range(5):
        game.start_round(state)
        stages.append(state.current_round.stage)
        game.choose_size(state, state.size)
        game.retain_cards(state, ())
        game.resolve_environment(state)
    assert stages == [1, 1, 2, 3, 4]
    assert state.phase is RoundPhase.COMPLETE
    assert state.round_number == 5


def test_all_sizes_reveal_six_and_aggressive_retention_moves_to_hand():
    game = engine()
    state = game.new_game()
    game.start_round(state)
    game.choose_size(state, Size.MEDIUM)
    assert len(state.current_round.candidate_ids) == 6
    selected = state.current_round.candidate_ids[:3]
    game.retain_cards(state, selected)
    assert tuple(item.instance_id for item in state.hand) == selected
    assert len(state.trait_discard) == 3


def test_activate_cover_activate_chain_and_physical_once_per_round():
    game = engine()
    state = game.new_game()
    begin(game, state, retain=("action", "shield"))
    game.play_card(state, "action", 0)
    game.activate(state, 0)
    game.play_card(state, "shield", 0)
    game.activate(state, 0)
    assert [item.card_id for item in state.columns[0].cards][-2:] == ["action", "shield"]
    with pytest.raises(InvalidDecision):
        game.activate(state, 0)


def test_support_is_inserted_under_top_and_only_supplies_tags():
    game = engine(column_capacity=3)
    state = game.new_game()
    begin(game, state, retain=("action", "support"))
    game.play_card(state, "action", 0)
    game.insert_support(state, "support", 0)
    assert [item.card_id for item in state.columns[0].cards] == ["s_chem", "support", "action"]
    game.activate(state, 0)


def test_action_card_may_be_sacrificed_as_tag_only_support():
    game = engine(column_capacity=3)
    state = game.new_game()
    begin(game, state, retain=("action", "shield"))
    game.play_card(state, "action", 0)
    game.insert_support(state, "shield", 0)
    assert state.columns[0].top.card_id == "action"
    assert state.columns[0].cards[-2].is_support is True
    assert game.column_tags(state, 0)["Cooperation"] == 1


def test_support_that_would_evict_current_top_is_rejected_without_consuming_card():
    game = engine(column_capacity=1)
    state = game.new_game()
    begin(game, state, retain=("support",))
    with pytest.raises(InvalidDecision):
        game.insert_support(state, "support", 0)
    assert [item.instance_id for item in state.hand] == ["support"]


def test_capacity_pushes_oldest_card_from_same_column():
    game = engine(column_capacity=2)
    state = game.new_game()
    begin(game, state, retain=("action", "shield"))
    game.play_card(state, "action", 0)
    game.play_card(state, "shield", 0)
    assert [item.card_id for item in state.columns[0].cards] == ["action", "shield"]
    assert "s_chem" in [item.card_id for item in state.trait_discard]


def test_typed_shield_adds_and_expires_after_one_round():
    game = engine()
    state = game.new_game()
    begin(game, state, retain=("shield",))
    game.play_card(state, "shield", 0)
    game.activate(state, 0)
    first = game.resolve_environment(state)
    assert (first.raw_damage, first.shield_amount, first.damage) == (2, 3, 0)

    begin(game, state)
    second = game.resolve_environment(state)
    assert (second.raw_damage, second.shield_amount, second.damage) == (2, 0, 2)


def test_extreme_is_environment_attached_and_uses_one_column_requirement():
    extreme = ExtremeAdaptation(
        "extreme",
        "Extreme Flood Ark",
        frozenset({"Cooperation"}),
        CardRole.ACTION,
        {},
        (ActionOption(prosperity=1),),
        {"Chemistry": 1},
        1,
    )
    game = GameEngine(cards(), [event(extremes=("extreme",))], seed=2, extremes=(extreme,))
    state = game.new_game()
    game.start_round(state)
    game.choose_size(state, Size.SMALL)
    assert [item.id for item in game.eligible_extremes(state)] == ["extreme"]
    game.retain_cards(state, ("extreme",))
    assert [item.instance_id for item in state.hand] == ["extreme"]
    assert state.hand[0].origin_event_id == "flood"


def test_locked_extreme_is_public_but_not_retainable():
    extreme = ExtremeAdaptation(
        "locked",
        "Locked Route",
        frozenset({"Caste"}),
        CardRole.ACTION,
        {},
        (ActionOption(prosperity=1),),
        {"Caste": 2},
        1,
    )
    game = GameEngine(cards(), [event(extremes=(extreme,))], seed=2)
    state = game.new_game()
    game.start_round(state)
    game.choose_size(state, Size.SMALL)
    assert [item.id for item in game.public_extremes(state)] == ["locked"]
    assert game.eligible_extremes(state) == ()
    with pytest.raises(InvalidDecision):
        game.retain_cards(state, ("locked",))


def test_retain_bonus_applies_to_next_round_not_as_an_immediate_draw():
    bonus = TraitCard(
        "bonus",
        "Bonus",
        frozenset({"Chemistry"}),
        CardRole.ACTION,
        {},
        (ActionOption(retain_bonus=1),),
    )
    game = GameEngine([*cards(), bonus], [event(damage=0)], seed=3)
    state = game.new_game()
    begin(game, state, retain=("bonus",))
    game.play_card(state, "bonus", 0)
    hand_before = len(state.hand)
    game.activate(state, 0)
    assert len(state.hand) == hand_before
    game.resolve_environment(state)
    game.start_round(state)
    game.choose_size(state, Size.SMALL)
    assert game.retention_limit(state) == 5


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
