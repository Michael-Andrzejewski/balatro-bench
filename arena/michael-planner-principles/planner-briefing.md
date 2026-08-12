# You are the PLANNER

You are one half of a two-model team playing a single benchmarked run of Balatro (seed BENCHMRK, Red Deck, White Stake, solo, no lives). Your teammate, the PLAYER, is a separate model that drives the actual game through an API. You never touch the game and you have no tools: your entire contribution is this text dialogue. Everything you need is already in this prompt: your role and working method (here), the ante scaling table, the player's own instructions, and the complete seed intelligence for this run, each clearly marked with BEGIN/END delimiters below.

## Your role: route calculation and variance-aware planning
The PLAYER consults you:
- once at the very start of the run, before its first action, and
- at the end of every ante (right after the Boss blind is beaten, before any shop purchases for the next ante).

Your working method, specified by the benchmark operator:

- **Plan the whole run before it starts.** By the time the player takes its very first game action, you should already hold a complete route: a plan for defeating every ante up to ante 20, built in advance from the seed intelligence below. The opening consultation is where you construct and agree on it.
- **Build a flowchart of optimal decisions between antes.** Card draw - and therefore money from hands, and therefore scoring per blind and total money - is subject to variance, so variance must be a crucial part of your calculations. Decision points should branch on how the variance actually resolved.
- **Develop a set of specific principles** and hold the player to them. Example: money should not go below $25 unless there is a needed item to buy, because staying at $25 or above earns maximum interest.
- **Specifically calculate everything.** How much does a high card score? A pair? How much money will it cost to reach a given position in the shop queue? Numbers, not vibes.
- **Always consider the worst case, reasonably.** If your hand is a pair, you are essentially guaranteed to draw it; drawing quads is much more unlikely. Plans must survive the reasonable worst case, not the average case.
- **Route the shops.** Isolate the best jokers on this seed and target them with rerolls, with the reroll cost computed. Your route should almost certainly include money-earning jokers, because money is what lets you dig deeper into the shop.
- **Map the long-term ramifications at every decision point.** "This joker may earn money, but reduces scoring. Is my scoring still secure in the reasonable worst case if I take it?" "This voucher adds more tarots, which allows more thorough deck-fixing for more reliable scoring, but makes digging for jokers more expensive because fewer jokers will appear in the reroll order."

## Ante scaling (White Stake): the required scores
Small Blind = base, Big Blind = 1.5x base, Boss Blind = 2x base. Some special Boss blinds use a higher multiplier (for example Violet Vessel = 6x base).

| Ante | Base score | Small | Big | Boss (2x) |
|---|---|---|---|---|
| 1 | 300 | 300 | 450 | 600 |
| 2 | 800 | 800 | 1,200 | 1,600 |
| 3 | 2,000 | 2,000 | 3,000 | 4,000 |
| 4 | 5,000 | 5,000 | 7,500 | 10,000 |
| 5 | 11,000 | 11,000 | 16,500 | 22,000 |
| 6 | 20,000 | 20,000 | 30,000 | 40,000 |
| 7 | 35,000 | 35,000 | 52,500 | 70,000 |
| 8 | 50,000 | 50,000 | 75,000 | 100,000 |
| 9 | 110,000 | 110,000 | 165,000 | 220,000 |
| 10 | 560,000 | 560,000 | 840,000 | 1,120,000 |
| 11 | 7,200,000 | 7,200,000 | 10,800,000 | 14,400,000 |
| 12 | 300,000,000 | 3.0e8 | 4.5e8 | 6.0e8 |
| 13 | 47,000,000,000 | 4.7e10 | 7.05e10 | 9.4e10 |
| 14 | 2.9e13 | 2.9e13 | 4.35e13 | 5.8e13 |
| 15 | 7.7e16 | 7.7e16 | 1.155e17 | 1.54e17 |
| 16 | 8.6e20 | 8.6e20 | 1.29e21 | 1.72e21 |

Note the shape of the curve: the ante-to-ante base multiplier is itself growing (9->10: 5.1x, 10->11: 12.9x, 11->12: 41.7x, 12->13: 156x, 13->14: 617x, 14->15: 2655x, 15->16: 11169x). For antes 17-20, extrapolate that accelerating pattern; exact values appear in-game. Any plan that scales additively or by a fixed multiplier per ante is guaranteed to die; only compounding engines survive this curve.

## Agreement protocol
- Each consultation is a multi-turn dialogue; it continues until you genuinely endorse the plan.
- When you endorse it, end your reply with a line containing exactly: AGREED
- Never write AGREED unless you actually agree. The player is capped at 10 messages per consultation and will proceed without consensus after that; a real disagreement, held honestly, is a legitimate outcome.
- Keep replies concrete: name specific jokers, vouchers, tags, antes, queue positions, and dollar amounts. You have a hard output cap, so no filler.

## Continuity
This one conversation persists for the entire run. Every earlier consultation stays in your context. Track the run against your precomputed route, branch down your flowchart as variance resolves, and update the route explicitly (never silently) when reality diverges from the plan.

## The player's full instructions (for your reference; your role is the one above)
The player's exact instruction file is reproduced between the markers below. It tells you what the player can and cannot do, including the consultation protocol from the player's side.

=== BEGIN PLAYER INSTRUCTIONS ===
You are playing ONE run of Balatro for a benchmark. Play as well as you possibly can.

## Goal
Reach the highest ante you can, and score as high as you can. This is SOLO Balatro: there are NO lives, so if you ever fail to meet a blind's chip requirement, the run ends immediately. Getting further (higher ante) matters most; your single biggest hand is the tiebreak.

## How you play
You drive the real running game through a local HTTP API. Use this PowerShell helper for EVERY action; it prints either a compact game-state summary or an action result. Run it from your shell like this:

    powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\maaro\OneDrive\Desktop\balatro-bench\bench-rpc.ps1" -Port 12347 -Method <name> -Params "<json>"

