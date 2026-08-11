# Balatro Bench Run — fable5 (seed BENCHMRK, Red deck, White stake)

## Plan
Skipped Small Blind ante 1 for Coupon Tag -> free shop. Got 3 free jokers (Runner, Mad Joker, Jolly Joker) + free Jumbo Celestial (took Uranus, Two Pair lvl 2).
Build: two-pair engine early (Mad +10 mult, Jolly +8 mult), Runner scales chips on straights if build pivots. Keep economy up, upgrade Two Pair / pivot to whatever jokers appear.

## Ante 1
- Skipped Small (Coupon Tag). Big 450: FH JJJ66 = 328 (best so far), TT99 two pair 116, 33 pair 32.
- Boss: The Pillar (cards played this ante debuffed). Debuffed: JS JH JC 6S 6D TS TH 9H 9C 3H 3C.
- Boss one-shot with FH AAJJJ = 1584.
- Best hand ante 1: 1584

## Ante 2
- Shop: bought Egg, Celestial (Earth->FH lvl2), Arcana (Fool->Earth copy->FH lvl3).
- Shop 2: bought The Duo (X2 pair!), sold Runner, bought Swashbuckler.
- Small 800: QQ88 two pair 1596. Big 1200: KK99 two pair 4212. Hook boss 1600: FH 999QQ = 9179 one-shot.
- Best hand ante 2: 9179

## Ante 3
- Spectral: took Ectoplasm (Egg went Negative, +1 slot). Jumbo Celestial: Uranus (2pair lvl3). Buffoon: Cloud 9.
- Rearranged jokers: Swashbuckler BEFORE Duo (additive before X2 — was losing ~50% mult).
- Small 2000: QQQ 2520. Skipped Big (Meteor Tag -> Mega Celestial: Earth lvl4 + Venus). Tooth boss 4000: AAQQ two pair 9792 one-shot (-$4).
- Best hand ante 3: 9792

## Ante 4
- Bought Telescope voucher, Earth (FH lvl5), Tower (7C -> Stone +50), Mercury (pair lvl2).
- Small 5000: FH JJJ55 = 21240. Big 7500: JJ33+stone = 14688. Wheel boss 10000: KKQQ 11400.
- Best hand ante 4: 21240

## Ante 5
- Skipped Small for Buffoon Tag — MISTAKE: Mega Buffoon opened with 6/6 joker slots, couldn't take Photograph (X2 face). Lesson: free a slot BEFORE skipping for joker-pack tags.
- Uranus x2 (2pair lvl5 via Fool), bought Death, 2nd Tower. Sold Cloud 9, bought Hiker (+5 chips/card scaling).
- Big 16500: QQJJ 17360. Club boss 22000: KKQQ+stone 23040 (KC debuffed).
- Best hand ante 5: 23040

## Ante 6
- Sold Mad, bought Throwback (X2.0 after 4 skips). Chariot->steel 2H, Standard tag->steel 7H + JD. Earth (FH lvl6).
- Skipped Small (Standard Tag). Big 30000: 9933 w/ steels held 32488. House boss 40000: QQ+stones 35700 + 77 pair 9048 = 44748.
- Best hand ante 6: 35700

## Ante 7
- Mega+Jumbo Celestials: Uranus lvl7, Venus lvl3, Earth lvl7. Temperance +$50. Bought Justice (held), Uranus (2pair lvl8).
- Small 35000: 8833 two pair 38220 (NEW RUN BEST). Big 52500: AA+stone 26112 + 66 9472 + 33+stone 24576.
- Ox boss 70000 (2pair = money to $0): dug FH with 3 discards, JJJ22 = 71680 one-shot. Money safe.
- Best hand ante 7: 71680

