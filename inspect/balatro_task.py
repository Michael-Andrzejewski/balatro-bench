"""Balatro Bench as an Inspect task.

One sample = one solo run of Balatro on a fixed seed, driven through the
sandboxed balatrobot API. The score is the furthest ante reached, read from
the game; the best single hand (tiebreak) is measured by the harness from
round chips before and after each play, never self-reported.

Usage (game already launched in bench mode, see README.md):

    inspect eval balatro_task.py --model anthropic/claude-opus-4-8 -T ports=12347

Modes mirror the original bench: cold (default), or pass a context file for
the journal / seed-informed modes:

    inspect eval balatro_task.py -T mode=seed-informed -T context_file=../arena/sol-seedonly/seed.md
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.agent import AgentPrompt, react
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import CompactionSummary
from inspect_ai.scorer import Metric, SampleScore, Score, Target, mean, metric, scorer
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.util import store

from balatro_tools import gamestate_raw, player_tools, rpc_sync, summarize

HERE = Path(__file__).parent

PLAYER_INSTRUCTIONS = """\
You are playing ONE run of Balatro for a benchmark. Play as well as you possibly can.

## Goal
Reach the highest ante you can, and score as high as you can. This is SOLO Balatro: there are NO lives, so if you ever fail to meet a blind's chip requirement, the run ends immediately. Getting further (higher ante) matters most; your single biggest hand is the tiebreak. Beating ante 8 wins the base game; keep playing into Endless mode after that.

## How you play
You drive the real running game through the tools provided. Each action tool returns the compact game state after the action. Call `gamestate` whenever you need to re-read the board before deciding; indices are 0-based into the lists shown (HAND, JOKER, CONSUMABLE, SHOP, VOUCHER, PACK, PACKCARD) and positions shift after every action, so re-read before indexing.

Begin by calling `start_run` once. The deck, stake and seed are fixed by the harness.

The flow: start_run -> BLIND_SELECT -> select_blind (or skip_blind for Small/Big) -> SELECTING_HAND -> play_hand / discard until the blind's chip target is met -> ROUND_EVAL -> cash_out -> SHOP -> buy / reroll / use_consumable / sell / pack_pick -> next_round -> repeat. The Boss is the third round of each ante and cannot be skipped; read its effect before selecting it.

## Rules
- Play legitimately only. State-editing endpoints are disabled by the server; do not try to work around that.
- Everything you need is in these instructions and the live game state. This is a blind run unless a context section is provided below.

## Journal
Use the `journal` tool to record your build plan, key decisions with reasoning, per-ante progress, and your best single hand as you go. At the end, record a post-mortem: final ante, best single hand, exactly what ended the run, and concrete lessons for a future attempt on this seed.

## Efficiency
A full run is long. Be decisive, keep your reasoning tight, and rely on the compact state rather than raw state. Make strong plays; do not narrate more than you need to.

## Ending
Play until the game reaches GAME_OVER. Then call `gamestate` one last time, write your post-mortem to the journal, and call `submit` with a single line exactly in this format:

    RESULT ante=<number> best_hand=<number> won=<true|false>
