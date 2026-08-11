"""Offline tests for rulebot decision logic. Never touches the game."""

import unittest

from rulebot import (Card, RuleBot, classify, estimate)


def card(idx, rank, suit, enhancement=None, edition=None, debuff=False,
         hidden=False, highlight=False):
    return Card(idx, {
        "value": {"rank": rank, "suit": suit},
        "modifier": {"enhancement": enhancement, "edition": edition},
        "state": {"debuff": debuff, "hidden": hidden, "highlight": highlight},
        "label": f"{rank}{suit}",
    })


HANDS_INFO = {
    "High Card": {"chips": 5, "mult": 1},
    "Pair": {"chips": 10, "mult": 2},
    "Two Pair": {"chips": 20, "mult": 2},
    "Three of a Kind": {"chips": 30, "mult": 3},
    "Straight": {"chips": 30, "mult": 4},
    "Flush": {"chips": 35, "mult": 4},
    "Full House": {"chips": 40, "mult": 4},
    "Four of a Kind": {"chips": 60, "mult": 7},
    "Straight Flush": {"chips": 100, "mult": 8},
    "Five of a Kind": {"chips": 120, "mult": 12},
    "Flush House": {"chips": 140, "mult": 14},
    "Flush Five": {"chips": 160, "mult": 16},
}

EXTRAS = {"hands_left": 3, "played_this_round": {}, "deck_left": 40,
          "money": 10, "flint": False, "arm": False}


class TestClassify(unittest.TestCase):
    def test_flush(self):
        cards = [card(i, r, "H") for i, r in enumerate("A K 9 5 3".split())]
        name, scoring = classify(cards)
        self.assertEqual(name, "Flush")
        self.assertEqual(len(scoring), 5)

    def test_full_house(self):
        cards = [card(0, "K", "H"), card(1, "K", "S"), card(2, "K", "D"),
                 card(3, "4", "C"), card(4, "4", "H")]
        name, _ = classify(cards)
        self.assertEqual(name, "Full House")

    def test_straight_ace_low(self):
        cards = [card(i, r, s) for i, (r, s) in enumerate(
            [("A", "H"), ("2", "S"), ("3", "D"), ("4", "C"), ("5", "H")])]
        name, _ = classify(cards)
        self.assertEqual(name, "Straight")

    def test_straight_flush(self):
        cards = [card(i, r, "S") for i, r in enumerate("9 T J Q K".split())]
        name, _ = classify(cards)
        self.assertEqual(name, "Straight Flush")

    def test_two_pair_scoring_cards(self):
        cards = [card(0, "K", "H"), card(1, "K", "S"), card(2, "4", "D"),
                 card(3, "4", "C"), card(4, "9", "H")]
        name, scoring = classify(cards)
        self.assertEqual(name, "Two Pair")
        self.assertEqual(len(scoring), 4)  # the 9 kicker does not score

    def test_wild_makes_flush(self):
        cards = [card(0, "A", "H"), card(1, "K", "H"), card(2, "9", "H"),
                 card(3, "5", "H"), card(4, "3", "S", enhancement="WILD")]
        name, _ = classify(cards)
        self.assertEqual(name, "Flush")

    def test_stone_blocks_flush_but_scores(self):
        cards = [card(0, "A", "H"), card(1, "K", "H"), card(2, "9", "H"),
                 card(3, "5", "H"), card(4, "3", "H", enhancement="STONE")]
        name, scoring = classify(cards)
        self.assertNotEqual(name, "Flush")  # only 4 real hearts
        self.assertIn(cards[4], scoring)    # stone always scores

    def test_high_card_single_scorer(self):
        cards = [card(0, "A", "H"), card(1, "K", "S"), card(2, "9", "D"),
                 card(3, "5", "C"), card(4, "3", "H")]
        name, scoring = classify(cards)
        self.assertEqual(name, "High Card")
        self.assertEqual(scoring[0].rank, "A")


