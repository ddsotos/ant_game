# CODEX_NEXT_PHASE_INSTRUCTIONS.md
## Ant Evolution Game — Daybreak-style Core Exploration

## 0. Purpose of this document

This document defines the next design/prototyping phase for the ant-evolution board game.

The project has changed substantially since the earlier design passes. The goal of this phase is **not** to preserve previous prototype assumptions.

The primary goal is:

> **Seriously test a Daybreak-style tableau/tag system as the core card-combo structure, while preserving the game's unique identity: preparing evolutionary potential, choosing when to accelerate into prosperity, and risking extinction before the inevitable final mass extinction.**

Do not add new subsystems unless the current structure clearly fails.

The most important experiments in this phase are:

1. 3 columns vs 4 columns.
2. Per-column capacity vs global tableau capacity.
3. Capacity values and how old cards are pushed out.
4. Size differences expressed primarily through how many newly revealed cards may be retained.
5. Increasing the value of holding cards by adding more cards that require an existing tag foundation before becoming strong.
6. Comparing several ways of penalizing failure to adapt to ecological events.
7. Testing whether the system still feels exciting when players may play many cards in a round.

---

# 1. Core experiential target

The game should create moments like:

> "I can still spend another round preparing, but I am losing scoring time."

> "Six interesting adaptations appeared, but at this size I can only keep one."

> "This card would be excellent later, but right now I do not have enough Chemical tags to justify playing it."

> "I can add this powerful card, but doing so pushes an old card out of this evolutionary line and I lose a tag I still need."

> "The flood is already visible. I need to decide whether to shape my species toward one of the known survival routes, or ignore it and accelerate into prosperity."

> "I am taking ecological damage, but the scoring burst is worth it."

The player should not be trying to build a permanently safe species.

The player should be deciding:

> **When is my evolutionary foundation good enough to stop preparing and start aggressively converting the remaining time into prosperity?**

---

# 2. Design philosophy

Preserve these principles unless strong playtest evidence says otherwise.

## 2.1 Species scale, not colony-management scale

The player controls the long-term evolutionary history of an ant species.

Do not turn the game into worker placement, food accounting, colony construction, or fine-grained resource simulation.

## 2.2 Real ant traits should drive the fiction

Cards should be inspired by real unusual ant adaptations whenever possible.

The game should contain memorable cards such as:

- SOLENOPSIS ARK
- PARAPONERA PONERATOXIN
- OECOPHYLLA SILKWORKS
- CEPHALOTES AERIALIS
- CEPHALOTES LIVING GATE
- ODONTOMACHUS TENSION LOCK
- PHEIDOLE ANCESTRAL SWITCH
- PHEIDOLE SUPERMAJOR PROGRAM
- MYRMECOCYSTUS RESERVE
- MEGAPONERA FIELD MEDICINE
- COLOBOPSIS LAST DEFENSE

Avoid generic names such as "Flood Resistance +2" unless used only as temporary prototype labels.

## 2.3 Flavor rich, resolution simple

Real ant biology may inspire the rule.

The rule itself should remain easy to resolve.

Do not reproduce biological complexity literally.

## 2.4 Prefer meaningful constraints over extra currencies

Do not introduce an "evolution point" currency unless clearly necessary.

Prefer constraints already present in:

- hand size,
- retained cards,
- tableau capacity,
- tag requirements,
- old-card push-out,
- size,
- time remaining.

## 2.5 Randomness is welcome, helplessness is not

Card luck should matter.

The game does not need to be perfectly deterministic.

However:

> "I did not draw the required tag, therefore I could not meaningfully play"

is a failure state.

Players should usually have several rounds of planning, card selection, holding, and redirection before important environmental consequences resolve.

---

# 3. Daybreak-style system is the main experiment

For this phase, treat the Daybreak-style structure as the primary candidate rather than a minor reference.

The important borrowed idea is:

- cards are placed into a small number of columns / evolutionary lines,
- older cards remain underneath newer cards,
- underlying cards contribute tags,
- newer cards may exploit accumulated tags,
- the tableau forms an evolutionary history.

Do **not** mechanically reproduce Daybreak.

The system must address a key weakness observed in Daybreak-style play:

> In the late game, accumulated tags can become broad enough that almost any new card can be used somewhere.

This project should instead aim for:

