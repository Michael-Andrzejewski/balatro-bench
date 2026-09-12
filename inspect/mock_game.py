"""A tiny fake Balatro JSON-RPC server for testing the Inspect harness offline.

It is not Balatro. It walks the same state machine (MENU -> BLIND_SELECT ->
SELECTING_HAND -> ROUND_EVAL -> SHOP -> ...), scores 40 chips per card played,
grows the blind target each round, refuses set/add/load like bench mode, and
ends the run at a configurable ante so scorers have something to read.

    python mock_game.py --port 12399 --die-at-ante 3
"""

from __future__ import annotations

import argparse
import json
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
SUITS = ["S", "H", "D", "C"]


class MockGame:
    def __init__(self, die_at_ante: int = 3, seed_rng: int = 7):
        self.die_at_ante = die_at_ante
        self.rng = random.Random(seed_rng)
        self.reset()

    def reset(self):
        self.state = "MENU"
        self.ante = 0
        self.round = 0
        self.money = 4
        self.won = False
        self.hand: list[dict] = []
        self.chips = 0
        self.hands_left = 4
        self.discards_left = 3
        self.blind_target = 0
        self.blind_idx = 0  # 0 small, 1 big, 2 boss

    def _card(self) -> dict:
        return {
            "label": "card",
            "value": {"rank": self.rng.choice(RANKS), "suit": self.rng.choice(SUITS)},
            "modifier": {},
            "state": {},
        }

    def _deal(self):
        self.hand = [self._card() for _ in range(8)]

    def _target(self) -> int:
        base = 300 * (2 ** (self.ante - 1))
        return int(base * (1.0, 1.5, 2.0)[self.blind_idx])

    def gamestate(self) -> dict:
        names = ("Small Blind", "Big Blind", "The Wall")
        blinds = {
            "small": {"name": "Small Blind", "type": "SMALL", "score": int(300 * 2 ** max(0, self.ante - 1)),
                      "tag_name": "Uncommon Tag", "status": "CURRENT" if self.blind_idx == 0 else "UPCOMING"},
            "big": {"name": "Big Blind", "type": "BIG", "score": int(450 * 2 ** max(0, self.ante - 1)),
                    "tag_name": "Double Tag", "status": "CURRENT" if self.blind_idx == 1 else "UPCOMING"},
            "boss": {"name": "The Wall", "type": "BOSS", "score": int(600 * 2 ** max(0, self.ante - 1)),
                     "effect": "Extra large blind", "status": "CURRENT" if self.blind_idx == 2 else "UPCOMING"},
        }
        g = {
            "state": self.state,
            "ante_num": self.ante,
            "round_num": self.round,
            "money": self.money,
            "won": self.won,
            "blinds": blinds if self.state != "MENU" else None,
            "jokers": {"cards": [], "limit": 5},
            "consumables": {"cards": []},
            "hands": {"High Card": {"level": 1}, "Pair": {"level": 1}},
        }
        if self.state in ("SELECTING_HAND", "ROUND_EVAL"):
            g["hand"] = {"cards": self.hand}
            g["round"] = {
                "chips": self.chips,
                "hands_left": self.hands_left,
                "discards_left": self.discards_left,
                "reroll_cost": 5,
            }
        if self.state == "SHOP":
            g["shop"] = {"cards": [{"label": "Joker", "cost": {"buy": 4}, "set": "Joker",
                                     "value": {"effect": "+4 Mult"}}]}
            g["vouchers"] = {"cards": []}
            g["packs"] = {"cards": []}
        if self.state == "GAME_OVER":
            g["post_run_interview"] = "Do you consent to this run being published?"
        return g

    def call(self, method: str, params: dict) -> dict:
        if method in ("set", "add", "load"):
            raise ValueError(f"{method} is disabled in benchmark mode")
        if method == "gamestate":
            return self.gamestate()
        if method == "start":
            if self.state != "MENU":
                raise ValueError("start only valid in MENU")
            if params.get("seed") != "BENCHMRK":
                raise ValueError("mock only knows seed BENCHMRK")
            self.ante, self.round, self.blind_idx = 1, 0, 0
            self.state = "BLIND_SELECT"
            return self.gamestate()
        if method == "select":
            if self.state != "BLIND_SELECT":
                raise ValueError("select only valid in BLIND_SELECT")
            self.round += 1
            self.blind_target = self._target()
            self.chips, self.hands_left, self.discards_left = 0, 4, 3
            self._deal()
            self.state = "SELECTING_HAND"
            return self.gamestate()
        if method == "skip":
            if self.state != "BLIND_SELECT" or self.blind_idx == 2:
                raise ValueError("cannot skip")
            self.blind_idx += 1
            return self.gamestate()
        if method == "play":
            if self.state != "SELECTING_HAND":
                raise ValueError("play only valid in SELECTING_HAND")
            cards = params.get("cards") or []
            if not cards or len(cards) > 5 or any(i >= len(self.hand) for i in cards):
                raise ValueError("bad card indices")
            # Boss at die_at_ante is unbeatable: scoring is crippled.
            per_card = 5 if (self.ante >= self.die_at_ante and self.blind_idx == 2) else 40
            self.chips += per_card * len(cards) * self.ante
            self.hands_left -= 1
            for i in sorted(cards, reverse=True):
                self.hand.pop(i)
            self.hand += [self._card() for _ in range(len(cards))]
            if self.chips >= self.blind_target:
                self.state = "ROUND_EVAL"
                if self.blind_idx == 2 and self.ante >= 8:
                    self.won = True
            elif self.hands_left == 0:
                self.state = "GAME_OVER"
            return self.gamestate()
        if method == "discard":
            if self.state != "SELECTING_HAND" or self.discards_left <= 0:
                raise ValueError("cannot discard")
            cards = params.get("cards") or []
            for i in sorted(cards, reverse=True):
                self.hand.pop(i)
            self.hand += [self._card() for _ in range(len(cards))]
            self.discards_left -= 1
            return self.gamestate()
        if method == "cash_out":
            if self.state != "ROUND_EVAL":
                raise ValueError("cash_out only valid in ROUND_EVAL")
            self.money += 4 + self.hands_left
            self.state = "SHOP"
            return self.gamestate()
        if method in ("buy", "reroll", "sell", "use", "rearrange", "pack"):
            if self.state not in ("SHOP", "SELECTING_HAND"):
                raise ValueError(f"{method} not valid now")
            if method == "buy":
                self.money -= 4
            return self.gamestate()
        if method == "next_round":
            if self.state != "SHOP":
                raise ValueError("next_round only valid in SHOP")
            self.blind_idx += 1
            if self.blind_idx == 3:
                self.blind_idx = 0
                self.ante += 1
            self.state = "BLIND_SELECT"
            return self.gamestate()
        raise ValueError(f"unknown method {method}")


def make_handler(game: MockGame):
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # quiet
            pass

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            rid = req.get("id", 1)
            with lock:
                try:
                    result = game.call(req.get("method", ""), req.get("params") or {})
                    body = {"jsonrpc": "2.0", "id": rid, "result": result}
                except ValueError as e:
                    body = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32000, "message": str(e)}}
            out = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

    return Handler


def serve(port: int, die_at_ante: int = 3) -> HTTPServer:
    game = MockGame(die_at_ante=die_at_ante)
    srv = HTTPServer(("127.0.0.1", port), make_handler(game))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=12399)
    ap.add_argument("--die-at-ante", type=int, default=3)
    a = ap.parse_args()
    srv = serve(a.port, a.die_at_ante)
    print(f"mock Balatro on http://127.0.0.1:{a.port} (dies at ante {a.die_at_ante}); Ctrl+C to stop")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        srv.shutdown()
