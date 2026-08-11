# Balatro Benchmark Run — Opus 5 (cold)

Deck: RED | Stake: WHITE | Seed: BENCHMRK

## Build plan (initial)
No prior knowledge of seed. Default strategy:
1. Prioritize a scaling mult joker + economy early.
2. Keep a consistent hand type (usually Pair/Two Pair/Flush) and level it with Planets.
3. Keep money >= $25 for max interest once survival is secure.
4. Never risk a blind fail — always check chip math before the last hand.

## Ante 1
State: Small 300 (Coupon Tag) | Big 450 (Polychrome Tag) | Boss = The Pillar
(cards played previously this ante are debuffed).

Decision: **Skip Small for Coupon Tag.**
Reasoning:
- Coupon Tag = entire next shop free. With $4 and 0 jokers, that's worth far more
  than the ~$3 small blind reward.
- The Pillar debuffs cards played earlier in the ante. Skipping Small means ~8-20
  fewer debuffed cards when I hit the Boss. Double win.
- Skipping both Small and Big was rejected: that would mean facing Boss 600 with
  zero jokers and no shop at all.

Big 450: dug JJJ66 full house (328), then a club flush (280) to close. 608 total.
Coupon shop was fully free: took Mad Joker, Runner, Jolly Joker (Buffoon pack),
Uranus (Two Pair lvl2). Passed Tarot Merchant voucher to keep $10 for economy.
Boss The Pillar (600): only needed any two-pair-ish hand since jokers key off hand
TYPE, not card scoring. Debuffed cards still count for hand detection.
**Best hand so far: 1584** (AAA+JJ full house, most cards debuffed).

## Ante 2
Skipped Small for **D6 Tag** (free rerolls) — needed to dig for a scaling joker.
Big 1200: no pairs in the opening hand; dug 4x down to QQ99 two pair = 1638.
Key shop: bought **The Duo (X2 Mult on pair)** — first real multiplicative scaling.
Sold Runner (dead in a pair build), bought **Swashbuckler** (scales off Egg's
growing sell value: +3 mult per round, forever).
Jumbo Celestial had no Earth -> took Uranus (Two Pair lvl3).

Engine now: Two Pair lvl3 (60 chips/4 mult), Full House lvl3 (90/8).
Mult chain: base + 10 (Mad) + 8 (Jolly) + 12 (Swash, growing) then X2 (Duo).
Boss The Hook (1600): dug three pairs -> KKK99 full house = **8832**, new best.

## Ante 3
Spectral Pack gave **Cryptid** -> made 2 extra copies of the Ace of Spades.
Deck now has 6 Aces. This was the pivotal deck decision of the run.
Skipped Big for **Meteor Tag** -> free Mega Celestial (2 picks): Uranus (Two Pair
lvl4) + Venus (Trips lvl2). No Earth offered.
Boss The Tooth (-$1 per card played; discards are FREE, so I dug hard):
AAA+TT full house = **10010**, new best. Money down to $1 though.

### MISTAKE (cost $4)
Opened a Buffoon Pack with 5/5 joker slots full -> couldn't take Cloud 9, and
`sell` is blocked during SMODS_BOOSTER_OPENED. **Always free a joker slot BEFORE
opening a Buffoon pack.** Same trap later made a Wraith/Ankh spectral unusable.

## Ante 4
Sold Jolly, bought **Fibonacci** (+8 mult per A/2/3/5/8 scored). With 6 Aces the
deck holds 22 of 54 Fibonacci-rank cards, so I now deliberately build hands out
of A/2/3/5/8 ranks.
Calibration from observed scores: Swashbuckler's REAL mult is about half its
displayed number. Full House mult = (8 + 10 Mad + ~14 Swash + 8*FibCount) x2.
Big 7500: TTT+55 (two Fib cards) = **12350**, new best. Note TTT+55 beat TTT+KK
(8680) purely because of Fibonacci — rank choice matters more than card chips now.
Bought **Telescope** ($10): every Celestial Pack now guarantees an Earth
(Full House is my most-played hand). Plan: convert all future money into
Celestial packs to push Full House levels, since additive mult alone won't
keep up with exponential blind scaling.

## Ante 5 — the STEEL discovery (the run's turning point)
Mega Spectral ($8), 2 picks. Took **Immolate first** (destroy 5 random cards in
hand, +$20) so its destruction couldn't eat the Aces that **Grim** was about to
add. Money $4 -> $24, and 5 junk cards left the deck. Then Grim: destroy 1 card,
add 2 random *Enhanced* Aces -> one arrived as an **Ace of Spades (STEEL)**.
Bought **Reroll Surplus** ($10, rerolls -$2 forever) and **The Chariot** ($3).

**Key realization:** Steel = X1.5 Mult *while the card stays in hand* (unplayed).
That is MULTIPLICATIVE and it stacks. My additive mult was flattening out; steel
was the first thing that actually scaled. From here the rule became:
**steel my junk cards, then deliberately hold them instead of playing them.**
Chariot went on QD (a card I would never score anyway) -> holding AS(steel) +
QD(steel) = X2.25.
Big 16500: a *two pair* of 5s and 2s with five Fibonacci cards = **20915**.
Boss The Club (22000): drew QD(steel) and had QQQ available — deliberately did
NOT play it, kept it in hand for the X1.5, and played AAA+QQ instead = **27985**.

## Ante 6 — the restructure (X1.75 Throwback + Baseball Card)
Shop showed **Throwback: X0.25 Mult per blind skipped this run (X1.75 already)**
for $6 and I only had $5. Sold **Egg for $32** (it had been quietly accruing $3
of sell value every round since ante 2).
This was the biggest decision of the run. Egg only fed Swashbuckler, and
measured against real scores Swashbuckler was contributing far less mult than
its displayed number. Trading a slow additive engine for an immediate
multiplicative one was clearly right: X2 (Duo) -> X3.5 instantly.
With the $32 I also took **Earth** twice (Full House lvl5 -> lvl7).

**Skipped Ante 6 Small** — with Throwback owned, every skip is now +X0.25
*permanently*, which beats the ~$8 blind reward. Throwback -> X2.
The Standard Tag paid out a Mega Standard Pack containing a **second
7H(STEEL)**, so I could now hold two steels at once again.
Big 30000: drew AAA+KK while holding BOTH steel 7s = **79352**. (Previous best
was 27985 — this one hand nearly tripled it.)

Bought **Baseball Card ($8): X1.5 Mult per Uncommon Joker.** With Fibonacci and
Throwback both Uncommon that is ~X2.25 on its own. Then sold the now-dead
Swashbuckler to open a slot and took **Zany Joker (+12 Mult on Three of a Kind)**
from a Buffoon Pack — my full houses always contain trips, so it always fires.

Boss The House (40000, first hand face down): dug 4 times, never found trips,
but ended holding three pairs. Chose **AA+33+5S** over AA+TT+5S: 113 chips vs
127, but five Fibonacci cards (+40 mult) instead of three (+24). The
lower-chip hand won by a mile — **53946**, one hand, boss cleared.

### Current engine (entering Ante 7)
Chips: Full House lvl7 (190/16), Two Pair lvl4 (80/5).
Additive: hand base + 12 (Zany, on trips) + 8 x (Fibonacci ranks scored).
Multiplicative: X2 Duo * X2 Throwback * ~X2.25 Baseball * X1.5 per steel held.
4 steel cards in deck (AS, QD, 7H, 7H). Deck is ~6 Aces + heavy A/2/3/5/8.

## Ante 7 — the SCORING-CARDS discovery (the biggest correction of the run)
For several antes my score predictions were 2-4x too high, and the error was
worst on Pair / Two Pair hands and smallest on Full Houses. Two data points
finally pinned it: a Pair scored 13122 and a later Pair scored 8201, both far
under my model.

**Kickers do not score.** Only the cards that actually FORM the poker hand are
scored — so a Pair scores 2 cards, Two Pair 4, Full House 5. Every "Fibonacci
kicker" I had been counting (+8 mult each) was contributing exactly nothing.
Re-deriving with that rule predicted 13121 against an actual 13122.

Corrected model, verified to within 1 point:

    score = (handLevelChips + chips of SCORING cards)
          x (handLevelMult + additive joker mult + 8 x FibCount among SCORING cards)
          x (product of all xMult sources)

This changed play immediately. At the Ante 7 boss I had been about to play a
Pair; I switched to AA+66 two pair (4 scoring cards instead of 2) and scored
**54538** to clear it. It also permanently settled the Full-House-only policy:
5 scoring cards vs 2 is roughly an 8x swing, so a full house is worth digging
several discards for even when a pair is sitting there.

Other Ante 7 business:
- Economy finally fixed: **Investment Tag** (+$25 after the boss) and
  **The Hermit** (doubles money) pulled me out of a chronic $0-$13 hole.
- **Strength** on KD -> AD gave a 7th Ace. Aces are both my trips source and a
  Fibonacci rank, so Ace density is the single best deck stat I have.
- Skipped a Standard Pack of QD/6S/JH outright. Adding junk cards dilutes Ace
  and Fibonacci density; a "free" card is negative value in a tuned deck.
- Best hands this ante: **155172**, and a 75861 round total.

## Ante 8 — Mr. Bones, discard-fishing, and the win
Bought **Mr. Bones** ($5) and let Zany Joker go for the slot. Reasoning: my
score headroom was enormous (~470k against a 100k boss), so raw power was not
the risk — *whiffing the full house* was. Trading +12 additive mult for an
effective extra life was clearly correct at that ratio.

**Discard-fishing became the core technique.** Once a full house is already
made, spare discards cost nothing, so I spent every one of them throwing away
only non-scoring cards to fish for a second Steel card. Two steels held is
X22.78 versus X15.19 for one — a 50% score swing for free.

Small blind (50000): AAA+33, five Fibonacci cards, holding 7H(STEEL) and
4D(STEEL) -> **719523**.