- early flexibility,
- midgame branching,
- late specialization,
- meaningful loss of old evolutionary foundations,
- continued risk that a strong card does not fit the species the player has actually built.

---

# 4. Tag system

Tags represent **evolutionary roots / mechanisms**, not the ecological problem a card solves.

Current primary tag set:

1. **Morphology**
2. **Chemistry**
3. **Cooperation**
4. **Caste**
5. **Nesting**
6. **Movement**
7. **Resource Ecology**

Japanese working meanings:

- 形態
- 化学
- 協働
- カースト
- 営巣
- 移動
- 資源生態

Normal trait cards should usually have **1–2 tags**.

Do not add tags merely to describe every detail of a card.

---

# 5. Meaning of the tags

## Morphology

Physical specialization:

- mandibles,
- head structure,
- body shape,
- specialized hairs,
- armor,
- thermal body adaptations.

Morphology may lead to very different outcomes:

- weaponry,
- locomotion,
- nest defense,
- thermal survival,
- caste specialization.

## Chemistry

Chemical evolutionary machinery:

- venom,
- antimicrobial secretions,
- pheromones,
- wound treatment,
- chemical signaling.

Chemistry is intentionally broad because this creates interesting evolutionary branching.

The same root may lead to:

- PARAPONERA-style venom,
- antimicrobial defense,
- pheromone recruitment,
- medical treatment.

Do not split "weapon chemistry" and "sanitation chemistry" into separate tags.

Their effects differ; their evolutionary root can be shared.

## Cooperation

Capabilities that require multiple ants acting as a functional collective:

- living rafts,
- living chains,
- mass raids,
- rescue,
- cooperative transport,
- collective construction.

"All ants are social" is not enough to grant Cooperation.

The card should represent a special collective capability.

## Caste

Specialized worker/reproductive forms and division into distinct physical or functional castes:

- soldiers,
- supermajors,
- repletes,
- reproductive specialization.

## Nesting

Specialization of the nest itself:

- underground architecture,
- leaf nests,
- multiple nests,
- defended entrances,
- fungus chambers,
- waste chambers.

## Movement

Specialized spatial behavior or locomotion:

- gliding,
- trap-jaw escape,
- nomadism,
- navigation,
- scouting,
- long-distance movement.

## Resource Ecology

How the species obtains, stores, cultivates, or structures access to resources:

- food storage,
- fungus farming,
- aphid husbandry,
- plant mutualisms,
- specialized foraging.

This tag intentionally includes many former "resource" and "symbiosis" concepts.

---

# 6. Effects and tags must remain separate

Do not turn ecological effects into tags.

Examples:

PARAPONERA PONERATOXIN may have:
- Chemistry / Morphology
- strong predator/competition effects.

MEGAPONERA FIELD MEDICINE may have:
- Chemistry / Cooperation
- disease/wound effects.

Both use Chemistry, but their actual ecological effects are very different.

Similarly:

- Flood,
- desert,
- fungal disease,
- predators,
- rival ants

should not automatically become permanent player-side tag categories.

---

# 7. Starter species

The species should begin as something recognizably "ordinary ant", not already as an exotic specialist.

Initial starter-card candidates:

## TRAIL PHEROMONE
Tags:
- Chemistry
- Movement

Represents ordinary pheromone-based recruitment/foraging.

## EARTHWORK NEST
Tags:
- Nesting

Represents a basic soil nest.

## COLLECTIVE FORAGING
Tags:
- Cooperation
- Resource Ecology

Represents ordinary cooperative food exploitation.

Start with approximately 3–4 simple cards.

The visual/emotional contrast should be:

> "At the beginning this is just an ant."

Then, by the end:

> "This species became a fungus-farming, medically sophisticated, chemically armed, hyper-specialized superorganism."

---

# 8. Column count: only test 3 vs 4

Do not test 5 columns in the current phase.

Primary variants:

## C3
3 evolutionary columns.

Expected effect:
- stronger specialization,
- more conflict over where cards belong,
- higher risk that good cards do not fit.

Risk:
- may become too restrictive,
- may force specialization instead of allowing it.

## C4
4 evolutionary columns.

Expected effect:
- more flexibility,
- more room for branching,
- still meaningfully less forgiving than 5 columns.

Risk:
- may still allow late-game universal compatibility.

Use actual card data when comparing these.

Do not decide from theory alone.

---

# 9. Old-card removal: use push-out only

