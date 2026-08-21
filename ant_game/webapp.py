"""依存追加なしで遊べる、日本語ブラウザ版のHTTPサーバー。"""

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
from typing import Any
from urllib.parse import urlparse

from .content import EVENTS, TRAITS
from .engine import GameEngine, InvalidDecision
from .localization_ja import (
    CARD_TEXTS,
    EVENT_NAMES,
    HAZARD_NAMES,
    ROLE_NAMES,
    SIZE_NAMES,
    card_name,
    event_name,
    option_text,
    requirement_text,
    tags_text,
)
from .models import CardRole, GameState, RoundPhase, Size, TraitCard


STATIC_DIR = Path(__file__).with_name("web_static")
STAGE_NAMES = {1: "I", 2: "II", 3: "III", 4: "IV"}


@dataclass
class Session:
    engine: GameEngine
    state: GameState


class WebGameService:
    """HTTPと分離した、テスト可能な薄いゲーム操作層。"""

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}
        self._lock = threading.RLock()

    def config(self) -> dict[str, Any]:
        return {
            "environments": [
                {
                    "id": event.id,
                    "name": event_name(event.id, event.name),
                    "text": EVENT_NAMES[event.id][1],
                    "forecast": [event.stage_damage.get(stage, 0) for stage in GameEngine.STAGES],
                }
                for event in EVENTS
            ]
        }

    def new_game(self, seed: int = 0, environment_id: str | None = None) -> dict[str, Any]:
        with self._lock:
            engine = GameEngine(TRAITS, EVENTS, seed=int(seed))
            state = engine.new_game(environment_id=environment_id or None)
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
        names = {size.name.lower(): size for size in Size}
        try:
            return names[str(raw).lower()]
        except KeyError as exc:
            raise InvalidDecision("選べないサイズです。") from exc

    def project(self, engine: GameEngine, state: GameState) -> dict[str, Any]:
        context = state.current_round
        event = engine.current_event(state)
        candidate_ids = context.candidate_ids if context else ()
        eligible = {item.id for item in engine.eligible_extremes(state)} if not state.finished else set()
        public_extremes = engine.public_extremes(state) if not state.finished else ()
        last = state.history[-1] if state.history else None
        return {
            "phase": state.phase.value,
            "finished": state.finished,
            "extinct": state.phase is RoundPhase.EXTINCT,
            "round": context.round_number if context else state.round_number,
            "stage": STAGE_NAMES.get(context.stage if context else engine.current_stage(state), "IV"),
            "prosperity": state.prosperity,
            "damage": state.cumulative_damage,
            "damage_limit": engine.extinction_threshold,
            "size": state.size.name.lower(),
            "size_name": SIZE_NAMES[state.size.name],
            "legal_sizes": [self._size_data(engine, size) for size in engine.legal_sizes(state)] if state.phase is RoundPhase.SIZE else [],
            "retention_limit": engine.retention_limit(state) if context else 0,
            "hand_limit": engine.hand_limit,
            "round_prosperity": context.prosperity_base if context else 0,
            "round_shield": sum(item.amount for item in context.shields) if context else 0,
            "environment": {
                "id": event.id,
                "name": event_name(event.id, event.name),
                "text": EVENT_NAMES[event.id][1],
                "current_damage": event.stage_damage.get(context.stage, 0) if context else 0,
                "forecast": [
                    {"round": number, "stage": STAGE_NAMES[stage], "damage": event.stage_damage.get(stage, 0)}
                    for number, stage in enumerate(engine.STAGES, start=1)
                ],
            },
            "candidates": [self._card_data(engine.traits[card_id], card_id) for card_id in candidate_ids],
            "hand": [self._card_data(engine.traits[item.card_id], item.instance_id) for item in state.hand],
            "columns": [self._column_data(engine, state, index) for index in range(len(state.columns))],
            "extremes": [
                {**self._card_data(item.as_trait(), item.id), "eligible": item.id in eligible}
                for item in public_extremes
            ],
            "last_result": None if last is None else {
                "round": last.round_number,
                "stage": STAGE_NAMES[last.stage],
                "raw_damage": last.raw_damage,
                "shield": last.shield_amount,
                "damage": last.damage,
                "prosperity": last.prosperity_delta,
                "total_prosperity": last.total_prosperity,
                "total_damage": last.cumulative_damage,
                "pushed": [card_name(item, item) for item in last.pushed_out],
            },
        }

    @staticmethod
    def _size_data(engine: GameEngine, size: Size) -> dict[str, Any]:
        return {
            "id": size.name.lower(), "name": SIZE_NAMES[size.name],
            "multiplier": size.prosperity_multiplier, "retention": engine.retention_curve[size],
        }

    def _column_data(self, engine: GameEngine, state: GameState, index: int) -> dict[str, Any]:
        column = state.columns[index]
        tag_counts = engine.column_tags(state, index)
        cards = []
        for position, played in enumerate(column.cards):
            card = engine.traits[played.card_id]
            cards.append({
                **self._card_data(card, played.instance_id),
                "top": position == len(column.cards) - 1,
                "support": played.is_support,
                "activated": bool(state.current_round and played.activated_round == state.current_round.round_number),
            })
        top = column.top
        activations = []
        if top is not None and state.phase is RoundPhase.ACTIONS:
            card = engine.traits[top.card_id]
            tags_ok = all(tag_counts[tag] >= amount for tag, amount in card.activation_requirements.items())
            already = top.activated_round == state.current_round.round_number
            role_ok = card.role in (CardRole.ACTION, CardRole.STARTER)
            for option_index, option in enumerate(card.options):
                activations.append({
                    "option": option_index,
                    "text": option_text(option),
                    "enabled": role_ok and tags_ok and not already,
                    "reason": "" if role_ok and tags_ok and not already else (
                        "このラウンドは起動済み" if already else "起動条件を満たしていません"
                    ),
                })
        return {
            "index": index,
            "name": f"進化列 {index + 1}",
            "cards": cards,
            "tags": [{"name": tags_text([tag])[0], "count": count} for tag, count in sorted(tag_counts.items())],
            "capacity": engine.column_capacity,
            "next_pushed": card_name(column.cards[0].card_id, column.cards[0].card_id)
            if len(column.cards) >= engine.column_capacity else None,
            "activations": activations,
        }

    @staticmethod
    def _card_data(card: TraitCard, instance_id: str) -> dict[str, Any]:
        return {
            "id": instance_id,
            "card_id": card.id,
            "name": card_name(card.id, card.name),
            "text": CARD_TEXTS.get(card.id, "実在するアリの適応をもとにした進化形質。"),
            "tags": tags_text(card.root_tags),
            "requirements": requirement_text(card.activation_requirements),
            "role": ROLE_NAMES.get(card.design_role, card.design_role),
            "options": [option_text(option) for option in card.options],
        }