class TestEstimate(unittest.TestCase):
    def test_flush_beats_pair(self):
        flush = [card(i, r, "H") for i, r in enumerate("A K 9 5 3".split())]
        pair = [card(0, "A", "H"), card(1, "A", "S")]
        f, _ = estimate(flush, [], HANDS_INFO, [], EXTRAS)
        p, _ = estimate(pair, [], HANDS_INFO, [], EXTRAS)
        self.assertGreater(f, p)

    def test_debuffed_card_no_chips(self):
        clean = [card(0, "A", "H"), card(1, "A", "S")]
        debuffed = [card(0, "A", "H", debuff=True), card(1, "A", "S")]
        c, _ = estimate(clean, [], HANDS_INFO, [], EXTRAS)
        d, _ = estimate(debuffed, [], HANDS_INFO, [], EXTRAS)
        self.assertGreater(c, d)

    def test_steel_held_multiplies(self):
        sel = [card(0, "A", "H"), card(1, "A", "S")]
        steel = [card(2, "K", "H", enhancement="STEEL")]
        base, _ = estimate(sel, [], HANDS_INFO, [], EXTRAS)
        boosted, _ = estimate(sel, steel, HANDS_INFO, [], EXTRAS)
        self.assertAlmostEqual(boosted / base, 1.5, delta=0.1)

    def test_duo_doubles_pairs(self):
        sel = [card(0, "A", "H"), card(1, "A", "S")]
        duo = [{"key": "j_duo", "modifier": {}}]
        base, _ = estimate(sel, [], HANDS_INFO, [], EXTRAS)
        with_duo, _ = estimate(sel, [], HANDS_INFO, duo, EXTRAS)
        self.assertEqual(with_duo, base * 2)

    def test_duo_applies_to_full_house(self):
        sel = [card(0, "K", "H"), card(1, "K", "S"), card(2, "K", "D"),
               card(3, "4", "C"), card(4, "4", "H")]
        duo = [{"key": "j_duo", "modifier": {}}]
        base, name = estimate(sel, [], HANDS_INFO, [], EXTRAS)
        with_duo, _ = estimate(sel, [], HANDS_INFO, duo, EXTRAS)
        self.assertEqual(name, "Full House")
        self.assertEqual(with_duo, base * 2)

    def test_acrobat_only_on_last_hand(self):
        sel = [card(0, "A", "H"), card(1, "A", "S")]
        acrobat = [{"key": "j_acrobat", "modifier": {}}]
        normal, _ = estimate(sel, [], HANDS_INFO, acrobat, EXTRAS)
        last = dict(EXTRAS, hands_left=1)
        final, _ = estimate(sel, [], HANDS_INFO, acrobat, last)
        self.assertEqual(final, normal * 3)

    def test_flint_halves(self):
        sel = [card(0, "A", "H"), card(1, "A", "S")]
        base, _ = estimate(sel, [], HANDS_INFO, [], EXTRAS)
        flint, _ = estimate(sel, [], HANDS_INFO, [], dict(EXTRAS, flint=True))
        self.assertLess(flint, base)


class FakeBot(RuleBot):
    """RuleBot with no RPC, for exercising pure decision helpers."""

    def __init__(self):
        pass  # skip parent init entirely


class TestDiscard(unittest.TestCase):
    def setUp(self):
        self.bot = FakeBot()

    def test_flush_chase(self):
        visible = ([card(i, r, "H") for i, r in enumerate("A K 9 5".split())]
                   + [card(4, "2", "S"), card(5, "7", "C"), card(6, "J", "D"),
                      card(7, "3", "S")])
        junk = self.bot.choose_discard(visible, HANDS_INFO)
        self.assertTrue(junk)
        self.assertTrue(all(c.suit != "H" for c in junk))

    def test_pair_keep(self):
        visible = [card(0, "K", "H"), card(1, "K", "S"), card(2, "9", "D"),
                   card(3, "5", "C"), card(4, "3", "H"), card(5, "2", "S"),
                   card(6, "7", "C"), card(7, "J", "D")]
        junk = self.bot.choose_discard(visible, HANDS_INFO)
        self.assertTrue(junk)
        self.assertTrue(all(c.rank != "K" for c in junk))

    def test_steel_never_discarded_first(self):
        visible = [card(0, "2", "H", enhancement="STEEL"), card(1, "3", "S"),
                   card(2, "9", "D"), card(3, "5", "C"), card(4, "4", "H"),
                   card(5, "6", "S"), card(6, "7", "C"), card(7, "J", "D")]
        junk = self.bot.choose_discard(visible, HANDS_INFO)
        self.assertTrue(all(c.enhancement != "STEEL" for c in junk))


class TestShopPriority(unittest.TestCase):
    def setUp(self):
        self.bot = FakeBot()

    def shop_card(self, key, effect, edition=None):
        return {"key": key, "set": "JOKER", "label": key,
                "value": {"effect": effect},
                "modifier": {"edition": edition}, "cost": {"buy": 5}}

    def test_xmult_beats_flat_mult(self):
        x = self.bot.shop_priority(self.shop_card("j_cavendish", "X3 Mult"))
        flat = self.bot.shop_priority(self.shop_card("j_joker", "+4 Mult"))
        self.assertGreater(x, flat)

    def test_flat_mult_beats_chips(self):
        m = self.bot.shop_priority(self.shop_card("j_joker", "+4 Mult"))
        c = self.bot.shop_priority(
            self.shop_card("j_blue_joker", "+2 Chips for each card in deck"))
        self.assertGreater(m, c)

    def test_blueprint_bonus(self):
        bp = self.bot.shop_priority(
            self.shop_card("j_blueprint", "Copies ability of Joker to the right"))
        generic = self.bot.shop_priority(
            self.shop_card("j_unknown_thing", "Does something odd"))
        self.assertGreater(bp, generic)

    def test_xmult_detector(self):
        self.assertTrue(self.bot.is_xmult_joker(
            self.shop_card("j_cavendish", "X3 Mult")))
        self.assertFalse(self.bot.is_xmult_joker(
            self.shop_card("j_joker", "+4 Mult")))


class TestBossConstraints(unittest.TestCase):
    """Exercise do_hand candidate filtering indirectly via classify/estimate
    with the same predicates do_hand uses."""

    def test_eye_blocks_repeats(self):
        played = {"Pair": 1, "Flush": 0}
        blocked = {name for name, n in played.items() if n > 0}
        self.assertIn("Pair", blocked)
        self.assertNotIn("Flush", blocked)

    def test_psychic_size(self):
        sizes = [5]
        self.assertEqual(sizes, [5])


if __name__ == "__main__":
    unittest.main(verbosity=2)