For this phase, old cards should leave the tableau only because **new cards push them out**.

Do not use:

- automatic aging every N rounds,
- card destruction from ecological damage,
- size-up automatic deletion,
- ancestral-tag remnants,
- random loss of established traits.

The thematic interpretation is:

> New evolutionary specialization displaces older foundations within that evolutionary line.

This is more appropriate than an ecological event arbitrarily deleting genes/traits.

---

# 10. Compare two capacity models

The main old-card experiment is:

> **per-column capacity vs global tableau capacity**

Do not compare unrelated removal systems at the same time.

---

# 11. Capacity Variant L — per-column limit

Each column has a maximum depth.

Example:

- 3 columns × 5 cards
- or 4 columns × 4 cards

When a player adds a card beyond that column's limit:

> the oldest card in that same column is discarded.

The player does not choose an arbitrary card to discard.

This preserves the feeling of a historical evolutionary line.

Questions to test:

- Does this create interesting pain when an old tag is pushed out?
- Does it make players hesitate over which column receives a new card?
- Does it become a mechanical conveyor belt?
- Does a low capacity destroy combos before they become interesting?
- Does a high capacity simply recreate Daybreak's late-game tag abundance?

---

# 12. Capacity Variant G — global tableau limit

The entire species has a maximum number of tableau cards.

Example:

- 3 columns, total maximum around 15
- 4 columns, total maximum around 16

When the tableau is full and the player adds a new card:

> the oldest card in the column receiving the new card is pushed out.

Do not let the player freely discard any card from anywhere.

This distinction is critical.

The global limit allows:

- one deep evolutionary line,
- several shallower lines,
- highly uneven specialization.

Questions to test:

- Is global capacity more expressive than fixed per-column depth?
- Does it create better specialization?
- Does it become too easy to keep one "museum column" untouched forever?
- Does it reduce placement tension because players can simply grow one preferred line?
- Do players still experience painful tag loss?

---

# 13. Capacity tuning methodology

First compare the **type of limit**, not dozens of numeric values.

Keep total capacity roughly similar between variants.

Example comparison set:

- C3 + per-column depth 5 = 15 cards
- C4 + per-column depth 4 = 16 cards
- C3 + global capacity 15
- C4 + global capacity 16

After identifying the more promising capacity model, test:

- low capacity,
- medium capacity,
- high capacity.

The desired frequency is:

> Players should sometimes have to sacrifice an old, still-useful tag to make room for something new.

Not:

> Every card play automatically deletes something.

And not:

> The capacity limit matters only in the final turn.

---

# 14. No card-play-count limit

For now, there is **no per-round limit on the number of trait cards a player may play**.

This is deliberate.

The project should preserve the tactile/combo excitement of:

- drawing many cards,
- holding several possibilities,
- unloading multiple cards,
- suddenly completing tag requirements,
- transforming multiple columns,
- creating a dramatic evolutionary burst.

If the game becomes too long because players can play many cards:

> reduce the number of rounds before reducing the number of cards players may play.

Do not use a play-count limit as the first balancing tool.

---

# 15. Why hand retention matters

If players can play unlimited cards and every card is immediately useful, then size-based retention differences do not matter.

Therefore, the card pool must contain a substantial number of cards that are:

> weak / inefficient before the player has built the right tag foundation,  
> but powerful once the correct evolutionary history exists.

This creates reasons to hold cards rather than immediately dump the hand.

---

# 16. Card-role distribution

Build the prototype card pool with several functional roles.

## Foundation cards

Low/no tag requirements.

Used to establish evolutionary roots.

Useful early.

Examples:
- simple Chemistry,
- simple Nesting,
- simple Cooperation.

## Payoff cards

Become meaningfully stronger when enough tags already exist.

Examples:

> If this column contains Chemistry 2+, gain a large effect.

> If the species has Cooperation 3+, gain extra Prosperity.

> This ability functions only if both Morphology and Caste are present.

These should create:

> "I want to hold this for later."

## Bridge cards

Connect evolutionary roots that would otherwise be distant.

Examples:
- Nesting + Caste
- Chemistry + Cooperation
- Resource Ecology + Morphology

Bridge cards should make redirection possible without making every card universally compatible.

## Extreme Adaptations

Highly distinctive real-ant adaptations.

Usually publicly available through environmental conditions or other visible requirements.

