# Rule bot

A Balatro player with zero AI: every decision is a hardcoded rule or a simple
statistic. It drives the same sandboxed balatrobot API as the LLM entrants and
plays as fast as the game can process actions.

## Run

Launch a bench instance first (bench-launch-ai.ps1), then:

```
python rulebot.py --port 12347
```

Defaults: seed BENCHMRK, Red Deck, White Stake. The bot refuses to act unless
the game is at the main menu; pass `--resume` to take over a run in progress.
Logs land in `logs/`, and the last line is the standard bench result format:
`RESULT ante=N best_hand=N won=true|false`.

## How it decides

- **Playing:** enumerates every possible selection of 1 to 5 cards, classifies
  the poker hand, and estimates its score using the live per-hand chips and
  mult from the API (so planet levels are always exact), card chips,
  enhancements, editions, held steel and Baron-style effects, and a table of
  about 40 common vanilla jokers. Plays when the best option beats the pace
  (chips still needed divided by hands left); otherwise discards, chasing
  flush, then full house, then pitching low cards.
- **Bosses:** special handling for The Psychic (must play 5), The Eye (no
  repeat hand types), The Mouth (one hand type), The Ox (avoid the most
  played hand), The Flint (halved base), The Arm (level penalty), Verdant
  Leaf (sells a joker to clear the debuff), Cerulean Bell (forced card always
  included). Face-down cards are excluded from consideration; debuffed cards
  score zero in estimates.
- **Shopping:** priority score parsed from effect text, xMult >> +Mult >
  economy > chips, with a curated bonus table for known-strong jokers
  (Blueprint, Baron, the Duo family). Buys planets that level its most-played
  hand, buys Celestial, Buffoon, and Arcana packs, sells its worst joker when
  a clearly better one appears, keeps a small interest reserve after ante 2,
  rerolls up to twice when joker slots sit empty, and rearranges jokers so
  xMults score last.
- **Packs:** always picks rather than skips (pack-skip has caused a desync
  crash before); skip is only a last-resort fallback.

## Tests

Pure-logic tests, no game contact:

```
python test_rulebot.py
```
