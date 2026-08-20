from ant_game.cli import HumanPolicy
from ant_game.content import EVENTS, TRAITS
from ant_game.engine import GameEngine
from ant_game.models import EvolutionChoice, Size


def scripted_policy(*answers: str) -> HumanPolicy:
    iterator = iter(answers)
    return HumanPolicy(input_fn=lambda _prompt: next(iterator), output_fn=lambda _line: None)


def test_human_policy_accepts_a_legal_size_name() -> None:
    engine = GameEngine(TRAITS, EVENTS, seed=1)
    state = engine.new_game()
    assert scripted_policy("large").choose_size(state, engine) is Size.LARGE


def test_human_policy_can_spend_budget_on_two_cards() -> None:
    engine = GameEngine(TRAITS, EVENTS, seed=1)
    state = engine.new_game()
    choice = scripted_policy("paraponera_poneratoxin,formica_rufa_sunshield").choose_evolution(
        state,
        ("paraponera_poneratoxin", "formica_rufa_sunshield"),
        2,
        engine,
    )
    assert choice == EvolutionChoice(
        ("paraponera_poneratoxin", "formica_rufa_sunshield"), ()
    )
