import json
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ant_game.engine import PROBLEM_IDS, InvalidDecision
from ant_game.models import PlayedCard, ShieldSpec
from ant_game.webapp import RequestHandler, WebGameService


def test_service_exposes_five_tags_and_environment_forecast_without_problem_classes():
    service = WebGameService()
    first = service.new_game(seed=3)["state"]
    second = service.new_game(seed=3)["state"]
    assert len(service.config()["tags"]) == 5
    assert {tag["id"] for tag in service.config()["tags"]} == {
        "Morphology", "Chemistry", "Sociality", "Nesting", "Resource Ecology"
    }
    assert len(first["forecast"]) == 5
    assert [item["id"] for item in first["forecast"]] == [item["id"] for item in second["forecast"]]
    assert all("hazard_tags" not in item for item in first["forecast"])
    assert "environment" in first and "hazard_tags" not in first["environment"]
    assert all("optimizations" in item for item in first["forecast"])
    assert all("optimization" in item for item in first["forecast"])  # compatibility alias
    assert [item["id"] for item in first["problems"]] == list(PROBLEM_IDS)


def test_sociality_has_japanese_name_and_dedicated_symbol():
    sociality = next(tag for tag in WebGameService().config()["tags"] if tag["id"] == "Sociality")
    assert sociality["name"] == "\u793e\u4f1a\u6027"
    assert sociality["symbol"] == "linked-ants"
    assert sociality["color"]


def test_problem_rolls_and_shields_are_projected_independently():
    service = WebGameService()
    result = service.new_game(seed=4)
    game_id = result["game_id"]
    state = service.act(game_id, "size", {"size": "small"})["state"]
    assert all(problem["roll"] in range(1, 5) for problem in state["problems"])
    state = service.act(game_id, "retain", {"card_ids": []})["state"]
    assert [problem["id"] for problem in state["problems"]] == ["raid", "sanitation"]
    assert all(set(problem) >= {"id", "roll", "raw_rolls", "selected_roll", "modifier", "shield", "unblocked", "penalty"} for problem in state["problems"])
    state = service.act(game_id, "resolve", {})["state"]
    result = state["last_result"]
    assert [problem["id"] for problem in result["problems"]] == list(PROBLEM_IDS)
    assert result["problem_penalty"] == sum(problem["penalty"] for problem in result["problems"])
    for problem in result["problems"]:
        assert problem["unblocked"] == max(0, problem["roll"] - problem["defense"])
        assert problem["penalty"] == (0 if problem["unblocked"] == 0 else 2 ** problem["unblocked"])


def test_live_projection_includes_activated_shields_and_round_prosperity_delta():
    service = WebGameService()
    opened = service.new_game(seed=4)
    game_id = opened["game_id"]
    session = service.sessions[game_id]
    session.state.current_round.shields.append(ShieldSpec("raid", 2))
    state = service.get(game_id)["state"]
    raid = next(problem for problem in state["problems"] if problem["id"] == "raid")
    assert raid["shield"] == 2
    assert raid["unblocked"] == max(0, raid["roll"] - 2)
    assert state["round_prosperity_base"] == 5
    assert state["round_prosperity_delta"] == 5
    assert state["round_prosperity_multiplier"] == 1


def test_retention_projection_keeps_existing_hand_visible():
    service = WebGameService()
    opened = service.new_game(seed=12)
    game_id = opened["game_id"]
    state = service.act(game_id, "size", {"size": "small"})["state"]
    kept_id = state["candidates"][0]["id"]
    service.act(game_id, "retain", {"card_ids": [kept_id]})
    service.act(game_id, "resolve", {})
    state = service.act(game_id, "size", {"size": "small"})["state"]
    assert state["phase"] == "retain"
    assert [card["id"] for card in state["hand"]] == [kept_id]


def test_undo_restores_the_previous_action_and_failed_actions_add_nothing():
    service = WebGameService()
    opened = service.new_game(seed=17)
    game_id = opened["game_id"]
    original = opened["state"]
    changed = service.act(game_id, "size", {"size": "small"})["state"]
    assert changed["phase"] == "retain"
    assert changed["can_undo"] is True

    restored = service.act(game_id, "undo", {})["state"]
    assert restored["phase"] == "size"
    assert restored["problems"] == original["problems"]
    assert restored["can_undo"] is False
    with pytest.raises(InvalidDecision):
        service.act(game_id, "unknown", {})
    assert service.get(game_id)["state"]["can_undo"] is False


def test_placement_color_prediction_accounts_for_oldest_card_pushout():
    service = WebGameService()
    opened = service.new_game(seed=21)
    session = service.sessions[opened["game_id"]]
    target = session.engine.traits["oecophylla_living_chain"]
    assert target.activation_requirements == {"Sociality": 2}
    session.state.columns[0].cards = [
        PlayedCard("old-social", "collective_foraging"),
        PlayedCard("non-social-1", "trail_pheromone"),
        PlayedCard("non-social-2", "trail_pheromone"),
        PlayedCard("non-social-3", "trail_pheromone"),
        PlayedCard("non-social-4", "trail_pheromone"),
    ]
    option = service._placement_option_data(session.engine, session.state, 0, target)
    assert option["status"] == "other"
    assert option["requirements"][0]["missing"] == 2


def test_browser_service_resolves_one_round_and_exposes_audit_trail():
    service = WebGameService()
    result = service.new_game(seed=5)
    game_id = result["game_id"]
    service.act(game_id, "size", {"size": "small"})
    service.act(game_id, "retain", {"card_ids": []})
    result = service.act(game_id, "resolve", {})
    resolved = result["state"]["last_result"]
    assert resolved["score_after_problems"] == max(0, resolved["score_after_prosperity"] - resolved["problem_penalty"])
    assert all(problem["raw_rolls"] for problem in resolved["problems"])
    assert result["state"]["round"] == 2


def test_card_effects_and_conditions_are_structured_data():
    state = WebGameService().new_game(seed=8)["state"]
    card = state["forecast"][0]["optimizations"][0]
    assert card["requirements"]
    assert all({"id", "required", "name", "color", "symbol"} <= set(item) for item in card["requirements"])
    service = WebGameService()
    game_id = service.new_game(seed=8)["game_id"]
    state = service.act(game_id, "size", {"size": "small"})["state"]
    assert state["candidates"]
    for candidate in state["candidates"]:
        assert isinstance(candidate["options"], list)
        for option in candidate["options"]:
            assert {"text", "prosperity", "draw_cards", "shields", "retention_bonus", "store_hand_card", "storage_income_per_card", "tag_prosperity"} <= set(option)


def test_real_http_server_serves_v05_page_and_rejects_non_object_json():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/", timeout=2) as response:
            page = response.read().decode("utf-8")
            assert 'lang="ja"' in page
            assert "symbol-linked-ants" in page
            assert 'id="environment"' not in page
        with urlopen(base + "/style.css", timeout=2) as response:
            css = response.read().decode("utf-8")
            assert "min-height:44px" in css
            assert "max-width:420px" in css
        with urlopen(base + "/api/config", timeout=2) as response:
            config = json.load(response)
            assert len(config["tags"]) == 5
            assert len(config["environments"]) >= 5
            assert len(config["problems"]) == 2
        request = Request(base + "/api/new", data=b"[]", headers={"Content-Type": "application/json"}, method="POST")
        try:
            urlopen(request, timeout=2)
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("non-object JSON should be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
