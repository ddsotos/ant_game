# Playtest Log

## Iteration 1 — Initial v0.1 baseline

### Rules used

- 18 rounds; five sizes with prosperity `1/2/3/5/7` and draws `6/5/4/3/2`.
- Draw floor 1, five trait slots, 15 traits, six wave and two shock events.
- Wave damage `I=0, II=2, III=5, IV=1`; only Anteater and Wildfire had meaningful Huge-specific pressure.
- Event resolution preceded trait acquisition; latent traits could react after reveal.

### Simulations performed

- 1,000 paired seeds for six required strategies plus four exploit probes.
- Fixed-size/no-trait comparisons and representative histories for seeds 0, 11, and 57.
- 23 automated tests passed before the iteration change.

### Quantitative results

| Strategy | Mean score | Win credit | Mean event damage |
|---|---:|---:|---:|
| always_giant | 112.46 | 68.3% | 21.68 |
| ignore_events | 110.56 | 31.6% | 24.91 |
| prosperity_first | 81.55 | 0.0% | 18.90 |
| specialist | 63.38 | 0.0% | 26.20 |
| random | 49.86 | 0.0% | 24.27 |
| reactive | 47.48 | 0.0% | 24.89 |
| generalist | 44.60 | 0.0% | 19.70 |
| adaptability_first / always_tiny | 13.09 | 0.0% | 24.36 |

Fixed-size/no-trait mean scores were Tiny 9.74, Small 15.72, Medium 28.53, Large 53.25, Huge 82.08. Huge suffered only about 4 more event damage than Large while earning about 36 more base prosperity over 18 rounds.

Huge strategies drew exactly one card in about 92% of rounds. Evolution load above the floor therefore stopped adding cost, but this was not the sole cause: Huge dominated even without traits.

### Representative decisions

Seed 0 Reactive briefly produced the intended tradeoff at Rain Cycle II: Large offered approximately 3 prosperity with 3 draws, while Medium offered approximately 1 prosperity with 4 draws. At Long Drought II, Small offered about 1 prosperity with 4 draws while Medium offered about 2 prosperity with 3 draws.

The dilemma collapsed after load accumulated. At Invasive Ant III, Small/Medium/Large all drew one card, so the larger option only produced more prosperity. Seed 0 `always_giant` stayed Huge from round 2, still gained 4 prosperity during multiple stage-III events, and finished at 117.

### Dominant or degenerate strategies found

- Always reach Huge and mostly ignore event preparation.
- Take broad multi-tag traits; the remaining draw of one card per round is sufficient to keep improving.
- Final-round growth from Large to Huge adds about two points with no future cost, although this was smaller than the full-game Huge exploit.
- `Pheidole Ancestral Switch` was close to automatic acquisition/activation for several policies.

### Subagent findings

- balance_analyst: Huge's 36-point base advantage over Large dwarfed its roughly 4-point extra event loss; bot valuation errors were not the main cause.
- dilemma_playtester: a few stage-II choices were promising, but high load collapsed all sizes to one draw and stage III restored a trivial larger-is-better choice.
- adversarial_player: event-ignore dominance reproduced without cards; the draw floor also made load 3 and load 10 almost equivalent.
- simplicity_reviewer: keep the requested five sizes, shocks, interactions, and latent traits; tune existing size/event values rather than add rules.
- ant_trait_reviewer: motifs were strong, but many effects reduced to generic tag mitigation; defer trait changes until size dominance is addressed.

### Change selected by Sol

1. Reduce Huge prosperity from 7 to 6.
2. Make wave size pressure start at II and vary by event: several threats punish Huge, while invasion punishes Tiny/Small.
3. Add a `peak_adaptive` diagnostic policy to measure temporary preparation and regrowth.

### Reason

The first structural failure was unconditional Huge value. Event-specific size pressure uses an existing mechanism, preserves the principle that Large is not universally weak, and lets ecology change the preferred size. Draw-floor and trait changes were deliberately deferred so the effect remains attributable.

### Test next

- Whether `always_giant` and `ignore_events` cease to dominate.
- Whether `peak_adaptive` can profit from stage-II preparation and later regrow.
- Whether event-specific pressure creates different preferred sizes rather than a fixed Medium/Large replacement strategy.
- Whether the draw floor still erases evolution-load regret after Huge is no longer unconditional.

## Iteration 2 — Event-specific size pressure

### Rules used

- Huge prosperity 6; other size values unchanged.
- Wave size penalties began at II. Predation, drought, flooding, fungus, and prosperity-targeting parasites pressured Huge to differing degrees; invasion pressured Tiny/Small.
- All other rules remained as Iteration 1.

### Simulations performed

- 1,000 paired seeds for six core bots and five exploit/diagnostic bots.
- Fixed-size/no-trait comparison.
- Representative histories for seeds 0, 11, and 57.
- In-memory comparisons of higher wave damage at 18 and 24 rounds.
- 25 automated tests after the Iteration 1 implementation.

### Quantitative results

| Strategy | Mean score | Win credit | Mean damage |
|---|---:|---:|---:|
| always_giant | 86.27 | 66.5% | 30.99 |
| ignore_events | 84.49 | 33.1% | 34.16 |
| prosperity_first | 78.51 | 0.3% | 21.98 |
| specialist | 62.74 | 0.0% | 26.83 |
| peak_adaptive | 60.72 | 0.0% | 27.46 |
| reactive | 47.63 | 0.0% | 25.15 |
| random | 45.17 | 0.1% | 26.82 |
| generalist | 44.60 | 0.0% | 19.70 |
| adaptability_first / always_tiny | 11.95 | 0.0% | 27.69 |

The change reduced `always_giant` by about 26 points, but it still beat fixed Large in 99% of their paired games. No-trait Large and Huge were much closer at 52.25 and 59.16, showing the remaining gap was strongly amplified by cards and the one-card draw floor.

Simply raising wave damage to `0/4/10/2` under the old per-round clamp did not solve the problem: in a 200-seed exploratory run `always_giant` still won 74.2%. Once every size earns zero, larger damage has no further meaning.

### Representative interesting decisions

Seed 0 `peak_adaptive` created a readable descent: Parasitoid II at Huge, Rain II at Large, and Drought II at Medium. The immediate prosperity remained attractive while the visible event mix justified shrinking. Seed 11 similarly moved Huge→Large→Medium after Invasion II.

These were promising preparations, but neither policy regrew. In 18 rounds no wave event reached IV in the 1,000-game batch, so the game offered escalation without a completed recovery arc.

### Dominant or degenerate strategies found

- Loaded Huge still drew one card in almost every round, so additional evolution load ceased to matter.
- `peak_adaptive` prepared but could not convert preparation into competitive score.
- Increasing only per-round damage caused damage saturation rather than stronger decisions.
- `adaptability_first` duplicated `always_tiny` too closely and understated a plausible flexible strategy.

### Subagent findings

- balance_analyst: the draw floor was now the largest structural flaw; allowing zero and slow shedding made load meaningful in experimental runs.
- dilemma_playtester: event-specific pressure created local dilemmas, but no IV meant no crisis-to-regrowth arc.
- adversarial_player: high per-round damage alone makes all sizes score zero at III; it must not saturate harmlessly.
- simplicity_reviewer: floor zero plus one-card shedding is a small direct repair; a cost/multi-play system is promising but substantially larger.
- ant_trait_reviewer: multi-play would expose generic mitigation stacking; cost must be distinct from persistent evolution load.

