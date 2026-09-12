# Balatro Bench on Inspect

The same benchmark as the repo root, ported to the
[Inspect](https://inspect.aisi.org.uk/) evaluation framework. One sample is one
solo run of Balatro on a fixed seed, driven through the sandboxed balatrobot
JSON-RPC API by an Inspect agent with typed tools. The score is the furthest
ante reached, read from the game.

## What the port changes

| | Original bench | Inspect port |
| --- | --- | --- |
| Player | Claude Code / Codex session calling a PowerShell RPC helper | Inspect `react` agent with one typed tool per endpoint |
| Best single hand | Journaled by the model from what it observed | Measured by the harness from `round.chips` before and after every `play_hand` |
| Seed / deck / stake | In the prompt; the model passes them to `start` | Fixed by the harness; `start_run` takes no arguments |
| Sandbox check | Operator verifies `set`/`add`/`load` are refused before the run | `start_run` verifies all three and the run is scored invalid if any succeeds |
| Journal | A markdown file the model writes | A `journal` tool; entries land in the sample's score metadata |
| Transcript | Session logs, audited by hand | Inspect `.eval` log: every tool call, argument and result; `inspect view` |
| Long runs | Claude Code's own compaction | `CompactionSummary`; the instructions are the system prompt and survive |
| Multiple seeds | Not supported | `-T seed=A,B,C` with one launched instance per seed |

The metric, ruleset, and anti-cheat design are unchanged from `PROTOCOL.md`.

## Setup

```powershell
pip install inspect-ai
# one launched, sandboxed game instance per sample (see the repo README):
powershell -ExecutionPolicy Bypass -File ..\bench-launch-ai.ps1 -Port 12347
```

Wait for the main menu. The task refuses to start unless the instance is at `MENU`.

Set the model key in the environment (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, ...);
never commit it.

## Run

Cold mode (no context beyond how to play):

```powershell
cd inspect
inspect eval balatro_task.py --model anthropic/claude-opus-4-8 -T ports=12347
inspect view
```

Journal or seed-informed modes append a file to the prompt verbatim:

```powershell
inspect eval balatro_task.py --model anthropic/claude-opus-4-8 -T ports=12347 `
  -T mode=journal -T context_file=../runs/opus-run1-journal.md
inspect eval balatro_task.py --model openai/gpt-5.6 -T ports=12347 `
  -T mode=seed-informed -T context_file=../arena/sol-seedonly/seed.md
```

Several seeds at once, one instance each:

```powershell
inspect eval balatro_task.py --model anthropic/claude-opus-4-8 `
  -T seed=BENCHMRK,SEED2 -T ports=12346,12347 --max-samples 2
```

Task options (`-T name=value`): `seed`, `deck`, `stake`, `ports`, `mode`,
`context_file`, `message_limit` (default 3000), `compaction` (default true),
`player` (`react` or `scripted`).

## Scoring

`balatro_scorer` reads the final `gamestate` from the API:

- **value**: `ante_num` (0 if the run never started or the sandbox check failed)
- **answer**: `RESULT ante=N best_hand=N won=true|false`, the bench's standard line
- **metadata**: `best_hand`, `best_hand_ante`, `won`, `final_state`, `game_over`,
  `sandbox_verified`, `actions`, `plays`, `journal`, `self_report`, `invalid`

Metrics across samples: `mean` ante, `max_ante`, `best_hand`, `win_rate`.

## Test without the game or a model

`mock_game.py` is a fake server that walks the same state machine, refuses the
cheat endpoints, and dies on the ante-3 boss. `test_harness.py` runs the
scripted no-LLM player through it end to end and checks the scorer:

```powershell
python test_harness.py
```

The scripted player (`-T player=scripted`) also works against the real game
as a smoke test of the API; it plays the first five cards every hand and dies
early.

## Files

- `balatro_tools.py`: RPC client, compact state summary, the tools.
- `balatro_task.py`: task, setup solver, scripted player, scorer, metrics.
- `mock_game.py`: offline fake server.
- `test_harness.py`: offline tests.
