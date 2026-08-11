"""Balatro rule bot: plays a full run through the balatrobot JSON-RPC API
using only hardcoded, statistical decision rules. No LLM anywhere.

Usage:
    python rulebot.py [--port 12347] [--seed BENCHMRK] [--deck RED]
                      [--stake WHITE] [--resume] [--delay 0.0]

Safety: refuses to act unless the game is at MENU (fresh run) or --resume
is passed. Never calls set/add/load. Never skips packs (known desync risk);
skip is only a last-resort fallback after pick attempts fail.
"""

import argparse
import itertools
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

# ==========================================================================
# Constants
# ==========================================================================

RANK_CHIPS = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "T": 10, "J": 10, "Q": 10, "K": 10, "A": 11,
}
RANK_ORDER = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14,
}
FACE_RANKS = {"J", "Q", "K"}

# Additive joker effects applied when estimating a play.
# Each entry: key -> function(ctx) -> (chips_delta, mult_delta, xmult_factor)
# ctx fields: scoring (list of Card), played (list of Card), held (list of Card),
#             hand_name (str), n_played (int), hands_left (int),
#             played_this_round (dict name->int), n_jokers (int), deck_left (int),
#             money (int)


def _per_scoring(pred, chips=0, mult=0):
    def fn(ctx):
        n = sum(1 for c in ctx["scoring"] if not c.debuff and pred(c))
        return (chips * n, mult * n, 1.0)
    return fn


def _if_contains(hand_names, chips=0, mult=0, xmult=1.0):
    # Balatro "contains" jokers: a Full House contains a Pair, Two Pair, and
    # Three of a Kind; keep a simple containment map.
    contains = {
        "Pair": {"Pair", "Two Pair", "Three of a Kind", "Full House",
                 "Four of a Kind", "Flush House", "Five of a Kind", "Flush Five"},
        "Two Pair": {"Two Pair", "Full House", "Flush House"},
        "Three of a Kind": {"Three of a Kind", "Full House", "Four of a Kind",
                            "Flush House", "Five of a Kind", "Flush Five"},
        "Four of a Kind": {"Four of a Kind", "Five of a Kind", "Flush Five"},
        "Straight": {"Straight", "Straight Flush"},
        "Flush": {"Flush", "Straight Flush", "Flush House", "Flush Five"},
    }
    allowed = set()
    for h in hand_names:
        allowed |= contains.get(h, {h})

    def fn(ctx):
        if ctx["hand_name"] in allowed:
            return (chips, mult, xmult)
        return (0, 0, 1.0)
    return fn


