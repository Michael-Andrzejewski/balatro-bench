# Balatro Benchmark Run — seed BENCHMRK, Red Deck, White Stake

## Build plan
Committed to a **Full House / Two Pair** core, because every cheap "contains X" joker
(Jolly = pair, Mad = two pair, The Duo = X2 on pair) fires simultaneously on a Full House.
Level Full House with Earth and Two Pair with Uranus (both plentiful in this seed's
Celestial packs). Scary Face (+30 chips per face card) is the chip engine since my
full houses are face-heavy.

Key seed-intel finding: the shop queue advances 2 items per shop view, and **each ante's
queue is used by the 3 shops that start with the shop after the previous ante's boss**.
So deep queue items (#20+) are essentially unreachable without heavy reroll money.

## Ante-by-ante

### Ante 1 — Boss: The Pillar
- Skipped Small Blind for **Coupon Tag** -> made the whole ante-1 shop free.
- Free: Mad Joker, Runner, Buffoon Pack (took Jolly Joker), Jumbo Celestial (took Uranus).
- Big Blind cleared with a full house JJJ66 (328).
- Boss (Pillar, 600) cleared in one hand: full house AA JJJ.
- **Best hand ante 1: 1584**

### Ante 2 — Boss: The Hook
- Rerolled once ($5) to reach **The Duo** (X2 Mult on pair) — the run's anchor joker.
- Sold Runner, bought **Scary Face** ($4) — nearly doubled scoring.
- Planets: Earth (Full House lvl2), Uranus (Two Pair lvl3).
- Boss cleared one-hand: full house 999QQ = 8256.
- **Best hand ante 2: 8256**

### Ante 3 — Boss: The Tooth
- Chased Cavendish (X3 Mult, analysis item #12) by rerolling to advance the queue.
  Queue drifted by one slot (Mad Joker was excluded as a duplicate) and Cavendish
  never appeared — $11 of rerolls wasted. Lesson: queue positions drift when you
  already own a listed joker.
- Planets: Uranus (Two Pair lvl4), Earth (Full House lvl3).
- Small 2000 cleared with full house QQQJJ = 12720 (all face cards + Scary Face).
- Boss (Tooth, 4000) cleared with two pair JJ77 = 8004.
- **Best hand ante 3: 12720**

### Ante 4 — Boss: The Water
- Bought **Photograph** (X2 Mult on first scored face card) and **Hiker** (+5 permanent
  chips per scored card). Used a Spectral **Ectoplasm** — it landed Negative on The Duo,
  giving a 6th joker slot at the cost of hand size 8 -> 7. **Immolate** gave +$20.
- Bought **Supernova**; it auto-placed after The Duo so its flat mult wasn't multiplied.
  Fixed with `rearrange` to push The Duo (and later Baseball Card) to the end.
  **Rule: flat-mult jokers must sit BEFORE X-mult jokers.**
- Missed the Telescope voucher by $1 on the last ante-4 shop.
- **Best hand ante 4: 20300**

### Ante 5 — Boss: The Club (all Clubs debuffed)
- Bought the **Reroll Surplus** voucher ($10, rerolls -$2) specifically to fund deep
  queue digs in antes 6-7. Took Earth from the Jumbo Celestial (Full House lvl4).
- Big Blind 16500 took two hands (14400 + 21460).
- Boss 22000 one-shot with QQQ JJ = 23940, even with the QC debuffed to zero.
- **Best hand ante 5: 23940**

### Ante 6 — Boss: The House (first hand face down)
- **The run's biggest upgrade.** Dug the shop queue across two shops using the cheap
  rerolls: 3 rerolls in shop 1 to reach Earth (#8), then 1 reroll in shop 2 to reach
  **Baseball Card** (#11, X1.5 Mult per Uncommon joker). Splitting the dig across two
  shops mattered — reroll cost resets each shop, so 3+1 rerolls cost $15 instead of
  the $25 a single 5-reroll dig would have cost.
- Sold **Mad Joker** (+10 Mult, ~20% of score) to free the slot. Baseball Card counts
  Supernova and Hiker -> **X2.25 Mult**, nearly doubling output.
- Bought a third Earth in shop 3 (#16). Full House now **level 6**.
- The House's face-down hand is still fully visible through the API, so it cost nothing.
- Boss 40000 one-shot with KKK JJ = 50955.
- **Best hand ante 6: 50955**

### Ante 7 — Small Blind 35000 — RUN ENDED HERE
- Shop: bought the **Telescope** voucher ($10) — every Celestial Pack now guarantees the
  planet for my most-played hand (Earth). Immediately cashed it in on a Mega Celestial
  (Earth + Venus) and a Jumbo Celestial (Earth). **Full House reached level 8.**
- Read ahead and found **The Trio (X3 Mult on three-of-a-kind) at ante-8 queue slot #25**,
  reachable with ~10 cheap rerolls spread across the three ante-8 shops. Also planned to
  skip the ante-7 Big Blind for the **Investment Tag** ($25 paid *after* the boss), because
  the ante-7 boss The Ox zeroes your money when you play your most-played hand (Full House).
  Neither plan got to happen.
- **What actually killed the run:** the Small Blind (35000). I opened with junk, and spent
  all 4 discards chasing a full house. I found KK QQ but never trips, so I banked a two
  pair for 12825 with **0 discards and 3 hands left**. The next three draws contained no
  pair better than 5s, so the remaining hands were pure card-cycling (276, 60, 300).
  Final: **13461 / 35000**.
- **Best hand ante 7: 12825**

## Post-mortem

**Final ante: 7. Best single hand: 50955 (KKK JJ, ante 6 boss). Won: no.**

**What ended the run:** not a scoring ceiling — a *variance* failure on the ante-7 Small
Blind. My build one-shot the ante-5 and ante-6 bosses (23940 vs 22000, 50955 vs 40000)
and would have one-shot ante 7's boss too. I lost to a blind I had roughly 8x the power
to beat, because I ran out of ways to find a full house.

**Concrete lessons:**

1. **Don't spend the last discard while the hand is still unbanked.** I went to 0 discards
   with 3 hands left. A hands-heavy, discard-empty position is nearly worthless with a
   made-hand build, because playing is a far worse way to cycle cards than discarding
   (5 cards per hand, and it consumes the resource that actually clears the blind).
   The rule should be: *never drop below 1 discard until the blind is already cleared.*
2. **A one-hand build needs a real fallback, and mine was a decoy.** I told myself Two
   Pair was the backup, but Two Pair was level 4 while Full House was level 8 — the gap
   had grown to 4x. A "fallback" that scores 12825 against a 35000 blind is not a
   fallback. I should have spent ~$4 on a couple of Uranus/Mercury levels so that a
   two pair could clear a small blind on its own, or picked Uranus over Venus in the
   ante-7 Jumbo Celestial (I took Venus for a three-of-a-kind I never played).
3. **Hand size is a scoring stat.** I traded 8 -> 7 hand size for the Ectoplasm joker slot
   at ante 4. That slot paid for itself, but every subsequent round I was searching for a
   5-card made hand out of 7 instead of 8. On the fatal round that missing card is very
   plausibly the difference. I was right to refuse a *second* Ectoplasm at ante 7.
4. **The seed intel is worth the most when spent early.** The two best purchases of the
   run — The Duo (ante 2, one reroll) and Baseball Card (ante 6, #11) — both came from
   deliberately digging the queue. The dig discipline that worked: **split rerolls across
   consecutive shops**, since reroll cost resets each shop (3+1 rerolls cost $15 where
   5 in one shop cost $25). The dig that failed (Cavendish, ante 3, ~$11 wasted) failed
   because **queue positions drift when you already own a listed joker.**
5. **Read the boss two rounds ahead, not one.** I only noticed The Ox's money-wipe when I
   was already standing in the blind-select screen, after I had shaped my whole economy
   plan around banking ~$60 for the ante-8 Trio dig.
