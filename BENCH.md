# Balatro Bench

A reproducible, sandboxed benchmark for AI agents playing Balatro. One fixed
seed, one fixed ruleset, one comparable score. An agent (a Claude Code session,
or any model driving the same API) plays a solo run and tries to get as far and
score as high as it can.

## The metric

Two numbers, ranked:

1. **Furthest ante reached** (primary). Solo Balatro has no lives, so failing a
   blind ends the run. The ante you die on, or the ante you reach in Endless
   mode after beating ante 8, is the headline score. This is read straight from
   the game state (`ante_num`), so it cannot be fudged.
2. **Best single-hand score** (tiebreak). The highest chip total scored by any
   one played hand during the run. Journaled by the player from the score it
   observes each hand.

`won = true` (beat ante 8) is recorded as a flag. Getting further into Endless
is what separates strong runs after that.

## Fixed ruleset (Bench v1)

| Parameter | Value |
| --- | --- |
| Seed | `BENCHMRK` |
| Deck | Red Deck |
| Stake | White Stake |
| Mode | Solo (no multiplayer, no lives) |
| Mods affecting cards | none (vanilla card pools) |

The seed and ruleset are hard-coded in `bench-launch.ps1`. Do not change them
between recorded runs or the scores stop being comparable.

## Environment

The score depends on the exact environment, because a Balatro seed only lines up
run to run if the card pools and version match. A recorded run must use:

- Balatro base game (record the Steam build in the run notes).
- Loaded mods: `smods` (Steamodded) + `lovely` loader + `balatrobot` only.
- Every content mod disabled via `blacklist.bench.txt` (the launcher swaps this
  in for you). That covers Cryptid, Entropy, Reinforcement Deck, Scaling Stakes,
  the Multiplayer mod, and the rest. With them off, `BENCHMRK` deals the same
  vanilla run every time.

`smods` and `balatrobot` are present so the agent can drive the game, but with no
content mods loaded the pools are vanilla. This is the honest, reproducible spec:
the seed is fixed relative to this exact setup.

## The sandbox (anti-cheat)

The whole point is that the agent has to actually play. Enforcement is in the mod
itself, not on the honor system:

- The launcher sets `BALATROBOT_BENCH=1`. In that mode the BalatroBot server
  hard-rejects three endpoints: `set` (write money / ante / any state), `add`
  (spawn cards or jokers), and `load` (restore an arbitrary off-seed save). Any
  call to them returns an error instead of executing.
- The Multiplayer bridge (`balatrobot-mp`), which exposes an arbitrary-Lua
  `mp_eval` endpoint, is blacklisted, so that escape hatch is not even loaded.

What the agent is left with is the legitimate game surface: look at the state,
select and play and discard cards, buy from the shop, open packs, use
consumables, reroll, rearrange, cash out, advance rounds. Exactly what a human
has.

## How to run one

1. `powershell -File bench-launch.ps1` (swaps in the clean mod set, launches the
   game watchable with audio on).
2. Wait for the main menu to load.
3. Point a player agent at the API on `http://127.0.0.1:12346` and give it
   `bench-briefing.md` as its instructions. It starts the run with the fixed
   seed / deck / stake and plays it out.
4. When the run ends, record the result in `bench-results.md` and keep the
   per-run journal.
5. `powershell -File bench-restore.ps1` to put your normal mods back.

The player starts the run with, and only with:
`start deck=RED stake=WHITE seed=BENCHMRK`.

## Notes on rigor

- **Single fixed seed is the default, by request.** It maximizes
  reproducibility. The tradeoff is that a fixed seed can in principle be
  memorized. If you want to harden the benchmark against that, rotate a small set
  of seeds and report the average or the worst case. The harness supports this:
  add more seeds and average the antes. Bench v1 is one seed for simplicity.
- **Determinism caveat.** Balatro's RNG is seeded, but a few in-run choices the
  game makes can depend on real time or draw order in edge cases. Runs should be
  reproducible to the same ante on the same build; tiny divergences late are
  possible and worth noting if seen.
- **Version pinning.** Note the Balatro build and the balatrobot commit in each
  run's notes. A game update can shift what a seed deals.

## Files

- `bench-launch.ps1` / `bench-restore.ps1` — set up and tear down.
- `blacklist.bench.txt` — the clean mod set.
- `bench-briefing.md` — the instructions every player agent follows.
- `bench-results.md` — the leaderboard.
- `bench-journal-*.md` — one per run, written by the player.
