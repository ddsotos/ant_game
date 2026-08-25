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

## D-013 — v0.2 Phase 1: replace retreat play with an acceleration loop

Date: 2026-08-20

Accepted for the first redesigned headless build:

- Start at Small; retain five sizes and one-step movement.
- Use candidate counts 6/5/4/3/2 and prosperity multipliers 0/0/1/2/3.
- Separate a four-card hand from three established traits.
- Keep at most one candidate and establish at most one card per round; new traits work next round.
- Only established traits have effect and evolution load. Initial load values are 0 or 1, and at least one candidate is always seen.
- Use cumulative extinction damage with threshold 5 and no recovery.
- Draw the mass-extinction deadline uniformly from rounds 12–18 and reveal it at least one round ahead.
- Keep previously earned prosperity after early extinction as a measured hypothesis, with no survival bonus.
- Use six wave-event families with two deck copies each. Stage IV is harmless resolution and removal.

Removed or deferred:

- v0.1 play costs, evolution budget, multiple-card play, growth cost, shedding, and dormant/activated latent state.
- Shock events, event-order interactions, healing, and survival bonuses.

Why:

The redesign must first test one question: whether preparing a prosperity engine and defenses while Small creates a variable decision about when to accelerate. Hand/established state and evolution load directly serve that question. The removed systems add currencies, timing exceptions, or safety valves before the new loop has evidence that it needs them.

Structural risks to measure before changing rules:

- Event-I damage plus threshold 5 may make preparation too short.
- Retained score may reward intentional early extinction.
- A known final round weakly favors the largest reachable size when damage is size-independent.
- Seeing six of fifteen traits per Tiny round may make deck cycling too reliable.

This is a new experimental baseline and inherits none of v0.1's three-iteration `promising` count.

## D-014 — document internal “trump card” experiments

Date: 2026-08-20

Accepted as an experiment plan, not yet as a player rule:

- Use `切り札カード` only as an internal development and analysis label for memorable end points of an ant lineage, not merely normal cards with larger numbers.
- Do not expose a collective type name, rarity label, special frame, or separate deck to players; show only each trait's individual name and rules.
- Compare four primary forms independently: high evolution load, lineage requirements, crisis unlocks, and requirement plus high load.
- Treat requirement plus high load as the leading hypothesis, while using load-only as the simplest control.
- Mix only one or two experiment cards into the ordinary trait deck; do not add a separate trump-card deck.
- Let an unmet trump card occupy an ordinary hand slot, making a long-term goal costly without a new currency.
- Allow load 2–3 and prosperity 3–5 only inside these isolated experiments; ordinary v0.2 cards remain load 0–1.
- Include a simple establishment-cost control only if load cannot create enough contrast. It must reuse hand/candidate opportunity cost rather than restore v0.1's budget subsystem.

Why:

The new acceleration loop benefits from cards whose future cost naturally expires near mass extinction. A high-load trump card can make the final commitment dramatic while reinforcing, rather than bypassing, the prosperity-versus-flexibility dilemma. Requirement cards can also turn an early draw into a lineage goal, but they risk fixed build orders and dead hands, so they must be compared rather than assumed superior.

Guardrails:

- Establish the normal-card v0.2 baseline before adding any trump-card experiment.
- Test one form at a time on paired seeds.
- Reject forms that are automatic keeps, automatic establishments, near-impossible plays, or mandatory for winning.
- Judge representative histories for anticipation, payoff, regret, and ant-specific identity; win rates alone are insufficient.

No implementation or simulation was authorized as part of this documentation update.

## D-015 — v0.3: adopt the five-round Daybreak-style baseline

Date: 2026-08-21

Accepted by the user for implementation and first measurement:

- Use five rounds with one public environment progressing I / I / II / III / IV.
- Start Small; use four sizes, six visible normal candidates at every size, and size-dependent retention.
- Replace flat trait slots with Daybreak-style columns. Covered cards keep root tags; only the current top ACTION can activate, once per physical card each round.
- Allow activate → cover → activate chains and allow any normal hand card to be committed as permanent tag-only support.
- Include both prosperity and typed one-round disaster shields in ACTION effects.
- Attach public Extreme Adaptations to environment cards. They consume a normal retention slot, enter the ordinary hand, and then use ordinary placement rules.
- Base player-facing cards on documented real-ant biology and retain source metadata in data definitions.
- End every design iteration with fresh Luna reviews and a Sol recommendation; require user approval before implementing the next design change.

