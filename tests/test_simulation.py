import json

import pytest

from ant_game.models import Size
from ant_game.simulation import history_as_dict, history_as_text, main, play_game, simulate_strategies
from ant_game.strategies import make_strategy, strategy_names


def test_all_required_strategies_finish_a_game():
    for name in strategy_names():
        state = play_game(name, 17)
        assert state.finished
        assert len(state.history) == 18


def test_peak_adaptive_probe_finishes_a_game():
    state = play_game("peak_adaptive", 7)
    assert len(state.history) == 18


def test_simulation_is_deterministic_and_win_rates_sum_to_one():
    first = simulate_strategies(8, seed_start=30)
    second = simulate_strategies(8, seed_start=30)
    assert first == second
    assert sum(row["win_rate"] for row in first["strategies"].values()) == pytest.approx(1)


def test_size_extreme_exploit_policies_reach_their_targets():
    giant = play_game("always_giant", 2)
    tiny = play_game("always_tiny", 2)
    assert [row.size for row in giant.history[:2]] == [Size.LARGE, Size.HUGE]
    assert [row.size for row in tiny.history[:2]] == [Size.SMALL, Size.TINY]
    assert all(row.size == Size.HUGE for row in giant.history[2:])
    assert all(row.size == Size.TINY for row in tiny.history[2:])


def test_metrics_cover_required_playtest_signals():
    report = simulate_strategies(3, strategies=("reactive", "random"))
    row = report["strategies"]["reactive"]
    for key in (
        "mean_score", "median_score", "win_rate", "size_distribution", "mean_size_changes",
        "mean_traits_acquired", "mean_traits_discarded", "mean_evolution_load_rounds",
        "mean_traits_shed", "mean_zero_evolution_draws", "mean_evolution_recovery_rounds",
        "mean_lost_evolution_draws", "mean_event_damage", "mean_stage_iii_damage",
        "after_stage_iii_size_response", "trait_acquisition_rate_per_game",
        "latent_activation_rate_per_game", "mean_traits_consumed",
    ):
        assert key in row
    assert sum(row["size_distribution"].values()) == pytest.approx(1)


def test_history_exports_are_json_safe_and_readable(capsys):
    state = play_game("reactive", 4)
    payload = history_as_dict(state)
    json.dumps(payload)
    assert payload["rounds"][0]["size"] in {size.name.lower() for size in Size}
    assert "R01" in history_as_text(state)
    assert main(["--history", "reactive", "--history-seed", "4"]) == 0
    assert "score=" in capsys.readouterr().out


def test_strategy_validation():
    with pytest.raises(ValueError):
        make_strategy("unknown")
    with pytest.raises(ValueError):
        simulate_strategies(0)
    with pytest.raises(ValueError):
        simulate_strategies(1, strategies=("random", "random"))
