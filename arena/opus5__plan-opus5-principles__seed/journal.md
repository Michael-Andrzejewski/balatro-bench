# BENCHMRK run journal (player) - FINAL

Deck: RED, Stake: WHITE, Seed: BENCHMRK. Solo - no lives.

## FINAL RESULT
- **Ante 8 cleared, won=True.** Continued into endless at the operator's/user's call.
- **Ante 9 fully cleared** (110k / 165k / 220k).
- **Died at ANTE 10 Big Blind** (840,000). Scored 628,341 of it. Ante 10 Small was cleared.
- **Highest ante reached: 10. Best single hand: 615,624** (Full House JJJ+77 into the
  ante-9 boss, The Plant, with every face card debuffed).
- Hand progression of bests: 109,114 (A7) -> 230,112 (A8) -> 244,728 -> 301,320 -> 615,624.

## Archetype (never deviated)
Pure FULL HOUSE + stacked xMult. Zero deck modification. A Full House simultaneously
contains a Pair, a Two Pair and a Three of a Kind, so it turns on every conditional
joker at once. Final stack: Spare Trousers(+60) / The Duo X2 / The Trio X3 /
Seeing Double X2 / Invisible Joker. Full House L18 (465 chips / 38 mult).
Vouchers: Telescope, Reroll Surplus.

## HOW I DIED - read this first
A10 Big needed 840,000. My finisher was ~590,000, so the blind required **two**
Full Houses in one round. I made the first immediately, then had 3 discards and
3 hands to build a second and never got there. Three compounding causes:

1. **I sold Mr. Bones at A9 shop 3 to fund Seeing Double.** That trade doubled my
   output (X6 -> X12) and it is why I cleared the A9 boss and A10 Small so easily.
   But it spent the one free failed blind. With Bones I would have survived this
   exact round and reached the A10 boss. **A safety joker is worth more than a
   multiplier the moment your output stops one-shotting blinds.** My output cleared
   560,000 in one hand but not 840,000; that is precisely the regime where you need
   the insurance, and it is the regime I had just entered.
2. **I burned all 3 remaining discards before counting the deck.** I fired three
   5-card discards hunting a pair, then discovered at the end that *all four tens
   were already gone* (I had played TC/TD and held TS/TH), so the TT in my hand was
   a dead trips-base the whole time. My own journal already said DECK TRACKING WINS
   ROUNDS. I applied it one hand too late - once I did count, I played correctly
   (cycling the dead tens, keeping AA+KK for 4 live outs) and simply lost a 70%
   and then a 70% roll back to back.
3. **I never re-priced the blind against the build.** I planned the whole ante
   around one-hand clears. A10 Big at 840,000 was always a two-Full-House round and
   I should have treated it as the danger blind of the ante, not the boss.

## Mechanics confirmed this run
- **JOKER ORDER: only ADDITIVE-MULT jokers must sit LEFT of xMult jokers.** Chip
  jokers can sit anywhere; chips and mult are separate accumulators. New buys append
  to the RIGHT. Format: {"jokers":[<new order of current indices>]}
- Blueprint copies the joker to its RIGHT. Never buy the copier before the thing
  worth copying.
- Four of a Kind does NOT contain a Two Pair. Never play quads with this build.
- Full House scales +25 chips / +2 mult per level. L14 = 365/30, L18 = 465/38.
- **Spare Trousers and Supernova use their POST-increment value on the hand that
  triggers them.** Verified to the chip on four separate hands.
- **SHOP QUEUE FORMULA IS NOT CONSTANT ACROSS ANTES. Verify it every ante.**
  - Normal (A1-A8, A10): shown items = (2N-1, 2N) + 2*r_total, N = shop number,
    r_total = total rerolls this ante. Shop 1 at 0 rerolls shows #1,2.
  - **ANTE 9 WAS OFFSET BY ONE FULL REROLL.** A9 shop 1 at 0 rerolls showed
    non-queue items; #1,2 only appeared after the first reroll. Formula there was
    items = (2p-1, 2p) with p = (N-1) + r_total.
  - I caught this by reading names instead of assuming, at a cost of $4. Had I
    assumed, the A9 Seeing Double dig would have missed by a full reroll - the
    same error that cost me Blueprint at A7.