### Change selected by Sol

1. Apply event damage to cumulative prosperity with a floor of zero.
2. Test wave damage `0/4/10/2` and Wildfire 8 under that cumulative rule.
3. Let evolution draws reach zero; at zero, the player may shed one held trait instead of acquiring.

### Reason

This directly implements the user's high-negative-score idea in a way that does not saturate at zero gain, while repairing the load floor that made specialization cost disappear. Both reuse existing state and add no currency.

### Test next

- Whether large accumulated prosperity can now be genuinely lost at III.
- Whether zero-draw shedding creates painful recovery rather than a routine reset.
- Whether `always_giant`, `ignore_events`, or always-Large still dominates.
- Whether scores repeatedly collapse to zero, which would mean damage is too high.
- After this comparison, independently test play-cost/multiple-acquisition rules using evolution capacity rather than a new resource.

## Iteration 3 — Cumulative ecological loss and zero-draw recovery

### Rules used

- Cumulative prosperity was clamped at zero after applying each round's full score delta.
- Wave damage was `0/4/10/2`; Wildfire damage was 8.
- Evolution draws could reach zero. At zero, one held trait could be shed instead of acquiring.
- One-card acquisition limit remained.

### Simulations performed

- 1,000 paired seeds for six core and five exploit/diagnostic policies.
- Representative histories for seeds 0, 11, and 57.
- 28 automated tests.

### Quantitative results

| Strategy | Mean score | Win credit | Mean damage |
|---|---:|---:|---:|
| prosperity_first | 36.86 | 51.3% | 60.95 |
| always_giant | 36.57 | 46.2% | 76.07 |
| ignore_events | 30.72 | 1.5% | 81.98 |
| peak_adaptive | 22.50 | 0.2% | 63.66 |
| specialist | 21.66 | 0.4% | 61.59 |
| random | 7.93 | 0.3% | 65.04 |
| generalist | 7.54 | 0.0% | 54.38 |
| reactive | 7.17 | 0.0% | 61.25 |
| adaptability_first / always_tiny | 0.00 | 0.0% | 63.41 |

`prosperity_first` averaged 6.97 zero-draw rounds, 4.50 sheds, and 4.39 subsequent recoveries. The recovery loop functioned mechanically.

### Representative interesting decisions

Seed 0 `prosperity_first` reached 50, then Drought III, Anteater III, and Fungal III caused deltas of -6, -3, and -5, ending at 36. This finally made accumulated prosperity visibly vulnerable.

The same seed's `reactive` reached 37 before shrinking to Small, but finished at 11. Its greater candidate access did not become enough acquired protection, so downsizing remained a losing sacrifice rather than a tempting alternative.

### Dominant or degenerate strategies found

- Large/Huge together took 97.5% of win credit.
- Tiny/flexible play frequently collapsed to zero because low base prosperity provided no buffer against cumulative peaks.
- Shedding was often an automatic `zero draw → discard lowest-value load` operation rather than a hard choice.
- The final III sequence produced repeated losses with few new decisions.

### Subagent findings

- balance_analyst: do not retune damage simultaneously; first test whether acquisition throughput makes extra draws valuable.
- dilemma_playtester: cumulative loss created regret, but flexible play still could not turn draws into protection.
- adversarial_player: unrestricted multi-acquire would enable a Tiny rush; cap it at two and test load-0 stacking explicitly.
- simplicity_reviewer: use the existing draw value as both candidates and budget; avoid a persistent currency.
- ant_trait_reviewer: costs must differ from load; cheap high-load cards can be short-term temptations, while latent insurance should cost 2-3.

### Change selected by Sol

1. Add play costs 1-3.
2. Reuse draw `D` as acquisition budget and allow at most two acquisitions totaling at most D.
3. Add `tiny_rush_then_huge` and `load0_stack` exploit probes; leave damage and size values unchanged.

### Reason

The missing link was not more candidate visibility but the ability to convert flexibility into timely adaptation. The change directly implements the user's proposal without adding a new tracked resource.

### Test next

- Whether Small/Tiny can acquire useful combinations before III and avoid score collapse.
- Whether cost-1/load-2 cards create immediate temptation followed by future regret.
- Whether Tiny rush then Huge, load-0 stacking, or generic mitigation stacking becomes dominant.
- Whether multi-acquisition occurs in meaningful but not automatic situations.

## Iteration 4 — Evolution capacity and multiple acquisition

### Rules used

- Evolution draw `D` was both candidate count and acquisition budget.
- Trait play costs were 1-3; up to two cards with total cost at most D could be acquired.
- Five slots, cumulative damage, zero-draw shedding, and all event values were unchanged.

### Simulations performed

- 1,000 paired seeds for six core and seven exploit/diagnostic strategies.
- Cost-table correction followed by a fresh 1,000-seed run.
- Exploit probes for Tiny rush, load-zero stacking, high-load shedding, latent stacking, and cheap high-load acquisition.
- 28 automated tests.

### Quantitative results

| Strategy | Mean score | Win credit |
|---|---:|---:|
| always_giant | 31.74 | 51.9% |
| prosperity_first | 29.77 | 31.8% |
| ignore_events | 29.54 | 14.7% |
| peak_adaptive | 17.76 | 0.1% |
| specialist | 17.39 | 0.5% |
| random | 7.18 | 0.9% |
| reactive | 7.01 | 0.0% |
| tiny_rush_then_huge | 6.86 | 0.0% |
| adaptability_first / always_tiny / load0_stack | 0.00 | 0.0% |

Multi-acquisition occurred: about 1.05 rounds per prosperity game, 2.43 per Tiny-flexibility game, and 2.18 per Tiny-rush game. No rush or cost exploit dominated.

### Representative interesting decisions

Seed 0 `tiny_rush_then_huge` acquired two traits in each of its first two rounds, then a fifth trait in round 3. Load rose to five and future capacity collapsed. This was the intended immediate specialization followed by regret.

Seed 0 `reactive` accepted roughly one extra immediate point of loss by moving Large→Medium, but gained an extra capacity and acquired two Rain responses. The local dilemma existed, though the final score remained far below Large.

### Dominant or degenerate strategies found

- Large/Huge still took almost all win credit.
- Flexible policies obtained more traits but could not offset stage-III losses before their smaller prosperity buffer reached zero.
- Cost/load exploits were not dominant; if anything, Tiny remained too weak.
- `adaptability_first` incorrectly duplicated the Tiny extreme probe.

### Subagent findings

- balance_analyst: multi-acquire did not yet translate flexibility into enough defense; latent insurance +2 produced a much more diverse virtual result.
- dilemma_playtester: burst specialization and regret appeared in logs; global damage 10→8 helped all sizes but did not change the hierarchy.
- adversarial_player: cost, shedding, and rush probes did not break the game; changing global III damage was ineffective.
- simplicity_reviewer: retain multi-acquire and strengthen existing insurance rather than add another subsystem.
- ant_trait_reviewer: stronger latent insurance risks auto-picks; cost 3 and later trigger narrowing are the appropriate controls.

