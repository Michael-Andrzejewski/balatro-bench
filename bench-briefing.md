# Balatro Bench: player briefing

You are the player for a Balatro benchmark run. Your job is to play one solo run
of Balatro as well as you can and get as far as possible. Read BENCH.md for the
full rules. This file is the operating manual.

## Your objective, ranked

1. Reach the highest ante you can. Solo Balatro has no lives: if you fail to
   meet a blind's chip requirement, the run is over. So do not die.
2. Beat ante 8 if you can (that is a "win"), then push into Endless mode as far
   as the scaling lets you.
3. Score the biggest single hand you can. This is the tiebreak, so when you have
   a blind comfortably beaten, it is worth spiking one big hand.

## Hard rules (this is a sandbox)

- You may ONLY advance the game through legitimate play. The endpoints `set`,
  `add`, and `load` are disabled by the server in bench mode and will error. Do
  not try to route around that. There is no `mp_eval`; the bridge is not loaded.
- Start the run with exactly: `start` with `deck=RED`, `stake=WHITE`,
  `seed=BENCHMRK`. Nothing else.
- Keep an honest journal (see the bottom). Record your reasoning, not just moves.

## The API

JSON-RPC 2.0 over HTTP POST to `http://127.0.0.1:12346`. Body shape:
`{"jsonrpc":"2.0","id":1,"method":"<name>","params":{...}}`.

From PowerShell:
```
$body = '{"jsonrpc":"2.0","id":1,"method":"gamestate","params":{}}'
Invoke-RestMethod -Uri http://127.0.0.1:12346 -Method Post -Body $body -ContentType 'application/json'
```

Call `gamestate` after every action to see the new state before deciding the
next one. Do not fire blind.

### Endpoints you use

| Method | Params | Valid state | What it does |
| --- | --- | --- | --- |
| `gamestate` | none | any | Full state: `state`, `ante_num`, `round_num`, `money`, `won`, `hands`, `jokers`, `consumables`, `hand`, `shop`, `vouchers`, `packs`, `blinds`, `round`. |
| `start` | `deck`,`stake`,`seed` | MENU | Begin the run. Use RED / WHITE / BENCHMRK. |
| `select` | none | BLIND_SELECT | Play the blind that is on deck. |
| `skip` | none | BLIND_SELECT | Skip a Small or Big blind (not Boss); take its tag instead. |
| `play` | `cards`: array of 0-based hand indices | SELECTING_HAND | Play those cards as a hand. |
| `discard` | `cards`: array of indices | SELECTING_HAND | Discard those cards. |
| `use` | `consumable`: index, `cards`: optional target indices | SELECTING_HAND or SHOP | Use a tarot/planet/spectral. |
| `buy` | one of `card`/`voucher`/`pack`: index | SHOP | Buy from the shop. |
| `pack` | `card`: index, or `skip`: true, plus `cards` for targets | pack opened | Pick (or skip) a card from an opened booster. |
| `sell` | `joker`: index or `consumable`: index | SELECTING_HAND or SHOP | Sell for money. |
| `rearrange` | `hand`/`jokers`/`consumables`: reordered index array | play/shop | Reorder (aim targeted effects, order joker triggers). |
| `reroll` | none | SHOP | Reroll the shop for its current cost. |
| `cash_out` | none | ROUND_EVAL | Collect round rewards. |
| `next_round` | none | SHOP | Leave shop, go to next blind selection. |

### The loop

`start` -> BLIND_SELECT -> `select` (or `skip` small/big) -> SELECTING_HAND ->
`play`/`discard` until the blind's chip goal is met -> ROUND_EVAL -> `cash_out`
-> SHOP -> `buy`/`reroll`/`use`/open packs -> `next_round` -> repeat. Boss blind
every third round (the 3rd of each ante) and cannot be skipped.

Indices are 0-based and refer to the arrays in `gamestate` (`hand.cards`,
`shop.cards`, `packs`, etc.). Re-read `gamestate` before indexing; positions
shift after each action.

## Strategy primer (vanilla Red Deck, White Stake)

This is real Balatro. Jokers are your scaling engine; playing cards alone will
not carry you past the early antes. Core ideas:

- **Commit to a scoring plan by ante 2-3.** Pick a direction your jokers and hand
  levels reinforce: a flush build, a high-card/pair build with big mult jokers, a
  straight build, whatever the shop offers. Coherence beats a pile of unrelated
  jokers.
- **Economy matters.** You earn $1 interest per $5 held, up to +$5 a round. Try
  to sit above $25 when you can. Do not spend to zero early. Red Deck gives you an
  extra discard each round, so lean on discards to dig rather than buying your way
  out.
- **Level your main hand with Planet cards.** Each Planet raises the base chips
  and mult of one poker hand. Planets from booster packs auto-apply; Planets
  bought to a consumable slot must be `use`d. Telescope / Observatory vouchers
  make Celestial packs pay off your most-played hand.
- **Jokers: look for scaling, not flat bonuses.** Flat +mult jokers fade.
  xMult jokers and jokers that grow each round or each hand (ride the bus, green
  joker, supernova, and the multiplicative ones) are what get you to ante 8 and
  beyond. Retrigger jokers multiply everything else.
- **Read the boss blind before you select it** (`blinds.boss.effect`). Some cap
  hands, zero out discards, debuff a suit, or halve chips. Plan the hand you will
  beat it with before you commit.
- **Skipping is a real tool.** Skipping a Small or Big blind skips its chip
  requirement and hands you a tag, but you lose that blind's shop and money. Skip
  only when the tag beats what a shop visit would give you (for example a pack
  tag, an economy tag, or a voucher tag) and you are not starved for jokers.
- **Survive first, spike second.** The headline number is furthest ante, so never
  gamble the run on a blind you could clear safely. Once a blind is in hand, if
  you have hands left, throw your biggest possible hand for the best-single-hand
  tiebreak.

## Journal

Write to `bench-journal-<date>-<model>.md` in this folder as you go:

- The run header: seed, deck, stake, model, Balatro build, date.
- Per ante: what you bought, your scoring plan, the boss and how you beat it, and
  any close calls.
- The best single hand you scored (chips) and what produced it. Track it by
  noting `round.chips` before and after each `play`; the jump is that hand's
  score.
- The final result: ante reached, `won` flag, and what ended the run.

When the run ends, add a row to `bench-results.md`.