SERVICE = WebGameService()


ERROR_TRANSLATIONS = {
    "operation requires phase": "今のフェーズではその操作はできません。",
    "column index is out of range": "進化列の指定が正しくありません。",
    "card is not in hand": "そのカードは手札にありません。",
    "a physical card may activate only once": "同じカードは1ラウンドに1回だけ起動できます。",
    "activation requirements": "起動条件を満たしていません。",
    "retained cards exceed": "保持できる枚数を超えています。",
    "retained cards must": "公開されていないカードは保持できません。",
}


def japanese_error(exc: Exception) -> str:
    message = str(exc)
    for fragment, translated in ERROR_TRANSLATIONS.items():
        if fragment in message:
            return translated
    return message if any("ぁ" <= char <= "龥" for char in message) else "操作を実行できませんでした。"


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "AntGame/0.3"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/config":
            self._json(SERVICE.config())
        elif path.startswith("/api/game/"):
            try:
                self._json(SERVICE.get(path.rsplit("/", 1)[-1]))
            except InvalidDecision as exc:
                self._json({"error": japanese_error(exc)}, HTTPStatus.NOT_FOUND)
        elif path in ("/", "/index.html"):
            self._static("index.html", "text/html; charset=utf-8")
        elif path == "/app.js":
            self._static("app.js", "text/javascript; charset=utf-8")
        elif path == "/style.css":
            self._static("style.css", "text/css; charset=utf-8")
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._body()
            if self.path == "/api/new":
                result = SERVICE.new_game(payload.get("seed", 0), payload.get("environment_id"))
            elif self.path == "/api/action":
                result = SERVICE.act(str(payload.get("game_id", "")), str(payload.get("kind", "")), payload)
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._json(result)
        except (InvalidDecision, ValueError, TypeError, json.JSONDecodeError) as exc:
            self._json({"error": japanese_error(exc)}, HTTPStatus.BAD_REQUEST)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("送信データが大きすぎます。")
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if not isinstance(payload, dict):
            raise ValueError("送信データの形式が正しくありません。")
        return payload

    def _json(self, data: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, filename: str, content_type: str) -> None:
        body = (STATIC_DIR / filename).read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), RequestHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"アリ進化ゲームを起動しました: {url}")
    print("終了するには Ctrl+C を押してください。")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
