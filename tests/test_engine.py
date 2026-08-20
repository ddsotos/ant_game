import unittest

from ant_game.engine import GameEngine, InvalidDecision
from ant_game.models import EventCard, EventKind, RoundDecision, Size, TraitCard, TraitState


def traits():
    return [
        TraitCard("armor", "Armor", evolution_load=2, mitigation_tags={"heat": 2}),
        TraitCard(
            "latent", "Latent", evolution_load=1, latent=True,
            trigger_tags=frozenset({"heat"}), trigger_min_stage=2,
            mitigation_tags={"heat": 3}, consume_on_trigger=True,
        ),
        *[TraitCard(f"t{i}", f"Trait {i}") for i in range(10)],
    ]


def events():
    return [
        EventCard("heat", "Heat", tags=frozenset({"heat"})),
        EventCard("shock", "Shock", kind=EventKind.SHOCK, shock_damage=3),
    ]


class HoldPolicy:
    def choose_size(self, state, engine):
        return state.size


class EngineTests(unittest.TestCase):
    def test_upward_size_change_pays_growth_cost_but_shrinking_is_free(self):
        engine = GameEngine(traits(), [events()[0]], seed=4, rounds=2)
        state = engine.new_game()
        grow = engine.resolve_round(state, RoundDecision(Size.LARGE))
        shrink = engine.resolve_round(state, RoundDecision(Size.MEDIUM))
        self.assertEqual((grow.growth_cost, grow.raw_prosperity_delta), (2, 3))
        self.assertEqual(shrink.growth_cost, 0)

    def test_wave_advances_and_is_removed_after_iv(self):
        engine = GameEngine(traits(), [events()[0]], seed=4, rounds=4)
        state = engine.new_game()
        stages = []
        for _ in range(4):
            stages.append(engine.resolve_round(state, RoundDecision(Size.MEDIUM)).event_stage)
        self.assertEqual(stages, [1, 2, 3, 4])
        self.assertEqual(state.removed_events, ["heat"])
        self.assertEqual(state.event_discard, [])

    def test_wave_size_damage_starts_at_configured_stage(self):
        event = EventCard(
            "scaled", "Scaled", tags=frozenset({"heat"}),
            size_damage={Size.HUGE: 2}, size_damage_min_stage=2,
        )
        engine = GameEngine(traits(), [event], seed=4, rounds=2)
        state = engine.new_game()
        state.size = Size.HUGE
        first = engine.resolve_round(state, RoundDecision(Size.HUGE))
        second = engine.resolve_round(state, RoundDecision(Size.HUGE))
        self.assertEqual((first.event_stage, first.raw_damage), (1, 0))
        self.assertEqual((second.event_stage, second.raw_damage), (2, 6))

    def test_peak_size_damage_only_applies_at_stage_three(self):
        event = EventCard(
            "peak", "Peak", size_damage={Size.LARGE: 1},
            peak_size_damage={Size.LARGE: 2}, size_damage_min_stage=2,
        )
        engine = GameEngine(traits(), [event], seed=4, rounds=3)
        state = engine.new_game()
        state.size = Size.LARGE
        records = [engine.resolve_round(state, RoundDecision(Size.LARGE)) for _ in range(3)]
        self.assertEqual([record.raw_damage for record in records], [0, 5, 13])

    def test_shock_resolves_once_and_is_removed(self):
        engine = GameEngine(traits(), events(), seed=1)
        state = engine.new_game()
        while "shock" not in state.removed_events:
            engine.resolve_round(state, RoundDecision(state.size))
        self.assertEqual(sum(r.event_id == "shock" for r in state.history), 1)

    def test_seed_reproduces_complete_history(self):
        event_set = [EventCard(f"e{i}", f"Event {i}") for i in range(3)]
        first = GameEngine(traits(), event_set, seed=99, rounds=6).run(HoldPolicy())
        second = GameEngine(traits(), event_set, seed=99, rounds=6).run(HoldPolicy())
        self.assertEqual(first.history, second.history)

    def test_policy_can_react_after_event_reveal_and_trait_draw(self):
        class ReactivePolicy(HoldPolicy):
            def choose_latents(self, state, event, stage, engine):
                return ("latent",) if stage == 2 else ()

            def choose_trait(self, state, candidates, engine):
                return 0

        engine = GameEngine(traits(), [events()[0]], seed=5, rounds=1)
        state = engine.new_game()
        state.event_stages["heat"] = 1
        state.traits = [TraitState("latent", active=False)]
        record = engine.run(ReactivePolicy(), state).history[0]
        self.assertEqual(record.latent_activated, ("latent",))
        self.assertIsNotNone(record.acquired_trait_id)

    def test_evolution_draw_can_reach_zero(self):
        engine = GameEngine(traits(), events(), seed=2)
        state = engine.new_game()
        state.traits = [TraitState("armor")]
        state.size = Size.HUGE
        self.assertEqual(engine.draw_count(state), 0)
        record = engine.resolve_round(state, RoundDecision(Size.HUGE))
        self.assertEqual(record.evolution_draw_count, 0)

    def test_discarding_loaded_trait_removes_load(self):
        engine = GameEngine(traits(), events(), seed=3)
        state = engine.new_game()
        state.traits = [TraitState("armor"), *[TraitState(f"t{i}") for i in range(4)]]
        record = engine.resolve_round(
            state,
            RoundDecision(Size.MEDIUM, acquire_index=0, discard_trait_id="armor"),
        )
        self.assertEqual(record.evolution_load, 2)
        self.assertEqual(engine.evolution_load(state), 0)

    def test_new_trait_is_not_active_during_acquisition_round(self):
        engine = GameEngine(traits(), [events()[0]], seed=8)
        state = engine.new_game()
        state.trait_deck = [x for x in state.trait_deck if x != "armor"] + ["armor"]
        first = engine.resolve_round(state, RoundDecision(Size.MEDIUM, acquire_index=0))
        self.assertEqual(first.mitigation, 0)
        # Stage II on the next round is mitigated by the acquired armor.
        second = engine.resolve_round(state, RoundDecision(Size.MEDIUM))
        self.assertEqual(second.event_stage, 2)
        self.assertEqual(second.mitigation, 2)

    def test_latent_can_only_activate_after_reveal_when_trigger_matches(self):
        engine = GameEngine(traits(), [events()[0]], seed=5)
        state = engine.new_game()
        state.traits = [TraitState("latent", active=False)]
        with self.assertRaises(InvalidDecision):
            engine.resolve_round(state, RoundDecision(Size.MEDIUM, activate_latent_ids=("latent",)))
        # Failed decisions are not transactional, so use a fresh state at stage II.
        state = engine.new_game()
        state.traits = [TraitState("latent", active=False)]
        state.event_stages["heat"] = 1
        record = engine.resolve_round(state, RoundDecision(Size.MEDIUM, activate_latent_ids=("latent",)))
        self.assertEqual(record.latent_activated, ("latent",))
        self.assertEqual(record.latent_consumed, ("latent",))
        self.assertEqual(record.damage, 1)
        self.assertNotIn("latent", [t.card_id for t in state.traits])

    def test_persistent_latent_gains_its_post_activation_load_next_round(self):
        latent = TraitCard(
            "persistent", "Persistent", latent=True,
            trigger_tags=frozenset({"heat"}), trigger_min_stage=1,
            activated_evolution_load=2, mitigation_tags={"heat": 1},
        )
        engine = GameEngine([latent, *traits()], [events()[0]], seed=7)
        state = engine.new_game()
        state.traits = [TraitState("persistent", active=False)]
        first = engine.resolve_round(
            state, RoundDecision(Size.MEDIUM, activate_latent_ids=("persistent",))
        )
        self.assertEqual(first.evolution_load, 0)
        self.assertEqual(engine.evolution_load(state), 2)
        second = engine.resolve_round(state, RoundDecision(Size.MEDIUM))
        self.assertEqual(second.evolution_load, 2)
        self.assertEqual(second.evolution_draw_count, 2)

    def test_cumulative_score_floor_preserves_negative_actual_delta(self):
        event = EventCard(
            "catastrophe", "Catastrophe", stage_damage={1: 0, 2: 0, 3: 10, 4: 0}
        )
        engine = GameEngine(traits(), [event], seed=1)
        state = engine.new_game()
        state.prosperity = 5
        state.size = Size.SMALL
        state.event_stages["catastrophe"] = 2
        record = engine.resolve_round(state, RoundDecision(Size.TINY))
        self.assertEqual(record.raw_prosperity_delta, -9)
        self.assertEqual(record.actual_prosperity_delta, -5)
        self.assertEqual(record.prosperity_gained, -5)
        self.assertEqual(state.prosperity, 0)

    def test_zero_draw_allows_one_shed_and_recovers_next_round(self):
        engine = GameEngine(traits(), [events()[0]], seed=4, rounds=2)
        state = engine.new_game()
        state.size = Size.HUGE
        state.traits = [TraitState("armor")]
        state.trait_deck = []
        first = engine.resolve_round(
            state, RoundDecision(Size.HUGE, shed_trait_id="armor")
        )
        self.assertEqual(first.evolution_draw_count, 0)
        self.assertEqual(first.shed_trait_id, "armor")
        self.assertEqual(state.traits, [])
        second = engine.resolve_round(state, RoundDecision(Size.HUGE))
        self.assertEqual(second.evolution_draw_count, 2)

    def test_shed_cannot_be_combined_with_acquisition(self):
        engine = GameEngine(traits(), [events()[0]], seed=4)
        state = engine.new_game()
        state.size = Size.HUGE
        state.traits = [TraitState("armor")]
        with self.assertRaises(InvalidDecision):
            engine.resolve_round(
                state,
                RoundDecision(Size.HUGE, acquire_index=0, shed_trait_id="armor"),
            )

    def test_game_runs_all_eighteen_rounds(self):
        wave_events = [EventCard(f"e{i}", f"Event {i}") for i in range(6)]
        engine = GameEngine(traits(), wave_events, seed=11)
        state = engine.run(HoldPolicy())
        self.assertEqual(state.round_number, 18)
        self.assertEqual(len(state.history), 18)
        self.assertTrue(engine.is_finished(state))


if __name__ == "__main__":
    unittest.main()
