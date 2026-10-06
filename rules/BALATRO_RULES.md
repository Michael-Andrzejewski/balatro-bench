# Balatro rules reference (from the game's source code)

Written 2026-10-05/06 from the vanilla Lua source of Balatro 1.0.1o (extracted from Balatro.exe), plus the BalatroBot API source (1.5.2) and the Steamodded patches it runs on. Every claim was read from code, most with a file:line citation; anything the code leaves ambiguous is marked as such. Treat this file as ground truth over wikis or memory.

Sections:
1. Core rules and the bot API (setup, scoring order, blind sizes, economy, shop, packs, card draw, endpoints)
2. Jokers 1 to 75 (Joker through Obelisk)
3. Jokers 76 to 150 (Midas Mask through Perkeo)
4. Tarots, Planets, Spectrals, Vouchers, Tags, Boss Blinds, enhancements, editions, seals



---

# 01. Core rules and the bot API

Derived from source code only. File references are given so any line can be re-checked.

- Vanilla source (1.0.1o): `scratchpad/balatro-src/` (game.lua, card.lua, cardarea.lua, blind.lua, tag.lua, back.lua, functions/*.lua).
- Bot API (BalatroBot 1.5.1): `C:\Users\maaro\AppData\Roaming\Balatro\Mods\balatrobot\src\lua\`.

## 0. Read this first: the runtime is vanilla patched by Steamodded

BalatroBot declares `"dependencies": ["Steamodded (>=1.~)"]` (balatrobot.json) and loads every file through `SMODS.load_file`. So the game the bot plays is vanilla Lua with Steamodded's patches applied (Steamodded version file says `26.829.0`, folder `Mods\smods`). Steamodded replaces some vanilla code paths. I spot-checked the ones that matter for this section:

| Area | Vanilla | Steamodded runtime | Effect on rules |
|---|---|---|---|
| Booster pack state | `TAROT_PACK`, `PLANET_PACK`, `SPECTRAL_PACK`, `STANDARD_PACK`, `BUFFOON_PACK` | One state for every pack: `SMODS_BOOSTER_OPENED` (smods/lovely/booster.toml line 36) | State name only. The API uses `SMODS_BOOSTER_OPENED`. |
| Which packs deal you a hand | Arcana and Spectral call `draw_from_deck_to_hand` | Arcana and Spectral have `draw_hand = true`; Celestial, Standard, Buffoon do not (smods/src/game_object.lua ~1743, ~1829) | Same as vanilla. |
| Pack card generation keys | `ar1`/`ar2`, `pl1`, `spe`, `sta`, `buf` | Same keys (game_object.lua ~1750-1880) | Same. |
| Scoring loop | `G.FUNCS.evaluate_play` | Rewritten by smods/lovely/better_calc.toml into `SMODS.calculate_main_scoring` / `SMODS.score_card` / `SMODS.trigger_effects` | Order of operations for vanilla content is the same (checked below in section 2.6). |
| Joker rarity roll | `rarity > 0.95` Rare, `> 0.7` Uncommon, else Common | `SMODS.poll_rarity` with weights Common 0.7, Uncommon 0.25, Rare 0.05, same seed key | Same probabilities. |
| Number display | `number_format` | Patched: infinity prints `naneinf`, mantissa 2 decimals for exponents 10 to 99, 1 decimal for exponent 100+ | Display only. |
| Optional "object weights" pool system | n/a | Only active if some mod turns `SMODS.optional_features.object_weights` on | Off with only BalatroBot loaded, so vanilla pools apply. |

Everything else in this file is vanilla behaviour, and where I found a Steamodded difference it is called out. I did not audit all of Steamodded; anything not listed above is assumed unchanged and that assumption is flagged in section 9.

---

## 1. Run setup for this benchmark (Red Deck, White Stake)

Defaults come from `get_starting_params()` (functions/misc_functions.lua 1868):

| Parameter | Base value | Red Deck change | White Stake change | Value in this run |
|---|---|---|---|---|
| Starting money | $4 | none | none | **$4** |
| Hands per round | 4 | none | none | **4** |
| Discards per round | 3 | +1 (`b_red config = {discards = 1}`, game.lua 628; applied in back.lua `apply_to_run`: `starting_params.discards + config.discards`) | none | **4** |
| Hand size | 8 | none | none | **8** |
| Joker slots | 5 | none | none | **5** |
| Consumable slots | 2 | none | none | **2** |
| Base reroll cost | $5 | none | none | **$5** |
| Interest cap | $25 (= max $5 interest) | none | none | **$25** |
| Max cards per play or discard | 5 (`highlighted_limit` default 5, cardarea.lua 18) | none | none | **5** |
| Ante scaling | 1 | none | none | **1** |

- Red Deck has no other effect. `Back:trigger_effect` only has code for Anaglyph and Plasma (back.lua).
- White Stake is stake 1. `Game:start_run` (game.lua 2050-2059) only adds modifiers for stake >= 2 (no Small Blind reward), >= 3 (faster scaling), >= 4 (eternals), >= 5 (-1 discard), >= 6, >= 7 (perishables), >= 8 (rentals). None apply at stake 1. So: Small Blind pays money, blind scaling is the base table, no eternal/perishable/rental stickers ever appear.
- `G.GAME.win_ante = 8`. Inflation is 0 and never increases (only the `inflation` challenge modifier raises it).
- Deck: the standard 52 cards. Shuffled once at run start with key `shuffle`.
- At run start, in this order: Boss for ante 1 (`get_new_boss`), the ante-1 voucher (`get_next_voucher_key`), the Small Blind tag, the Big Blind tag (game.lua 2177-2180).
- A run started with a seed sets `G.GAME.seeded = true`. In seeded runs `check_for_unlock`, `unlock_card` and `discover_card` return immediately (common_events.lua 1165, 1630, 1880). Nothing is unlocked or discovered during the run, so pool contents that depend on unlock/discovery state stay fixed at whatever the profile had before the run (see section 9).

---

## 2. Scoring

### 2.1 Poker hand base values and level-ups

From `init_game_object` (game.lua 1990-2003). A hand at level L has `chips = s_chips + l_chips*(L-1)` (minimum 0) and `mult = s_mult + l_mult*(L-1)` (minimum 1) (`level_up_hand`, common_events.lua 464).

| Hand | Base chips | Base mult | +chips per level | +mult per level | Visible at start |
|---|---|---|---|---|---|
| Flush Five | 160 | 16 | 50 | 3 | no |
| Flush House | 140 | 14 | 40 | 4 | no |
| Five of a Kind | 120 | 12 | 35 | 3 | no |
| Straight Flush | 100 | 8 | 40 | 4 | yes |
| Four of a Kind | 60 | 7 | 30 | 3 | yes |
| Full House | 40 | 4 | 25 | 2 | yes |
| Flush | 35 | 4 | 15 | 2 | yes |
| Straight | 30 | 4 | 30 | 3 | yes |
| Three of a Kind | 30 | 3 | 20 | 2 | yes |
| Two Pair | 20 | 2 | 20 | 1 | yes |
| Pair | 10 | 2 | 15 | 1 | yes |
| High Card | 5 | 1 | 10 | 1 | yes |

### 2.2 Card values

`Card:set_base` (card.lua 97-146):

| Rank | Chips (nominal) | id |
|---|---|---|
| 2 to 10 | face value | 2 to 10 |
| Jack | 10 | 11 |
| Queen | 10 | 12 |
| King | 10 | 13 |
| Ace | 11 | 14 |

Played card chips = `nominal + ability.bonus + perma_bonus` (`get_chip_bonus`, card.lua 976). Bonus Card adds 30 to `bonus`. Stone Card scores only `bonus (50) + perma_bonus`, no rank chips. A debuffed card returns 0 from every scoring getter.

Enhancement values (game.lua 648-655): Bonus +30 chips; Mult +4 mult; Wild any suit; Glass x2 mult and 1 in 4 destroy chance; Steel x1.5 mult while held; Stone +50 chips, no rank or suit; Gold $3 if held at end of round; Lucky 1 in 5 for +20 mult and 1 in 15 for $20.
Editions (game.lua 659-662): Foil +50 chips, Holographic +10 mult, Polychrome x1.5 mult, Negative +1 slot (no scoring effect).
Seals: Red = retrigger once; Gold = +$3 when scored (`get_p_dollars`, card.lua 1068); Blue and Purple are not scoring effects.

### 2.3 How the poker hand is identified

`G.FUNCS.get_poker_hand_info` (state_events.lua 540) calls `evaluate_poker_hand` (misc_functions.lua 376) on **all played cards** and takes the first match in this priority order: Flush Five, Flush House, Five of a Kind, Straight Flush, Four of a Kind, Full House, Flush, Straight, Three of a Kind, Two Pair, Pair, High Card.

The parts:
- **N of a kind** (`get_X_same`): groups cards by `get_id()`. A group counts only if its size is **exactly** N. So four Kings are not a Pair group; instead, after detection, a Five of a Kind result is copied down into Four of a Kind, Four into Three, Three into Pair (misc_functions.lua 507-517).
- **Two Pair** needs exactly two groups of exactly 2, or one group of 3 plus one group of 2.
- **Flush** (`get_flush`): only checked if 5 cards are played (4 or 5 with Four Fingers; never more than 5). Suit test uses `is_suit(suit, nil, true)`: Stone never counts; Wild counts for every suit **unless debuffed**; Smeared Joker merges Hearts/Diamonds and Spades/Clubs. Suits are tried in order Spades, Hearts, Clubs, Diamonds and the first that reaches 5 (or 4) wins.
- **Straight** (`get_straight`): only with exactly 5 played (4 or 5 with Four Fingers). Uses ids 2 to 14; Ace counts as both 1 (low, A-2-3-4-5) and 14 (high, 10-J-Q-K-A). No wrap-around (Q-K-A-2-3 is not a straight). Shortcut lets one rank be skipped once per gap.
- **High Card** (`get_highest`): the single card with the highest `get_nominal()`.
- **Stone Cards** return a random negative id on every `get_id()` call (card.lua 957), so they never pair, never make straights, never make flushes.
- Debuffed cards still count toward identifying the hand (id and base suit are not debuff-checked), but they score nothing.
- "Royal Flush" is only a display name for a Straight Flush whose lowest id is 10 or more; it scores as Straight Flush.

**Which cards score** (`scoring_hand`): only the cards that form the hand. Example: Pair played with 3 other cards scores only the 2 paired cards. Two Pair scores 4 cards. Flush/Straight/Full House/Straight Flush score all cards in that part.
Additions (state_events.lua 580-597):
- **Stone Cards** that were played but are not part of the hand are always added to the scoring hand ("pure bonus" cards).
- **Splash** (if owned and not debuffed): every played card scores.
- The scoring hand is then **sorted by on-screen x position, left to right**. That left-to-right order is the scoring order.

If the boss blind rejects the hand (`Blind:debuff_hand`, for example The Psychic with fewer than 5 cards, The Eye repeated hand type, The Mouth wrong type), chips and mult are set to 0, the hand scores 0, jokers get only the `debuffed_hand` context, and the hand is still used up.

### 2.4 Order of operations (vanilla `G.FUNCS.evaluate_play`, state_events.lua 571-1086)

Two running numbers: `hand_chips` and `mult`. Final score of the hand = `floor(hand_chips * mult)`.

1. **Hand statistics.** `played` and `played_this_round` for the identified hand +1. The hand becomes visible.
2. **"Before" joker phase.** Each joker, left to right, gets `context.before` (Space Joker level-up, Green Joker, Ride the Bus, Midas Mask, Vampire, etc.).
3. **Base values read after the before phase.** `mult = hands[text].mult`, `hand_chips = hands[text].chips`. So a level-up during step 2 counts for this hand.
4. **Boss modify.** The Flint: `mult = max(floor(mult*0.5+0.5),1)`, `chips = max(floor(chips*0.5+0.5),0)`.
5. **Each scoring card, left to right.** For each card:
   - If debuffed: no effect at all (no chips, no retriggers), shows "Debuffed".
   - Otherwise build the repetition list first: 1 normal pass, +1 for a Red Seal, + each joker's `context.repetition` result (Sock and Buskin, Hanging Chad, Dusk, Seltzer, Hack, Mime does not apply here). Then for **each pass**:
     a. The card's own effects, applied in this order: chips (`get_chip_bonus`), +mult (Mult Card, Lucky roll), Xmult (Glass x2; Steel is not here), money (Gold Seal $3, Lucky $20 roll), then the card's **edition**: Foil +50 chips, Holo +10 mult, Polychrome x1.5.
     b. Then each joker left to right with `context.individual` and `other_card = this card` (for example Greedy/Lusty/Wrathful/Gluttonous, Scholar, Walkie Talkie, Fibonacci, Even Steven, Odd Todd, Smiley, Photograph, Triboulet, Bloodstone, Ancient Joker, Idol, Arrowhead, Onyx Agate, Hiker, Golden Ticket, Business Card, Rough Gem, Lucky Cat). Within one joker's result the order is: chips, mult, money, extra, Xmult.
     Every retrigger repeats a and b completely, including new Lucky rolls.
6. **Held-in-hand phase.** Each card still in hand, left to right:
   - The card's own held effects: Steel x1.5 (`h_x_mult`).
   - Each joker's held effect (`context.individual`, `cardarea = G.hand`): Baron, Shoot the Moon, Raised Fist, Reserved Parking ($).
   - Retriggers for held cards (Red Seal, Mime) are added **only if the card produced some effect on its first pass** (state_events.lua 822-824). So a Red Seal on a plain held card does nothing here.
   - Per effect the order is: money, +mult (`h_mult`), Xmult.
   - Gold Card's $3 is **not** paid here; it is paid at end of round (section 4).
7. **Joker phase.** For each card in the joker row left to right, **then each card in the consumable row** (`for i=1, #G.jokers.cards + #G.consumeables.cards`):
   a. The joker's edition, additive part: Foil +50 chips, Holo +10 mult.
   b. The joker's own main effect (`context.joker_main`): +mult, +chips, then Xmult. (Vanilla order inside one result: mult_mod, chip_mod, Xmult_mod.)
   c. "Joker on joker" effects: every joker is asked about this card (`other_joker`). Only Baseball Card uses this in vanilla (x1.5 for each Uncommon joker, applied when that Uncommon joker's turn comes).
   d. The joker's edition, multiplicative part: Polychrome x1.5.
   In the consumable row, the only vanilla effect is Observatory: each Planet card in the consumable row whose hand matches gives x1.5 at its turn (card.lua 2293-2302). Because consumables come after all jokers, Observatory multipliers are applied last.
8. **Deck end step.** `selected_back:trigger_effect{context = 'final_scoring_step'}`. Only Plasma Deck acts. Red Deck: nothing.
9. **Destruction step.** For each card in the scoring hand: jokers with `context.destroying_card` (Sixth Sense...) can mark it destroyed; then a **Glass Card** that is not debuffed is destroyed if `pseudorandom('glass') < probabilities.normal / 4` (1 in 4; Oops! All 6s doubles `normal`). This happens **after all scoring and all retriggers**, once per card regardless of how many times it was retriggered. Then jokers get `remove_playing_cards` (Glass Joker, Caino). Destroyed cards are removed from the game; they do not go to the discard pile.
10. **Score added.** `G.GAME.chips` eases to `G.GAME.chips + floor(hand_chips * mult)`.
11. **"After" joker phase** (`context.after`): Ice Cream, Seltzer countdown, etc.
12. Played cards (not destroyed) go to the discard pile; `hands_played` +1.

**Where each kind of number is applied, and why order matters.** Chips and +mult are added to the running totals. Xmult multiplies **the mult accumulated so far**. So +mult that comes later is not multiplied by an earlier Xmult. Example: base mult 4, Polychrome card (x1.5) scored first, then a joker giving +10 mult: mult = 4 x 1.5 + 10 = 16. If the +10 came first: (4+10) x 1.5 = 21. Within the joker phase, jokers further right act on the result of jokers further left, so place +mult jokers left of Xmult jokers. Played-card Xmult (Glass, Polychrome cards, Triboulet, Bloodstone) happens before held-card Xmult (Steel, Baron), which happens before joker-row Xmult.

### 2.5 Retriggers and probabilities, recap

- Retrigger sources on played cards are counted once, before the first pass; each adds one complete extra pass.
- Lucky Card: two independent rolls per pass (`lucky_mult` 1 in 5, `lucky_money` 1 in 15), each scaled by `G.GAME.probabilities.normal`.

### 2.6 Steamodded's version of the loop (the code that actually runs)

Checked in smods/lovely/better_calc.toml and smods/src/utils.lua 2216-2290, 1499-1545:
- Played cards are iterated in `G.play.cards` order (left to right). Cards in the scoring hand are scored; unscored played cards get an `'unscored'` context that no vanilla joker uses.
- Per card the effect tables are applied in the order `playing_card` (chips, mult, Xmult from Glass, money), then `enhancement`, then `edition`, then `seals`, then each joker's `individual` result left to right. Same as vanilla.
- Inside one effect table Steamodded applies keys in its own list order: chips first, then mult, then x_chips, then Xmult, then money. Vanilla applied money before Xmult. Score is identical; only animation timing differs.
- Retriggers: Steamodded computes the repetition list **after** the first pass, and only if the first pass produced any effect (`flags.calculated`). For played cards this never matters in vanilla content, because a scoring, non-debuffed card always gives chips.
- Joker phase per joker: pre-joker edition (Foil/Holo), `joker_main`, other-joker effects, post-joker edition (Polychrome). Same as vanilla. Areas iterated: jokers then consumables.
- Destruction step uses `SMODS.calculate_destroying_cards`; Glass destruction is still a 1-in-4 roll per scored Glass card after scoring.

### 2.7 Overflow and naneinf

- Lua numbers are doubles. The largest finite value is about 1.797e308. A hand whose `hand_chips * mult` exceeds that becomes `inf`.
- `G.GAME.chips` then becomes `inf`. `inf - blind_chips >= 0` is true, so the blind is beaten.
- Display: vanilla `number_format(inf)` produces the text `naneinf` by accident (`"nan".."e".."inf"`). Steamodded patches `number_format` to return `naneinf` explicitly for infinity (smods/lovely/number_formatting.toml lines 116-123). Numbers at or above 1e11 are shown in scientific notation: Steamodded shows 2 decimals for exponents 10 to 99 (`2.90e13`) and 1 decimal for exponent 100 and above (`4.5e288`). Below 1e11 numbers are shown with thousands commas.
- **API and infinite numbers.** The JSON encoder (smods/libs/json/json.lua line 107-110) refuses `inf` and `nan`. Since BalatroBot 1.5.2 the server retries the encode with every infinite or NaN number replaced by the string `"inf"`, `"-inf"` or `"nan"` (core/server.lua). So after a naneinf hand, fields such as `round.chips` arrive as the string `"inf"` instead of a number. (Before 1.5.2 the response was dropped and the call timed out after 60 seconds.) `cash_out` eases `G.GAME.chips` back to 0 (button_callbacks.lua 2948).
- A NaN score (for example `inf * 0`) makes `G.GAME.chips` NaN; every comparison with NaN is false, so the blind can never be beaten after that.

---

## 3. Blind chip requirements

### 3.1 Formula

`Blind:set_blind` (blind.lua 107): `chips = get_blind_amount(ante) * blind.mult * starting_params.ante_scaling` (ante_scaling = 1 here).

`get_blind_amount(ante)` with no scaling modifier (White Stake) (misc_functions.lua 919-931):
- ante < 1: 100
- antes 1 to 8: 300, 800, 2000, 5000, 11000, 20000, 35000, 50000
- ante > 8: `a = 50000, b = 1.6, c = ante - 8, d = 1 + 0.2*(ante-8)`; `amount = floor(a * (b + (0.75*c)^d)^c)`; then truncated to 2 significant figures: `amount = amount - amount % 10^(floor(log10(amount)) - 1)`.

Blind multipliers (game.lua 264-295): Small 1, Big 1.5, ordinary bosses 2, **The Wall 4**, **The Needle 1**, finisher bosses 2 except **Violet Vessel 6**.

### 3.2 Table, antes 1 to 20 (computed from the formula above)

| Ante | Small (x1) | Big (x1.5) | Boss (x2) | The Wall (x4) | The Needle (x1) | Violet Vessel (x6) |
|---|---|---|---|---|---|---|
| 1 | 300 | 450 | 600 | 1,200 | 300 | n/a |
| 2 | 800 | 1,200 | 1,600 | 3,200 | 800 | n/a |
| 3 | 2,000 | 3,000 | 4,000 | 8,000 | 2,000 | n/a |
| 4 | 5,000 | 7,500 | 10,000 | 20,000 | 5,000 | n/a |
| 5 | 11,000 | 16,500 | 22,000 | 44,000 | 11,000 | n/a |
| 6 | 20,000 | 30,000 | 40,000 | 80,000 | 20,000 | n/a |
| 7 | 35,000 | 52,500 | 70,000 | 140,000 | 35,000 | n/a |
| 8 | 50,000 | 75,000 | 100,000 | n/a (finisher ante) | n/a | 300,000 |
| 9 | 110,000 | 165,000 | 220,000 | 440,000 | 110,000 | n/a |
| 10 | 560,000 | 840,000 | 1,120,000 | 2,240,000 | 560,000 | n/a |
| 11 | 7,200,000 | 10,800,000 | 14,400,000 | 28,800,000 | 7,200,000 | n/a |
| 12 | 300,000,000 | 450,000,000 | 600,000,000 | 1,200,000,000 | 300,000,000 | n/a |
| 13 | 47,000,000,000 | 70,500,000,000 | 94,000,000,000 | 1.88e11 | 47,000,000,000 | n/a |
| 14 | 2.9e13 | 4.35e13 | 5.8e13 | 1.16e14 | 2.9e13 | n/a |
| 15 | 7.7e16 | 1.155e17 | 1.54e17 | 3.08e17 | 7.7e16 | n/a |
| 16 | 8.6e20 | 1.29e21 | 1.72e21 | n/a (finisher ante) | n/a | 5.16e21 |
| 17 | 4.2e25 | 6.3e25 | 8.4e25 | 1.68e26 | 4.2e25 | n/a |
| 18 | 9.2e30 | 1.38e31 | 1.84e31 | 3.68e31 | 9.2e30 | n/a |
| 19 | 9.2e36 | 1.38e37 | 1.84e37 | 3.68e37 | 9.2e36 | n/a |
| 20 | 4.3e43 | 6.45e43 | 8.6e43 | 1.72e44 | 4.3e43 | n/a |

Notes:
- On antes 8, 16, 24, ... only finisher bosses can appear (section 6.3); on other antes only ordinary bosses. Finisher bosses other than Violet Vessel use x2, so their requirement equals the "Boss (x2)" column.
- Beyond ante 20 the base amount keeps growing: ante 25 is 2.4e87, ante 30 is 2.1e149, ante 35 is 2.8e230, **ante 38 is 4.5e288** (Boss x2 = 9.0e288, still finite).
- **Ante 39 and later:** the power overflows to `inf`, and the truncation step computes `inf % inf = nan`, so the blind requirement becomes **NaN**. `G.GAME.chips - NaN >= 0` is always false, so no score, even naneinf, can beat an ante-39 blind. The run cannot pass ante 39. (The API reports the NaN requirement as the string `"nan"`, see 2.7.)
- The API reports these numbers in `blinds.small/big/boss.score`, computed as `floor(get_blind_amount(ante) * blind.mult * ante_scaling)` for the blinds currently assigned (utils/gamestate.lua `get_blinds_info`).

---

## 4. Economy

### 4.1 End-of-round money (`G.FUNCS.evaluate_round`, state_events.lua 1135-1208)

Shown on the round-evaluation screen and paid all at once when you **cash out**:

| Row | Amount |
|---|---|
| Blind reward | Small $3, Big $4, ordinary Boss $5, finisher Boss (ante 8, 16...) $8 (game.lua 264-295). White Stake keeps the Small reward. |
| Remaining hands | $1 for each hand not used (`money_per_hand` is nil, so 1). |
| Remaining discards | $0 (only Green Deck sets `money_per_discard`). |
| Joker payouts | `calculate_dollar_bonus`: Golden Joker, Cloud 9, Rocket, Satellite, Delayed Gratification. |
| Tags | Investment Tag ($25, only when the blind just beaten was a Boss). |
| Interest | `interest_amount * min(floor(dollars/5), interest_cap/5)` = $1 per full $5 held, capped at $5 (cap $25). Only if dollars >= 5. |

Interest timing: it is computed from `G.GAME.dollars` when the evaluation screen is built. That includes money already gained during the round (Gold Seals, Lucky money, Business Card, held Gold Cards at end of round, which are paid in `end_round` before this screen), but **not** the blind reward, hand money, joker payouts and tag payouts on the same screen (they are added at cash out). Interest cap by voucher: Seed Money sets `interest_cap = 50` (max $10), Money Tree sets it to 100 (max $20) (card.lua `apply_to_run`).

Gold Card: $3 per Gold Card held in hand at end of round (`get_end_of_round_effect`, card.lua 1033), paid during `end_round`, with Red Seal / Mime retriggers if applicable.

### 4.2 Reroll cost (`calculate_reroll_cost`, common_events.lua 2263; `G.FUNCS.reroll_shop`, button_callbacks.lua 2855)

- Cost = `round_resets.reroll_cost` (base $5) + `reroll_cost_increase`.
- Each paid reroll adds 1 to the increase: $5, $6, $7, ...
- The increase resets to 0 in `new_round()` (state_events.lua 300), which runs when you **select** the next blind. So every shop starts at $5 (with no vouchers). Skipping a blind does not run `new_round`.
- Free rerolls (Chaos the Clown: 1 per round, reset in `new_round`) cost $0 and do not increase the cost.
- D6 Tag: `temp_reroll_cost = 0` for that shop, so rerolls cost $0, $1, $2, ... until the end of the next round.
- Reroll Surplus and Reroll Glut each lower the base by $2 permanently.
- A reroll replaces only the joker/consumable card slots. Packs and the voucher are not rerolled.

### 4.3 Buy prices (`Card:set_cost`, card.lua 369)

`cost = max(1, floor((base_cost + extra_cost + 0.5) * (100 - discount_percent) / 100))`, where `extra_cost = inflation (0) + edition surcharge`.

| Item | base_cost |
|---|---|
| Joker | its center `cost` (varies by joker) |
| Tarot | 3 |
| Planet | 3 |
| Spectral | 4 |
| Voucher | 10 |
| Booster: normal / jumbo / mega | 4 / 6 / 8 |
| Playing card (Magic Trick / Illusion shop cards) | 1 (no `cost` on `c_base` or enhancement centers, so `center.cost or 1`) |

Edition surcharge: Foil +2, Holographic +3, Polychrome +5, Negative +5.
Discounts: Clearance Sale 25%, Liquidation 50% (replaces, does not stack). Examples with 25%: $3 item -> $2, $4 -> $3, $5 -> $4, $6 -> $4, $8 -> $6, $10 -> $7. With 50%: $3 -> $1, $4 -> $2, $6 -> $3, $8 -> $4, $10 -> $5.
Other overrides: Astronomer makes Planets and Celestial packs cost $0. Coupon Tag makes the shop's initial joker/consumable cards and packs cost $0 (vouchers are not affected; cards added by reroll are not couponed). Rental sets cost to $1 (not at White Stake).
Affordability: you can buy if `cost <= dollars - bankrupt_at` (`bankrupt_at` is 0, or -20 with Credit Card).

### 4.4 Sell value

`sell_cost = max(1, floor(cost / 2)) + extra_value` (card.lua 381), computed from the current `cost` **before** the Coupon override sets cost to 0. So couponed items still sell for half their normal price. With Astronomer a Planet's cost is 0, so it sells for $1. `extra_value` grows with Egg, Gift Card and similar. Selling is allowed for anything in the joker or consumable rows (both areas have type `'joker'`), except eternal cards, and not while cards are in the play area.

### 4.5 Money from skipping

Skipping a blind gives **no blind reward, no hand money and no interest** for that blind (there is no round). You get the blind's tag. Money tags:
- Skip Tag: `$5 * G.GAME.skips`, and `skips` is incremented before the tag is added, so the count includes this skip (button_callbacks.lua 2755; tag.lua 149-156).
- Economy Tag: gain `min(40, max(0, dollars))` (doubles your money, max $40).
- Handy Tag: $1 per hand played this run (`G.GAME.hands_played`).
- Garbage Tag: $1 per unused discard this run (`G.GAME.unused_discards`, which adds each round's leftover discards).
- Investment Tag: $25 on the evaluation screen after the next Boss is beaten.

---

## 5. Shop, packs and the random number streams

### 5.1 Shop layout

- **Card slots: 2** (`G.GAME.shop.joker_max = 2`; Overstock and Overstock Plus each +1 via `change_shop_size`). Bought slots stay empty until a reroll.
- **Pack slots: 2.** Rolled once per round when the shop opens (`G.GAME.current_round.used_packs`, game.lua 3145-3156) and not refilled after purchase. `used_packs` resets in `new_round`.
- **Voucher slot: 1.** The voucher is chosen when the previous Boss is beaten (in `end_round`, after the ante has increased) or at run start. It stays the same in every shop of that ante until bought. After buying it, no voucher appears for the rest of the ante (unless a Voucher Tag adds one).
- A completely new shop is generated for each round's shop.

### 5.2 What a shop card slot contains (`create_card_for_shop`, UI_definitions.lua 742)

Weights: `joker_rate 20`, `tarot_rate 4`, `planet_rate 4`, `playing_card_rate 0`, `spectral_rate 0` (game.lua 1900-1905). One roll `pseudorandom('cdt'..ante) * total` picks the type:

| Type | Weight | Chance (no vouchers) |
|---|---|---|
| Joker | 20 | 20/28 = 71.4% |
| Tarot | 4 | 14.3% |
| Planet | 4 | 14.3% |
| Playing card | 0 | 0% (Magic Trick sets 4) |
| Spectral | 0 | 0% (Ghost Deck only) |

Tarot Merchant sets tarot weight 9.6, Tarot Tycoon 32; Planet Merchant / Tycoon likewise for planets.
Before that roll, tags of type `store_joker_create` (Uncommon Tag, Rare Tag) can replace the card.

Joker rarity (`get_current_pool`, seed `'rarity'..ante..'sho'`): Common 70%, Uncommon 25%, Rare 5%. Legendary never appears in shops (only The Soul).
Joker edition (`poll_edition('edi'..'sho'..ante)`, common_events.lua 2055), with `edition_rate = 1`:

| Edition | Roll range | Chance | With Hone (rate 2) | With Glow Up (rate 4) |
|---|---|---|---|---|
| Negative | > 0.997 | 0.3% | 0.3% | 0.3% |
| Polychrome | 0.994 to 0.997 | 0.3% | 0.9% | 2.1% |
| Holographic | 0.98 to 0.994 | 1.4% | 2.8% | 5.6% |
| Foil | 0.96 to 0.98 | 2.0% | 4.0% | 8.0% |

Shop cards never contain The Soul or Black Hole (they are excluded from pools and shop cards are not "soulable").

### 5.3 Duplicate rule (`used_jokers`)

- `G.GAME.used_jokers[key] = true` is set whenever **any card** with that center is created (`Card:set_ability`, card.lua 346-352): jokers, tarots, planets, spectrals, vouchers, whether in the shop, in a pack, or owned.
- It is cleared when a card is removed (`Card:remove`, card.lua 4740-4748) **only if** no card with that name remains in the joker row or the consumable row (`find_joker` checks only those two areas).
- Pools exclude any key in `used_jokers` unless you own Showman (`get_current_pool`, common_events.lua 1987).
- Consequences: you cannot be offered a joker, tarot or planet that you currently hold in your joker or consumable rows. Two shop slots cannot show the same card at once. While a pack is open, its cards (and the current shop cards) are excluded from each other. A rerolled card is removed before new cards are made, so it can reappear on the very next reroll (unless you own a copy). Selling or using a card frees its key again.
- Planets for hidden hands (Planet X, Ceres, Eris) need that hand played at least once (`softlock`).
- Jokers with `enhancement_gate` (Steel Joker, Stone Joker, Lucky Cat, Golden Ticket, Glass Joker) appear only if your deck contains that enhancement.
- Steamodded keeps this rule (pool.toml: `used_jokers[v.key] and not pool_opts.allow_duplicates and not SMODS.showman(v.key)`).

### 5.4 Booster packs

From game.lua 665-696. "Shown" = cards in the pack, "Choose" = picks allowed.

| Pack | Cost | Shown | Choose | Shop weight (each variant) | Variants |
|---|---|---|---|---|---|
| Arcana | 4 | 3 | 1 | 1 | 4 |
| Jumbo Arcana | 6 | 5 | 1 | 1 | 2 |
| Mega Arcana | 8 | 5 | 2 | 0.25 | 2 |
| Celestial | 4 | 3 | 1 | 1 | 4 |
| Jumbo Celestial | 6 | 5 | 1 | 1 | 2 |
| Mega Celestial | 8 | 5 | 2 | 0.25 | 2 |
| Standard | 4 | 3 | 1 | 1 | 4 |
| Jumbo Standard | 6 | 5 | 1 | 1 | 2 |
| Mega Standard | 8 | 5 | 2 | 0.25 | 2 |
| Buffoon | 4 | 2 | 1 | 0.6 | 2 |
| Jumbo Buffoon | 6 | 4 | 1 | 0.6 | 1 |
| Mega Buffoon | 8 | 4 | 2 | 0.15 | 1 |
| Spectral | 4 | 2 | 1 | 0.3 | 2 |
| Jumbo Spectral | 6 | 4 | 1 | 0.3 | 1 |
| Mega Spectral | 8 | 4 | 2 | 0.07 | 1 |

Total weight 22.42: Arcana family 6.5 (29.0%), Celestial 6.5 (29.0%), Standard 6.5 (29.0%), Buffoon 1.95 (8.7%), Spectral 0.97 (4.3%). Roll: `pseudorandom('shop_pack'..ante) * total` (`get_pack`, common_events.lua 1944).
**The first pack slot of the first shop of the run is always a normal Buffoon Pack** (`first_shop_buffoon`). The art variant uses unseeded `math.random`, but both variants are identical.

What happens to picks:
- **Arcana** (Tarot; with Omen Globe each card has 20% to be a Spectral): opening deals a hand of cards from your deck (see 7.4). A picked Tarot is **used immediately** (`use_card` -> `use_consumeable`), targeting the cards you highlighted in that hand. It does not go to your consumable slots.
- **Spectral**: same as Arcana: deals a hand, picked card is used immediately.
- **Celestial**: no hand is dealt. A picked Planet is used immediately (levels up its hand). With Telescope, card 1 is the Planet of your most played hand.
- **Buffoon**: picked Joker goes to your joker row (needs a free slot, or the card must be Negative in the vanilla UI).
- **Standard**: picked playing card is added to your **deck** (`G.deck:emplace`). Each card: 40% Enhanced (`stdset` roll > 0.6) else plain; edition `poll_edition(key, 2, no negative)`: Polychrome 1.2%, Holo 2.8%, Foil 4%; 20% chance of a seal (vanilla: roll > 0.8), seal type 25% each Red/Blue/Gold/Purple. (Steamodded draws the seal with `SMODS.poll_seal({mod = 10})`; I did not verify its seed key.)
- The Soul (Tarot and Spectral packs) and Black Hole (Celestial and Spectral packs) each have a 0.3% chance per card slot (`pseudorandom('soul_'..type..ante) > 0.997`), and each can appear only if not already in `used_jokers` (unless Showman).
- Mega packs: after the first pick `pack_choices` goes from 2 to 1 and the pack stays open. Skipping ends the pack immediately.
- Using a consumable from your own consumable row while a pack is open does not use up a pick (vanilla UI; the API cannot do this, see 8).
- Jokers in Buffoon packs: rarity seed `'rarity'..ante..'buf'`, edition seed `'edibuf'..ante`, same rates as the shop.

### 5.5 Random number streams

`pseudoseed(key)` (misc_functions.lua 298) keeps **one independent stream per key string**, seeded from the run seed, advancing by one step each call. Most keys include the ante number, so each ante has fresh streams that are shared by all shops and rerolls of that ante. Calls to one key never affect another key.

| What | Key |
|---|---|
| Shop card type | `'cdt'..ante` |
| Shop joker rarity | `'rarity'..ante..'sho'` |
| Shop joker choice | `'Joker'..rarity..'sho'..ante` (rarity 1/2/3); resample when an unavailable entry is hit: same key + `'_resample'..n` |
| Shop joker edition | `'edisho'..ante` |
| Shop tarot / planet / spectral | `'Tarotsho'..ante`, `'Planetsho'..ante`, `'Spectralsho'..ante` |
| Illusion (playing cards) | `'illusion'` |
| Shop packs | `'shop_pack'..ante` |
| Arcana contents | `'Tarotar1'..ante`, Omen Globe check `'omen_globe'`, Spectral variant `'Spectralar2'..ante` |
| Celestial contents | `'Planetpl1'..ante` |
| Spectral pack contents | `'Spectralspe'..ante` |
| Buffoon contents | `'rarity'..ante..'buf'`, `'Joker'..rarity..'buf'..ante`, `'edibuf'..ante` |
| Standard contents | `'stdset'..ante`, front `'frontsta'..ante`, enhancement `'Enhancedsta'..ante`, edition `'standard_edition'..ante`, seal (vanilla) `'stdseal'..ante` and `'stdsealtype'..ante` |
| Soul / Black Hole | `'soul_Tarot'..ante`, `'soul_Planet'..ante`, `'soul_Spectral'..ante` |
| Voucher | `'Voucher'..ante` (from Voucher Tag: `'Voucher_fromtag'`, no ante) |
| Skip tags | `'Tag'..ante` |
| Boss | `'boss'` (no ante: one stream for the whole run) |
| Deck shuffle at blind start | `'nr'..ante` |
| Deck shuffle at cash out | `'cashout'..ante` |
| Glass, Lucky | `'glass'`, `'lucky_mult'`, `'lucky_money'` |

Practical consequence: the n-th shop card generated in an ante depends on how many cards were generated before it in that ante (initial stock of earlier shops plus every reroll). Skipping a blind removes that shop, so later shops in the ante show what the skipped shop would have shown. Pools depend on what you own (resampling), so owning or selling a card can change which card a given roll lands on.

---

## 6. Blind flow

### 6.1 Order

Each ante: Small Blind, Big Blind, Boss Blind. At blind select the blind "on deck" can be **selected** or (Small and Big only) **skipped**. Blinds cannot be taken out of order.

### 6.2 Skipping (`G.FUNCS.skip_blind`, button_callbacks.lua 2740)

- You gain that blind's tag immediately (`add_tag`), `G.GAME.skips` +1, the blind is marked "Skipped" and the next blind becomes "Select".
- You do not play the round: no reward, no hand money, no interest, **and no shop** (the state stays at blind select). Jokers get `context.skip_blind` (Throwback).
- Tags with type `immediate` fire right away (Skip, Economy, Handy, Garbage, Top-up, Orbital). Tags with type `new_blind_choice` fire right away too (Charm, Buffoon, Meteor, Ethereal, Standard open a free pack on the spot; Boss Tag rerolls the boss). Other tags wait for their trigger (Investment at the next Boss evaluation, Coupon/D6/Voucher at the next shop, Juggle at the next round start, Uncommon/Rare/edition tags at the next shop card creation).
- The Boss cannot be skipped: there is no tag button for it, and the API refuses (section 8).
- Round counter `G.GAME.round` increases only when a blind is selected (`ease_round(1)` in `select_blind`), not on skip.

### 6.3 How the boss is chosen (`get_new_boss`, common_events.lua 2338)

- Eligible: ordinary bosses whose `boss.min <= ante`, but only on antes that are **not** multiples of 8; finisher bosses (Cerulean Bell, Verdant Leaf, Violet Vessel, Amber Acorn, Crimson Heart) only on antes 8, 16, 24, ... (`ante % win_ante == 0`).
- Among eligible bosses, only those used the fewest times so far this run (`G.GAME.bosses_used`) stay in the draw. Then one is picked with the `'boss'` stream.
- Minimum antes: ante 1+ The Hook, The Club, The Manacle, The Psychic, The Goad, The Head, The Window, The Pillar; ante 2+ The Mouth, The Fish, The Wall, The House, The Mark, The Wheel, The Arm, The Water, The Needle, The Flint; ante 3+ The Tooth, The Eye; ante 4+ The Plant; ante 5+ The Serpent; ante 6+ The Ox. (`boss.max` is never read.)
- When chosen: ante 1 at run start; every later ante at the cash out after beating the Boss (`reset_blinds`, after the ante number has already gone up). Boss rerolls (Director's Cut once per ante, Retcon unlimited, $10 each; Boss Tag free) call `get_new_boss` again and also count as a use.
- The Small and Big tags for the new ante are chosen at that same cash out (Small first, then Big).

### 6.4 Losing, winning and Endless

- A round ends after a hand when `G.GAME.chips >= blind.chips` or `hands_left < 1` (`Game:update_hand_played`, game.lua 3196). It also ends if the hand and deck are both empty.
- At round end, if chips < requirement, it is game over, unless a joker returns `saved` (Mr. Bones).
- Beating the Boss of **ante 8** (the only ante equal to `win_ante`) wins the run: `win_game()` pauses the game behind the win screen. Clicking "Endless Mode" continues to ante 9 with the formula in section 3. The BalatroBot code deliberately does **not** dismiss this screen; the operator clicks Endless manually (balatrobot.lua comment). The API reports `paused: true` meanwhile.
- In Endless, finisher bosses return on antes 16, 24, 32. Losing later still ends the run normally.

---

## 7. Cards, deck, draw and hand order

### 7.1 Deck and piles

- Deck (`G.deck`), hand (`G.hand`, limit 8), play area (limit 5), discard pile.
- Played cards go to the discard pile after scoring (destroyed ones are removed). Discarded cards go to the discard pile. Neither returns to the deck during the round.
- After each play or discard, the hand is refilled from the deck up to the hand size (`draw_from_deck_to_hand`: draws `min(#deck, hand_limit - #hand)`). The Serpent changes this to 3 cards after the first play or discard.
- At round end: all hand cards go to discard, then the whole discard pile goes back to the deck.
- Discards: up to 5 cards per discard, needs `discards_left > 0`. Plays: 1 to 5 cards.

### 7.2 Shuffles and which card is drawn next

- The deck is shuffled at run start (`'shuffle'`), at every blind start (`new_round`: `G.deck:shuffle('nr'..ante)`), and at every cash out (`'cashout'..ante`).
- `pseudoshuffle` (misc_functions.lua 206) first **sorts the cards by `sort_id`**, then does a seeded Fisher-Yates shuffle. So the round's deck order depends only on which cards are in the deck and on the stream position, never on the previous order.
- Drawing takes the **last** card of `G.deck.cards` (`CardArea:remove_card` on a deck takes `_cards[#_cards]`, cardarea.lua 75-79). Cards put into the deck are inserted at position 1 (bottom).
- The API's `cards` area lists `G.deck.cards` in order with rank and suit visible. **During a round, the next card to be drawn is the last entry of `cards`.** The listing seen at blind select is not the round order, because the deck is reshuffled when the blind starts.

### 7.3 Hand sorting and manual order

- Every card drawn into the hand calls `G.hand:sort()` (`draw_card(..., sort = true)`, common_events.lua 418-420). The hand's sort mode starts as `'desc'` (cardarea.lua 23): by `get_nominal()` descending, which is rank first (A > K > Q > J > 10 > ... > 2, using nominal plus face offsets), ties broken by suit Spades > Hearts > Clubs > Diamonds. Stone Cards sort to the far right (their suit term is multiplied by -1000). The vanilla "Sort by suit" button switches the mode to `'suit desc'`; the API has no endpoint for it.
- So **any manual reordering is undone by the next draw** (after every play or discard, and when an Arcana/Spectral pack deals its hand). Reorder right before the action that needs it.
- Position matters:
  - **Scoring order** is left to right by x position (scoring hand sorted by `T.x`). The order in which you list card indices in a play request does not matter.
  - **Death** converts the **left** card into a copy of the **rightmost** highlighted card (card.lua 1111-1119: `rightmost` by `T.x`, others become `copy_card(rightmost, ...)`). To copy card X onto card Y, X must be to the right of Y.
- Hand array order equals screen order: `CardArea:align_cards` assigns x positions from array index and then sorts the array by x (cardarea.lua 451-466).

### 7.4 The hand dealt while a pack is open

- Arcana and Spectral packs call `draw_from_deck_to_hand`, so you get `min(#deck, hand_size)` cards **from your own deck**. In the shop the deck holds every card you own (all cards returned at round end), in the order produced by the cash-out shuffle; the dealt cards are the last entries of `cards`.
- Tarots used from the pack affect these real cards permanently.
- When the pack closes, `draw_from_hand_to_deck` returns the hand to the deck. This does not change the next round's order, because the next blind reshuffles (sorted by `sort_id` first).
- Celestial, Standard and Buffoon packs deal no hand.

---

## 8. The bot API (BalatroBot 1.5.1), as implemented

### 8.1 Transport and general behaviour

- JSON-RPC 2.0 over HTTP POST to `/` on `127.0.0.1:12346` (env `BALATROBOT_HOST`, `BALATROBOT_PORT`). One client at a time; the connection closes after each response.
- Validation tiers (core/dispatcher.lua): method exists; schema types (`integer`, `array` with item type, `string`, `boolean`; no range checks); **game state must be one of the endpoint's `requires_state`**; then the endpoint runs.
- Errors: `BAD_REQUEST` (-32001), `INVALID_STATE` (-32002), `NOT_ALLOWED` (-32003), `INTERNAL_ERROR` (-32000).
- Most action endpoints answer only when a completion condition becomes true. A watchdog answers after 60 s with "Request timed out in game, but the action may still have completed. Call gamestate and check before retrying." Always re-read `gamestate` after a timeout before retrying.
- Bench mode (`BALATROBOT_BENCH=1`): `set`, `add`, `load` are refused.
- All indices are **0-based**.

### 8.2 Endpoints

| Endpoint | Params | Legal states | What it does |
|---|---|---|---|
| `health` | none | any | Returns `{status: "ok"}`. |
| `rpc.discover` | none | any | Returns the OpenRPC spec. |
| `gamestate` | none | any | Returns the state object (8.3). |
| `menu` | none | any | Goes to the main menu (`G.FUNCS.go_to_menu`). Leaves the current run. |
| `start` | `deck` (enum, e.g. `"RED"`), `stake` (enum, e.g. `"WHITE"`), `seed` (optional string) | `MENU` | Sets the deck and calls `start_run({stake, seed})`. Answers once the Small blind panel exists. |
| `select` | none | `BLIND_SELECT` | Clicks select on the blind on deck. Answers in `SELECTING_HAND`. |
| `skip` | none | `BLIND_SELECT` | Refuses the Boss (`NOT_ALLOWED`, "Cannot skip Boss blind"). Otherwise calls `skip_blind` on the tag button. Answers when that blind's status is `SKIPPED` and the state is `BLIND_SELECT` or `SMODS_BOOSTER_OPENED` (a tag can open a pack immediately). |
| `play` | `cards`: int array | `SELECTING_HAND` | Checks: not empty, length <= 5, each index exists. Unhighlights the hand (a forced Cerulean Bell card stays), clicks each listed card, then presses Play. Answers after the hand resolves: back in `SELECTING_HAND`, or at `ROUND_EVAL` once the evaluation rows are built (or at once if the run was won), or at `GAME_OVER`. |
| `discard` | `cards`: int array | `SELECTING_HAND` | Same checks plus `discards_left > 0`. Answers back in `SELECTING_HAND`. |
| `cash_out` | none | `ROUND_EVAL` | Waits for the evaluation screen to finish, clicks Cash Out. Answers in `SHOP` once shop items exist. |
| `buy` | exactly one of `card`, `voucher`, `pack` (int) | `SHOP` | Checks index, money (`cost <= dollars - bankrupt_at`), free joker slot for jokers, free consumable slot for tarot/planet/spectral. Cards use `buy_from_shop`; vouchers and packs use `use_card` (redeem / open). For a pack, answers in `SMODS_BOOSTER_OPENED` once the pack cards exist (and, for Arcana/Spectral, once the hand is dealt). |
| `reroll` | none | `SHOP` | Checks money (unless reroll cost is 0), calls `reroll_shop`. |
| `next_round` | none | `SHOP` | Leaves the shop (`toggle_shop`). Answers in `BLIND_SELECT`. |
| `pack` | `card` (int) or `skip: true`; optional `targets` (int array; alias `cards`) | `SMODS_BOOSTER_OPENED` | See 8.4. |
| `use` | `consumable` (int), optional `cards` (int array) | `SELECTING_HAND`, `SHOP` | See 8.5. |
| `sell` | exactly one of `joker`, `consumable` (int) | `SELECTING_HAND`, `SHOP`, `SMODS_BOOSTER_OPENED` | Calls `G.FUNCS.sell_card`. Answers when money rose by exactly the card's `sell_cost` and the card is gone. |
| `rearrange` | exactly one of `hand`, `jokers`, `consumables`: a full permutation (int array) | `SELECTING_HAND`, `SHOP`, `SMODS_BOOSTER_OPENED` (hand: only `SELECTING_HAND` or `SMODS_BOOSTER_OPENED` with cards in hand) | Replaces the area's card array with the new order. |
| `save` | `path` | most in-run states | Writes the run save to a file. |
| `screenshot` | `path` (string) | any | Writes a screenshot file. |
| `set`, `add`, `load` | | | Refused in bench mode. |

### 8.3 What `gamestate` reports (utils/gamestate.lua)

- `state` (name of `G.STATE`), `paused`, `round_num`, `ante_num`, `money`, `won`, `deck`, `stake`, `seed`, `used_vouchers` (keys), `hands` (per hand: order, level, chips, mult, played, played_this_round, example), `round` (hands_left, hands_played, discards_left, discards_used, reroll_cost, `chips` = current round score `G.GAME.chips`), `blinds` (small/big/boss: type, status SELECT/CURRENT/UPCOMING/DEFEATED/SKIPPED, name, effect text, `score` requirement, tag_name, tag_effect).
- Areas: `jokers`, `consumables`, `cards` (the deck, in draw order with the next draw last), `hand` (left to right), `shop`, `vouchers`, `packs`, `pack` (the open pack). Each area: `count`, `limit`, `cards`, and for the hand `highlighted_limit`.
- Each card: `id` (`sort_id`, stable per card), `key`, `set` (JOKER, TAROT, PLANET, SPECTRAL, VOUCHER, BOOSTER, ENHANCED, DEFAULT), `label`, `value` (`suit`, `rank`, `effect` = description text including current numbers), `modifier` (seal, edition, enhancement, eternal, perishable, rental), `state` (debuff, hidden, highlight), `cost` (`buy`, `sell`).
- Rank and suit are read from `config.card` with no facing check, so **face-down cards (The House, The Wheel, The Mark, The Fish) still report their rank and suit**, with `state.hidden = true`.
- `count` comes from `config.card_count`, which is updated once per frame, so it can lag the `cards` list by a frame.

### 8.4 `pack` in detail

- Exactly one of `card` or `skip` must be given.
- `skip: true` calls `G.FUNCS.skip_booster` directly (no `can_skip_booster` check). Answers when the pack is closed and the state is `SHOP` or `BLIND_SELECT` (packs opened by tags return to blind select).
- `card`: for Arcana and Spectral packs it first waits until the hand is dealt (enough cards for the target indices), then:
  - Joker pick: refused if `joker_count >= joker_limit`, **even for a Negative joker** (the vanilla UI would allow a Negative one).
  - Target rules: Aura needs exactly 1 target (special-cased); Ankh needs at least 1 joker; any card whose config has `max_highlighted` needs between `min_highlighted` (default 1) and `max_highlighted` targets. The targets (indices into the current `hand` array) are highlighted, then `G.FUNCS.use_card` is called on the pack card.
  - The API does **not** call the game's `can_use_consumeable` for pack picks. Cards whose vanilla UI would be greyed out (for example Judgement, The Soul or Wraith with full joker slots; The Fool with no previous tarot/planet; Wheel of Fortune or Hex with no eligible joker) are executed anyway. By vanilla code, Judgement and The Soul then create and add a joker even beyond the slot limit (card.lua 1415-1420). Untested; treat this as outside normal rules.
  - Mega packs: if `pack_choices` was 2 and becomes 1, answers with the pack still open; otherwise answers when the pack has closed and the state is `SHOP` or `BLIND_SELECT`.
- **Rearranging the hand while a pack is open is allowed** (`rearrange` with `hand` in `SMODS_BOOSTER_OPENED`, if the pack dealt a hand). This matters for Death targets.
- **Selling while a pack is open is allowed** (`sell` lists `SMODS_BOOSTER_OPENED`).
- **Using a consumable from your own slots while a pack is open is not possible**: `use` only accepts `SELECTING_HAND` and `SHOP`.

### 8.5 `use` in detail

- `consumable` indexes your consumable row.
- "Requires cards" means the card's config has `max_highlighted`. Those can only be used in `SELECTING_HAND`; `cards` must be given, each index must exist, and the count must be within `min_highlighted` (default 1) to `max_highlighted` (exact if equal; Death needs exactly 2). The API clears the hand's highlights and highlights the listed cards in the given order. Which card is "left" or "right" for Death is decided by **position in hand**, not by list order.
- Cards without `max_highlighted` are used with no targets. Then the game's own `can_use_consumeable()` must pass and `check_use()` must not report a full joker row (Ankh), otherwise `NOT_ALLOWED`.
- **Aura from your consumable row cannot be targeted through `use`.** Its config is empty (game.lua 575), so the API does not highlight the `cards` you send, and `can_use_consumeable` requires exactly one highlighted card, so the request will normally be refused. (Aura inside a Spectral pack works, because `pack` special-cases it.)
- Familiar, Grim, Incantation, Immolate, Sigil, Ouija: no `max_highlighted`, so they work in `SELECTING_HAND` (need more than 1 card in hand) and are refused in `SHOP`.
- Planets, The Hermit, Temperance, Black Hole, Judgement, The Soul, Wraith, The Emperor, The High Priestess, The Fool, Wheel of Fortune, Ankh, Ectoplasm, Hex: usable in `SHOP` and in `SELECTING_HAND` when their own conditions hold.

### 8.6 Other quirks found in the code

- `play` / `discard` do not check for duplicate indices. Listing the same index twice clicks the card twice, which unselects it. If that leaves nothing selected, `play` would run with an empty hand (the hand name would be `NULL`, which by vanilla code is not a valid key; likely a crash). Never repeat an index.
- With Cerulean Bell the forced card is always included. The highlight limit is 5, so at most 4 other cards can be added; extra listed cards are silently not selected (the ones listed last lose).
- `buy` refuses a Negative joker or consumable when slots are full (vanilla allows it).
- `sell` does not check eternal stickers (not relevant at White Stake). Its completion check needs money to rise by exactly `sell_cost`; if something else changes money in the same moment, the request may hang until the 60 s watchdog.
- `buy` of an Arcana or Spectral pack waits until the hand holds exactly `hand_limit` cards. If your deck has fewer cards than your hand size, that never happens and the request ends with the 60 s watchdog timeout (the pack is still open; check `gamestate`).
- `rearrange` writes `order` into the shared card/center tables. No gameplay effect found for vanilla content.
- After a run is won, `play` answers with `won: true` while the win screen pauses the game; actions stall until the operator clicks Endless (`paused` becomes false).

### 8.7 What the game can do that the API cannot

- Reroll the Boss (Director's Cut, Retcon). There is no endpoint for `reroll_boss`.
- "Buy and use" a consumable straight from the shop (the API always buys into a slot, which needs a free slot).
- Use a consumable from your slots during `BLIND_SELECT`, `ROUND_EVAL`, or while a pack is open.
- Sell during `BLIND_SELECT` or `ROUND_EVAL` (vanilla allows selling there; the API does not list those states).
- Take a Negative joker or consumable when slots are full (shop or pack).
- Use Aura from the consumable row.
- Switch the hand's auto-sort to suit order.
- Dismiss the win screen / choose Endless (operator only).

---

## 9. Ambiguities and assumptions (stated, not guessed)

1. **Profile-dependent pools.** `get_current_pool` only adds jokers and vouchers whose `unlocked ~= false` (all tier-2 vouchers such as Overstock Plus, Liquidation, Glow Up, Reroll Glut, Money Tree, Observatory, and many jokers are defined `unlocked = false` until the profile unlocks them). Tags with `requires` need that item discovered in the profile (Rare Tag needs Blueprint discovered; Foil/Holo/Polychrome/Negative tags need that edition discovered). In a seeded run nothing is unlocked or discovered during the run. I could not read the benchmark machine's profile, so which of these items can appear is unknown from code alone.
2. **Steamodded.** I checked only the Steamodded areas listed in section 0. Other Steamodded patches (blinds, specific jokers, tags, consumables) were not audited and are assumed to keep vanilla behaviour.
3. **Interest timing** relies on event order: held Gold Card money is queued in `end_round` before the state switches to `ROUND_EVAL`, so it should be counted for interest. This is from reading the event queue order, not from a test.
4. **Standard pack seal seed under Steamodded**: `SMODS.poll_seal({mod = 10})`; the rate is presumably the vanilla 20%, but I did not verify its seed key or exact rate.
5. **API pack picks that skip `can_use_consumeable`** (8.4): the outcome for each such card was read from vanilla `use_consumeable`, not tested, and Steamodded may differ.
6. **NaN display text** (ante 39+ requirement, or a NaN score) is platform dependent (`nan` or `-nan`); the rule that it can never be beaten is not.


---

# Jokers, part A (game.lua lines 368 to 446: Joker through Obelisk, 75 jokers)

Source: vanilla Balatro 1.0.1o Lua. Numbers come from `config` in game.lua; behaviour comes from `Card:calculate_joker`, `Card:calculate_dollar_bonus`, `Card:add_to_deck` / `remove_from_deck`, `Card:update` (card.lua) and `G.FUNCS.evaluate_play` / `end_round` / `new_round` (functions/state_events.lua). "Base cost" is the `cost` field; the shop price adds edition surcharges and inflation and applies discounts (`Card:set_cost`). Line 447 is blank; Midas Mask (line 448) onward belongs to the next writer.

## How joker effects are evaluated (read this first)

These are facts from `evaluate_play` and `calculate_joker` that the per-joker entries rely on.

1. **Order of one played hand.** Inside `evaluate_play`, in this order:
   1. The hand type is found. `G.GAME.hands[hand].played` and `.played_this_round` are increased by 1 **before anything else**, so jokers that read these counts include the current hand.
   2. If the boss blind debuffs the whole hand (`debuff_hand`), steps 3 to 7 are skipped. Only the `debuffed_hand` context runs. None of the jokers in this file react to it.
   3. **"Before" phase**: every joker, left to right, gets `context.before`. Scaling jokers update here (Ride the Bus, Green Joker, Runner, Square Joker, Obelisk, Vampire), and To Do List, DNA and Space Joker act here. After this loop, base chips and mult are re-read from the hand level, so a Space Joker level-up counts for this same hand.
   4. **Scored cards**, left to right. A debuffed scoring card is skipped completely: no chips and no joker per-card effects. For each non-debuffed card, one pass is: the card's own chips, mult, dollars, then Glass xmult, then the card's edition; after that, every joker left to right gets `context.individual` with `cardarea = G.play`.
   5. **Cards held in hand**, left to right: the card's own held effect (Steel x1.5 etc.), then every joker's `context.individual` with `cardarea = G.hand` (Raised Fist, Baron).
   6. **Joker phase** (`joker_main`), jokers left to right, and then consumables (only for the Observatory voucher). For each joker, in this order: its Foil or Holographic edition bonus; its main effect; any "joker on joker" effects aimed at it (Baseball Card); its Polychrome x1.5 last. So a Polychrome joker multiplies after its own +mult, and a Holographic joker's +10 Mult comes before its own effect.
   7. The deck's final scoring step (Plasma Deck), then card destruction (`destroying_card`, used by Sixth Sense; Glass shatter rolls).
   8. **"After" phase** (`context.after`): this runs **even when the hand was debuffed** (Ice Cream decays here).
   9. Only after `evaluate_play` finishes are `G.GAME.hands_played` and `G.GAME.current_round.hands_played` increased. So during scoring of the first hand of a round, `current_round.hands_played == 0` (DNA, Sixth Sense). `current_round.hands_left` has **already** been reduced by 1 when the Play button was pressed, so it is 0 during the final hand (Dusk).

2. **Retriggers.** For each scored card, a list of repetitions is built: the Red Seal first (1 extra), then each joker left to right that answers `context.repetition` (Hack, Dusk, Sock and Buskin, Hanging Chad, Seltzer). Each repetition re-runs the **whole pass from step 4**: the card's own chips, mult and edition, **and every joker's per-card (`individual`) effect**, including random rolls (8 Ball, Business Card roll again). Joker-phase effects (step 6) are never retriggered by card retriggers. For held cards, the Red Seal and Mime add repetitions, but only if that card produced some effect on its first pass: its own held effect was non-empty, or at least one joker returned something for it.

3. **"Contains" checks use every sub-hand.** `evaluate_poker_hand` fills all hand types that are present, not only the scored one:
   - Pair is present in any Pair, Two Pair, Three of a Kind, Full House, Four or Five of a Kind.
   - Three of a Kind is present in Full House and in Four or Five of a Kind.
   - Two Pair is present in Two Pair and Full House only. It is **not** present in Four of a Kind, because pairs are found as exact groups of 2.
   - Straight and Flush are present in Straight Flush, and Flush is present in Flush House and Flush Five.
   - The "Straight Flush" entry is filled whenever both a straight and a flush exist among the played cards.

4. **Blueprint and Brainstorm.** The `blueprint_compat` flag in game.lua only sets the "compatible / incompatible" label. In the code, Blueprint and Brainstorm call the copied joker's `calculate_joker` with `context.blueprint` set, and each joker's own guards decide what is copied:
   - Scaling steps written with `not context.blueprint` are never copied. Only the payoff is copied.
   - `calculate_dollar_bonus` (cash-out money) is never copied, because Blueprint only hooks `calculate_joker`.
   - Passive rule changes (Four Fingers, Shortcut, Splash, Pareidolia, Credit Card, Chaos) are not copied.
   - For all 75 jokers here, the flag matches what the code does.

5. **Debuffed jokers** return nothing from `calculate_joker` and from `calculate_dollar_bonus`. When a joker becomes debuffed, `remove_from_deck(true)` runs, so its passive effects (Credit Card debt limit, Chaos free reroll) switch off until the debuff ends.

6. **Probabilities** are written below as base odds "1 in N". The code compares a random number against `G.GAME.probabilities.normal / N`. `probabilities.normal` starts at 1, and each Oops! All 6s doubles it.

7. **Money timing.** `ease_dollars` queues its change as an event. A joker that reads `G.GAME.dollars` directly while a hand is scoring does not see money earned earlier in that same hand (Vagabond). Jokers that add `G.GAME.dollar_buffer` (Bull, Bootstraps) do see it. Business Card and To Do List add their payouts to `dollar_buffer`.

8. **Face cards and suits on debuffed cards.** `Card:is_face()` returns false for a debuffed card; Pareidolia only applies to non-debuffed cards. `Card:is_suit()` normally returns false for a debuffed card, but with `flush_calc = true` (used by flushes and Blackboard) it ignores the debuff and uses the base suit. Stone Cards have no suit, and `get_id()` gives them a random negative rank, so no rank check ever matches a Stone Card.

---

### Joker  (rarity Common, base cost $2, Blueprint/Brainstorm compatible: yes)
- Effect: +4 Mult.
- When it acts: joker phase, +mult (`mult_mod`), every non-debuffed hand.
- Interactions: no conditions and no state. Not retriggered by card retriggers.

### Greedy Joker  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of Diamonds suit gives +3 Mult.
- When it acts: per scored card, during card scoring, +mult.
- Interactions: uses `is_suit('Diamonds')`, so Wild Cards count, Stone Cards never count, and Smeared Joker makes Hearts count too. Retriggers of a card (Red Seal, Hack, Dusk, Sock and Buskin, Hanging Chad, Seltzer) give the +3 again. Only scoring cards count; with Splash every played card scores.

### Lusty Joker  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of Hearts suit gives +3 Mult.
- When it acts: per scored card, during card scoring, +mult.
- Interactions: same rules as Greedy Joker (Wild counts, Stone never, Smeared Joker merges Hearts and Diamonds, retriggers repeat it).

### Wrathful Joker  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of Spades suit gives +3 Mult.
- When it acts: per scored card, during card scoring, +mult.
- Interactions: same rules as Greedy Joker (Smeared Joker merges Spades and Clubs).

### Gluttonous Joker  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of Clubs suit gives +3 Mult. (Internal key `j_gluttenous_joker`.)
- When it acts: per scored card, during card scoring, +mult.
- Interactions: same rules as Greedy Joker.

### Jolly Joker  (rarity Common, base cost $3, Blueprint/Brainstorm compatible: yes)
- Effect: +8 Mult if the played hand contains a Pair.
- When it acts: joker phase, +mult.
- Interactions: "contains" means a Pair exists anywhere among the played cards, so it also triggers on Two Pair, Three of a Kind, Full House, Four of a Kind and Five of a Kind (see note 3). It checks all played cards, not only scoring ones.

### Zany Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +12 Mult if the played hand contains a Three of a Kind.
- When it acts: joker phase, +mult.
- Interactions: also triggers on Full House, Four of a Kind and Five of a Kind (and on Flush House and Flush Five).

### Mad Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +10 Mult if the played hand contains a Two Pair.
- When it acts: joker phase, +mult.
- Interactions: Two Pair is present in Two Pair and Full House (and Flush House). It is NOT present in Four of a Kind (note 3).

### Crazy Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +12 Mult if the played hand contains a Straight.
- When it acts: joker phase, +mult.
- Interactions: also triggers on Straight Flush. Four Fingers (4-card straights) and Shortcut (one-rank gaps) widen what counts as a straight.

### Droll Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +10 Mult if the played hand contains a Flush.
- When it acts: joker phase, +mult.
- Interactions: also triggers on Straight Flush, Flush House and Flush Five. Four Fingers allows 4-card flushes.

### Sly Joker  (rarity Common, base cost $3, Blueprint/Brainstorm compatible: yes)
- Effect: +50 Chips if the played hand contains a Pair.
- When it acts: joker phase, +chips (`chip_mod`).
- Interactions: same "contains" rule as Jolly Joker.

### Wily Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +100 Chips if the played hand contains a Three of a Kind.
- When it acts: joker phase, +chips.
- Interactions: same "contains" rule as Zany Joker.

### Clever Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +80 Chips if the played hand contains a Two Pair.
- When it acts: joker phase, +chips.
- Interactions: same rule as Mad Joker. Not on Four of a Kind.

### Devious Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +100 Chips if the played hand contains a Straight.
- When it acts: joker phase, +chips.
- Interactions: same rule as Crazy Joker.

### Crafty Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +80 Chips if the played hand contains a Flush.
- When it acts: joker phase, +chips.
- Interactions: same rule as Droll Joker.

### Half Joker  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: +20 Mult if the played hand has 3 or fewer cards.
- When it acts: joker phase, +mult.
- Interactions: counts all played cards (`#context.full_hand`), not just the scoring ones.

### Joker Stencil  (rarity Uncommon, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: X1 Mult for each empty Joker slot, with each Joker Stencil counting as an empty slot.
- When it acts: joker phase, Xmult.
- Interactions: `Card:update` recomputes the value every frame as (joker slot limit minus number of cards in the joker area) plus (number of Joker Stencils owned, itself included). Example: 5 slots, Stencil plus 2 other jokers gives 5 - 3 + 1 = X3. A Negative edition raises the slot limit by 1. The Xmult is applied only when it is greater than 1. Blueprint or Brainstorm copying Stencil applies the same Xmult.

### Four Fingers  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: no)
- Effect: all Flushes and Straights can be made with 4 cards.
- When it acts: passive, during hand-type detection (`get_flush`, `get_straight`).
- Interactions: when any non-debuffed Four Fingers is owned, the minimum is 4 matching cards instead of 5. The played hand must still have 4 or 5 cards. A 5-card hand with 4 suited cards is a Flush; the fifth card is not part of the flush and only scores if another rule includes it (for example Splash, or being part of a pair). It also enables 4-card Straight Flushes, where the straight and the flush need not be the same 4 cards. Not copyable.

### Mime  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: retrigger every card held in hand once (`extra = 1`).
- When it acts: during the held-in-hand step of scoring, and again during the end-of-round held-card step.
- Interactions:
  - A held card is retriggered only if its first pass produced something: either its own held effect (Steel Card X1.5) or a joker effect aimed at it (Baron, Raised Fist, Shoot the Moon, Reserved Parking).
  - At end of round, it also retriggers Gold Card $3 and Blue Seal planet creation.
  - Blueprint and Brainstorm copies add one more retrigger each, and these stack with Red Seals on held cards.
  - For a debuffed held card, jokers such as Baron return a "Debuffed" message. That message counts as an effect, so Mime repeats the message but adds nothing.

### Credit Card  (rarity Common, base cost $1, Blueprint/Brainstorm compatible: no)
- Effect: you may spend down to -$20.
- When it acts: passive. On acquiring, `G.GAME.bankrupt_at` is lowered by 20; it is raised back when the card is sold, destroyed or debuffed.
- Interactions: purchase and reroll checks use `dollars - bankrupt_at`. Being in debt gives no interest (interest needs $5 or more).

### Ceremonial Dagger  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: when a blind is selected, destroy the joker immediately to its right and permanently add twice that joker's sell value to this joker's Mult. Starts at +0 Mult.
- When it acts: on blind selected (every blind: Small, Big and Boss) for the destruction and gain; joker phase for the +mult. It returns its mult only when the mult is above 0.
- Interactions:
  - Does nothing if there is no joker to its right, or if that joker is Eternal or is already being destroyed.
  - The sell value read includes any added sell value (Egg, Gift Card).
  - The gain is not copied (`not context.blueprint`), but Blueprint and Brainstorm do copy the +mult.
  - Cannot be Perishable (`perishable_compat = false`).
  - Jokers act left to right on blind select, so a Dagger further left resolves first.

### Banner  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: +30 Chips for each remaining discard.
- When it acts: joker phase, +chips. The bonus is 30 x `current_round.discards_left` at the moment of scoring, and it only applies when discards_left is above 0.
- Interactions: Burglar sets discards to 0, which turns Banner off.

### Mystic Summit  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: +15 Mult when 0 discards remain.
- When it acts: joker phase, +mult, when `discards_left == 0`.
- Interactions: works with Burglar (which removes all discards).

### Marble Joker  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: when a blind is selected, add 1 Stone Card (with a random rank and suit underneath) to the deck.
- When it acts: on blind selected, every blind.
- Interactions:
  - The card goes into the draw pile, and the deck size limit grows by 1.
  - It counts as "playing card added", so Hologram gains from it.
  - Blueprint and Brainstorm copies each add another Stone Card.
  - The `extra = 1` value is not used by the code; it always adds exactly one card.

### Loyalty Card  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: X4 Mult every 6 hands played. The card text shows `every + 1` = 6.
- When it acts: joker phase, Xmult.
- Interactions:
  - The counter is `remaining = (4 - (G.GAME.hands_played - hands_played_at_create)) mod 6`, and it pays when remaining equals 5. `hands_played_at_create` is set when the card is created, and the run-wide `G.GAME.hands_played` is only increased after scoring.
  - Result: it pays on the 6th, 12th, 18th... hand played after the card was created. Hands count across rounds.
  - If that hand is debuffed by the boss, the joker phase does not run and the payout is lost. The cycle continues anyway.
  - Blueprint and Brainstorm copies pay on the same hands.

### 8 Ball  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: each scored 8 has a 1 in 4 chance to create a Tarot card. You must have room.
- When it acts: per scored card, during card scoring.
- Interactions:
  - Room is checked first (`#consumables + buffer < limit`), then the roll.
  - Each retrigger of an 8 is another roll.
  - Oops! All 6s doubles the odds (2 in 4).
  - Blueprint and Brainstorm copies roll separately.
  - Stone Cards never count as 8.

### Misprint  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +0 to +23 Mult, chosen at random each hand. It is a whole number, every value from 0 to 23 is equally likely (`math.random(0, 23)`), and both ends are included.
- When it acts: joker phase, +mult.
- Interactions: Oops! All 6s does not affect it. Blueprint and Brainstorm copies roll their own values.

### Dusk  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: retrigger every played scoring card once, but only in the final hand of the round.
- When it acts: during card scoring (`context.repetition`), when `current_round.hands_left == 0`. The count was already lowered when Play was pressed, so this is the last hand you have.
- Interactions: stacks with the Red Seal and other retrigger jokers. Each copy (Blueprint, Brainstorm) adds another retrigger. Debuffed scoring cards are skipped entirely, so they are not retriggered.

### Raised Fist  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: adds twice the rank value of the lowest-ranked card held in hand to Mult.
- When it acts: held-in-hand step, +mult (`h_mult`), applied on that one held card.
- Interactions:
  - The lowest card is found by `base.id` among all held cards except Stone Cards. On ties, the rightmost of the tied cards is chosen.
  - The Mult added is 2 x `base.nominal`: 2 to 10 at face value, J, Q and K count as 10, and Ace counts as 11. Aces have the highest id, so an Ace is chosen only if every non-Stone held card is an Ace (+22).
  - If the chosen card is debuffed, it gives nothing. It does not fall back to another card.
  - If all held cards are Stone Cards, or the hand is empty, it gives nothing.
  - Mime and a Red Seal on the chosen card retrigger it.

### Chaos the Clown  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: no)
- Effect: 1 free reroll per shop.
- When it acts: passive. `new_round` sets `free_rerolls` to the number of non-debuffed Chaos the Clowns owned. Buying one adds +1 immediately, so it works in the shop where you buy it, and selling one removes 1.
- Interactions: free rerolls are used before paid ones and do not raise the reroll price while free. Several Chaos the Clowns stack.

### Fibonacci  (rarity Uncommon, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: each scored Ace, 2, 3, 5 or 8 gives +8 Mult.
- When it acts: per scored card, during card scoring, +mult.
- Interactions: retriggers repeat it. Stone Cards never match.

### Steel Joker  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: X0.2 Mult for each Steel Card in your full deck. Total: X(1 + 0.2 x count).
- When it acts: joker phase, Xmult. It is applied only when the count is above 0.
- Interactions:
  - Counts every playing card you own with the Steel enhancement, wherever it is (deck, hand, discard), debuffed or not. The count is recomputed every frame.
  - It only appears in shops or packs if your deck contains at least one Steel Card (`enhancement_gate = 'm_steel'`).

### Scary Face  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: each scored face card gives +30 Chips.
- When it acts: per scored card, during card scoring, +chips.
- Interactions: uses `is_face()`. With Pareidolia, every non-debuffed card is a face card. Retriggers (including Sock and Buskin) repeat it.

### Abstract Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +3 Mult for each Joker card you have.
- When it acts: joker phase, +mult.
- Interactions: counts every card in the joker area whose set is Joker, including itself and including debuffed jokers. With only Abstract Joker, it gives +3.

### Delayed Gratification  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: no)
- Effect: earn $2 per remaining discard if no discards were used this round.
- When it acts: end of round, cash-out money (`calculate_dollar_bonus`).
- Interactions:
  - Pays 2 x `discards_left` only if `discards_used == 0` and `discards_left > 0`. With Burglar (0 discards) it pays nothing.
  - The Hook's forced discards do not increase `discards_used`.
  - Blueprint and Brainstorm cannot copy cash-out money.

### Hack  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: retrigger each scored 2, 3, 4 or 5 once.
- When it acts: during card scoring (`context.repetition`).
- Interactions: stacks with Red Seal and other retriggers. Each copy adds one more retrigger. Stone Cards never match. Debuffed cards are skipped.

### Pareidolia  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: no)
- Effect: all cards count as face cards.
- When it acts: passive, inside `Card:is_face()`.
- Interactions:
  - A debuffed card is still not a face card, because the debuff check comes first. A debuffed Pareidolia does nothing.
  - Every card now resets Ride the Bus, triggers Scary Face, Business Card and Sock and Buskin, and counts for Faceless Joker.

### Gros Michel  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: +15 Mult. At end of round, a 1 in 6 chance that this card is destroyed.
- When it acts: joker phase for +mult; the end-of-round roll happens after every round.
- Interactions:
  - When it is destroyed, the flag `gros_michel_extinct` is set for the run. After that Gros Michel can no longer appear, and Cavendish can.
  - Oops! All 6s doubles the destruction odds (2 in 6).
  - Blueprint and Brainstorm copy the +15 but do not roll.
  - Cannot be Eternal.

### Even Steven  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of even rank (10, 8, 6, 4, 2) gives +4 Mult.
- When it acts: per scored card, during card scoring, +mult.
- Interactions: the check is rank id between 0 and 10 and even, so face cards and Aces never count. Retriggers repeat it.

### Odd Todd  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of odd rank (Ace, 9, 7, 5, 3) gives +31 Chips.
- When it acts: per scored card, during card scoring, +chips.
- Interactions: Ace (id 14) is included by a special case. Retriggers repeat it.

### Scholar  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: each scored Ace gives +20 Chips and +4 Mult.
- When it acts: per scored card, during card scoring, +chips and +mult.
- Interactions: retriggers repeat it.

### Business Card  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: each scored face card has a 1 in 2 chance to give $2.
- When it acts: per scored card, during card scoring, money.
- Interactions: the $2 is written into the code, not taken from config (`extra = 2` is the odds). Each retrigger rolls again. Oops! All 6s makes it certain (2 in 2). The money is added to `dollar_buffer`. Copies roll separately.

### Supernova  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: adds to Mult the number of times this poker hand has been played this run.
- When it acts: joker phase, +mult equal to `G.GAME.hands[scoring hand].played`.
- Interactions: the count already includes the current hand, so the first ever Pair gives +1. It uses the scored hand type only (the top hand), not sub-hands.

### Ride the Bus  (rarity Common, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: gains +1 Mult for each hand in a row played without a scoring face card. Starts at +0.
- When it acts: before phase for the update; joker phase for the +mult (only when above 0).
- Interactions:
  - In the before phase, if any card in the scoring hand passes `is_face()`, the mult resets to 0. Otherwise it gains +1, and the gain already counts this hand.
  - Face cards that are played but not scoring do not reset it. Debuffed face cards do not reset it (`is_face` is false for them). With Pareidolia, any non-debuffed scoring card resets it.
  - A hand debuffed by the boss skips the before phase, so it neither gains nor resets.
  - The update is not copied; only the +mult is. Cannot be Perishable.

### Space Joker  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: 1 in 4 chance to upgrade the level of the played poker hand by 1.
- When it acts: before phase, before cards score. The new level counts for the current hand, because base chips and mult are re-read after the before phase.
- Interactions: Oops! All 6s gives 2 in 4. Blueprint and Brainstorm copies roll separately and can each level up. It does not run on hands debuffed by the boss.

### Egg  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: no)
- Effect: gains $3 of sell value at end of round.
- When it acts: end of round (every round).
- Interactions: increases `extra_value` by 3. The sell value is max(1, floor(cost/2)) + extra_value. The raised value also raises what Ceremonial Dagger gains from destroying it, and what Swashbuckler counts. Not copied.

### Burglar  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: when a blind is selected, gain +3 Hands and lose all discards.
- When it acts: on blind selected, every blind. Hands and discards change for this round only.
- Interactions: each Blueprint or Brainstorm copy adds another +3 hands. Zero discards turns on Mystic Summit and turns off Banner and Delayed Gratification.

### Blackboard  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult if every card held in hand is a Spade or a Club.
- When it acts: joker phase, Xmult.
- Interactions:
  - Uses `is_suit(..., flush_calc = true)`: debuffed cards count by their base suit, a non-debuffed Wild Card passes, a debuffed Wild Card counts by its base suit, and any held Stone Card fails the check.
  - Smeared Joker makes Spades and Clubs interchangeable, but Hearts and Diamonds still fail.
  - If no cards are held, the condition is true (0 of 0), so it gives X3.

### Runner  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: gains +15 Chips each time the played hand contains a Straight. Starts at 0.
- When it acts: before phase for the gain; joker phase for the +chips. The gain counts for this same hand.
- Interactions: Straight Flush counts. Four Fingers and Shortcut widen what counts. The gain is not copied, but the chips are. Cannot be Perishable.

### Ice Cream  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: +100 Chips, minus 5 Chips after every hand played.
- When it acts: joker phase for +chips; after phase for the decay.
- Interactions:
  - The decay runs after every hand, including hands debuffed by the boss.
  - When chips would reach 0 or less, it melts (is destroyed) instead. It gives 100, 95, ..., 5 Chips over 20 hands and melts after the 20th.
  - The decay is not copied. Cannot be Eternal.

### DNA  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: if the first hand of the round has exactly 1 card, add a permanent copy of that card to the deck and draw it to hand.
- When it acts: before phase, when `current_round.hands_played == 0` and exactly 1 card is played.
- Interactions:
  - The copy keeps the original card's enhancement, seal and edition (`copy_card`). It goes straight into the hand, and the deck size limit grows by 1.
  - It counts as "playing card added" (Hologram gains).
  - A Blueprint or Brainstorm copy makes another copy (there is no blueprint guard).
  - It does not act if that hand is debuffed by the boss, because the before phase is skipped.

### Splash  (rarity Common, base cost $3, Blueprint/Brainstorm compatible: no)
- Effect: every played card counts in scoring.
- When it acts: passive. When `evaluate_play` builds the scoring hand, it replaces it with all played cards if a non-debuffed Splash is owned.
- Interactions: debuffed played cards are still in the scoring hand but are skipped during scoring. Splash makes every played card eligible for per-card jokers and for retriggers.

### Blue Joker  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: +2 Chips for each card remaining in the deck.
- When it acts: joker phase, +chips = 2 x the number of cards left in the draw pile at scoring time. It only applies when that number is above 0.
- Interactions: cards in hand, played or discarded do not count.

### Sixth Sense  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: no)
- Effect: if the first hand of the round is a single 6, destroy that 6 and create a Spectral card. You must have room for the Spectral.
- When it acts: card destruction step after scoring. Conditions: exactly 1 card played, its rank id is 6, and `current_round.hands_played == 0`.
- Interactions:
  - The 6 scores normally first and is then destroyed.
  - The card is destroyed even when there is no room for a Spectral; only the Spectral needs room.
  - The rank check does not look at debuffs, so a debuffed 6 is still destroyed.
  - Not copyable (the branch is guarded).

### Constellation  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: gains X0.1 Mult every time a Planet card is used. Starts at X1.
- When it acts: on using a consumable whose set is Planet (the gain); joker phase for the Xmult (only when above X1).
- Interactions: the gain is not copied, but the Xmult is. Cannot be Perishable.

### Hiker  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: every scored card permanently gains +5 Chips.
- When it acts: per scored card, during card scoring. It adds 5 to the card's `perma_bonus`.
- Interactions:
  - The card's chips for the current pass were already counted before Hiker acts, so the +5 shows from the card's next pass. A retrigger in the same hand already includes it.
  - Each retrigger adds another +5.
  - A Blueprint or Brainstorm copy also adds +5 per trigger (no blueprint guard).

### Faceless Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: earn $5 if 3 or more face cards are discarded at the same time.
- When it acts: on discard, checked once per discard action (when the last discarded card is processed).
- Interactions:
  - It counts `is_face()` over all cards in the discard. Debuffed face cards do not count; with Pareidolia, any 3 non-debuffed cards count.
  - The Hook boss's forced discards also run this check.
  - Blueprint and Brainstorm copies also pay.

### Green Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +1 Mult per hand played, -1 Mult per discard. Starts at +0.
- When it acts: before phase for the +1, which counts for this same hand; on discard for the -1, once per discard action; joker phase for the +mult (only when above 0).
- Interactions:
  - The mult never goes below 0.
  - Hands debuffed by the boss skip the before phase, so they give no +1.
  - The Hook's forced discards also cost -1.
  - The scaling is not copied. Cannot be Perishable.

### Superposition  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: create a Tarot card if the poker hand contains an Ace and a Straight. You must have room.
- When it acts: joker phase.
- Interactions:
  - The Ace must be in the scoring hand (rank id 14). The debuff state is not checked, so a debuffed scoring Ace still counts.
  - The Straight check uses "contains", so Straight Flush counts.
  - Blueprint and Brainstorm copies create one more each, if there is room.

### To Do List  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: earn $4 if the scored poker hand is the listed hand. The listed hand changes at end of round.
- When it acts: before phase (money), comparing the scored hand type exactly, not sub-hands. End of round: the target is rerolled.
- Interactions:
  - The first target is a random visible hand chosen when the card is created. Each end-of-round reroll picks a random visible hand other than the current one. Secret hands are visible only after you have played them.
  - The money is added to `dollar_buffer`.
  - A copy pays again, but the reroll is not copied.
  - It does not pay on hands debuffed by the boss.

### Cavendish  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult. At end of round, a 1 in 1000 chance that this card is destroyed.
- When it acts: joker phase, Xmult; the roll happens at end of round.
- Interactions: it can only appear after Gros Michel has gone extinct this run (`yes_pool_flag`). Oops! All 6s doubles the odds. Copies give X3 without rolling. Cannot be Eternal.

### Card Sharp  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult if this poker hand type has already been played this round.
- When it acts: joker phase, Xmult, when `played_this_round > 1`. The count includes the current hand, so this means a second or later play of that hand type this round.
- Interactions: `played_this_round` resets at the start of each round. It uses the scored (top) hand type.

### Red Card  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: gains +3 Mult whenever any Booster Pack is skipped. Starts at +0.
- When it acts: on skipping a booster pack (the gain); joker phase for the +mult (only when above 0).
- Interactions: the gain is not copied. Cannot be Perishable.

### Madness  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: when a Small Blind or Big Blind is selected, gain X0.5 Mult and destroy a random other joker. Starts at X1.
- When it acts: on blind selected, but not for boss blinds; joker phase for the Xmult (only when above X1).
- Interactions:
  - The joker to destroy is picked at random from the other jokers that are not Eternal and not already being destroyed.
  - It still gains X0.5 if there is nothing to destroy.
  - The gain and the destruction are not copied; the Xmult is. Cannot be Perishable.

### Square Joker  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: gains +4 Chips if the played hand has exactly 4 cards. Starts at 0.
- When it acts: before phase for the gain, which counts for this same hand; joker phase for the +chips.
- Interactions: counts all played cards, not only scoring ones. The gain is not copied. Cannot be Perishable.

### Seance  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: if the poker hand contains a Straight Flush, create a random Spectral card. You must have room. (Display name "Séance".)
- When it acts: joker phase.
- Interactions: the "Straight Flush" entry exists whenever the played cards hold both a straight and a flush; this includes Royal Flush and the 4-card versions allowed by Four Fingers. Copies create more Spectrals if there is room.

### Riff-raff  (rarity Common, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: when a blind is selected, create 2 Common jokers. You must have room.
- When it acts: on blind selected, every blind.
- Interactions:
  - It creates min(2, free joker slots) jokers, counting jokers already queued. The 2 is written into the code.
  - The created jokers have random editions according to normal creation rules.
  - Blueprint and Brainstorm copies create more if room remains.

### Vampire  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: gains X0.1 Mult for each scoring Enhanced card played, and removes that card's enhancement. Starts at X1.
- When it acts: before phase (strip and gain); joker phase for the Xmult (only when above X1).
- Interactions:
  - Affects scoring cards whose enhancement is not "base" (Bonus, Mult, Wild, Glass, Steel, Stone, Gold, Lucky) and that are not debuffed.
  - The enhancement is removed **before** card scoring, so those cards score as plain cards this hand.
  - Seals and editions are kept.
  - Jokers act left to right in the before phase. A Midas Mask placed left of Vampire turns face cards Gold first, and Vampire then strips them and gains.
  - The gain is not copied. Cannot be Perishable.

### Shortcut  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: no)
- Effect: Straights can be made with gaps of 1 rank (example: 10 8 6 5 3).
- When it acts: passive, in `get_straight`.
- Interactions:
  - Each single missing rank may be skipped, but not two missing ranks in a row.
  - Ace can be low or high.
  - Combines with Four Fingers.

### Hologram  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: gains X0.25 Mult every time a playing card is added to your deck. Starts at X1.
- When it acts: on "playing card added" (gain of 0.25 x number of cards added); joker phase for the Xmult (only when above X1).
- Interactions:
  - Ways a card is added: Standard Pack picks, buying playing cards in the shop, Marble Joker, DNA, Certificate, Cryptid (2 cards at once gives +0.5), Familiar, Grim and Incantation.
  - It does not gain while it is itself being destroyed.
  - The gain is not copied. Cannot be Perishable.

### Vagabond  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: create a Tarot card if the hand is played while you have $4 or less. You must have room.
- When it acts: joker phase. It checks `G.GAME.dollars <= 4`, and negative money (with Credit Card) qualifies.
- Interactions: it reads `G.GAME.dollars` directly, without `dollar_buffer`. Money from this hand's own scoring is applied by queued events (note 7), so the check most likely sees your money as it was before this hand's payouts. This timing is inferred from the event queue, not written explicitly. Copies create more Tarots if there is room.

### Baron  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: each King held in hand gives X1.5 Mult.
- When it acts: held-in-hand step, Xmult, once per held King.
- Interactions:
  - Debuffed Kings give nothing (a "Debuffed" message only). Stone Cards are never Kings.
  - Mime and a Red Seal on held Kings retrigger the X1.5.
  - Blueprint and Brainstorm copies each apply X1.5 per King again.

### Cloud 9  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: no)
- Effect: earn $1 for each 9 in your full deck at end of round.
- When it acts: end of round, cash-out money (`calculate_dollar_bonus`).
- Interactions: counts every playing card you own with rank id 9, including debuffed and enhanced ones but not Stone Cards. The count is recomputed every frame. It pays nothing if there are no 9s. Not copyable.

### Rocket  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: no)
- Effect: earn $1 at end of round. The payout increases by $2 each time a Boss Blind is defeated.
- When it acts: end of round, cash-out money.
- Interactions:
  - The +$2 is applied in `end_round`, which runs before the cash-out screen. So the round in which you beat a boss already pays the raised amount: the first boss round pays $3.
  - Not copyable. Cannot be Perishable.

### Obelisk  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: gains X0.2 Mult for each hand in a row played without playing your most played poker hand. Starts at X1.
- When it acts: before phase for the update, which counts for this same hand; joker phase for the Xmult (only when above X1).
- Interactions:
  - It compares play counts after the current hand has been added. If the scored hand type's run-wide play count is now strictly greater than every other visible hand's count, Obelisk resets to X1. Otherwise it gains X0.2.
  - A tie for most played does NOT reset it.
  - Hands debuffed by the boss skip the before phase, so they neither gain nor reset.
  - The update is not copied. Cannot be Perishable.

---

## Ambiguities and code quirks found

- **Vagabond money timing**: the code reads `G.GAME.dollars` without `dollar_buffer`. Concluding that same-hand income is not yet counted relies on `ease_dollars` being queued as an event. This is well supported but not stated explicitly in the code.
- **Riff-raff and Business Card** use the literal 2 in code rather than their config values. For Business Card, config `extra = 2` is the odds denominator.
- **Marble Joker** `extra = 1` is unused; it always adds exactly one Stone Card.
- **Joker Stencil** pays through the generic "x_mult > 1" branch that comes before its own empty-slot branch, so its real value is exactly the `Card:update` formula (empty slots + number of Stencils).
- **Raised Fist** picks the lowest card by `base.id`, ignoring debuffs, and gives nothing if that card is debuffed. On ties, the rightmost tied card is chosen.
- **Loyalty Card** counts hands from when the card was **created** (`hands_played_at_create` is set in `set_ability`), not from when it was bought. In practice no hands are played in a shop, so the two are the same.


---

# Jokers, part B (game.lua lines 448 to 526: Midas Mask through Perkeo)

Source: vanilla Balatro 1.0.1o Lua. Every number below comes from the `config` table in game.lua, and every behaviour comes from card.lua (`Card:calculate_joker`, `Card:add_to_deck`, `Card:update`, `Card:calculate_dollar_bonus`, `Card:set_cost`, `Card:is_suit`, `Card:is_face`) and functions/state_events.lua (`G.FUNCS.evaluate_play`, `end_round`, `G.FUNCS.discard_cards_from_highlighted`). Part A (another file) covers game.lua lines up to 447 (through Obelisk).

75 jokers are in this section (order 76 to 150).

## Shared rules that every entry below relies on

### Scoring order of one played hand (from G.FUNCS.evaluate_play)
1. The poker hand is identified. The "scoring hand" is the cards that make the hand, plus every played Stone Card, then sorted left to right by screen position (Splash makes every played card scoring).
2. If the Boss Blind debuffs the whole hand, steps 3 to 8 are skipped. Instead each joker gets a "debuffed hand" call (only Matador in this section uses it). Then step 9 still happens.
3. "Before" phase: each joker, left to right (Midas Mask, Spare Trousers, and others act here).
4. The Flint halves chips and mult (if active).
5. Scored cards, left to right. A debuffed scored card is skipped completely: no chips, no per-card joker effects, no retriggers. For a non-debuffed card the game first counts its retriggers (Red Seal, then every joker's retrigger answer, left to right). Then, for the first trigger and each retrigger, it evaluates: the card's own chips, mult, Xmult, dollars, edition, and then every joker's per-card effect, left to right. Each trigger recalculates everything, so random effects roll again on each retrigger.
6. Cards held in hand, left to right. For each card: the card's own held effect (Steel), then every joker's held-card effect. Retriggers for held cards (Red Seal, Mime) are only granted if the first evaluation produced at least one effect for that card. Retriggers are counted once, on the first pass, and do not chain.
7. Joker phase ("joker_main"): for each joker left to right (then each consumable, for Observatory): that joker's edition +chips/+mult, then its main effect, then "joker-on-joker" effects aimed at it (Baseball Card), then its edition Xmult.
8. Deck final step (Plasma Deck), then card destruction (Glass Card breaking and "destroying_card" jokers), then every joker gets a "playing cards removed" call.
9. "After" phase: each joker, left to right. This runs even when the hand was debuffed by the boss.

### Copying (Blueprint, Brainstorm)
- The `blueprint_compat` flag in game.lua is used only for the "Compatible / Incompatible" label in the UI (card.lua line 4234). The real behaviour is decided in code: a copied joker does whatever its code does for that call, except parts guarded by `not context.blueprint`. Effects that live outside `calculate_joker` are never copied: hand size, discards, hands, Oops! All 6s, To the Moon, Astronomer prices, Smeared Joker suit merging, Showman pool rules, and end-of-round cash from `calculate_dollar_bonus` (Golden Joker, Satellite, Rocket, Cloud 9, Delayed Gratification). Each entry below says what actually copies.
- A joker's edition is never copied. The copier's own edition applies to the copier.

### Debuffed jokers
- `calculate_joker` returns nothing for a debuffed joker.
- When a joker becomes debuffed, `remove_from_deck(true)` runs, so passive effects (hand size, discards, hands, Oops, To the Moon, Astronomer) switch off. They switch back on when the debuff ends.
- `find_joker` ignores debuffed jokers by default, so a debuffed Showman, Smeared Joker or Astronomer does nothing.

### Probabilities
Odds are written as base odds "1 in N". In code the roll is `pseudorandom(...) < G.GAME.probabilities.normal / N`. Each Oops! All 6s doubles `G.GAME.probabilities.normal`.

### Cost
"Base cost" is `cost` in game.lua. The shop price is `max(1, floor((base + inflation + edition surcharge + 0.5) * (100 - discount%) / 100))`. Edition surcharge: Foil +2, Holo +3, Polychrome +5, Negative +5. Sell value is `max(1, floor(price / 2)) + extra_value`. Gift Card and Egg add to extra_value.

"Eternal: no" means `eternal_compat = false`, so the joker cannot get the Eternal sticker. "Perishable: no" means `perishable_compat = false`.

---

### Midas Mask  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: no)
- Effect: every scoring card that counts as a face card is permanently turned into a Gold Card.
- When it acts: "before" phase, before any card is scored. No chips or mult of its own.
- Interactions:
  - It changes the cards before they score, so the converted cards score as Gold Cards in this same hand (Golden Ticket pays $4 for each, on each trigger).
  - It checks only the scoring cards, using `is_face()`. A debuffed card is never a face card, so debuffed faces are not converted.
  - With Pareidolia, every scoring card counts as a face card, Stone Cards included, so every scoring card becomes Gold. Any existing enhancement (Glass, Steel, Lucky, Stone and others) is overwritten. Seals and editions are kept, because only the enhancement changes.
  - The code is guarded by `not context.blueprint`, so copies do nothing.

### Luchador  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: yes; Eternal: no)
- Effect: when sold, if the current blind is a Boss Blind that is not already disabled, it disables that blind.
- When it acts: on selling this card.
- Interactions:
  - Selling sends the "selling self" call only to the card being sold. So a Blueprint next to Luchador gains nothing when Luchador is sold.
  - The reverse works. If you sell a Blueprint whose target is Luchador (or a Brainstorm while Luchador is leftmost), the call is forwarded and the boss is disabled. Luchador stays.

### Photograph  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: the first face card in the scoring hand gives X2 Mult when scored.
- When it acts: per scored card, during card scoring. Xmult.
- Interactions:
  - "First" means the leftmost card in the scoring hand for which `is_face()` is true. Only scoring cards count; unscored played cards are ignored.
  - A debuffed face card does not count as a face card, so the next non-debuffed face card is "first".
  - With Pareidolia, the leftmost scoring card is "first" (this can be a Stone Card).
  - It is evaluated on every trigger of that card, so retriggers repeat the X2: Red Seal, Sock and Buskin, Hanging Chad if the face card is leftmost, Seltzer, Dusk.
  - A copy gives another X2 on that same card, on each trigger, at the copier's position in the joker order.

### Gift Card  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: no)
- Effect: at end of round, adds $1 to the sell value (`extra_value`) of every joker you own (Gift Card included) and every consumable.
- When it acts: end of round. No scoring.
- Interactions:
  - Higher sell values raise Swashbuckler and Ceremonial Dagger's gain, and the money from selling.
  - The code is in the `not context.blueprint` end-of-round branch, so copies do nothing.

### Turtle Bean  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: no; Eternal: no)
- Effect: +5 hand size. At each end of round the bonus drops by 1.
- When it acts: hand size is added when you get it. The drop happens at end of round.
- Interactions:
  - The bonus goes 5, 4, 3, 2, 1. At the 5th end of round, when the bonus would reach 0, the bean is destroyed ("Eaten") and the remaining +1 is removed.
  - It does not respond to copies.

### Erosion  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: +4 Mult for each card your full deck has below the starting deck size.
- When it acts: joker phase. +Mult.
- Interactions:
  - The formula is `4 * (starting_deck_size - number of playing cards)`, applied only if the result is above 0.
  - `starting_deck_size` is the deck size when the run started: 52 normally, 40 for Abandoned Deck.
  - Copies give the same +Mult again.

### Reserved Parking  (rarity Common, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: each face card held in hand has a 1 in 2 chance to give $1.
- When it acts: per card held in hand, during the held-card step of a played hand. Money only.
- Interactions:
  - It uses `is_face()`, which is false for debuffed cards. So debuffed faces never pay. The code's "debuffed" message branch can never run, because the face check fails first.
  - Mime and Red Seal retrigger a held face card only if the first roll succeeded (or another effect hit that card). Each retrigger rolls again.
  - Each copy rolls separately.
  - The money goes into the dollar buffer immediately, so Bull and Bootstraps later in the same hand count it.

### Mail-In Rebate  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: earn $5 for each discarded card of the chosen rank.
- When it acts: on discard, once per discarded card that matches.
- Interactions:
  - Debuffed cards are skipped. Stone Cards never match, because their rank id is random and negative.
  - The rank is reset at every end of round, to the rank of a random non-Stone card in your deck (seed `mail` plus ante). It can land on the same rank again. If the deck has no non-Stone cards, the displayed rank becomes Ace, but the rank id actually checked is left unchanged (a code quirk with no practical effect in normal play).
  - It also counts cards that The Hook discards for you.
  - It has no copy guard, so copies pay again.

### To the Moon  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: no)
- Effect: interest per $5 rises by $1.
- When it acts: passive. It adds 1 to `interest_amount` when you get it.
- Interactions:
  - Interest at cash-out is `interest_amount * min(floor(money / 5), interest_cap / 5)`. The default cap is 25, so 5 steps. With one To the Moon that is $2 per $5, up to $10.
  - Two copies of To the Moon stack.
  - Blueprint cannot copy it.

### Hallucination  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: 1 in 2 chance to create a random Tarot card when any Booster Pack is opened.
- When it acts: when a pack is opened. It must have room: consumables held plus pending must be below the limit.
- Interactions:
  - The roll uses seed `halu` plus ante.
  - Each copy rolls separately, and also needs room.

### Fortune Teller  (rarity Common, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: +1 Mult per Tarot card used this run.
- When it acts: joker phase. +Mult.
- Interactions:
  - The code adds `G.GAME.consumeable_usage_total.tarot` directly. Config `extra = 1` is only used in the description.
  - It counts all Tarots used this run, including those used before you got it.
  - Copies give the same amount again.

### Juggler  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: no)
- Effect: +1 hand size.
- When it acts: passive, from when you get it.

### Drunkard  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: no)
- Effect: +1 discard each round.
- When it acts: passive. It raises the per-round discard count and also gives +1 discard right away when you get it.

### Stone Joker  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: +25 Chips for each Stone Card in your full deck.
- When it acts: joker phase. +Chips.
- Interactions:
  - The count includes every playing card with the Stone enhancement, wherever it is. It is recounted every frame.
  - It only appears in the shop or packs if your deck has at least one Stone Card (`enhancement_gate`).
  - Copies give the same chips again.

### Golden Joker  (rarity Common, base cost $6, Blueprint/Brainstorm compatible: no)
- Effect: earn $4 at end of round.
- When it acts: cash-out screen (`calculate_dollar_bonus`).
- Interactions: Blueprint cannot copy it.

### Lucky Cat  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes; Perishable: no)
- Effect: gains X0.25 Mult each time a Lucky Card triggers successfully. Starts at X1.
- When it acts:
  - The gain happens per scored card, during card scoring.
  - The Xmult is applied in the joker phase, only once it is above X1.
- Interactions:
  - A Lucky Card sets a "lucky_trigger" flag if its 1 in 5 Mult roll or its 1 in 15 money roll succeeds. The card's own effects are evaluated before the jokers' per-card effects, so Lucky Cat sees the flag in the same trigger. The flag is cleared after each trigger.
  - Result: +X0.25 per successful trigger instance, even if both rolls hit.
  - Each retrigger of a Lucky Card rolls again and can add another X0.25.
  - Debuffed Lucky Cards are skipped.
  - The gain is guarded against copies. The Xmult can be copied.
  - It only appears if your deck has a Lucky Card.

### Baseball Card  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: each Uncommon joker gives X1.5 Mult.
- When it acts: joker phase, as a "joker-on-joker" effect. Xmult.
- Interactions:
  - The X1.5 is applied right after each Uncommon joker's own main effect, and before that joker's edition Xmult.
  - It applies to every Uncommon joker, even one that produced no effect.
  - The code checks only `rarity == 2` and does not check debuff. So a debuffed Uncommon joker still triggers it, as long as Baseball Card itself is not debuffed.
  - A Blueprint or Brainstorm copying Baseball Card gives another X1.5 for each Uncommon joker.

### Bull  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: +2 Chips for each $1 you have.
- When it acts: joker phase. +Chips.
- Interactions:
  - It uses money plus the dollar buffer, so money earned earlier in this same hand counts (Golden Ticket, Rough Gem, Reserved Parking, Gold Seals).
  - At $0 or less, nothing.
  - Copies give the same chips again.

### Diet Cola  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes; Eternal: no)
- Effect: when sold, you get a free Double Tag.
- When it acts: on selling this card.
- Interactions:
  - As with Luchador, a Blueprint gains nothing when Diet Cola is sold.
  - Selling a Blueprint whose target is Diet Cola (or a Brainstorm while Diet Cola is leftmost) does create a Double Tag.

### Trading Card  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: no)
- Effect: if the first discard of the round has exactly 1 card, that card is destroyed and you earn $3.
- When it acts: on discard.
- Interactions:
  - Condition: `discards_used <= 0` and the discard has exactly 1 card.
  - The destroyed card counts as removed: a Glass Card shatters and feeds Glass Joker, and a face card feeds Canio.
  - The code does not exclude The Hook's forced discard, but The Hook discards 2 cards whenever it can.
  - The code is guarded against copies.

### Flash Card  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: yes; Perishable: no)
- Effect: gains +2 Mult per shop reroll. Starts at +0.
- When it acts: the gain happens on each reroll, free rerolls included. The +Mult applies in the joker phase.
- Interactions: the gain is guarded against copies. The +Mult can be copied.

### Popcorn  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes; Eternal: no)
- Effect: +20 Mult, minus 4 Mult at each end of round.
- When it acts: joker phase for the +Mult. The drop happens at end of round.
- Interactions:
  - Value by round: +20, +16, +12, +8, +4.
  - At the 5th end of round, when the value would reach 0, it is destroyed.
  - The drop is guarded against copies. The +Mult can be copied.

### Spare Trousers  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes; Perishable: no)
- Effect: gains +2 Mult if the played hand contains a Two Pair. Starts at +0.
- When it acts:
  - The gain happens in the "before" phase, so it already counts this hand.
  - The +Mult applies in the joker phase.
- Interactions:
  - The code checks whether the hand contains a Two Pair or a Full House.
  - The gain is guarded against copies. The +Mult can be copied.

### Ancient Joker  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of the chosen suit gives X1.5 Mult.
- When it acts: per scored card. Xmult.
- Interactions:
  - The suit check uses `is_suit`, so Wild Cards and Smeared Joker count.
  - At every end of round, the suit is re-picked from the 3 suits other than the current one.
  - Retriggers repeat the X1.5, and copies apply it again.

### Ramen  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes; Eternal: no)
- Effect: X2 Mult, which drops by X0.01 for each card discarded.
- When it acts: the Xmult applies in the joker phase while above X1. The drop happens on discard, once per card.
- Interactions:
  - Every discarded card counts, debuffed ones and The Hook's forced discards included.
  - When `Xmult - 0.01 <= 1` it is destroyed instead. Floating-point simulation: 99 cards bring it to about X1.01, and the 100th discarded card destroys it.
  - The drop is guarded against copies. The Xmult can be copied.

### Walkie Talkie  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: each scored 10 or 4 gives +10 Chips and +4 Mult.
- When it acts: per scored card.
- Interactions: retriggers repeat it, and copies apply it again.

### Seltzer  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes; Eternal: no)
- Effect: retriggers every scored card once, for the next 10 hands.
- When it acts:
  - The retrigger happens in card scoring, 1 extra trigger per scored non-debuffed card.
  - The countdown happens in the "after" phase of every played hand, including hands the boss debuffs.
- Interactions:
  - The counter goes 10 down to 1. It is destroyed in the "after" phase of the 10th hand.
  - The retrigger has no copy guard, so a copy adds one more retrigger per card. The countdown is guarded.

### Castle  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes; Perishable: no)
- Effect: gains +3 Chips for each discarded card of the chosen suit. Starts at +0.
- When it acts:
  - The gain happens on discard, once per matching card.
  - The +Chips applies in the joker phase while above 0.
- Interactions:
  - Debuffed cards don't count.
  - The suit check uses `is_suit`, so Wild Cards and Smeared Joker count.
  - At every end of round, the suit is reset to the suit of a random non-Stone card in your deck. It can repeat.
  - The gain is guarded against copies. The +Chips can be copied.

### Smiley Face  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: each scored face card gives +5 Mult.
- When it acts: per scored card. +Mult.
- Interactions: with Pareidolia every scored card counts. Retriggers repeat it, and copies apply it again.

### Campfire  (rarity Rare, base cost $9, Blueprint/Brainstorm compatible: yes)
- Effect: gains X0.25 Mult for each card sold. Resets to X1 when a Boss Blind is defeated.
- When it acts:
  - The gain happens when any other card is sold: jokers and consumables both count.
  - The Xmult applies in the joker phase while above X1.
  - The reset happens at the end of a round against a Boss Blind.
- Interactions: the gain and reset are guarded against copies. The Xmult can be copied.

### Golden Ticket  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: each scored Gold Card earns $4.
- When it acts: per scored card. Money only.
- Interactions:
  - Retriggers pay again, and copies pay again.
  - Cards that Midas Mask turns to Gold in the same hand count.
  - It only appears if your deck has a Gold Card.

### Mr. Bones  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: no; Eternal: no)
- Effect: prevents the game over if your chips are at least 25% of the blind's requirement. It then destroys itself.
- When it acts: end of round, only if you would lose. The check is `chips / blind chips >= 0.25`.
- Interactions: the code is in the copy-guarded end-of-round branch, so copies do nothing.

### Acrobat  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult on the final hand of the round.
- When it acts: joker phase, when no hands remain after this one (`hands_left == 0`). Xmult.
- Interactions: copies give another X3.

### Sock and Buskin  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: retriggers every scored face card once.
- When it acts: when card scoring counts retriggers.
- Interactions:
  - It uses `is_face()`, so Pareidolia makes it retrigger every scored card. Debuffed cards are skipped anyway.
  - A copy adds one more retrigger per face card.

### Swashbuckler  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: +Mult equal to the total sell value of all your other jokers.
- When it acts: joker phase, while above 0. The value is recalculated every frame.
- Interactions:
  - Config `mult = 1` is overwritten by the recalculation.
  - Gift Card and Egg raise it.
  - Copies give the same +Mult again.

### Troubadour  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: no)
- Effect: +2 hand size and -1 hand each round.
- When it acts: passive. The hand-size change is immediate. The hand change edits the per-round hand count, so it takes effect from the next round.

### Certificate  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: when a round begins, adds a random playing card with a random seal to your hand.
- When it acts: when the first hand of a blind is drawn (no hands played, no discards used).
- Interactions:
  - The card has a random rank and suit and no enhancement. It joins your deck permanently.
  - Seal odds, from one roll: Red 25%, Blue 25%, Gold 25%, Purple 25%.
  - The boss's debuffs are applied to the new card.
  - It counts as a playing card added (Hologram).
  - Copies create another card.

### Smeared Joker  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: no)
- Effect: Hearts and Diamonds count as the same suit, and Spades and Clubs count as the same suit.
- When it acts: passive, inside every suit check (`is_suit`), flush checks included.
- Interactions:
  - Stone Cards still have no suit.
  - Any suit-based joker sees a Heart as a Diamond and the reverse (and likewise for Spades and Clubs). For example, Rough Gem pays on Hearts.
  - See Seeing Double and Flower Pot for odd results.
  - It does nothing while debuffed.

### Throwback  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: X0.25 Mult for each blind skipped this run, so the total is `X(1 + 0.25 * skips)`.
- When it acts: joker phase, only when above X1 (at least one skip).
- Interactions: the run skip count only goes up. Copies give the same Xmult again.

### Hanging Chad  (rarity Common, base cost $4, Blueprint/Brainstorm compatible: yes)
- Effect: retriggers the first scoring card 2 more times.
- When it acts: when card scoring counts retriggers.
- Interactions:
  - "First" means `scoring_hand[1]`: the leftmost card in the scoring hand after Stone Cards are added and sorted by position. Unscored played cards don't count. This can be a Stone Card.
  - If that card is debuffed, it is skipped and nothing is retriggered. Chad does not move on to the next card.
  - It stacks with Red Seal, Sock and Buskin, Seltzer and Dusk.
  - A copy adds 2 more retriggers.

### Rough Gem  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: each scored Diamond card earns $1.
- When it acts: per scored card. Money.
- Interactions: Wild Cards and Smeared Joker count. Retriggers pay again, and copies pay again.

### Bloodstone  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: each scored Heart card has a 1 in 2 chance to give X1.5 Mult.
- When it acts: per scored card. Xmult.
- Interactions: it rolls separately on each trigger and for each copy. Wild Cards and Smeared Joker count.

### Arrowhead  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: each scored Spade card gives +50 Chips.
- When it acts: per scored card.
- Interactions: Wild Cards and Smeared Joker count. Retriggers repeat it, and copies apply it again.

### Onyx Agate  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: each scored Club card gives +7 Mult.
- When it acts: per scored card.
- Interactions: Wild Cards and Smeared Joker count. Retriggers repeat it, and copies apply it again.

### Glass Joker  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes; Perishable: no)
- Effect: gains X0.75 Mult for each Glass Card destroyed. Starts at X1.
- When it acts: the Xmult applies in the joker phase while above X1. Gains come from:
  - Scored Glass Cards that break (Glass Card's own 1 in 4 base roll, which Oops doubles). These are counted at the "playing cards removed" step of the same hand.
  - A Glass Card destroyed by Trading Card.
  - Glass Cards destroyed by The Hanged Man (special branch in the "consumable used" call).
- Interactions:
  - The gain is guarded against copies. The Xmult can be copied.
  - It only appears if your deck has a Glass Card.
  - Inferred, not certain: Glass Cards destroyed by Immolate, Familiar, Grim or Incantation probably do not count. Those cards only get their "shattered" flag in a later event, after the jokers have already been notified. The Hanged Man special branch exists for the same reason.

### Showman  (rarity Uncommon, base cost $5, Blueprint/Brainstorm compatible: no)
- Effect: Joker, Tarot, Planet and Spectral cards can appear even if a copy already exists.
- When it acts: passive, in the shop and pack card pools.
- Interactions:
  - Without Showman, a card key in `G.GAME.used_jokers` is left out of the pool. The key is added when any card of that kind is created. It is removed when such a card is removed and no copy remains in your joker or consumable slots.
  - Showman also lets The Soul and Black Hole be rolled again after they have been seen.
  - It does nothing while debuffed.

### Flower Pot  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult if the scoring hand contains a Diamond, a Club, a Heart and a Spade.
- When it acts: joker phase. Xmult.
- Interactions:
  - Only scoring cards count, so you need at least 4 scoring cards.
  - Non-Wild cards are checked first. Each one fills the first empty suit it matches, in the order Hearts, Diamonds, Spades, Clubs. This check ignores debuff, so debuffed scoring cards still count their suit.
  - Wild Cards then fill any empty suit, in the same order. A debuffed Wild Card counts for nothing.
  - Stone Cards count for nothing.
  - With Smeared Joker, a red card fills Hearts first, then Diamonds.
  - Copies give another X3.

### Blueprint  (rarity Rare, base cost $10, Blueprint/Brainstorm compatible: yes)
- Effect: copies the ability of the joker directly to its right.
- Exactly what the code does:
  - Target: the joker in the next slot to the right. If Blueprint is rightmost, there is no target and it does nothing.
  - Every call Blueprint receives (scoring phases, discard, end of round, blind selected, pack opened, shop end, and so on) is passed to the target's `calculate_joker` with `context.blueprint` set. Whatever the target returns is returned as Blueprint's own result, at Blueprint's position in the joker order.
  - Side effects inside the target's code also happen again. Examples: Matador pays again, Mail-In Rebate pays again, Hallucination rolls again, Certificate makes another card, Cartomancer another Tarot, Perkeo another Negative copy, Burnt Joker another level up.
  - Parts of the target guarded by `not context.blueprint` do not run: scaling gains, countdowns, self-destruction, Midas Mask, Trading Card, Invisible Joker's sale, Chicot.
  - Effects outside `calculate_joker` are not copied (see "Copying" at the top).
- Retriggers:
  - Copying a retrigger joker returns its repetitions, so the copy adds retriggers.
  - Examples: Sock and Buskin gives one more per face card. Hanging Chad gives 2 more on the first scoring card. Seltzer gives one more per scored card. Mime gives one more per held card that had an effect.
- Per-card effects: during card scoring, every joker (Blueprint included) is asked once per scored card per trigger. So Photograph, Triboulet, The Idol, Bloodstone (its own roll) and other per-card effects apply again in Blueprint's slot, on every trigger.
- Joker-on-joker: copying Baseball Card gives another X1.5 for each Uncommon joker.
- Chains:
  - Blueprint can point at another Blueprint or a Brainstorm, and the call passes along the chain.
  - A counter stops the chain once it has passed through more copiers than there are jokers plus one.
  - The effect is credited to the first copier in the chain.
- Debuff: if Blueprint is debuffed, or its target is debuffed, nothing happens.
- Selling: selling Blueprint sends its "selling self" call to its target. If the target is Luchador, the boss is disabled. If the target is Diet Cola, you get a Double Tag. Invisible Joker's sale is guarded.
- The "Compatible / Incompatible" label just reads the target's `blueprint_compat` flag.

### Wee Joker  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes; Perishable: no)
- Effect: gains +8 Chips each time a 2 is scored. Starts at +0.
- When it acts:
  - The gain happens per scored card, on every trigger (retriggers count).
  - The +Chips applies in the joker phase, so this hand's 2s already count.
- Interactions: the gain is guarded against copies. The +Chips can be copied.

### Merry Andy  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: no)
- Effect: +3 discards each round and -1 hand size.
- When it acts: passive. The 3 discards are added right away and to every later round. The hand-size cut is immediate.

### Oops! All 6s  (rarity Uncommon, base cost $4, Blueprint/Brainstorm compatible: no)
- Effect: doubles all listed probabilities.
- When it acts: passive. It multiplies `G.GAME.probabilities.normal` by 2 when you get it, and divides by 2 when it leaves or is debuffed. Several copies stack: 2 give x4.
- Interactions: in 1.0.1o the doubled value is used by:
  - Lucky Card (1 in 5 Mult, 1 in 15 money)
  - Glass Card break (1 in 4)
  - Bloodstone, Reserved Parking, Hallucination, Business Card, Space Joker, 8 Ball
  - Gros Michel and Cavendish dying (bad for you)
  - The Wheel of Fortune
  - The Wheel boss (1 in 7 face down, bad for you)

### The Idol  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: each scored card of the chosen rank and suit gives X2 Mult.
- When it acts: per scored card. Xmult.
- Interactions:
  - Rank must match exactly. The suit check uses `is_suit`, so a Wild Card or a Smeared Joker match of the right rank counts.
  - At every end of round, the target card is reset to the rank and suit of a random non-Stone card in your deck. It can repeat.
  - Retriggers repeat it, and copies apply it again.

### Seeing Double  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: X2 Mult if the scoring hand has a scoring Club and a scoring card of any other suit.
- When it acts: joker phase. Xmult.
- Interactions:
  - Non-Wild scoring cards add to every suit they match. Debuffed cards match nothing.
  - Wild Cards then fill the first empty suit, in the order Clubs, Diamonds, Spades, Hearts.
  - The condition is: Clubs filled, and at least one of Hearts, Diamonds or Spades filled.
  - With Smeared Joker, a single scoring Club or Spade counts as both Clubs and Spades, so it triggers on its own.
  - A lone Wild Card does not trigger it (it fills only Clubs). Two Wild Cards do.
  - The generic Xmult rule skips this joker by name, so it uses only this logic.
  - Copies give another X2.

### Matador  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: earn $8 if the played hand triggers the Boss Blind's ability.
- When it acts:
  - It checks `G.GAME.blind.triggered`. The flag is reset to false at the start of every played hand.
  - It pays in the joker phase, or in the "debuffed hand" call if the boss debuffed the whole hand. Either way, once per hand.
- What sets the flag:
  - A debuffed scoring card being skipped
  - The Flint
  - The Hook (when it discards)
  - Crimson Heart (if you have jokers)
  - The Tooth
  - A hand debuffed by a boss rule (The Psychic, The Eye, The Mouth, and the hand-type and card-count debuffs)
  - The Arm (if the hand's level is above 1)
  - The Ox (if it is the most played hand)
- Interactions: copies pay again.

### Hit the Road  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: gains X0.5 Mult for each Jack discarded this round. Resets to X1 at end of round.
- When it acts:
  - The gain happens on discard, per Jack. Debuffed Jacks and Stone Cards don't count.
  - The Xmult applies in the joker phase while above X1.
- Interactions: the gain and reset are guarded against copies. The Xmult can be copied.

### The Duo  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: X2 Mult if the played hand contains a Pair.
- When it acts: joker phase. Xmult.
- Interactions:
  - "Contains" means any hand that includes a Pair: Two Pair, Three of a Kind, Full House, Four of a Kind and others.
  - Ignore the `effect = "X1.5 Mult"` text in game.lua; the code uses `config.Xmult = 2`.
  - Copies give another X2.

### The Trio  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult if the played hand contains a Three of a Kind (so Full House and Four of a Kind count too).
- When it acts: joker phase.
- Interactions: ignore the `effect = "X2 Mult"` text; config is `Xmult = 3`. Copies give another X3.

### The Family  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: X4 Mult if the played hand contains a Four of a Kind.
- When it acts: joker phase.
- Interactions: ignore the `effect = "X3 Mult"` text; config is `Xmult = 4`. Copies give another X4.

### The Order  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult if the played hand contains a Straight (Straight Flush included).
- When it acts: joker phase.
- Interactions: copies give another X3.

### The Tribe  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: X2 Mult if the played hand contains a Flush (Straight Flush, Flush House and Flush Five included).
- When it acts: joker phase.
- Interactions: ignore the `effect = "X3 Mult"` text; config is `Xmult = 2`. Copies give another X2.

### Stuntman  (rarity Rare, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: +250 Chips and -2 hand size.
- When it acts: +Chips in the joker phase. The hand-size cut is passive and immediate.
- Interactions: copies add +250 Chips but not the hand-size cut.

### Invisible Joker  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: no; Eternal: no)
- Effect: after 2 rounds, selling it duplicates a random other joker.
- When it acts:
  - The round counter goes up by 1 at every end of round.
  - On sale, if the counter is at least 2, it copies a random other joker you own.
- Interactions:
  - Room check at sale time: joker count (Invisible still included) must not exceed the joker limit. Otherwise "No room!".
  - With no other jokers, nothing happens.
  - The copy keeps all of the original's state (scaling values) and its edition, except Negative: if the chosen joker is Negative, the copy gets no edition.
  - Copying another Invisible Joker resets the copy's counter to 0.
  - The code is guarded against copies, and selling a Blueprint aimed at it does nothing.

### Brainstorm  (rarity Rare, base cost $10, Blueprint/Brainstorm compatible: yes)
- Effect: copies the ability of the leftmost joker.
- Exactly what the code does: the same as Blueprint, but the target is always the joker in slot 1. If Brainstorm is in slot 1, it does nothing. All Blueprint rules apply: guarded parts, retriggers, per-card effects, chains, selling Brainstorm forwarding to Luchador or Diet Cola, and no edition copying.

### Satellite  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: no)
- Effect: earn $1 at end of round per unique Planet card used this run.
- When it acts: cash-out screen (`calculate_dollar_bonus`).
- Interactions:
  - It counts distinct Planet card types used this run, not total uses.
  - Black Hole is a Spectral card, so it does not count.
  - Blueprint cannot copy it.

### Shoot the Moon  (rarity Common, base cost $5, Blueprint/Brainstorm compatible: yes)
- Effect: each Queen held in hand gives +13 Mult.
- When it acts: per card held in hand, during a played hand. +Mult.
- Interactions:
  - The code uses a literal 13, not the config value (which is also 13).
  - A debuffed Queen gives only a "Debuffed" message and no Mult. That message still counts as an effect, so Mime and Red Seal retrigger it, for nothing.
  - Mime and Red Seal retrigger a non-debuffed Queen for another +13.
  - Copies give another +13 per Queen.

### Driver's License  (rarity Rare, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: X3 Mult if your full deck has at least 16 Enhanced cards.
- When it acts: joker phase. Xmult.
- Interactions:
  - An Enhanced card is any playing card whose enhancement is not "none": Bonus, Mult, Wild, Glass, Steel, Stone, Gold, Lucky. Seals and editions alone do not count.
  - The count is recalculated every frame.
  - Copies give another X3.

### Cartomancer  (rarity Uncommon, base cost $6, Blueprint/Brainstorm compatible: yes)
- Effect: creates a random Tarot card when a blind is selected.
- When it acts: when a blind is selected. It must have room in the consumable slots.
- Interactions: copies create another Tarot, if there is room.

### Astronomer  (rarity Uncommon, base cost $8, Blueprint/Brainstorm compatible: no)
- Effect: all Planet cards and Celestial Packs in the shop are free.
- When it acts: passive, in `set_cost`. All prices are recalculated when it is gained or lost.
- Interactions:
  - The price becomes $0. The resulting sell value is $1 plus any extra_value.
  - It does nothing while debuffed.

### Burnt Joker  (rarity Rare, base cost $8, Blueprint/Brainstorm compatible: yes)
- Effect: upgrades the level of the first discarded poker hand each round by 1.
- When it acts: just before the first discard of the round resolves (`discards_used <= 0`). It is skipped for The Hook's forced discard.
- Interactions:
  - The hand type is whatever the discarded cards form. One card or junk is High Card.
  - Config `h_size = 0` and `extra = 4` are not used by its effect.
  - Copies level the hand up again.

### Bootstraps  (rarity Uncommon, base cost $7, Blueprint/Brainstorm compatible: yes)
- Effect: +2 Mult for every $5 you have.
- When it acts: joker phase. The formula is `2 * floor((money + dollar buffer) / 5)`, applied only if that floor is at least 1.
- Interactions: money earned earlier in the same hand counts. Copies give the same +Mult again.

### Canio  (code name "Caino"; rarity Legendary, base cost $20, Blueprint/Brainstorm compatible: yes)
- Effect: gains X1 Mult each time a face card is destroyed. Starts at X1.
- When it acts:
  - The gain happens at every "playing cards removed" call, +1 per removed card for which `is_face()` is true.
  - The Xmult applies in the joker phase while above X1.
- What triggers a removal:
  - Scored cards destroyed by breaking or by joker effects
  - Trading Card
  - Hanged Man, Immolate, Familiar, Grim and Incantation destructions
- Interactions:
  - `is_face()` is false for debuffed cards, so destroyed debuffed face cards don't count. With Pareidolia every destroyed card counts.
  - The gain is guarded against copies. The Xmult can be copied.

### Triboulet  (rarity Legendary, base cost $20, Blueprint/Brainstorm compatible: yes)
- Effect: each scored King or Queen gives X2 Mult.
- When it acts: per scored card. Xmult.
- Interactions:
  - It checks the rank directly, not "face", so Pareidolia does not widen it.
  - Retriggers repeat it, and copies apply it again.

### Yorick  (rarity Legendary, base cost $20, Blueprint/Brainstorm compatible: yes)
- Effect: gains X1 Mult every 23 cards discarded. Starts at X1.
- When it acts:
  - On discard, per card. A counter starts at 23 and drops by 1 per discarded card. On the card that finds it at 1, it resets to 23 and Yorick gains X1. So the 23rd card, the 46th, and so on.
  - The Xmult applies in the joker phase while above X1.
- Interactions:
  - Every discarded card counts, debuffed ones and The Hook's forced discards included.
  - The gain is guarded against copies. The Xmult can be copied.

### Chicot  (rarity Legendary, base cost $20, Blueprint/Brainstorm compatible: no)
- Effect: disables the effect of every Boss Blind.
- When it acts:
  - When a Boss Blind is selected.
  - Also immediately on being gained, if the current blind is an active Boss Blind.
- Interactions: guarded against copies.

### Perkeo  (rarity Legendary, base cost $20, Blueprint/Brainstorm compatible: yes)
- Effect: at the end of the shop, creates a Negative copy of 1 random consumable you hold.
- When it acts: when you leave the shop, if you hold at least one consumable.
- Interactions:
  - The pick is random among all held consumables, Negative ones included.
  - Negative gives +1 consumable slot, so the copy always fits.
  - Copies create another Negative copy. Each picks separately, at the time its event runs.


---

# 04. Consumables, Vouchers, Tags, Boss Blinds, Enhancements, Editions, Seals

Source: vanilla Balatro 1.0.1o Lua. Every number below was read from the code. File references are given as `file:line` so any claim can be re-checked. Where the code is genuinely unclear, the entry says "AMBIGUOUS".

Conventions used throughout:

- "1 in N" chances are always coded as `pseudorandom(...) < G.GAME.probabilities.normal / N`. `probabilities.normal` is 1 normally and is doubled by the joker Oops! All 6s, so every "1 in N" below becomes "2 in N" with one copy of that joker, and so on.
- "Selected" means highlighted cards in hand (`G.hand.highlighted`).
- Base costs listed are before discounts. Real price = `max(1, floor((base_cost + inflation + edition_extra + 0.5) * (100 - discount_percent) / 100))` (card.lua:369-385). Edition extras: Foil +2, Holographic +3, Polychrome +5, Negative +5. With the joker Astronomer, Planet cards and Celestial packs cost $0. Sell value = `max(1, floor(cost/2)) + extra_value`.

---

## 0. General rules for using consumables (card.lua:1523-1588, button_callbacks.lua:2155)

- No consumable can be used while cards are in the play area, while the controller is locked, or while another consumable is resolving. Nothing can be used in states HAND_PLAYED, DRAW_TO_HAND or PLAY_TAROT.
- The used card is removed from its area BEFORE its effect runs (button_callbacks.lua:2209). So a card used from your consumable slots frees its own slot first. This matters for The Emperor, The High Priestess and The Fool.
- Usable at any time (shop, blind select, in a blind, in a pack), subject to the rules above: The Hermit, Temperance, every Planet, Black Hole (always), The Wheel of Fortune (needs an eligible joker), Ankh, Ectoplasm, Hex, The Emperor, The High Priestess, The Fool, Judgement, The Soul, Wraith (each has its own condition, listed per card).
- Cards that target selected cards (anything with `max_highlighted`) can only be used in state SELECTING_HAND (during a blind) or while a Tarot, Spectral or Planet pack is open. The number selected must be between `min_highlighted` (default 1) and `max_highlighted`. (`mod_num = min(5, max_highlighted)`, card.lua:4155, so the limits below are exact.)
- Familiar, Grim, Incantation, Immolate, Sigil and Ouija need the same states and at least 2 cards in hand (`#G.hand.cards > 1`).
- If the consumable itself is debuffed, using it does nothing (card.lua:1094).
- Pool rule for random creation: any Tarot, Planet, Spectral or Joker that currently exists anywhere in the run (held, in shop, in a pack) is excluded from random pools, unless you own Showman (common_events.lua:1987, card.lua:352, card.lua:4741-4746). The Soul and Black Hole are never in normal pools; they only appear by the special 0.3% roll in packs (see The Soul).

---

## 1. Tarot cards (22). All cost $3. (game.lua:533-554, card.lua:1091-1521)

Enhancement tarots (Magician, Empress, Hierophant, Lovers, Chariot, Justice, Devil, Tower) call `set_ability` on each selected card (card.lua:1143). This REPLACES the card's existing enhancement. The card keeps its rank, suit, edition, seal and permanent bonus chips (`perma_bonus`, e.g. from Hiker). Any enhancement can be overwritten by any other, including Stone.

Suit tarots (Star, Moon, Sun, World) call `change_suit` (card.lua:547-562). Rank, enhancement, edition and seal are kept. After the change the boss debuff is re-checked immediately, so converting a Club to a Heart during The Club removes its debuff (and the reverse during The Head adds one).

| # | Card | Targets | Exact effect |
|---|---|---|---|
| 1 | The Fool | none | Creates a new copy of the last Tarot or Planet card used this run (`G.GAME.last_tarot_planet`). It is a fresh card (no edition). Cannot be used if no Tarot/Planet has been used yet, or if the last one was The Fool itself. Needs a free consumable slot (its own slot counts as free if used from the slots). Spectral cards never set `last_tarot_planet`. The Fool records itself as "last used" only after it has made its card (the record is set by nested events queued after the creation event, misc_functions.lua:1215-1224), so using The Fool creates the previous card and then The Fool becomes the new "last used". |
| 2 | The Magician | 1 to 2 | Selected cards become Lucky Cards. |
| 3 | The High Priestess | none | Creates `min(2, free consumable slots)` random Planet cards. Usable only if there is a free slot or it is used from the consumable slots. |
| 4 | The Empress | 1 to 2 | Selected cards become Mult Cards. |
| 5 | The Emperor | none | Creates `min(2, free consumable slots)` random Tarot cards. Same usability rule as High Priestess. AMBIGUOUS: whether The Emperor can create another Emperor depends on whether the used Emperor still counts as existing when the new cards are generated (it is dissolved in a later event); probably it is still counted and so excluded, but this was not verified. |
| 6 | The Hierophant | 1 to 2 | Selected cards become Bonus Cards. |
| 7 | The Lovers | 1 | Selected card becomes a Wild Card. |
| 8 | The Chariot | 1 | Selected card becomes a Steel Card. |
| 9 | Justice | 1 | Selected card becomes a Glass Card. |
| 10 | The Hermit | none | Gain `max(0, min(current money, 20))`. So it doubles your money, capped at +$20, and gives $0 if money is $0 or negative. |
| 11 | The Wheel of Fortune | none | 1 in 4 chance. On success, one random joker that has NO edition gets Foil (50%), Holographic (35%) or Polychrome (15%) (`poll_edition(..., no_neg=true, guaranteed=true)`, common_events.lua:2055-2067). Never Negative. On failure: "Nope!", nothing happens, the card is still consumed. Cannot be used at all unless at least one joker without an edition exists. Jokers with any edition (including Negative) are never chosen. |
| 12 | Strength | 1 to 2 | Each selected card goes up one rank: 2->3 ... 10->Jack, Jack->Queen, Queen->King, King->Ace, and Ace wraps to 2 (card.lua:1126). Suit, enhancement, edition and seal kept. Works on Stone cards too (changes the hidden rank). |
| 13 | The Hanged Man | 1 to 2 | Destroys the selected cards (permanently removed from the deck). Glass cards use the shatter animation. Jokers are then told which cards were removed (`remove_playing_cards` context). |
| 14 | Death | exactly 2 (`min_highlighted = 2`, `max_highlighted = 2`) | The selected card with the greater on-screen x position (`T.x`, i.e. the RIGHTMOST of the two as currently displayed in hand) is the source. The other selected card is turned into an exact copy of it via `copy_card(rightmost, other)` (card.lua:1111-1120, common_events.lua:2156-2181). Rank and value of the cards play NO role; only position does. Because hand order can be rearranged by dragging (or by the sort buttons), the player fully controls which card is the source. What is copied: rank, suit, enhancement, the whole `ability` table (including `perma_bonus` chips and flags such as `played_this_ante`), edition (if the source has no edition, the target LOSES its edition), seal (if the source has no seal, the target LOSES its seal), and the current debuff state. |
| 15 | Temperance | none | Gain the total current sell value of all your jokers (each joker's `sell_cost`, which includes `extra_value` from things like Egg or Gift Card), capped at $50 (card.lua:4167-4175). Always usable; gives $0 with no jokers. Debuffed jokers still count. |
| 16 | The Devil | 1 | Selected card becomes a Gold Card. |
| 17 | The Tower | 1 | Selected card becomes a Stone Card. |
| 18 | The Star | 1 to 3 | Selected cards become Diamonds. |
| 19 | The Moon | 1 to 3 | Selected cards become Clubs. |
| 20 | The Sun | 1 to 3 | Selected cards become Hearts. |
| 21 | Judgement | none | Creates one random Joker with normal rarity odds (70% Common, 25% Uncommon, 5% Rare; never Legendary; common_events.lua:1969-1970). The new joker gets a normal edition roll like any created joker (see Editions). Needs a free joker slot. |
| 22 | The World | 1 to 3 | Selected cards become Spades. |

---

## 2. Planet cards (12). All cost $3. (game.lua:557-568, card.lua:1264-1268, common_events.lua:464-468)

Using a Planet calls `level_up_hand(hand, +1)`. After any level change:

- `level = max(0, level + amount)`
- `mult = max(base_mult + per_level_mult * (level - 1), 1)`
- `chips = max(base_chips + per_level_chips * (level - 1), 0)`

So each level adds exactly the per-level numbers below. Planets are always usable (any state allowed by section 0).

| Planet | Hand | +Chips per level | +Mult per level |
|---|---|---|---|
| Pluto | High Card | +10 | +1 |
| Mercury | Pair | +15 | +1 |
| Uranus | Two Pair | +20 | +1 |
| Venus | Three of a Kind | +20 | +2 |
| Saturn | Straight | +30 | +3 |
| Jupiter | Flush | +15 | +2 |
| Earth | Full House | +25 | +2 |
| Mars | Four of a Kind | +30 | +3 |
| Neptune | Straight Flush | +40 | +4 |
| Planet X (secret) | Five of a Kind | +35 | +3 |
| Ceres (secret) | Flush House | +40 | +4 |
| Eris (secret) | Flush Five | +50 | +3 |

Secret planets have `softlock = true`: they can only appear in shops and packs once that hand has been played at least once this run (`G.GAME.hands[hand].played > 0`, common_events.lua:2008-2011). The three secret hands start hidden (`visible = false`) and become visible when first played (state_events.lua:578).

### Every poker hand: base values and per-level increase (game.lua:2001-2014)

| Hand | Base chips | Base mult | +Chips per level | +Mult per level | Display order (lower = stronger) |
|---|---|---|---|---|---|
| Flush Five | 160 | 16 | 50 | 3 | 1 |
| Flush House | 140 | 14 | 40 | 4 | 2 |
| Five of a Kind | 120 | 12 | 35 | 3 | 3 |
| Straight Flush | 100 | 8 | 40 | 4 | 4 |
| Four of a Kind | 60 | 7 | 30 | 3 | 5 |
| Full House | 40 | 4 | 25 | 2 | 6 |
| Flush | 35 | 4 | 15 | 2 | 7 |
| Straight | 30 | 4 | 30 | 3 | 8 |
| Three of a Kind | 30 | 3 | 20 | 2 | 9 |
| Two Pair | 20 | 2 | 20 | 1 | 10 |
| Pair | 10 | 2 | 15 | 1 | 11 |
| High Card | 5 | 1 | 10 | 1 | 12 |

Example: Flush at level 3 = 35 + 15*2 = 65 chips, 4 + 2*2 = 8 mult.

"Royal Flush" is only a display name for a Straight Flush whose lowest card is 10 or higher; it uses Straight Flush values.

---

## 3. Spectral cards (18). All cost $4. (game.lua:571-588, card.lua:1091-1521)

| # | Card | Targets | Exact effect and side effects |
|---|---|---|---|
| 1 | Familiar | none (needs 2+ cards in hand) | Destroys 1 random card in hand. Then adds 3 new cards to your hand (and deck): each has a random rank among Jack, Queen, King, a random suit, and a random enhancement chosen uniformly from the 7 enhancements other than Stone (Bonus, Mult, Wild, Glass, Steel, Gold, Lucky). No edition, no seal (card.lua:1292-1339, common_events.lua:1927-1942). |
| 2 | Grim | none (needs 2+ in hand) | Destroys 1 random card in hand, adds 2 Aces of random suit, each with a random non-Stone enhancement. |
| 3 | Incantation | none (needs 2+ in hand) | Destroys 1 random card in hand, adds 4 cards of random rank 2 to 10 and random suit, each with a random non-Stone enhancement. |
| 4 | Talisman | 1 | Puts a Gold Seal on the selected card, replacing any existing seal. |
| 5 | Aura | exactly 1, and that card must have NO edition | Gives it Foil (50%), Holographic (35%) or Polychrome (15%). Never Negative. Cannot be used on a card that already has an edition (card.lua:1544-1546). |
| 6 | Wraith | none | Creates a random Rare joker (`_rarity = 0.99`), which also gets a normal edition roll. Then sets money to $0 (subtracts current money, so a negative balance is also raised to $0). Needs a free joker slot. |
| 7 | Sigil | none (needs 2+ in hand) | Every card in hand becomes one single random suit (same suit for all). Ranks, enhancements, editions, seals kept. |
| 8 | Ouija | none (needs 2+ in hand) | Every card in hand becomes one single random rank (same rank for all, suits kept). Then hand size -1 permanently. |
| 9 | Ectoplasm | none | One random joker WITHOUT an edition gets Negative (so +1 joker slot). Eligible pool: any joker with no edition, eternal included. Jokers that already have Foil, Holographic, Polychrome or Negative can never be picked; cannot be used if no editionless joker exists. Side effect: hand size is reduced by `G.GAME.ecto_minus`, which starts at 1 and goes up by 1 after each Ectoplasm used this run. So the 1st Ectoplasm is -1 hand size, the 2nd is -2, the 3rd is -3 (card.lua:1494-1498). Permanent. |
| 10 | Immolate | none (needs 2+ in hand) | Destroys 5 random cards in hand (all of them if fewer than 5), then gain $20. |
| 11 | Ankh | none | Picks one random joker from ALL your jokers (any edition, eternal included) and creates a copy of it. Then destroys every other joker that is not Eternal (the original chosen joker is kept, Eternal jokers are kept). The copy keeps the original's edition, EXCEPT Negative: a Negative original produces a copy with no edition (card.lua:1445-1450). The copy also copies the whole ability table, so stickers (Eternal, Perishable, Rental) and stored values come along. Usable only if you own at least 1 joker and your joker slot limit is more than 1. If your joker slots are full at the moment of use, it shows "No space" and is NOT consumed (card.lua:1581-1587). |
| 12 | Deja Vu | 1 | Red Seal on the selected card (replaces any seal). |
| 13 | Hex | none | One random joker WITHOUT an edition gets Polychrome. Then every other joker that is not Eternal is destroyed (including jokers with editions). Same eligibility as Ectoplasm: jokers with any edition cannot be the target; cannot be used if none is editionless. |
| 14 | Trance | 1 | Blue Seal on the selected card. |
| 15 | Medium | 1 | Purple Seal on the selected card. |
| 16 | Cryptid | 1 | Adds 2 exact copies of the selected card (same rank, suit, enhancement, edition, seal, ability values) to your hand and deck. |
| 17 | The Soul | none | Creates a random Legendary joker (normal edition roll applies). Needs a free joker slot. |
| 18 | Black Hole | none | Levels up all 12 poker hands by 1, including the secret hands even if not yet visible. Always usable. |

How The Soul and Black Hole appear (common_events.lua:2088-2101, card.lua:1732-1774): only in packs. Each card generated for an Arcana pack (as a Tarot) or a Spectral pack has a 0.3% chance (`> 0.997`) to be The Soul. Each card generated for a Celestial pack (as a Planet) or a Spectral pack has a 0.3% chance to be Black Hole. Once one exists in the run (counted via `used_jokers`), it cannot appear again unless you own Showman. They never appear in the shop. Probabilities here are NOT affected by Oops! All 6s.

---

## 4. Vouchers (32). All cost $10. (game.lua:592-624, card.lua:1813-1971)

A voucher is in the shop pool only if: it is unlocked in the profile, not already redeemed this run, every voucher in its `requires` list has been redeemed this run, and it is not already in the shop (common_events.lua:1989-2007). Effects apply immediately when redeemed and are permanent for the run.

Base rates for reference: shop card weights joker 20, tarot 4, planet 4, playing card 0, spectral 0 (game.lua:1901-1905). Interest: $1 per $5 held, capped at `interest_cap/5`, base cap $25 so max $5 (state_events.lua:1191-1202). Base reroll cost $5.

| Voucher | Requires | Exact effect | Unlock condition (profile) |
|---|---|---|---|
| Overstock | none | +1 card slot in the shop (`change_shop_size(1)`). | unlocked |
| Overstock Plus | Overstock | +1 more shop slot. | spend $2500 total in shops |
| Clearance Sale | none | All shop prices 25% off (`discount_percent = 25`). | unlocked |
| Liquidation | Clearance Sale | Discount becomes 50% (sets, not adds). | `run_redeem`, 10 (redeem 10 vouchers) |
| Hone | none | `edition_rate = 2`: Foil, Holo and Polychrome appear twice as often on generated jokers (Negative unchanged). | unlocked |
| Glow Up | Hone | `edition_rate = 4` (4x base). | `have_edition`, 5 |
| Reroll Surplus | none | Reroll cost -$2 (base reroll 5 -> 3; also lowers the current reroll price by 2, minimum 0). | unlocked |
| Reroll Glut | Reroll Surplus | A further -$2. | reroll 100 times total |
| Crystal Ball | none | +1 consumable slot. | unlocked |
| Omen Globe | Crystal Ball | Each card generated in an Arcana pack has a 20% chance (`pseudorandom > 0.8`) to be a Spectral card instead of a Tarot (card.lua:1731). | `c_tarot_reading_used`, 25 |
| Telescope | none | The FIRST card of every Celestial pack is the Planet for your most played hand (highest `played` count among visible hands; ties go to the stronger hand because the list is scanned strongest first with a strict "greater than"). If no hand has been played yet, it is random (card.lua:1737-1752). | unlocked |
| Observatory | Telescope | Every Planet card sitting in your consumable slots gives x1.5 Mult when the played hand is that Planet's hand. Applied in the joker phase, after all jokers (consumables are evaluated after the jokers, left to right) (card.lua:2293-2300, state_events.lua:877-878). | `c_planetarium_used`, 25 |
| Grabber | none | +1 hand per round, permanent (also +1 to the current round). | unlocked |
| Nacho Tong | Grabber | +1 more hand per round. | play 2500 cards total |
| Wasteful | none | +1 discard per round, permanent. | unlocked |
| Recyclomancy | Wasteful | +1 more discard per round. | discard 2500 cards total |
| Tarot Merchant | none | Tarot shop weight becomes 9.6 (from 4) (`4 * 9.6/4`). | unlocked |
| Tarot Tycoon | Tarot Merchant | Tarot shop weight becomes 32. | buy 50 Tarots total |
| Planet Merchant | none | Planet shop weight becomes 9.6. | unlocked |
| Planet Tycoon | Planet Merchant | Planet shop weight becomes 32. | buy 50 Planets total |
| Seed Money | none | Interest cap $50, so max $10 interest per round. | unlocked |
| Money Tree | Seed Money | Interest cap $100, so max $20 per round. | `interest_streak`, 10 (max interest 10 rounds in a row) |
| Blank | none | Does nothing. | unlocked |
| Antimatter | Blank | +1 joker slot. | `blank_redeems`, 10 |
| Magic Trick | none | Playing card shop weight becomes 4 (playing cards can appear in the shop). | unlocked |
| Illusion | Magic Trick | Playing card weight stays 4. Shop playing cards: 40% chance to be Enhanced instead of plain (`> 0.6`); separately 20% chance (`> 0.8`) to get an edition: Polychrome 15%, Holographic 35%, Foil 50% (UI_definitions.lua:772-792). No seal from Illusion in this code. | buy 20 playing cards total |
| Hieroglyph | none | Ante -1 (both the ante counter and the blind ante). Hands per round -1, permanent. | unlocked |
| Petroglyph | Hieroglyph | Ante -1. Discards per round -1, permanent. | `ante_up`, ante 12 |
| Director's Cut | none | You may reroll the Boss Blind once per ante for $10 (needs money - bankrupt limit >= 10) (button_callbacks.lua:2791-2795). | unlocked |
| Retcon | Director's Cut | Boss reroll becomes unlimited, $10 each. | `blind_discoveries`, 25 |
| Paint Brush | none | +1 hand size, permanent. | unlocked |
| Palette | Paint Brush | +1 more hand size. | `min_hand_size`, 5 |

---

## 5. Tags (24). (game.lua:224-249, tag.lua:115-468)

How tags are gained: each Small and Big Blind shows one tag; skipping that blind gives it. The tag is chosen uniformly from all tags whose `min_ante` is not above the current ante and whose `requires` item is discovered in the profile (common_events.lua:1982-1986). The `odds` values in the tag config table are never read anywhere in the code (unused).

Timing hooks (where `apply_to_run` is called):

- "immediate": right after skipping (after the skip is counted), and also every time the blind select screen opens (button_callbacks.lua:2766-2778, game.lua:3290-3295).
- "new_blind_choice": at the same moments, plus after a booster pack is closed and after a boss reroll. Only ONE such tag fires per call (the loop breaks on the first that fires), so several pack tags open their packs one after another.
- "round_start_bonus": at the start of the next round actually played (DRAW_TO_HAND, game.lua:3213-3216).
- Shop hooks fire when the next shop opens.
- "eval": during the cash-out screen of a round, only counted if that round was a Boss Blind.
- "tag_add": whenever another tag is added.

| Tag | min_ante | requires (discovered) | Exact effect and timing |
|---|---|---|---|
| Uncommon Tag | - | - | Next shop: the first shop card generated is a free Uncommon joker (`_rarity = 0.9`). It can then also be modified by an edition tag. |
| Rare Tag | - | Blueprint (j_blueprint) | Next shop: the first shop card generated is a free Rare joker. If you already own every Rare joker (counted by distinct keys), it says "Nope" instead and is used up. |
| Negative Tag | 2 | Negative edition | Next shop: the next shop Joker that has no edition becomes Negative and free. |
| Foil Tag | - | Foil edition | Same, Foil. |
| Holographic Tag | - | Holographic edition | Same, Holographic. |
| Polychrome Tag | - | Polychrome edition | Same, Polychrome. |
| Investment Tag | - | - | Pays $25 in the cash-out of the next Boss Blind you defeat (waits through Small/Big blinds). |
| Voucher Tag | - | - | Next shop: one extra voucher is added to the shop (voucher slots +1). |
| Boss Tag | - | - | Immediately rerolls the upcoming Boss Blind for free. This sets `boss_rerolled = true`, so Director's Cut cannot reroll again this ante (Retcon still can). |
| Standard Tag | 2 | - | Immediately opens a free Mega Standard Pack (5 cards, choose 2). |
| Charm Tag | - | - | Immediately opens a free Mega Arcana Pack (5 cards, choose 2). |
| Meteor Tag | 2 | - | Immediately opens a free Mega Celestial Pack (5 cards, choose 2). |
| Buffoon Tag | 2 | - | Immediately opens a free Mega Buffoon Pack (4 jokers, choose 2). |
| Handy Tag | 2 | - | Immediately: +$1 per hand played this run (`G.GAME.hands_played`, run total). |
| Garbage Tag | 2 | - | Immediately: +$1 per unused discard this run (`G.GAME.unused_discards`, which adds your leftover discards at the end of every won round). |
| Ethereal Tag | 2 | - | Immediately opens a free normal Spectral Pack (2 cards, choose 1). |
| Coupon Tag | - | - | Next shop: every card in the main shop row and every booster pack present when the shop opens costs $0. Vouchers are not included. Cards that appear after a reroll are full price. |
| Double Tag | - | - | When the next tag is gained (other than a Double Tag), you also get a copy of it. A copied Orbital Tag keeps the same poker hand. If you hold several Double Tags, each one adds its own copy. |
| Juggle Tag | - | - | +3 hand size for the next round played only; removed when that round is won (state_events.lua:270). |
| D6 Tag | - | - | Next shop: rerolls start at $0 (then rise by $1 per reroll as usual). The reduced base lasts until the end of the following round. |
| Top-up Tag | 2 | - | Immediately: creates up to 2 Common jokers, only while you have free joker slots. They get normal edition rolls. |
| Skip Tag | - | - | Immediately: +$5 per blind skipped this run. The skip that gave this tag is already counted (`G.GAME.skips` increments before the tag fires). |
| Orbital Tag | 2 | - | Immediately: levels up one poker hand 3 times. The hand is chosen randomly among visible hands when that ante's blind choices are first shown, fixed per ante per blind (Small/Big), and shown on the tag. |
| Economy Tag | - | - | Immediately: gain `min(40, max(0, money))`. So doubles money, max +$40. |

---

## 6. Blinds (game.lua:263-293, blind.lua, functions/common_events.lua:2338-2383)

Blind chip target = `get_blind_amount(ante) * blind.mult * ante_scaling` (blind.lua:107). On normal scaling the base amounts for antes 1 to 8 are 300, 800, 2000, 5000, 11000, 20000, 35000, 50000 (misc_functions.lua:919-930). Small Blind: mult 1, $3. Big Blind: mult 1.5, $4.

### How bosses are chosen (IMPORTANT: differs from the min/max data)

`get_new_boss` (common_events.lua:2338-2383):

- A regular boss is eligible if `boss.min <= max(1, ante)` AND (`ante % win_ante ~= 0` OR `ante < 2`). `win_ante` is 8 normally.
- A showdown (finisher) boss is eligible only if `ante % win_ante == 0` and `ante >= 2`. So finishers appear at ante 8, 16, 24 and so on. Their data says `min = 10, max = 10`, but those numbers are NOT used; only the `showdown` flag is.
- `boss.max` is never read anywhere. Every boss lists max 10, but there is no upper ante limit in practice.
- Among eligible bosses, only those used the fewest times so far this run can be picked (`bosses_used`). A reroll counts the new boss as used.

### Regular bosses (23). Reward $5 unless noted.

| Boss | Chip mult | Reward | min ante | Exact effect from code |
|---|---|---|---|---|
| The Hook | 2 | $5 | 1 | When you play a hand, 2 random cards still in your hand (after the played cards have left) are discarded (fewer if fewer remain). These count as discards for Purple Seals and discard jokers, but do not use up a discard (blind.lua:466-487, state_events.lua:432). |
| The Club | 2 | $5 | 1 | All Clubs debuffed. Uses `is_suit('Clubs', bypass_debuff)`, so Wild Cards are debuffed too (they count as every suit) and, with Smeared Joker, Spades are also Clubs-like. Stone cards are never debuffed by suit bosses. |
| The Goad | 2 | $5 | 1 | All Spades debuffed (same rules as The Club). |
| The Head | 2 | $5 | 1 | All Hearts debuffed (same rules). |
| The Window | 2 | $5 | 1 | All Diamonds debuffed (same rules). |
| The Manacle | 2 | $5 | 1 | -1 hand size for this round (restored on defeat or disable). |
| The Psychic | 2 | $5 | 1 | A hand of fewer than 5 cards is "Not Allowed": it scores 0 (`h_size_ge = 5`). The hand still uses a hand and still counts as played. |
| The Pillar | 2 | $5 | 1 | Debuffs every card with `played_this_ante` set. That flag is set on every card you PLAY (scoring or not) and is cleared only after a Boss Blind is defeated. The debuff check runs at the start of the blind and whenever a card's rank, suit or enhancement changes, so in practice it hits cards played in this ante's Small and Big Blinds. |
| The Mouth | 2 | $5 | 2 | The first hand type you play this round becomes the only allowed type; any other type scores 0. |
| The Fish | 2 | $5 | 2 | Cards drawn after you PLAY a hand come in face down. The opening hand and cards drawn after a discard are face up. |
| The Wall | 4 | $5 | 2 | No effect other than double the normal boss chip target. If disabled, the target is halved. |
| The House | 2 | $5 | 2 | Cards drawn while no hand has been played and no discard used (the whole opening hand) are face down. |
| The Mark | 2 | $5 | 2 | Face cards are drawn face down (`is_face(true)`, so with Pareidolia every card). |
| The Wheel | 2 | $5 | 2 | Each card drawn has a 1 in 7 chance to be face down. |
| The Arm | 2 | $5 | 2 | When you play a hand whose level is above 1, that hand loses 1 level BEFORE it is scored, so it scores at the reduced level. Level 1 hands are unaffected. |
| The Water | 2 | $5 | 2 | Start the round with 0 discards (all current discards removed; restored if disabled). |
| The Needle | 1 | $5 | 2 | Hands are reduced by `(base hands per round - 1)`, normally leaving 1 hand. Chip target is the same as a Small Blind (mult 1). AMBIGUOUS: if your hands this round differ from the base (e.g. a bonus applied before the blind is set), the result may not be exactly 1; the code subtracts `round_resets.hands - 1`. |
| The Flint | 2 | $5 | 2 | Base chips and base mult of the played hand are halved, rounding half up: `mult = max(floor(mult/2 + 0.5), 1)`, `chips = max(floor(chips/2 + 0.5), 0)`. Applied after "before" joker effects (such as hand level-ups) and before any card scores (blind.lua:510-517, state_events.lua:645). |
| The Ox | 2 | $5 | 6 | Playing the "most played hand" sets your money to $0. The hand still scores normally. IMPORTANT: the "most played hand" is NOT live. It is recalculated only when a Boss Blind is won (state_events.lua:129-138): the hand with the highest run-total play count, ties going to the stronger hand. It is then fixed until the next boss is beaten (starts as High Card). The boss text shows which hand it is. |
| The Eye | 2 | $5 | 3 | No hand type may be repeated this round; a repeated type scores 0. |
| The Tooth | 2 | $5 | 3 | Lose $1 for every card played (all played cards, scoring or not). |
| The Plant | 2 | $5 | 4 | All face cards debuffed (`is_face(true)`; with Pareidolia, every card). |
| The Serpent | 2 | $5 | 5 | After the first play or discard of the round, every draw is exactly 3 cards (or fewer if the deck runs out), regardless of how many cards were used or of hand size (state_events.lua:363-368). |

### Showdown bosses (5). Reward $8. Appear only at antes divisible by 8.

| Boss | Chip mult | Reward | Exact effect |
|---|---|---|---|
| Amber Acorn | 2 | $8 | At the start of the blind, all jokers are flipped face down and, if 2 or more, shuffled into a random order. They still work. Flipped back up on defeat or disable. |
| Verdant Leaf | 2 | $8 | Every playing card is debuffed (including cards created during the round) until you sell any Joker; selling a joker disables the boss. |
| Violet Vessel | 6 | $8 | No effect other than a target 3x a normal boss. If disabled, the target is divided by 3. |
| Crimson Heart | 2 | $8 | At the start of the round and after every hand PLAYED (not after discards), all jokers are un-debuffed and one random joker is debuffed. If you have 2 or more jokers, the joker that was debuffed just before is excluded from the pick (the pool is jokers not currently debuffed) (blind.lua:588-600). |
| Cerulean Bell | 2 | $8 | Whenever cards are drawn and no card in hand is force-selected, one random card in hand is force-selected: it stays highlighted, cannot be deselected and must be part of the next play or discard (it takes one of the 5 selection slots). The flag is cleared on every play or discard. |

### Rules common to bosses

- A "Not Allowed" (debuffed) hand scores 0 chips and 0 mult. No card effects, no Glass break rolls. It still costs a hand and still increments that hand's play count (the count is incremented before the debuff check, state_events.lua:574 then 614). Only jokers with a `debuffed_hand` effect react.
- Debuffed playing cards contribute nothing when scored (no chips, mult, enhancement, edition, seal, held effects or end-of-round money). They still count toward forming the poker hand: rank via `get_id` and suit for flushes via `is_suit(..., flush_calc)` both ignore debuff (a debuffed Wild Card falls back to its printed suit for flushes).
- Face-down cards can still be selected and played normally.
- Disabling a boss (for example by Chicot or Luchador) restores Water discards, Needle hands, Manacle hand size (and draws 1 card), un-flips cards and jokers, halves The Wall's target, divides Violet Vessel's target by 3, clears Cerulean Bell's forced card, removes all debuffs, and if your score already meets the target the round ends immediately (blind.lua:356-415).

---

## 7. Enhancements, editions and seals

### Scoring order for one scored card (state_events.lua:648-779, common_events.lua:580-622)

For each scored card, for each trigger (the first plus every retrigger):

1. The card's own effects, in this order: chips (rank chips + enhancement bonus + perma_bonus), +mult, money (Gold Seal and Lucky money), x mult (Glass), then the card's edition (Foil chips, Holographic mult, then Polychrome x mult).
2. Then every joker's per-card effect for that card, left to right.

So a playing card's Polychrome x1.5 applies before jokers' per-card bonuses for that same card.

Retriggers for a scored card: start with 1, add 1 for a Red Seal, then add each joker's repetitions. They simply add up (state_events.lua:666-684). Each trigger re-runs step 1 and 2 completely, including fresh Lucky rolls.

### Enhancements (game.lua:648-655)

| Enhancement | Exact effect | Timing and notes |
|---|---|---|
| Bonus Card | +30 chips (on top of rank chips). | When scored, every trigger. |
| Mult Card | +4 mult. | When scored, every trigger. |
| Wild Card | Counts as every suit (`is_suit` returns true). | Always. Because of this it is debuffed by The Club, Goad, Head and Window. If debuffed, it counts only as its printed suit for flushes. |
| Glass Card | x2 mult when scored, every trigger. | Break chance: 1 in 4, rolled ONCE per hand played, after the whole hand has been scored, for each Glass card in the scoring hand that is not debuffed (state_events.lua:961-963). Retriggers do NOT add rolls. Glass cards held in hand or played but not scoring never roll. No rolls on a "Not Allowed" hand. |
| Steel Card | x1.5 mult while held in hand. | Applied once per hand played, for each Steel card still in hand, left to right, after all scored cards. Retriggered by a Red Seal and by joker retriggers that apply to held cards. Playing a Steel card does nothing. |
| Stone Card | +50 chips. No rank and no suit. | Always scores when played (added to the scoring hand even if not part of the poker hand). Its rank chips are NOT added (only 50 + perma_bonus). Never counts for flushes or straights or pairs (its id is a random negative number), never a face card unless Pareidolia. Not affected by suit bosses. |
| Gold Card | +$3 at end of round if held in hand. | Paid at round end for each Gold card in hand, retriggered by a Red Seal (so $6) (state_events.lua:171-230). Not paid if debuffed. Playing it does nothing. |
| Lucky Card | 1 in 5 chance for +20 mult, and separately 1 in 15 chance for +$20. | Both rolled independently on EVERY trigger when scored (card.lua:984-997, 1068-1089). Retriggers roll again. Nothing when held. |

### Editions (game.lua:658-662, card.lua:387-462)

| Edition | Effect on a playing card (when scored, every trigger) | Effect on a joker | Shop cost extra |
|---|---|---|---|
| Foil | +50 chips | +50 chips, applied just before that joker's own effect | +$2 |
| Holographic | +10 mult | +10 mult, applied just before that joker's own effect | +$3 |
| Polychrome | x1.5 mult | x1.5 mult, applied after that joker's own effect and after any joker-on-joker effects for it | +$5 |
| Negative | (not normally on playing cards) | +1 joker slot. On a consumable: +1 consumable slot. No scoring effect. | +$5 |

Random edition rolls on created jokers (shop, packs, Judgement, Wraith, The Soul, Top-up Tag, and so on) use `poll_edition` with `edition_rate` (1 base, 2 with Hone, 4 with Glow Up) (common_events.lua:2068-2077):

| | Negative | Polychrome | Holographic | Foil | Total |
|---|---|---|---|---|---|
| Base | 0.3% | 0.3% | 1.4% | 2.0% | 4% |
| Hone | 0.3% | 0.9% | 2.8% | 4.0% | 8% |
| Glow Up | 0.3% | 2.1% | 5.6% | 8.0% | 16% |

Guaranteed editions (Aura, The Wheel of Fortune) use a separate table: Polychrome 15%, Holographic 35%, Foil 50%, never Negative, unaffected by Hone and Glow Up.

### Seals (card.lua:1040-1089, 2242-2269)

| Seal | Exact effect | Timing and notes |
|---|---|---|
| Gold Seal | +$3 | When the card is scored, every trigger (so a retriggered Gold Seal pays again). Not when held. |
| Red Seal | Exactly 1 extra trigger (`repetitions = 1`). | Scored cards: always adds 1 retrigger. Held cards: retriggers the card's held effects (Steel x1.5, joker per-card held effects) only if the card actually has a held effect. End of round: retriggers the Gold Card $3 and end-of-round per-card joker effects. Stacks additively with joker retriggers (for example a Red Seal card plus one joker granting 1 retrigger = 1 + 1 + 1 = 3 triggers). Does nothing while the card is debuffed. |
| Blue Seal | Creates the Planet card for the last poker hand you played (`G.GAME.last_hand_played`). | At end of round, if the card is held in hand and you have a free consumable slot. Not if debuffed. |
| Purple Seal | Creates a random Tarot card. | When the card is discarded, if you have a free consumable slot. This includes the forced discards from The Hook. Not if debuffed. |

A card has at most one seal. Talisman, Deja Vu, Trance and Medium replace any existing seal.