First measured baseline settings, not final balance decisions:

- Three columns of capacity five, aggressive retention 4/3/2/1, hand limit eight.
- Prosperity multipliers 0/1/2/3.
- Cumulative extinction threshold six and environment stage damage 0/2/4/2.
- Three starters, thirty normal ACTION cards, four environments, and eight environment-attached Extreme Adaptations.

Why:

This is the smallest implementation that directly tests the approved new question: whether holding and arranging real-ant adaptations, then choosing between prosperity actions and temporary disaster shields, creates a meaningful five-round acceleration decision. The baseline values make the first simulation falsifiable and do not inherit v0.1's `promising` status.

## D-016 — make starters usable and provide a Japanese browser client

Date: 2026-08-21

Accepted by direct user request:

- Keep the three starter cards in their dedicated starter role, but give each an unconditional action that can activate from round one.
- Trail Pheromone draws one card immediately; Earthwork Nest grants +1 retention next round; Collective Foraging grants +1 base prosperity.
- Apply the normal once-per-physical-card-per-round activation limit to starters.
- Treat these as readable tutorial baselines, not final balance values.
- Make the human play surface Japanese and browser-based. Keep English IDs internal so the deterministic engine, tests, and simulation remain stable.
- Retain the CLI as a debugging interface rather than the recommended human interface.

Why:

The previous starters displayed activation conditions but had no legal action options, so the very first board taught the player that visible cards could not be used. The browser client removes command memorization and presents the forecast, cards, columns, tags, legal actions, and round result in one Japanese play surface without changing the headless rules or adding a frontend dependency.

A universal starter shield was briefly implemented but rejected before commit: it raised every deterministic non-random bot to 100% survival in a 100-seed smoke simulation and made disaster preparation largely automatic.

## D-017 — v0.4: replace staged environments with public disaster forecasts

Date: 2026-08-22

Accepted by direct user request:

- Replace the single I / I / II / III / IV environment with five unique disasters selected from eight and revealed in order at game start.
- At each round start, roll 1d6 for every hazard tag on the current disaster and reveal the result before the player acts.
- Resolve uncovered hazard amount `n` as a `2^n` prosperity loss, with prosperity never falling below zero.
- Remove extinction, cumulative damage, stage progression, and separate Extreme/Trump cards.
- Print a named Optimization requirement on every disaster. Count tags across the full board; failure halves the remaining score instead of causing extinction.
- Exclude the top card's own tags from its activation requirement and count only other cards in the same column.
- Make Foundation and Bridge actions unconditional; retain deliberately asymmetric, biology-derived requirements on Payoffs.
- Allow one to three root tags per card and use cross-tag requirements where the real-ant behavior supports them.
- Replace all card-based retention bonuses with an immediate one-card draw. Preserve the size retention curve.
- Keep five rounds and deliver this version directly as a Japanese browser game for human evaluation, without an intervening NPC balance iteration.
- Present root tags with fixed colors and distinct symbols, and use multicolor bands for multi-tag cards without copying an existing game's trade dress.

Why:

The staged environment had become burdened with multiple coupled subsystems and made the user wait for simulation evidence before personally judging the game. The new structure exposes all five strategic targets immediately while the die roll creates a different short-term defensive problem each round. Optimization reuses the existing board-tag mechanism, and failure affects the same prosperity score rather than introducing a separate death track.

This is a structural redesign and resets prior balance conclusions. It is a human-play baseline, not a `promising` result. The next accepted changes should be based first on concrete human play decisions and should remain limited to one to three targeted adjustments.

## D-018 — v0.5: separate environmental change from recurring problems

Date: 2026-08-22

Accepted by direct user request:

