"""Fast paired-seed simulation, metrics, and history inspection CLI."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict
from typing import Any, Iterable

from .content import EVENTS, TRAITS
from .engine import GameEngine
from .models import GameState, RoundRecord, Size
from .strategies import make_strategy, strategy_names


def play_game(strategy: str, seed: int, *, rounds: int = 18) -> GameState:
    engine = GameEngine(TRAITS, EVENTS, seed=seed, rounds=rounds)
    return engine.run(make_strategy(strategy, seed=seed))


def _game_metrics(state: GameState) -> dict[str, Any]:
    history = state.history
    first_iii = next((i for i, row in enumerate(history) if row.event_stage == 3), None)
    pre = history[:first_iii] if first_iii is not None else history
    post = history[first_iii:] if first_iii is not None else []
    after_iii_moves = []
    for i, row in enumerate(history[:-1]):
        if row.event_stage == 3:
            after_iii_moves.append(int(history[i + 1].size) - int(row.size))

    def mean_size(rows):
        return statistics.fmean(int(row.size) for row in rows) if rows else None

    def change_rate(rows):
        return sum(row.size != row.size_before for row in rows) / len(rows) if rows else None

    acquired = Counter(card_id for row in history for card_id in row.acquired_trait_ids)
    discarded = Counter(card_id for row in history for card_id in row.discarded_trait_ids)
    shed = Counter(row.shed_trait_id for row in history if row.shed_trait_id)
    consumed = Counter(card_id for row in history for card_id in row.latent_consumed)
    activated = Counter(card_id for row in history for card_id in row.latent_activated)
    size_counts = Counter(row.size.name.lower() for row in history)
    size_acquisitions = Counter(
        row.size.name.lower() for row in history if row.acquired_trait_ids
    )
    recovery_rounds = sum(
        bool(row.shed_trait_id and i + 1 < len(history)
             and history[i + 1].evolution_draw_count > row.evolution_draw_count)
        for i, row in enumerate(history)
    )
    return {
        "score": state.prosperity,
        "size_counts": dict(size_counts),
        "size_changes": sum(row.size != row.size_before for row in history),
        "traits_acquired": sum(acquired.values()),
        "traits_discarded": sum(discarded.values()),
        "traits_shed": sum(shed.values()),
        "traits_consumed": sum(consumed.values()),
        "trait_acquired_counts": dict(acquired),
        "trait_discarded_counts": dict(discarded),
        "multi_acquire_rounds": sum(len(row.acquired_trait_ids) > 1 for row in history),
        "budget_spent": sum(row.evolution_budget_spent for row in history),
        "budget_available": sum(row.evolution_budget for row in history),
        "budget_utilization": (
            sum(row.evolution_budget_spent for row in history)
            / sum(row.evolution_budget for row in history)
            if sum(row.evolution_budget for row in history) else 0.0
        ),
        "size_acquisition_counts": dict(size_acquisitions),
        "trait_shed_counts": dict(shed),
        "latent_activated_counts": dict(activated),
        "latent_consumed_counts": dict(consumed),
        "evolution_load_rounds": sum(row.evolution_load for row in history),
        "evolution_draws": sum(row.evolution_draw_count for row in history),
        "zero_evolution_draws": sum(row.evolution_draw_count == 0 for row in history),
        "evolution_recovery_rounds": recovery_rounds,
        "lost_evolution_draws": sum(row.size.evolution_draw - row.evolution_draw_count for row in history),
        "event_damage": sum(row.damage for row in history),
        "growth_cost": sum(row.growth_cost for row in history),
        "stage_iii_count": sum(row.event_stage == 3 for row in history),
        "stage_iii_damage": sum(row.damage for row in history if row.event_stage == 3),
        "pre_stage_iii_mean_size": mean_size(pre),
        "post_stage_iii_mean_size": mean_size(post),
        "pre_stage_iii_size_change_rate": change_rate(pre),
        "post_stage_iii_size_change_rate": change_rate(post),
        "pre_stage_iii_trait_take_rate": sum(bool(row.acquired_trait_ids) for row in pre) / len(pre) if pre else None,
        "post_stage_iii_trait_take_rate": sum(bool(row.acquired_trait_ids) for row in post) / len(post) if post else None,
        "after_stage_iii_size_moves": after_iii_moves,
        "behavior_changed_after_stage_iii": bool(pre and post and abs(mean_size(pre) - mean_size(post)) >= 0.5),
    }


def _average(values: Iterable[float | int | None]) -> float | None:
    usable = [value for value in values if value is not None]
    return statistics.fmean(usable) if usable else None


def _aggregate(games: list[dict[str, Any]], win_credit: float) -> dict[str, Any]:
    count = len(games)
    size_counts = Counter()
    acquired = Counter()
    discarded = Counter()
    shed = Counter()
    activated = Counter()
    consumed = Counter()
    moves = Counter()
    for game in games:
        size_counts.update(game["size_counts"])
        acquired.update(game["trait_acquired_counts"])
        discarded.update(game["trait_discarded_counts"])
        shed.update(game["trait_shed_counts"])
        activated.update(game["latent_activated_counts"])
        consumed.update(game["latent_consumed_counts"])
        moves.update("lower" if x < 0 else "raise" if x > 0 else "hold" for x in game["after_stage_iii_size_moves"])
    total_rounds = sum(size_counts.values())
    scalar_keys = (
        "size_changes", "traits_acquired", "traits_discarded", "traits_shed", "traits_consumed", "evolution_load_rounds",
        "evolution_draws", "zero_evolution_draws", "evolution_recovery_rounds", "lost_evolution_draws", "event_damage", "growth_cost", "stage_iii_count",
        "stage_iii_damage", "multi_acquire_rounds", "budget_spent", "budget_available", "budget_utilization",
        "pre_stage_iii_mean_size", "post_stage_iii_mean_size",
        "pre_stage_iii_size_change_rate", "post_stage_iii_size_change_rate",
        "pre_stage_iii_trait_take_rate", "post_stage_iii_trait_take_rate",
    )
    return {
        "games": count,
        "mean_score": _average(game["score"] for game in games),
        "median_score": statistics.median(game["score"] for game in games),
        "min_score": min(game["score"] for game in games),
        "max_score": max(game["score"] for game in games),
        "win_rate": win_credit / count,
        **{f"mean_{key}": _average(game[key] for game in games) for key in scalar_keys},
        "size_distribution": {size.name.lower(): size_counts[size.name.lower()] / total_rounds for size in Size},
        "trait_acquisition_rate_per_game": {card_id: value / count for card_id, value in sorted(acquired.items())},
        "trait_discard_rate_per_game": {card_id: value / count for card_id, value in sorted(discarded.items())},
        "trait_shed_rate_per_game": {card_id: value / count for card_id, value in sorted(shed.items())},
        "latent_activation_rate_per_game": {card_id: value / count for card_id, value in sorted(activated.items())},
        "latent_consumed_rate_per_game": {card_id: value / count for card_id, value in sorted(consumed.items())},
        "size_acquisition_rate_per_game": {
            size.name.lower(): sum(game["size_acquisition_counts"].get(size.name.lower(), 0) for game in games) / count
            for size in Size
        },
        "games_with_behavior_change_after_stage_iii_rate": sum(game["behavior_changed_after_stage_iii"] for game in games) / count,
        "after_stage_iii_size_response": dict(moves),
    }


def simulate_strategies(
    games: int = 1000,
    *,
    seed_start: int = 0,
    strategies: Iterable[str] | None = None,
    rounds: int = 18,
) -> dict[str, Any]:
    """Run every policy on identical seeds and return JSON-compatible metrics.

    A tie for the best score awards ``1 / number_of_tied_strategies`` win credit.
    """
    if games <= 0:
        raise ValueError("games must be positive")
    names = tuple(strategies or strategy_names())
    if not names or len(set(names)) != len(names):
        raise ValueError("strategies must be a non-empty unique sequence")
    per_strategy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    wins = Counter()
    for seed in range(seed_start, seed_start + games):
        states = {name: play_game(name, seed, rounds=rounds) for name in names}
        best = max(state.prosperity for state in states.values())
        winners = [name for name, state in states.items() if state.prosperity == best]
        credit = 1 / len(winners)
        for winner in winners:
            wins[winner] += credit
        for name, state in states.items():
            per_strategy[name].append(_game_metrics(state))
    return {
        "metadata": {
            "games_per_strategy": games,
            "seed_start": seed_start,
            "rounds": rounds,
            "paired_seeds": True,
            "win_definition": "highest score for each seed; ties split equally",
            "strategies": list(names),
        },
        "strategies": {name: _aggregate(per_strategy[name], wins[name]) for name in names},
    }


def history_as_dict(state: GameState) -> dict[str, Any]:
    def record(row: RoundRecord) -> dict[str, Any]:
        data = asdict(row)
        for key in ("size", "size_before"):
            data[key] = Size(data[key]).name.lower()
        data["event_kind"] = row.event_kind.value
        return data
    return {"seed": state.seed, "score": state.prosperity, "rounds": [record(row) for row in state.history]}


def history_as_text(state: GameState) -> str:
    lines = [f"seed={state.seed} score={state.prosperity}"]
    for row in state.history:
        stage = "shock" if row.event_stage is None else str(row.event_stage)
        trait = ",".join(row.acquired_trait_ids) or "-"
        move = "=" if row.size == row.size_before else f"{row.size_before.name}->{row.size.name}"
        lines.append(
            f"R{row.round_number:02d} {move:<14} {row.size.name:<6} {row.event_name} [{stage}] "
            f"damage={row.damage} raw_delta={row.raw_prosperity_delta} "
            f"growth={row.growth_cost} "
            f"delta={row.actual_prosperity_delta} total={row.total_prosperity} "
            f"draw={row.evolution_draw_count} load={row.evolution_load} "
            f"budget={row.evolution_budget_spent}/{row.evolution_budget} take={trait}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=1000)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--strategies", nargs="+", choices=tuple(strategy_names(include_exploits=True)))
    parser.add_argument("--include-exploits", action="store_true")
    parser.add_argument("--history", metavar="STRATEGY", choices=tuple(strategy_names(include_exploits=True)))
    parser.add_argument("--history-seed", type=int, default=0)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    if args.history:
        state = play_game(args.history, args.history_seed)
        print(json.dumps(history_as_dict(state), ensure_ascii=False, indent=2) if args.json else history_as_text(state))
        return 0
    names = tuple(args.strategies) if args.strategies else strategy_names(include_exploits=args.include_exploits)
    result = simulate_strategies(args.games, seed_start=args.seed_start, strategies=names)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"paired seeds={args.games}; ties split equally")
        print(f"{'strategy':22} {'mean':>7} {'median':>7} {'win%':>7} {'damage':>8} {'lost draws':>11}")
        for name, metrics in result["strategies"].items():
            print(f"{name:22} {metrics['mean_score']:7.2f} {metrics['median_score']:7.1f} "
                  f"{100 * metrics['win_rate']:6.1f}% {metrics['mean_event_damage']:8.2f} "
                  f"{metrics['mean_lost_evolution_draws']:11.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["history_as_dict", "history_as_text", "play_game", "simulate_strategies"]
