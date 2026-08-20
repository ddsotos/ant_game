# Design Decisions

## D-001 — v0.1 baseline after Phase 1 review

Date: 2026-08-19

Accepted:

- Use a solo, fixed 18-round score game for the first headless prototype.
- Keep the requested five sizes, 15 traits, three latent traits, six wave events, two shock events, and two sequence interactions.
- Resolve damage only as a reduction to the current round's prosperity.
- Acquire normal traits after event resolution; only previously held latent traits may react after reveal.
- Use five trait slots and a minimum evolution draw of one.
- Defer extinction, persistent damage, trait categories, exclusions, environment transitions, and a general tag matchup table.

Why:

This is the smallest interpretation that still tests every explicitly requested v0.1 hypothesis: prosperity versus flexibility, specialization load, staged warning, latent insurance, shock events, and limited event order effects. The deferred systems add state or exceptions without being necessary to measure the central dilemma.

Rejected for now:

- Reducing the prototype to three sizes, no latent traits, and wave events only. This is simpler, but it removes several hypotheses the requested v0.1 must test.
- Adding an end-game-only size rule before measurement. Final-round growth is a known exploit candidate and should first be quantified under the normal rule.

## D-002 — Iteration 1: reduce unconditional giant value

Date: 2026-08-19

Accepted:

- Reduce Huge base prosperity from 7 to 6.
- Apply wave-event size damage only from stage II onward.
- Add event-specific size pressure: predators, drought, and prosperity-targeting parasites punish Large/Huge, while invasion punishes Tiny/Small.
- Add `peak_adaptive` as a diagnostic bot; this does not change the player rules.

Why:

Across 1,000 paired seeds, `always_giant` scored 112.46 with 68.3% win credit and `ignore_events` scored 110.56 with 31.6%. A no-trait fixed Huge policy also beat fixed Large by about 29 points, proving the failure was structural rather than only a bot or card-selection artifact. Individual event pressure preserves the rule that Large is not universally vulnerable while making current ecology matter.

Deferred:

- Allowing zero evolution draws and voluntary trait shedding. The draw-floor saturation is real, but changing it simultaneously would obscure whether size/event tuning fixes the first dominant strategy.
- Trait balance changes. Ant identity review found issues, but they are secondary to unconditional Huge dominance.

## D-003 — Iteration 2: make prosperity destructible and load non-saturating

Date: 2026-08-19

Accepted:

- Event damage changes cumulative prosperity, which remains clamped at zero, rather than merely clamping each round's gain.
- Increase wave damage to `I=0, II=4, III=10, IV=2` and Wildfire shock damage to 8 for the next measured iteration.
- Allow evolution draw to reach zero.
- On a zero-draw round, allow shedding at most one held trait instead of acquiring a trait; the reduced load matters from the following round.

Why:

After D-002, no-trait Large and Huge were within about seven points, yet loaded Huge policies still dominated. The one-card draw floor made load 2 and load 8 nearly equivalent. Separately, increasing per-round damage alone saturated at zero gain and did not make larger negative values meaningful. Applying damage to cumulative prosperity and allowing zero draws creates real regret without adding a new resource.

Experiment deferred, not rejected:

- Trait play costs and multiple acquisitions. The preferred version reuses evolution draw `N` as both candidate count and acquisition capacity, with costs 1-3. It will be tested independently after the cumulative-damage/load change so its effect can be attributed.

## D-004 — Iteration 3: convert flexibility into adaptation throughput

Date: 2026-08-19

Accepted for the next measured iteration:

- Add trait play cost 1-3, distinct from persistent evolution load.
- Reuse evolution draw `D` as both candidate count and per-round acquisition budget.
- Allow at most two acquisitions per round with combined cost at most `D`.
- Keep five slots; discard exactly the number of held traits needed to make room.
- Preserve zero-draw shedding and all current damage/size values for causal comparison.

Why:

Cumulative damage and zero draws made specialization costly, but Large/Huge still earned 97.5% of win credit while Tiny/flexible policies ended near zero. Extra draws only improved selection quality and did not create enough actual adaptation. Reusing the existing draw number as throughput adds no currency and directly turns temporary downsizing into the ability to acquire multiple adaptations.