- Merge `Cooperation` and `Caste` into one `Sociality` root tag; do not count cards that formerly had both twice.
- Treat forecast cards as long-term environmental changes that contain only an Optimization, not a shield/problem category.
- Use exactly five environmental changes: Flood, Desert Heat Wave, Prolonged Drought, Habitat Instability, and Landmark Loss.
- Combine living-raft and canopy-retreat biology into one Flood Optimization rather than two forecast cards.
- Move heat-shock response into the Desert Heat Wave Optimization.
- Remove spore contamination and post-raid injuries as separate environmental changes; represent them inside recurring fungal and raid problems.
- Independently roll 1d6 for raid, fungal disease, and nest damage every round. Typed one-round shields answer those three problems regardless of the current environmental change.
- Remove heat and drought shields. Storage adaptations use conditional draw rather than shields.
- Treat draw as a scarce strong effect: six cards have draw and all require supporting tags.
- Increase immediately usable cards: sixteen of thirty normal cards are unconditional, especially ordinary shield-1 cards.
- Require substantial tag preparation for every shield of three or more.
- Keep the existing `2^n`, zero floor, and Optimization-halving sequence for the first human-play build, while explicitly flagging the increased three-die pressure for review.

Why:

The v0.4 card conflated two time scales: predictable habitat change and routine colony hazards. Separating them makes the forecast ask “what kind of ant must this colony become?” while the three problem dice ask “what must it handle right now?” The tag merge removes a semantic distinction that was not useful to the player. Scarce, gated draw prevents card flow from becoming an automatic best action, while unconditional small shields preserve legal tactical responses.

This is another structural human-play baseline and does not count toward `promising`. The first tuning question is whether three independent exponential losses erase prosperity too often.

## D-019 — v0.6: remove Movement and add reversible placement guidance

Date: 2026-08-22

Accepted by direct user request:

- Remove `Movement` as a root tag. Reinterpret each affected card through the biological adaptation that produces movement—such as morphology, chemistry, sociality, nesting, or resource ecology—or delete the tag when it adds no independent meaning. Record every individual judgment in `ANT_RESEARCH_CATALOG.md`.
- Reduce each independent raid, fungal, and nest-damage roll from 1d6 to 1d4 while retaining typed shields and the existing exponential penalty.
- During retention, show the player's existing hand beside the new candidates.
- Color ordinary placement buttons green when the played card would immediately meet its activation requirement, yellow when it would be exactly one tag short, and neutrally otherwise. Calculate this from the post-placement column, including the loss of the oldest card when the column is full.
- Add an Undo control that restores the complete state before the previous successful UI action, including deterministic RNG state. Failed actions do not enter undo history.

Why:

Movement described an outcome shared by many adaptations rather than an independent evolutionary basis, and overlapped heavily with the other roots. The UI changes expose information already present in the rules without adding a gameplay subsystem. The d4 change lowers the ceiling of three simultaneous exponential losses. Per the user's instruction, this build is delivered for human play without NPC simulation or a balance playtest, so none of these changes establishes `promising` status.

## D-020 — v0.7: pair raid with sanitation and diversify environments

Date: 2026-08-22

Accepted by direct user request:

- Remove nest damage completely and broaden fungal disease into `sanitation`, covering pathogens, parasites, infected wounds, decay, waste, and brood hygiene.
- Keep the ordinary problem roll at 1d4, but allow optimization-free environments to alter dice or add a public modifier derived from that environment's ecology.
- Expand the environment deck from five to eight and continue revealing five seed-selected cards. Existing environments offer two harder Optimization routes; three new environments have no Optimization and therefore no halving.
- Give every existing card with a total activation requirement of four an explicit weak fallback that activates automatically while its strong condition is unmet.
- Add ten source-backed ant traits, primarily reproductive adaptations. Player-facing names must use the form “ant name's adaptation” in Japanese; when no reliable Japanese common name exists, use a clearly documented game translation of at most five Japanese characters and keep the scientific name outside the title.

Why:

Raid and sanitation form a wider, more legible pair of acute external pressure and colony-internal health pressure. Multiple Optimization routes make a difficult environment less prescriptive, while optimization-free habitats trade long-term construction for immediately stronger routine problems. Weak fallbacks keep demanding cards usable without erasing the reward for completing their conditions. Environment and card effects must follow the represented ecology rather than receiving flavor after their numbers are chosen.

This is a human-play baseline. No NPC simulation or balance playtest is authorized for this implementation, so it does not count toward `promising`.

