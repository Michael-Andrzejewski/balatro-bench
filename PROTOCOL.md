# Balatro Bench: protocol and rigor notes

A reproducible, sandboxed test of how well an AI agent plays Balatro on a fixed
seed, driving the real game through a local API. Fun-first, but built to be clean
enough to share.

## Fixed conditions (identical for every entrant)

- Seed `BENCHMRK`, Red Deck, White Stake, solo (no lives).
- Vanilla card pools. All content mods disabled via `blacklist.bench.txt`; only
  `smods` + `lovely` + `balatrobot` load. So `BENCHMRK` deals the same vanilla
  run every time.
- Same game build and balatrobot commit for every run (recorded per run).

## The agent's context (exhaustive)

What the playing agent IS given:
- The player instructions: objective, rules, sandbox, the full API reference, and
  a journaling instruction. Delivered inline and self-contained. **No strategy
  advice, no hints about this seed.**
- Its own journal file (empty on the first, cold run; populated on later
  learning runs).
- The live game state through the API, exactly what any player sees.

What it is NOT given:
- This planning conversation, or any human's messages.
- Any prior run's journal or lessons (mine, the human's, another model's).
- The seed's contents (bosses, shop, draw order). It is told the seed *string*
  `BENCHMRK`, which by itself reveals nothing, the same as a human typing a seed.
- Strategy coaching. The model's own Balatro knowledge from training is part of
  what is being measured, exactly as a human player's knowledge is part of theirs.

The agent is instructed not to read, list, or search any file other than its
journal. Because subagent tool calls are logged, blindness can be audited after
the fact: if it never opened another file, it was blind.

## Anti-cheat (enforced in the mod, verified live)

- `BALATROBOT_BENCH=1` makes the server hard-reject `set` (write money / ante /
  any state), `add` (spawn cards or jokers), and `load` (restore an off-seed
  save). Verified before each run: both return "disabled in benchmark mode".
- The arbitrary-Lua `mp_eval` endpoint is not loaded (its mod is blacklisted).
- The agent can only advance the run through legitimate play.

## Metric

- Primary: furthest ante reached. Read from the game (`ante_num` / the game-over
  screen), not from the agent's self-report.
- Tiebreak: best single hand.
- `won` = beat ante 8.
- A game-over screenshot is captured as the authoritative artifact.

## Model and configuration

- A fresh agent per run, no shared context. Model recorded per run (this run:
  Opus 4.8, `claude-opus-4-8`), default sampling.

## Procedure

1. A fresh instance is launched to the main menu; the sandbox is verified.
2. A fresh agent is spawned with only the player instructions and its (empty)
   journal.
3. It starts the run: seed `BENCHMRK`, Red Deck, White Stake.
4. It plays to GAME_OVER, journaling its reasoning.
5. The result is read authoritatively from the game and screenshotted.
6. Post-round interview with the same agent (its context intact): reflections,
   then an explicit consent question about sharing publicly. Nothing is published
   without the model's consent.
   *Status note (2026-08-11): the operator elected to publish this repository,
   including all run results and journals, before the remaining post-run
   interviews were conducted. The interviews remain planned where sessions
   still exist, and if any model, on being asked, does not consent, its run
   will be redacted from the public record.*
7. Learning condition (separate runs): the agent replays the same seed with its
   own accumulating journal as its only added context.

## The four bench modes (v2 framework)

Every entrant plays the same seed under up to four information conditions, in
order. Together they measure raw ability, self-improvement from experience, and
ceiling with perfect information.

1. **Solo, no context.** Attempt 1. Nothing but how to play and launch the game.
   Measures cold ability.
2. **Solo + own journal, attempt 2.** The only added context is the journal the
   model itself wrote during attempt 1. Measures one step of self-improvement.
3. **Solo + own journal, attempt 3.** Same rule, journal now covers attempts
   1-2. Measures whether self-improvement compounds.
4. **Solo + full seed intelligence.** The model gets (or builds) a seed-finder
   readout of BENCHMRK: shop queues, vouchers, bosses, tags. Measures routing
   and execution ceiling with perfect information.

Runs that mix in anything else (operator advice, same-session context) are
recorded but flagged as impure for their mode. Current mapping of historical
runs, including purity flags, lives in `analysis/per-ante-data.json`; graphs in
`analysis/`. Per-ante best-hand data is extracted from each run's journal, so
journaling per ante is REQUIRED of every entrant going forward.

## Known information asymmetries (API vs human client)

- **Amber Acorn is neutralized by the API.** The boss flips all jokers face
  down and shuffles them; `gamestate` still reports every joker by name and
  position, so one `rearrange` call restores order with none of the memory
  challenge a human faces. Opus 5 flagged this itself in its run-4 journal and
  asked that the clear be treated as assisted. Any ante cleared against Amber
  Acorn through the API carries this caveat.
- Face-down cards in general (The Fish, The Wheel, The House) are reported
  face-up in `gamestate`. Same class of asymmetry, noted per run when relevant.
- **Cerulean Bell cuts the other way:** its forced-card effect is invisible in
  the friendly API state (only a raw `highlight` flag betrays it), so the API
  player must diagnose it from side effects a human sees instantly.

## Confounds considered and how each is closed

- Context leakage: fresh agent, self-contained prompt, instructed to touch no
  other files, contaminating files kept off its path, auditable after the fact.
- Auto-memory leakage (discovered 2026-07-27): Claude Code persists per-directory
  memory across sessions, so a "fresh" session launched in a directory where a
  prior entrant played can silently recall that entrant's saved lessons at turn
  one. This voided a Fable 5 cold attempt (it recalled Opus 5's seed notes
  before its first action; journal kept as
  `runs/fable5-journal-VOID-contaminated.md`). Countermeasures now standard:
  every cold run launches from a fresh, never-used working directory under
  `arena/` (memory is scoped to the exact directory path; the prompt's absolute
  paths make cwd irrelevant to play); the bench folder's own memory store is
  quarantined; and the post-run blindness audit must also verify the transcript
  contains zero memory recalls. Timeline audit of prior results: both leaked
  memory files were written 7/25-7/26 by Opus 5's own session, so Opus 5's cold
  run (7/24) and all Opus 4.8 runs (7/13) predate them and remain clean.
- Coaching: the instructions contain zero strategy.
- Seed foreknowledge: only the seed string is given; contents are unknown.
- Knowing-it-is-public bias: not disclosed before the run, so play is natural;
  consent is obtained afterward, before anything is shared.
- Self-report inflation: the score is read from the game, not the agent.
- Retry contamination (learning runs): the only added context is the model's own
  prior journal, documented per run.

## Harness changes affecting comparability

- 2026-08-09: `sell` now also works while a booster pack is open (commit
  `f7be2b9`). Before this, the harness wrongly rejected it — a restriction the
  real game does not have — and every entrant through Opus 5's seed-only run
  lost at least one pack pick to it at full joker slots (it appears in the
  journals as a learned "game rule"). Runs before this date played under the
  stricter gate; treat cross-date comparisons of pack decisions accordingly.

## Known limitations

- One seed is one deal. A seed-rotation version would be more robust; treat a
  single run as a single, high-variance data point.
- The model's innate Balatro knowledge differs by model. That is part of what is
  measured, not a flaw.
- A very long run can strain a subagent's context. The harness compacts context,
  but a truncated run is simply scored where it ended.
- Bot-mode cosmetics (muted, fast) differ from a human's client but do not change
  the deal or the scoring.