Guardrails:

- Maximum two acquisitions prevents a one-round five-trait Tiny rush.
- Latent insurance costs 2-3.
- Some cost-1 cards deliberately carry load 2, creating immediate temptation followed by reduced future capacity.

## D-005 — Iteration 4: make costly latent insurance consequential

Date: 2026-08-19

Accepted:

- Increase Pheidole and Cataglyphis mitigation by two on their existing trigger-relevant tags.
- Correct `adaptability_first` to target Small; `always_tiny` remains the separate extreme probe.
- Keep damage, size values, and multi-acquisition unchanged.

Why:

Multi-acquisition created real burst-specialization regret but did not lift flexible policies. Lowering global stage-III damage helped every size similarly. Cost-3 latent cards can only be acquired with sufficient current capacity, so strengthening them directly rewards prior flexibility and tests latent insurance without adding rules.

## D-006 — Iteration 5: event-specific relief for Small

Date: 2026-08-19

Accepted:

- Add `Small: -2` signed size-damage modifiers to Anteater, Parasitoid Fly, Fungal Infection, and Long Drought from stage II onward.
- Do not protect Small from Rain Cycle or Invasive Ant Incursion.
- Keep all other values unchanged.

Why:

A universal Small reduction of two produced competitive reactive play without making fixed Small dominant, but risked becoming a hidden universal ability. Four event-specific signed modifiers reuse existing data, preserve Rain/Invasion counterexamples, and make ecology determine whether shrinking is worthwhile.

## D-007 — Iteration 7: constrain stage-switching and latent auto-picks

Date: 2026-08-19

Accepted:

- Set the four event-specific Small relief modifiers to `-3` rather than `-4`.
- Give each dormant latent trait evolution load 1; its explicit activated load replaces that value after activation.
- Raise Cephalotes Living Gate's competition mitigation from 2 to 3, differentiating it from Eciton Living Span.
- Keep `stage_small` as a permanent diagnostic bot; this changes no player rule.

Why:

At Small relief `-4`, ordinary strategies appeared diverse, but a legal policy that watched public event stages and moved toward Small whenever a relieved wave was at II or III scored 34.76 and took 43.7% win credit. At `-3`, its win credit fell to 28.4% in the same sensitivity test without making fixed Small viable. Separately, all three latent traits were acquired in roughly 0.9–1.0 games by several flexible policies because dormant insurance had no load. Dormant load 1 reuses the core opportunity-cost mechanism. The Gate and Living Span otherwise had identical effects and load while the Gate cost one more.

Rejected:

- Keep relief `-4` based only on the six standard bots. The adversarial policy demonstrated that those bots missed a simple legal exploit.
- Add a separate insurance currency or upkeep phase. Existing evolution load expresses the intended cost.
- Remove one of Eciton or Cephalotes. A one-point event-specific distinction preserves two recognizable adaptations without adding a rule.

## D-008 — Iteration 8: split the safe-size answer by ecology

Date: 2026-08-20

Accepted:

- Anteater and Fungal Infection favor Small with a `-4` damage modifier from II onward.
- Parasitoid Fly and Long Drought instead favor Medium with a `-3` modifier.
- Raise the consumed Colobopsis Last Defense from competition mitigation 3 to 4.
- Add `stage_safe` as a diagnostic policy using only public stage-II warnings; it changes no player rule.

Why:

At the previous common Small `-3`, `stage_small` did not dominate numerically, but five independent reviews rejected the candidate because the same Huge-to-Small route occurred in almost every game. Splitting the answer across existing event data creates conflicting preparations when multiple waves advance and gives Medium a purpose beyond transit. Colobopsis was strictly dominated by the persistent Living Gate at equal cost and mitigation while carrying more load and self-consuming.

Deferred:

- Increasing the acquisition cap from two to three to rescue Tiny. This may be worthwhile, but changing throughput together with event geometry would hide which change affected the central dilemma.
- New stage-specific modifier machinery. The existing signed size modifiers are sufficient for this experiment.

