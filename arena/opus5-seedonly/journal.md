# BENCHMRK run journal (Red deck, White stake)

## Build plan (from seed analysis)
- Seed is planet-rich: nearly every ante offers 1-3 Celestial packs (many Jumbo/Mega).
  => Plan: commit to ONE hand type and level it hard with planets.
- Multiplicative jokers reachable: The Duo (A2 #3, X2 if hand contains Pair),
  The Trio (A3 #67, X3 three-of-a-kind), The Family (A3 #66/#93, X4 four-of-a-kind),
  Card Sharp (A3 #46/#60, X3 if hand type repeated this round), Blueprint (A6 #80, A7 #40, A10 #49),
  Baron (A1 #10), Photograph, Vampire, Campfire (foil A3 #44), Constellation (A8+).
- Target: pair-containing hands (Three of a Kind / Full House / Four of a Kind) so
  Duo+Trio(+Family) all stack. Level Venus/Earth/Mars.
- Ante 3 Spectral pack has Cryptid (duplicate a card twice) -> card duplication for consistency.
- Voucher notes: A1 Tarot Merchant (good), A2 Hieroglyph (SKIP - loses an ante and a hand),
  A4 Telescope (good with planet packs), A7 Crystal Ball, A11 Overstock.

## Ante 1
Boss: The Pillar (cards played earlier this ante are debuffed) -> minimize cards played
before the boss. Decision: SKIP Small blind to bank Coupon Tag (free shop), play Big.
Coupon Tag made the whole shop free -> picked up Mad Joker, Jolly Joker, Drunkard cheap.
Committed to FULL HOUSE as primary hand (contains Pair + Two Pair + Three of a Kind, so it
triggers Mad Joker, Jolly Joker and The Duo all at once). Fallback: Two Pair.
BEST HAND ANTE 1: 1512

## Ante 2
Voucher Hieroglyph offered - SKIPPED on purpose (it lowers ante but costs a hand, bad for a
score/ante-max run). Bought The Duo (X2 Mult if hand contains a Pair) from shop queue #3.
Leveling Earth (Full House) and Uranus (Two Pair) from Celestial packs.
BEST HAND ANTE 2: 8256

## Ante 3
Traded Jolly Joker + Drunkard away for Mystic Summit (+15 Mult at 0 discards) and Supernova
(+Mult equal to times this hand played this run, grows every round). Mystic Summit is
effectively unconditional: with 8 card hand and a 5 card scoring hand I burn the spare
discards one card at a time before playing.
Lesson learned: the seed's shop queue in the analysis file is only APPROXIMATE - jokers I
already own get substituted out, so predicted entries shift. Wasted ~$10 rerolling for a
Cavendish that never appeared.
BEST HAND ANTE 3: 12720

## Ante 4
Bought TELESCOPE voucher ($10, left me at $1) - every Celestial Pack now guarantees the planet
for my most played hand (Earth / Full House). This is the backbone of the scaling plan.
Boss The Wheel cleared with KKQQ two pair for 10340.
*** MAJOR SELF-INFLICTED BUG FOUND HERE ***: that hand should have been ~14080. Factoring
10340 = 220 x 47 showed mult was 47 not 64. Joker order was Mad(+10), Duo(x2), Scary Face,
Mystic(+15), Supernova(+4) => (4+10)x2+15+4 = 47. Jokers apply LEFT TO RIGHT, so the x2 was
multiplying only part of the flat mult. Fixed with rearrange -> Duo moved to slot 4 (last).
Correct now: (4+10+15+4)x2 = 66. RULE: every X-mult joker goes AFTER all flat +mult jokers.
BEST HAND ANTE 4: 15080

## Ante 5
Boss: The Club (all Club cards debuffed). Voucher Reroll Surplus.
Shop 1: bought Celestial Pack -> Earth, Full House to level 4. Saving cash: the analysis says
ante 5's SECOND shop has a Buffoon Pack containing PHOTOGRAPH (X2 Mult on first scored face
card) plus a Mega Spectral (Immolate/Grim/Ectoplasm/Sigil). Photograph is the top target since
my build is additive-heavy and needs a second multiplier.

*** BLUNDER: I opened the Buffoon Pack with all 5 joker slots FULL. Photograph could not be
taken ("Cannot select joker, joker slots are full"), so I had to skip the pack and lost
Photograph for $4.
Note on the escape hatch that did NOT work: I tried to sell Scary Face from inside the pack
and got "API ERROR: Method 'sell' requires one of these states: SELECTING_HAND, SHOP". That
is a limitation of THIS BENCHMARK HARNESS, not a Balatro rule - in the real game the joker
row is still interactive while a booster is open and you can sell to make room. So under this
API the rule is absolute: free the joker slot in the SHOP, before buying the pack. There is
no recovery once the pack is open. ***
Recovered with the Mega Spectral: took Immolate (+$20, destroyed 5 junk cards from hand) and
Ectoplasm (Negative on Scary Face -> 6th joker slot, hand size 8 -> 7).
Also bought Hiker ($5, permanent +5 chips per scored card) and the Reroll Surplus voucher
($10, rerolls -$2) to make future digging for X-mult jokers cheaper.
Small Blind (11000): two pair KKQQ for 14960.
Big Blind (16500): full house QQTTT for 19800.
Bought Jumbo Celestial -> Earth (Full House lvl 5) and The Chariot -> steel 2D (X1.5 in hand).
BOSS The Club (22000, all clubs debuffed): DIED at 16919/22000.
BEST HAND ANTE 5: 19800

## Post-mortem
Final ante: 5 (died on the ante 5 boss, The Club).
Best single hand of the run: 19800 (full house QQTTT, ante 5 big blind).
Run total on the fatal blind: 16919 of 22000 required.

What actually killed the run, step by step:
1. Boss hand 1 drew four Queens with no second pair. Four of a Kind was still LEVEL 1 (I had
   funneled every planet into Earth/Full House), so QQQQ scored only 10070 instead of the
   ~35000 a levelled four of a kind would have given. One of the Queens was a club and was
   debuffed, costing chips and a Scary Face trigger too.
2. I had already spent all 4 discards early in the round just to switch on Mystic Summit
   (+15 Mult at 0 discards). That left me with zero ability to fix a bad board.
3. With 0 discards I burned hands 2 and 3 playing junk purely to cycle cards, scoring ~340
   combined. The last hand found only AA66 (with the 6 of clubs debuffed) for ~6500.

Concrete lessons for a future attempt on BENCHMRK (Red / White):
- DO NOT pre-burn discards for Mystic Summit on BOSS rounds. Mystic Summit is fine on small
  and big blinds where one hand wins the round, but on a boss you need the discards to hunt.
  Burn the discards only once the scoring hand is already assembled in hand.
- Do not put 100% of planets into a single hand type. Earth-only meant Four of a Kind sat at
  level 1 and a natural quads draw was a dead end. Take at least a couple of Mars (Four of a
  Kind) - QQQQ at Mars lvl 4 would have cleared this boss on its own.
- Joker order is a real damage multiplier: X-mult jokers LAST. I lost ~27% of my score for
  several rounds before catching this at ante 4.
- Free a joker slot BEFORE opening a Buffoon pack (see the Photograph blunder above). The
  harness blocks `sell` outside SELECTING_HAND/SHOP, so a full board when the pack opens is
  unrecoverable. The ante 5 Buffoon pack is the last easily-reachable X-mult joker on this
  seed, so this single sequencing error probably cost the run an ante or two.
- The additive core (Mad +10 / Mystic +15 / Supernova) with a single X2 (The Duo) tops out
  around 20-25k, which is exactly ante 5 boss territory. This seed needs a SECOND multiplier
  by ante 5: Photograph (ante 5 Buffoon pack) or steel cards en masse via The Chariot.
  Buying The Chariot repeatedly and stacking steel cards on cards you never play is the
  cheapest multiplicative scaling available here.
- Skipping the ante 1 small blind for the Coupon Tag was good and worth repeating.
- Treat the seed analysis' shop queue as approximate: owned jokers get substituted out and
  shift every later position. Do not spend money rerolling toward a specific deep entry.
