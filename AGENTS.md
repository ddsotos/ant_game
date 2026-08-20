## Project goal

This repository is an experimental game-design project.

Read GAME_DESIGN.md first.
GAME_DESIGN.md is the source of truth for the current game concept.

The primary objective is NOT visual polish or feature completeness.

The primary objective is to discover a small, playable ruleset that repeatedly creates
interesting dilemmas between:

- immediate prosperity
- evolutionary flexibility
- specialization
- preparation for escalating ecological events

## Development priority

Priority order:

1. Core game loop
2. Interesting player decisions
3. Automated simulation and playtesting
4. Balance
5. Rules clarity
6. Content variety
7. UI/visual polish

Do not work on item 7 while major problems remain in items 1-5.

Until explicitly allowed, UI should be only the minimum needed to play and inspect the game.
A CLI, debug screen, or extremely plain web UI is sufficient.

Do not spend significant effort on:
- animation
- visual effects
- art
- responsive layout
- polished transitions
- sound
- menus beyond what is required to test the game

## Game design authority

Do not casually expand the scope.

Prefer:
- removing a rule
- simplifying a rule
- reusing an existing mechanism

over introducing a new subsystem.

When a proposed rule improves depth but substantially increases cognitive load,
prefer the simpler version unless playtest evidence strongly supports the complex version.

## Iterative design loop

Do not treat the first playable implementation as completion.

After a playable core exists, repeatedly perform this loop:

1. Run automated simulations.
2. Have specialized subagents analyze the game from different perspectives.
3. Identify the most important design problem.
4. Make the smallest rule or balance change that addresses it.
5. Run tests and simulations again.
6. Compare results with the previous iteration.
7. Record findings in PLAYTEST_LOG.md.
8. Record accepted design changes and their reasons in DECISIONS.md.
9. Repeat.

Do not change many fundamental mechanics simultaneously.
Prefer 1-3 targeted changes per iteration so their effect can be evaluated.

## Required subagent reviews

Use GPT-5.6 Luna subagents for narrow parallel analysis.

At minimum use:

- balance_analyst
  Look for dominant strategies, useless traits, runaway scoring, and trivial size choices.

- dilemma_playtester
  Examine representative games and ask whether multiple choices were genuinely tempting.
  Identify moments where one decision was obviously correct.

- adversarial_player
  Attempt to exploit the rules and find degenerate strategies.

- simplicity_reviewer
  Identify mechanics, tags, exceptions, and text that can be removed without losing interesting decisions.

- ant_trait_reviewer
  Check whether trait cards still feel like distinctive ant adaptations rather than generic stat modifiers.

Subagents should primarily analyze, test, and report.
Avoid having multiple subagents simultaneously rewrite the same core game files.

The parent GPT-5.6 Sol agent is responsible for deciding which feedback to accept.

Do not use majority vote.
Use GAME_DESIGN.md and the project goals as the decision criteria.

## Simulation

Build the game logic independently from the UI so thousands of games can be simulated quickly.

Create several simple strategy bots, such as:

- prosperity-first / large-size strategy
- flexibility-first / small-size strategy
- reactive strategy
- specialization strategy
- generalist strategy
- random baseline

The purpose of these bots is not to create a strong NPC.
They are instruments for discovering balance problems and dominant strategies.

Track useful statistics such as:

- score
- survival/extinction rate if applicable
- size choices over time
- number of size changes
- traits acquired
- traits discarded
- evolution draw count
- ecological event damage
- response to stage-II and stage-III threats
- strategy win rates

Do not assume statistical balance means the game is fun.

Also inspect representative game histories and decision points qualitatively.

## What counts as an interesting dilemma

A decision is promising when:

- at least two choices have plausible advantages
- the best choice depends on the current ecological state
- the best choice can change as event stages progress
- short-term scoring conflicts with long-term adaptability
- acquiring a powerful trait can create future regret
- reducing size can feel painful but strategically justified
- increasing size can feel rewarding but risky
- known future event peaks influence decisions without making them deterministic

A decision is weak when:

- one choice is almost always correct
- a mechanic can safely be ignored
- the player makes the same size choice every round
- powerful traits are automatic picks
- evolution-load traits are never worth taking
- preparing for an event peak has an obvious fixed solution

## Iteration success criteria

Continue iterating while major structural problems remain.

Do not declare the prototype successful merely because:
- it runs
- tests pass
- strategies have similar win rates
- cards exist
- the UI works

The prototype becomes promising only when repeated playtest analysis shows that the core
prosperity-versus-adaptability dilemma occurs naturally in many games.

Before stopping, require at least three consecutive design iterations in which no obvious
dominant strategy or trivial core decision is found.

If further progress would require a major redesign rather than tuning,
stop and clearly report that conclusion instead of endlessly adding mechanics.

## Documentation

After every design iteration append to PLAYTEST_LOG.md:

- iteration number
- rules used
- simulations performed
- important quantitative results
- representative interesting decisions
- dominant or degenerate strategies found
- subagent findings
- change selected by Sol
- reason for that change
- what should be tested next

Update GAME_DESIGN.md only when a design change is accepted.

Keep rejected experiments in PLAYTEST_LOG.md rather than silently deleting their history.

## Engineering

Keep game logic deterministic when supplied with a random seed.

Keep core rules separate from UI.

Write tests for rule resolution and event progression.

Make simulation fast enough to run large batches.

Favor simple data-driven definitions for trait and ecological event cards.