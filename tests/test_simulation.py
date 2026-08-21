import json

import pytest

from ant_game.models import Size
from ant_game.simulation import history_as_dict, history_as_text, main, play_game, simulate_strategies
from ant_game.strategies import make_strategy, strategy_names


def test_all_required_strategies_finish_or_go_extinct() -> None:
    for name in strategy_names():
        state = play_game(name, 17)
        assert state.finished
        assert 1 <= len(state.history) <= 5


def test_bots_use_the_new_unconditional_starter_actions() -> None:
    state = play_game("reactive", 17)
    activated = {
        action["card_id"]
        for action in state.history[0].actions
        if action["kind"] == "activate"
    }
    assert "trail_pheromone" in activated
    assert "collective_foraging" in activated


def test_all_exploit_probes_run() -> None:
    for name in strategy_names(include_exploits=True):
        assert play_game(name, 7).finished


def test_simulation_is_deterministic_and_win_rates_sum_to_one() -> None:
    first = simulate_strategies(8, seed_start=30)
    second = simulate_strategies(8, seed_start=30)
    assert first == second
    assert sum(row["win_rate"] for row in first["strategies"].values()) == pytest.approx(1)


def test_size_extreme_policies_reach_their_targets_when_alive() -> None:
    giant = play_game("always_giant", 2)
    small = play_game("always_small", 2)
    assert [row.size for row in giant.history[:3]] == [Size.MEDIUM, Size.LARGE, Size.GIANT]
    assert all(row.size is Size.SMALL for row in small.history)


def test_metrics_cover_required_playtest_signals() -> None:
    report = simulate_strategies(3, strategies=("reactive", "random"))
    row = report["strategies"]["reactive"]
    for key in (
        "mean_score",
        "median_score",
        "win_rate",
        "survival_rate",
        "size_distribution",
        "mean_size_changes",
        "mean_retained",
        "mean_played",
        "mean_supported",
        "mean_activated",
        "mean_push_outs",
        "mean_extremes_retained",
        "mean_shield_used",
        "mean_shield_surplus",
        "mean_damage",
        "peak_behavior_change_rate",
    ):
        assert key in row
    assert sum(row["size_distribution"].values()) == pytest.approx(1)


def test_history_exports_are_json_safe_and_readable(capsys) -> None:
    state = play_game("reactive", 4)
    payload = history_as_dict(state)
    json.dumps(payload)
    assert payload["rounds"][0]["size"] in {size.name.lower() for size in Size}
    assert "R1" in history_as_text(state)
    assert main(["--history", "reactive", "--history-seed", "4"]) == 0
    assert "score=" in capsys.readouterr().out


def test_strategy_validation() -> None:
    with pytest.raises(ValueError):
        make_strategy("unknown")
    with pytest.raises(ValueError):
        simulate_strategies(0)
    with pytest.raises(ValueError):
        simulate_strategies(1, strategies=("random", "random"))