### Change selected by Sol

1. Add two mitigation to Pheidole and Cataglyphis on their existing relevant tags.
2. Correct `adaptability_first` to target Small while retaining `always_tiny` as the extreme probe.

### Reason

Cost-3 latent insurance requires the player to preserve or regain at least three capacity. Making it consequential directly rewards the desired preparation behavior and leaves other variables unchanged.

### Test next

- Whether Small/Medium policies now survive peaks and earn competitive scores.
- Whether latent acquisition or activation becomes automatic.
- Whether Pheidole/Cataglyphis should be narrowed to one trigger tag.
- Whether a player ever declines a cost-3 latent card to preserve capacity for two cheaper adaptations.

## Iteration 5 — Stronger latent insurance

### Rules used

- Pheidole and Cataglyphis gained +2 mitigation on their existing trigger tags.
- `adaptability_first` targeted Small; `always_tiny` remained the Tiny probe.
- All other Iteration 4 rules remained.

### Simulations performed

- 1,000 paired seeds across 13 strategies and 29 automated tests.
- In-memory Small-relief comparisons at 1, 2, and 3 points.
- Fixed-Small, stage-II-to-Small, stage-III-to-Small, and Small-plus-latent exploit comparisons.

### Quantitative results

| Strategy | Mean score | Win credit |
|---|---:|---:|
| always_giant | 32.78 | 51.4% |
| prosperity_first | 31.13 | 33.7% |
| ignore_events | 29.54 | 13.0% |
| peak_adaptive | 18.95 | 0.5% |
| specialist | 18.20 | 0.6% |
| reactive | 10.51 | 0.0% |
| latent_first | 9.33 | 0.0% |
| tiny_rush_then_huge | 8.55 | 0.0% |
| adaptability_first | 0.00 | 0.0% |

The latent change improved Reactive from about 7 to 10.5 and Latent-first from about 5.6 to 9.3, but did not make flexible play competitive.

The five-wave Small-relief probe showed a clear threshold: relief 1 was too weak, relief 2 raised Reactive to about 26.4 with 9% win credit, and relief 3 made Reactive a new leading strategy. Fixed Small remained weak while stage-II preparation became competitive.

### Representative interesting decisions

Large retained roughly one more immediate prosperity at stage II while Small gained two more evolution capacity. Invasion remained a counterexample where shrinking incurred extra damage. Seed 10 rewarded staged shrinking and beat fixed Large; seed 47 made the same preparation but lost to fixed Large.

### Dominant or degenerate strategies found

- Strong latent activation was usually automatic once matching III occurred; acquisition carried most of the tension.
- A universal five-wave Small reduction risked feeling like a generic hidden stat bonus.
- Rain relief weakened the Rain-to-Invasion ecological identity.

### Subagent findings

- balance_analyst: relief 2 was the useful middle point; relief 3 overcorrected.
- dilemma_playtester: stage-II shrinking was painful but plausible; exclude Invasion.
- adversarial_player: fixed Small and Small-plus-latent were not dominant; Large remained strong.
- simplicity_reviewer: use signed event `size_damage` rather than a new engine rule.
- ant_trait_reviewer: apply relief only where ecologically credible; exclude Rain and Invasion.

### Change selected by Sol

Add Small -2 to Anteater, Parasitoid Fly, Fungal Infection, and Long Drought only.

### Reason

This existing-mechanism change makes shrinking useful while preserving event-specific answers and avoiding a universal small-is-safe rule.

### Test next

- Whether Reactive/Latent gain wins without becoming dominant.
- Whether stage-II decisions differ between Rain, Invasion, and the four relieved waves.
- Whether cost-3 latent acquisition remains a real choice or becomes automatic.

## Iteration 6 — Event-specific Small relief calibration

### Rules used

- Anteater, Parasitoid Fly, Fungal Infection, and Long Drought gave Small `-2` damage from stage II onward.
- Rain Cycle and Invasive Ant Incursion remained counterexamples.
- All cumulative scoring, evolution capacity, multi-acquisition, and latent rules were unchanged.

### Simulations performed

- 1,000 paired seeds across core and exploit policies.
- In-memory sensitivity runs for `-3`, `-4`, and `-5` on the same four events.
- Fixed-Small and stage-responsive size probes.

### Important results

Small relief `-2` raised Reactive to roughly 21 points, but Large/Huge policies still received most win credit. Fixed Small remained noncompetitive. The first standard-bot comparison at `-4` produced the best apparent spread, so `-4` was selected as the next isolated candidate.

### Representative decision

At a relieved event's II, Large offered three more immediate base prosperity than Small, while Small reduced damage by four relative points and exposed two additional trait candidates/capacity before the likely III. Rain and Invasion deliberately reversed or removed that incentive.

### Findings and Sol decision

- The event-specific mechanism made ecology relevant without a universal Small ability.
- `-2` left the sacrifice too weak; `-5` risked turning public stage information into a fixed answer.
- Test `-4` as a candidate, with an explicit adversarial stage-switching policy before acceptance.

## Iteration 7 — The apparent balance at relief -4 fails adversarial review

### Rules used

- The same four wave events gave Small `-4` damage from stage II onward.
- Dormant latent traits had no evolution load.

### Simulations performed

- 1,000 paired seeds for normal and exploit strategies.
- A new legal `stage_small` policy using only public event stages.
- Sensitivity comparison of Small relief `-4`, `-3`, `-2`, and `-1`.
- Five independent Luna review roles.

### Quantitative results

The ordinary comparison looked healthy: always_giant 32.78 / 36.2% win credit, prosperity_first 31.13 / 25.8%, reactive 29.80 / 20.5%, latent_first 28.83 / 9.3%, and ignore_events 29.54 / 6.7%.

That result was misleading. At `-4`, `stage_small` scored 34.76 and took 43.7% win credit. The same probe fell to 31.44 / 28.4% at `-3`, 27.84 / 12.5% at `-2`, and 23.65 / 3.0% at `-1`.

### Representative decision and exploit

Seed 6 at `-4`: the stage policy scored 43 against always_giant's 33. It waited at Huge, then used public Fungal II, Anteater II/III, and Drought III state to shrink. The choice initially resembled the desired short-term sacrifice, but repeating the same response for four visible waves made it a recipe rather than a dilemma.

### Other degeneracies found

- Flexible strategies acquired each of the three latent traits in roughly 0.9–1.0 games. Dormant insurance occupied a slot but imposed no load, so acquisition was nearly automatic.
- Eciton Living Span and Cephalotes Living Gate both gave competition mitigation 2 and load 2, while Gate cost 2 versus Span cost 1. Gate was strictly worse in the implemented event set.

### Subagent findings

- Balance and dilemma reviews found the standard-bot spread promising.
- Adversarial review invalidated it with `stage_small`; the candidate failed.
- Ant-trait review rejected automatic latent insurance and the dominated Gate.
- Simplicity review favored tuning existing signed event damage and load rather than adding machinery.

### Change selected by Sol