Do not rely on random draw as the only way to find them.

---

# 17. Approximate card-role mix to test

Do not make every card conditional.

Initial rough experiment:

- 40–50% Foundation / independently usable
- 35–45% Payoff / strongly tag-dependent
- 10–20% high-requirement payoff or extreme cards

These are not final percentages.

The important requirement is:

> In a typical hand, there should sometimes be cards worth keeping because they may become excellent in 1–3 rounds.

---

# 18. Size system: primary penalty is retention

For the current phase, do not add several size penalties at once.

All sizes should see the **same number of newly revealed cards**.

Example:

> Reveal/see 6 new trait cards every round.

Size primarily determines:

> **how many of those newly revealed cards may be retained into the player's hand.**

This preserves the "gacha" excitement at every size.

A Giant species still sees interesting mutations/adaptations.

It is not evolutionarily blind.

It simply cannot preserve as many possible future directions.

---

# 19. Size retention variants

Start with at least two curves.

## Size Curve A — aggressive

From 6 seen cards:

- Small: retain 4
- Medium: retain 3
- Large: retain 2
- Giant: retain 1

## Size Curve B — softer

- Small: retain 4
- Medium: retain 3
- Large: retain 3
- Giant: retain 2

Do not assume the aggressive curve is correct.

---

# 20. Desired size feeling

## Small

> "I can preserve several interesting future paths."

The species stores evolutionary options.

Prosperity should be low.

## Medium

> "I can still maintain my hand while beginning to score."

A transition size.

## Large

> "I see many possibilities, but I must throw most of them away."

Prosperity becomes attractive.

## Giant

> "The mutations are still appearing, but only one or two directions can survive into the future."

This should feel like:

> high current prosperity + collapsing future flexibility.

Not:

> "I stopped drawing cards, so I stopped playing the card game."

---

# 21. Hand size

Use a finite hand limit.

Initial range:

> approximately 7–9 cards.

This is necessary because otherwise Small players can hoard a massive hand, become Giant, and retain enough stored options to ignore the Giant penalty.

Questions to test:

- How many rounds of Small play are needed to fill the hand?
- Does reaching hand cap feel like "I am prepared"?
- Is a held payoff/extreme card meaningfully expensive because it occupies hand capacity?
- Can a Giant species burn through its stored hand over several rounds?

---

# 22. Extreme adaptations are public

Extreme adaptations required for important survival routes should not depend entirely on random draw.

Examples:

- SOLENOPSIS ARK
- extreme heat adaptations,
- supermajor-like emergency adaptations,
- dramatic disease/sanitation adaptations,
- last-resort defensive systems.

When a relevant ecological event is present, its available extreme adaptations and tag requirements should be visible.

Players can therefore plan toward them.

---

# 23. Environmental information is public for now

Do not hide environmental intensity in the current prototype.

If an event is coming / active, players should know:

- what it is,
- its current strength/stage,
- any known survival routes,
- extreme adaptations it can unlock,
- their tag requirements.

This is intentional.

The game already contains card randomness.

Environmental hidden information should not simultaneously remove planning.

Future uncertainty can be tested later after the core decisions work.

---

# 24. Survival routes

Do not force every ecological event into one abstract resistance stat.

Prefer:

> a concrete environmental problem with several biologically interesting ant-specific survival routes.

For example, Flood should not be:

> "Environment resistance 3 required."

Instead, research real ant flood responses and identify multiple plausible adaptations.

SOLENOPSIS ARK is one known example.

Avoid generic, dull routes such as:

> "move to high ground"

unless the real ant behavior itself is distinctive enough to deserve a card.

The goal is that survival routes themselves feel like interesting ant biology.

---

# 25. Environment-induced evolution

An ecological event may unlock a visible extreme adaptation if a species already has the right evolutionary foundation.

Example concept:

FLOOD:

> SOLENOPSIS ARK  
> Requirement: Cooperation X + Morphology Y

The environment does not automatically grant the trait.

It creates an evolutionary opportunity.

The player must still choose whether pursuing/playing it is worth it.

This allows:

> the same environment to have several possible evolutionary responses.

Do not assume one canonical solution per event.

---

# 26. Environmental failure penalty is still open

This is one of the major design questions for the next phase.

Do not prematurely lock in one penalty system.

The desired properties are:

