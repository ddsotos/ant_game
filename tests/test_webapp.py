import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ant_game.content import DISASTERS, TRAITS
from ant_game.localization_ja import CARD_NAMES, CARD_TEXTS, EVENT_NAMES, TAG_COLORS, TAG_SYMBOLS
from ant_game.models import RoundPhase
from ant_game.webapp import RequestHandler, WebGameService


def test_every_playable_card_and_disaster_has_japanese_display_text():
    for card in TRAITS:
        assert card.id in CARD_NAMES
        assert card.id in CARD_TEXTS
        assert any("ぁ" <= char <= "龥" for char in CARD_NAMES[card.id])
    assert {disaster.id for disaster in DISASTERS} <= EVENT_NAMES.keys()


def test_browser_service_starts_with_public_forecast_and_seed_only():
    service = WebGameService()
    first = service.new_game(seed=3)["state"]
    second = service.new_game(seed=3)["state"]
    assert first["phase"] == "size"
    assert len(first["forecast"]) == 5
    assert len({item["id"] for item in first["forecast"]}) == 5
    assert [item["id"] for item in first["forecast"]] == [item["id"] for item in second["forecast"]]
    assert first["disaster"]["hazards"] == second["disaster"]["hazards"]
    assert all(item["optimization"]["requirements"] for item in first["forecast"])
    assert "environments" not in service.config()


def test_api_uses_structured_colored_tags_and_excludes_top_from_activation_progress():
    service = WebGameService()
    result = service.new_game(seed=4)
    game_id = result["game_id"]
    state = result["state"]
    own_tag = state["columns"][0]["tags"][0]
    assert {"id", "name", "color", "symbol", "count"} <= own_tag.keys()
    assert own_tag["color"] == TAG_COLORS[own_tag["id"]]
    assert own_tag["symbol"] == TAG_SYMBOLS[own_tag["id"]]
    assert state["columns"][0]["activation_tags"] == []

    service.act(game_id, "size", {"size": "small"})
    state = service.act(game_id, "retain", {"card_ids": []})["state"]
    assert all(column["activations"][0]["enabled"] for column in state["columns"])


def test_browser_retention_limit_respects_remaining_hand_space():
    service = WebGameService()
    result = service.new_game(seed=8)
    game_id = result["game_id"]
    session = service.sessions[game_id]
    session.engine.choose_size(session.state, session.state.size)
    candidates = session.state.current_round.candidate_instances
    session.state.hand.extend([*candidates, candidates[0]])
    state = service.project(session.engine, session.state)
    assert state["retention_limit"] == 1


def test_browser_service_reports_full_resolution_and_finishes_five_rounds():
    service = WebGameService()
    result = service.new_game(seed=5)
    game_id = result["game_id"]
    for _ in range(5):
        service.act(game_id, "size", {"size": "small"})
        service.act(game_id, "retain", {"card_ids": []})
        result = service.act(game_id, "resolve", {})
        resolved = result["state"]["last_result"]
        assert resolved["score_after_prosperity"] == resolved["score_before"] + resolved["prosperity_delta"]
        assert resolved["score_after_hazard"] == max(
            0, resolved["score_after_prosperity"] - resolved["hazard_penalty"]
        )
        expected = resolved["score_after_hazard"] if resolved["optimization_met"] else resolved["score_after_hazard"] // 2
        assert resolved["total_prosperity"] == expected
        for hazard in resolved["hazards"]:
            assert hazard["unblocked"] == max(0, hazard["roll"] - hazard["defense"])
            assert hazard["penalty"] == (0 if hazard["unblocked"] == 0 else 2 ** hazard["unblocked"])
    assert result["state"]["finished"] is True
    assert result["state"]["phase"] == RoundPhase.COMPLETE.value
    assert result["state"]["round"] == 5


def test_real_http_server_serves_japanese_responsive_page_and_rejects_non_object_json():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/", timeout=2) as response:
            page = response.read().decode("utf-8")
            assert "アリ進化ゲーム" in page
            assert 'id="environment"' not in page
            assert "symbol-mandibles" in page
        with urlopen(base + "/style.css", timeout=2) as response:
            css = response.read().decode("utf-8")
            assert "min-height:44px" in css
            assert "max-width:420px" in css
        with urlopen(base + "/api/config", timeout=2) as response:
            config = json.load(response)
            assert len(config["tags"]) == 7
            assert len(config["disasters"]) >= 5
        request = Request(
            base + "/api/new", data=b"[]",
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=2)
        assert error.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