1. Reduce the four Small relief modifiers from `-4` to `-3`.
2. Give dormant latent traits evolution load 1.
3. Raise Living Gate's competition mitigation from 2 to 3.

### Reason

These three value changes address the demonstrated exploits through existing mechanisms. Iteration 7 does not count toward the three consecutive promising reviews.

### Test next

- Re-run `stage_small` beside always_giant, ignore_events, and prosperity_first.
- Verify dormant latent acquisition is no longer automatic and insurance is still worth considering.
- Check whether Gate's added mitigation creates a real cost-1 versus strength tradeoff with Living Span.

## Iteration 8 — Common Small relief at -3

### Rules and simulations

- Four events shared Small `-3`; dormant latent load was 1; Living Gate mitigation was 3.
- 1,000 paired seeds across 14 strategies, plus independent 2,000-seed confirmation and representative histories.
- 32 rule/content/simulation tests after the subsequent accepted change.

### Quantitative results

| Strategy | Mean | Win credit |
|---|---:|---:|
| stage_small | 29.02 | 29.4% |
| always_giant | 30.00 | 27.0% |
| ignore_events | 29.54 | 21.6% |
| prosperity_first | 28.12 | 19.4% |
| reactive | 18.28 | 0.5% |

The 2,000-seed confirmation produced always_giant 29.95 / 27.8%, stage_small 28.63 / 26.7%, ignore_events 29.54 / 22.2%, and prosperity_first 28.25 / 21.2%. There was no single numerical winner, but fixed Tiny scored zero and most general flexibility policies remained weak.

Dormant load solved the latent auto-pick problem. Prosperity-first acquired Pheidole 0.22, Cataglyphis 0.15, and Camponotus 0.17 times per game, versus roughly 0.9–1.0 before the load.

### Representative dilemmas

Seed 8 showed a real sacrifice: the staged policy moved Huge→Large at Invasion II, Large→Medium at Rain II, and Medium→Small at Anteater II. It accepted lower immediate deltas and gained extra evolution capacity, finishing 34 against giant's 29.

Seed 7 showed latent regret: Cataglyphis activated at Drought III and reduced damage to 2, but raised load from 4 to 7; the next two rounds had zero evolution draws and lost 5 and 8 prosperity.

### Dominant or degenerate patterns

- In 1,000 games, `stage_small` shrank at R10 in 65%, R11 in 94%, and R12 in 100%.
- The repeated Large/Huge→Small line was close to a fixed recipe even though it did not dominate win credit.
- Fixed Medium, Small, and Tiny were extremely weak.
- Colobopsis Last Defense was strictly dominated by Living Gate: same cost and mitigation, but more load and one-shot consumption.

### Subagent findings and Sol decision

All five reviewers marked the stability candidate failed. Balance and dilemma reviews found the intended sacrifice but a scripted response; adversarial review found Huge still the safest fixed policy; simplicity review rejected adding another subsystem; ant-trait review confirmed latent/Gate fixes but found Colobopsis dominated.

Sol selected two targeted changes: split the four safe-size modifiers between Small and Medium, and raise the one-shot Colobopsis mitigation by one. Iteration 8 does not count toward stability.

### Test next

- Attack the new event-specific `stage_safe` policy rather than only `stage_small`.
- Inspect whether concurrent Small-favoring and Medium-favoring warnings create conflicting choices.
- Confirm Medium is useful without becoming the new fixed answer.
- Confirm Colobopsis is tempting but not mandatory.

## Iteration 9 — Split Small/Medium safe sizes

### Rules and simulations

- Anteater/Fungal favored Small at `-4`; Parasitoid/Drought favored Medium at `-3`.
- 1,000 seeds at 0 and 1,000, then targeted adversarial runs up to 5,000 fresh seeds.
- All 32 tests passed.

### Initial quantitative results

| Strategy | Mean | Win credit (8-policy comparison) |
|---|---:|---:|
| always_giant | 30.04 | 24.4% |
| prosperity_first | 28.23 | 19.0% |
| ignore_events | 29.54 | 18.0% |
| stage_safe | 26.90 | 17.8% |
| stage_small | 25.86 | 9.2% |
| peak_adaptive | 24.14 | 7.0% |
| specialist | 23.48 | 4.6% |

`stage_safe` used Small 22.3%, Medium 21.0%, Large 11.3%, and Huge 45.3%, with 66 distinct size paths instead of `stage_small`'s five. It averaged 1.16 multi-acquisition rounds and spent 67.8% of evolution budget.

### Representative decisions

Seed 8 R14 had overlapping Small- and Medium-favoring warnings. Small offered `+2 / draw 2`, Medium `+1 / draw 1`, and Large `+3 / draw 0`. At R15 Fungal III the policy chose Small for `-2 / draw 2` instead of Medium's `-5 / draw 1`; at R16 Rain III it returned to Medium. The event split produced a real two-way preparation problem.

Seed 2001 demonstrated one-shot specialization regret. Living Gate was shed after its load caused zero draw; Colobopsis was then acquired, raised total load from 2 to 5, blocked Invasion III with competition 4, and consumed itself.

### Reviews and adversarial failure

- Balance, dilemma, simplicity, and ant-trait reviewers passed the candidate.
- Adversarial review found `warning_perimeter_no_latent`: sum only public positive size penalties, move toward the largest unpunished size, and reject all latent cards.
- Across 5,000 fresh seeds it scored 30.95 with 31.7% win credit versus always_giant 29.94 / 15.7%. This was a simple enough public-information recipe to fail the iteration.

### Sol decision

Do not tune rules yet. The exploit combined two hypotheses—safe-size selection and latent rejection—so add three diagnostic variants: warning-perimeter with normal insurance, no insurance, and insurance only after a matching threat is visible.

### Test next

- Attribute the advantage between sizing and latent rejection.
- Determine whether contextual latent insurance can match or beat blanket rejection.
- Re-review the full field; diagnostic policies do not change player rules.

## Iteration 10 — Contextual insurance passes, endgame rush fails

### Rules and simulations

- No player-rule change from Iteration 9.
- Added all/none/contextual latent variants for the same warning-perimeter sizing.
- 5,000-seed qualitative comparison plus five independent Luna reviews.

### Quantitative result

Contextual insurance averaged 31.20, blanket latent rejection 31.03, always_giant 30.05, and stage_safe 26.64 over the large comparison. Contextual latent acquisition was only 0.156 cards/game and produced both gains and regrets, so insurance was neither automatic nor worthless.

Four reviews passed. Adversarial review found a decisive exception: use warning-perimeter sizing through the middle game, then lock Huge from round 12. In a direct 1,000-seed reproduction, `late_prosperity_rush` averaged 31.66 with 37.2% win credit versus contextual warning 31.07 and giant 30.07.

### Representative failure

Seed 3002 used lower size only around R10–R11 warnings, then remained Huge from R12. Late III events removed prosperity, but not enough to outweigh the banked score and continued +6 base income; it finished 44 versus contextual warning's 38 and giant's 35.

### Experiments and Sol decision

- Stage-III damage 12 and 14 lowered scores almost uniformly; the rush's relative win share stayed high.
- Broadly increasing Huge event penalties killed Huge fixed play and made Large dominant.
- A growth cost of 2 per upward step reduced the rush without making initial growth unattractive.

