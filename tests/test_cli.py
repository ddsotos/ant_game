from ant_game.cli import HumanPolicy, main
from ant_game.content import EVENTS, TRAITS
from ant_game.engine import GameEngine
from ant_game.models import RoundPhase, Size


def scripted_policy(*answers: str):
    iterator = iter(answers)
    output: list[str] = []
    return HumanPolicy(input_fn=lambda _prompt: next(iterator), output_fn=output.append), output


def test_human_policy_accepts_a_legal_size_name() -> None:
    engine = GameEngine(TRAITS, EVENTS, seed=1)
    state = engine.new_game()
    engine.start_round(state)
    policy, _ = scripted_policy("medium")
    assert policy.choose_size(state, engine) is Size.MEDIUM


def test_human_policy_keeps_a_visible_candidate() -> None:
    engine = GameEngine(TRAITS, EVENTS, seed=1)
    state = engine.new_game()
    engine.start_round(state)
    candidates = engine.choose_size(state, Size.SMALL)
    policy, _ = scripted_policy(candidates[0])
    assert policy.choose_retained(state, candidates, engine) == (candidates[0],)


def test_human_policy_done_leaves_action_phase_cleanly() -> None:
    engine = GameEngine(TRAITS, EVENTS, seed=1)
    state = engine.new_game()
    engine.start_round(state)
    engine.choose_size(state, Size.SMALL)
    engine.retain_cards(state, ())
    policy, output = scripted_policy("done")
    policy.take_actions(state, engine)
    assert state.phase is RoundPhase.ACTIONS
    assert any("C1" in line for line in output)


def test_environment_list_is_available_without_starting_a_game(capsys) -> None:
    assert main(["--list-environments"]) == 0
    assert "flood_front" in capsys.readouterr().out
