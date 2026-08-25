"""Small Japanese browser adapter for the deterministic ant game engine."""

from __future__ import annotations

import argparse
import copy
import json
import threading
import uuid
import webbrowser
from collections import Counter
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from .content import DISASTERS, TRAITS
from .engine import PROBLEM_IDS, GameEngine, InvalidDecision
from .localization_ja import (
    CARD_TEXTS,
    EVENT_NAMES,
    ROLE_NAMES,
    SIZE_NAMES,
    TAG_COLORS,
    TAG_NAMES,
    TAG_SYMBOLS,
    card_name,
    event_name,
    optimization_name,
)
from .models import ActionOption, CardRole, EnvironmentCard, GameState, RoundPhase, Size, TraitCard

STATIC_DIR = Path(__file__).with_name("web_static")
TAG_INFO = {
    tag: (TAG_NAMES[tag], TAG_COLORS[tag], TAG_SYMBOLS[tag])
    for tag in TAG_NAMES
}
PROBLEM_NAMES = {"raid": "襲撃", "sanitation": "衛生"}
SIZE_LABELS = SIZE_NAMES


@dataclass
class Session:
    engine: GameEngine
    state: GameState
    undo_stack: list[GameState]


class WebGameService:
    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}
        self._lock = threading.RLock()

    def config(self) -> dict[str, Any]:
        return {"tags": [self._tag_data(tag) for tag in TAG_INFO], "environments": [self._environment_data(item) for item in DISASTERS], "problems": [self._problem_data(problem) for problem in PROBLEM_IDS]}

    def card_catalog(self) -> dict[str, Any]:
        cards = [self._card_data(card, card.id) for card in TRAITS]
        return {
            "count": len(cards),
            "tags": [self._tag_data(tag) for tag in TAG_INFO],
            "roles": sorted({card["role"] for card in cards}),
            "cards": cards,
        }

    def environment_export(self) -> dict[str, Any]:
        """Return a self-contained, Japanese dataset suitable for ChatGPT input."""

        environments: list[dict[str, Any]] = []
        for environment in DISASTERS:
            localized = EVENT_NAMES.get(environment.id, (environment.name, environment.text))
            patterns = []
            for requirement in environment.optimizations:
                patterns.append({
                    "name": requirement.name,
                    "requirements": {
                        TAG_NAMES.get(tag, tag): amount
                        for tag, amount in requirement.required_root_tags.items()
                    },
                    "source_taxon": requirement.source_taxon,
                    "biology_basis": requirement.biology_basis,
                    "biology_source": requirement.biology_source,
                    "description": requirement.text,
                })
            roll_rules = {
                PROBLEM_NAMES.get(problem, problem): {
                    "dice": f"{rule.rolls}d4",
                    "combine": "合計" if rule.combine == "sum" else "最大値",
                    "fixed_bonus": rule.bonus,
                    "previous_round_value_plus": rule.previous_round_bonus,
                }
                for problem, rule in environment.problem_roll_rules.items()
            }
            environments.append({
                "id": environment.id,
                "name": localized[0] or environment.name,
                "description": localized[1] or environment.text,
                "deck": "最終環境" if environment.deck == "finale" else "通常環境",
                "optimizations": patterns,
                "problem_roll_overrides": roll_rules,
            })
        return {
            "schema_version": "ant-game-environments-v0.12",
            "language": "ja",
            "rules_note": (
                "現行版に独立した災害カードはありません。環境変化カードと、"
                "毎ラウンド個別に判定する2つの問題に分かれています。"
            ),
            "independent_problems": [
                {
                    "id": problem,
                    "name": PROBLEM_NAMES.get(problem, problem),
                    "default_roll": "1d4",
                    "resolution": "n=max(0, 出目-シールド)。n=0なら減点0、それ以外は2^nを繁栄プールから減点。",
                }
                for problem in PROBLEM_IDS
            ],
            "environment_cards": environments,
        }

    def new_game(self, seed: int = 0) -> dict[str, Any]:
        with self._lock:
            engine = GameEngine(TRAITS, DISASTERS, seed=int(seed))
            state = engine.new_game()
            engine.start_round(state)
            game_id = uuid.uuid4().hex
            self.sessions[game_id] = Session(engine, state, [])
            return {"game_id": game_id, "state": self.project(engine, state)}

    def act(self, game_id: str, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            session = self.sessions.get(game_id)
            if session is None:
                raise InvalidDecision("ゲームが見つかりません。新しいゲームを開始してください。")
            engine = session.engine
            if kind == "undo":
                if not session.undo_stack:
                    raise InvalidDecision("戻せる操作がありません")
                session.state = session.undo_stack.pop()
                return {"game_id": game_id, "state": self.project(engine, session.state, session)}
            snapshot = copy.deepcopy(session.state)
            state = copy.deepcopy(session.state)
            if kind == "size": engine.choose_size(state, self._parse_size(payload.get("size")))
            elif kind == "retain": engine.retain_cards(state, tuple(payload.get("card_ids", ())))
            elif kind == "expand_candidates": engine.expand_retention_candidates(state)
            elif kind == "play": engine.play_card(state, str(payload.get("card_id", "")), int(payload.get("column", -1)))
            elif kind == "support": engine.insert_support(state, str(payload.get("card_id", "")), int(payload.get("column", -1)))
            elif kind == "activate": engine.activate(state, int(payload.get("column", -1)), int(payload.get("option", 0)), payload.get("target_card_id"))
            elif kind == "resolve":
                engine.resolve_environment(state)
                if not state.finished: engine.start_round(state)
            else: raise InvalidDecision("不明な操作です。")
            session.state = state
            session.undo_stack.append(snapshot)
            return {"game_id": game_id, "state": self.project(engine, state, session)}

    def get(self, game_id: str) -> dict[str, Any]:
        with self._lock:
            session = self.sessions.get(game_id)
            if session is None: raise InvalidDecision("ゲームが見つかりません。")
            return {"game_id": game_id, "state": self.project(session.engine, session.state, session)}

    @staticmethod
    def _parse_size(raw: Any) -> Size:
        try: return {size.name.lower(): size for size in Size}[str(raw).lower()]
        except KeyError as exc: raise InvalidDecision("選べないサイズです。") from exc

    def project(self, engine: GameEngine, state: GameState, session: Session | None = None) -> dict[str, Any]:
        context = state.current_round
        environment = engine.current_disaster(state)
        board_tags = engine.board_tags(state)
        optimization = self._optimization_data(environment, board_tags)
        shields = self._shield_totals(context) if context else {}
        round_base = context.prosperity_base if context else 0
        round_multiplier = state.size.prosperity_multiplier
        live_penalty = self._live_problem_penalty(context, shields) if context else 0
        gain_breakdown = self._gain_breakdown(context, round_multiplier, live_penalty) if context else {
            "base": 0, "activation": 0, "card": 0, "storage": 0, "tag": 0,
            "pool_before_problems": 0, "problem_penalty": 0,
            "pool_after_problems": 0, "multiplier": round_multiplier, "delta": 0,
        }
        return {
            "phase": state.phase.value, "finished": state.finished,
            "round": context.round_number if context else state.round_number,
            "prosperity": state.prosperity, "size": state.size.name.lower(),
            "size_name": SIZE_LABELS.get(state.size.name, state.size.name),
            "legal_sizes": [self._size_data(engine, size) for size in engine.legal_sizes(state)] if state.phase is RoundPhase.SIZE else [],
            "retention_limit": min(engine.retention_limit(state), engine.hand_limit - len(state.hand)) if context else 0,
            "retention_trade_used": bool(context and context.retention_trade_used),
            "can_expand_candidates": bool(
                context and state.phase is RoundPhase.RETAIN and not context.retention_trade_used
                and min(engine.retention_limit(state), engine.hand_limit - len(state.hand)) >= 1
                and len(state.trait_deck) + len(state.trait_discard)
                >= 2 + state.pending_candidate_trade_bonus
            ),
            "hand_limit": engine.hand_limit,
            "pending_retention_bonus": state.pending_retention_bonus,
            "pending_candidate_bonus": state.pending_candidate_bonus,
            "pending_candidate_trade_bonus": state.pending_candidate_trade_bonus,
            "candidate_draw_count": context.candidate_draw_count if context else 0,
            "round_prosperity_base": round_base,
            "round_prosperity_multiplier": round_multiplier,
            "round_prosperity_delta": gain_breakdown["delta"],
            "round_gain_breakdown": gain_breakdown,
            "forecast": [self._forecast_data(engine, state, i) for i in range(len(state.disaster_ids))],
            "environment": {**self._environment_data(environment), "optimizations": optimization["optimizations"], "optimization_met": optimization["met"]},
            "optimizations": optimization["optimizations"],
            "problems": [self._problem_data(problem, context, shields.get(problem, 0)) for problem in PROBLEM_IDS] if context else [],
            "candidates": [self._card_data(engine.traits[item.card_id], item.instance_id) for item in (context.candidate_instances if context else ())],
            "hand": [self._hand_card_data(engine, state, item) for item in state.hand],
            "columns": [self._column_data(engine, state, i) for i in range(len(state.columns))],
            "last_result": None if not state.history else self._result_data(engine, state.history[-1]),
            "can_undo": bool(session and session.undo_stack),
        }

    def _optimization_data(self, environment: EnvironmentCard, board_tags: Mapping[str, int]) -> dict[str, Any]:
        result = []
        labels = self._optimization_labels(environment)
        for index, item in enumerate(environment.optimizations):
            progress = self._requirements_data(item.required_root_tags, board_tags)
            result.append({"name": labels[index], "text": item.text, "source_taxon": item.source_taxon, "requirements": progress, "met": all(entry["missing"] == 0 for entry in progress)})
        return {"optimizations": result, "met": not result or any(item["met"] for item in result)}

    @staticmethod
    def _optimization_labels(environment: EnvironmentCard) -> tuple[str, ...]:
        """Return per-pattern Japanese names from the UI localization only."""

        if not environment.optimizations:
            return ()
        localized = optimization_name(environment.id, "")
        names = tuple(part.strip() for part in localized.split("／") if part.strip())
        return tuple(
            names[index] if index < len(names) else f"最適化{index + 1}"
            for index in range(len(environment.optimizations))
        )

    @staticmethod
    def _shield_totals(context: Any) -> dict[str, int]:
        return {
            problem: sum(shield.amount for shield in context.shields if shield.problem_id == problem)
            for problem in PROBLEM_IDS
        }

    @classmethod
    def _live_problem_penalty(cls, context: Any, shields: Mapping[str, int]) -> int:
        total = 0
        for problem in PROBLEM_IDS:
            roll = context.problem_rolls.get(problem, 0)
            vulnerability = sum(
                item.amount for item in context.vulnerabilities if item.problem_id == problem
            )
            unblocked = max(0, roll + vulnerability - shields.get(problem, 0))
            total += 0 if unblocked == 0 else 2 ** unblocked
        return total

    @staticmethod
    def _gain_breakdown(context: Any, multiplier: int, problem_penalty: int) -> dict[str, int]:
        pool_before = context.prosperity_base
        pool_after = max(0, pool_before - problem_penalty)
        return {
            "base": context.base_prosperity,
            "activation": context.activation_prosperity,
            "card": context.card_prosperity,
            "storage": context.storage_prosperity,
            "tag": context.tag_prosperity,
            "pool_before_problems": pool_before,
            "problem_penalty": problem_penalty,
            "pool_after_problems": pool_after,
            "multiplier": multiplier,
            "delta": pool_after * multiplier,
        }

    def _hand_card_data(self, engine: GameEngine, state: GameState, instance: Any) -> dict[str, Any]:
        data = self._card_data(engine.traits[instance.card_id], instance.instance_id)
        data["placement_options"] = [self._placement_option_data(engine, state, i, engine.traits[instance.card_id]) for i in range(len(state.columns))]
        return data

    def _placement_option_data(self, engine: GameEngine, state: GameState, index: int, card: TraitCard) -> dict[str, Any]:
        existing = list(state.columns[index].cards)
        if len(existing) >= engine.column_capacity: existing = existing[1:]
        tags: Counter[str] = Counter()
        for played in existing: tags.update(engine.traits[played.card_id].counted_root_tags)
        missing = sum(max(0, required - tags.get(tag, 0)) for tag, required in card.activation_requirements.items())
        return {"column": index, "status": "ready" if missing == 0 else "one-short" if missing == 1 else "other", "requirements": self._requirements_data(card.activation_requirements, tags), "fallback": bool(card.fallback_options)}

    def _forecast_data(self, engine: GameEngine, state: GameState, index: int) -> dict[str, Any]:
        environment = engine.disasters[state.disaster_ids[index]]
        return {**self._environment_data(environment), "round": index + 1, "current": not state.finished and index == state.round_number, "completed": index < state.round_number}

    @classmethod
    def _environment_data(cls, environment: EnvironmentCard) -> dict[str, Any]:
        localized = EVENT_NAMES.get(environment.id, (environment.name, environment.text))
        labels = cls._optimization_labels(environment)
        optimizations = [{"name": labels[index], "text": item.text, "source_taxon": item.source_taxon, "requirements": cls._requirements_data_static(item.required_root_tags)} for index, item in enumerate(environment.optimizations)]
        # ``optimization`` is retained as a read-only compatibility alias for
        # older debug clients; new clients must use ``optimizations``.
        legacy = optimizations[0] if optimizations else {"name": "最適化なし", "text": "", "requirements": []}
        return {"id": environment.id, "name": localized[0] or environment.name, "text": localized[1] or environment.text, "deck": environment.deck, "finale": environment.deck == "finale", "optimizations": optimizations, "optimization": legacy, "problem_roll_rules": {problem: {"rolls": rule.rolls, "combine": rule.combine, "bonus": rule.bonus, "previous_round_bonus": rule.previous_round_bonus} for problem, rule in environment.problem_roll_rules.items()}}

    @classmethod
    def _problem_data(cls, problem: str, context: Any = None, shield: int = 0) -> dict[str, Any]:
        if context is None: return {"id": problem, "name": PROBLEM_NAMES.get(problem, problem), "roll": None, "raw_rolls": [], "selected_roll": None, "modifier": 0, "roll_source": None, "combine": "highest", "shield": shield, "unblocked": None, "penalty": None}
        roll = context.problem_rolls.get(problem)
        raw = tuple(context.problem_raw_rolls.get(problem, ()))
        selected = context.problem_selected_rolls.get(problem)
        modifier = context.problem_modifiers.get(problem, 0)
        vulnerability = sum(
            item.amount for item in context.vulnerabilities if item.problem_id == problem
        )
        effective_roll = roll + vulnerability if roll is not None else None
        unblocked = max(0, effective_roll - shield) if effective_roll is not None else None
        return {"id": problem, "name": PROBLEM_NAMES.get(problem, problem), "roll": roll, "effective_roll": effective_roll, "vulnerability": vulnerability, "raw_rolls": list(raw), "selected_roll": selected, "modifier": modifier, "roll_source": context.problem_roll_sources.get(problem, "dice"), "combine": context.problem_roll_combines.get(problem, "highest"), "shield": shield, "unblocked": unblocked, "penalty": None if unblocked is None else (0 if unblocked == 0 else 2 ** unblocked)}

    @staticmethod
    def _tag_data(tag: str, count: int | None = None) -> dict[str, Any]:
        name, color, symbol = TAG_INFO.get(tag, (tag, "#777777", "dot"))
        data = {"id": tag, "name": name, "color": color, "symbol": symbol}
        if count is not None: data["count"] = count
        return data

    @classmethod
    def _requirements_data_static(cls, requirements: Mapping[str, int], actual: Mapping[str, int] | None = None) -> list[dict[str, Any]]:
        return [{**cls._tag_data(tag), "required": required, "actual": actual.get(tag, 0) if actual is not None else None, "missing": max(0, required - actual.get(tag, 0)) if actual is not None else None} for tag, required in sorted(requirements.items())]

    _requirements_data = _requirements_data_static

    @staticmethod
    def _size_data(engine: GameEngine, size: Size) -> dict[str, Any]:
        return {"id": size.name.lower(), "name": SIZE_LABELS.get(size.name, size.name), "multiplier": size.prosperity_multiplier, "retention": engine.retention_curve[size]}

    def _column_data(self, engine: GameEngine, state: GameState, index: int) -> dict[str, Any]:
        column = state.columns[index]; all_tags = engine.column_tags(state, index); activation_tags = engine.activation_tags(state, index)
        cards = []
        for position, played in enumerate(column.cards):
            card = engine.traits[played.card_id]
            cards.append({**self._card_data(card, played.instance_id), "top": position == len(column.cards) - 1, "support": played.is_support, "activated": bool(state.current_round and played.activated_round == state.current_round.round_number), "stored_count": len(played.stored_cards), "storage_income_per_card": played.storage_income_per_card, "storage_income_next_round": len(played.stored_cards) * played.storage_income_per_card})
        activations = []
        if column.top is not None and state.phase is RoundPhase.ACTIONS:
            top = column.top; card = engine.traits[top.card_id]; requirements = self._requirements_data(card.activation_requirements, activation_tags)
            already = top.activated_round == state.current_round.round_number; role_ok = card.role in (CardRole.ACTION, CardRole.STARTER); met = all(item["missing"] == 0 for item in requirements); options = card.options if met else card.fallback_options
            recovery_targets = [{"id": played.instance_id, "name": card_name(played.card_id, played.card_id)} for played in column.cards[:-1] if not played.is_support and engine.traits[played.card_id].role is not CardRole.STARTER and not played.stored_cards and played.activated_round != state.current_round.round_number and state.current_round.recovered_lower_card_id is None]
            for option_index, option in enumerate(options):
                requires_recovery = option.recover_lower_card
                if requires_recovery:
                    has_target = bool(recovery_targets) and len(state.hand) < engine.hand_limit
                elif option.store_hand_card:
                    has_target = bool(state.hand)
                else:
                    has_target = True
                enabled = role_ok and not already and has_target
                reason = "" if enabled else ("このラウンドは起動済みです。" if already else "手札がいっぱいです。" if requires_recovery and len(state.hand) >= engine.hand_limit else "回収できる下段カードを選んでください。" if requires_recovery else "貯蔵する手札カードを選んでください。" if option.store_hand_card and not has_target else "起動条件を満たしていません。")
                activations.append({"option": option_index, "tier": "strong" if met else "fallback", "effect": self._option_data(option), "enabled": enabled, "requires_storage_target": option.store_hand_card, "requires_recovery_target": requires_recovery, "target_candidates": recovery_targets if requires_recovery else [item.instance_id for item in state.hand] if option.store_hand_card else [], "reason": reason, "requirements": requirements})
        return {"index": index, "name": f"進化列 {index + 1}", "cards": cards, "tags": [self._tag_data(tag, count) for tag, count in sorted(all_tags.items()) if tag in TAG_INFO], "activation_tags": [self._tag_data(tag, count) for tag, count in sorted(activation_tags.items()) if tag in TAG_INFO], "capacity": engine.column_capacity, "next_pushed": card_name(column.cards[0].card_id, column.cards[0].card_id) if len(column.cards) >= engine.column_capacity else None, "activations": activations}

    def _card_data(self, card: TraitCard, instance_id: str) -> dict[str, Any]:
        role = "初期形質" if card.role is CardRole.STARTER else ROLE_NAMES.get(card.design_role, card.design_role)
        return {"id": instance_id, "card_id": card.id, "name": card_name(card.id, card.name), "text": CARD_TEXTS.get(card.id, card.text), "subject_taxon": card.source_taxon, "biology_basis": card.biology_basis, "biology_source": card.biology_source, "tags": [self._tag_data(tag, card.counted_root_tags[tag]) for tag in sorted(card.root_tags) if tag in TAG_INFO], "requirements": self._requirements_data(card.activation_requirements), "role": role, "options": [self._option_data(option) for option in card.options], "fallback_options": [self._option_data(option) for option in card.fallback_options], "on_pushed_out": self._option_data(card.on_pushed_out) if card.on_pushed_out else None}

    @staticmethod
    def _option_data(option: ActionOption) -> dict[str, Any]:
        return {
            "text": option.text,
            "prosperity": option.prosperity,
            "draw_cards": option.draw_cards,
            "retention_bonus": option.retention_bonus,
            "recover_lower_card": option.recover_lower_card,
            "next_candidate_bonus": option.next_candidate_bonus,
            "store_hand_card": option.store_hand_card,
            "storage_income_per_card": option.storage_income_per_card,
            "tag_prosperity_cap": option.tag_prosperity_cap,
            "tag_prosperity_divisor": option.tag_prosperity_divisor,
            "tag_prosperity": [{"tag": tag, "name": TAG_NAMES.get(tag, tag), "coefficient": coefficient} for tag, coefficient in option.tag_prosperity],
            "shields": [{"problem_id": shield.problem_id, "name": PROBLEM_NAMES.get(shield.problem_id, shield.problem_id), "amount": shield.amount} for shield in option.shields],
            "vulnerabilities": [{"problem_id": item.problem_id, "name": PROBLEM_NAMES.get(item.problem_id, item.problem_id), "amount": item.amount} for item in option.vulnerabilities],
            "environment_prosperity_loss_reduction": option.environment_prosperity_loss_reduction,
            "candidate_bonus_when_reduce_retention_for_more_candidates": option.candidate_bonus_when_reduce_retention_for_more_candidates,
            "prosperity_if_environment_has_no_optimizations": option.prosperity_if_environment_has_no_optimizations,
            "size_effects": [{"size": item.size.name.lower(), "prosperity": item.prosperity, "next_candidate_bonus": item.next_candidate_bonus, "environment_prosperity_loss_reduction": item.environment_prosperity_loss_reduction, "shields": [{"problem_id": shield.problem_id, "name": PROBLEM_NAMES.get(shield.problem_id, shield.problem_id), "amount": shield.amount} for shield in item.shields], "vulnerabilities": [{"problem_id": vulnerability.problem_id, "name": PROBLEM_NAMES.get(vulnerability.problem_id, vulnerability.problem_id), "amount": vulnerability.amount} for vulnerability in item.vulnerabilities]} for item in option.size_effects],
        }

    @classmethod
    def _result_data(cls, engine: GameEngine, record: Any) -> dict[str, Any]:
        environment = engine.disasters[record.disaster_id]
        labels = cls._optimization_labels(environment)
        gain_breakdown = {"base": record.base_prosperity, "activation": record.activation_prosperity, "card": record.card_prosperity, "storage": record.storage_prosperity, "tag": record.tag_prosperity, "pool_before_problems": record.prosperity_pool_before_problems, "problem_penalty": record.problem_penalty, "pool_after_problems": record.prosperity_pool_after_problems, "multiplier": record.size.prosperity_multiplier, "delta": record.prosperity_delta}
        return {"round": record.round_number, "environment_name": event_name(environment.id, environment.name), "score_before": record.score_before, "prosperity_base": record.prosperity_base, "size_multiplier": record.size.prosperity_multiplier, "prosperity_delta": record.prosperity_delta, "score_after_prosperity": record.score_after_prosperity, "problems": [cls._problem_result(record, problem) for problem in PROBLEM_IDS], "problem_penalty": record.problem_penalty, "score_after_problems": record.score_after_problems, "gain_breakdown": gain_breakdown, "optimizations": [{"name": labels[index] if index < len(labels) else f"最適化{index + 1}", "requirements": cls._requirements_data_static(req), "met": record.optimization_results[index]} for index, req in enumerate(record.optimization_requirements)], "optimization_met": record.optimization_met, "optimization_half_loss": record.optimization_half_loss, "optimization_loss_before_reduction": record.optimization_loss_before_reduction, "environment_prosperity_loss_reduction": record.environment_prosperity_loss_reduction, "total_prosperity": record.total_prosperity}

    @classmethod
    def _problem_result(cls, record: Any, problem: str) -> dict[str, Any]:
        roll = record.problem_rolls[problem]; unblocked = record.unblocked_by_problem[problem]
        vulnerability = record.vulnerability_by_problem[problem]
        return {"id": problem, "name": PROBLEM_NAMES.get(problem, problem), "roll": roll, "effective_roll": roll + vulnerability, "vulnerability": vulnerability, "raw_rolls": list(record.problem_raw_rolls.get(problem, ())), "selected_roll": record.problem_selected_rolls.get(problem), "modifier": record.problem_modifiers.get(problem, 0), "roll_source": record.problem_roll_sources.get(problem, "dice"), "combine": record.problem_roll_combines.get(problem, "highest"), "defense": record.defense_by_problem[problem], "unblocked": unblocked, "penalty": record.penalty_by_problem[problem]}


SERVICE = WebGameService()
ERROR_TRANSLATIONS = {"operation requires phase": "今のフェーズではその操作はできません。", "column index is out of range": "進化列の指定が正しくありません。", "card is not in hand": "そのカードは手札にありません。", "a physical card may activate only once": "同じカードは1ラウンドに1回だけ起動できます。", "activation requirements": "起動条件を満たしていません。", "other cards in the column": "列の条件を満たしていません。", "retained cards exceed": "保持できる枚数を超えています。", "retained cards must": "公開されているカードだけ保持できます。", "retention candidate expansion may": "候補追加は各ラウンド1回だけ使えます。", "no retention slot": "候補追加に使える保持枠がありません。", "two trait cards": "候補を2枚追加できる山札がありません。"}


def japanese_error(exc: Exception) -> str:
    message = str(exc)
    for fragment, translated in ERROR_TRANSLATIONS.items():
        if fragment in message: return translated
    return message if any("\u3040" <= char <= "\u9fff" for char in message) else "操作を実行できませんでした。"


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "AntGame/0.12"
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/config": self._json(SERVICE.config())
        elif path == "/api/cards": self._json(SERVICE.card_catalog())
        elif path == "/api/environment-data": self._json(
            SERVICE.environment_export(),
            download_name="ant_game_environment_data_v0.12.json",
        )
        elif path.startswith("/api/game/"):
            try: self._json(SERVICE.get(path.rsplit("/", 1)[-1]))
            except InvalidDecision as exc: self._json({"error": japanese_error(exc)}, HTTPStatus.NOT_FOUND)
        elif path in ("/", "/index.html"): self._static("index.html", "text/html; charset=utf-8")
        elif path in ("/cards", "/cards.html"): self._static("cards.html", "text/html; charset=utf-8")
        elif path == "/app.js": self._static("app.js", "text/javascript; charset=utf-8")
        elif path == "/cards.js": self._static("cards.js", "text/javascript; charset=utf-8")
        elif path == "/style.css": self._static("style.css", "text/css; charset=utf-8")
        else: self.send_error(HTTPStatus.NOT_FOUND)
    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._body()
            if self.path == "/api/new": result = SERVICE.new_game(payload.get("seed", 0))
            elif self.path == "/api/action": result = SERVICE.act(str(payload.get("game_id", "")), str(payload.get("kind", "")), payload)
            else: self.send_error(HTTPStatus.NOT_FOUND); return
            self._json(result)
        except (InvalidDecision, ValueError, TypeError, json.JSONDecodeError) as exc: self._json({"error": japanese_error(exc)}, HTTPStatus.BAD_REQUEST)
    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000: raise ValueError("送信データが大きすぎます。")
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if not isinstance(payload, dict): raise ValueError("送信データの形式が正しくありません。")
        return payload
    def _json(
        self,
        data: Any,
        status: HTTPStatus = HTTPStatus.OK,
        download_name: str | None = None,
    ) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if download_name:
            self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def _static(self, filename: str, content_type: str) -> None:
        body = (STATIC_DIR / filename).read_bytes(); self.send_response(HTTPStatus.OK); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, format: str, *args: Any) -> None: return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8000); parser.add_argument("--no-browser", action="store_true"); args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), RequestHandler); url = f"http://{args.host}:{args.port}/"; print(f"アリ進化ゲームを起動しました: {url}")
    if not args.no_browser: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0


if __name__ == "__main__": raise SystemExit(main())
