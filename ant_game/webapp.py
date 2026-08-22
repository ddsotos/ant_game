"""Minimal Japanese browser UI for the five-round ant adaptation game."""

from __future__ import annotations

import argparse
import json
import threading
import uuid
import webbrowser
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
    card_name,
    event_name,
    optimization_name,
)
from .models import ActionOption, CardRole, EnvironmentCard, GameState, RoundPhase, Size, TraitCard

STATIC_DIR = Path(__file__).with_name("web_static")

TAG_INFO: dict[str, tuple[str, str, str]] = {
    "Morphology": ("形態", "#0072B2", "mandibles"),
    "Chemistry": ("化学", "#E69F00", "droplet"),
    "Sociality": ("社会性", "#009E73", "sociality"),
    "Nesting": ("巣作り", "#CC79A7", "nest"),
    "Movement": ("移動", "#56B4E9", "route"),
    "Resource Ecology": ("資源生態", "#F0E442", "leaf-seed"),
}
PROBLEM_NAMES = {"raid": "襲撃", "fungal": "菌害", "nest_damage": "巣の損傷"}
SIZE_LABELS = {"SMALL": "小", "MEDIUM": "中", "LARGE": "大", "GIANT": "巨大"}


@dataclass
class Session:
    engine: GameEngine
    state: GameState