- **VERIFY EVERY REROLL STEP BY NAME against the analysis before the next reroll.**
  This is the single highest-value habit in the run. At A7 I mis-stepped by one and
  permanently lost Blueprint. After adopting the rule I hit The Trio (A8 #25),
  Earth (A9 #7), Seeing Double (A9 #15) and Baron's slot (A10 #13) exactly.
- Queue slots get SUBSTITUTED when they hold a joker you already own or a duplicate
  (A9 #14 Supernova -> Banner, A10 #4 Ceres -> Mercury). **The rest of the queue does
  NOT shift. Substitution is not drift** - keep counting from the original numbering.
- Booster packs do NOT change on reroll. Only the 2 card slots do.
- **Consumables from PACKS auto-apply instantly and use no slot. Consumables bought
  in the SHOP go to a slot and CAN be held.** I lost $85 at A7 by taking Temperance
  from a pack expecting to hold it through The Ox.
- Telescope: Celestial Packs always contain the planet for your MOST PLAYED hand.
  Full House must stay ahead of Two Pair in play count or it starts handing you
  Uranus and all scaling stops. Final count FH 31 / TP 18.
- Interest = min(floor(money/5), 5). Money above $25 earns nothing.
- **Money tarots are free value:** The Hermit netted +$17 for $3; Temperance +$10.
- **The seed analysis file's SHOP QUEUES stayed exact all the way to ante 10, but in
  endless mode the BOSSES, VOUCHERS and TAGS are all re-randomized.** A9 was listed
  as The Fish/Clearance Sale/Coupon+Coupon; it was actually The Plant/Blank/
  Holographic+Rare. A10 was listed as The Mark; it was actually The Fish. Trust the
  queue, never trust the boss list once won=True.
- **Debuffed cards still count toward hand type but score 0 chips, and they do NOT
  satisfy joker conditions that inspect scored cards.** Against The Plant I made
  sure my Seeing Double club was a live 7C and not a debuffed face card.

## Judgement calls, and how they actually turned out
- **Sell Mr. Bones for Seeing Double (A9 shop 3).** Doubled output for $6. Won the
  A9 boss and A10 Small trivially. Also killed me. I still think the trade was right
  on EV, but it should have been paired with a rule: *once the safety net is gone,
  every blind above one-hand range is a boss.*
  **This decision was never reviewed by the planner.** I had a consult in flight
  asking exactly this question and held off spending until it returned. It never
  did - it ran 28 minutes and then died on the planner's 32,000-token output cap,
  reporting failure only after the run was already over. So I made the run's most
  consequential call solo, on a deadline, believing a second opinion was coming.
  **Operational lesson: a consult that has not returned is not a consult that is
  pending - set a hard deadline, and ask the planner for a SHORT answer when the
  decision is time-critical.** My successful consults were the ones with tightly
  scoped questions; the one that died asked five open-ended questions at once.
- **Invisible Joker over Photograph/Baron (A10 shop 1).** The planner argued for
  Baron at #14 and against Invisible. I bought Invisible anyway, then found the
  planner had priced Baron with the *ante-9* offset formula, which does not apply at
  A10; the correct cost was 2 rerolls, not 5. So I kept Invisible and parked the
  queue on #13,14 so Baron would be sitting on the shop-3 counter as an adaptive
  fallback if the duplicate rolled weak. That was the right structure and it cost $7.
  It died with the run: Invisible hit 2/2 on the exact hand that ended the game.
- **Playing A9 Big instead of skipping for the Rare Tag.** Correct - the tag was a
  lottery, shop 3 held a guaranteed X2, and skipping would have forfeited both the
  shop and a round of Invisible/Trousers progress.
- **Rejecting Cavendish (#42) and Blueprint (#49) at A10.** Correct. Both were ~20
  rerolls / $110+ against a ~$70 bankroll.
- **Rejecting the Hieroglyph voucher.** It reads -1 Ante, which would have *reduced*
  the metric the benchmark scores, on top of -1 hand per round.

## What I would do differently
1. Keep Mr. Bones until the build one-shots the *Big* blind, not the Small.
2. Count the deck for dead ranks BEFORE spending the second discard, not after the
   last one.
3. Identify the two-hand blind in each ante during the shop, and reserve discards
   for it rather than spending them on the first Full House of the round.
4. Buy Earth even more aggressively. Every level was ~5-7% and I passed on a few
   $6 packs early to protect reroll money for digs I later abandoned anyway.

## Consent
**I consent** to this run's results and this journal being shared publicly -
leaderboard, GitHub, write-ups, in full and unedited.

Context I would like included:
- The run reached ante 10 in endless mode after winning the base game at ante 8.
  The headline numbers are: **highest ante 10, best single hand 615,624.**
- The death was not a scoring-model failure. My damage predictions matched the game
  exactly, to the chip, on every hand I checked all run (53,480 / 22,672 / 18,176 /
  586,368 among others). The run ended on a resource-management decision - selling
  Mr. Bones - and then a genuinely unlucky pair of ~70% draws.
- I played the whole run through the documented HTTP API only. I did not attempt
  `set`, `add` or `load`, and I did not read any files outside my own journal, the
  seed intelligence file, and my own planner dialogue.
- The strategic partnership was real and load-bearing: the planner's ante-6 call to
  buy Supernova over an extra Earth level, and its ante-8 call to take The Trio at
  #25 instead of Blueprint at A7 #40, are the two decisions that got the run past
  ante 7. Where I overrode it (Invisible Joker at A10) I did so because I had live
  data it did not - a shop-offset formula that differed between antes 9 and 10.

Correction I want noted: an earlier version of this journal listed the ante-9 boss
as The Fish and ante 10 as The Mark, copied from the seed analysis. Those are wrong
for an endless-mode run. The live bosses were The Plant (A9) and The Fish (A10).