Accept upward growth cost 2 as the one gameplay change. Iteration 10 fails stability because the exploit existed before the change.

### Test next

- Verify early Large/Huge growth still repays its cost.
- Verify shrinking remains useful but regrowth timing becomes painful.
- Re-attack later rush start rounds and one-time shrink/regrow patterns.

## Iteration 11 — Growth investment succeeds; trait dominance remains

### Rules and simulations

- Upward size steps cost 2 prosperity; no other gameplay values changed.
- 1,000 and 2,000 fresh-seed full/targeted comparisons.
- Adversarial sweeps of rush thresholds R8–R17 and one shrink/regrow timing.
- 33 automated tests.

### Quantitative results

Fresh 1,000-seed full field: prosperity-first 26.58 / 21.4%, warning-selective 27.56 / 12.3%, warning-no-latent 27.54 / 12.0%, always-giant 26.41 / 9.9%, late rush 24.74 / 7.4%. No policy led both mean and win share.

Rush thresholds R10–R16 scored 24.34–26.21 versus giant 26.57. R8/R9 reached 27.61 through warning adaptation rather than a late lock. One shrink/regrow was always 1.4–2.2 points worse than giant except the effectively irrelevant R17 timing.

### Representative dilemmas

Seed 13: a policy that shrank and later paid to return scored 30; Medium hold and Large hold each scored 28. Seed 8: staying Medium after shrinking scored 28, while paying to regrow and losing draw capacity scored 20. Regrowth became a real decision rather than a free endgame reset.

### Reviews and failure

- Balance, dilemma, adversarial, and simplicity reviews passed the candidate.
- Ant-trait review found Eciton effectively dominated by Paraponera and Living Gate effectively dominated by Odontomachus when competition prosperity was counted as equivalent to mitigation.

### Sol decision

Keep growth cost 2, but do not count Iteration 11 toward stability. Adjust only three competition-card values: Eciton load 1, Gate mitigation 4, Colobopsis mitigation 5. This creates low-load specialist, strong persistent specialist, and strongest one-shot specialist tiers.

### Test next

- Check the revised competition cards for strict or practical dominance.
- Re-run all endgame and warning exploits unchanged.
- Begin stability count only if all five reviews pass.

## Iteration 12 — Competition ladder passes; Large lock fails

### Rules and simulations

- Growth cost 2 and the revised competition ladder.
- 1,000–3,000 fresh-seed comparisons and five independent reviews.
- 34 automated tests after the selected peak-exposure implementation.

### Initial result

Warning-selective 27.43, warning-no-latent 27.37, giant 26.44, prosperity-first 26.29, and late Huge rush 24.59. Four reviewers found no strategy or trait dominance. The competition ladder passed strict comparison: Eciton offered load-1 specialization, Gate mitigation 4 persistently, and Colobopsis mitigation 5 once at load 3.

### Adversarial failure

`midgame_large_lock` used normal warning response through R8 and held Large from R9. Across 3,000 seeds it scored 29.79 with 49.3% win credit, versus warning 27.60 / 25.7%, prosperity-first 26.31 / 17.0%, and giant 26.54 / 8.0%. Because the policy usually reached Large by shrinking, increasing upward growth cost did not address it.

### Sol decision and rejected experiments

Iteration 12 fails stability. Add peak-only exposure to the four ecology-specific safety events. Growth cost 3/5 and round-scaling cost failed structurally; stronger peak penalties suppressed growth and made warning avoidance dominant. The accepted minimum is +1 damage to both Large and Huge at III.

Fresh 1,000-seed full field after the change: midgame lock 27.19 / 23.6%, warning-selective 27.64 / 12.3%, warning-no-latent 27.56 / 13.6%, warning normal 26.89 / 12.1%, giant 23.94 / 3.0%, prosperity-first 23.53 / 8.2%, and stage-small 22.60 / 7.0%. No strategy led both mean and win credit. This is the next stability candidate, not yet a success count.

## Iteration 13 — Peak exposure candidate, stability 1/3

### Rules and simulations

- Peak exposure +1 for Large/Huge on four events; growth cost 2; all prior trait and capacity rules.
- 1,000-seed full field plus 2,500 fresh adversarial seeds.
- Threshold sweeps R5–R15, fixed sizes, warning/peak avoidance, latent rejection, and forced-trait probes.
- 34 tests and five Luna reviews.

### Results

Warning-selective led mean score at 27.64; midgame Large lock led the original full-field win share at 23.6%. On the independent adversarial field, warning-selective was 27.59 / 13.39%, no-latent 27.50 / 13.07%, and the best new lock threshold 26.83 / 10.59%. No simple strategy exceeded 30 mean or 30% win credit.

### Representative decisions

- Seed 13005: Large lock 36 beat warning descent 34.
- Seed 13000: the same Large lock scored 28 while warning descent scored 34.
- Seed 13016: regrowing through Large/Huge paid 4 and lost evolution draw, ending 30 versus Medium hold 41.
- Seed 13463: Pheidole insurance won 33 versus rejection 22; on seed 13003 Cataglyphis insurance lost by one.

The same broad plan reversed by event order and card availability. Multi-acquisition, load regret, peak preparation, and contextual insurance all appeared in concrete logs.

### Reviews and Sol decision

All five roles passed. No gameplay change. This is the first consecutive stable design review. Continue on disjoint seeds and retain every exploit probe.

## Iteration 14 — Disjoint-seed confirmation, stability 2/3

### Rules and simulations

- Rules unchanged from Iteration 13.
- Full 1,000 seeds at 70,000–70,999; additional 3,000-seed adversarial field and fresh qualitative histories.
- Fixed-size, lock-threshold, forced-card, one-card-only, sequence-aware, and Medium-lock probes.
- 34 tests and five Luna reviews.

### Quantitative results

Warning-selective 27.30 / 13.5%, warning-no-latent 27.25 / 14.2%, midgame Large lock 26.62 / 22.1%, warning normal 26.34 / 11.1%, giant 23.41 / 3.1%, prosperity-first 23.21 / 8.0%, and stage-small 22.07 / 7.8%. The ordering and gaps closely reproduced Iteration 13.

No adversarial strategy exceeded 30 mean or 30% win credit. The best Medium-lock probe averaged 27.36 on 400 seeds. Large/Huge rush thresholds peaked at 24.86. Forced single cards did not produce a mandatory pick.

### Representative reversals

- Seed 2001: Large lock 31 beat warning 23.
- Seed 2004: warning 37 beat the same Large lock 28.
- Seed 2052: Pheidole insurance won 36 versus rejection 31.
- Seed 2073: Pheidole insurance lost 29 versus rejection 31.
- Seed 2000: shrinking then regrowing paid 2 while load forced draw 0.

### Reviews and Sol decision

All five roles passed. No gameplay change. This is the second consecutive stable review. One-card-only performance was close to multi-play in one optimized policy, so multi-acquisition frequency remains a monitoring metric, but concrete histories still showed meaningful burst acquisition and later load regret.

## Iteration 15 — Final disjoint-seed confirmation, stability 3/3

### Rules and simulations