## D-009 — Iteration 10: make regrowth an investment

Date: 2026-08-20

Accepted:

- Charge 2 prosperity for each upward size step in the round it occurs.
- Keep holding size and shrinking free.
- Record growth cost explicitly in round history and simulation metrics.
- Retain `late_prosperity_rush` as an exploit probe.

Why:

The public-information policy that adapted during the middle game and locked Huge from round 12 scored 31.66 and received 37.2% win credit in a targeted comparison. Raising global stage-III damage from 10 to 12 or 14 reduced every strategy by nearly the same amount and did not change the exploit's relative advantage. Increasing Huge event modifiers instead made Huge effectively dead. A two-point upward growth cost directly prices the exploit: early growth still has many rounds to repay its investment, while shrinking creates a meaningful cost to regrow. On 1,000 fresh seeds, late rush fell to 24.74 / 7.4%, while prosperity-first, giant, and contextual warning strategies remained within about 1.2 mean points.

Rejected experiments:

- Global stage-III damage 12 and 14. The strategy ordering and win shares barely changed while scores compressed.
- Raising Huge modifiers across most waves. Huge fixed play collapsed far below Large, violating the requirement that growth remain attractive.

## D-010 — Iteration 11: clarify competition-specialist tiers

Date: 2026-08-20

Accepted:

- Eciton Living Span: evolution load 2 → 1.
- Cephalotes Living Gate: competition mitigation 3 → 4.
- Colobopsis Last Defense: competition mitigation 4 → 5.

Why:

Four of five reviews passed growth cost 2, but the ant-trait review found two effective dominance chains after accounting for prosperity as damage-equivalent value. Paraponera matched Eciton against competition while also answering predators, and Odontomachus matched Gate while carrying less load and answering predators. The new ladder uses existing cost/load/persistence axes: Eciton is cheap and low-load, Gate is stronger and persistent, and Colobopsis is the strongest emergency answer but high-load and consumed.

## D-011 — Iteration 12: peak-only exposure for prosperous sizes

Date: 2026-08-20

Accepted:

- On Anteater, Parasitoid Fly, Fungal Infection, and Long Drought, stage III adds 1 damage to Large and Huge.
- Keep stage-II size pressure and the upward growth cost 2 unchanged.
- Add `midgame_large_lock` as a permanent exploit probe.

Why:

The new public-information exploit adapted through round 8 and then simply held Large, scoring 29.79 with 49.3% win credit across 3,000 fresh seeds. Raising the one-time growth cost could not fix a strategy that reached Large by shrinking for free. Peak-only exposure directly makes III preparation matter while preserving Large/Huge income through I and II. Stronger peak modifiers made warning avoidance dominate and suppressed growth; +1 was the smallest useful value. In the next fresh 1,000-seed full field, midgame lock led win credit at 23.6%, contextual warning led mean score at 27.64, and no strategy led both.

Rejected experiments:

- Growth cost 3 or 5: the exploit often shrank into Large and paid no growth cost.
- Growth cost increasing by round: same structural failure, plus more arithmetic.
- Peak exposure Large +2 / Huge +3: overcorrected toward warning avoidance.
- Global stage-III damage increases: compressed all strategies without changing ordering.

## D-012 — Iterations 13–15: declare the v0.1 loop promising

Date: 2026-08-20

Accepted:

- Freeze gameplay values after D-011 for the v0.1 handoff.
- Rate the core loop `promising`, not complete.
- Permit a minimal human CLI; defer visual design and polish.

Why:

All five review roles passed three consecutive disjoint-seed iterations. Contextual warning response led mean score, midgame Large lock often led win share, and neither dominated both. Representative seeds reversed the preferred size route and latent-insurance choice. Fixed Huge, fixed Small, endgame rushes, forced traits, load-zero stacking, single-card-only play, and public-stage recipes did not produce a clear winning pattern. The remaining issues—weak fixed Tiny, near-equal one-card-only performance in one policy, and implementation compatibility debt—are monitoring or engineering concerns rather than a failure of the central prosperity/adaptability dilemma.