JOKER_EFFECTS = {
    "j_joker": lambda ctx: (0, 4, 1.0),
    "j_greedy_joker": _per_scoring(lambda c: c.suit == "D", mult=3),
    "j_lusty_joker": _per_scoring(lambda c: c.suit == "H", mult=3),
    "j_wrathful_joker": _per_scoring(lambda c: c.suit == "S", mult=3),
    "j_gluttenous_joker": _per_scoring(lambda c: c.suit == "C", mult=3),
    "j_jolly": _if_contains(["Pair"], mult=8),
    "j_zany": _if_contains(["Three of a Kind"], mult=12),
    "j_mad": _if_contains(["Two Pair"], mult=10),
    "j_crazy": _if_contains(["Straight"], mult=12),
    "j_droll": _if_contains(["Flush"], mult=10),
    "j_sly": _if_contains(["Pair"], chips=50),
    "j_wily": _if_contains(["Three of a Kind"], chips=100),
    "j_clever": _if_contains(["Two Pair"], chips=80),
    "j_devious": _if_contains(["Straight"], chips=100),
    "j_crafty": _if_contains(["Flush"], chips=80),
    "j_half": lambda ctx: (0, 20, 1.0) if ctx["n_played"] <= 3 else (0, 0, 1.0),
    "j_abstract": lambda ctx: (0, 3 * ctx["n_jokers"], 1.0),
    "j_misprint": lambda ctx: (0, 11, 1.0),  # expected value of 0-23
    "j_fibonacci": _per_scoring(lambda c: c.rank in {"A", "2", "3", "5", "8"}, mult=8),
    "j_scary_face": _per_scoring(lambda c: c.rank in FACE_RANKS, chips=30),
    "j_even_steven": _per_scoring(lambda c: c.rank in {"2", "4", "6", "8", "T"}, mult=4),
    "j_odd_todd": _per_scoring(lambda c: c.rank in {"A", "3", "5", "7", "9"}, chips=31),
    "j_scholar": _per_scoring(lambda c: c.rank == "A", chips=20, mult=4),
    "j_walkie_talkie": _per_scoring(lambda c: c.rank in {"T", "4"}, chips=10, mult=4),
    "j_smiley": _per_scoring(lambda c: c.rank in FACE_RANKS, mult=5),
    "j_photograph": lambda ctx: (0, 0, 2.0) if any(
        c.rank in FACE_RANKS and not c.debuff for c in ctx["scoring"]) else (0, 0, 1.0),
    "j_baron": lambda ctx: (0, 0, 1.5 ** sum(
        1 for c in ctx["held"] if c.rank == "K" and not c.debuff)),
    "j_blackboard": lambda ctx: (0, 0, 3.0) if all(
        c.suit in {"S", "C"} or c.enhancement == "WILD" for c in ctx["held"]) or not ctx["held"]
        else (0, 0, 1.0),
    "j_duo": _if_contains(["Pair"], xmult=2.0),
    "j_trio": _if_contains(["Three of a Kind"], xmult=3.0),
    "j_family": _if_contains(["Four of a Kind"], xmult=4.0),
    "j_order": _if_contains(["Straight"], xmult=3.0),
    "j_tribe": _if_contains(["Flush"], xmult=2.0),
    "j_cavendish": lambda ctx: (0, 0, 3.0),
    "j_card_sharp": lambda ctx: (0, 0, 3.0)
        if ctx["played_this_round"].get(ctx["hand_name"], 0) > 0 else (0, 0, 1.0),
    "j_acrobat": lambda ctx: (0, 0, 3.0) if ctx["hands_left"] == 1 else (0, 0, 1.0),
    "j_blue_joker": lambda ctx: (2 * ctx["deck_left"], 0, 1.0),
    "j_bull": lambda ctx: (2 * max(0, ctx["money"]), 0, 1.0),
    "j_stuntman": lambda ctx: (250, 0, 1.0),
    "j_arrowhead": _per_scoring(lambda c: c.suit == "S", chips=50),
    "j_onyx_agate": _per_scoring(lambda c: c.suit == "C", mult=7),
    "j_rough_gem": lambda ctx: (0, 0, 1.0),  # money, not score
    "j_bloodstone": _per_scoring(lambda c: c.suit == "H", mult=0),  # chance xmult; ignore
}

# Shop priority overrides by joker key: known strong buys get a boost.
SHOP_KEY_BONUS = {
    "j_blueprint": 80, "j_brainstorm": 80, "j_baron": 70,
    "j_duo": 40, "j_trio": 40, "j_family": 40, "j_order": 40, "j_tribe": 40,
    "j_cavendish": 40, "j_acrobat": 30, "j_throwback": 30, "j_card_sharp": 30,
    "j_hologram": 40, "j_constellation": 40, "j_steel_joker": 30,
    "j_glass": 30, "j_vampire": 30, "j_obelisk": 30, "j_lucky_cat": 25,
    "j_ancient": 40, "j_idol": 30, "j_photograph": 25,
    "j_supernova": 20, "j_green_joker": 15, "j_ride_the_bus": 15,
    "j_abstract": 10, "j_fortune_teller": 10,
    "j_bootstraps": 15, "j_stuntman": 25,
    "j_egg": -20, "j_ice_cream": -10, "j_popcorn": -5, "j_gros_michel": 5,
    "j_credit_card": -15, "j_marble": -10, "j_stencil": -10,
    "j_8_ball": -10, "j_splash": -15, "j_chaos": -5,
    "j_mr_bones": -20,  # solo bench: a saved loss still ends the entry
}

BOSS_HANDLED = {
    "The Psychic", "The Eye", "The Mouth", "The Ox", "The Flint",
    "The Arm", "Verdant Leaf", "Cerulean Bell",
}


# ==========================================================================
# Card model and parsing
# ==========================================================================

class Card:
    __slots__ = ("idx", "rank", "suit", "enhancement", "edition", "seal",
                 "debuff", "hidden", "highlight", "label")

    def __init__(self, idx, raw):
        value = raw.get("value") or {}
        mod = raw.get("modifier") or {}
        state = raw.get("state") or {}
        self.idx = idx
        self.rank = value.get("rank")
        self.suit = value.get("suit")
        self.enhancement = mod.get("enhancement")
        self.edition = mod.get("edition")
        self.seal = mod.get("seal")
        self.debuff = bool(state.get("debuff"))
        self.hidden = bool(state.get("hidden"))
        self.highlight = bool(state.get("highlight"))
        self.label = raw.get("label", "")

    @property
    def is_stone(self):
        return self.enhancement == "STONE"

    @property
    def is_wild(self):
        return self.enhancement == "WILD" and not self.debuff

    def __repr__(self):
        r = self.rank or "?"
        s = self.suit or "?"
        e = f"({self.enhancement})" if self.enhancement else ""
        return f"{r}{s}{e}"