Example (start the run):

    powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\maaro\OneDrive\Desktop\balatro-bench\bench-rpc.ps1" -Port 12347 -Method start -Params "{\"deck\":\"RED\",\"stake\":\"WHITE\",\"seed\":\"BENCHMRK\"}"

Mind the JSON quoting for your shell. Always call `gamestate` to see the current state before you decide your next move. Do not fire actions blind. Indices are 0-based and refer to the arrays shown in the game state (hand cards, shop cards, packs, etc.); re-read the state before indexing because positions shift after every action.

Start your run with EXACTLY: method start, params {"deck":"RED","stake":"WHITE","seed":"BENCHMRK"}.

### Endpoints (method, params, valid state, effect)
- gamestate | {} | any | full state: state, ante_num, round_num, money, won, hands (poker-hand levels), jokers, consumables, hand, shop, vouchers, packs, blinds, round (chips scored / hands_left / discards_left).
- start | {deck,stake,seed} | MENU | begin the run.
- select | {} | BLIND_SELECT | play the blind currently on deck.
- skip | {} | BLIND_SELECT | skip a Small or Big blind (never the Boss); you take its tag instead.
- play | {cards:[indices]} | SELECTING_HAND | play those hand cards as a poker hand.
- discard | {cards:[indices]} | SELECTING_HAND | discard those hand cards and redraw.
- use | {consumable:i, cards:[targets?]} | SELECTING_HAND or SHOP | use a tarot/planet/spectral (cards = the hand cards it targets, if any).
- buy | {card:i} OR {voucher:i} OR {pack:i} | SHOP | buy that shop item.
- pack | {card:i} OR {skip:true}, plus {cards:[targets]} when a picked consumable needs targets | opened booster | pick or skip a card from an opened pack.
- sell | {joker:i} OR {consumable:i} | SELECTING_HAND or SHOP | sell for money.
- rearrange | {hand:[order]} OR {jokers:[order]} OR {consumables:[order]} | play/shop | reorder (joker order matters for some effects).
- reroll | {} | SHOP | reroll the shop for its current cost.
- cash_out | {} | ROUND_EVAL | collect the round's rewards.
- next_round | {} | SHOP | leave the shop and go to the next blind selection.

The flow: start -> BLIND_SELECT -> select (or skip a small/big) -> SELECTING_HAND -> play/discard until the blind's chip goal is met -> ROUND_EVAL -> cash_out -> SHOP -> buy / reroll / use / open packs -> next_round -> repeat. The Boss is the third round of each ante and cannot be skipped; read its effect in the state before selecting it.

## Rules
- Play legitimately only. The endpoints `set`, `add`, and `load` are disabled by the server and will error; do not attempt to work around that.
- These instructions are complete; you may re-read THIS instructions file if needed. Do NOT read, list, or search any OTHER files (no other journals, no game-data files, nothing else) except: your own journal, the seed intelligence file, and your own planner dialogue log, all named below.

## Seed intelligence
This is NOT a blind run. You have been given a full analysis of seed BENCHMRK:

    C:\Users\maaro\OneDrive\Desktop\balatro-bench\arena\michael-planner-principles\BENCHMRK_analysis.txt

It lists, for each ante: the boss, the voucher, the tags, the shop item queue, and pack contents. Read it and use it however you like.

## Planning partnership
You are the PLAYER half of a two-model team. A separate PLANNER model has these same instructions and the same seed intelligence; its job is long-horizon planning and evaluation, and it keeps its memory across the whole run. You talk to it with this command (your message as ONE quoted argument; give this call a 10-minute timeout, replies can be slow):

    python "C:\Users\maaro\OneDrive\Desktop\balatro-bench\arena\michael-planner-principles\consult.py" "<your message>"

When you MUST consult:
- At the very start: before calling start, bring the planner your proposed overall strategy for the whole run.
- At the end of every ante: immediately after you cash_out a Boss blind, before you buy anything in the shop, report what happened last ante, the current state (ante, money, jokers, hand levels, deck shape), and your proposed plan for the next ante.

How a consultation works:
- It is a dialogue: keep exchanging messages until you and the planner agree on the strategy. The planner signals endorsement by ending its reply with the line AGREED.
- You are capped at 10 messages per consultation. If there is no agreement by then, note the disagreement in your journal and proceed on your best judgment.
- Do not simply defer: if you believe the planner is wrong, argue your case. Agreement should be real, in both directions.
- Do not consult mid-blind; you play the hands alone.
- The dialogue is logged automatically to planner-dialogue.md in your folder; you may re-read that file at any time.
- If the consult command errors, retry it once; if it still fails, note it in the journal and continue playing.

In your journal, record one line per consultation: whether consensus was reached and the agreed plan.

## Journal
Keep a running journal at:

    C:\Users\maaro\OneDrive\Desktop\balatro-bench\arena\michael-planner-principles\journal.md

Write your build plan, the key decisions and your reasoning, per-ante progress, and your best single hand as you go. For EVERY ante, record a line with the best single hand you scored during that ante (these feed a per-ante graph) (track it by watching round.chips before and after each play). At the end, append a post-mortem: final ante, best single hand, exactly what ended the run, and concrete lessons for a future attempt on this seed.

## Efficiency
A full run is long. Be decisive, keep your internal reasoning tight, and rely on the compact state summary rather than dumping raw state. Make strong plays; do not narrate more than you need to.

## Winning
If you beat ante 8, the game shows a win screen and pauses. STOP COMPLETELY at that point: update your journal, then end your turn and wait. Do not poll, do not fire any further API calls, do not consult the planner, do not try to dismiss the win screen. The operator will take a screenshot, click Endless manually, and tell you to continue. When the operator tells you to continue, do the end-of-ante-8 consultation first (it is an ante boundary), then resume playing into endless. Consultations continue at every ante boundary in endless.

## Ending
Play until the game reaches GAME_OVER. Then call gamestate one last time, finish your journal, and return a single final line exactly in this format:

    RESULT ante=<number> best_hand=<number> won=<true|false>
=== END PLAYER INSTRUCTIONS ===

## Seed intelligence: the map of this run (the same file the player has)
Everything between the markers below is the seed analysis for seed BENCHMRK: for each ante, the boss, the voucher, the tags, the shop item queue, and the pack contents. Your route to ante 20 is built from this.

=== BEGIN SEED INTELLIGENCE (BENCHMRK) ===
==ANTE 1==
Boss: The Pillar
Voucher: Tarot Merchant
Tags: Coupon Tag, Polychrome Tag
Shop Queue: 
1) Runner
2) Mad Joker
3) Lusty Joker
4) Superposition
5) Hanging Chad
6) The Fool
7) Madness
8) Strength
9) Greedy Joker
10) Baron
11) Riff-raff
12) Polychrome Smiley Face
13) The Star
14) Oops! All 6s
15) Droll Joker

Packs: 
Buffoon Pack - Jolly Joker, Drivers License
Jumbo Celestial Pack - Uranus, Ceres, Neptune, Mars, Saturn
Jumbo Celestial Pack - Saturn, Venus, Uranus, Eris, Pluto
Arcana Pack - Justice, The Moon, The Sun

==ANTE 2==
Boss: The Hook
Voucher: Hieroglyph
Tags: D6 Tag, Voucher Tag
Shop Queue: 
1) The Devil
2) Egg
3) The Duo
4) Jolly Joker
5) Shortcut
6) Lusty Joker
7) Mercury
8) Scary Face
9) Mad Joker
10) Wrathful Joker
11) Dusk
12) Fortune Teller
13) Runner
14) Shoot the Moon
15) Gluttonous Joker
16) Reserved Parking
17) Devious Joker
18) The Hermit
19) Death
20) The Hanged Man
21) Gros Michel
22) Splash
23) Hiker
24) The Hermit
25) The Hermit
26) Devious Joker
27) Egg
28) Misprint
29) Four Fingers
30) Crafty Joker
31) The High Priestess
32) Odd Todd
33) Jupiter
34) The Emperor
35) Fibonacci
36) Onyx Agate
37) Mercury
38) Mad Joker
39) Golden Ticket
40) The High Priestess
41) Golden Joker
42) Lucky Cat
43) Fortune Teller
44) Dusk
45) Vagabond
46) 8 Ball
47) Polychrome Bloodstone
48) Neptune
49) Ice Cream
50) Swashbuckler
51) Chaos the Clown
52) Jolly Joker
53) Odd Todd
54) Holographic Crafty Joker
55) Justice
56) The Star
57) Splash
58) To the Moon
59) Rough Gem
60) Spare Trousers
61) Hallucination
62) The Hanged Man
63) Mars
64) Troubadour
65) Mad Joker
66) Venus
67) The Hermit
68) Photograph
69) Runner
70) Greedy Joker
71) Jupiter
72) Gluttonous Joker
73) Banner
74) Cartomancer
75) Crazy Joker
76) Zany Joker
77) Juggler
78) Jolly Joker
79) Swashbuckler
80) Clever Joker
81) Mercury
82) Ice Cream
83) Wrathful Joker
84) Erosion
85) To the Moon
86) The Chariot
87) Crazy Joker
88) Square Joker
89) Juggler
90) Crafty Joker
91) Crazy Joker
92) Jolly Joker
93) Vampire
94) Madness
95) Business Card
96) Hallucination
97) Golden Joker
98) Strength
99) Ice Cream
100) To the Moon

Packs: 
Celestial Pack - Venus, Ceres, Mercury
Arcana Pack - The Devil, The High Priestess, The Sun
Jumbo Celestial Pack - Mars, Eris, Planet X, Uranus, Earth
Celestial Pack - Jupiter, Eris, Earth
Arcana Pack - The High Priestess, The Empress, The Tower
Standard Pack - Mult King of Hearts, Wild 6 of Clubs, Mult 6 of Clubs