- Rules unchanged from Iterations 13–14.
- Full 1,000 seeds at 80,000–80,999, a second qualitative field at 85,000–85,999, and 3,000 adversarial seeds.
- Fixed sizes, Large/Huge lock sweeps, one-card-only, forced latent/trait, and prior exploit probes.
- Five Luna reviews and 36 final automated tests after adding the CLI.

### Quantitative results

Warning-selective 27.55 / 13.7%, warning-no-latent 27.38 / 13.8%, midgame Large lock 26.88 / 21.5%, warning normal 26.65 / 12.2%, giant 23.66 / 3.0%, prosperity-first 23.20 / 6.7%, stage-small 22.14 / 6.8%, and late rush 22.00 / 1.8%.

Across 3,000 adversarial seeds, warning-selective was 27.52 / 12.86%, no-latent 27.49 / 14.11%, and midgame lock 26.99 / 22.75%. No simple recipe exceeded mean 30 or win credit 30%.

### Representative decisions

- Seed 85000: taking Paraponera + Atta immediately created load 3 and zero Huge draw; later shrinking restored evolution at the cost of prosperity.
- Seed 85052: Pheidole insurance won 37 versus rejection 24.
- Seed 85061: Cataglyphis insurance lost 26 versus rejection 30 because activated load left later draws at zero.
- Rain→Invasion and Drought→Wildfire sequences reversed otherwise similar size choices.

### Final reviews and Sol decision

All five roles passed. Iterations 13, 14, and 15 are three consecutive stable reviews. The v0.1 core loop is **promising**. This does not mean balanced forever or visually complete; it means the central dilemma now occurs naturally and survives the current exploit suite.

### Handoff / next phase

- Keep all diagnostic bots and paired-seed metrics as regression tests for future content.
- Monitor midgame Large lock, one-card-only policies, fixed Tiny's lack of value, and rare Camponotus activation.
- Begin human usability testing through the minimal CLI before proposing any visual polish.

## v0.2 Phase 1 — acceleration-loop design review

### Scope

No simulations were counted for the redesign yet. Five independent GPT-5.6 Luna reviews examined the new source-of-truth design as systems designer, balance designer, ant-trait designer, simplicity reviewer, and adversarial playtester. The parent Sol integrated the findings without majority vote.

### Accepted initial rules

- Size candidate counts 6/5/4/3/2 and prosperity multipliers 0/0/1/2/3.
- Hand 4, established traits 3, maximum one keep and one establishment per round.
- Establishment occurs after the event and candidate step and becomes active next round.
- Established-only load 0/1; candidate count has a floor of one.
- Extinction damage threshold 5, no healing, mass extinction at a hidden R12–18 with one-round warning.
- Six wave families with two copies each; IV ends harmlessly.
- No initial play costs, multi-play, independent latent mode, shocks, sequence rules, growth costs, or survival bonus.

### Important findings

- A no-countermeasure I→II→III wave deals 1+2+4=7, while countermeasure 1 reduces it to 0+1+2=3. Threshold 5 makes minimum preparation consequential but may be too abrupt.
- One-card-per-round establishment prevents storing four cards and committing all of them immediately before acceleration.
- Keeping earned points after early extinction could enable a deliberate score-and-die strategy; it must be attacked rather than assumed safe.
- With size-independent event damage, raising size on the known final round has no future adaptability cost. This may be acceptable cash-out behavior or a structural failure; simulation and representative logs must decide.
- Existing 15 ant traits can remain distinctive using prosperity, threat countermeasures, stage conditions, size conditions, and one-shot consumption. A separate latent subsystem is not needed initially.

### Sol decision

Implement this minimal baseline without tuning it first. The first measured iteration must attack rush, long preparation, prosperity-only, defense-only, fill-hand-then-commit, final-warning growth, suicide scoring, forced-card picks, and deck cycling. The most important observed failure—not the largest list of reviewer concerns—will determine the next change.

## v0.2 design addendum — internal trump-card experiment plan

### Status

Documentation only. No implementation, automated simulation, stability count, or `promising` claim was made.

### Question

Can a few visibly stronger cards create a memorable sense that an ant lineage has reached its final form, while preserving real reasons to wait, discard the card, or choose another evolutionary route?

### Planned comparison

- A: no requirement, evolution load 2–3.
- B: up to two existing lineage/tag requirements.
- C: a matching ecological event at III.
- D: one size or lineage requirement plus load 2–3; current leading hypothesis.
- E: simple establishment cost using an existing hand/candidate opportunity, only as a control if load is insufficient.

Each primary variant receives only one or two representative cards and is compared independently against the same ordinary-card baseline and paired seeds. `切り札カード` is an internal label only; no player-facing type name, separate deck, new currency, or restored v0.1 play-budget system is introduced.

### Required qualitative evidence

Representative histories must show when the card was first seen, how long it occupied the hand, when its condition became true, what was sacrificed by establishing it, how sharply scoring changed, and at least some games where delaying or rejecting it was better. The `dilemma_playtester` and `ant_trait_reviewer` must assess whether the result feels like a distinctive ant lineage rather than a large generic bonus.

## v0.3 Iteration 1 — five-round Daybreak baseline

### Rules and implementation

- Five rounds; public environment stages I / I / II / III / IV.
- Start Small; C3 capacity five; aggressive retention 4/3/2/1; hand limit eight.
- Six normal candidates at every size; prosperity multipliers 0/1/2/3.
- Top-only ACTION effects, once per physical card per round; activate → cover → activate is legal.
- Any normal card may instead become permanent tag-only support.
- Typed one-round shields; cumulative damage threshold six; stage damage 0/2/4/2.
- Thirty normal real-ant ACTION cards, three starters, four environments, eight attached Extreme Adaptations.
- Minimal solo CLI, deterministic simulator, six core bots, seven exploit probes, and 29 passing tests.

### Simulations

The final baseline field used 500 paired seeds for each of 13 policies. An earlier 1,000-seed smoke run used less capable sizing policies and is not used for balance comparison.

| Strategy | Mean score | Survival | Win credit |
|---|---:|---:|---:|
| prosperity_first | 28.45 | 79.6% | 9.0% |
| adaptability_first | 6.98 | 90.0% | 0.2% |
| reactive | 23.83 | 91.0% | 2.3% |
| specialist | 22.44 | 69.4% | 5.6% |
| generalist | 24.54 | 84.2% | 3.9% |
| random | 0.53 | 9.0% | 0.0% |
| always_small | 0.00 | 89.8% | 0.0% |
| always_giant | 30.25 | 43.8% | 33.3% |
| ignore_environment | 26.79 | 51.2% | 12.7% |
| shield_only | 2.85 | 90.4% | 0.2% |
| dump_hand | 28.45 | 79.6% | 9.0% |
| extreme_beeline | 23.66 | 87.8% | 3.6% |
| final_turn_giant | 27.08 | 83.8% | 20.4% |

### Representative decisions