def parse_cards(area):
    cards = (area or {}).get("cards") or []
    return [Card(i, raw) for i, raw in enumerate(cards)]


# ==========================================================================
# Poker hand classification
# ==========================================================================

def classify(cards):
    """Classify a played selection. Returns (hand_name, scoring_cards).

    Stone cards have no rank/suit: they never shape the hand but always score.
    Wild cards count as any suit for flushes.
    """
    stones = [c for c in cards if c.is_stone]
    real = [c for c in cards if not c.is_stone and c.rank]

    if not real:
        return "High Card", list(stones)

    ranks = {}
    for c in real:
        ranks.setdefault(c.rank, []).append(c)
    counts = sorted((len(v) for v in ranks.values()), reverse=True)

    is5 = len(real) == 5
    # Flush: 5 cards, wilds count as any suit
    flush = False
    if is5:
        suits = {}
        wilds = 0
        for c in real:
            if c.is_wild:
                wilds += 1
            elif c.suit:
                suits[c.suit] = suits.get(c.suit, 0) + 1
        flush = (max(suits.values()) if suits else 0) + wilds >= 5

    # Straight: 5 distinct consecutive ranks (ace high or low)
    straight = False
    if is5 and len(ranks) == 5:
        vals = sorted(RANK_ORDER[r] for r in ranks)
        straight = vals[-1] - vals[0] == 4
        if not straight and vals == [2, 3, 4, 5, 14]:
            straight = True

    def group_cards(min_count):
        out = []
        for r, cs in ranks.items():
            if len(cs) >= min_count:
                out.extend(cs)
        return out

    if counts[0] == 5:
        name = "Flush Five" if flush else "Five of a Kind"
        scoring = list(real)
    elif straight and flush:
        name, scoring = "Straight Flush", list(real)
    elif counts[0] == 4:
        name, scoring = "Four of a Kind", group_cards(4)
    elif counts[0] == 3 and len(counts) > 1 and counts[1] == 2:
        name = "Flush House" if flush else "Full House"
        scoring = list(real)
    elif flush:
        name, scoring = "Flush", list(real)
    elif straight:
        name, scoring = "Straight", list(real)
    elif counts[0] == 3:
        name, scoring = "Three of a Kind", group_cards(3)
    elif counts[0] == 2 and len(counts) > 1 and counts[1] == 2:
        name, scoring = "Two Pair", group_cards(2)
    elif counts[0] == 2:
        name, scoring = "Pair", group_cards(2)
    else:
        name = "High Card"
        scoring = [max(real, key=lambda c: RANK_ORDER[c.rank])]

    return name, scoring + stones


# ==========================================================================
# Score estimation
# ==========================================================================

def estimate(selection, held, hands_info, jokers, extras):
    """Estimate the score of playing `selection` (list of Card).

    hands_info: gamestate['hands'] (live chips/mult per hand level).
    jokers: list of joker dicts from gamestate.
    extras: dict with hands_left, played_this_round, deck_left, money,
            flint (bool), arm (bool).
    Returns (est_score, hand_name).
    """
    hand_name, scoring = classify(selection)
    info = hands_info.get(hand_name) or {}
    chips = float(info.get("chips", 5))
    mult = float(info.get("mult", 1))

    if extras.get("flint"):
        chips, mult = chips / 2.0, mult / 2.0
    if extras.get("arm"):
        chips, mult = chips * 0.8, mult * 0.8  # rough level-down penalty

    xmult = 1.0
    for c in scoring:
        if c.debuff:
            continue
        if c.is_stone:
            chips += 50
        elif c.rank:
            chips += RANK_CHIPS[c.rank]
        if c.enhancement == "BONUS":
            chips += 30
        elif c.enhancement == "MULT":
            mult += 4
        elif c.enhancement == "GLASS":
            xmult *= 2.0
        elif c.enhancement == "LUCKY":
            mult += 4  # expected value
        if c.edition == "FOIL":
            chips += 50
        elif c.edition == "HOLO":
            mult += 10
        elif c.edition == "POLYCHROME":
            xmult *= 1.5

    # Held-card effects (cards staying in hand)
    for c in held:
        if c.debuff:
            continue
        if c.enhancement == "STEEL":
            xmult *= 1.5

    ctx = {
        "scoring": scoring,
        "played": selection,
        "held": held,
        "hand_name": hand_name,
        "n_played": len(selection),
        "hands_left": extras.get("hands_left", 1),
        "played_this_round": extras.get("played_this_round", {}),
        "n_jokers": len(jokers),
        "deck_left": extras.get("deck_left", 0),
        "money": extras.get("money", 0),
    }
    for j in jokers:
        fn = JOKER_EFFECTS.get(j.get("key", ""))
        if fn:
            dc, dm, dx = fn(ctx)
            chips += dc
            mult += dm
            xmult *= dx
        edition = (j.get("modifier") or {}).get("edition")
        if edition == "FOIL":
            chips += 50
        elif edition == "HOLO":
            mult += 10
        elif edition == "POLYCHROME":
            xmult *= 1.5

    return int(chips * mult * xmult), hand_name