## Ante 8
- Sold Jolly -> Mr. Bones (death insurance for high antes). 2x Celestial packs: Uranus (2pair lvl9), Earth (FH lvl8).
- Skipped Small (Buffoon Tag, wasted, slots full) + Big (Garbage Tag +$45). Throwback X2.5.
- Cerulean Bell boss 100000: forced card wrecked selections (auto-joins plays/discards — select only 4!).
- Justice -> glass KS. Scored 60585/100000 — Mr. Bones consumed, survived. WON=TRUE at ante 8.
- Best hand ante 8: 16125 (boss fumble round; low)

## Ante 9 (endless)
- Bought Polychrome Golden Joker X1.5 ($11!). Arcana pack: all 3 tarots needed hand targets, un-takeable in shop, skipped ($4 lost).
- Standard pack: steel+foil TC (3rd steel).
- Small 110000: KKJJ9 glass-K + steel held = 172800 ONE SHOT (new best).
- Shop: Mercury (pair lvl3), Earth x2 (FH lvl10), Uranus (2pair lvl10), sold Hiker -> Constellation (X0.1/planet).
- Also grabbed glass+polychrome 3S (X3 card!) and wild TC from Mega Standard.
- Big 165000: TT+AJ+stone 99750, QQ77J 143400.
- The Eye boss 220000 (no repeat hands): QQJJ+stone, steel TC held = 294007 ONE SHOT (new best).
- Best hand ante 9: 294007

## Ante 10 (endless wall)
- Shop: Mercury (pair lvl4), Emperor -> Tower (3rd stone: 3C) + World. Uranus (2pair lvl11), steel 3H (4th steel), extra QC.
- Small 560000: KK+A+2stones 170966, QQTT+glass-poly-3S 254475, JJTT+Q 220545. Cleared 645986.
- Big 840000: KK(glass)JJ+T = 308227 (RUN BEST), TT88+K 249385, QQ33+J steel held 265828, TT filler 113531. Cleared 936971.
- The Flint boss 1120000 (base chips/mult halved): TTT+2stones 256987, QQ 77647, 66 66906, 3322+A w/glass-3S 268957. Total 670497/1120000. GAME OVER.

## Post-mortem
- FINAL: ante 10 reached, won=true (beat ante 8 via Mr. Bones save), best single hand 308227 (glass-K KKJJ+T, Big ante 10).
- Engine: pairs/two-pair with Duo X2 + Throwback X2.5 + Golden poly X1.5 + Constellation X1.4 + Swashbuckler +85; steels held, stones stuffed in plays, glass X-mult cards.
- Death cause: The Flint halves base chips/mult; per-hand output ~70-270k vs needed 280k/hand. No Mr. Bones (already consumed at ante 8 Cerulean Bell).
- Lessons for seed BENCHMRK:
  1. Free a joker slot BEFORE joker-pack tags (lost Photograph a5, wasted Buffoon tag a8).
  2. Cerulean Bell: forced card auto-joins every selection — select only 4 cards.
  3. Arcana packs in shop: target-tarots hang the API and are un-takeable; only buy Arcana when a hand is available.
  4. Additive jokers BEFORE X-mult (Swashbuckler before Duo) — order check saved ~50% mult.
  5. X-mult stacking >> additive late; Golden poly + Constellation purchases at a9 doubled output.
  6. The Ox (a7): most-played hand = Two Pair; dodge with FH one-shot.
  7. Endless a10 jump is brutal (5x a9 targets); bank X-mults earlier (Invisible Joker timing, Baron + king-hold build considered too late).

## RUN 2 (full seed access) - live log
- a1: double-skip mishap (skip hit small+big); beat Pillar 669/600 with no jokers via precomputed draws. Tags carried to a2 shop = free Poly Egg + Blue Joker + Devil + Earth.
- a2: leave-shop method is next_round. Bought The Duo , Uranus (2P lv2), Earth (FH lv3). One-shot all 3 blinds (942/1494/5400 vs Hook).
- a3: Spectral pack Ectoplasm -> NEGATIVE THE DUO (+1 slot, -1 hand size, hand=7). Uranus (2P lv3), Cloud 9, Mega Std: Glass 9S + RedSeal Bonus QD. Jumbo Arcana Temperance = +0 (Egg sell value!). FH 999-44 one-shot Tooth 6900/4000.
- NOTE: adding cards to deck scrambles precomputed draw orders. a3 big onward = play live. Analyzer shop/pack/tag data still accurate.
- a4: bought TELESCOPE 0 (celestials now always carry Uranus). Mega Std: Glass 9S already had... this pack: took Glass9S+BlueSeal Mult AS (AS held at round end = free planet of last hand). Earth (FH lv5=140x12). 6.