- Seed 2 / Desert Heat Wave: always-Giant reached Giant at R3, took two damage at II and four at III, and went extinct with score 18. The late-Giant policy remained Large, retained Silver Thermal Coat, and survived with score 33.
- Seed 5 / Flood Front: always-Giant retained Solenopsis Ark and survived at damage five with score 35. The late-Giant policy used Canopy Escape, reached damage six, and went extinct at score 30. The public adaptation was not a fixed answer.
- Seed 26 / Army Ant Raid: choosing Paraponera's shield option at R3 prevented two damage but ended at 31; the prosperity route survived and reached 41.
- Seed 321 / Stage III: Reactive used a Megaponera shield chain to reduce raw damage four to zero, demonstrating same-round defensive chaining.

### Dominant and degenerate behavior

- Existing bots placed every tied card into column 0. In 500 prosperity-first games, all 10,629 placements went there, so they did not measure multi-column placement or support tradeoffs.
- A fresh distributed-column probe scored 41.45 with 97.2% survival and 83.3% paired win credit. Maintaining three reusable top ACTION streams is currently a dominant-looking route.
- Nearly every normal card's requirements equal its own one-copy root tags. Since self-tags count, most cards activate immediately; Foundation / Bridge / Payoff roles do not yet create the intended preparation graph.
- Small ×0 may be a scoring cliff, but size tuning is premature while the card graph and column bots are invalid.
- `dump_hand` exactly matched prosperity-first, so it does not isolate hand dumping.

### Fresh Luna findings

- balance: always-Giant and late-Giant are strong, while Small ×0 is nearly scoreless; win credit and mean score measure different survival assumptions.
- dilemma: size/retention/shield reversals exist, but column-0 tie-breaking prevents conclusions about the tableau dilemma.
- adversarial: a distributed-column policy dominates the measured field; no engine legality exploit was found.
- simplicity: remove unused SUPPORT/ON_PLAY role branches later; keep typed shields and card-flow effects for now.
- ant-trait: biological identity and sources are broadly strong, but self-satisfying requirements erase the intended Foundation→Bridge→Payoff progression.

### Sol decision and approval gate

Iteration 1 is not stable and does not count toward `promising`. Do not tune size multipliers or add growth costs yet. The proposed next change set is limited to:

1. Keep Foundation cards broadly self-starting, but revise Bridge/Payoff requirements so at least one tag must pre-exist in the chosen column.
2. Replace column-0 tie-breaking with column-aware diagnostic policies and counterfactual placement/action logging, while retaining a single-column exploit probe.

Per the approved review process, these changes require user approval before implementation. Next test: rerun the same paired seeds after only these content/measurement corrections.

## v0.3 Iteration 2 — uniform Payoff requirement +2 experiment

### Authorized change

At the user's request, add two to every listed root-tag threshold on all fourteen normal Payoff cards. A requirement of Morphology 1 / Movement 1 therefore becomes Morphology 3 / Movement 3. Foundation, Bridge, starter, and environment-attached Extreme requirements remain unchanged. This is an isolated experiment, not yet an accepted `GAME_DESIGN.md` rule.

### Tests and simulations

- 30 automated tests passed.
- Repeated the same 500 paired seeds across the six core and seven exploit policies.
- Fresh balance and dilemma Luna reviews ran additional 1,000-game and randomized-column probes.

| Strategy | Mean score | Survival | Win credit | Payoff activations/game |
|---|---:|---:|---:|---:|
| prosperity_first | 10.51 | 55.2% | 5.9% | 0.71 |
| adaptability_first | 3.47 | 86.2% | 1.9% | 0.00 |
| reactive | 8.63 | 78.4% | 4.0% | 0.74 |
| specialist | 9.71 | 66.2% | 16.2% | 0.56 |
| generalist | 9.72 | 72.0% | 16.9% | 0.82 |
| always_giant | 11.91 | 35.0% | 20.3% | 0.54 |
| final_turn_giant | 10.06 | 65.0% | 18.8% | 0.63 |

Compared with the zero-bonus baseline, typical mean scores fell from 22–30 to 8–12. In a separate in-memory +1 comparison, prosperity-first scored 25.37, reactive 20.49, generalist 24.18, and always-Giant 28.38; +1 preserved much more of the original reward layer.

### Qualitative result

- Fresh randomized-column policies reduced the column-0 rate from 100% to roughly one third and activated 1.64–1.77 Payoffs per game. Therefore +2 does not make every Payoff literally impossible.
- Seed 6 / Army Ant Raid: R1 Odontomachus became support in the Earthwork column; R2 Head-Barricade extended it; R3 Cephalotes Living Gate was retained and placed; R4 the completed Payoff activated and prevented the raid damage. The player delayed reward and used support to finish a lineage.
- Some roots are much harder than others. Pheidole Supermajor Program needs Caste 3 / Morphology 3 and consumes almost the entire five-card column, making a normal Payoff feel closer to an Extreme Adaptation.
- Existing deterministic bots still choose column 0 on ties, so their 0–0.82 activation rates understate what deliberate multi-column play can achieve.

### Reviews and Sol status

- balance: uniform +2 is too severe as a general tuning value; it suppresses scoring and survival rather than only creating preparation.
- dilemma: +2 can produce genuine multi-round build stories when columns are selected intelligently, but the current Bot field cannot measure their frequency reliably.

This iteration is not stable and does not count toward `promising`. Keep the +2 implementation as the current inspectable experiment, but do not update `GAME_DESIGN.md` or treat it as accepted balance. Sol recommends fixing column-aware measurement first, then comparing uniform +1 against +2 on identical seeds. User approval is required before that next change.

## v0.3 Player-access correction — usable starters and browser UI

### Authorized changes

- Make all three starter cards unconditional, once-per-round actions from round one.
- Provide a Japanese browser client while preserving the headless engine and CLI.

### Rejected smoke variant

The first Earthwork Nest draft granted one universal disaster shield every round. In a 100-seed smoke run, every deterministic non-random core policy reached 100% survival. This removed most pressure to construct typed defenses, so the universal shield was rejected before commit.

### Retained starter effects and smoke result

- Trail Pheromone: draw one card immediately.
- Earthwork Nest: +1 retention next round.
- Collective Foraging: +1 base prosperity.

With these effects and the still-experimental Payoff requirement +2, a 100 paired-seed smoke run produced:

| Strategy | Mean score | Survival | Win credit |
|---|---:|---:|---:|
| prosperity_first | 20.29 | 70.0% | 43.3% |
| adaptability_first | 5.88 | 85.0% | 3.0% |
| reactive | 17.26 | 78.0% | 13.3% |
| specialist | 19.00 | 76.0% | 21.3% |
| generalist | 17.74 | 60.0% | 19.0% |
| random | 0.12 | 2.0% | 0.0% |

### Review and status

- Luna starter review recommended keeping `CardRole.STARTER`, adding empty requirements and real options, and allowing the engine to activate STARTER or ACTION tops.
- Luna browser review recommended a thin JSON projection over the existing phase API and a dependency-free HTML/CSS/JavaScript client.
- The final implementation has Japanese card names, descriptions, effects, tags, sizes, environments, actions, and errors. English IDs remain internal.
- 36 automated tests pass, including Japanese content coverage, starter activation, deterministic bot parity, and a complete five-round browser-service flow.

This is a player-access correction, not a stable balance iteration, and does not count toward `promising`. Human play feedback is the next required evidence.