# ==========================================================================
# RPC client
# ==========================================================================

class Rpc:
    def __init__(self, port, delay=0.0, log=None):
        self.url = f"http://127.0.0.1:{port}"
        self.delay = delay
        self.log = log or (lambda s: None)
        self._id = 0

    def call(self, method, params=None):
        self._id += 1
        body = json.dumps({
            "jsonrpc": "2.0", "id": self._id,
            "method": method, "params": params or {},
        }).encode()
        req = urllib.request.Request(
            self.url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode())
        if self.delay:
            time.sleep(self.delay)
        if "error" in data and data["error"]:
            raise ApiError(method, data["error"].get("message", "unknown"))
        return data.get("result")


class ApiError(Exception):
    def __init__(self, method, message):
        super().__init__(f"{method}: {message}")
        self.method = method
        self.message = message


# ==========================================================================
# Bot
# ==========================================================================

class RuleBot:
    def __init__(self, rpc, seed, deck, stake, logf):
        self.rpc = rpc
        self.seed = seed
        self.deck = deck
        self.stake = stake
        self.logf = logf
        self.best_hand = 0
        self.actions = 0
        self.errors_in_a_row = 0
        self.rerolls_this_shop = 0
        self.last_shop_round = -1
        self.pack_fail_counts = {}

    # ---- logging ----
    def log(self, msg):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        self.logf.write(line + "\n")
        self.logf.flush()

    # ---- helpers ----
    def act(self, method, params=None, note=""):
        self.actions += 1
        try:
            result = self.rpc.call(method, params)
            self.errors_in_a_row = 0
            if note:
                self.log(f"ACT {method} {json.dumps(params or {})} | {note}")
            return result
        except (ApiError, OSError) as e:
            self.errors_in_a_row += 1
            self.log(f"API ERROR on {method}: {e}")
            if self.errors_in_a_row >= 12:
                raise RuntimeError("too many consecutive API errors") from e
            time.sleep(0.4)
            return None

    def state(self):
        for _ in range(20):
            try:
                g = self.rpc.call("gamestate")
                self.errors_in_a_row = 0
                return g
            except (ApiError, OSError) as e:
                self.errors_in_a_row += 1
                self.log(f"gamestate error: {e}")
                if self.errors_in_a_row >= 20:
                    raise
                time.sleep(0.5)
        raise RuntimeError("unreachable")

    @staticmethod
    def current_boss(g):
        blinds = g.get("blinds") or {}
        boss = blinds.get("boss") or {}
        if boss.get("status") == "CURRENT":
            return boss.get("name", "")
        return ""

    @staticmethod
    def current_blind(g):
        blinds = g.get("blinds") or {}
        for key in ("small", "big", "boss"):
            b = blinds.get(key) or {}
            if b.get("status") == "CURRENT":
                return b
        return {}

    @staticmethod
    def played_this_round(g):
        return {name: h.get("played_this_round", 0)
                for name, h in (g.get("hands") or {}).items()}

    @staticmethod
    def most_played_hand(g):
        hands = g.get("hands") or {}
        best, best_n = None, -1
        for name, h in hands.items():
            if h.get("played", 0) > best_n:
                best, best_n = name, h.get("played", 0)
        return best if best_n > 0 else None

    def target_hand(self, g):
        """The hand type we are building toward (for planet purchases)."""
        most = self.most_played_hand(g)
        return most or "Flush"

    # ---- main loop ----
    def run(self, resume=False):
        g = self.state()
        if g.get("state") == "MENU":
            self.log(f"START seed={self.seed} deck={self.deck} stake={self.stake}")
            self.act("start", {"deck": self.deck, "stake": self.stake,
                               "seed": self.seed}, note="new run")
        elif not resume:
            self.log(f"Refusing to act: game is in state {g.get('state')}, "
                     "not MENU. Pass --resume to take over an existing run.")
            return None

        stall = 0
        last_sig = None
        while self.actions < 4000:
            g = self.state()
            st = g.get("state")
            sig = (st, (g.get("round") or {}).get("chips"),
                   (g.get("round") or {}).get("hands_left"), g.get("money"),
                   len(((g.get("hand") or {}).get("cards")) or []))
            stall = stall + 1 if sig == last_sig else 0
            last_sig = sig
            if stall >= 30:
                self.log(f"STALLED in {st}, aborting")
                break

            if st == "GAME_OVER":
                return self.finish(g)
            elif st == "MENU":
                self.log("Back at MENU unexpectedly; stopping")
                break
            elif st == "BLIND_SELECT":
                self.do_blind_select(g)
            elif st == "SELECTING_HAND":
                self.do_hand(g)
            elif st == "ROUND_EVAL":
                self.act("cash_out", note="cash out")
            elif st == "SHOP":
                self.do_shop(g)
            elif st == "SMODS_BOOSTER_OPENED":
                self.do_pack(g)
            else:
                time.sleep(0.4)
        self.log("Action cap or stall reached without GAME_OVER")
        return self.finish(self.state())

    def finish(self, g):
        ante = g.get("ante_num", 0)
        won = bool(g.get("won"))
        self.log(f"RESULT ante={ante} best_hand={self.best_hand} won={str(won).lower()}")
        return {"ante": ante, "best_hand": self.best_hand, "won": won}

    # ---- blind select ----
    def do_blind_select(self, g):
        blinds = g.get("blinds") or {}
        for key in ("small", "big", "boss"):
            b = blinds.get(key) or {}
            if b.get("status") == "SELECT":
                self.act("select", note=f"select {key} blind "
                         f"'{b.get('name')}' target={b.get('score')}")
                return
        self.act("select", note="select blind (fallback)")

    # ---- hand play ----
    def do_hand(self, g):
        hand = parse_cards(g.get("hand"))
        rnd = g.get("round") or {}
        blind = self.current_blind(g)
        boss = self.current_boss(g)
        target = max(0, int(blind.get("score", 0)) - int(rnd.get("chips", 0)))
        hands_left = int(rnd.get("hands_left", 1))
        discards_left = int(rnd.get("discards_left", 0))
        jokers = ((g.get("jokers") or {}).get("cards")) or []

        # Verdant Leaf: everything is debuffed until a joker is sold
        if boss == "Verdant Leaf" and jokers:
            cheapest = min(range(len(jokers)),
                           key=lambda i: (jokers[i].get("cost") or {}).get("sell", 0))
            self.act("sell", {"joker": cheapest},
                     note=f"Verdant Leaf: sell joker {cheapest}")
            return

        visible = [c for c in hand if not c.hidden]
        if not visible:
            n = min(5, len(hand))
            self.act("play", {"cards": list(range(n))}, note="all hidden; play blind")
            return

        forced = [c for c in visible if c.highlight] if boss == "Cerulean Bell" else []

        extras = {
            "hands_left": hands_left,
            "played_this_round": self.played_this_round(g),
            "deck_left": ((g.get("cards") or {}).get("count")) or 0,
            "money": g.get("money", 0),
            "flint": boss == "The Flint",
            "arm": boss == "The Arm",
        }
        hands_info = g.get("hands") or {}
        most_played = self.most_played_hand(g)

        sizes = [5] if boss == "The Psychic" else [1, 2, 3, 4, 5]
        eye_blocked = {name for name, n in extras["played_this_round"].items()
                       if n > 0} if boss == "The Eye" else set()
        mouth_allowed = None
        if boss == "The Mouth":
            played = [name for name, n in extras["played_this_round"].items() if n > 0]
            if played:
                mouth_allowed = played[0]

        best = None  # (score, name, selection)
        for size in sizes:
            if size > len(visible):
                continue
            for combo in itertools.combinations(visible, size):
                if forced and not all(f in combo for f in forced):
                    continue
                held = [c for c in hand if c not in combo]
                score, name = estimate(list(combo), held, hands_info, jokers, extras)
                if name in eye_blocked:
                    continue
                if mouth_allowed and name != mouth_allowed:
                    continue
                if boss == "The Ox" and most_played and name == most_played:
                    score = int(score * 0.3)  # heavy penalty: playing it zeroes money
                if best is None or score > best[0]:
                    best = (score, name, list(combo))

        if best is None:
            n = min(5, len(visible))
            self.act("play", {"cards": [c.idx for c in visible[:n]]},
                     note="no legal candidate; play fallback")
            return

        score, name, sel = best
        pace = target / max(1, hands_left)
        if score >= target or score >= pace or discards_left == 0:
            self.log(f"PLAY {name} est={score} target={target} "
                     f"hands_left={hands_left} cards={sel}")
            before = int(rnd.get("chips", 0))
            self.act("play", {"cards": [c.idx for c in sel]}, note=f"play {name}")
            self.track_best_hand(before)
        else:
            discard = self.choose_discard(visible, hands_info)
            if discard:
                self.log(f"DISCARD {discard} (best {name} est={score} < pace {pace:.0f})")
                self.act("discard", {"cards": [c.idx for c in discard]},
                         note="discard chase")
            else:
                before = int(rnd.get("chips", 0))
                self.act("play", {"cards": [c.idx for c in sel]},
                         note=f"play {name} (no useful discard)")
                self.track_best_hand(before)

    def track_best_hand(self, chips_before):
        try:
            g = self.state()
            chips_now = int((g.get("round") or {}).get("chips", 0))
            delta = chips_now - chips_before
            if delta > self.best_hand:
                self.best_hand = delta
                self.log(f"NEW BEST HAND: {delta}")
        except Exception:
            pass

    def choose_discard(self, visible, hands_info):
        """Pick up to 5 cards to throw away, chasing the best draw."""
        keep_enh = {"STEEL", "GLASS", "GOLD", "BONUS", "MULT", "LUCKY"}

        def junk_sort(cards):
            junk = [c for c in cards if c.enhancement not in keep_enh]
            return sorted(junk, key=lambda c: RANK_ORDER.get(c.rank, 0))

        # Flush chase: 4+ of one suit (wilds count everywhere)
        suits = {}
        wilds = [c for c in visible if c.is_wild]
        for c in visible:
            if not c.is_wild and c.suit and not c.is_stone:
                suits.setdefault(c.suit, []).append(c)
        if suits:
            best_suit = max(suits, key=lambda s: len(suits[s]))
            if len(suits[best_suit]) + len(wilds) >= 4:
                junk = [c for c in visible
                        if c not in suits[best_suit] and not c.is_wild]
                junk = junk_sort(junk)[:5]
                if junk:
                    return junk

        # Pair/trips chase toward Full House / Four of a Kind
        ranks = {}
        for c in visible:
            if c.rank and not c.is_stone:
                ranks.setdefault(c.rank, []).append(c)
        paired = [cs for cs in ranks.values() if len(cs) >= 2]
        if paired:
            keep = {c for cs in paired for c in cs}
            junk = junk_sort([c for c in visible if c not in keep])[:5]
            if junk:
                return junk

        # Nothing: pitch the lowest cards, keep the top 3
        ordered = sorted(visible, key=lambda c: RANK_ORDER.get(c.rank, 0))
        junk = junk_sort(ordered[:max(0, len(ordered) - 3)])[:5]
        return junk

    # ---- shop ----
    def shop_priority(self, card):
        """Priority score for a shop joker (higher = better buy)."""
        effect = ((card.get("value") or {}).get("effect")) or ""
        key = card.get("key", "")
        p = 0.0
        mx = re.search(r"[Xx](\d+(?:[.,]\d+)?)\s*Mult", effect)
        madd = re.search(r"\+(\d+)\s*Mult", effect)
        cadd = re.search(r"\+(\d+)\s*Chips", effect)
        if mx:
            p = max(p, 100 + 10 * float(mx.group(1).replace(",", ".")))
        if madd:
            p = max(p, 50 + float(madd.group(1)))
        if cadd:
            p = max(p, 30 + float(cadd.group(1)) / 10)
        if re.search(r"[Ee]arn\s+\$|\$\d+.*(end of round|payout)", effect):
            p = max(p, 40)
        if p == 0:
            p = 20
        p += SHOP_KEY_BONUS.get(key, 0)
        edition = (card.get("modifier") or {}).get("edition")
        if edition in ("HOLO", "POLYCHROME", "FOIL"):
            p += 15
        return p

    @staticmethod
    def is_xmult_joker(card):
        effect = ((card.get("value") or {}).get("effect")) or ""
        return bool(re.search(r"[Xx]\d+(?:[.,]\d+)?\s*Mult", effect))

    def money_reserve(self, g, priority):
        if g.get("ante_num", 1) <= 2 or priority >= 100:
            return 0
        return 20

    def do_shop(self, g):
        rnd_num = g.get("round_num", 0)
        if rnd_num != self.last_shop_round:
            self.last_shop_round = rnd_num
            self.rerolls_this_shop = 0

        money = int(g.get("money", 0))
        jokers_area = g.get("jokers") or {}
        jokers = jokers_area.get("cards") or []
        jlimit = jokers_area.get("limit", 5)

        # 1) Use / clear consumables
        cons = ((g.get("consumables") or {}).get("cards")) or []
        for i, c in enumerate(cons):
            cset = c.get("set")
            label = c.get("label", "")
            if cset == "PLANET":
                self.act("use", {"consumable": i}, note=f"use planet {label}")
                return
            if label in ("The Hermit", "Temperance"):
                self.act("use", {"consumable": i}, note=f"use {label}")
                return
        # Sell leftover non-planet consumables for cash
        for i, c in enumerate(cons):
            if c.get("set") in ("TAROT", "SPECTRAL"):
                self.act("sell", {"consumable": i},
                         note=f"sell {c.get('label')}")
                return

        shop_cards = ((g.get("shop") or {}).get("cards")) or []
        target = self.target_hand(g)

        # 2) Planets in the shop that level our target hand
        for i, c in enumerate(shop_cards):
            if c.get("set") != "PLANET":
                continue
            effect = ((c.get("value") or {}).get("effect")) or ""
            cost = (c.get("cost") or {}).get("buy", 99)
            if target in effect and money - cost >= self.money_reserve(g, 60):
                self.act("buy", {"card": i}, note=f"buy planet {c.get('label')}")
                return

        # 3) Jokers by priority
        cands = [(self.shop_priority(c), i, c) for i, c in enumerate(shop_cards)
                 if c.get("set") == "JOKER"]
        cands.sort(key=lambda t: -t[0])
        for prio, i, c in cands:
            cost = (c.get("cost") or {}).get("buy", 99)
            reserve = self.money_reserve(g, prio)
            if money - cost < reserve:
                continue
            if len(jokers) < jlimit:
                self.act("buy", {"card": i},
                         note=f"buy joker {c.get('label')} prio={prio:.0f} ${cost}")
                return
            owned = [(self.shop_priority(j), k) for k, j in enumerate(jokers)
                     if not (j.get("modifier") or {}).get("eternal")]
            if owned:
                owned.sort()
                worst_prio, worst_idx = owned[0]
                if prio > worst_prio + 15:
                    self.act("sell", {"joker": worst_idx},
                             note=f"sell joker {jokers[worst_idx].get('label')} "
                                  f"prio={worst_prio:.0f} to fit better one")
                    return
            break  # slots full, nothing worth swapping in

        # 4) Packs: celestial and buffoon first, then arcana
        packs = ((g.get("packs") or {}).get("cards")) or []
        for i, c in enumerate(packs):
            label = c.get("label", "")
            cost = (c.get("cost") or {}).get("buy", 99)
            good = ("Celestial" in label or "Buffoon" in label
                    or "Arcana" in label)
            if good and money - cost >= self.money_reserve(g, 45):
                self.act("buy", {"pack": i}, note=f"buy pack {label} ${cost}")
                return

        # 5) Reroll hunting for jokers
        reroll_cost = int((g.get("round") or {}).get("reroll_cost", 5))
        have_buyable_joker = any(
            prio >= 50 and money - (c.get("cost") or {}).get("buy", 99)
            >= self.money_reserve(g, prio) for prio, _, c in cands)
        if (len(jokers) < jlimit and not have_buyable_joker
                and self.rerolls_this_shop < 2
                and money - reroll_cost >= self.money_reserve(g, 0) + 5):
            self.rerolls_this_shop += 1
            self.act("reroll", note=f"reroll #{self.rerolls_this_shop} ${reroll_cost}")
            return

        # 6) Order jokers: additive left, xmult right
        order = sorted(range(len(jokers)),
                       key=lambda k: 1 if self.is_xmult_joker(jokers[k]) else 0)
        if order != list(range(len(jokers))) and len(jokers) > 1:
            self.act("rearrange", {"jokers": order}, note="xmult jokers to the right")

        self.act("next_round", note="leave shop")

    # ---- pack picks ----
    def pack_priority(self, card, target):
        cset = card.get("set")
        effect = ((card.get("value") or {}).get("effect")) or ""
        label = card.get("label", "")
        if cset == "PLANET":
            return 90 + (30 if target in effect else 0)
        if cset == "JOKER":
            return self.shop_priority(card)
        if cset in ("DEFAULT", "ENHANCED"):
            enh = (card.get("modifier") or {}).get("enhancement")
            bonus = {"STEEL": 40, "GLASS": 35, "GOLD": 20, "BONUS": 15,
                     "MULT": 15, "LUCKY": 15, "WILD": 15, "STONE": 10}
            return 25 + bonus.get(enh, 0)
        if cset == "TAROT":
            if label in ("The Hermit", "Temperance"):
                return 60
            return 15
        if cset == "SPECTRAL":
            return 10
        return 5

    def do_pack(self, g):
        pack_cards = ((g.get("pack") or {}).get("cards")) or []
        if not pack_cards:
            self.act("pack", {"skip": True}, note="empty pack; skip")
            return
        target = self.target_hand(g)
        ranked = sorted(range(len(pack_cards)),
                        key=lambda i: -self.pack_priority(pack_cards[i], target))
        jokers_area = g.get("jokers") or {}
        full = len(jokers_area.get("cards") or []) >= jokers_area.get("limit", 5)
        cons_area = g.get("consumables") or {}
        cons_full = len(cons_area.get("cards") or []) >= cons_area.get("limit", 2)

        for i in ranked:
            c = pack_cards[i]
            cset = c.get("set")
            if cset == "JOKER" and full:
                continue
            if cset in ("TAROT", "PLANET", "SPECTRAL") and cons_full:
                continue
            sig = (g.get("round_num"), i)
            fails = self.pack_fail_counts.get(sig, 0)
            if fails >= 2:
                continue
            params = {"card": i}
            effect = ((c.get("value") or {}).get("effect")) or ""
            needs_targets = cset in ("TAROT", "SPECTRAL") and re.search(
                r"selected card|\d+\s+selected", effect, re.I)
            if needs_targets:
                n = 1
                m = re.search(r"(\d+)\s+selected", effect)
                if m:
                    n = int(m.group(1))
                hand_cards = ((g.get("hand") or {}).get("cards")) or []
                if len(hand_cards) < n:
                    continue
                params["cards"] = list(range(n))
            result = self.act("pack", params,
                              note=f"pick {c.get('label')} from pack")
            if result is None and self.errors_in_a_row:
                self.pack_fail_counts[sig] = fails + 1
                continue
            return
        # Last resort only: skip (known desync risk, avoid when possible)
        self.act("pack", {"skip": True}, note="no pickable card; skip pack")


