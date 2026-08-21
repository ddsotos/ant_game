import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ant_game.content import EVENTS, EXTREMES, TRAITS
from ant_game.models import RoundPhase
from ant_game.webapp import RequestHandler, WebGameService
from ant_game.localization_ja import CARD_NAMES, CARD_TEXTS, EVENT_NAMES


def test_every_playable_card_and_event_has_japanese_display_text():
    for card in (*TRAITS, *EXTREMES):
        assert card.id in CARD_NAMES
        assert card.id in CARD_TEXTS
        assert any("ぁ" <= char <= "龥" for char in CARD_NAMES[card.id])
    assert {event.id for event in EVENTS} <= EVENT_NAMES.keys()


def test_browser_service_starts_with_japanese_data_and_usable_starters():
    service = WebGameService()
    result = service.new_game(seed=3, environment_id="flood_front")
    game_id = result["game_id"]
    state = result["state"]
    assert state["phase"] == "size"
    assert state["environment"]["name"] == "洪水前線"
    assert all(column["activations"] == [] for column in state["columns"])

    service.act(game_id, "size", {"size": "small"})
    state = service.act(game_id, "retain", {"card_ids": []})["state"]
    assert all(column["activations"][0]["enabled"] for column in state["columns"])
    assert state["columns"][0]["activations"][0]["text"] == "カードを今すぐ1枚引く"


def test_browser_service_can_step_through_all_five_rounds():
    service = WebGameService()
    result = service.new_game(seed=5, environment_id="flood_front")
    game_id = result["game_id"]
    # This test isolates the five-round browser phase flow from balance/extinction.
    service.sessions[game_id].engine.extinction_threshold = 100
    for _ in range(5):
        service.act(game_id, "size", {"size": "small"})
        service.act(game_id, "retain", {"card_ids": []})
        service.act(game_id, "activate", {"column": 1, "option": 0})
        result = service.act(game_id, "resolve", {})
    assert result["state"]["finished"] is True
    assert result["state"]["phase"] == RoundPhase.COMPLETE.value
    assert result["state"]["round"] == 5


def test_real_http_server_serves_japanese_page_and_rejects_non_object_json():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/", timeout=2) as response:
            assert "アリ進化ゲーム" in response.read().decode("utf-8")
        with urlopen(base + "/api/config", timeout=2) as response:
            assert json.load(response)["environments"][0]["name"] == "洪水前線"
        request = Request(
            base + "/api/new",
            data=b"[]",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=2)
        assert error.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