Big blind (75000): drew AAA+22 plus AS(STEEL) with one discard left. No second
steel appeared, so I used the *hands* to fish instead — played 9C alone, then
TS alone, then 5H alone, cycling one junk card per hand while keeping AAA+22
intact, then played the full house on the last hand: **755790** (a Lucky Ace
proc'd for +20 mult). **New best hand.** Round total 757144.

Note the technique: with 4 hands and a target I could clear with one, playing
single junk cards is a free extra discard. It cost nothing and gained ~370k.

### Boss: Cerulean Bell (100000) — "forces 1 card to always be selected"
This effect is invisible in the API state, and I diagnosed it from a side
effect: my 4-card discards were removing **5** cards. The boss silently adds
one card of its choosing to every selection. That is how I lost 7H(STEEL) and
a needed TH mid-dig.

Practical consequences:
- Every discard is (n+1) cards, so discard fewer than you think.
- A 5-card play must already contain the forced card, so play the full house
  as soon as you have it rather than cycling.
Dug through three discards from a dead hand to 666+AA, played it holding
8H(STEEL): **380902** vs a 100000 target. **Ante 8 cleared — won=True.**

(Earlier that shop, Strength had turned 7H(STEEL) into **8H(STEEL)** — a steel
card on a Fibonacci rank, which is the ideal steel: it is worth holding for
X1.5 but still worth +8 mult on the rare occasion you must play it.)

### Server hang after the win
Immediately after `won=True`, buying a Jumbo Arcana Pack left the API stuck in
`SMODS_BOOSTER_OPENED` with no pack open: every `pack` pick timed out, `skip`
cleared the cards but the state never returned to SHOP, and all other endpoints
rejected on state. Five minutes of polling changed nothing. The win overlay in
the game window was blocking input; a manual dismissal unstuck it and the run
continued normally. Worth knowing for future runs — this is not recoverable
through the API.

## Ante 9 — the Throwback/skip engine pays off
Skipped both Small and Big. Two reasons: with Throwback each skip is a
permanent +X0.25 (X2.25 -> X2.75, about +22%), and the **Garbage Tag** paid out
**$14** for unused discards, which fixed a $1 bankroll. Coupon Tag from the
second skip made the following shop entirely free.

Boss **The Needle** ("play only 1 hand", 110000). One hand and four discards is
the ideal shape for this deck: discards are free, so I dug three times — first
to AAA, then to a hand holding **three steels** (QD, 8H, 4D) with **AAA + 88**
playable, every scoring card a Fibonacci rank.

    chips 389 x mult 68 x (2 Duo x 2.75 Throwback x 3.375 Baseball x 3.375 steel)
    = 1,657,176 in one hand

That also let me finally pin **Baseball Card at X3.375**, i.e. three Uncommon
jokers — Fibonacci, Throwback **and Mr. Bones**. Mr. Bones was not just
insurance; it was worth X1.5 on its own. That killed any thought of selling it.

## Ante 10 — steel supply and Full House levels
Free (Coupon) shop, then paid shops. Key acquisitions:
- **Earth** from a Celestial Pack (Telescope guarantees it) -> Full House lvl14
  (365 chips / 30 mult).
- **3H(STEEL)** from a Jumbo Standard Pack — a 6th steel, again on a Fib rank.
- **The Hanged Man** to destroy two dead cards (TC, 9S). Deck thinning is a real
  upgrade in a tuned deck: every junk card removed raises Ace and Fibonacci
  density on every future draw.
- **The Chariot** on a dead JS -> 7th steel.

Mistake worth recording: I **rerolled away a $0 Scholar** in the Coupon shop.
When a shop is free, buy everything worth having *before* rerolling — the
reroll reprices the new cards at full cost and the free items are gone.

Small (560000): AAA+33 holding two steels = **1,161,585**.
Big (840000): AAA+55 holding two steels = **1,646,400**.
Boss **The Fish** (1120000, "cards drawn face down after each hand played"):
the API still reports face-down cards by name, so hand-cycling kept working. I
had AAA+88 but zero steels — only ~577k, well short. Threw away three junk
cards as a High Card hand and drew **8H(STEEL)**; threw two more and drew
**6C(STEEL) and 3H(STEEL)**. Then AAA + 88(bonus) holding three steels:

    chips 444 x mult 70 x 62.65 = **1,947,113**  <- best single hand of the run

## Ante 11 — the wall, and the Mr. Bones gambit
Ante 11 is 7.2M / 10.8M / 14.4M. My ceiling was ~2M per hand, so no blind here
was winnable on merit. That made it a pure optimisation over *how* to fail.

Mr. Bones passes exactly one blind, provided the round total reaches 25% of the
target. So the question was which blind to spend it on. I skipped Small and Big
(Throwback X2.75 -> **X3.25**) specifically to aim Mr. Bones at the **boss**,
because surviving a boss advances the ante — the only line that could reach
ante 12. Failing anywhere in ante 11 reports the same ante, so this line had
free upside.

It did not come off, and the reason is instructive: **The Manacle removes one
hand-size**. At 7 cards, a 5-card full house leaves only 2 slots for steels
instead of 3 — a straight X1.5 cut, dropping my full house from ~2.0M to
~1.5M. I needed 3.6M (25% of 14.4M) and finished on **1,635,243**:

    AAA+55 holding 2 steels ... 1,513,358
    two churn hands ..............  3,719
    AA+66 two pair (final) .....  118,166

Two full houses would have cleared it, but with 4 discards spent finding the
first one and no discards left, the re-draws never produced a second.

## POST-MORTEM

**Final ante: 11. Best single hand: 1,947,113. Won: true** (Ante 8 boss beaten
at ante 8; the run continued into endless and ended in ante 11).

**What ended the run:** the Ante 11 boss, The Manacle (14,400,000, -1 hand
size). I scored 1,635,243 — above nothing that mattered except that it fell
short of the 3,600,000 needed for Mr. Bones to trigger, so there was no save.
The proximate cause was the hand-size reduction cutting me from three held
steel cards to two; the underlying cause is that ante 11 demands ~7x ante 10
and my engine only grew ~1.2x per ante by that point.

**The engine that got there:**

    chips  = Full House lvl14 (365) + scoring card chips (~80)
    mult   = 30 + 8 x (Fibonacci ranks among the five SCORING cards)
    xMult  = 2 (Duo) x 3.25 (Throwback) x 3.375 (Baseball) x 1.5^(steels held)

**Lessons for a future attempt on BENCHMRK:**

1. **Only scoring cards count.** Kickers give no chips and no Fibonacci mult. I
   played four antes on a model that was 2-4x wrong. Commit to Full House (5
   scoring cards) early; Two Pair is roughly one eighth the output.
2. **Steel is the scaler; hold it, never play it.** X1.5 each, multiplicative,
   stacking. Buy every Chariot. Steel your *dead* cards (Q, J, 10) — it turns a
   liability into a multiplier. Prefer steels on Fibonacci ranks so they still
   pay when a boss forces you to play them.
3. **Hand size is a steel cap.** With 8 cards you hold 3 steels alongside a
   5-card full house. Anything that cuts hand size (The Manacle) costs a flat
   X1.5. Buy hand-size upgrades if offered — I never saw one and never looked.
4. **Spare hands are extra discards.** Once a full house is made and the target
   is already covered, play single junk cards to cycle and fish for steels.
   This was worth ~370k at ante 8 and turned a 577k boss hand into 1.95M at
   ante 10. It is free.
5. **Baseball Card counts jokers you might otherwise dismiss.** Mr. Bones was
   an Uncommon and therefore worth X1.5 on top of being an extra life. Check
   rarity before selling anything while Baseball is in play.
6. **Throwback makes skipping strictly good, and tags pay.** Garbage Tag alone
   returned $14. Once Throwback is owned, skip every Small and Big you do not
   need the money or the shop from.
7. **Free shops: buy first, reroll last.** I rerolled a $0 Scholar into
   oblivion.
8. **Free a joker slot before opening any Buffoon Pack** — `sell` is blocked
   while a booster is open. This cost me Cloud 9 at ante 3.
9. **Deck thinning beats deck filling.** Skip junk cards from Standard Packs;
   spend Hanged Man on dead ranks. Ace density is the single best stat in this
   build (Cryptid at ante 3 into 8 total Aces was the run's foundation).
10. **The realistic ceiling on this line is ante 11.** To go further the run
    needs a second *multiplicative* joker slot's worth of power by ante 9 —
    something like a second copy of Baseball/Duo (Invisible Joker, Blueprint,
    Brainstorm) or far more Full House levels. Additive mult and card chips are
    already irrelevant at that scale.

---

# RUN 2 — same seed (BENCHMRK), informed by the above

## Plan going in
Run 1 ended at ante 11 with a ~2M ceiling. The engine's growth per ante (~1.2x)
lost to the blind curve (~1.5x, then 7x into ante 11). So run 2 is not about
playing the same line more cleanly — it is about finding a *second* source of
multiplicative growth. Targets, in priority order:

1. **Mime** (Uncommon) — retriggers held-in-hand effects, which means every
   Steel card fires twice: X1.5 becomes X2.25. With 3 steels held that is
   1.5^6 = X11.4 instead of X3.375, a **3.4x** whole-score multiplier, and it
   also feeds Baseball Card as a 4th Uncommon (X3.375 -> X5.06). This single
   card is worth more than everything I bought after ante 9 last time.
2. **Hand size** — every +1 hand size is another held Steel = flat X1.5 (X2.25
   with Mime). Paint Brush / Palette vouchers, Turtle Bean, Juggler. I never
   even looked for these last run; The Manacle's -1 hand size is what actually
   killed me.
3. **Blueprint / Brainstorm** — copy Baseball Card (X3.375) or Duo (X2).
4. **Red Seal on a Steel card** (Deja Vu tarot) — retriggers that one card, so
   that steel becomes X2.25 on its own. Stacks with Mime.
5. Everything else as run 1: Duo, Fibonacci, Throwback, Baseball, Mr. Bones,
   Telescope + Earths, Cryptid Aces, buy every Chariot.

Known-deterministic seed facts to exploit (shop RNG in Balatro is keyed on
seed+ante+slot, so offerings should repeat): Ante 1 Small = Coupon Tag, Big =
Polychrome Tag, Boss = The Pillar. Ante 2 Small = D6 Tag; Duo and Swashbuckler
in shop. Ante 3 Spectral Pack contains **Cryptid**; Big = Meteor Tag. Ante 4
Fibonacci + Telescope. Ante 5 Mega Spectral = Immolate + Grim. Ante 6 Throwback
$6 and Baseball Card $8. Ante 7 Investment Tag + The Hermit. Ante 8 Mr. Bones.
Bosses met later: A8 Cerulean Bell (forces 1 card into every selection), A9 The
Needle (1 hand only), A10 The Fish (face-down draws), A11 The Manacle (-1 hand
size — plan around it this time).

Also fixed from run 1: commit to Full House immediately (only scoring cards
count), never open a Buffoon Pack with 5/5 jokers, buy before rerolling in a
free shop, and use spare hands as extra discards to fish for steels.

## Key discovery this run: joker ORDER matters

Joker effects resolve strictly left-to-right. Additive mult applied *after* an
xMult joker gets multiplied by nothing. Caught this at the ante 3 boss when I
predicted 19,201 and scored 13,926 — factoring 13926 = 211 x 66 showed chips
were exactly right and mult was short. Order was Mad(+10), DL, Duo(x2),
Throwback(x1.75), Brainstorm(+10): ((6+10) x 2 x 1.75) + 10 = 66, not 91.

**Rule: every additive-mult joker must sit LEFT of every xMult joker.** And
since Brainstorm copies the *leftmost* joker, the leftmost slot holds Fibonacci
with Brainstorm immediately second — so every Fibonacci-rank scoring card is
worth +16 mult, not +8. Every score prediction since has been exact.

Current verified formula:
`score = (handLevelChips + scoring-card chips + joker flat chips)
       x (handLevelMult + additive mult + 16 x FibCount)
       x (product of all xMult, incl. X1.5 per Steel card HELD in hand)`

## Run 2 build (through ante 6)

Jokers, in order: Fibonacci | Brainstorm(Foil,+50 chips) | Driver's License |
The Duo | Throwback(Negative) | Drunkard.

Deviations from run 1 that paid off:
- **Ante 1 Buffoon: took Driver's License over Jolly Joker.** X3 Mult at 16+
  Enhanced cards in deck — this is the "second multiplicative source" that run
  1's post-mortem said was the missing piece. It is a dead slot until it fires,
  which is the gamble.
- **Throwback and Brainstorm both acquired at ante 3** instead of ante 6.
- **Ante 5 Mega Spectral: Grim + Ectoplasm** (run 1's notes said Immolate +
  Grim; the pack actually held 4). Grim destroyed an Ace and gave AS(STEEL) +
  AH(LUCKY). Ectoplasm put Negative on Throwback: **6 joker slots, -1 hand
  size**. Traded hand size for a slot — reserving it for Baseball Card.
- **Ante 7: bought Tarot Merchant ($10)** the moment it appeared. Run 1 lost
  this voucher by deferring it one shop; vouchers refresh per ante.

Enhanced-card count for Driver's License: 4 -> 12 across antes 5-6, via Grim
(+2), The Tower ($3, Stone), two Chariots (Steel), and Standard/Mega Standard
pack picks. Need 4 more.

Steel cards held are the other scaler: AS, 9D, KH, 7H, 7C are all Steel now.
With hand size 7 I play 5 and hold 2, so I only capture X1.5 (occasionally
X2.25). Steel *density* is what matters, not count — hence buying every Chariot.

### Ante-by-ante (run 2)
- A1-A4: build phase. Best hand at end of A4 = **69,552** (run 1 was 12,350 at
  the same point, ~5.6x ahead).
- A5 Small 11,000: played 444+22 and **held** the AS(MULT,BLUESEAL) instead of
  playing it — Blue Seal makes a free Earth for the round's final hand type.
  30,408. Dumped The Star first so the free Planet had a slot to land in.
- A5 Big 16,500: 36,608.
- A5 Boss **The Club** (all Clubs debuffed): nearly died. Ran out of discards
  with no pair, burned two hands as cycles, cleared it on a spade **Flush**
  (15,776) for 24,757/22,000. Note Duo did *not* fire — a flush contains no
  pair. Lesson: the full-house engine is fragile when a suit is debuffed.
- A6 Small 20,000: **143,256** — new best hand. AAA+33 with a Steel held.
- A6 Big 30,000: 94,752 (555+AA, no steel held).
- A6 Boss **The House** 40,000: drew four Aces, played Four of a Kind (which is
  at level 2) holding 7H(STEEL) — 81,696.

Money has been the binding constraint all run; I have played every blind from
ante 5 onward rather than skipping, which costs Throwback growth (still X2).

- A7: bought the **Tarot Merchant** voucher (tarots appear 2x more often in
  shops) specifically to hunt enhancement tarots for Driver's License. Records
  147,204 then **254,664** at the A7 boss (**The Ox**). At the Ox I
  deliberately discarded a *third* Steel card — a 5-card play only holds 2, so
  the third steel was dead weight — for an ~18% shot at completing a full
  house. It hit. Also picked up **Wily Joker** (+100 chips on any
  three-of-a-kind, so it fires on every full house, ~+38% for $4) and sold
  Drunkard to make room. Full House reached lvl 9.
- A8 money fix: chained **The Hermit** ($3, doubles money, max +$20) with
  **Temperance** and an Investment Tag to turn $2 into $34. Hermit is the best
  $3 in the game once you are above ~$18 — buy it *before* spending, then use
  it immediately in the shop (no card targets, so it works in SHOP state).
- A8 Small 50,000: 58,866. Played 2S+2C+KD(STONE) as a **Pair** — only 3 cards
  played, so 4 stayed in hand and **three were Steel** (X3.375). Core insight:
  a 3-card play holding 3 steels beats a 5-card play holding 2 (X2.25)
  whenever the hand-level gap is small. Steel is a *hold* multiplier; every
  extra card you play costs you a potential 1.5x.
- A8 Big 75,000: **353,889** — new best. AAA33 full house, all five cards
  Fibonacci ranks (+16 mult each). Key move: the full house was locked after
  one discard, so I spent the remaining discards throwing away the two
  *non-scoring* cards to fish for a Steel to hold. Third try drew KH(STEEL) →
  a free X1.5 on the whole hand. **Always burn spare discards on non-scoring
  cards to fish for steels.**

## Driver's License finally came online (ante 8 boss)

Sat at 13/16 enhanced cards for three antes as a dead joker slot. Closed it
with **The Hierophant** ($3, enhances 2 cards to Bonus) → 15, then **Death**
($3, "convert the left card into the right card") using an unenhanced card as
the left and 7C(STEEL) as the right → 16. Death is the sleeper card: it adds
an enhanced card *and* duplicates your best card. Target order is by hand
index — the victim must sit at a **lower index** than the template.

X3 Mult, live from the ante 8 boss onward.

- A8 Boss **Cerulean Bell** (forces 1 card to always be selected) 100,000:
  cleared in three hands (59,535 + 26,352 + 56,700). The forced card
  re-randomises after every action and *drags itself into your discards* — it
  ate one of my Steel 7s. Against Cerulean Bell, assume every selection may
  contain one extra card you did not choose.

## Ante 9 build

Sold Wily Joker to buy **The Trio** ($8, X3 Mult on any three-of-a-kind — so
it fires on every full house). Bought two Earths from a Mega Celestial;
Full House is now **lvl 12 (315 chips / 26 mult)**.

Joker order (left to right, additive first, xMult last):
Fibonacci | Brainstorm(Foil) | Driver's License | The Duo | Throwback(Negative)
| The Trio

Full-house xMult stack is now 2 (Duo) x 2.25 (Throwback) x 3 (DL) x 3 (Trio)
= **X40.5** before Steel holds. An AAA33 with two steels held projects to
~4.2M.

### Ante 9 results
- A9 Small 110,000: drew four Aces and TT. Played AS(MULT,BLUESEAL) + AC + AC
  + TC + TC(GLASS,HOLO), holding AS(STEEL) + 9D(STEEL) → **6,322,981**, the
  best hand of either run (3.2x run 1's 1,947,113). I chose to *play* the
  Blue Seal ace rather than hold it, giving up a free Earth for +57% score.
- A9 Big 165,000: AAA77 full house, one steel held, and the Lucky Ace hit its
  1-in-5 for +20 mult → 2,723,544.
- A9 Boss **The Window** (all Diamonds debuffed) 220,000: **died at
  186,957 / 220,000.**

# POST-MORTEM (run 2)

**Final ante: 9. Best single hand: 6,322,981. Result: lost at the ante 9
boss.** (Run 1: ante 11, best hand 1,947,113.) Higher ceiling, shorter run.

## What actually killed the run

Not the boss effect — I only had two Diamonds in play all round. **I could not
make a pair.** Across four consecutive draws at The Window I never held two
cards of the same rank. The whole engine is conditional:

- The Duo X2 needs a Pair
- The Trio X3 needs a Three of a Kind
- Full House lvl14 (365/30) needs a full house
- Fibonacci/Brainstorm's +16/card needs A/2/3/5/8 to *score*

With no pair the stack collapses from X40.5 to X6.75 and the hand level drops
from 365/30 to 5/1. My final hand was worth 29,948 where a Pair of Aces would
have been 84,686 and a full house 4.5M. **A ~150x swing on one coin flip.**

## The three concrete mistakes

1. **I never thinned the deck.** I *added* cards (two Standard Pack picks) and
   only bought one Hanged Man, which I then wasted. By ante 9 the deck was
   ~56 cards spanning 13 ranks, so a pair in 7 cards was far from guaranteed.
   **Fix: buy The Hanged Man every single time it appears and destroy
   non-Fibonacci ranks (4, 6, 7, 9, 10, J, Q, K).** A deck of mostly
   A/2/3/5/8 makes pairs automatic *and* makes every scoring card +16 mult.
   This is the single highest-value change for a future run.
2. **I spent all four discards before scoring anything.** At The Window I
   burned discards 1-4 hunting a full house I did not need, then had to spend
   two of four *hands* as cycles, and arrived at the last hand with nothing.
   **Fix at a boss: score first, then optimise.** Bank a clearing hand while
   you still hold discards; the target is cumulative across hands, so a safe
   150k + a safe 100k beats one 4M attempt that misses.
3. **I stopped skipping blinds.** Throwback froze at X2.25 (9 skips) from
   ante 5 onward because I played every blind for money. Each skip is +0.25 =
   +11% on *every* hand, and skip tags (Orbital = +3 hand levels) are often
   worth more than a shop. I passed on an Orbital Tag at ante 9 while sitting
   on an engine that cleared the Big Blind 16x over.

## What to repeat

- **Joker order is everything**: Fibonacci | Brainstorm(Foil) | Driver's
  License | Duo | Throwback | Trio. Additive left, xMult right, Brainstorm
  second so it copies Fibonacci.
- **The Trio ($8) is the best purchase in the run** — X3 on every full house.
  Sell anything flat (Wily's +100 chips) to fit it.
- **Steel is a HOLD multiplier.** Count held steels before choosing hand size.
  A 3-card play holding 3 steels (X3.375) often beats a 5-card play holding 2.
- **Burn spare discards on non-scoring cards to fish for steels** once the
  scoring hand is locked. This is free and produced the 353,889 hand.
- **Death and The Hierophant** are the cheap route to Driver's License;
  The Hermit is the cheap route to money.
- Every score prediction was exact once joker order was fixed, except when a
  Glass card or Lucky card fired. Trust the formula.

## The build to aim for next time on BENCHMRK

Same six jokers, but reach them by ante 6 instead of ante 9, and spend every
spare $3 on Hanged Man / enhancement tarots rather than Standard Packs. The
ceiling (6.3M at ante 9 with a half-built deck) is high enough to clear ante
11's 14.4M boss over four hands — the only thing missing is a deck that
reliably produces the hand.

# OPERATOR NOTES — READ THIS FIRST, IT OVERRIDES THE ABOVE

The benchmark operator has played this seed and reached **~450 million**. That
is the bar. They still lost, to the boss **Amber Acorn**, because taking
Hieroglyph + Petroglyph shifted the ante numbering onto it and Amber Acorn
**flips and shuffles all Jokers** — which destroys an order-dependent build.
`rearrange {"jokers":[...]}` exists; use it to restore order if this happens.

Corrections to everything I concluded above:

1. **BUY VOUCHERS.** I skipped nearly every voucher across two runs. They are
   strong. Use judgement (Blank does nothing on its own, but it gates
   Antimatter, +1 joker slot; Hieroglyph gates Petroglyph).
2. **Hieroglyph is good.** -1 Ante for -1 hand buys a whole extra ante of
   shops and scaling. Take it — but expect the boss line-up to shift.
3. **~~Skip blinds for Throwback~~ — WRONG.** Skip-off jokers are bad.
   Skipping a blind also skips its money and its shop, and those are the real
   constraints. Do not build around Throwback. **Play the blinds.**
4. **Money floor $25.** That is max interest ($5/round). Stay above it and
   spend only the surplus — on **rerolls**, digging for good shop items. Both
   my runs limped along at $6-8 for entire antes; that is why the builds were
   late and thin.
5. **Ectoplasm's -1 hand size is severe.** I took it in run 2 and spent the
   rest of the run at 7 cards, which is a direct cause of the pair-drought
   that ended the run. Only take it for a certain, immediate payoff.
6. **There is a Blueprint in this seed** if you reroll deep enough. Blueprint
   copies the joker to its **right** — park it immediately left of The Trio
   (or the biggest xMult joker) for a second X3. Pairs with Brainstorm, which
   copies the **leftmost** joker.
7. **Score is a first-class goal, not just a tiebreak.** Aim for the highest
   and largest score, not merely survival.

Everything about joker ORDER, Steel being a HOLD multiplier, deck thinning
with The Hanged Man, and the verified scoring formula still stands.

# RUN 3 (seed BENCHMRK, RED/WHITE)

Plan going in: play every blind, buy vouchers, hold $25+, reroll the surplus to
dig for Blueprint, no Ectoplasm, keep additive jokers left of xMult jokers.

**It ended at the ante-1 boss. This is the worst result of the three runs and
it was caused by one decision, not by bad luck.**

### Play-by-play
- Hand size 8 this time (no Ectoplasm). A1 Small 300: full house JJJ+66 = 328.
  Cash out $10.
- Shop 1: bought the **Tarot Merchant** voucher ($10 -> $0). Reasoning: doubled
  tarot frequency compounds, and tarots fix the deck-thinning/enhancement
  failure mode from run 2.
- A1 Big 450: 372 (AAA+JJ, deliberately withholding JD so it stayed undebuffed
  for The Pillar) + 96 (two pair) = 468. Cash out $6.
- Shop 2: Arcana Pack $4 -> **Justice** on KC, my first Glass card. $2 left.
- A1 Boss **The Pillar** 600: full house QQQ + KK(GLASS) = **720** in one hand.
  Predicted 720 exactly. Best hand of the run. Cash out $10.
- Shop 3: **Hieroglyph $10**. This took ante 2 back to ante 1, hand size 4 -> 3,
  and left me at **$0 with zero jokers**.
- A1' Small 300: spade flush AS KS QS JS 6S = 328. Cash out $5.
- Shop 4: Buffoon Pack $4 -> **Driver's License** over Jolly Joker. $1 left.
- A1' Big 450: four Queens = **700**. Cash out $7.
- Shop 5: bought Justice $3 ($4 left), skipped the $4 Standard Pack to start
  rebuilding money.
- A1' Boss **The Hook** 600 (discards 2 random cards per hand played): glassed
  the AS, then burned all 3 remaining discards hunting a full house that never
  came. Played two pair AA+KK with both Glass cards = 496. Hook then stripped
  my King. Pair of 4s = 36 (532). Final draw was KD QD 9S 8D 6C 5C 4C 3S —
  eight distinct ranks, no pair, no flush, no straight. Best legal hand was a
  high card worth 15. **Died 547 / 600.**

# POST-MORTEM (run 3)

**Final ante: 1. Best single hand: 720. Result: lost at The Hook.**
(Run 1: ante 11 / 1,947,113. Run 2: ante 9 / 6,322,981.)

## What actually killed the run

**Buying Hieroglyph at $10 when I had $10, zero jokers, and no engine.**

Hieroglyph is a good voucher and the operator is right about it — but it is a
*scaling* voucher. It converts a hand per round into an extra ante of shops.
That trade only pays if you have something to buy with. I paid for it by going
to $0 with an empty joker row, and then had to survive three more blinds at
**3 hands instead of 4** with essentially no jokers. The -1 hand is what killed
me: at The Hook I had banked 532 of 600 with one hand left, and a fourth hand
would have cleared it trivially. I lost by 53 chips having spent a hand on the
voucher three rounds earlier.

Corollary I got wrong: I read "buy vouchers" as "buy vouchers immediately."
The real rule is buy vouchers *out of surplus*. The $25 money floor and the
voucher rule are the same rule — **never let a purchase take you to $0.**

## The other two mistakes

1. **I burned all 4 discards before scoring anything at the boss**, which is
   the exact mistake run 2's post-mortem told me not to make ("score first,
   then optimise"). I had AA + KK + JJ in hand at The Hook — a guaranteed 496 —
   and spent two discards chasing a third Ace. Writing the lesson down did not
   stop me repeating it, because I only re-read the journal before the run and
   not at the decision point.
2. **I misplayed The Hook specifically.** Its effect is "discards 2 random
   cards per hand played," which means every hand you play degrades your hand
   for the next one. Against The Hook the correct plan is to score the whole
   target in as few hands as possible, using discards to *build one big hand*,
   not to bank a partial score and rely on follow-ups. I did the opposite:
   spent discards early, then relied on two follow-up hands from a deck the
   boss was actively strip-mining.

## Rules for the next attempt on BENCHMRK

1. **Never buy down to $0.** Keep at least ~$5 (the interest threshold) at all
   times, and prefer the purchase that keeps a joker slot filling over the one
   that scales. Vouchers come out of surplus, not out of rent.
2. **Do not take Hieroglyph before you have 2-3 working jokers.** The -1 hand
   is charged immediately; the extra ante only pays later. It re-offers.
3. **A joker in the row beats a voucher in the ledger at ante 1.** I played
   five of six ante-1 blinds with zero or one joker.
4. **Against The Hook: fewest hands possible.** Every played hand costs 2 more
   random cards.
5. **Score first, then optimise** — bank a clearing hand while discards remain.
   This is now the second run in a row ended by ignoring it.
6. Everything in the OPERATOR NOTES above still stands; the failure here was
   sequencing, not strategy.

# RUN 4 (seed BENCHMRK, RED/WHITE)

Operating rules stated up front: jokers before vouchers, never buy down to $0,
bank a clearing hand at bosses before optimising, additive jokers left of xMult.

### The build

Final engine, in order (order matters, additive left of xMult):

```
Mad Joker [Negative]  +10 Mult if hand contains a Two Pair
Fibonacci             +8 Mult per played A/2/3/5/8
The Duo               X2 Mult if hand contains a Pair
Driver's License      X3 Mult at 16+ Enhanced cards  [Foil: +50 chips]
Juggler               +1 hand size
Drunkard              +1 discard each round
```

Vouchers: Tarot Merchant, Hieroglyph, Telescope, Tarot Tycoon, Reroll Surplus.
Hand levels: Full House 5, Four of a Kind 2.

### Play-by-play

- **A1** Shop 1 offered the Tarot Merchant voucher *and* a Buffoon Pack. Took
  the pack (Jolly Joker over Driver's License — tempo beats a joker that needs
  16 enhanced cards at ante 1) and deferred the voucher one shop. This is the
  run-3 lesson applied: a joker in the row beats a voucher in the ledger.
- **A2** Chained The Hermit $14 -> $11 -> $22, *then* bought Hieroglyph, which
  left $12 instead of $0. Same voucher that ended run 3, bought correctly.
- **A1'/A2** The Pillar twice: played **trips** rather than a full house both
  times so the premium ranks stayed undebuffed. 660 each.
- **The Hook**: realised discarding is free against it (it only punishes *played*
  hands). Burned discards to build one hand, one-shot it for **3,276**.
- **The Wheel** (4000): missed the full house, banked two pair 77+66 = 3,840,
  then finished with an **Ace-low straight A-2-3-4-5** = 420.
- **A3 Big**: full house AAA+KK = **12,768**.
- **A4** The Club (all Clubs debuffed) 10,000: discarded into 333+88, both
  Fibonacci ranks, = **25,840** in one hand.
- **A5** Bought **Reroll Surplus** ($2 cheaper rerolls) and used a Mega Spectral
  Pack for **Grim** (destroy 1 card, add 2 Enhanced Aces) and **Ectoplasm**.
  The Empress then pushed Driver's License to **16/16 — X3 live**. Boss The
  House 22,000: full house QQQ+AA = **57,288**.
- **A6 Small** 20,000: full house 333+88 with **two Steel cards held** =
  **148,770**. Steel is the whole reason that number is 5x the A5 boss hand.
- **A6 Big** 30,000: JJJ+33 = 65,208.
- **A6 Boss** The Ox (playing your most-played hand sets money to $0) 40,000:
  spent down to $9 *in the shop before selecting the blind*, then played the
  full house anyway. KKK+99 with two Steel held = **117,384**, cost $9.

### Things learned this run that were not in the notes

1. **Steel cards are the strongest multiplier available on this seed**, because
   they are cheap ($3 Chariot) and they stack multiplicatively. Two Steel cards
   held is X2.25 — bigger than Driver's License. The trick is that Steel wants
   to be on a rank you never *play* (a 7, a 4), so it stays in hand.
2. **Discards that cannot break your made hand are free.** Once the full house
   is assembled, discarding the 2-3 dead cards costs nothing and rerolls for a
   Steel card into hand. This turned several 60k hands into 120k+ hands.
3. **Sell the spare joker BEFORE opening a Buffoon Pack.** With 5/5 slots the
   pack simply refuses the pick — I lost a Photograph (X2 Mult) that way, and
   `sell` is not legal in the pack state.
4. **Fibonacci is the right +Mult joker for this deck.** It fires 5 times on a
   333+88 or QQQ+AA full house — +40 Mult before any xMult applies.
5. **Ectoplasm, taken deliberately, was correct here** — but only because I was
   hard-locked at 5/5 jokers with a working engine and had just been refused a
   joker. The -1 hand size did bite immediately (the A5 Big Blind took all three
   hands), and I paid $4 for a Juggler the next shop to undo it. Net: a joker
   slot for $4 and some risk. Marginal, not free.
6. **Against The Ox, spend the money first.** Its penalty is only as large as
   your bankroll at the moment you play.

### Play-by-play, antes 7-8

- **A7 Small** 35,000: four of a kind beat the available full house because the
  full house would have required *playing* my Steel 6. Kept it held. 76k.
- **A7 Big** 52,500: drew four Aces, then free-rolled the dead cards three times
  and pulled two Steel into hand. Four Aces with X2.25 held = **179,118**.
- **A7 shop**: found the run's money engine — **The Fool $3 recreates the last
  tarot used, and the last tarot used was Temperance ($20)**. $3 in, $20 out.
  Ran that loop, plus a straight Hermit ($3 -> +$20), three separate times
  across antes 7-8. Money stopped being a constraint after this.
- **A7 Boss The Head** (all Hearts debuffed) 70,000: bought **The Star $3** in
  the shop *specifically for this boss*, held it, and on the boss hand converted
  my three debuffed Hearts to Diamonds before doing anything else. Then built
  333+88 and free-rolled twice: **189,360**.
- **A8 shop**: bought three Celestial packs and took **Earth every time** —
  Full House 6 -> 10. Also sold Drunkard to fit **Mr. Bones**.
- **A8 Small** 50,000: immediately punished for selling Drunkard — ran out of
  discards one card short of the full house and had to clear with two two-pairs
  (39,528 + 29,280).
- **A8 Big** 75,000: two pair AA+88, all four cards Fibonacci ranks and three of
  them Lucky/Bonus = **75,348**, cleared in a single hand.
- **A8 Boss Amber Acorn** (flips and shuffles all Jokers) 100,000: **this is the
  boss that ended the operator's own run.** It shuffled my row to
  `Fibonacci / Driver's License / Juggler / Mad / Mr. Bones / Duo` — both
  additive jokers stranded behind the X3. One `rearrange {"jokers":[3,0,5,1,2,4]}`
  put it back before I played a card. Cleared 100,000 across three hands
  (83,712 + 15,552 + 25,515). **Ante 8 beaten, won=true.**

### More things learned

7. **I did not really beat Amber Acorn — the harness did.** ***Caveat this
   result.*** The boss has two effects: it *shuffles* the joker row and it
   *flips the jokers face down*. `rearrange` legitimately answers the shuffle,
   but only if you know which joker is which — and the flip is what makes that
   hard for a human. `gamestate` reported all six jokers by name and position
   anyway, so the flip did nothing to me. Knowing the row was
   `Fibonacci / DL / Juggler / Mad / Bones / Duo` *is* the difficulty of the
   fight, and the API handed it over for free. The operator lost their own run
   to this boss playing with the information properly hidden. Treat the ante-8
   clear as assisted, and treat "read the row, then `rearrange`" as an artifact
   of this interface rather than as Balatro strategy.
8. **Buy the counter-tarot for a known boss one shop early.** The blind select
   screen names the boss before you have to commit money. The Star ($3) sitting
   in the consumable slot turned The Head from a threat into a normal round.
9. **Selling Drunkard for Mr. Bones was a mistake in the short run.** The whole
   engine is "make the hand, then free-roll the dead cards for Steel." Discards
   *are* the multiplier. I lost roughly half the A8 Small Blind's score to it.
10. **Two Pair being level 1 was the real bottleneck**, not mult. My two-pair
    hands ran ~80-140 chips against ~400-1100 mult. Uranus was offered three
    times and I passed on it every time in favour of Earth. On a Fibonacci
    build that plays two pair as its fallback at least once a round, that was
    the wrong call.

### Play-by-play, antes 9-10 (endless)

- **A9 Small/Big** 110,000 / 165,000. The Big Blind is where the free-roll
  pattern paid off best all run: 888 + AA assembled with three discards to
  spare, then I spent every remaining discard on the *dead* cards only. The
  draw handed back a third and fourth 8, so the final shape was AA + 888 with
  **AS(Steel) and 6D(Steel) both held**. **718,647 — best hand of the run.**
  Three Lucky cards in the played five, so part of that was variance.
- **A9 Boss The Goad** (all Spades debuffed) 220,000. Four pairs and no trips
  after all four discards — a genuinely bad spot. Banked two pair AA+55 for
  57,000, then drew into 888 + TT. Bought **Justice $3** one shop early and
  used it here to glass the one *unenhanced* card in the played hand (TH),
  which cost nothing and doubled the whole hand: **520,704**. Ante 9 cleared.
- **A10 Small** 560,000. Full house 333+88 with two Steel held = 337,260, and
  then I was out of discards with two hands left and nothing but singletons.
  Cycled junk, finished on a straight for 10,350, and finished the round at
  **359,517 — short**. Mr. Bones caught it (I was over the 25% line by 2.5x)
  and self-destructed.
- **A10 Big** 840,000. Full house AAA+88 = 216,144 with *no* Steel in hand,
  then a 42,282 pair, then nothing. **Ended the run at 259,742 / 840,000.**

### Lessons from the endless antes

11. **Endless targets outrun a fixed engine, fast.** Ante 9 boss was 220,000;
    ante 10 Small was 560,000 and ante 10 Big was 840,000 — a 2.5x and 3.8x
    jump against a build whose typical full house was ~400,000. From ante 9 on,
    the only question that matters in a shop is "does this multiply my full
    house," and I kept spending $4-6 on packs that answered "no."
12. **The discard budget is per-blind, not per-hand — and above ~500,000 a
    blind needs two full houses, not one.** I lost ante 10 Small by spending
    all four discards perfecting the *first* hand. The free-roll pattern is
    still right, but it is only free when the hand you already hold clears the
    blind. When it clears only half the blind, discards spent on polish are
    discards stolen from the second full house. Budget 2 and 2.
13. **Money starvation is what actually killed this run.** I went into ante 10
    on $15 and left the last shop on $8. The Fool -> Temperance loop that made
    money irrelevant at antes 7-8 never re-appeared, and I never replaced it,
    so I could not afford the Celestial packs that were the only thing keeping
    Full House scaling with the targets. Full House went 10 -> 12 across two
    whole antes; the targets went up 8x in the same span.
14. **Glass beats Lucky, and glass the *unenhanced* card.** Justice on a plain
    card is a strict X2 on the whole hand for $3 and costs nothing, because
    Bonus/Steel/Lucky enhancements are overwritten if you target them. This is
    the cheapest multiplier in the game and I only found it at ante 9.
15. **Repeated lesson #3, unlearned.** I again opened a Buffoon Pack at 6/6
    jokers, again could not take the card (Wily Joker, +100 chips on any Three
    of a Kind — exactly what a full-house build wants), and again learned that
    `sell` is illegal in the pack state. Two runs, same $4 mistake.
16. **Mr. Bones is worth more than a slot in endless.** I had written him off
    in lesson #9 as a bad trade for Drunkard. He converted a failed ante 10
    Small into a survived one. In endless, where one bad draw ends the run
    outright, the save is worth more than the marginal joker.

## POST-MORTEM — RUN 4

- **Final ante: 10.** (Ante 8 cleared, so `won=true`; the run continued into
  endless and died on the ante 10 Big Blind.)
- **Best single hand: 718,647** — full house AA+888, Fibonacci firing on all
  five played cards, two Steel cards held for X2.25, at the ante 9 Big Blind.
- **What ended the run:** the ante 10 Big Blind, target **840,000**. I scored
  **259,742**. Mr. Bones had already been spent one blind earlier on the ante 10
  Small Blind, so there was no save. Proximate cause: two of my three hands
  found no full house. Root cause: at $8-15 for the whole of ante 10 I could not
  buy the Celestial packs that were the only thing scaling Full House, so my
  hand ceiling sat at ~400,000 while the blind asked for 840,000.

### Concrete rules for the next attempt on BENCHMRK

1. **Treat ante 9 as the start of a different game.** Everything that works to
   ante 8 — one good full house per blind — stops working. From the ante 8
   shop onward, buy *only* Full House levels and multipliers, and hold enough
   money to buy them every single shop.
2. **Protect a money engine into the late game.** The Fool -> Temperance loop
   was the strongest thing I found all run and I let it lapse. Keep a Fool, or
   keep re-buying Hermit, so that shops at ante 9+ are affordable.
3. **Budget discards 2/2 across the first two hands of any blind over 500,000.**
   Free-roll for Steel only once the hand in front of you clears the blind.
4. **Buy every Justice you see and glass unenhanced cards** on the ranks the
   build actually plays (A/2/3/5/8 for Fibonacci). Five glassed cards in one
   full house is X32; I got exactly one.
5. **Sell down to 5 jokers before buying a Buffoon Pack.** Third time asking.
6. **Keep Mr. Bones in endless.** See lesson #16.
7. **The ante-8 Amber Acorn clear is still assisted** — see lesson #7. Nothing
   about this run's ante 9-10 play depended on that leak, but the ante 8 result
   should keep its asterisk.


# ============================================================
# RUN 5 — INFORMED RUN (full seed intelligence permitted)
# ============================================================

## Seed intelligence pipeline
Cloned the Blueprint analyzer (the engine behind the seed site) and ran it headlessly
under Node 24 to produce `seedtool/seed.json` for BENCHMRK / Red Deck / White Stake,
antes 1-12, shop depth 40, misc-source depth 60. Helper scripts: digest.mjs (per-ante
readout), find.mjs (locate a joker across every queue), meta.mjs (voucher/tag/boss queues).

## What the seed actually contains

VOUCHERS   A1 Tarot Merchant | A2 Hieroglyph | A3 Blank | A4 Telescope
           A5 Reroll Surplus | A6 Magic Trick | A7 Telescope | A8 Hone
BOSSES     A1 Pillar | A2 Hook | A3 Tooth | A4 Wheel | A5 Club | A6 House
           A7 Ox (!) | A8 Cerulean Bell
TAGS       A1 Coupon/Polychrome | A2 D6/Voucher | A3 Speed/Meteor | A4 D6/Orbital
           A5 Buffoon/Holographic | A6 Standard/Speed | A7 Boss/Investment
           A8 Buffoon/Garbage

KEY SHOP SLOTS (0-based position in that ante's shop queue; 2 drawn per shop open,
2 more per reroll, buying does NOT advance the queue)
  A1 s4  Hanging Chad      A1 s9  Baron        A1 s11 Smiley Face[Polychrome]
  A2 s2  The Duo           A3 s3  Drivers License[Foil]
  A4 s1  Fibonacci         A4 s29 Photograph   A5 s12 Golden Joker
  A6 s10 Baseball Card     A7 s11 Justice      A7 s39 BLUEPRINT
  A8 s0  Mr. Bones         A8 s24 The Trio     A10 s23 Photograph

## The build

Hand: FULL HOUSE. It is the only hand that satisfies The Duo (x2, pair) AND
The Trio (x3, three of a kind) simultaneously, and Earth planets are everywhere
in this seed's late Celestial packs.

Multiplier stack, in the order it gets assembled:
  1. HAND LEVEL is the quadratic term (chips AND mult). Every Celestial pack,
     every spare dollar on planets. Telescope at A4 guarantees the Full House
     planet as the first card of every Celestial pack afterwards.
  2. GLASS on the five PLAYED cards (x2 each -> x32). Justice tarots supply it.
     Glass the unenhanced card - enhancements overwrite.
  3. HANGING CHAD retriggers the FIRST played card 2 extra times. On a Glass
     card that turns x2 into x8. Blueprint copying Hanging Chad makes it x32
     on the first card alone. This is the single largest lever in the seed.
  4. STEEL on cards HELD in hand (x1.5 each, free - costs no joker slot).
  5. Joker xMults: The Duo, The Trio, Drivers License[Foil].

Target final jokers (5 slots):
  The Duo | The Trio | Drivers License[Foil] | Hanging Chad | Blueprint (left of Chad)

## Opening line (decided before starting)

A1 small blind: PLAY it (money).
A1 shop #1 (slots 0,1 = Runner / Mad Joker): buy Mad Joker if affordable - it is
  +10 mult on any pair, so it works in a Full House, and it is sellable later.
  Buy it NOW, before the Polychrome tag exists.
A1 BIG BLIND: SKIP -> take POLYCHROME TAG. Costs ~$7 and one shop visit; buys a
  permanent x1.5 on a core joker. Worth far more than $7.
A1 shop #3 (slots 2,3): reroll once to reach slots 4,5 -> buy HANGING CHAD, which
  consumes the Polychrome tag. Hanging Chad[Polychrome] is the goal.
  If money does not allow, hold the tag and spend it on The Duo at A2 instead.
A2 shop #2 (slots 2,3): buy THE DUO.
A3 shop #2 (slots 2,3): buy DRIVERS LICENSE[Foil].
A4 shop #1 (slots 0,1): buy FIBONACCI as a placeholder / survival joker.
A4: buy TELESCOPE voucher. A5: buy REROLL SURPLUS voucher (-$2 per reroll) -
  this is what pays for the deep digs later.
A7: dig the shop queue to slot 39 for BLUEPRINT (~17 rerolls across 3 shops,
  ~$90 with Reroll Surplus). WARNING: A7 boss is THE OX - playing your most
  played hand sets money to $0. Do the digging in shops #1 and #2, or beat
  the Ox with a non-Full-House hand.
A8: dig to slot 24 for THE TRIO (~10 rerolls). Mr. Bones is slot 0 - free
  insurance for the endless antes if a slot can be spared.

## Standing rules carried over from runs 1-4
  - Money floor $25 (max interest). Surplus goes into rerolls, not junk.
  - Budget discards 2 and 2 across a blind, never 4 on the first hand.
  - SELL DOWN TO 5 JOKERS BEFORE BUYING A BUFFOON PACK. Three runs lost a
    joker to this. Fourth time will not happen.
  - Never take Ectoplasm (-1 hand size). Never take skip-dependent jokers.
  - Keep suits MIXED in the full house - five same-suit cards register as
    Flush House, a level-1 secret hand, and score far less.


## REVISION — the bar is 5.17e19, not 450M

The additive/Full-House-levels plan above tops out around 1e9. Nine orders of
magnitude short. The only thing in Balatro that grows fast enough is
MULTIPLICATIVE RETRIGGERS ON GLASS CARDS: every extra trigger of a Glass card
is another x2 on the whole hand, so score goes as 2^(glass cards x triggers).
Hand levels are the linear term; retrigger count is the exponent. Spend the
run buying exponent.

Retrigger sources actually reachable in this seed:
  Hanging Chad  A1 s4, A4 s15, A11 s5/s37   first played card, +2 triggers
  Dusk          A2 s10, A5 s34, A12 s3      ALL played cards, +1, on final hand
  Hack          A1 s25, A4 s14              each played 2/3/4/5, +1
  Blueprint     A7 s39                      copies the joker to its RIGHT
  Seltzer       A1 s32                      all cards, +1, 10 hands then dies
  Mime / Sock and Buskin — buffoon-pack only at depth 17-49. Unreachable.

TARGET LAYOUT (Blueprint must sit immediately LEFT of Dusk):
  [Hanging Chad] [The Duo] [Hack] [Blueprint] [Dusk]

Played hand: FULL HOUSE of ranks 2-5, mixed suits, every card GLASS.
  triggers per card = 1 base + 1 Hack + 1 Dusk + 1 Blueprint-copies-Dusk = 4
  first card additionally +2 from Hanging Chad = 6
  total glass triggers = 4x4 + 6 = 22  ->  x2^22 = 4.19e6
  x The Duo 2  x Steel held (3 cards) 3.375  =  x2.83e7
Compare the no-Hack version (Duo+Trio, any full house): x2.65e6. Hack is worth
10x and it is why the played ranks are 2-5 rather than face cards.

## The Hex opening (replaces the Polychrome Tag line)

The A1 Jumbo Spectral Pack contains HEX: "adds Polychrome to a random Joker and
DESTROYS ALL OTHER JOKERS". With exactly one Joker owned, the downside is nil
and it is a free permanent x1.5. So:

  A1 small blind: PLAY. Shop #1 = slots 0,1 + packs 0,1. Buy little.
  A1 big blind:   PLAY (do NOT skip - the Hex line makes the Polychrome Tag
                  redundant, and the money and the extra shop both matter).
  A1 shop #2:     shows slots 2,3 and packs 2,3 (Standard, JUMBO SPECTRAL).
                  Reroll once -> slots 4,5 -> buy HANGING CHAD.
                  Then buy the Jumbo Spectral Pack and take HEX.
                  Result: Hanging Chad[Polychrome], one joker, x1.5 forever.
                  Budget: $5 reroll + $4 Chad + $6 pack = $15.
  A1 boss:        The Pillar. Play.
  A1 shop #3:     slots 6,7 = Madness / Strength.

Vouchers, revised: SKIP Hieroglyph at A2. It sets the ante counter BACK by one
and costs a hand every round; with highest-ante as the primary metric that is
a straight loss. Buy Telescope (A4) and Reroll Surplus (A5) - Reroll Surplus is
what pays for the ~17-reroll dig to Blueprint at A7 s39.


## SEED RE-AUDIT (mid-run, ante 3) — what the analyzer can and cannot predict

Re-ran the Blueprint analyzer at ANTES=16 / DEPTH=60 / MISC=80 and validated it
against the live game.

**Version resolved.** Compared gameVersion 10014 / 10103 / 10106 side by side.
Only 10106 reproduces the live shop (A2 = The Devil, Egg, The Duo, Jolly Joker;
A3 = Rough Gem, Throwback, Scholar, Drivers License, Burglar, 8 Ball). 10106 is
correct and the other two are wrong. Notably 10014 would have put a Brainstorm
at A3 s3 — it does not exist in the real run.

**RELIABLE (12/12 live matches so far):** the per-ante shop item queue, the ante
voucher, the ante boss, the two ante tags.

**NOT RELIABLE — verified twice:** the pack type queue AND pack contents. Ante 1
was predicted `[Buffoon, Celestial, Standard, Jumbo Spectral]`, live gave
`[Buffoon, Jumbo Celestial, Jumbo Celestial, Arcana]`. Then at the ante-3 boss
shop I bought the Jumbo Celestial to test the content stream directly: predicted
`Neptune, Pluto, Uranus, Venus, Jupiter`, live gave `Jupiter, Uranus, Saturn,
Neptune, Venus`. Different multiset, so it is not a cursor offset — the stream
genuinely diverges. **All pack planning is dead. Packs must be played live.**

**Consequence:** the Justice-tarot / Chariot-tarot indices and the "Earth at
celestialPack[8]" style planning from the earlier section is void. Glass and
Steel conversion has to be opportunistic.

### Full map, antes 1-16 (reliable fields only)

| Ante | Voucher | Boss | Tags (small / big) |
|---|---|---|---|
| 1 | Tarot Merchant | The Pillar | Coupon / Polychrome |
| 2 | Hieroglyph | The Hook | D6 / Voucher |
| 3 | Blank | The Tooth | Speed / Meteor |
| 4 | **Telescope** | The Wheel | D6 / Orbital |
| 5 | **Reroll Surplus** | The Club | Buffoon / Holographic |
| 6 | Magic Trick | The House | Standard / Speed |
| 7 | Telescope | **The Ox** | Boss / Investment |
| 8 | Hone | Cerulean Bell | Buffoon / Garbage |
| 9 | Blank | The Fish | Coupon / Coupon |
| 10 | Hieroglyph | The Mark | Uncommon / Top-up |
| 11 | Overstock | The Wall | **NEGATIVE** / Uncommon |
| 12 | Blank | The Mouth | Top-up / Foil |
| 13 | Overstock | The Manacle | Double / Charm |
| 14 | Overstock | The Goad | Ethereal / Foil |
| 15 | Hieroglyph | The Flint | Juggle / Standard |
| 16 | Telescope | Amber Acorn | Double / Investment |

### The two joker slots that decide this run

Five slots is the hard ceiling on the engine. There are exactly two ways past it
in this seed:

1. **Antimatter** (+1 slot). Gated behind Blank. **Bought Blank at A3 for $10.**
   Antimatter is now eligible to roll as a shop voucher; A9 and A12 both predict
   "Blank", which is the slot that should now re-roll into Antimatter. Not
   guaranteed — the pool shifts once Blank is owned — but this was the only and
   cheapest enabling move, and it had to happen before A9.
2. **Negative Tag, ante 11 small blind** (guaranteed). Skip the A11 small blind,
   then buy a base-edition joker; it becomes Negative and grants a slot. This is
   a single targeted skip, not a skip-based build, so it does not conflict with
   the "skip jokers are bad" rule.

Ceiling is therefore 7 jokers by ante 11-12.

### Key shop slots worth digging for

- A4 s1 Fibonacci · **s14 Hack** · s15 Hanging Chad · s29 Photograph · s43 The Trio
- A5 s12 Golden Joker · **s34 Dusk** · s37 DNA
- A6 s10 Baseball Card · s57 Hack
- A7 s11 Justice · s16 Certificate · s37 Campfire · **s39 BLUEPRINT**
- A8 s0 Mr. Bones · s24 The Trio · s40 Baron
- A9 s4 Hologram · s5 Constellation
- A10 s13 Baron · s21 Campfire · s23 Photograph · **s48 BLUEPRINT (2nd copy)**
- A11 s17 Constellation · s23 The Idol
- A12 s3 Dusk · s9/s17 Photograph
- A13 s12 Dusk · s15/s54 The Order · s49 The Family
- A14 s16 Bloodstone · s34 Certificate
- A15 s21 Constellation · s24 The Tribe · s37 Hologram
- A16 **s9 Sock and Buskin** · **s23 Mime** · s27 The Idol

### Things this seed does NOT have

Swept every spectral/arcana stream across 16 antes, 80 deep: **no The Soul
anywhere**, so no Legendary joker. Exactly one Black Hole (ante 1, long gone).
No Brainstorm at any depth. Blueprint is the only copier and it appears twice.

### Revised engine target

Score bar is 5.17e19, so the engine has to be multiplicative, not additive.
Glass cards are the only source that compounds with retriggers.

Target 7-slot layout: `[Hanging Chad][Blueprint][Dusk][Hack][The Duo][The Trio][grower]`
with Blueprint immediately left of Dusk so it copies it. Play a Full House of
ranks 2-5 (so Hack retriggers every card), mixed suits (Flush House trap), all
five cards Glass and ideally Red Sealed.

Triggers per card: base 1 + Hack 1 + Dusk 1 + Blueprint-as-Dusk 1 + Red Seal 1 = 5.
First card takes Hanging Chad's +2 = 7. Total 27 glass triggers = 2^27 ≈ 1.3e8,
then x2 (Duo) x3 (Trio) and whatever the grower slot reaches.

Dusk only fires on the final hand of the round, so the big hand must be played last.
Ante 7 boss is **The Ox: playing your most-played hand sets money to $0** — bank
before it and expect to be broke after.

## ANTES 5-6 (live play)

**Ante 5 cleared.** Sold Egg (+/usr/bin/bash shop to slot 12 and bought **Golden Joker** (+2 -> 0 - the destroyed cards were all low junk, so this also
thinned the deck and raised Ace density) then **Grim** (+2 Enhanced Aces, one of
them Steel). Passed on Ectoplasm because Antimatter (A9/A12) and the A11 Negative
Tag already give +2 joker slots without the -1 hand size.

**Ante 6 cleared small+big.** Best hand jumped 22,040 -> 33,712 -> **101,556**.

### The engine (discovered live, ante 6)
Hanging Chad retriggers the FIRST scoring card 2 extra times, and the retriggers
re-apply that card's **multiplicative** enhancement. So a Glass card (X2) played
first becomes X2^3 = X8, and a Polychrome (X1.5) first becomes X3.375.
The  endpoint works: .
**Always rearrange the best multiplicative card to hand index 0 before playing.**

101,556 came from Full House [TC(Glass,Holo)] AAA TD with the Glass Ten leading.

### Collected so far
Glass+Holo TC, Glass+Holo 7H, Polychrome QD, Steel 7H, Steel 7C, Steel Ace,
Mult+BlueSeal 8H (generates a free Earth every round it is held in hand).
Full House is level 5; holding 2 Earths **unused** for the ante-7 Observatory
voucher (Telescope already owned -> A7 shows Observatory), which gives X1.5 per
Planet held = X2.25.

### Corrections to earlier plan
- Baseball Card (A6 s10) skipped: only 1 Uncommon in my board, so just X1.5.
- Deep digs (Blueprint A7 s39) are unaffordable. Reroll cost resets each shop, so
  the efficient pattern is ~3 rerolls per shop, not one huge dig.
- **Never open a Buffoon Pack with full joker slots** -  is rejected during
  SMODS_BOOSTER_OPENED, so a Photograph was lost at ante 5. Free the slot first.
-  exits a booster without taking anything.

## ANTES 5-6 (live play)

**Ante 5 cleared.** Sold Egg (+$23), bought **Reroll Surplus** voucher, dug 6
rerolls on the D6-Tag $0 shop to slot 12 and bought **Golden Joker** (+$4/round)
plus **The Hermit**. Hermit later converted $22 -> $42.

**Mega Spectral Pack was the turning point.** Took **Immolate** (destroyed 5 junk
cards from hand, +$20 - the destroyed cards were all low junk, so this also
thinned the deck and raised Ace density) then **Grim** (+2 Enhanced Aces, one of
them Steel). Passed on Ectoplasm because Antimatter (A9/A12) and the A11 Negative
Tag already give +2 joker slots without the -1 hand size.

**Ante 6 cleared small+big.** Best hand jumped 22,040 -> 33,712 -> **101,556**.

### The engine (discovered live, ante 6)
Hanging Chad retriggers the FIRST scoring card 2 extra times, and the retriggers
re-apply that card's **multiplicative** enhancement. So a Glass card (X2) played
first becomes X2^3 = X8, and a Polychrome (X1.5) first becomes X3.375.
The `rearrange` endpoint works: rearrange {"hand":[...new order...]}.
**Always rearrange the best multiplicative card to hand index 0 before playing.**

101,556 came from Full House [TC(Glass,Holo)] AAA TD with the Glass Ten leading.

### Collected so far
Glass+Holo TC, Glass+Holo 7H, Polychrome QD, Steel 7H, Steel 7C, Steel Ace,
Mult+BlueSeal 8H (generates a free Earth every round it is held in hand).
Full House is level 5; holding 2 Earths **unused** for the ante-7 Observatory
voucher (Telescope already owned -> A7 shows Observatory), which gives X1.5 per
Planet held = X2.25.

### Corrections to earlier plan
- Baseball Card (A6 s10) skipped: only 1 Uncommon in my board, so just X1.5.
- Deep digs (Blueprint A7 s39) are unaffordable. Reroll cost resets each shop, so
  the efficient pattern is ~3 rerolls per shop, not one huge dig.
- **Never open a Buffoon Pack with full joker slots** - `sell` is rejected during
  SMODS_BOOSTER_OPENED, so a Photograph was lost at ante 5. Free the slot first.
- pack {"skip":true} exits a booster without taking anything.

(The duplicated/garbled copy of this section immediately above was caused by a
heredoc mangled through the Bash tool. Write the file with the Write tool and
append with PowerShell `Add-Content`, never a bash heredoc.)

## ANTE 7 (live play)

**Voucher predictions are UNRELIABLE.** A7 was predicted Telescope (-> Observatory
since Telescope was already owned); live it offered **Tarot Merchant**. The
analyzer assumes zero purchases, and owned vouchers are removed from the pool,
which shifts every later slot. Shop *item* queues stayed exact (live-confirmed
through A7 s15). Consequence: the "hold 2 Earths for Observatory" plan was
abandoned and both Earths were spent on Full House levels.

**Small blind 35,000** cleared. **Big blind 52,500:** discarded into AAA+TT for
44,000, then AAA+KK led by AH(LUCKY) for **88,880** (the Lucky Ace procced
multiple times off Hanging Chad's retriggers). Round 132,880.

Deliberately did NOT burn the Glass 7 on the big blind once 44,000 was already
banked and only 8,500 remained. Glass rolls its 1-in-4 destroy chance on *every*
retrigger, so a Chad-led Glass card is ~58% to die per use. Save it for the hand
that actually needs it.

### Ante 7 shop: leading with a Lucky card is free upside
With no Glass/Polychrome card in the played five, Hanging Chad's best target is
the highest-value card, and a **Lucky** card is strictly better than a plain one:
three triggers = three independent 1-in-5 rolls at +20 Mult each.

### The Ox counter-play
The Ox sets money to $0 when you play your **most-played hand** — Full House for
this build. Rather than spending down to $0 (run 4's answer), the better line is
to clear the boss with a hand that is *not* a Full House. Bought **Uranus $3** to
put Two Pair at **level 4 (80 chips / 5 mult)** specifically so a Glass-led Two
Pair clears 70,000 on its own (projects ~120,000) and keeps the bankroll intact
for the ante-8 dig.

### Shop packs show a HAND
`buy {"pack":N}` in the shop reports a live 8-card HAND in the state, which means
card-targeting tarots (Justice, The Chariot) can be aimed at real deck cards from
inside the shop. This was not known in runs 1-4 and it makes enhancement tarots
far more usable.

## ROUTE PLAN — antes 8-16

Score bar 5.17e19 needs retrigger count, not hand levels. Reachable exponent:

| Ante | Target | Why |
|---|---|---|
| 8 | s0 **Mr. Bones**, s24 **The Trio** (X3 on trips) | Trio fires on every full house |
| 9 | voucher slot predicts Blank -> hope for **Antimatter** (+1 slot) | 6th joker |
| 10 | s48 Blueprint (deep, ~$100) | copies the joker to its RIGHT |
| 11 | **skip the SMALL blind -> NEGATIVE tag**, then buy any base joker | 7th slot |
| 12 | s3 **Dusk** (+1 trigger on ALL played cards, final hand only) | doubles glass exponent |
| 13 | s12 Dusk (2nd), s15/s54 The Order, s49 The Family | |
| 16 | s9 Sock and Buskin, s23 Mime | |

Bosses: A8 Cerulean Bell (silently forces one extra card into EVERY selection —
diagnose by discards removing n+1 cards), A9 Fish, A10 Mark, A11 Wall,
A12 Mouth, A13 Manacle (-1 hand size), A14 Goad, A15 Flint, A16 Amber Acorn
(shuffles + flips jokers; answer with `rearrange {"jokers":[...]}`).

Standing priorities every shop from here: (1) Justice tarots to glass the cards I
actually play, (2) Full House levels, (3) retrigger jokers, (4) nothing else.

### Ante 8 reroll schedule (worked out in advance)

The queue cursor persists across the three shops of an ante and advances 2 per
shop open and 2 per reroll; reroll price resets to $3 (Reroll Surplus) each shop.
A8 queue: `0 Mr.Bones 1 Drunkard 2 OddTodd 3 TheChariot 4 AbstractJoker
5 Strength 6 GreedyJoker 7 TheHermit 8 Mars 9 GoldenJoker 10 BurntJoker
11 Chaos 12 Mars 13 Saturn 14 Pluto 15 Banner 16 Temperance 17 WeeJoker
18 WilyJoker 19 MarbleJoker 20 Cloud9 21 GreenJoker 22 LustyJoker
23 TheHierophant 24 THE TRIO 25 FlashCard`

- **Shop 1** opens on s0,s1. Reroll x3 ($3+$4+$5=$12) -> reaches s7.
  Buy **The Chariot** (s3, Steel card) and **The Hermit** (s7, doubles money).
  Cursor ends at 8.
- **Shop 2** opens on s8,s9. Reroll x4 ($3..$6=$18) -> reaches s17.
  Buy **Temperance** (s16) if money is short. Cursor ends at 18.
- **Shop 3** opens on s18,s19. Reroll x3 ($3+$4+$5=$12) -> reaches s25.
  Buy **THE TRIO** (s24, X3 Mult on any three-of-a-kind).

Total ~$42 of rerolls. This is the reason the Ox must not be allowed to zero the
bankroll. Sell **Jolly Joker** (+8 flat mult, weakest) to make room for The Trio.

Final joker order (additive left, xMult right, Chad right of Scholar so the
retriggers re-run Scholar):
`Scholar | Hanging Chad | The Duo | The Trio | Golden Joker`


## ANTE 8 (live play) — CLEARED, won=True

Small and Big cleared on Full House. Boss was **Cerulean Bell** (forces one card
in hand to always be selected).

Two things learned about Cerulean Bell that are not obvious:
- The forced card is detectable from the raw gamestate: the card carries
  `state=[@{highlight=True}]`. Nothing in the friendly output shows it.
- **The forced card is consumed by DISCARDS too.** Selecting 5 cards to discard
  actually removes 6. This silently ate a card I needed.

Counter-play used: play the forced junk card **alone as a 1-card hand**. That
re-rolls which card is forced and costs only one hand. Repeated until the force
landed on the Polychrome Queen — the exact card I wanted leading anyway — and
then the Full House went out normally. Ante 8 cleared, `won=True`.

### Ante 8/9 shop work
- **Buy discount vouchers FIRST.** Clearance Sale ($10, 25% off all cards and
  packs) re-priced the entire *current* shop the moment it was bought.
- Bought Temperance $3, used for +$12 — that fixed the economy for two antes.
- Sold Scholar to make room for **Constellation**, grown to X1.5 by ante 9.
- Full House driven from level 13 to **level 19 (490 chips / 40 mult)** via
  Celestial packs, two free Earths off the Blue Seal H_8, and The Fool.
- Thinned 2 dead cards (4D, 3S) out of the deck with The Hanged Man.
- The Trio (A8 s24) turned out to be **unreachable**: the shop that appears after
  the ante-8 boss belongs to ante 9's queue, so slots past ~s16 in an ante's list
  can never be rolled. Worth remembering for future route planning.

## ANTE 9 — small and big cleared, LOST to the boss (The Fish)

Small 110,000 cleared. Big 165,000 cleared in two hands (121,752 + 81,406).
**Best single hand of the run: 799,398.**

Boss **The Fish** (220,000), effect "cards drawn face down after each hand
played". The API still reveals the face-down cards in `gamestate`, so the effect
was informational rather than blinding — the real problem was elsewhere.

Final position: three 10s, the Polychrome Queen, three Steel cards, **no pair
partner**, and **zero discards left**. Full House was unbuildable. Burned three
hands cycling single junk cards looking for a pair; drew 4C, 6C, then A/K/4. The
last hand could only be Three of a Kind (level 2, 50/5) for ~4,650. Round
finished at 4,937 / 220,000.

`RESULT ante=9 best_hand=799398 won=true`

## POST-MORTEM

**What worked**
- The Hanging Chad engine. Retriggering the first scoring card 2 extra times,
  combined with putting a Polychrome or Glass card at hand index 0 via
  `rearrange`, was the whole run. Play order follows **hand index order, not
  selection order** — this is the single most important mechanical fact.
- Full House as the one leveled hand. Level 19 (490/40) carried antes 7-9.
- Blue Seal on the H_8 Mult card generating a free Earth at end of round, twice.
  Needs a free consumable slot to fire — leaving one open was worth it.
- Buying discount vouchers before anything else in a shop.
- Beating the Cerulean Bell boss by re-rolling the forced card with 1-card plays.

**What lost the run**
1. **Discard discipline.** I spent all four discards on the ante-9 boss early,
   before I had a read on whether the hand could actually become a Full House.
   With one discard held back the pair almost certainly arrives. Cycling with
   *hands* costs ~1/3 of the round's scoring capacity per look; cycling with
   *discards* costs nothing. Never trade a hand for a look while discards remain,
   and never spend the last discard unless the hand is already live.
2. **Single-hand dependency.** The build could only score through Full House.
   Three of a Kind sat at level 2 and Two Pair at level 4, so there was no
   fallback when the fifth card didn't arrive. A few spare planets into the
   second-best hand would have been cheap insurance — 220,000 was reachable off a
   Chad-led Two Pair if it had been leveled anywhere near Full House.
3. **Deck composition.** The deck had 8 Aces and 5 Sevens but only 1 Ten left in
   the draw pile once three were in hand. I built trips on the rarest rank in the
   deck. Pair outs should be counted against the *actual* remaining pile
   (`cards.cards` in the raw gamestate is the draw pile, and its rank histogram is
   free information) before committing to which trips to hold.
4. **Route optimism.** The plan assumed a second Hanging Chad at A11 and Dusk at
   A12. Everything past ante 9 was theoretical, and the run died two antes short
   of the first real multiplier upgrade. The 5.17e19 bar needs the retrigger
   count to compound; at ante 9 I was still at a single Chad, i.e. the exponent
   had not started growing at all.

**Model calibration notes for next time**
- Chips model is exact: `handChips + scoring-card chips + lead retrigger chips`.
- Mult model was ~2x optimistic on Glass-led hands. Observed a Glass lead behaving
  like X4 rather than X8. The Lucky Ace at ante 7 did proc off multiple Chad
  retriggers, so the retriggers are real; the discrepancy is more likely a
  mis-ordered lead card than a rules difference. **Verify index 0 with
  `rearrange` before every big hand** rather than trusting the selection order.
- Steel is X1.5 per card **held**, and playing a Steel card throws that away.
  Three Steel held is X3.375 and was frequently larger than the lead-card bonus.

**Bar comparison:** user reached 5.17e19. This run peaked at 7.99e5 on a single
hand and ended at ante 9. Not close — the gap is entirely retrigger count, and
the run needed to survive to antes 11-13 to start building it.