- zero preparation should be genuinely dangerous,
- partial adaptation should rapidly reduce the risk,
- perfect adaptation should not always be mandatory,
- taking damage in exchange for prosperity must sometimes be rational,
- historical prosperity already earned should generally remain,
- environmental events should not arbitrarily delete established trait cards,
- the system should remain easy to calculate.

Ask fresh Luna reviewers to propose and compare penalty models.

At minimum compare the following families.

---

# 27. Penalty family A — cumulative extinction damage

Failure causes damage on an extinction track.

Example shapes to test:

- linear,
- exponential,
- strongly front-loaded.

A previously discussed candidate shape:

> effective threat difference 1 → 1 damage  
> difference 2 → 2 damage  
> difference 3 → 4 damage

But do not treat these exact values as fixed.

Questions:

- Does this become generic HP?
- Does it produce the desired "take the hit and score anyway" decisions?
- Is no adaptation sufficiently scary?

---

# 28. Penalty family B — prosperity suppression first

Mild ecological mismatch primarily suppresses prosperity.

Example:

- mild failure → reduced prosperity this round,
- medium failure → zero prosperity + some extinction damage,
- severe failure → major extinction damage.

This may better represent:

> "the species survived, but this was not a prosperous era."

Questions:

- Does this make environmental events feel more integrated with the scoring race?
- Does it overly punish the player's main reward?
- Does it create more interesting choices than pure damage?

---

# 29. Penalty family C — cliff / threshold damage

The penalty curve is intentionally non-linear.

Example:

- well adapted → 0
- slightly under-adapted → 1
- clearly under-adapted → 2
- essentially unadapted → catastrophic 4–5

The purpose is:

> doing *something* to prepare should matter enormously.

This matches the desired feeling:

> "No answer at all is terrifying. A partial answer may be enough to gamble."

---

# 30. Penalty family D — evolutionary bottleneck

Severe failure also reduces future evolutionary flexibility.

Possible effects:

- temporarily retain one fewer new card,
- discard some future candidates,
- other temporary retention penalty.

Do not test this first if it confounds the size system.

Retention is already the main size mechanism.

Only test bottlenecks after the size curve is understandable.

---

# 31. Penalty family E — loss of latent possibilities

Severe failure may discard cards from hand rather than deleting established traits.

Theme:

> the population bottleneck destroyed future genetic possibilities, not already-established adaptations.

This could be elegant because hand = latent evolutionary possibilities.

However it may over-punish Large/Giant species because retention is already their weakness.

Treat this as a secondary experiment.

---

# 32. Environmental penalty evaluation criteria

For every candidate system record:

- extinction frequency,
- average round of extinction,
- survival to Mass Extinction,
- prosperity earned before extinction,
- frequency of players deliberately accepting damage,
- frequency of total "no-answer" disasters,
- frequency of perfect-defense play,
- whether environmental decisions change size decisions,
- whether the penalty is easy to understand from other players' boards.

Representative logs matter more than only aggregate win rate.

---

# 33. Mass Extinction remains an inevitable deadline

The final Mass Extinction is not a boss fight.

It cannot be resisted.

When it arrives, the game ends and all species are extinct.

The objective is:

> accumulate as much Prosperity as possible before then, without dying too early to ordinary ecological crises.

Early extinction should generally preserve already-earned Prosperity rather than reset the player to zero.

Exact end-game survival bonus remains optional and should not be assumed.

---

# 34. Scoring and size

Large/Giant must be genuinely tempting.

Do not make them merely dangerous.

The exact scoring model remains subject to testing, but the intended structure is:

- Small: low/zero prosperity multiplier
- Medium: modest
- Large: strong
- Giant: explosive

Size should feel like an accelerator.

The key decision should not be:

> "How long can I stay safe?"

It should be:

> **"Is my hand/tableau ready enough that I should start cashing the remaining time into points now?"**

---

# 35. Round structure — current candidate

A useful starting loop:

1. **Reveal / update ecological situation**
2. **Reveal normal evolution candidates**
3. **Players retain cards according to size**
4. **Players may play any number of cards from hand**
5. **Players may change size according to the size-change rule**
6. **Resolve ecological consequences**
7. **Resolve prosperity**
8. **Advance events / round / Mass Extinction timeline**

Exact ordering may need revision.

Especially test whether size choice should occur before or after card play.

Do not add complexity unless this ordering creates a clear exploit.

