# Balatro Bench run: Opus 4.8, 2026-07-13

- Seed: `BENCHMRK` | Deck: Red | Stake: White | Sandbox: BALATROBOT_BENCH=1 verified (set/add blocked)
- Metric: furthest ante (primary), best single hand (tiebreak)

## Build

Two Pair / Full House engine: **Mad Joker** (+10 mult, triggers on two pair and
full house) + **Burnt Joker** (levels a hand per round from first discard) +
**Baron** (X1.5 mult per King held in hand) + **Acrobat** (X3 on final hand) +
**Egg** (Negative, economy + the extra joker slot). Two Pair and Full House
leveled via planets (Uranus, Earth).

Key discovery: Baron with several Kings *held* is enormous. Holding three Kings
and playing a lone Ace scored 945. Doctrine: hoard Kings, play a small hand while
holding them.

## Progress

- **Ante 1**: Small (300) cleared with a full house 328. Big (450) two pair AAJJ
  744. Boss The Pillar (600) full house KKQQQ **1260**. Bought Burnt (from
  Buffoon pack), Mad, leveled Two Pair (Uranus) and Full House (Earth).
- **Ante 2**: Small (800) two pair QQ99 1014. Big (1200) cleared 2117 across two
  hands (Baron + 3 Kings held = 945 on an Ace). Boss The Hook (1600) full house
  999QQ **1792**. Bought Baron, Acrobat, Egg; Ectoplasm made Egg Negative (+1
  slot). Score model note: full-house math is exact; Baron interaction scored
  higher than expected.
- **Ante 3**: Small (2000) full house QQQ77 holding K = 2071. Big (3000) cleared
  3789: full house QQQAA holding KK = **2749** (best hand), then KKTT to finish.
  Added Cloud 9 (economy), Ectoplasm made Egg Negative (+1 slot), Temperance for
  +$35 (economy fixed too late). Boss **The Tooth** (4000, lose $1/card):
  **DIED at 2937.** No pairs in the opening hand; ground out two-pairs across
  three banking hands, then the final Acrobat (x3) hand whiffed on pairing and
  only made a lone 99 pair (252). Run over.

## FINAL RESULT: Ante 3, best single hand 2,749, won=False

## Post-mortem

1. **Over-relied on Baron.** X1.5/King-held scored far below my model on
   two-pair hands (holding a King added almost nothing; only the 3-Kings-held
   Ace hand paid off). Baron wants MANY kings held or a different shell.
2. **Split my pairs across banking hands.** On The Tooth I spent KK, JJ, 66, 33
   on separate banking hands, leaving the decisive Acrobat (x3) hand to chance,
   and it never paired. Should have concentrated one big hand INTO the Acrobat
   play, banking only throwaway high-card-hold-King hands between.
3. **Economy too slow early.** Sat at $1-$3 for antes 1-3, skipping strong buys
   (Ancient Joker) until Temperance bailed me out at ante 3, too late to convert.
4. **Additive Mad + linear hand levels don't keep pace** with the exponential
   blind curve. Needed real multiplicative scaling (steel Kings, a second xMult
   joker, polychrome) locked in by ante 3. Never got it.

Next time: commit to the Baron shell HARD (steel Kings + more Kings via
standard packs) or pivot to a flush/xMult engine, thin the deck, bank economy
to $25 by ante 2, and reserve the Acrobat hand for a pre-built monster.