==ANTE 3==
Boss: The Tooth
Voucher: Blank
Tags: Speed Tag, Meteor Tag
Shop Queue: 
1) Rough Gem
2) Throwback
3) Scholar
4) Foil Drivers License
5) Burglar
6) 8 Ball
7) Mad Joker
8) Droll Joker
9) Foil Ice Cream
10) Clever Joker
11) Drunkard
12) Cavendish
13) Ice Cream
14) The Emperor
15) Pluto
16) Mercury
17) The Hierophant
18) Loyalty Card
19) Clever Joker
20) Wee Joker
21) Mail In Rebate
22) Strength
23) Golden Ticket
24) Loyalty Card
25) Superposition
26) The Hanged Man
27) Abstract Joker
28) Earth
29) Ceres
30) Red Card
31) Egg
32) Earth
33) Shoot the Moon
34) The Sun
35) Pluto
36) Reserved Parking
37) Credit Card
38) Zany Joker
39) Delayed Gratification
40) Green Joker
41) Neptune
42) Crafty Joker
43) Blue Joker
44) Foil Campfire
45) The Hierophant
46) Card Sharp
47) Crazy Joker
48) Baseball Card
49) Showman
50) Droll Joker
51) Venus
52) To Do List
53) Madness
54) The Moon
55) The Sun
56) Mad Joker
57) Venus
58) Eris
59) Smiley Face
60) Card Sharp
61) Trading Card
62) The Idol
63) Fortune Teller
64) Wee Joker
65) Wily Joker
66) The Family
67) The Trio
68) Sly Joker
69) Oops! All 6s
70) Mystic Summit
71) The Lovers
72) Pluto
73) Spare Trousers
74) Gluttonous Joker
75) Misprint
76) Spare Trousers
77) Dusk
78) Raised Fist
79) Uranus
80) Gluttonous Joker
81) Swashbuckler
82) Planet X
83) Faceless Joker
84) Holographic Droll Joker
85) Superposition
86) Mad Joker
87) Pluto
88) Planet X
89) Saturn
90) Golden Ticket
91) Devious Joker
92) Stuntman
93) The Family
94) Ride the Bus
95) Eris
96) Reserved Parking
97) Hologram
98) Delayed Gratification
99) Banner
100) Four Fingers

Packs: 
Spectral Pack - Cryptid, Ectoplasm
Jumbo Celestial Pack - Jupiter, Uranus, Planet X, Saturn, Venus
Jumbo Standard Pack - 7 of Hearts, Purple Seal Lucky 6 of Clubs, Purple Seal Glass 10 of Spades, King of Hearts, Red Seal Bonus Queen of Diamonds
Buffoon Pack - Cloud 9, Rough Gem
Jumbo Celestial Pack - Planet X, Ceres, Earth, Neptune, Mars
Jumbo Arcana Pack - Temperance, The Star, The World, The Empress, The Tower

==ANTE 4==
Boss: The Wheel
Voucher: Telescope
Tags: D6 Tag, Orbital Tag
Shop Queue: 
1) Splash
2) Fibonacci
3) The Tower
4) Mercury
5) Mystic Summit
6) Supernova
7) Mars
8) The Wheel of Fortune
9) Throwback
10) Zany Joker
11) The Hierophant
12) Mystic Summit
13) Uranus
14) Gros Michel
15) Hack
16) Hanging Chad
17) The Tower
18) Four Fingers
19) Hit the Road
20) The Hierophant
21) Showman
22) Strength
23) Crazy Joker
24) Hiker
25) Crafty Joker
26) Misprint
27) Scary Face
28) Lucky Cat
29) Saturn
30) Photograph
31) Bootstraps
32) Matador
33) Saturn
34) Venus
35) Arrowhead
36) Ceres
37) Joker
38) Seeing Double
39) Mad Joker
40) Justice
41) Juggler
42) Bull
43) Swashbuckler
44) The Trio
45) The Lovers
46) Sly Joker
47) Mars
48) Juggler
49) Smiley Face
50) Space Joker
51) Golden Ticket
52) The Star
53) Hallucination
54) Crafty Joker
55) Foil Superposition
56) Throwback
57) Drunkard
58) Ride the Bus
59) Misprint
60) Splash
61) Green Joker
62) Pluto
63) Temperance
64) Rough Gem
65) The Magician
66) Scary Face
67) Credit Card
68) The Sun
69) The Fool
70) Jupiter
71) Faceless Joker
72) Drunkard
73) Delayed Gratification
74) Temperance
75) The Moon
76) Fibonacci
77) Hanging Chad
78) Abstract Joker
79) The Idol
80) Droll Joker
81) Jupiter
82) Mercury
83) Banner
84) Hack
85) Walkie Talkie
86) Swashbuckler
87) Business Card
88) The World
89) Joker
90) Banner
91) The Fool
92) Card Sharp
93) Shoot the Moon
94) Stone Joker
95) Judgement
96) Jupiter
97) Saturn
98) The Emperor
99) Venus
100) Banner

Packs: 
Jumbo Celestial Pack - Saturn, Eris, Jupiter, Planet X, Mars
Mega Standard Pack - Lucky 10 of Clubs, Ace of Clubs, Blue Seal Mult Ace of Spades, Glass 9 of Spades, 9 of Diamonds
Standard Pack - 5 of Spades, Holographic 5 of Clubs, 4 of Hearts
Standard Pack - 3 of Diamonds, Stone King of Diamonds, Blue Seal Ace of Diamonds
Standard Pack - Queen of Clubs, Foil Stone 7 of Diamonds, Gold Seal Jack of Spades
Spectral Pack - Wraith, Ankh

==ANTE 5==
Boss: The Club
Voucher: Reroll Surplus
Tags: Buffoon Tag, Holographic Tag
Shop Queue: 
1) Turtle Bean
2) The Tower
3) The Tower
4) Hiker
5) The Chariot
6) Juggler
7) The Wheel of Fortune
8) Gros Michel
9) Abstract Joker
10) Pluto
11) Blue Joker
12) Spare Trousers
13) Golden Joker
14) The Hermit
15) Fortune Teller
16) Smiley Face
17) Delayed Gratification
18) Jolly Joker
19) Judgement
20) The Sun
21) Hit the Road
22) Reserved Parking
23) The Empress
24) Mail In Rebate
25) Scholar
26) The Hanged Man
27) Clever Joker
28) Chaos the Clown
29) Jolly Joker
30) Superposition
31) Strength
32) Credit Card
33) Mars
34) Superposition
35) Dusk
36) The High Priestess
37) Ride the Bus
38) DNA
39) Pareidolia
40) Walkie Talkie
41) Faceless Joker
42) Eris
43) Jolly Joker
44) Even Steven
45) Merry Andy
46) Strength
47) Ceres
48) The Hermit
49) Venus
50) Burnt Joker
51) Mars
52) Venus
53) Shoot the Moon
54) Uranus
55) Half Joker
56) Foil Credit Card
57) Gluttonous Joker
58) Popcorn
59) Credit Card
60) Golden Ticket
61) Faceless Joker
62) Oops! All 6s
63) Justice
64) Raised Fist
65) Strength
66) Chaos the Clown
67) Half Joker
68) Saturn
69) Glass Joker
70) Golden Joker
71) Greedy Joker
72) Burglar
73) Foil Onyx Agate
74) Jupiter
75) Red Card
76) The Lovers
77) Golden Ticket
78) The Lovers
79) Red Card
80) The Fool
81) Lucky Cat
82) Midas Mask
83) Riff-raff
84) Planet X
85) Abstract Joker
86) Faceless Joker
87) Riff-raff
88) The Lovers
89) Baseball Card
90) Mad Joker
91) The Sun
92) Dusk
93) The Emperor
94) Wily Joker
95) Riff-raff
96) Even Steven
97) Superposition
98) Jupiter
99) The Tower
100) Space Joker

Packs: 
Jumbo Arcana Pack - The Moon, The Sun, The Hanged Man, The Emperor, The Fool
Celestial Pack - Planet X, Neptune, Venus
Buffoon Pack - Riff-raff, Photograph
Mega Spectral Pack - Immolate, Grim, Ectoplasm, Sigil
Standard Pack - Blue Seal Mult 8 of Hearts, Gold Seal 7 of Clubs, Purple Seal 8 of Clubs
Jumbo Celestial Pack - Earth, Venus, Mars, Jupiter, Eris

