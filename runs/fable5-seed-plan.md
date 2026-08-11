# BENCHMRK Run 2 — Full Seed Plan (fable5, Red Deck, White Stake)

## RE-READ AFTER COMPACTION
- Full seed data: `C:\Users\maaro\AppData\Local\Temp\Blueprint\benchmrk-compact.txt` (per-ante shop queues, packs, tags, misc streams; deck draw orders in `benchmrk-analysis.txt`).
- Re-run analyzer anytime: `cd $env:TEMP\Blueprint; npx -y tsx run-analysis.mts` (edit ANTES/settings in run-analysis.mts).
- Driver: `powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\maaro\OneDrive\Desktop\balatro-bench\bench-rpc.ps1 -Port 12347 -Method <name> -Params '<json>'` (plain double quotes in JSON, never backslash-escaped).
- Start: method `start`, params `{"deck":"RED","stake":"WHITE","seed":"BENCHMRK"}`. No lives. Journal: `runs\fable5-journal.md`. End with `RESULT ante=<n> best_hand=<n> won=<bool>`.
- Target: beat user's ante 19. Run 1 = ante 10 / 308,227.

## RELIABILITY NOTES
- Antes 1–8 analyzer data VERIFIED against run 1 (bosses, tags, shops, packs all match).
- A9+ BOSSES UNRELIABLE: analyzer said a9 Fish / a10 Mark, but run 1 actually got a9 The Eye / a10 The Flint. Check gamestate live every ante.
- Shop queues shift as I buy jokers (locking rerolls the stream). A1–a4 near-exact; later antes directional only. Live shop = ground truth; positions below are queue indices, not gospel.
- API quirks (run 1): timeouts often = success (re-check gamestate); NEVER pick target-needing tarots/spectrals from PACKS (hangs, wasted) — buy them as shop cards and use DURING BLINDS; Cerulean Bell-type forced card: select only 4; sell jokers before opening joker packs; indices are 0-based and shift.