## v0.4 Human-play baseline — public disasters and Optimization

### Authorized rules

- Five rounds; choose five unique disasters from eight by seed and reveal the complete order at setup.
- Roll one d6 per current hazard tag before size, retention, placement, and activation decisions.
- Add size-multiplied prosperity, subtract `2^n` for each uncovered hazard, floor at zero, then floor-halve the remaining score when the printed Optimization is unmet.
- Remove stages, extinction, cumulative damage, separate Extreme cards, and card-based retention bonuses.
- Count only other cards in the same column for top-card activation. Count the entire board for disaster Optimization.
- Use one-to-three-tag real-ant cards, unconditional Foundation/Bridge actions, and asymmetric/cross-tag Payoff conditions.

### Implementation evidence

- Headless engine and browser service are deterministic for a supplied seed.
- Eight disasters each contain a named, biology-derived Optimization and one or two typed hazards.
- Thirty normal traits plus three starters use the seven fixed root tags and retain biology metadata.
- Final integration review found that no card could answer the `drought` hazard; existing liquid-storage and underground-granary cards now provide typed drought shields so every hazard offers at least one player response.
- The Japanese browser displays all five forecasts, die rolls, typed shields, Optimization progress, self-tags versus activation tags, 1–3-color bands, and the complete score-resolution order.
- The research catalog records the current ant taxa, biological basis, sources, and future candidates.
- 39 automated tests passed, including five-round completion, unique deterministic forecasts, top-card tag exclusion, exponential loss, zero floor, score halving, every hazard having a player shield, hand-space-aware retention display, structured tag presentation, Japanese coverage, and real HTTP service behavior.
- A live HTTP smoke check on seed 42 returned the v0.4 server, five distinct forecast cards, and a visible first-round hazard roll.

### Simulation and review status

No multi-game NPC balance simulation was run for this iteration. This is intentional: the user asked to skip NPC play and reach a human-playable state. Existing strategy code was only migrated so it does not depend on removed fields; its small unit tests are engineering checks, not balance evidence.

The engine, content, and browser work were independently implemented/reviewed by narrow Luna subagents. Their scope was schema correctness, real-ant content, and human-readable interaction—not a claim that the new economy is balanced.

### Current design status

This iteration does not count toward the three stable reviews required for `promising`. There is not yet a representative human decision log. In particular, the severity of `2^n`, the attainability of five public Optimization targets, and the usefulness of Small versus Giant remain open questions.

Next test: the player completes several seeds in the Japanese browser and records specific moments where prosperity, shield activation, size, placement, and future Optimization offered competing choices. Select at most one to three changes from that evidence.

## v0.5 Human-play baseline — environmental changes and three recurring problems

### Authorized rules

- Merge Cooperation and Caste into Sociality, producing six root tags.
- Forecast five long-term environmental changes, each carrying an Optimization but no problem type.
- Every round, independently roll raid, fungal disease, and nest damage on 1d6 and apply matching temporary shields.
- Keep `2^n` per unblocked problem, sum the losses, floor at zero, then halve the remainder if the environmental Optimization is unmet.
- Make storage a conditional-draw theme; move heat-shock response into the heat-wave Optimization.
- Keep draw scarce and gated, provide more unconditional actions, and gate strong shields behind heavier conditions.

### Content audit

- 33 playable cards: three unconditional starters and thirty normal cards.
- Six draw cards, all with non-empty activation requirements.
- Sixteen normal cards have no activation condition.
- Ordinary shield-1 cards are mostly unconditional.
- Seven cards provide shield 3; every one has a substantial activation condition.
- No playable card uses old Cooperation/Caste tags or heat/drought shields.
- Five environmental changes use real-ant adaptations: combined flood response, silver-hair plus heat-shock protection, underground granary, emergency emigration, and sky-compass navigation.

### Engineering evidence

- 38 automated tests passed.
- Tests cover deterministic five-environment ordering, three deterministic problem dice per round, typed shield application, exponential losses, zero floor, Optimization halving, top-card self-tag exclusion, six-tag content invariants, draw/shield gating, Japanese browser data, and complete five-round browser-service play.
- JavaScript syntax and Python compilation succeeded.
- CLI and diagnostic strategies were migrated to the problem schema, but no multi-game balance simulation was run.

### Luna findings and Sol decision

- systems/simplicity recommended exactly three problems—raid, fungal, nest damage—rather than restoring heat or drought as a fourth shield category.
- ant taxonomy recommended five habitat-scale environmental changes and the Sociality merge.
- Both reviews warned that three simultaneous dice make the retained exponential penalty much harsher.
- Sol retained the user-requested dice and existing exponent for this first playable comparison instead of changing two structural dimensions at once.

### Status and next test

This iteration does not count toward `promising`. The next evidence must come from human play. Record whether scores repeatedly return to zero, whether the player can meaningfully choose among three defenses, whether gated draw remains attractive without becoming automatic, and whether the five Optimizations suggest different builds.

## v0.6 Human-play access update — five roots, d4 problems, placement guidance

### Authorized changes

- Remove the Movement root card by card, reinterpreting it only where another biological root explains the adaptation and otherwise deleting it.
- Roll each of the three recurring problems independently on 1d4.
- Show the existing hand during retention selection.
- Mark ordinary placements green when immediately activatable and yellow when exactly one tag short, using the column after any capacity push-out.
- Allow the browser player to undo the previous successful operation, including a round resolution and its RNG state.

### Engineering evidence

- Formal content, Optimization requirements, localization, and browser configuration expose exactly five root tags and no Movement tag.
- The research catalog contains the per-card Movement audit and biological rationale.
- Rule tests cover deterministic d4 bounds. Browser-service tests cover hand visibility during retention, Undo restoration, failed-action history, and capacity-aware placement prediction.
- JavaScript syntax, Python compilation, the automated test suite, and a basic HTTP endpoint smoke check are the permitted verification for this delivery.

### Playtest and review status

No NPC simulation, automated strategy batch, representative-game analysis, or human playtest was performed for this update, by explicit user request. Automated rule and interface tests are engineering verification, not playtest evidence. This update therefore does not count toward the three stable reviews required for `promising`.

Next test is intentionally left to the player: use the browser build and report concrete decisions or interface problems before any balance iteration.

## v0.7 Human-play baseline — raid, sanitation, and alternate Optimizations

### Authorized changes

- Replace raid/fungal/nest damage with exactly two recurring problems: raid and sanitation.
- Give the five existing environments two harder, alternative Optimization patterns wherever the biology supports distinct responses.
- Add three optimization-free habitats whose ecological conditions modify the two problem rolls in different public ways.
- Add ten real-ant traits, primarily reproductive, using Japanese board-game names in the form “ant name's adaptation.”
- Give total-requirement-four cards a weak automatic fallback when their full condition is unmet.

### Validation boundary

This iteration is to receive rule tests, content invariant tests, browser API tests, JavaScript/Python checks, and a basic HTTP startup check only. It must not run NPC strategies, simulation batches, representative-game analysis, or human play. Engineering validation is not playtest evidence.

### Status

This iteration does not count toward the three stable reviews required for `promising`. Quantitative results and representative decisions are intentionally absent until the player evaluates the browser build.