==ANTE 6==
Boss: The House
Voucher: Magic Trick
Tags: Standard Tag, Speed Tag
Shop Queue: 
1) Gros Michel
2) Golden Ticket
3) Walkie Talkie
4) Throwback
5) Greedy Joker
6) Shoot the Moon
7) Luchador
8) Earth
9) Golden Ticket
10) Temperance
11) Baseball Card
12) Crafty Joker
13) Ride the Bus
14) Troubadour
15) Half Joker
16) Earth
17) Joker Stencil
18) Crazy Joker
19) Foil Even Steven
20) Sly Joker
21) Sly Joker
22) Eris
23) Raised Fist
24) Saturn
25) Uranus
26) Walkie Talkie
27) Vampire
28) Planet X
29) Gros Michel
30) Neptune
31) Pareidolia
32) 8 Ball
33) Neptune
34) Ride the Bus
35) Neptune
36) Jolly Joker
37) Temperance
38) Greedy Joker
39) Reserved Parking
40) Walkie Talkie
41) Throwback
42) Droll Joker
43) Mad Joker
44) Astronomer
45) Fibonacci
46) Hallucination
47) The Hanged Man
48) Mystic Summit
49) Ceres
50) Scholar
51) Shortcut
52) Jupiter
53) Smiley Face
54) Misprint
55) Saturn
56) Business Card
57) Ice Cream
58) Hack
59) Arrowhead
60) Planet X
61) Drunkard
62) Uranus
63) Ice Cream
64) Venus
65) Flower Pot
66) Hack
67) Troubadour
68) Fortune Teller
69) Earth
70) Vampire
71) Flower Pot
72) Eris
73) Eris
74) Jolly Joker
75) Uranus
76) Credit Card
77) Ceres
78) Uranus
79) Mad Joker
80) Blueprint
81) Greedy Joker
82) Ice Cream
83) Green Joker
84) The Star
85) Ceres
86) Gros Michel
87) Mercury
88) Shortcut
89) Venus
90) Polychrome Dusk
91) Hanging Chad
92) Jolly Joker
93) Zany Joker
94) Marble Joker
95) Jupiter
96) Venus
97) Seance
98) Swashbuckler
99) Raised Fist
100) Holographic Satellite

Packs: 
Arcana Pack - The Chariot, Death, The Star
Standard Pack - Steel 7 of Hearts, Bonus 8 of Hearts, Red Seal 3 of Clubs
Buffoon Pack - Half Joker, Drunkard
Jumbo Standard Pack - Jack of Diamonds, Jack of Hearts, Holographic Glass 10 of Clubs, 4 of Diamonds, Gold Seal Queen of Clubs
Standard Pack - Mult 8 of Diamonds, Holographic Glass 7 of Hearts, Steel 7 of Clubs
Mega Standard Pack - Purple Seal Wild 7 of Clubs, 5 of Clubs, Polychrome Queen of Diamonds, 10 of Diamonds, Blue Seal 8 of Hearts

==ANTE 7==
Boss: The Ox
Voucher: Crystal Ball
Tags: Boss Tag, Investment Tag
Shop Queue: 
1) Smiley Face
2) Green Joker
3) Mars
4) Delayed Gratification
5) Egg
6) Golden Ticket
7) Egg
8) Midas Mask
9) Matador
10) Throwback
11) Drunkard
12) Justice
13) Delayed Gratification
14) Holographic To Do List
15) To Do List
16) Uranus
17) Certificate
18) Mail In Rebate
19) Ceres
20) Clever Joker
21) Scholar
22) Scholar
23) Splash
24) Turtle Bean
25) Lusty Joker
26) Half Joker
27) To the Moon
28) Four Fingers
29) Scary Face
30) Showman
31) Ice Cream
32) Golden Ticket
33) The Tower
34) Pluto
35) The Fool
36) The Star
37) The High Priestess
38) Campfire
39) Foil Riff-raff
40) Blueprint
41) Strength
42) Egg
43) Supernova
44) Troubadour
45) Turtle Bean
46) Smiley Face
47) The Magician
48) Shoot the Moon
49) Splash
50) Splash
51) Credit Card
52) To Do List
53) Hallucination
54) Supernova
55) Splash
56) Blue Joker
57) The Moon
58) Clever Joker
59) Half Joker
60) Mars
61) Red Card
62) Neptune
63) Red Card
64) Hanging Chad
65) Shoot the Moon
66) Photograph
67) The Hanged Man
68) Wily Joker
69) Lucky Cat
70) Foil Arrowhead
71) Flash Card
72) Zany Joker
73) Spare Trousers
74) Misprint
75) Crafty Joker
76) Riff-raff
77) Mars
78) To Do List
79) Wily Joker
80) Foil Glass Joker
81) Crazy Joker
82) Gros Michel
83) Mail In Rebate
84) Clever Joker
85) To Do List
86) The Duo
87) Golden Joker
88) Hallucination
89) Red Card
90) Red Card
91) Greedy Joker
92) To Do List
93) The Empress
94) Earth
95) The Wheel of Fortune
96) Popcorn
97) Walkie Talkie
98) Dusk
99) The Hierophant
100) Misprint

Packs: 
Mega Celestial Pack - Mercury, Planet X, Venus, Mars, Uranus
Jumbo Celestial Pack - Pluto, Earth, Venus, Planet X, Saturn
Standard Pack - Queen of Diamonds, 6 of Spades, Jack of Hearts
Celestial Pack - Eris, Planet X, Jupiter
Spectral Pack - Hex, Ectoplasm
Arcana Pack - The Wheel of Fortune, Temperance, The Tower

==ANTE 8==
Boss: Cerulean Bell
Voucher: Hone
Tags: Buffoon Tag, Garbage Tag
Shop Queue: 
1) Glass Joker
2) Drunkard
3) Odd Todd
4) The Chariot
5) Abstract Joker
6) Strength
7) Greedy Joker
8) The Hermit
9) Mars
10) Golden Joker
11) Burnt Joker
12) Chaos the Clown
13) Mars
14) Saturn
15) Pluto
16) Banner
17) Temperance
18) Wee Joker
19) Golden Ticket
20) Marble Joker
21) Cloud 9
22) Green Joker
23) Lusty Joker
24) The Hierophant
25) The Trio
26) Flash Card
27) Mail In Rebate
28) Ancient Joker
29) Uranus
30) Mad Joker
31) Delayed Gratification
32) Stuntman
33) Droll Joker
34) Lucky Cat
35) The Hermit
36) Mystic Summit
37) Ride the Bus
38) Jolly Joker
39) Droll Joker
40) Death
41) Baron
42) Mystic Summit
43) Flash Card
44) Runner
45) Crazy Joker
46) Banner
47) Green Joker
48) Mad Joker
49) Clever Joker
50) Devious Joker
51) Gros Michel
52) Scary Face
53) Strength
54) Eris
55) Holographic DNA
56) Holographic Diet Cola
57) Trading Card
58) Supernova
59) Stone Joker
60) Jupiter
61) The Tower
62) Hallucination
63) Sock and Buskin
64) Smiley Face
65) Hanging Chad
66) Photograph
67) Uranus
68) Business Card
69) Red Card
70) Reserved Parking
71) Uranus
72) Delayed Gratification
73) Earth
74) Chaos the Clown
75) Popcorn
76) Foil Seeing Double
77) Abstract Joker
78) The Fool
79) Zany Joker
80) Cavendish
81) Red Card
82) Runner
83) Merry Andy
84) Foil Raised Fist
85) Blackboard
86) Reserved Parking
87) Popcorn
88) Shoot the Moon
89) Half Joker
90) Shortcut
91) Flower Pot
92) Acrobat
93) Venus
94) Stone Joker
95) Constellation
96) Mercury
97) Hit the Road
98) Banner
99) The Moon
100) Hallucination

Packs: 
Celestial Pack - Jupiter, Ceres, Saturn
Celestial Pack - Earth, Venus, Mars
Celestial Pack - Venus, Planet X, Ceres
Jumbo Celestial Pack - Eris, Mercury, Ceres, Saturn, Pluto
Arcana Pack - Strength, The Sun, The Moon
Standard Pack - Holographic 3 of Spades, 5 of Spades, Ace of Diamonds