## D-021 — v0.8: strengthen Payoffs and make storage a delayed reward

Date: 2026-08-22

Accepted by direct user request:

- Change the size prosperity multipliers from 0/1/2/3 to 1/2/3/4, so a Small colony is not locked at zero prosperity, and start every round with five base prosperity.
- Treat `prosperity=5` as the normal strong Payoff contribution. Unconditional Foundation and Bridge cards remain at 1–2 so that preparation still matters.
- Give demanding Payoffs a biology-derived second benefit: a one-card draw, next-round retention, capped board-tag prosperity, or a strong typed shield.
- Replace the strongest storage-themed draw effects on four cards with a choice to hide one hand card and gain one base prosperity per round from the following round onward.
- Keep storage attached to its source card so pushing that card out also ends its income.
- Use Japanese names directly on Optimization requirements; internal IDs remain English for deterministic APIs.
- Use abstract patterns inspired by conditional activation, card tucking/caching, and icon-count rewards without copying any game's named cards or presentation.

Why:

The v0.7 baseline made many successful Payoffs feel numerically close to ordinary cards and made the first Small rounds scoreless. A strong conditional contribution creates a visible reason to build a column, while delayed storage converts a card into future prosperity at the cost of immediate flexibility. The cap on board-tag prosperity prevents a single dense tag from becoming an automatic choice.

This is still a human-play implementation baseline. No NPC simulation or balance playtest was run; it does not count toward `promising`.

## D-022 — v0.9: subtract problems before size and specialize foundations

Date: 2026-08-23

Accepted by direct user request:

- Subtract raid and sanitation penalties from the current round's unmultiplied prosperity pool, floor it at zero, then apply the size multiplier. Earlier-round score is protected; a failed Optimization still halves total score afterward.
- Show the live round breakdown beside the evolution columns: starting five, activations, other card effects, storage, tag rewards, shields, problem deduction, and multiplied gain.
- Rename player-facing “base prosperity” to simply “prosperity.”
- Raise every stored card's delayed income from one to three prosperity.
- Set total-two Payoffs to prosperity three plus their rider, while total-four Payoffs retain prosperity five plus a stronger rider.
- Allow a biology-justified specialist card to supply two copies of one printed root tag. Use one specialist foundation for each root rather than adding a new resource or subsystem.

Why:

Problem damage should interact with the current size decision instead of erasing prior progress after multiplication. Requirement-two and requirement-four cards need visibly different reward tiers. Double-root foundations give otherwise modest cards a durable construction role without adding bespoke card text, and delayed storage at three makes sacrificing a hand card worth considering in a five-round game.

This remains an unplayed human-play baseline. No NPC simulation or balance playtest was run; it does not count toward `promising`.

## D-023 — v0.10: reversible adaptation, exploration, and narrower Payoffs

Date: 2026-08-23

Accepted by direct user request:

- Reduce stored-card income from three to two, and give every storage card a non-storage option with the same immediate prosperity while preserving the hand card.
- Give the Harpegnathos reproductive-worker card a choice to return one eligible lower card in its column to hand, representing reversible gene-expression and caste state.
- Limit lower-card recovery to once per round across the board; starters, support cards, storage hosts, and cards already activated that round are ineligible.
- Give four movement- or exploration-grounded traits an alternative that reveals one extra evolution candidate next round. Candidate bonuses cap at +2 and never increase retention.
- Reduce every Payoff to one printed biological root tag.
- Replace Dry Savanna's two-die-high raid rule with an uncapped, forecastable raid value: first occurrence 1d4+2, thereafter the previous round's pre-shield raid value +2.

Why:

Storage should remain tempting without making sacrificing a card automatic. Recovery and wider preview use the existing hand and column systems to add timing decisions without a new currency. Narrower Payoff tags stop strong completed cards from also being generic construction upgrades. The uncapped savanna pressure is deliberately dangerous but known one round in advance, matching the user's desired reward-risk scale.

This is an unplayed human-play baseline. No NPC simulation or balance playtest was run; it does not count toward `promising`.

## D-024 — v0.11: diversify roots and reserve round five for a finale

Date: 2026-08-23

Accepted by direct user request:

