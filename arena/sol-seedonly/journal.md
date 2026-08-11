# BENCHMRK Run Journal

## Build plan

- Prioritize reliable blind clears and ante progression over speculative economy.
- Use the known shop/pack order to target scalable scoring, with early tempo from accessible jokers and a transition toward retrigger/multiplicative scoring when offered.
- Preserve enough cash for high-impact known purchases and packs; skip only when the tag is clearly stronger than playing the blind.
- Track every play from the round chip delta and record each ante's best single hand.

## Progress

- Ante 1: skipped Small and Big for Coupon + Polychrome tags, cleared The Pillar, bought free Polychrome Egg/Blue Joker and Hieroglyph, then replayed ante 1 with Mad + Jolly support. The Hook fell to a 2,562 two-pair hand.
- Ante 2: pivoted from Blue/Jolly into Duo + Swashbuckler around the scaling Egg, ordered additive mult before Xmult, and added Scary Face. A Q-Q-9-9-9 full house one-shot The Wall for 18,081.
- Ante 3: replaced Mad with Throwback, took a red-seal Bonus Queen from the known Jumbo Standard pack, and skipped Big for Meteor plus another Throwback stack. The red-seal Queen pair beat The Wheel for 43,890.
- Ante 4: added a blue-seal Mult Ace and Glass 9, raised Pair again, then skipped Big for Orbital and X2 Throwback. A clean non-club Queen pair beat The Club for 36,450.
- Ante 5: used the Fool and repeated blue-seal triggers to drive Pair to level 7, replaced Scary Face with Photograph, added a second blue seal and a held Steel Ten. Photograph plus held steel let a King pair one-shot The House for 52,560.
- Ante 6: duplicated the Gold Ace, added more steel/glass cards, and advanced Pair to level 9. The Ox zeroed the small bankroll as expected, but a Photograph King pair cleared it for 70,200.
- Ante 7: bought Telescope, skipped Big for Investment and X2.25 Throwback, then played a mixed-suit Jack pair through The Head while holding a live Steel Ten. The boss fell for 88,830.
- Ante 8: Telescope pushed Pair to level 13; held steel produced 121,621 on Big Blind. Against Amber Acorn, the shuffle left Swashbuckler before all Xmult, and Strength converted the Glass Tens into a Glass Jack pair. Photograph + Glass scored 182,857, cleared the boss, and reached the win screen. Paused here for the operator before Endless.
- Ante 9: resumed Endless, bought Blank, used a Coupon shop for free planets and premium cards, and raised Pair to level 16. The Mark required two hands; a held Steel Ace powered the 198,288 opener, and the Ace pair finished at 383,328 total.

## Per-ante best hands

- Ante 1 best single hand: 2562
- Ante 2 best single hand: 18081
- Ante 3 best single hand: 43890
- Ante 4 best single hand: 36450
- Ante 5 best single hand: 52560
- Ante 6 best single hand: 70200
- Ante 7 best single hand: 88830
- Ante 8 best single hand: 182857
- Ante 9 best single hand: 198288
- Ante 10 best single hand: 586687
- Ante 11 best single hand: 1074154

## Ante 10

- Cleared the Small Blind with 612,561 total chips, then cleared the Big Blind with 908,685 total chips, using all available hands in each round. The pre-patch Invisible Joker sale twice froze the RPC, but the restored run and patched API allowed the sale to resolve.
- Invisible Joker duplicated Throwback, producing two X2.5 Throwbacks alongside Duo and Polychrome Egg. Added a gold-seal Wild 5, then beat The Tooth's 1,120,000 target in two pairs for 1,153,687 total. The second pair scored 586,687 and the held blue seal generated Mercury level 19.

## Ante 11

- Applied Mercury, bought Overstock, and opened the known Jumbo Arcana pack. Tried to use Death to copy a Glass Jack onto a normal Jack, but the API normalized the target order and copied the normal card over the glass card instead, removing the glass enhancement.
- With blinds jumping to 7.2M/10.8M and The Mouth at 14.4M, skipped both non-boss blinds to raise both Throwbacks from X2.5 to X3.0 and took the Negative and Uncommon tags.
- Used all four discards before the first play to search for glass cards while retaining a Steel 7. None appeared. Three legal Pair hands scored 1,074,154, 977,629, and 1,016,347, totaling 3,068,130 against the 14,400,000 target.

## Post-mortem

- Final ante reached: **11**.
- Best single hand: **1,074,154**.
- Exact end condition: failed Ante 11 boss The Mouth. The run scored 3,068,130 with three Pair hands versus the required 14,400,000, then entered `GAME_OVER` with no hands remaining.
- Lessons for a future BENCHMRK attempt: the Mercury/Telescope Pair scaling, blue seals, held steel, and duplicated Throwback chain were sufficient through Ante 10, but Ante 11's exponential blind jump demanded repeatable glass or another scaling Xmult source. Preserve the Glass Jack when using Death: the API sorts/normalizes target indices, so arrange the hand first and pass the lower-index source as the card to be converted. Reaching Constellation before Ante 11, or retaining Photograph and the glass pair instead of gambling its conversion, would provide a much stronger chance at the 14.4M Mouth.