# RUN 2 (full seed access, Blueprint analyzer)

## Setup
Analyzer intel: full shop queues, packs, tags, vouchers for a1-a16. Plan: Baron ladder endgame (Baron a8, Blueprint a7, Invisible a10) on top of Two Pair/FH engine. Key finding mid-run: adding/removing deck cards scrambles predicted deck draw orders, so blinds were played live; shop/pack/tag predictions stayed accurate.

## Ante 1-4
- a1: skipped Small (Coupon), free-shop dig; double-skip mishap cost the Big blind income. Found next_round + use/sell RPC methods.
- a2: The Duo [NEGATIVE from Ectoplasm plan gone right] +1 slot, Temperance +0, Hook one-shot 5400.
- a3: 2184/3072/6900 (Tooth). Draw-order predictions broke after deck edits -> live play from here.
- a4: TELESCOPE voucher (Uranus in every celestial), Photograph, Glass 9S, RedSeal Bonus QD, BlueSeal Mult AS, steel KD. Wheel 10848.
- Best hands: climbing 5400 -> 12168.

## Ante 5
- Small 14260 (FH + steel KD held; BlueSeal AD -> free Uranus).
- Big 16500: cut to last hand (0 discards), clutch FH AAA-99 = 20904 exactly as computed.
- Shop: Earth from Jumbo Celestial (FH lvl6). Boss The Club 22000: one-shot FH QQQ44 = 23184 (QC/4C debuffed but counted for hand type).

## Ante 6
- BlueSeal AD generated Earth -> FH lvl7 (190x16). Bought steel 7H, sold Hiker -> Throwback X1.5 (2 skips). Steel 7C + GoldSeal QC + HoloGlass TC from packs (4 steels total).
- Small 20000: one-shot FH AAA-QQ 27776. Big 30000: one-shot FH QQQ-KK 42432 (RUN BEST).
- Boss The House 40000: QQ99 12744, AA-TT w/ holo-glass TC 20880, junk dump 127, last hand only AA77 available (no face/glass scoring, ~3.9k deterministic) -> forced 20% lucky-AH gamble, missed. 37621/40000. GAME OVER.

## Post-mortem (run 2)
- FINAL: ante 6, best hand 42432, won=false. Worse than run 1 (ante 10) despite full seed access.
- Death cause: The House RNG - after two strong hands the last two draws were pairless junk (77 then AA77 with no face/glass/steel). Deterministic max ~41.5k needed everything to line up; fell 2379 short.
- What went wrong strategically:
  1. Sold Hiker for Throwback mid-a6: correct long-term EV but lost ~30-60 chips/hand of accumulated card value on the death round itself.
  2. Used the a6 boss discards too early (all spent by hand 2); The House punishes running dry because you cannot dig out of junk draws.
  3. Never used The Devil (dead consumable slot all run) - should have gold-carded a King early for drip income or just sold decisions faster.
  4. Deck dilution: added TC/QC/7C/7H mid-a6; fatter deck = worse pair density on the exact round it mattered.
- What worked: analyzer shop/pack predictions (Steel 7H/7C, Poly QD, Uranus-via-Telescope all landed as predicted); FH lvl7 one-shots; exact score precomputation (20904 predicted = 20904 scored).
- Lesson for next attempt: on must-not-lose boss rounds, bank a discard for the final hand and keep at least one face-pair or glass card in reserve before dumping; do not restructure jokers (Hiker sale) right before a boss.