- Limit every card to at most two supplied root icons, and keep every Payoff at exactly one printed root.
- Strengthen unconditional one-root cards relative to two-root cards; in particular, raise the Harpegnathos reproductive worker while removing Oecophylla silkworks' third supplied icon.
- Add twenty real-ant traits, weighted toward eight Chemistry and eight Morphology cards, and use Chemistry/Morphology heavily in their Payoff requirements.
- Remove self-tag requirements from every Payoff and reduce the Matabele-ant termite raid to Sociality only.
- Make board-tag prosperity uncapped by default. A card may use a floor divisor instead of an arbitrary ceiling.
- Separate four finale environments from the standard environment deck. Draw four standard environments and one finale, always placing the finale in round five.
- Keep card flavor text biological; player actions and numerical effects belong only in the effect block.

Why:

The former deck asked for Sociality and Resource Ecology far more often than Chemistry and Morphology, making repeated builds converge. Strong cards also supplied too many construction icons. A one-root/strong-effect exchange makes compact cards attractive without turning completed adaptations into generic infrastructure. A dedicated fifth-round forecast gives a finished board a visible, suitably large target instead of another early-game-scale check.

This is an unplayed human-play baseline. No NPC simulation or balance playtest was run; it does not count toward `promising`.

## D-025 — v0.12: exchange retention capacity for a wider preview

Date: 2026-08-23

Accepted by direct user request:

- During retention, once per round, the player may reduce that round's retention limit by one to reveal two additional candidates immediately.
- Require at least one effective retention slot and two drawable cards; undo restores both candidates and deterministic RNG state.
- Treat the choice as a quality-versus-quantity exchange. It does not increase hand gain and uses no new currency.
- Rename every Optimization as “ant name's adaptation” in Japanese, and use directly verified Japanese common names where Japanese Wikipedia identifies the exact source species.
- Publish the current environments, Optimization requirements, sources, and independent-problem rules as downloadable Japanese JSON for external ChatGPT review.

Why:

The preview exchange reuses the existing retention dilemma and creates an explicit reason to accept fewer cards when the current six do not fit the board. Ant-prefixed Optimization names expose their biological model instead of presenting abstract mechanisms. The JSON export makes design review possible without reverse-engineering Python content data.

This is an unplayed human-play baseline. No NPC simulation or balance playtest was run; it does not count toward `promising`.
## D-026 — v0.16カード効果は既存の解決順へ統合する

Date: 2026-08-25

Accepted by direct user request:

- 衛生・襲撃脆弱性は問題の実効出目へ加算し、その後に同種シールドを適用する。
- 環境による繁栄損失軽減は、環境最適化失敗による半減損失だけを軽減し、問題ペナルティや過去ラウンドの得点獲得処理を変更しない。
- サイズ依存、押し出し時、保持交換強化はカードID分岐ではなく汎用データとして実装する。
- 押し出し時効果は実際に追放された物理カードへ1回だけ発火し、伏せ貯蔵カードや候補捨てには発火しない。
- v0.16調整に従い、要求合計3の完成形は原則として繁栄3＋シールド2とし、形態3要求のサシハリアリだけシールド3を維持する。

Why:

新しい管理資源やカード固有処理を増やさず、既存の問題・最適化・サイズ・押し出し・保持交換の判断へ効果を接続できるため。

This is an unplayed human-play baseline. No NPC simulation or balance playtest was run; it does not count toward `promising`.

## D-027 — v0.16完全版JSONをカード定義の正本にする

Date: 2026-08-25

Accepted by direct user request:

- チェックサム `7d63c54845081860df9493992938407720230059b6641c3f4653baa8428f82d4` の完全版JSONを読み込み、初期形質3枚と通常カード105枚を実装へ反映する。
- 最適化のない環境での繁栄置換と、サイズ依存の候補追加を汎用効果として追加する。
- カード一覧APIと日本語表示は、完全版JSONの名称・生態説明・効果を公開する。

Why:

不完全な復元データやカードID別の例外処理を避け、デザイン資料と実行時カードを同じ版管理データから再現するため。

This is an unplayed human-play baseline. No NPC simulation or balance playtest was run; it does not count toward `promising`.