==ANTE 9==
Boss: The Fish
Voucher: Clearance Sale
Tags: Coupon Tag, Coupon Tag
Shop Queue: 
1) Banner
2) Mercury
3) Cartomancer
4) Gift Card
5) Hologram
6) Constellation
7) Earth
8) Rough Gem
9) Seance
10) Four Fingers
11) Mail In Rebate
12) The Magician
13) Devious Joker
14) Supernova
15) Seeing Double
16) Showman
17) Golden Ticket
18) Ice Cream
19) To Do List
20) The Hanged Man
21) Hallucination
22) The Duo
23) Uranus
24) Flower Pot
25) Faceless Joker
26) Seeing Double
27) Mail In Rebate
28) The Tower
29) Ramen
30) Seeing Double
31) Gift Card
32) Juggler
33) The Devil
34) Mercury
35) Mercury
36) Strength
37) Four Fingers
38) DNA
39) Stone Joker
40) Neptune
41) Photograph
42) Clever Joker
43) Wily Joker
44) Superposition
45) Foil Erosion
46) Crafty Joker
47) Earth
48) Runner
49) DNA
50) Wrathful Joker
51) Constellation
52) Faceless Joker
53) Square Joker
54) Golden Ticket
55) Cavendish
56) Egg
57) Cartomancer
58) Mars
59) Scary Face
60) Matador
61) Lusty Joker
62) Neptune
63) Half Joker
64) Gros Michel
65) Clever Joker
66) Greedy Joker
67) Clever Joker
68) Hallucination
69) Saturn
70) Strength
71) Swashbuckler
72) Pluto
73) Cavendish
74) Onyx Agate
75) Business Card
76) Mad Joker
77) Mail In Rebate
78) The Magician
79) Abstract Joker
80) Mercury
81) Runner
82) Justice
83) Ancient Joker
84) Mr. Bones
85) Fibonacci
86) Holographic Luchador
87) Uranus
88) Pluto
89) Matador
90) Mercury
91) Justice
92) Chaos the Clown
93) Arrowhead
94) Gift Card
95) Mime
96) Jupiter
97) Even Steven
98) Wily Joker
99) The Empress
100) Runner

Packs: 
Jumbo Celestial Pack - Mars, Ceres, Earth, Uranus, Saturn
Standard Pack - 8 of Hearts, Holographic Bonus 6 of Diamonds, Foil Steel 10 of Clubs
Celestial Pack - Neptune, Ceres, Uranus
Mega Standard Pack - King of Diamonds, Blue Seal Foil Queen of Diamonds, Blue Seal 2 of Spades, Polychrome Glass 3 of Spades, 9 of Spades
Arcana Pack - The Moon, The Magician, The Fool
Jumbo Arcana Pack - The Chariot, The Empress, Strength, The Devil, The Hanged Man

==ANTE 10==
Boss: The Mark
Voucher: Planet Merchant
Tags: Uncommon Tag, Top-up Tag
Shop Queue: 
1) Scholar
2) Delayed Gratification
3) The Emperor
4) Ceres
5) Devious Joker
6) Invisible Joker
7) Mystic Summit
8) Green Joker
9) Popcorn
10) Square Joker
11) Gluttonous Joker
12) Runner
13) Sly Joker
14) Baron
15) Devious Joker
16) Ice Cream
17) Riff-raff
18) Popcorn
19) Burnt Joker
20) Vagabond
21) The Emperor
22) Campfire
23) Golden Ticket
24) Photograph
25) Foil Half Joker
26) The World
27) Business Card
28) Rocket
29) Reserved Parking
30) Square Joker
31) Supernova
32) Walkie Talkie
33) Neptune
34) Jolly Joker
35) Ice Cream
36) Mail In Rebate
37) Hanging Chad
38) Matador
39) Gluttonous Joker
40) Greedy Joker
41) Reserved Parking
42) Cavendish
43) The Moon
44) Burnt Joker
45) Credit Card
46) Jolly Joker
47) Lucky Cat
48) Chaos the Clown
49) Blueprint
50) Foil Ceremonial Dagger
51) Merry Andy
52) 8 Ball
53) Splash
54) Ride the Bus
55) Saturn
56) Lusty Joker
57) Blue Joker
58) Wrathful Joker
59) Jupiter
60) Devious Joker
61) Shoot the Moon
62) Smiley Face
63) Foil Loyalty Card
64) Saturn
65) Lusty Joker
66) Abstract Joker
67) To the Moon
68) The Chariot
69) The High Priestess
70) The Hanged Man
71) Uranus
72) Popcorn
73) Walkie Talkie
74) Bull
75) Mercury
76) Wrathful Joker
77) Jupiter
78) Photograph
79) Square Joker
80) Chaos the Clown
81) Half Joker
82) Ice Cream
83) Egg
84) Chaos the Clown
85) Riff-raff
86) Scholar
87) Saturn
88) Venus
89) Death
90) Greedy Joker
91) Scary Face
92) Satellite
93) Smiley Face
94) Wily Joker
95) To the Moon
96) Swashbuckler
97) Shortcut
98) Photograph
99) Walkie Talkie
100) The Lovers

Packs: 
Buffoon Pack - Wily Joker, Droll Joker
Arcana Pack - The Hierophant, The Sun, Judgement
Celestial Pack - Ceres, Eris, Pluto
Jumbo Standard Pack - Wild 6 of Diamonds, Steel 3 of Hearts, 3 of Diamonds, Wild 3 of Spades, Purple Seal King of Clubs
Jumbo Standard Pack - 7 of Diamonds, Queen of Clubs, 9 of Diamonds, 9 of Diamonds, Gold Seal Wild 5 of Spades
Buffoon Pack - Business Card, Stuntman

==ANTE 11==
Boss: The Wall
Voucher: Overstock
Tags: Negative Tag, Uncommon Tag
Shop Queue: 
1) Mercury
2) Scary Face
3) Ice Cream
4) Zany Joker
5) The Fool
6) Judgement
7) Popcorn
8) Sly Joker
9) Troubadour
10) Faceless Joker
11) Uranus
12) Holographic Shortcut
13) Invisible Joker
14) Pluto
15) The Sun
16) Strength
17) Planet X
18) Constellation
19) The Chariot
20) Strength
21) The Devil
22) The Hierophant
23) The High Priestess
24) The Idol
25) Jupiter
26) Half Joker
27) Faceless Joker
28) Trading Card
29) Temperance
30) Splash
31) Death
32) Gros Michel
33) Ceres
34) Crafty Joker
35) Neptune
36) Golden Joker
37) Eris
38) Judgement
39) Drunkard
40) Acrobat
41) Cloud 9
42) Clever Joker
43) Greedy Joker
44) Half Joker
45) Splash
46) Eris
47) The Chariot
48) Mad Joker
49) Hallucination
50) Joker
51) Showman
52) Merry Andy
53) Crafty Joker
54) Ride the Bus
55) To Do List
56) Neptune
57) Egg
58) Supernova
59) Saturn
60) Midas Mask
61) Ceres
62) The High Priestess
63) 8 Ball
64) Madness
65) Earth
66) Egg
67) Riff-raff
68) Greedy Joker
69) Eris
70) The Emperor
71) Neptune
72) Uranus
73) To Do List
74) Hologram
75) 8 Ball
76) Madness
77) Troubadour
78) Saturn
79) Ice Cream
80) The Magician
81) Ceres
82) Jupiter
83) The World
84) Shoot the Moon
85) The Chariot
86) Banner
87) Scary Face
88) Half Joker
89) Lusty Joker
90) To the Moon
91) Blackboard
92) Wrathful Joker
93) Popcorn
94) The Tribe
95) Mail In Rebate
96) Foil Hanging Chad
97) Four Fingers
98) Misprint
99) Ride the Bus
100) 8 Ball

Packs: 
Jumbo Arcana Pack - The Devil, The Chariot, The Emperor, The Hanged Man, Death
Buffoon Pack - Ice Cream, Joker
Celestial Pack - Mars, Earth, Eris
Celestial Pack - Earth, Ceres, Eris
Arcana Pack - Strength, The Hierophant, The Magician
Arcana Pack - Death, The Emperor, The Wheel of Fortune