---

# 36. Simultaneous / shared resolution

The design is interested in:

> showing the ecological situation first, letting all players respond, then resolving the round together.

This has several benefits:

- players know the danger before choosing how greedy to be,
- players can see others taking risks,
- cards have moments where they are visibly played,
- simultaneous prosperity/damage creates a shared dramatic payoff.

Do not turn the central board into a cooperative shared-defense meter.

Threats are shared.

Each species' adaptation is its own.

---

# 37. Other-player visibility

This game should avoid the feeling that everyone silently solves their own tableau.

Useful lightweight mechanisms include:

- shared environmental threats,
- visible extreme adaptation opportunities,
- visible size,
- visible columns/tags,
- simultaneous ecological settlement,
- dramatic play of named extreme traits.

Avoid adding direct attacks merely to force interaction.

The preferred interaction is:

> "I want to look at your species because I want to understand how you are surviving and why you are scoring so much."

---

# 38. Fresh Luna reset

The previous Luna agents should be considered finished.

Do not continue using them merely because they have historical context.

This project has changed enough that previous design assumptions may now cause anchoring.

For this phase:

> **Start a fresh Luna design-review team.**

Sol remains the continuing Game Director / Tech Lead.

Luna specialists are fresh reviewers for the current phase.

---

# 39. What fresh Luna agents should read

For their first pass, fresh Luna agents should read:

1. the current authoritative GAME_DESIGN.md,
2. this document,
3. current card/event data required for their task.

Do **not** initially give them old Luna conversations or full historical design commentary.

The goal is an independent evaluation of the current structure.

---

# 40. Historical logs should be read after independent analysis

Recommended workflow:

## Pass 1 — independent review

Fresh Luna forms its own conclusion from current rules.

## Pass 2 — historical check

Only after writing its initial conclusion, it may read relevant PLAYTEST_LOG / archived reviews to answer:

- Was this already tested?
- Did an old failure reappear?
- Is the new conclusion actually novel?
- Does current evidence contradict historical results?

This reduces anchoring without throwing away past work.

---

# 41. Archive, do not delete, old Luna work

Previous Luna reports should remain available in an archive.

Example:

`/archive/old_luna_reviews/`

They are evidence, not current authority.

Sol may consult them when necessary.

Fresh Luna should not treat them as instructions.

---

# 42. Fresh Luna roles

Recommended roles for this phase:

## board_system_luna

Focus:
- 3 vs 4 columns,
- per-column vs global capacity,
- capacity tuning,
- push-out behavior,
- late-game universal compatibility.

## size_economy_luna

Focus:
- retention curves,
- hand cap,
- Small vs Giant incentives,
- whether preparation dominates,
- whether Giant still has meaningful card choices.

## card_combo_luna

Focus:
- Foundation/Payoff/Bridge mix,
- tag network,
- whether cards need existing tag foundations,
- whether holding cards is genuinely valuable,
- whether there are enough interesting "not yet" cards.

## environment_luna

Focus:
- real-ant survival routes,
- environment-induced extreme adaptations,
- ecological failure penalty variants,
- avoiding generic environmental resistance.

## adversarial_playtester_luna

Focus:
attempt to break the system with:
- stay-Small hoarding,
- fastest possible Giant rush,
- dump entire hand immediately,
- broad tag soup,
- hyper-specialization,
- ignore-environment scoring,
- only-environment-defense play.

## simplicity_luna

Focus:
- rule burden,
- unnecessary tags,
- exception proliferation,
- whether environmental card text is becoming too long,
- whether a mechanic can be deleted.

---

# 43. Luna reset instruction

Each fresh Luna should receive a statement equivalent to:

> This is a fresh design-review pass.  
> Do not preserve a mechanic merely because it already exists in the prototype.  
> Treat the current design documents as authoritative, not previous agent assumptions.  
> Independently challenge the Daybreak-style structure before reading historical conclusions.  
> Prefer identifying a root design problem over adding a compensating subsystem.

---

# 44. What Sol should decide

Do not use majority voting among Luna reviewers.

Sol owns final design decisions.

Luna reports are evidence.

Sol should explicitly state after each experiment:

- what was observed,
- what design problem matters most,
- which variant wins for now,
- what remains uncertain,
- what 1–2 things change in the next iteration.

---

# 45. Experiment matrix — board structure