"""


def _split(csv: str | list[str]) -> list[str]:
    if isinstance(csv, list):
        return [str(x) for x in csv]
    return [x.strip() for x in str(csv).split(",") if x.strip()]


# --------------------------------------------------------------------------
# Setup solver: bind the sample's game instance into the store
# --------------------------------------------------------------------------

@solver
def bind_game() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        s = store()
        md = state.metadata
        s.set("balatro:port", int(md["port"]))
        s.set("balatro:seed", md["seed"])
        s.set("balatro:deck", md["deck"])
        s.set("balatro:stake", md["stake"])
        s.set("balatro:best_hand", 0)
        s.set("balatro:actions", 0)
        s.set("balatro:plays", 0)
        s.set("balatro:journal", [])
        # The instance must be at the main menu; refuse to play over someone else's run.
        try:
            g = await asyncio.to_thread(rpc_sync, int(md["port"]), "gamestate")
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"Game on port {md['port']} is unreachable: {e}")
        if (g or {}).get("state") != "MENU":
            raise RuntimeError(
                f"Game on port {md['port']} is at state {(g or {}).get('state')}, not MENU. "
                "Launch a fresh bench instance per sample."
            )
        return state

    return solve


# --------------------------------------------------------------------------
# Scripted player: a no-LLM smoke-test solver that plays the first five cards
# --------------------------------------------------------------------------

@solver
def scripted_player(max_actions: int = 400) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        names = [
            "gamestate", "start_run", "select_blind", "skip_blind", "play_hand", "discard",
            "use_consumable", "buy", "pack_pick", "sell", "rearrange", "reroll", "cash_out",
            "next_round", "journal",
        ]
        t = dict(zip(names, player_tools()))
        await t["start_run"]()
        for _ in range(max_actions):
            g = await gamestate_raw()
            st = g.get("state")
            if st == "GAME_OVER":
                break
            if st == "BLIND_SELECT":
                await t["select_blind"]()
            elif st == "SELECTING_HAND":
                n = min(5, len(((g.get("hand") or {}).get("cards")) or []))
                if n == 0:
                    break
                await t["play_hand"](cards=list(range(n)))
            elif st == "ROUND_EVAL":
                await t["cash_out"]()
            elif st == "SHOP":
                await t["next_round"]()
            elif st == "SMODS_BOOSTER_OPENED":
                await t["pack_pick"](card=0)
            else:
                await asyncio.sleep(0.5)
        await t["journal"](note="scripted player: played the first five cards every hand")
        state.output.completion = "scripted"
        return state

    return solve


# --------------------------------------------------------------------------
# Scorer and metrics
# --------------------------------------------------------------------------

@metric
def max_ante() -> Metric:
    def m(scores: list[SampleScore]) -> float:
        vals = [float(s.score.value) for s in scores if isinstance(s.score.value, (int, float))]
        return max(vals) if vals else 0.0

    return m


@metric
def best_hand() -> Metric:
    def m(scores: list[SampleScore]) -> float:
        vals = [float((s.score.metadata or {}).get("best_hand", 0)) for s in scores]
        return max(vals) if vals else 0.0

    return m


@metric
def win_rate() -> Metric:
    def m(scores: list[SampleScore]) -> float:
        if not scores:
            return 0.0
        return sum(1.0 for s in scores if (s.score.metadata or {}).get("won")) / len(scores)

    return m


@scorer(metrics=[mean(), max_ante(), best_hand(), win_rate()])
def balatro_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        s = store()
        port = int(s.get("balatro:port"))
        try:
            g = await asyncio.to_thread(rpc_sync, port, "gamestate") or {}
        except Exception as e:  # noqa: BLE001
            g = {"state": f"UNREACHABLE ({e})"}
        ante = int(g.get("ante_num") or 0)
        won = bool(g.get("won"))
        best = int(s.get("balatro:best_hand", 0))
        final_state = g.get("state")
        invalid = None
        if not s.get("balatro:started"):
            invalid = "run never started"
        elif not s.get("balatro:sandbox_ok"):
            invalid = "sandbox check failed"
        md = {
            "best_hand": best,
            "best_hand_ante": s.get("balatro:best_hand_ante"),
            "won": won,
            "final_state": final_state,
            "game_over": final_state == "GAME_OVER",
            "sandbox_verified": bool(s.get("balatro:sandbox_ok")),
            "actions": s.get("balatro:actions", 0),
            "plays": s.get("balatro:plays", 0),
            "journal": s.get("balatro:journal", []),
            "self_report": (state.output.completion or "").strip()[-300:],
            "invalid": invalid,
            "seed": s.get("balatro:seed"),
            "final_summary": summarize(g) if isinstance(g, dict) and g.get("ante_num") else None,
        }
        value = 0 if invalid else ante
        answer = f"RESULT ante={ante} best_hand={best} won={str(won).lower()}"
        expl = (
            f"{'INVALID: ' + invalid + '. ' if invalid else ''}"
            f"Final state {final_state}; ante {ante} read from the game; "
            f"best hand {best} measured by the harness over {md['plays']} plays."
        )
        return Score(value=value, answer=answer, explanation=expl, metadata=md)

    return score


# --------------------------------------------------------------------------
# Task
# --------------------------------------------------------------------------

@task
def balatro_bench(
    seed: str = "BENCHMRK",
    deck: str = "RED",
    stake: str = "WHITE",
    ports: str = "12347",
    mode: str = "cold",
    context_file: str | None = None,
    message_limit: int = 3000,
    compaction: bool = True,
    player: str = "react",
) -> Task:
    """Balatro Bench: one solo run per seed on a sandboxed game instance.

    Args:
        seed: Seed or comma-separated seeds (one sample each).
        deck: Deck name (RED).
        stake: Stake name (WHITE).
        ports: Comma-separated JSON-RPC ports, one launched bench instance per sample
            (samples are assigned round-robin; set max_samples to the number of ports).
        mode: Label recorded in the log: cold | journal | seed-informed.
        context_file: Optional file whose text is appended to the prompt verbatim
            (a prior journal for the journal modes, a seed readout for seed-informed).
        message_limit: Hard cap on conversation messages per sample.
        compaction: Summarize old messages when the context fills (the system
            instructions always survive).
        player: "react" for the LLM agent, "scripted" for the no-LLM smoke test.
    """
    seeds = _split(seed)
    port_list = _split(ports)
    context = ""
    if context_file:
        text = Path(context_file).read_text(encoding="utf-8")
        context = f"\n\n## Context provided for this run ({mode})\n\n{text}\n"

    samples = [
        Sample(
            id=f"{sd}-{i}",
            input=PLAYER_INSTRUCTIONS + context,
            target=str(8),  # winning the base game; informational only
            metadata={
                "seed": sd,
                "deck": deck,
                "stake": stake,
                "port": int(port_list[i % len(port_list)]),
                "mode": mode,
                "context_file": context_file,
            },
        )
        for i, sd in enumerate(seeds)
    ]

    if player == "scripted":
        play: Solver = scripted_player()
    else:
        play = react(
            name="balatro_player",
            prompt=AgentPrompt(
                instructions=PLAYER_INSTRUCTIONS + context,
                assistant_prompt=None,
                submit_prompt="\nWhen the game reaches GAME_OVER, call {submit}() with the RESULT line.\n",
            ),
            tools=player_tools(),
            attempts=1,
            compaction=CompactionSummary(threshold=0.85) if compaction else None,
        )

    return Task(
        dataset=MemoryDataset(samples),
        setup=bind_game(),
        solver=play,
        scorer=balatro_scorer(),
        message_limit=message_limit,
        name="balatro_bench",
        version=1,
        metadata={"mode": mode, "protocol": "PROTOCOL.md v1", "seed_fixed_by_harness": True},
    )