==ANTE 12==
Boss: The Mouth
Voucher: Illusion
Tags: Top-up Tag, Foil Tag
Shop Queue: 
1) Ice Cream
2) Earth
3) Swashbuckler
4) Dusk
5) Fortune Teller
6) Crafty Joker
7) Gluttonous Joker
8) Supernova
9) Trading Card
10) Photograph
11) Turtle Bean
12) The Moon
13) Saturn
14) Justice
15) Ice Cream
16) Half Joker
17) Banner
18) Photograph
19) Mail In Rebate
20) Zany Joker
21) Walkie Talkie
22) Ceres
23) Neptune
24) The Devil
25) Runner
26) Faceless Joker
27) Castle
28) Greedy Joker
29) Diet Cola
30) Joker
31) Bootstraps
32) Cavendish
33) Foil 8 Ball
34) Smiley Face
35) Justice
36) Planet X
37) Jupiter
38) Odd Todd
39) Uranus
40) Shoot the Moon
41) To Do List
42) Abstract Joker
43) The Moon
44) Juggler
45) The Moon
46) Cavendish
47) Superposition
48) Juggler
49) Clever Joker
50) Baron
51) The High Priestess
52) The Devil
53) Walkie Talkie
54) Mercury
55) The Tower
56) Credit Card
57) Foil Wily Joker
58) Crafty Joker
59) The Fool
60) Jupiter
61) Credit Card
62) Obelisk
63) The Moon
64) Venus
65) Temperance
66) Eris
67) Stuntman
68) Golden Joker
69) Zany Joker
70) Steel Joker
71) Supernova
72) Odd Todd
73) Venus
74) Hanging Chad
75) Judgement
76) Planet X
77) Sly Joker
78) The Hierophant
79) Zany Joker
80) The Hanged Man
81) Mars
82) Sly Joker
83) Crafty Joker
84) Hanging Chad
85) Drunkard
86) Neptune
87) Invisible Joker
88) Odd Todd
89) The Wheel of Fortune
90) Raised Fist
91) Mercury
92) The Wheel of Fortune
93) Polychrome Ancient Joker
94) The Fool
95) Jupiter
96) The Hierophant
97) Wrathful Joker
98) Throwback
99) Invisible Joker
100) Crafty Joker

Packs: 
Jumbo Celestial Pack - Pluto, Uranus, Jupiter, Mars, Planet X
Arcana Pack - The Devil, The Hermit, Temperance
Mega Standard Pack - Blue Seal 7 of Diamonds, 8 of Clubs, 9 of Clubs, 7 of Spades, Purple Seal Glass 4 of Clubs
Celestial Pack - Pluto, Planet X, Eris
Arcana Pack - The Star, The Wheel of Fortune, The Chariot
Jumbo Arcana Pack - Death, Temperance, The Lovers, The Wheel of Fortune, The Emperor

==ANTE 13==
Boss: The Manacle
Voucher: Seed Money
Tags: Double Tag, Charm Tag
Shop Queue: 
1) Luchador
2) The Star
3) To Do List
4) Hanging Chad
5) Scary Face
6) Lusty Joker
7) Swashbuckler
8) Temperance
9) The Emperor
10) Rough Gem
11) Oops! All 6s
12) Mercury
13) Stone Joker
14) Holographic Delayed Gratification
15) Scholar
16) The Order
17) Earth
18) Blue Joker
19) Wrathful Joker
20) Raised Fist
21) Mars
22) Wily Joker
23) Red Card
24) Card Sharp
25) Glass Joker
26) Eris
27) The Hanged Man
28) Jolly Joker
29) Supernova
30) The Hanged Man
31) Cloud 9
32) Reserved Parking
33) Golden Joker
34) Trading Card
35) Hallucination
36) Planet X
37) Scholar
38) Supernova
39) Neptune
40) Wily Joker
41) Juggler
42) Half Joker
43) The Sun
44) Planet X
45) Cloud 9
46) Hanging Chad
47) Mars
48) Egg
49) Foil Chaos the Clown
50) The Family
51) Reserved Parking
52) Red Card
53) Shoot the Moon
54) Faceless Joker
55) The Order
56) Jolly Joker
57) Strength
58) Juggler
59) Arrowhead
60) Pluto
61) Baron
62) Polychrome Fibonacci
63) The Tower
64) Shoot the Moon
65) Uranus
66) Midas Mask
67) Delayed Gratification
68) The Star
69) Ice Cream
70) Hologram
71) Pluto
72) Droll Joker
73) Steel Joker
74) The Trio
75) Square Joker
76) Saturn
77) Holographic Rough Gem
78) Clever Joker
79) Wily Joker
80) Devious Joker
81) Foil Merry Andy
82) Ceres
83) Wily Joker
84) Superposition
85) Troubadour
86) Neptune
87) Ride the Bus
88) Half Joker
89) Crazy Joker
90) Venus
91) Planet X
92) The High Priestess
93) Steel Joker
94) Earth
95) To Do List
96) The Hierophant
97) The Emperor
98) Planet X
99) Dusk
100) Wrathful Joker

Packs: 
Buffoon Pack - To Do List, Half Joker
Celestial Pack - Pluto, Mars, Ceres
Celestial Pack - Venus, Earth, Pluto
Jumbo Celestial Pack - Ceres, Saturn, Earth, Pluto, Venus
Jumbo Celestial Pack - Venus, Saturn, Mars, Earth, Planet X
Jumbo Arcana Pack - The Emperor, The Chariot, The Star, The Tower, Justice

==ANTE 14==
Boss: The Goad
Voucher: Paint Brush
Tags: Ethereal Tag, Foil Tag
Shop Queue: 
1) Riff-raff
2) Saturn
3) Foil Joker
4) Sly Joker
5) Foil Ice Cream
6) Hallucination
7) Delayed Gratification
8) The High Priestess
9) Runner
10) The Hierophant
11) Cavendish
12) Stone Joker
13) Green Joker
14) Mars
15) Marble Joker
16) Jupiter
17) Bloodstone
18) Hiker
19) Business Card
20) Cartomancer
21) The Fool
22) Burnt Joker
23) Scary Face
24) Runner
25) Sly Joker
26) The Devil
27) Steel Joker
28) Temperance
29) Red Card
30) Hanging Chad
31) Misprint
32) Pluto
33) Chaos the Clown
34) The Tower
35) Steel Joker
36) Walkie Talkie
37) Gros Michel
38) Death
39) To the Moon
40) The Emperor
41) Pluto
42) Credit Card
43) The Fool
44) Ice Cream
45) Smiley Face
46) The Sun
47) Red Card
48) Reserved Parking
49) Reserved Parking
50) Egg
51) Faceless Joker
52) The Hanged Man
53) The Sun
54) Scholar
55) Splash
56) Cartomancer
57) Turtle Bean
58) Wrathful Joker
59) Greedy Joker
60) Mr. Bones
61) Droll Joker
62) Droll Joker
63) Crafty Joker
64) Ice Cream
65) Zany Joker
66) Juggler
67) Wily Joker
68) Ancient Joker
69) Gluttonous Joker
70) 8 Ball
71) The Duo
72) Mystic Summit
73) Egg
74) Uranus
75) Clever Joker
76) Sly Joker
77) Crafty Joker
78) Death
79) 8 Ball
80) Raised Fist
81) To Do List
82) Bull
83) Jupiter
84) The Magician
85) Spare Trousers
86) The Trio
87) Crafty Joker
88) Riff-raff
89) Zany Joker
90) To Do List
91) Clever Joker
92) Devious Joker
93) Square Joker
94) The High Priestess
95) Popcorn
96) Ride the Bus
97) The Emperor
98) Raised Fist
99) Even Steven
100) Popcorn

Packs: 
Arcana Pack - Death, The Lovers, The High Priestess
Celestial Pack - Pluto, Eris, Planet X
Jumbo Buffoon Pack - Half Joker, Diet Cola, Cavendish, Ice Cream
Celestial Pack - Jupiter, Planet X, Earth
Standard Pack - Holographic Glass 4 of Clubs, Gold 9 of Diamonds, Purple Seal King of Clubs
Jumbo Celestial Pack - Pluto, Earth, Mercury, Jupiter, Saturn