Do not explode into a giant combinatorial grid.

Start with four structural variants:

1. 3 columns + per-column capacity
2. 4 columns + per-column capacity
3. 3 columns + global capacity
4. 4 columns + global capacity

Keep total capacity similar.

Use the same card pool and strategy bots.

Compare:

- average cards playable from hand,
- number of times a good card has no attractive placement,
- number of meaningful old-card push-outs,
- frequency of losing a still-needed tag,
- number of distinct active tag clusters,
- percentage of newly seen cards that are trivially usable,
- end-game tag breadth,
- representative player regret.

---

# 46. Experiment matrix — size retention

Once board capacity has a reasonable baseline, compare at least:

## Aggressive
4 / 3 / 2 / 1 retained

## Soft
4 / 3 / 3 / 2 retained

Optionally one intermediate curve.

Do not combine a large number of additional size penalties during this experiment.

Measure:

- rounds spent at each size,
- average hand size,
- cards discarded from newly revealed sets,
- number of useful cards discarded,
- number of turns Giant remains strategically flexible,
- prosperity per size,
- extinction rate per size,
- whether "stay Small until hand cap" dominates.

---

# 47. Experiment matrix — environmental failure

Once board/size behavior is readable, compare a small number of penalty systems using identical seeds where possible.

At minimum:

1. cumulative extinction damage,
2. prosperity suppression + damage,
3. cliff/non-linear damage.

Only later test:

4. evolutionary bottleneck,
5. latent-hand loss.

Do not compare all five simultaneously.

---

# 48. Card data required for this phase

The prototype should include enough cards to actually stress the tag network.

Target roughly:

- 20–30 normal trait cards,
- several tag-dependent Payoffs,
- several Bridge cards,
- 4–8 Extreme Adaptations,
- 3–4 starter cards.

The exact number is less important than having:

- every tag represented,
- multiple cross-tag bridges,
- no tag that is useful only for one event,
- no obvious single "correct" tag path.

---

# 49. Logging

Every design iteration should record in PLAYTEST_LOG.md:

- variant name,
- seed(s),
- structural settings,
- size-retention curve,
- hand cap,
- card pool version,
- environmental penalty model,
- summary statistics,
- representative decision logs,
- strongest exploit found,
- most painful / interesting decision,
- changes proposed.

Accepted decisions should be copied to DECISIONS.md.

Rejected experiments stay in PLAYTEST_LOG.md.

Do not silently rewrite history.

---

# 50. Stop conditions for this phase

The Daybreak-style core is promising if repeated playtests show:

- players often hold cards for future tag payoff,
- good cards sometimes do not fit,
- placement decisions are not automatic,
- old-card push-out sometimes hurts,
- end-game tableau is powerful but not universally compatible,
- Small is useful for preparation but not obviously dominant,
- Giant still sees exciting cards but must discard painful possibilities,
- environmental forecasts change which tags players value,
- players sometimes knowingly accept ecological damage to score,
- different games produce different acceleration timings.

The Daybreak-style core should be reconsidered if repeated tests show:

- tag placement is usually obvious,
- almost every card becomes playable in the late game,
- the player rarely regrets where a card was placed,
- holding cards is rarely useful,
- Small always dominates,
- Giant stops feeling like a card-combo game,
- ecological events feel like unrelated mini-rules,
- survival depends primarily on drawing one specific card,
- old-card push-out feels like bookkeeping instead of evolution.

---

# 51. Main design questions for Sol after this phase

Sol should be able to answer:

1. **3 columns or 4?**
2. **Per-column capacity or global capacity?**
3. **What approximate capacity creates the best push-out tension?**
4. **What retention curve makes Small feel preparatory and Giant feel greedy without making either dominant?**
5. **How many Payoff cards are needed before holding cards becomes meaningful?**
6. **Can real-ant survival routes keep environmental events specific without bloating card text?**
7. **Which ecological failure penalty best supports "take damage for prosperity" play?**
8. **Does the Daybreak-style system produce enough non-obvious combo decisions to deserve remaining the core?**

Do not move to major UI polish before these questions have credible answers.

---

# 52. One-sentence project target

> **Build an ant species from ordinary evolutionary roots into a highly specialized organism, preserve or discard future evolutionary possibilities as size increases, and decide when to stop preparing and aggressively convert the remaining time before extinction into prosperity.**
