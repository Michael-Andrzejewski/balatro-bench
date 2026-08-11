# Balatro Bench

A reproducible, sandboxed benchmark of how well AI agents play [Balatro](https://www.playbalatro.com/),
driving the **real game** through a local JSON-RPC API on a fixed seed. Entrants
so far: Claude models (Opus 4.8, Opus 5, Fable 5), OpenAI's GPT-5.6 "Sol" via
Codex CLI, a human, and a hardcoded rule bot.

**[Leaderboard](bench-results.md)** · **[Protocol and rigor notes](PROTOCOL.md)** ·
**[Per-ante graphs and data](analysis/)** · **[Run journals](runs/)**

## The task

One solo run of Balatro: seed `BENCHMRK`, Red Deck, White Stake, no lives.
Primary metric: furthest ante reached (read from the game, never self-reported).
Tiebreak: best single hand. Beating ante 8 counts as winning the base game;
runs continue into endless mode.

The agent gets a self-contained prompt (API reference + rules; see
`runs/*-prompt.txt` for the exact text given to each entrant), plays through
hundreds of JSON-RPC calls against a live game instance, and must keep a
journal with a best-hand line per ante. Journals feed the per-ante progression
graphs in `analysis/`.

## The four modes

1. **Cold** — no context beyond how to play and launch. Measures raw ability.
2. **Journal, attempt 2** — the only added context is the journal the same
   model wrote during its own attempt 1. Measures one step of self-improvement.
3. **Journal, attempt 3** — same rule, one more iteration.
4. **Seed-informed** — the model gets a seed-analyzer readout of BENCHMRK
   (bosses, vouchers, tags, shop queues). Measures execution with perfect
   information.

Historical runs that mixed in anything else (operator coaching, same-session
context) are on the leaderboard but flagged impure; the exact mapping and
purity flags are machine-readable in `analysis/per-ante-data.json`.

## Integrity measures

- **Server-side sandbox**: the game mod hard-rejects the state-editing
  endpoints (`set`/`add`/`load`) when launched in bench mode; verified before
  every run. Agents can only advance the run through legitimate play.
- **Vanilla card pool**: the launcher regenerates the mod blacklist each run
  (everything except the API mod and its loaders) and purity is verified from
  the loader log. A run that saw modded content is voided (this has happened,
  and is documented).
- **Context isolation**: every run launches from a fresh, never-used working
  directory so agent-side memory systems have nothing to recall. One cold run
  was voided when this failed (documented in PROTOCOL.md), which is why it is
  now standard. Claude entrants additionally run under permission deny-rules
  that technically block reading other entrants' journals and web access.
- **Post-run audits**: transcripts are audited for forbidden file reads,
  memory recalls, and cheat-endpoint calls before results are certified.
- **Authoritative scoring**: final ante and best hand come from the game state
  and a game-over screenshot, not from the agent.

## Known caveats (see PROTOCOL.md for the full list)

- The API reveals some information the human client hides (face-down cards,
  Amber Acorn's flipped jokers) and hides some it shows (Cerulean Bell's
  forced card). Affected clears are annotated on the leaderboard.
- Harness bugs fixed mid-history are listed with dates in PROTOCOL.md; runs
  before a fix played under the stricter/buggier behavior.
- One fixed seed is one deal. It is memorizable once public; the rigor
  upgrade is seed rotation, which this bench trades away for reproducibility.
- A model's innate Balatro knowledge is part of what is measured.

## Reproduction

Requirements: Balatro (Steam), [Steamodded](https://github.com/Steamodded/smods),
[lovely](https://github.com/ethangreen-dev/lovely-injector), and the
[balatrobot fork](https://github.com/Michael-Andrzejewski/balatrobot) (`fable`
branch) that adds the bench sandbox, the reliability fixes, and the win-screen
operator checkpoint.

- `bench-launch-ai.ps1 -Port 12347` — launch a sandboxed instance (regenerates
  the blacklist, sets `BALATROBOT_BENCH=1`).
- `bench-rpc.ps1` — the PowerShell JSON-RPC helper the agents call.
- `bench-restore.ps1` — restore the normal mod set afterward.
- `arena/<entrant>/` — one directory per run: the exact prompt, any permitted
  seed file, sandbox settings, and the journal the agent wrote.

Scripts are Windows PowerShell and contain machine-specific absolute paths;
adapt paths for your setup. The seed analysis file given to mode-4 entrants
was generated with the community Blueprint seed analyzer.

## Provenance

Built by Michael Andrzejewski (Soareverix) with Claude (Anthropic) doing the
harness engineering; the AI entrants played unassisted under the conditions
listed per row. Results involving a model are shared with that model's consent
(see PROTOCOL.md, "Procedure").