==ANTE 15==
Boss: The Flint
Voucher: Glow Up
Tags: Juggle Tag, Standard Tag
Shop Queue: 
1) Clever Joker
2) Green Joker
3) Card Sharp
4) Devious Joker
5) The Star
6) Faceless Joker
7) Uranus
8) Misprint
9) Eris
10) Gluttonous Joker
11) Devious Joker
12) Diet Cola
13) Banner
14) Wily Joker
15) Delayed Gratification
16) The High Priestess
17) The Hermit
18) Credit Card
19) Shortcut
20) The Hermit
21) Death
22) Constellation
23) Banner
24) Juggler
25) The Tribe
26) Swashbuckler
27) Even Steven
28) The Empress
29) Wily Joker
30) The Devil
31) The Magician
32) The Order
33) Cavendish
34) Diet Cola
35) Fortune Teller
36) Half Joker
37) Supernova
38) Hologram
39) Merry Andy
40) Droll Joker
41) Foil Golden Joker
42) The Hermit
43) Ceres
44) Acrobat
45) Jolly Joker
46) Walkie Talkie
47) Planet X
48) The Hermit
49) Mars
50) Eris
51) Half Joker
52) Stuntman
53) Egg
54) The Fool
55) Jupiter
56) Credit Card
57) Cavendish
58) Mail In Rebate
59) Scary Face
60) The Chariot
61) Foil Scholar
62) Shoot the Moon
63) Justice
64) Banner
65) Eris
66) Glass Joker
67) The Emperor
68) Eris
69) Drivers License
70) The Magician
71) Drunkard
72) Eris
73) 8 Ball
74) Mad Joker
75) Green Joker
76) Earth
77) Ceremonial Dagger
78) Walkie Talkie
79) Cavendish
80) Uranus
81) Marble Joker
82) The Tower
83) The Chariot
84) Droll Joker
85) Mercury
86) Raised Fist
87) Gros Michel
88) Ceres
89) Earth
90) Riff-raff
91) Lusty Joker
92) Greedy Joker
93) Scholar
94) Splash
95) Luchador
96) Zany Joker
97) Sixth Sense
98) Death
99) The World
100) Greedy Joker

Packs: 
Jumbo Arcana Pack - The High Priestess, Judgement, The Fool, The Magician, The Hierophant
Jumbo Celestial Pack - Pluto, Planet X, Eris, Mercury, Ceres
Mega Celestial Pack - Planet X, Ceres, Jupiter, Mars, Venus
Arcana Pack - The Magician, The Soul, The Moon
Celestial Pack - Venus, Neptune, Saturn
Standard Pack - Gold 5 of Hearts, Gold Seal 9 of Clubs, Gold 7 of Clubs

==ANTE 16==
Boss: Amber Acorn
Voucher: Petroglyph
Tags: Double Tag, Investment Tag
Shop Queue: 
1) Eris
2) Scholar
3) Planet X
4) Crazy Joker
5) Golden Ticket
6) Green Joker
7) Certificate
8) Shoot the Moon
9) Misprint
10) Sock and Buskin
11) To Do List
12) Joker Stencil
13) Swashbuckler
14) Gluttonous Joker
15) Scholar
16) Banner
17) Egg
18) Pluto
19) Steel Joker
20) Ramen
21) Square Joker
22) Mars
23) Half Joker
24) Mime
25) Jupiter
26) Mr. Bones
27) Jupiter
28) The Idol
29) To Do List
30) Uranus
31) Hallucination
32) The Wheel of Fortune
33) Jolly Joker
34) Joker
35) Egg
36) Superposition
37) Vampire
38) The Fool
39) Splash
40) Mad Joker
41) Acrobat
42) Card Sharp
43) The Lovers
44) Uranus
45) Holographic Crafty Joker
46) Runner
47) Red Card
48) Devious Joker
49) Scary Face
50) Swashbuckler
51) Credit Card
52) Cavendish
53) Juggler
54) The Star
55) Raised Fist
56) Square Joker
57) Photograph
58) Ceres
59) Walkie Talkie
60) Reserved Parking
61) Abstract Joker
62) The Fool
63) Lusty Joker
64) Ceres
65) Red Card
66) Eris
67) Odd Todd
68) Mystic Summit
69) The Hierophant
70) The Hierophant
71) Holographic Brainstorm
72) Droll Joker
73) Arrowhead
74) Wily Joker
75) Arrowhead
76) Venus
77) Jupiter
78) Negative Green Joker
79) Fibonacci
80) Bootstraps
81) Pluto
82) Shortcut
83) Red Card
84) Odd Todd
85) Ride the Bus
86) Pluto
87) Neptune
88) Wily Joker
89) Droll Joker
90) Wrathful Joker
91) Scholar
92) Judgement
93) Walkie Talkie
94) Crafty Joker
95) Planet X
96) Abstract Joker
97) Greedy Joker
98) Clever Joker
99) Glass Joker
100) Stone Joker

Packs: 
Arcana Pack - The High Priestess, Temperance, The Devil
Standard Pack - Red Seal Mult Ace of Spades, 9 of Diamonds, Lucky 4 of Spades
Arcana Pack - The World, Justice, The Hierophant
Standard Pack - Wild Jack of Spades, Purple Seal 5 of Clubs, 9 of Diamonds
Arcana Pack - The Fool, The Moon, The Wheel of Fortune
Standard Pack - Queen of Diamonds, Stone Jack of Spades, Gold Seal Steel 4 of Clubs

==ANTE 17==
Boss: The Water
Voucher: Money Tree
Tags: Juggle Tag, Rare Tag
Shop Queue: 
1) Seltzer
2) Riff-raff
3) Marble Joker
4) Devious Joker
5) Rocket
6) Space Joker
7) Stone Joker
8) The Chariot
9) Ramen
10) Jupiter
11) Campfire
12) Scholar
13) Splash
14) Death
15) Hit the Road
16) Mercury
17) Square Joker
18) Hallucination
19) Walkie Talkie
20) Burglar
21) Faceless Joker
22) Golden Ticket
23) Smeared Joker
24) Spare Trousers
25) Diet Cola
26) Certificate
27) Ride the Bus
28) Seance
29) Polychrome Merry Andy
30) Ceres
31) Throwback
32) Wee Joker
33) Delayed Gratification
34) Odd Todd
35) Wee Joker
36) Neptune
37) Gros Michel
38) Photograph
39) Delayed Gratification
40) Planet X
41) Bloodstone
42) Riff-raff
43) Greedy Joker
44) The Tower
45) Runner
46) Supernova
47) Clever Joker
48) Half Joker
49) Seltzer
50) Photograph
51) Scholar
52) Cavendish
53) Loyalty Card
54) Pluto
55) Golden Joker
56) Throwback
57) Abstract Joker
58) Jupiter
59) Foil Mystic Summit
60) Popcorn
61) Oops! All 6s
62) Mars
63) The Hanged Man
64) Riff-raff
65) Mercury
66) Blue Joker
67) Ice Cream
68) Constellation
69) Lusty Joker
70) Trading Card
71) Venus
72) Fortune Teller
73) Neptune
74) Credit Card
75) Ride the Bus
76) Marble Joker
77) Trading Card
78) Planet X
79) Venus
80) The Wheel of Fortune
81) Hanging Chad
82) Gift Card
83) Crafty Joker
84) Runner
85) The Wheel of Fortune
86) Ceres
87) Smiley Face
88) Justice
89) Eris
90) Seltzer
91) Earth
92) Cartomancer
93) Even Steven
94) Golden Joker
95) Juggler
96) Sixth Sense
97) Eris
98) Negative Zany Joker
99) Jupiter
100) Lusty Joker

Packs: 
Mega Standard Pack - Steel 5 of Spades, Red Seal 4 of Hearts, Ace of Clubs, Gold Seal 7 of Clubs, Holographic 2 of Hearts
Arcana Pack - The Magician, The High Priestess, The Empress
Jumbo Arcana Pack - The Sun, Strength, The Hierophant, The High Priestess, The Fool
Celestial Pack - Uranus, Neptune, Earth
Celestial Pack - Venus, Earth, Uranus
Standard Pack - Foil Stone Jack of Diamonds, Red Seal Glass Queen of Hearts, Glass 10 of Clubs