## CORE BUILD: Baron ladder (held steel Kings × copy jokers)
Endgame jokers: **Baron** (X1.5 per King held) + **Blueprint** + **Brainstorm** (both copying Baron; Baron leftmost for Brainstorm, Blueprint to Baron's left) + **Invisible Joker** (sell after 2 rounds → duplicate a Baron/copy) + X-mult filler (The Duo / Hologram / Photograph) + Mr. Bones insurance late.
Deck: maximize Kings (Strength Q→K, Death copy King, **DNA a5 = permanent King copy every round** — play lone King as first hand), steel them (The Chariot as shop card, standard-pack steels), hold max Kings (Juggler +1 hand size, Troubadour +2). Played hand: leveled Two Pair (Uranus everywhere in seed) with Photograph face cards (QQJJ).
Slots: Ectoplasm (a3 + a5 spectral packs) → Negative jokers (+1 slot each, costs -1 hand size — worth it); Negative Tag a11 small-skip → next base-edition shop joker free+Negative.
Money: Egg a2, sell-cycling during Coupon digs, interest cap $25 fast, Investment/Garbage tags late.

## ANTE-BY-ANTE (queue positions from analyzer)
**A1** — Boss: The Pillar. Tags: Coupon (small) | Polychrome. Voucher: Tarot Merchant.
- SKIP SMALL → Coupon Tag. Beat Big 450 (draw known, unmodified deck — see full analysis file). Play Big conservatively re: Pillar (debuffs cards played this ante).
- FREE SHOP after Big: queue = Runner, Mad, Lusty, Superposition, Hanging Chad, Fool, Madness, Strength, Greedy, **BARON(10)**, Riff-raff, Smiley Face[Polychrome](12), Star, Oops, Droll, Jupiter(16), Mars, ToDoList, SpareTrousers, Banner, Neptune, **Uranus(22)**, RideTheBus, Venus, Glutt, Hack, Misprint, Space, Vampire, Half, RideBus, Juggler, Seltzer, Matador, EvenSteven, Justice, Banner, CardSharp, Lusty, Magician, Seance, Jupiter, Smiley, Burglar, **Earth(45)**, Clever, Emperor, SpareTrousers, Burglar, Jolly(50).
- DIG PROTOCOL (verify refills stay free): buy joker→sell ($1 net), buy planet→use immediately, buy tarot→sell or keep (keep Strength for Q→K later? slots=2). Goal: Baron + Smiley[Poly] (early king mult) + all planets used (Uranus=2Pair, Earth=FH...). If refills NOT free, take best 2 + packs.
- Free packs (coupon): Buffoon(1/2): Jolly/Drivers License → Jolly (early mult, sell later). Jumbo Celestial(1/5): Uranus,Saturn,Neptune,Mars,Jupiter → Uranus.
- Boss Pillar: one-shot with FH/trips (run 1: AAJJJ FH = 1584).
- Post-boss shop (start of a2): packs Celestial(1/5: Saturn,Venus,Uranus,Jupiter,Pluto - take Uranus) + Arcana(1/3: Justice,Moon,Sun - Justice needs a card target = API hang risk from packs; Moon and Sun are planet cards here (Moon/Sun ARE planets in celestial packs; in an Arcana pack these are tarot names) - skip this arcana unless picks are target-free).
**A2** — Boss: The Hook (discards 2 random held per hand played — bad for held Kings, keep it simple, one-shot). Tags: D6|Voucher. Voucher: Hieroglyph (do NOT buy — reduces ante).
- Shop: Devil(1), Egg(2), **The Duo(3)**, Jolly(4), ..., Death(19) [copy King during blind], Emperor(34), Swashbuckler(39/50), Golden Joker(41).
- Buy: The Duo ($8), Egg ($4), Death if $ (use in blind: hold 2 Kings? copies left→right card). Packs: small Celestial(1/3 Venus,Earth,Mercury), boss Arcana(1/3 HighPriestess,Empress,Tower) — Tower target-needed, skip.
**A3** — Boss: The Tooth ($lost per card played — play few cards). Tags: Speed|Meteor. Voucher: Blank.
- Small-blind shop Pack1 Spectral(1/2): Cryptid/**Ectoplasm** → Ectoplasm (few jokers owned = likely hits Baron/Duo; -1 hand size accepted). Pack2 Celestial(1/5): Jupiter,Uranus,Saturn,Neptune,Venus → Uranus.
- Shop: Throwback(2), 8Ball(6), Wee Joker(20), Earth(28/32), Venus(29).
- Big-blind shop Pack2 Buffoon(1/2): Cloud 9/Rough Gem → Cloud 9 (economy) if slot spare.
**A4** — Boss: The Wheel (1 in 7 cards drawn face down — annoyance only). Tags: D6|Orbital. Voucher: **TELESCOPE — buy**.
- Shop: Mercury(4), Uranus(13), **Photograph(30)** ($5) — BUY (X2 first face played; pairs with QQJJ two pair). Saturn(29/33), Seeing Double(38).
- Packs: small Standard(pick 2/5): Lucky 10C, AC, BlueSeal Mult AS, **Glass 9S**, 9D. big Standard(1/3): ..., **Stone KD**... boss Standard incl Foil Stone 7D.
**A5** — Boss: The Club (Clubs debuffed). Tags: **Buffoon(small)**|Holographic. Voucher: Reroll Surplus (buy if $ — cheap rerolls help digging).
- KEEP A JOKER SLOT FREE (run-1 lesson). Skip small → Buffoon Tag → free Buffoon pack: stream starts Runner, Banner, HangingChad, Bloodstone, The Order... (meh — reconsider skipping; alternatively don't skip, money matters).
- Big-blind shop Pack1 Buffoon(1/2): Riff-raff/**Photograph** → Photograph backup if missed a4. Pack2 Spectral(2/4): Immolate,Grim,**Ectoplasm**,Sigil → 2nd Ectoplasm (+Grim only if safe—target? Grim no target, creates Aces? Grim=destroy? skip if risky).
- Shop: Chariot as CARD? (5)=The Chariot tarot — BUY, steel a King during blind. **DNA(38)** ($10) — BUY: from then on, play lone King first hand each round → permanent King copies. Hit the Road(21), Pareidolia(39).
**A6** — Boss: The House (first hand face down). Tags: Standard|Speed. Voucher: Magic Trick.
- Small shop Pack2 Standard(1/3): **Steel 7H**. Boss shop Pack1 Standard(1/3): Steel 7C option. Pack2 Standard(2/5): **Polychrome QD** + BlueSeal 8H.
- Shop: Throwback(4/41), Earth(8/16), Joker Stencil(17), Astronomer(44).
**A7** — Boss: The Ox (play most-played hand → $0; dodge with off-hand one-shot). Tags: Boss|Investment. Voucher: Telescope-slot (if bought a4, may show Observatory — BUY Observatory if offered).
- Shop: Earth(19), **Campfire(38)**, **BLUEPRINT(40)** ($10) — BUY Blueprint. Uranus(16).
- Packs: small Celestial(2/5!): Mercury,Venus,Saturn,Mars,Uranus. boss Arcana(1/3): Wheel,Temperance,Tower — skip (targets).
**A8** — Boss: Cerulean Bell (forced card auto-joins — SELECT ONLY 4). Tags: Buffoon|Garbage(+$45 big skip? No—Garbage = $ per unused discard... run1 got $45 from it via big skip; decide by money need). Voucher: Hone.
- Shop: **Mr. Bones(1)** — buy (death insurance), Chariot(4), Stuntman(32), Death(40), **BARON #2 (41)**! Trading Card(34).
- All 4 shop packs pre-boss are Celestial: levels galore (Jupiter/Pluto/Saturn; Earth/Venus/Mars; Venus/Uranus/Mercury; Earth/Mercury/Jupiter/Saturn/Mars).
**A9** — Boss: analyzer=Fish but run1 got THE EYE (no repeat hand types) — VERIFY LIVE. Tags: **Coupon(small)|Coupon**. Voucher: Blank.
- Skip small → Coupon → FREE SHOP after big: Banner, Mercury, **Cartomancer(3)**, Gift Card(4), **Hologram(5)**, **Constellation(6)**, Earth(7), ..., The Duo(22), DNA(38), Photograph(41), DNA(49). Dig deep (sell-cycle). Run 1 also saw Polychrome Golden Joker here (~$11).
- Packs: small Standard(1/3): Foil **Steel 10C**. big Standard(2/5): **Polychrome Glass 3S** + BlueSeal Foil QD.
**A10** — Boss: analyzer=Mark, run1 got THE FLINT — VERIFY. Tags: Uncommon|Top-up.
- Shop: **INVISIBLE JOKER(6)**, **BARON(14)**, Photograph(24), Blueprint(49). Buy Invisible (sell after 2 rounds → duplicate best joker; time so it dupes Blueprint/Brainstorm/Baron).
- Big shop Pack2 Standard(1/5): **Steel 3H**.
**A11** — Boss: The Wall? (4x blind) VERIFY. Tags: **NEGATIVE(small skip → next base shop joker becomes Negative+free)** | Uncommon. Voucher: Overstock.
- Skip small → Negative Tag. Shop queue1 = Mercury... first base-edition JOKER gets it: Scary Face(2)? — reroll/buy order so it lands on something useful (Invisible Joker(13)! = free Negative Invisible). Chariot(19/47), Constellation(18), Death(31), The Idol(24), Acrobat(40).
**A12+** — analyzer bosses (Mouth/Manacle/Goad/Flint/AmberAcorn a12-16) UNRELIABLE — verify live. Keep: rareTag streams stuffed with Blueprint/Brainstorm/Invisible/Baron/The Family/Duo — take Rare Tags when offered by skips ONLY if slot free. Shops keep offering Baron(a12#50), The Family(a13#50), Mime(a16#24 — retrigger held Kings, HUGE late buy), Sock and Buskin(a16#10).
- Yorick (Soul) sighted: a15 big Arcana(1/3) contains Soul→Yorick — grab if affordable (legendary X-mult grower).

## SCALING MATH / CHECKPOINTS
- X per held King: Baron X1.5 per copy chain; steel adds X1.5 (Mime a16 doubles steel triggers). With Baron+Blueprint+Brainstorm+1 Invisible dupe = 4 Baron triggers → X1.5^4 per King ≈ X5 per King. 9 Kings held ≈ 2M X-mult from Barons alone; steels ×38. Two Pair lvl ~12 played QQJJ+glass ≈ 1e5 → total ~1e12-13 by a12-13.
- To go further: more Invisible dupes (every 2 rounds), Hologram (grows with DNA king-adds), hand size (Juggler/Troubadour/Turtle Bean), Mime at a16, Observatory.
- Blind targets (from run 1): a9 110k/165k/220k, a10 560k/840k/1.12M; roughly ×5-13 per ante after (a11 ~7.2M base, a12 ~300M, a13 ~47B, a14 ~2.9e13, a15 ~7.7e16, a16 ~8.6e20, a17 ~4.2e25, a18 ~9.2e30, a19 ~9.2e36).
- Every ante: level Two Pair with every Uranus seen; DNA king first hand EVERY round once owned.

## RUN-1 LESSONS (still binding)
1. Free a joker slot BEFORE joker-pack tags.
2. Cerulean Bell: select only 4 cards.
3. Never take target-needing tarots/spectrals from packs (API hang) — shop cards only, use during blinds.
4. Additive jokers left of X-mults; Baron leftmost for Brainstorm.
5. The Ox: dodge most-played hand (will be Two Pair) with FH/other one-shot.
6. Timeouts often = success; always re-check gamestate before retrying.
7. Money: stay ≥$25 for interest when possible; Coupon digs are self-funding via sells.
