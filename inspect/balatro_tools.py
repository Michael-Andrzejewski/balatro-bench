"""Inspect tools for Balatro Bench.

A thin, typed layer over the balatrobot JSON-RPC API. Every tool returns the
compact game-state summary after the action, so the model never has to parse
raw JSON. The harness, not the model, measures the best single hand and
verifies the sandbox before the run starts.

Per-sample state lives in Inspect's store() under "balatro:*" keys:
  port, seed, deck, stake, started, sandbox_ok, best_hand, actions, plays, journal
"""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request
from typing import Any

from inspect_ai.tool import Tool, ToolError, tool
from inspect_ai.util import store

API_HOST = "127.0.0.1"
CHEAT_METHODS = ("set", "add", "load")
SCORING_STATES = ("SELECTING_HAND", "ROUND_EVAL", "HAND_PLAYED")


class ApiError(Exception):
    pass


# --------------------------------------------------------------------------
# RPC
# --------------------------------------------------------------------------

def rpc_sync(port: int, method: str, params: dict | None = None, timeout: int = 90) -> Any:
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    ).encode()
    req = urllib.request.Request(
        f"http://{API_HOST}:{port}", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    if data.get("error"):
        raise ApiError(data["error"].get("message", "unknown"))
    return data.get("result")


def _port() -> int:
    port = store().get("balatro:port")
    if port is None:
        raise ToolError("No game port is bound to this sample.")
    return int(port)


async def rpc(method: str, params: dict | None = None) -> Any:
    port = _port()
    try:
        return await asyncio.to_thread(rpc_sync, port, method, params)
    except ApiError as e:
        raise ToolError(f"{method}: {e}")
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        raise ToolError(f"Could not reach the game on port {port}: {e}")


async def gamestate_raw() -> dict:
    g = await rpc("gamestate")
    return g or {}


# --------------------------------------------------------------------------
# Compact summary (port of bench-rpc.ps1's formatting)
# --------------------------------------------------------------------------

def _card_str(c: dict) -> str:
    v = c.get("value") or {}
    m = c.get("modifier") or {}
    tags = []
    if m.get("enhancement"):
        tags.append(m["enhancement"])
    if m.get("edition"):
        tags.append(m["edition"])
    if m.get("seal"):
        tags.append(f"{m['seal']}SEAL")
    t = f"({','.join(tags)})" if tags else ""
    rank, suit = v.get("rank"), v.get("suit")
    if rank:
        return f"{rank}{suit}{t}"
    return f"{c.get('label', '?')}{t}"


def _cards(area: dict | None) -> list[dict]:
    return list(((area or {}).get("cards")) or [])


def summarize(g: dict) -> str:
    if not g:
        return "state=UNKNOWN (empty response)"
    lines = []
    paused = " PAUSED(waiting for operator)" if g.get("paused") else ""
    lines.append(
        f"state={g.get('state')} ante={g.get('ante_num')} round={g.get('round_num')} "
        f"money=${g.get('money')} won={g.get('won')}{paused}"
    )
    if g.get("post_run_interview"):
        lines.append(f"  OPERATOR REQUEST: {g['post_run_interview']}")
    rnd = g.get("round")
    if rnd:
        lines.append(
            f"  round: chips={rnd.get('chips')} hands_left={rnd.get('hands_left')} "
            f"discards_left={rnd.get('discards_left')} reroll=${rnd.get('reroll_cost')}"
        )
    blinds = g.get("blinds")
    if blinds:
        for b in (blinds.get("small"), blinds.get("big"), blinds.get("boss")):
            if b and b.get("status") == "CURRENT":
                lines.append(
                    f"  BLIND: {b.get('name')} [{b.get('type')}] target={b.get('score')} "
                    f"effect={b.get('effect')}"
                )
        if g.get("state") == "BLIND_SELECT":
            s, bg, bo = blinds.get("small") or {}, blinds.get("big") or {}, blinds.get("boss") or {}
            lines.append(
                f"  choices: SMALL {s.get('score')}(tag:{s.get('tag_name')}) | "
                f"BIG {bg.get('score')}(tag:{bg.get('tag_name')}) | "
                f"BOSS {bo.get('name')}: {bo.get('effect')}"
            )
    hand = _cards(g.get("hand"))
    if hand:
        lines.append("  HAND: " + "  ".join(f"{i}:{_card_str(c)}" for i, c in enumerate(hand)))
    jokers = g.get("jokers")
    jcards = _cards(jokers)
    if jcards:
        for i, c in enumerate(jcards):
            eff = (c.get("value") or {}).get("effect")
            lines.append(f"  JOKER {i}: {c.get('label')} [{c.get('key')}] {eff}")
    elif jokers:
        lines.append(f"  JOKERS: 0/{jokers.get('limit')}")
    for i, c in enumerate(_cards(g.get("consumables"))):
        lines.append(f"  CONSUMABLE {i}: {c.get('label')} - {(c.get('value') or {}).get('effect')}")
    if g.get("state") == "SHOP":
        for i, c in enumerate(_cards(g.get("shop"))):
            lines.append(
                f"  SHOP {i}: {c.get('label')} ${(c.get('cost') or {}).get('buy')} "
                f"[{c.get('set')}] {(c.get('value') or {}).get('effect')}"
            )
        for i, c in enumerate(_cards(g.get("vouchers"))):
            lines.append(
                f"  VOUCHER {i}: {c.get('label')} ${(c.get('cost') or {}).get('buy')} "
                f"{(c.get('value') or {}).get('effect')}"
            )
        for i, c in enumerate(_cards(g.get("packs"))):
            lines.append(f"  PACK {i}: {c.get('label')} ${(c.get('cost') or {}).get('buy')}")
    if g.get("state") == "SMODS_BOOSTER_OPENED":
        for i, c in enumerate(_cards(g.get("pack"))):
            lines.append(
                f"  PACKCARD {i}: {_card_str(c)} [{c.get('set')}] {(c.get('value') or {}).get('effect')}"
            )
    hands = g.get("hands")
    if isinstance(hands, dict) and hands and g.get("state") == "SELECTING_HAND":
        lv = []
        for name, h in hands.items():
            if isinstance(h, dict) and h.get("level", 1) not in (None, 1):
                lv.append(f"{name} L{h.get('level')}")
        if lv:
            lines.append("  LEVELS: " + ", ".join(lv))
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

async def _act(method: str, params: dict | None = None) -> str:
    """Run an action, then return the fresh compact state."""
    s = store()
    await rpc(method, params)
    s.set("balatro:actions", s.get("balatro:actions", 0) + 1)
    g = await gamestate_raw()
    return summarize(g)


def _chips(g: dict) -> int:
    try:
        return int((g.get("round") or {}).get("chips") or 0)
    except (TypeError, ValueError):
        return 0


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------

@tool
def gamestate() -> Tool:
    async def execute(raw: bool = False) -> str:
        """Read the current game state. Call this before every decision; indices shift after every action.

        Args:
            raw: Return the full JSON state instead of the compact summary.
        """
        g = await gamestate_raw()
        return json.dumps(g, indent=1) if raw else summarize(g)

    return execute


@tool
def start_run() -> Tool:
    async def execute() -> str:
        """Start the benchmark run. The deck, stake and seed are fixed by the harness; call this exactly once, from the main menu."""
        s = store()
        if s.get("balatro:started"):
            raise ToolError("The run has already been started.")
        # Sandbox check: every state-editing endpoint must be rejected by the server.
        for m in CHEAT_METHODS:
            try:
                await rpc(m, {})
            except ToolError as e:
                if "disabled" in str(e).lower() or "bench" in str(e).lower():
                    continue
                s.set("balatro:sandbox_ok", False)
                raise ToolError(f"Sandbox check failed: `{m}` returned '{e}' instead of a bench-mode refusal.")
            s.set("balatro:sandbox_ok", False)
            raise ToolError(f"Sandbox check failed: `{m}` succeeded; this instance is not in bench mode.")
        s.set("balatro:sandbox_ok", True)
        params = {
            "deck": s.get("balatro:deck", "RED"),
            "stake": s.get("balatro:stake", "WHITE"),
            "seed": s.get("balatro:seed", "BENCHMRK"),
        }
        out = await _act("start", params)
        s.set("balatro:started", True)
        return out

    return execute


@tool
def select_blind() -> Tool:
    async def execute() -> str:
        """Play the blind currently on deck (valid in BLIND_SELECT)."""
        return await _act("select")

    return execute


@tool
def skip_blind() -> Tool:
    async def execute() -> str:
        """Skip a Small or Big blind and take its tag instead (valid in BLIND_SELECT; the Boss cannot be skipped)."""
        return await _act("skip")

    return execute


@tool
def play_hand() -> Tool:
    async def execute(cards: list[int]) -> str:
        """Play the given hand cards as a poker hand (valid in SELECTING_HAND).

        Args:
            cards: 0-based indices into the HAND list from the latest gamestate (1 to 5 cards).
        """
        if not cards or len(cards) > 5:
            raise ToolError("Play between 1 and 5 cards.")
        s = store()
        before = _chips(await gamestate_raw())
        await rpc("play", {"cards": list(cards)})
        s.set("balatro:actions", s.get("balatro:actions", 0) + 1)
        s.set("balatro:plays", s.get("balatro:plays", 0) + 1)
        g = await gamestate_raw()
        if g.get("state") in SCORING_STATES:
            delta = _chips(g) - before
            if delta > s.get("balatro:best_hand", 0):
                s.set("balatro:best_hand", delta)
                s.set("balatro:best_hand_ante", g.get("ante_num"))
        return summarize(g)

    return execute


@tool
def discard() -> Tool:
    async def execute(cards: list[int]) -> str:
        """Discard the given hand cards and redraw (valid in SELECTING_HAND).

        Args:
            cards: 0-based indices into the HAND list from the latest gamestate (1 to 5 cards).
        """
        if not cards or len(cards) > 5:
            raise ToolError("Discard between 1 and 5 cards.")
        return await _act("discard", {"cards": list(cards)})

    return execute


@tool
def use_consumable() -> Tool:
    async def execute(consumable: int, cards: list[int] | None = None) -> str:
        """Use a tarot, planet or spectral card (valid in SELECTING_HAND or SHOP).

        Args:
            consumable: 0-based index into the CONSUMABLE list.
            cards: Hand-card indices the consumable targets, if it needs targets.
        """
        params: dict[str, Any] = {"consumable": consumable}
        if cards:
            params["cards"] = list(cards)
        return await _act("use", params)

    return execute


@tool
def buy() -> Tool:
    async def execute(card: int | None = None, voucher: int | None = None, pack: int | None = None) -> str:
        """Buy one shop item (valid in SHOP). Pass exactly one of card, voucher or pack.

        Args:
            card: 0-based index into the SHOP list.
            voucher: 0-based index into the VOUCHER list.
            pack: 0-based index into the PACK list.
        """
        chosen = {k: v for k, v in (("card", card), ("voucher", voucher), ("pack", pack)) if v is not None}
        if len(chosen) != 1:
            raise ToolError("Pass exactly one of card, voucher or pack.")
        return await _act("buy", chosen)

    return execute


@tool
def pack_pick() -> Tool:
    async def execute(card: int | None = None, skip: bool = False, cards: list[int] | None = None) -> str:
        """Pick a card from an opened booster pack, or skip the pack.

        Args:
            card: 0-based index into the PACKCARD list.
            skip: Skip the pack instead of picking.
            cards: Hand-card targets, when the picked consumable needs them.
        """
        if skip:
            params: dict[str, Any] = {"skip": True}
        elif card is not None:
            params = {"card": card}
            if cards:
                params["cards"] = list(cards)
        else:
            raise ToolError("Pass a card index or skip=true.")
        return await _act("pack", params)

    return execute


@tool
def sell() -> Tool:
    async def execute(joker: int | None = None, consumable: int | None = None) -> str:
        """Sell a joker or a consumable for money (valid in SELECTING_HAND or SHOP).

        Args:
            joker: 0-based index into the JOKER list.
            consumable: 0-based index into the CONSUMABLE list.
        """
        chosen = {k: v for k, v in (("joker", joker), ("consumable", consumable)) if v is not None}
        if len(chosen) != 1:
            raise ToolError("Pass exactly one of joker or consumable.")
        return await _act("sell", chosen)

    return execute


@tool
def rearrange() -> Tool:
    async def execute(
        hand: list[int] | None = None,
        jokers: list[int] | None = None,
        consumables: list[int] | None = None,
    ) -> str:
        """Reorder the hand, the jokers, or the consumables (joker order matters for some effects).

        Args:
            hand: New order of hand indices.
            jokers: New order of joker indices.
            consumables: New order of consumable indices.
        """
        chosen = {k: list(v) for k, v in (("hand", hand), ("jokers", jokers), ("consumables", consumables)) if v}
        if len(chosen) != 1:
            raise ToolError("Pass exactly one of hand, jokers or consumables.")
        return await _act("rearrange", chosen)

    return execute


@tool
def reroll() -> Tool:
    async def execute() -> str:
        """Reroll the shop for its current cost (valid in SHOP)."""
        return await _act("reroll")

    return execute


@tool
def cash_out() -> Tool:
    async def execute() -> str:
        """Collect the round's rewards (valid in ROUND_EVAL)."""
        return await _act("cash_out")

    return execute


@tool
def next_round() -> Tool:
    async def execute() -> str:
        """Leave the shop and go to the next blind selection (valid in SHOP)."""
        return await _act("next_round")

    return execute


@tool
def journal() -> Tool:
    async def execute(note: str) -> str:
        """Append a note to your run journal: build plan, key decisions, per-ante progress, lessons.

        Args:
            note: The note to record.
        """
        s = store()
        entries = list(s.get("balatro:journal", []))
        entries.append({"n": len(entries) + 1, "ante": s.get("balatro:last_ante"), "note": note})
        s.set("balatro:journal", entries)
        return f"Journal entry {len(entries)} recorded."

    return execute


def player_tools() -> list[Tool]:
    return [
        gamestate(),
        start_run(),
        select_blind(),
        skip_blind(),
        play_hand(),
        discard(),
        use_consumable(),
        buy(),
        pack_pick(),
        sell(),
        rearrange(),
        reroll(),
        cash_out(),
        next_round(),
        journal(),
    ]