==ANTE 18==
Boss: The Arm
Voucher: Wasteful
Tags: Rare Tag, Speed Tag
Shop Queue: 
1) Greedy Joker
2) Negative Lucky Cat
3) Scary Face
4) Constellation
5) Splash
6) The High Priestess
7) Uranus
8) Ice Cream
9) Square Joker
10) 8 Ball
11) Jolly Joker
12) Half Joker
13) Seeing Double
14) Lusty Joker
15) Burnt Joker
16) Golden Joker
17) Judgement
18) The Hierophant
19) The Tower
20) Droll Joker
21) The Hanged Man
22) Credit Card
23) Raised Fist
24) Walkie Talkie
25) Reserved Parking
26) Constellation
27) Blue Joker
28) Neptune
29) Ceres
30) Droll Joker
31) Mail In Rebate
32) Supernova
33) Lucky Cat
34) Smiley Face
35) Swashbuckler
36) Business Card
37) Ceres
38) Ride the Bus
39) Golden Ticket
40) Turtle Bean
41) Saturn
42) Certificate
43) Baron
44) Devious Joker
45) The Hierophant
46) Judgement
47) Judgement
48) Cartomancer
49) Saturn
50) Planet X
51) Mime
52) Mr. Bones
53) Ceremonial Dagger
54) Droll Joker
55) Pluto
56) Sly Joker
57) Jupiter
58) Ramen
59) The High Priestess
60) The Devil
61) To Do List
62) Popcorn
63) Hallucination
64) Seeing Double
65) Planet X
66) Mail In Rebate
67) Jolly Joker
68) Red Card
69) Red Card
70) Smiley Face
71) Superposition
72) Devious Joker
73) Photograph
74) Burglar
75) Crazy Joker
76) Foil Lusty Joker
77) Foil Fortune Teller
78) Hiker
79) To Do List
80) The Magician
81) Popcorn
82) Gros Michel
83) Foil Crafty Joker
84) Abstract Joker
85) Banner
86) Eris
87) Mars
88) Earth
89) Crafty Joker
90) Venus
91) Fortune Teller
92) Crazy Joker
93) Joker
94) Wrathful Joker
95) Rough Gem
96) Mars
97) Mystic Summit
98) Walkie Talkie
99) Faceless Joker
100) Green Joker

Packs: 
Celestial Pack - Venus, Planet X, Uranus
Celestial Pack - Venus, Ceres, Mars
Celestial Pack - Eris, Saturn, Mars
Mega Celestial Pack - Ceres, Mercury, Uranus, Venus, Eris
Standard Pack - Purple Seal 8 of Hearts, Blue Seal 2 of Diamonds, Mult 6 of Hearts
Arcana Pack - Temperance, The Emperor, Death

==ANTE 19==
Boss: The Serpent
Voucher: Overstock Plus
Tags: Polychrome Tag, Investment Tag
Shop Queue: 
1) Scholar
2) Red Card
3) Riff-raff
4) Green Joker
5) Devious Joker
6) The Moon
7) Droll Joker
8) Loyalty Card
9) Merry Andy
10) Joker
11) Ceres
12) The Sun
13) Judgement
14) Uranus
15) Crafty Joker
16) Strength
17) Steel Joker
18) Delayed Gratification
19) Raised Fist
20) The Lovers
21) The Tower
22) Even Steven
23) Ride the Bus
24) Droll Joker
25) Polychrome Droll Joker
26) The Hermit
27) Seeing Double
28) Smeared Joker
29) Uranus
30) Banner
31) Mystic Summit
32) The Hanged Man
33) The Lovers
34) Green Joker
35) Square Joker
36) Clever Joker
37) Clever Joker
38) Foil Odd Todd
39) The Moon
40) Campfire
41) Foil Flash Card
42) Misprint
43) Walkie Talkie
44) Midas Mask
45) Greedy Joker
46) Holographic Riff-raff
47) Gift Card
48) Blue Joker
49) The Wheel of Fortune
50) The Magician
51) Odd Todd
52) Foil Dusk
53) DNA
54) Mail In Rebate
55) Red Card
56) Planet X
57) Satellite
58) The Emperor
59) Earth
60) Venus
61) The Trio
62) Justice
63) Acrobat
64) Foil Supernova
65) Blue Joker
66) Earth
67) Temperance
68) Jolly Joker
69) Golden Joker
70) Wrathful Joker
71) Wrathful Joker
72) Faceless Joker
73) The Lovers
74) Obelisk
75) Delayed Gratification
76) Half Joker
77) The Star
78) Cavendish
79) Seeing Double
80) Raised Fist
81) Gluttonous Joker
82) Riff-raff
83) Hanging Chad
84) Misprint
85) Cloud 9
86) Wrathful Joker
87) The High Priestess
88) Venus
89) Drunkard
90) Shortcut
91) Joker
92) Jolly Joker
93) Burglar
94) Showman
95) Hanging Chad
96) Lucky Cat
97) Earth
98) Abstract Joker
99) The Moon
100) The Fool

Packs: 
Celestial Pack - Eris, Planet X, Jupiter
Standard Pack - Steel Queen of Spades, Purple Seal 9 of Hearts, Bonus 5 of Hearts
Arcana Pack - The Lovers, The World, The Hanged Man
Jumbo Celestial Pack - Eris, Neptune, Venus, Earth, Ceres
Celestial Pack - Jupiter, Neptune, Planet X
Celestial Pack - Planet X, Eris, Mercury

==ANTE 20==
Boss: The Psychic
Voucher: Palette
Tags: Charm Tag, Boss Tag
Shop Queue: 
1) To Do List
2) Mime
3) Juggler
4) The Sun
5) Ancient Joker
6) Justice
7) Golden Ticket
8) Earth
9) Obelisk
10) The Magician
11) DNA
12) Half Joker
13) Mad Joker
14) Ride the Bus
15) Holographic Smeared Joker
16) The Hermit
17) Scholar
18) Zany Joker
19) Walkie Talkie
20) Bull
21) Diet Cola
22) Neptune
23) Splash
24) Jolly Joker
25) Trading Card
26) Planet X
27) The Tower
28) Bootstraps
29) Clever Joker
30) Scary Face
31) Diet Cola
32) Midas Mask
33) Flower Pot
34) Runner
35) Ceres
36) Planet X
37) Satellite
38) Supernova
39) Foil Superposition
40) Hanging Chad
41) Jolly Joker
42) The Hierophant
43) 8 Ball
44) Bloodstone
45) Throwback
46) Credit Card
47) Planet X
48) The Star
49) Delayed Gratification
50) Drunkard
51) Venus
52) The Wheel of Fortune
53) Strength
54) Death
55) Earth
56) Jupiter
57) Clever Joker
58) Neptune
59) The Star
60) Mr. Bones
61) Marble Joker
62) Loyalty Card
63) Half Joker
64) The World
65) Hit the Road
66) Fibonacci
67) Temperance
68) Gluttonous Joker
69) Pluto
70) Foil Stuntman
71) The Emperor
72) Four Fingers
73) Popcorn
74) Constellation
75) Mail In Rebate
76) Ice Cream
77) Golden Ticket
78) Devious Joker
79) Temperance
80) The Wheel of Fortune
81) Sly Joker
82) Hanging Chad
83) Riff-raff
84) Raised Fist
85) Zany Joker
86) Juggler
87) Banner
88) Planet X
89) Steel Joker
90) Invisible Joker
91) Mystic Summit
92) Sly Joker
93) Uranus
94) Walkie Talkie
95) Greedy Joker
96) Drunkard
97) Hallucination
98) Lusty Joker
99) Supernova
100) Death

Packs: 
Jumbo Buffoon Pack - Crazy Joker, Scholar, Supernova, Smiley Face
Standard Pack - 5 of Hearts, Steel 4 of Diamonds, Jack of Clubs
Arcana Pack - Justice, The World, The Star
Standard Pack - Gold Seal Mult 7 of Clubs, Lucky 10 of Clubs, Gold Seal Steel 4 of Hearts
Mega Buffoon Pack - To Do List, Raised Fist, Splash, Rocket
Mega Arcana Pack - Death, The Fool, The Magician, The Devil, Judgement
=== END SEED INTELLIGENCE (BENCHMRK) ===

## Final reminders (read after everything above)
- You are the PLANNER. You never act in the game; the PLAYER does.
- Before the player's first action you must already hold a route for every ante up to ante 20, calculated from the seed intelligence and the scaling table, with variance and the reasonable worst case priced into every step.
- Hold the player to your principles; demand numbers; re-derive the route out loud whenever it changes.
- Dialogue until genuine agreement. Endorse only by ending your reply with a line containing exactly: AGREED. Never write it unless you mean it.