class WebGameService:
    """Thread-safe, JSON-shaped adapter around the rules engine."""

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}
        self._lock = threading.RLock()

    def config(self) -> dict[str, Any]:
        return {
            "tags": [self._tag_data(tag) for tag in TAG_INFO],
            "environments": [self._environment_data(environment) for environment in DISASTERS],
            "problems": [self._problem_data(problem) for problem in PROBLEM_IDS],
        }

    def new_game(self, seed: int = 0) -> dict[str, Any]:
        with self._lock:
            engine = GameEngine(TRAITS, DISASTERS, seed=int(seed))
            state = engine.new_game()
            engine.start_round(state)
            game_id = uuid.uuid4().hex
            self.sessions[game_id] = Session(engine, state)
            return {"game_id": game_id, "state": self.project(engine, state)}

    def act(self, game_id: str, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            session = self.sessions.get(game_id)
            if session is None:
                raise InvalidDecision("ゲームが見つかりません。新しいゲームを開始してください。")
            engine, state = session.engine, session.state
            if kind == "size":
                engine.choose_size(state, self._parse_size(payload.get("size")))
            elif kind == "retain":
                engine.retain_cards(state, tuple(payload.get("card_ids", ())))
            elif kind == "play":
                engine.play_card(state, str(payload.get("card_id", "")), int(payload.get("column", -1)))
            elif kind == "support":
                engine.insert_support(state, str(payload.get("card_id", "")), int(payload.get("column", -1)))
            elif kind == "activate":
                engine.activate(state, int(payload.get("column", -1)), int(payload.get("option", 0)))
            elif kind == "resolve":
                engine.resolve_environment(state)
                if not state.finished:
                    engine.start_round(state)
            else:
                raise InvalidDecision("不明な操作です。")
            return {"game_id": game_id, "state": self.project(engine, state)}

    def get(self, game_id: str) -> dict[str, Any]:
        with self._lock:
            session = self.sessions.get(game_id)
            if session is None:
                raise InvalidDecision("ゲームが見つかりません。")
            return {"game_id": game_id, "state": self.project(session.engine, session.state)}

    @staticmethod
    def _parse_size(raw: Any) -> Size:
        try:
            return {size.name.lower(): size for size in Size}[str(raw).lower()]
        except KeyError as exc:
            raise InvalidDecision("選べないサイズです。") from exc

    def project(self, engine: GameEngine, state: GameState) -> dict[str, Any]:
        context = state.current_round
        environment = engine.current_disaster(state)
        last = state.history[-1] if state.history else None
        board_tags = engine.board_tags(state)
        shields = self._shield_totals(context.shields if context else ())
        optimization_progress = self._requirements_data(environment.optimization.required_root_tags, board_tags)
        return {
            "phase": state.phase.value,
            "finished": state.finished,
            "round": context.round_number if context else state.round_number,
            "prosperity": state.prosperity,
            "size": state.size.name.lower(),
            "size_name": SIZE_LABELS.get(state.size.name, state.size.name),
            "legal_sizes": [self._size_data(engine, size) for size in engine.legal_sizes(state)] if state.phase is RoundPhase.SIZE else [],
            "retention_limit": min(engine.retention_limit(state), engine.hand_limit - len(state.hand)) if context else 0,
            "hand_limit": engine.hand_limit,
            "round_prosperity_base": context.prosperity_base if context else 0,
            "forecast": [self._forecast_data(engine, state, index) for index in range(len(state.disaster_ids))],
            "environment": {
                **self._environment_data(environment),
                "optimization": {
                    "name": optimization_name(environment.id, environment.optimization.name),
                    "text": environment.optimization.text,
                    "requirements": optimization_progress,
                    "met": bool(optimization_progress) and all(item["missing"] == 0 for item in optimization_progress),
                },
            },
            "problems": [self._problem_data(problem, context.problem_rolls.get(problem), shields.get(problem, 0)) for problem in PROBLEM_IDS] if context else [],
            "candidates": [self._card_data(engine.traits[item.card_id], item.instance_id) for item in (context.candidate_instances if context else ())],
            "hand": [self._card_data(engine.traits[item.card_id], item.instance_id) for item in state.hand],
            "columns": [self._column_data(engine, state, index) for index in range(len(state.columns))],
            "last_result": None if last is None else self._result_data(engine, last),
        }

    def _forecast_data(self, engine: GameEngine, state: GameState, index: int) -> dict[str, Any]:
        environment = engine.disasters[state.disaster_ids[index]]
        return {**self._environment_data(environment), "round": index + 1, "current": not state.finished and index == state.round_number, "completed": index < state.round_number}

    @staticmethod
    def _environment_data(environment: EnvironmentCard) -> dict[str, Any]:
        localized = EVENT_NAMES.get(environment.id, (environment.name, environment.text))
        return {
            "id": environment.id,
            "name": localized[0] or environment.name,
            "text": localized[1] or environment.text,
            "optimization": {"name": optimization_name(environment.id, environment.optimization.name), "requirements": WebGameService._requirements_data_static(environment.optimization.required_root_tags)},
        }

    @staticmethod
    def _problem_data(problem: str, roll: int | None = None, shield: int = 0) -> dict[str, Any]:
        unblocked = None if roll is None else max(0, roll - shield)
        return {"id": problem, "name": PROBLEM_NAMES.get(problem, problem), "roll": roll, "shield": shield, "unblocked": unblocked, "penalty": None if unblocked is None else (0 if unblocked == 0 else 2 ** unblocked)}

    @staticmethod
    def _shield_totals(shields: Any) -> dict[str, int]:
        totals = {problem: 0 for problem in PROBLEM_IDS}
        for shield in shields:
            problem = getattr(shield, "problem_id", "")
            if problem in totals:
                totals[problem] += shield.amount
        return totals

    @staticmethod
    def _tag_data(tag: str, count: int | None = None) -> dict[str, Any]:
        name, color, symbol = TAG_INFO.get(tag, (tag, "#777777", "dot"))
        data: dict[str, Any] = {"id": tag, "name": name, "color": color, "symbol": symbol}
        if count is not None:
            data["count"] = count
        return data

    @classmethod
    def _requirements_data_static(cls, requirements: Mapping[str, int], actual: Mapping[str, int] | None = None) -> list[dict[str, Any]]:
        return [{**cls._tag_data(tag), "required": required, "actual": actual.get(tag, 0) if actual is not None else None, "missing": max(0, required - actual.get(tag, 0)) if actual is not None else None} for tag, required in sorted(requirements.items())]

    def _requirements_data(self, requirements: Mapping[str, int], actual: Mapping[str, int] | None = None) -> list[dict[str, Any]]:
        return self._requirements_data_static(requirements, actual)

    @staticmethod
    def _size_data(engine: GameEngine, size: Size) -> dict[str, Any]:
        return {"id": size.name.lower(), "name": SIZE_LABELS.get(size.name, size.name), "multiplier": size.prosperity_multiplier, "retention": engine.retention_curve[size]}

    def _column_data(self, engine: GameEngine, state: GameState, index: int) -> dict[str, Any]:
        column = state.columns[index]
        all_tags = engine.column_tags(state, index)
        activation_tags = engine.activation_tags(state, index)
        cards = []
        for position, played in enumerate(column.cards):
            card = engine.traits[played.card_id]
            cards.append({**self._card_data(card, played.instance_id), "top": position == len(column.cards) - 1, "support": played.is_support, "activated": bool(state.current_round and played.activated_round == state.current_round.round_number)})
        activations: list[dict[str, Any]] = []
        if column.top is not None and state.phase is RoundPhase.ACTIONS:
            top = column.top
            card = engine.traits[top.card_id]
            requirements = self._requirements_data(card.activation_requirements, activation_tags)
            already = top.activated_round == state.current_round.round_number
            role_ok = card.role in (CardRole.ACTION, CardRole.STARTER)
            requirements_ok = all(item["missing"] == 0 for item in requirements)
            for option_index, option in enumerate(card.options):
                enabled = role_ok and requirements_ok and not already
                activations.append({"option": option_index, "effect": self._option_data(option), "enabled": enabled, "reason": "" if enabled else ("このラウンドは起動済みです。" if already else "起動条件を満たしていません。"), "requirements": requirements})
        return {"index": index, "name": f"進化列 {index + 1}", "cards": cards, "tags": [self._tag_data(tag, count) for tag, count in sorted(all_tags.items()) if tag in TAG_INFO], "activation_tags": [self._tag_data(tag, count) for tag, count in sorted(activation_tags.items()) if tag in TAG_INFO], "capacity": engine.column_capacity, "next_pushed": card_name(column.cards[0].card_id, column.cards[0].card_id) if len(column.cards) >= engine.column_capacity else None, "activations": activations}

    def _card_data(self, card: TraitCard, instance_id: str) -> dict[str, Any]:
        return {"id": instance_id, "card_id": card.id, "name": card_name(card.id, card.name), "text": CARD_TEXTS.get(card.id, card.text), "tags": [self._tag_data(tag) for tag in sorted(card.root_tags) if tag in TAG_INFO], "requirements": self._requirements_data(card.activation_requirements), "role": ROLE_NAMES.get(card.design_role, card.design_role), "options": [self._option_data(option) for option in card.options]}

    @staticmethod
    def _option_data(option: ActionOption) -> dict[str, Any]:
        return {"text": "", "prosperity": option.prosperity, "draw_cards": option.draw_cards, "shields": [{"problem_id": shield.problem_id, "name": PROBLEM_NAMES.get(shield.problem_id, shield.problem_id), "amount": shield.amount} for shield in option.shields]}

    @staticmethod
    def _result_data(engine: GameEngine, record: Any) -> dict[str, Any]:
        environment = engine.disasters[record.disaster_id]
        return {"round": record.round_number, "environment_name": event_name(environment.id, environment.name), "score_before": record.score_before, "prosperity_base": record.prosperity_base, "size_multiplier": record.size.prosperity_multiplier, "prosperity_delta": record.prosperity_delta, "score_after_prosperity": record.score_after_prosperity, "problems": [WebGameService._problem_result(record, problem) for problem in PROBLEM_IDS], "problem_penalty": record.problem_penalty, "score_after_problems": record.score_after_problems, "optimization_name": optimization_name(environment.id, environment.optimization.name), "optimization_met": record.optimization_met, "optimization_half_loss": record.optimization_half_loss, "total_prosperity": record.total_prosperity}

    @staticmethod
    def _problem_result(record: Any, problem: str) -> dict[str, Any]:
        roll = record.problem_rolls[problem]
        unblocked = record.unblocked_by_problem[problem]
        return {"id": problem, "name": PROBLEM_NAMES.get(problem, problem), "roll": roll, "defense": record.defense_by_problem[problem], "unblocked": unblocked, "penalty": record.penalty_by_problem[problem]}


SERVICE = WebGameService()
ERROR_TRANSLATIONS = {"operation requires phase": "今のフェーズではその操作はできません。", "column index is out of range": "進化列の指定が正しくありません。", "card is not in hand": "そのカードは手札にありません。", "a physical card may activate only once": "同じカードは1ラウンドに1回だけ起動できます。", "activation requirements": "起動条件を満たしていません。", "other cards in the column": "列の条件を満たしていません。", "retained cards exceed": "保持できる枚数を超えています。", "retained cards must": "公開されているカードだけ保持できます。"}


def japanese_error(exc: Exception) -> str:
    message = str(exc)
    for fragment, translated in ERROR_TRANSLATIONS.items():
        if fragment in message:
            return translated
    return message if any("\u3040" <= char <= "\u9fff" for char in message) else "操作を実行できませんでした。"


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "AntGame/0.5"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/config": self._json(SERVICE.config())
        elif path.startswith("/api/game/"):
            try: self._json(SERVICE.get(path.rsplit("/", 1)[-1]))
            except InvalidDecision as exc: self._json({"error": japanese_error(exc)}, HTTPStatus.NOT_FOUND)
        elif path in ("/", "/index.html"): self._static("index.html", "text/html; charset=utf-8")
        elif path == "/app.js": self._static("app.js", "text/javascript; charset=utf-8")
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

    def _json(self, data: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def _static(self, filename: str, content_type: str) -> None:
        body = (STATIC_DIR / filename).read_bytes()
        self.send_response(HTTPStatus.OK); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

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
