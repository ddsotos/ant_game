"""Paired-seed diagnostic simulation utilities (not run for v0.7 delivery)."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict
from typing import Any, Iterable

from .content import DISASTERS, TRAITS
from .engine import GameEngine
from .models import GameState, Size
from .strategies import make_strategy, strategy_names


def make_engine(seed: int, **settings: Any) -> GameEngine:
    return GameEngine(TRAITS, DISASTERS, seed=seed, **settings)


def play_game(strategy: str, seed: int, **settings: Any) -> GameState:
    engine = make_engine(seed, **settings)
    return engine.run(make_strategy(strategy, seed=seed))


def _game_metrics(
    state: GameState,
    design_roles: dict[str, str],
) -> dict[str, Any]:
    history = state.history
    actions = [action for row in history for action in row.actions]
    retained = [card_id for row in history for card_id in row.retained]
    activated_ids = [
        action["card_id"] for action in actions if action["kind"] == "activate"
    ]
    activation_roles = Counter(design_roles.get(card_id, "Unknown") for card_id in activated_ids)
    size_counts = Counter(row.size.name.lower() for row in history)
    shield_granted = sum(sum(row.defense_by_problem.values()) for row in history)
    shield_used = sum(
        sum(min(row.problem_rolls[tag], amount) for tag, amount in row.defense_by_problem.items())
        for row in history
    )
    before_peak = history[:3]
    peak_and_after = history[3:]

    def mean_size(rows):
        return statistics.fmean(int(row.size) for row in rows) if rows else None

    return {
        "score": state.prosperity,
        "survived": True,
        "extinction_round": None,
        "rounds_played": len(history),
        "size_counts": dict(size_counts),
        "size_changes": sum(row.size != row.size_before for row in history),
        "retained": len(retained),
        "played": sum(action["kind"] == "play" for action in actions),
        "supported": sum(action["kind"] == "support" for action in actions),
        "activated": sum(action["kind"] == "activate" for action in actions),
        "foundation_activated": activation_roles["Foundation"],
        "bridge_activated": activation_roles["Bridge"],
        "payoff_activated": activation_roles["Payoff"],
        "extreme_activated": 0,
        "push_outs": sum(len(row.pushed_out) for row in history),
        "extremes_retained": 0,
        "shield_granted": shield_granted,
        "shield_used": shield_used,
        "shield_surplus": shield_granted - shield_used,
        "raw_damage": sum(sum(row.problem_rolls.values()) for row in history),
        "damage": sum(row.problem_penalty for row in history),
        "max_action_chain": max(
            (sum(action["kind"] == "activate" for action in row.actions) for row in history),
            default=0,
        ),
        "pre_peak_mean_size": mean_size(before_peak),
        "peak_after_mean_size": mean_size(peak_and_after),
        "changed_at_peak": bool(
            before_peak and peak_and_after
            and abs(mean_size(before_peak) - mean_size(peak_and_after)) >= 0.5
        ),
        "final_hand": len(state.hand),
    }


def _average(values: Iterable[float | int | None]) -> float | None:
    usable = [value for value in values if value is not None]
    return statistics.fmean(usable) if usable else None


def _aggregate(games: list[dict[str, Any]], win_credit: float) -> dict[str, Any]:
    size_counts = Counter()
    for game in games:
        size_counts.update(game["size_counts"])
    total_rounds = sum(size_counts.values())
    scalar = (
        "score",
        "rounds_played",
        "size_changes",
        "retained",
        "played",
        "supported",
        "activated",
        "foundation_activated",
        "bridge_activated",
        "payoff_activated",
        "extreme_activated",
        "push_outs",
        "extremes_retained",
        "shield_granted",
        "shield_used",
        "shield_surplus",
        "raw_damage",
        "damage",
        "max_action_chain",
        "pre_peak_mean_size",
        "peak_after_mean_size",
        "final_hand",
    )
    return {
        "games": len(games),
        "win_rate": win_credit / len(games),
        "survival_rate": sum(game["survived"] for game in games) / len(games),
        "median_score": statistics.median(game["score"] for game in games),
        **{f"mean_{key}": _average(game[key] for game in games) for key in scalar},
        "peak_behavior_change_rate": sum(game["changed_at_peak"] for game in games) / len(games),
        "size_distribution": {
            size.name.lower(): (size_counts[size.name.lower()] / total_rounds if total_rounds else 0.0)
            for size in Size
        },
    }


def simulate_strategies(
    games: int = 1000,
    *,
    seed_start: int = 0,
    strategies: Iterable[str] | None = None,
    **settings: Any,
) -> dict[str, Any]:
    if games <= 0:
        raise ValueError("games must be positive")
    names = tuple(strategies or strategy_names())
    if not names or len(names) != len(set(names)):
        raise ValueError("strategies must be a non-empty unique sequence")
    per_strategy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    wins = Counter()
    design_roles = {card.id: card.design_role for card in TRAITS}
    for seed in range(seed_start, seed_start + games):
        states = {name: play_game(name, seed, **settings) for name in names}
        best_key = max(state.prosperity for state in states.values())
        winners = [
            name for name, state in states.items()
            if state.prosperity == best_key
        ]
        credit = 1 / len(winners)
        for winner in winners:
            wins[winner] += credit
        for name, state in states.items():
            per_strategy[name].append(_game_metrics(state, design_roles))
    return {
        "metadata": {
            "games_per_strategy": games,
            "seed_start": seed_start,
            "rounds": 5,
            "paired_seeds": True,
            "win_definition": "prosperity; ties split",
            "strategies": list(names),
            "settings": settings,
        },
        "strategies": {
            name: _aggregate(per_strategy[name], wins[name]) for name in names
        },
    }


def history_as_dict(state: GameState) -> dict[str, Any]:
    def json_safe(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: json_safe(item) for key, item in value.items()}
        if isinstance(value, (tuple, list, set, frozenset)):
            return [json_safe(item) for item in value]
        return value

    rows = []
    for row in state.history:
        data = json_safe(asdict(row))
        data["size"] = row.size.name.lower()
        data["size_before"] = row.size_before.name.lower()
        rows.append(data)
    return {
        "seed": state.seed,
        "environments": list(state.disaster_ids),
        "score": state.prosperity,
        "rounds": rows,
    }


def history_as_text(state: GameState) -> str:
    lines = [
        f"seed={state.seed} environments={','.join(state.disaster_ids)} score={state.prosperity}"
    ]
    for row in state.history:
        actions = ",".join(action["kind"] for action in row.actions) or "-"
        retained = ",".join(row.retained) or "-"
        lines.append(
            f"R{row.round_number} environment={row.disaster_id} size={row.size.name:<6} "
            f"keep=[{retained}] actions=[{actions}] "
            f"rolls={dict(row.problem_rolls)} penalty={row.problem_penalty} "
            f"prosperity={row.prosperity_delta:+d} total={row.total_prosperity} "
            f"optimization={row.optimization_met}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=1000)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--include-exploits", action="store_true")
    parser.add_argument("--strategies", nargs="+", choices=strategy_names(include_exploits=True))
    parser.add_argument("--history", choices=strategy_names(include_exploits=True))
    parser.add_argument("--history-seed", type=int, default=0)
    parser.add_argument("--json", action="store_true")
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
        print(f"paired seeds={args.games}; survival first; ties split")
        print(
            f"{'strategy':22} {'score':>7} {'survive':>8} {'win%':>7} "
            f"{'damage':>8} {'shield':>8} {'payoff':>8}"
        )
        for name, row in result["strategies"].items():
            print(
                f"{name:22} {row['mean_score']:7.2f} {100 * row['survival_rate']:7.1f}% "
                f"{100 * row['win_rate']:6.1f}% {row['mean_damage']:8.2f} "
                f"{row['mean_shield_used']:8.2f} {row['mean_payoff_activated']:8.2f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "history_as_dict",
    "history_as_text",
    "make_engine",
    "play_game",
    "simulate_strategies",
]
