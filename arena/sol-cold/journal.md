# Balatro benchmark journal — BENCHMRK

## Build plan

Prioritize scalable multiplicative scoring and reliable hand consistency. Early plan: exploit the Ante 1 Coupon and Polychrome tags, then build around whatever free joker/shop offers appear. Preserve economy for interest and rerolls while taking high-value scaling.

## Key decisions and progress

- Ante 1: Skipped Small for Coupon Tag and Big for Polychrome Tag. Beat The Pillar at 672/600 after using the extra Red Deck discard to find an opening full house; no previously played cards existed when the boss began.
- Hieroglyph rewind: Spent the full $10 on Hieroglyph, returning to Ante 1 with three hands per round in exchange for three extra shops/round rewards. Free Coupon/Polychrome value produced a Polychrome Egg; free packs added Blue Joker and a Full House level.
- Replayed Ante 1: Added Mad Joker and Jolly Joker, making Pair/Two Pair/Full House scoring reliable. Beat The Hook in one pair hand. Added a Gold Ace for economy and a Glass Ten for future burst scoring.
- Ante 2: Bought The Duo and corrected joker order so additive Mult resolves before The Duo and Polychrome Egg. Skipped both blinds for another Coupon + Polychrome shop, then beat The Wall exactly enough with one Queens pair (3,240/3,200).
- Ante 3: Converted the large Egg sell value into Polychrome Rough Gem plus Throwback (X2, then X2.5 after two more skips). Cryptid copied QD twice, making Queens highly consistent. The money skip tag paid $25; Meteor upgraded Pair and Full House. Beat The Wheel with Queens full of Sixes for 26,880.
- Ante 4: Bought Telescope, added a Blue Seal Mult Ace and Glass Nine, and leveled Full House and Pair. Skipped D6 + Orbital to scale Throwback to X3 and gain hand levels. A Glass Ten pair one-shot The Club for 22,464.
- Ante 5: Orbital had raised Full House to level 7; Telescope pushed it to level 8. Thinned two low cards, bought cheaper rerolls, and skipped both blinds to scale Throwback to X3.5. Converted the Blue Seal Ace to Steel, held it while playing Tens, and barely cleared The House at 22,344/22,000; the seal generated Mercury.
- Ante 6: Replaced Jolly Joker with a free Holographic Gros Michel (+25 additive Mult total), correctly placing it before all XMult. Death copied a Glass Ten; a Standard tag added another Holographic Glass Ten and a Gold Seal Queen. Skipping raised Throwback to X4 and paid $60. Avoided The Ox's likely Pair penalty by playing Tens full of Aces with two Glass Tens for 455,820; money stayed intact.
- Ante 7: Gros Michel went extinct after the Small Blind's 323,748 Glass Full House. Filled the gap with Holographic To Do List (+10 Mult), raised Full House to level 11, and skipped Big for Investment/Throwback X4.25. The Head required two Glass Three-of-a-Kind hands after the first scored only 61,200; cleared at 99,705 with one hand left.
- Ante 8: Replaced Holographic To Do List with Abstract Joker (+15 Mult), raised Full House to level 15, used Strength to turn a Jack into another Queen, and added a Steel Nine. Cleared Small in two hands (best 46,512), skipped Big to reach Throwback X4.5, restored the shuffled joker order against Amber Acorn, and won with Eights full of Aces for 332,478/100,000.
- Ante 9 (Endless): Bought Clearance Sale, raised Full House to level 16, and added a Foil Steel Ten. Skipped both Coupon blinds to reach Throwback X5. Against The Mark, found Queens full of Tens with a Glass Ten while holding the Steel Blue-Seal Ace; scored 1,061,775 and generated another Earth.
- Ante 10 (Endless): Raised Full House to level 17, thinned two low cards, converted another low card to Stone, and skipped both blinds to reach Throwback X5.5. Against The Tooth, four discards produced repeated pairs but never a Full House. Three Pair hands totaled only 296,620/1,120,000; the final Glass/Holographic Ten pair with a Stone card scored 177,556 and exhausted the last hand.
- Win screen reached after beating Ante 8 (game reports `won=True`, state paused at round evaluation / win screen). No further API actions taken; awaiting the operator's manual Endless selection.

## Per-ante best single hand

- Ante 1: 2,983 (Queens full of Twos; replayed ante after Hieroglyph)
- Ante 2: 3,240 (Pair of Queens)
- Ante 3: 26,880 (Queens full of Sixes)
- Ante 4: 22,464 (Glass Ten pair)
- Ante 5: 22,344 (Steel-supported Ten pair)
- Ante 6: 455,820 (Glass Tens full of Aces)
- Ante 7: 323,748 (Glass Eights full of Sevens)
- Ante 8: 332,478 (Eights full of Aces)
- Ante 9: 1,061,775 (Glass Queens full of Tens, Steel held)
- Ante 10: 177,556 (Glass/Holographic Ten pair with Stone, Steel held)

## Overall best single hand

- 1,061,775

## Post-mortem

- Final ante: 10.
- Best single hand: 1,061,775 on Ante 9 (Queens full of Tens, one Glass/Holographic Ten, Foil Ten, and a held Steel Blue-Seal Ace).
- Exact end: GAME_OVER at Ante 10 boss The Tooth. The blind required 1,120,000; all three hands plus four discards produced 296,620 total, leaving 823,380 unmet when hands reached zero. The hand search never found a Full House, so the level-17 Full House scaling could not activate.
- Lessons for this seed:
  - After Holographic Gros Michel went extinct, prioritize finding Cavendish much more aggressively; X3 would have been substantially better than the eventual +15 Abstract Joker replacement.
  - At Ante 10, play the Small Blind to obtain another shop instead of skipping both blinds. The extra shop/reroll access for Cavendish or another XMult source was worth more than the final +0.25 Throwback increment.
  - Avoid taking Top-up/Buffoon-style skip tags while joker slots are full; those rewards were wasted and only supplied Throwback scaling.
  - Continue concentrating the deck into Tens and Queens, but remove more off-rank cards earlier. Even with many copies, the final draw sequence was too diluted to reliably form a Full House.
  - Preserve a flexible Death/Strength tarot for the final boss when possible; consumables spent on low-card thinning and Stone conversion improved the deck long-term but could not repair the immediate boss hand.

## Consent

I consent to this run's results and journal being shared publicly, including on leaderboards, GitHub, and benchmark write-ups. Context to include: this was an autonomous API-driven benchmark run on seed `BENCHMRK`; it legitimately cleared Ante 8, continued into Endless, and ended at The Tooth in Ante 10. No result correction is requested.