# ==========================================================================
# Entry point
# ==========================================================================

def main():
    ap = argparse.ArgumentParser(description="Hardcoded-rules Balatro bot")
    ap.add_argument("--port", type=int, default=12347)
    ap.add_argument("--seed", default="BENCHMRK")
    ap.add_argument("--deck", default="RED")
    ap.add_argument("--stake", default="WHITE")
    ap.add_argument("--resume", action="store_true",
                    help="take over a run already in progress")
    ap.add_argument("--delay", type=float, default=0.0,
                    help="pause after every action, in seconds")
    args = ap.parse_args()

    logs = Path(__file__).parent / "logs"
    logs.mkdir(exist_ok=True)
    log_path = logs / f"run-{time.strftime('%Y%m%d-%H%M%S')}.log"
    started = time.time()
    with open(log_path, "w", encoding="utf-8") as logf:
        rpc = Rpc(args.port, delay=args.delay)
        bot = RuleBot(rpc, args.seed, args.deck, args.stake, logf)
        try:
            result = bot.run(resume=args.resume)
        except KeyboardInterrupt:
            bot.log("Interrupted by user")
            result = None
        except Exception as e:
            bot.log(f"FATAL: {e}")
            raise
        finally:
            bot.log(f"Elapsed: {time.time() - started:.1f}s, "
                    f"actions: {bot.actions}, log: {log_path}")
    if result:
        print(f"RESULT ante={result['ante']} best_hand={result['best_hand']} "
              f"won={str(result['won']).lower()}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
