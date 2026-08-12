"""Stage a Balatro Bench run from explicit eval factors.

Every condition variable is a command-line flag; the script builds a fresh,
isolated arena directory and prints the launch command(s).

    python stage-run.py --player claude-opus-5 --planner claude-opus-5 \
        --planner-prompt principles --seed-info on

Factors:
  --player <model id>        the model that plays (launch command uses it)
  --planner <who>            none | human | a model id
                             (claude-3-* models route via the research API key;
                              living models run as claude -p CLI sessions;
                              human uses the mailbox + planner console)
  --planner-prompt <which>   general | principles | inspire
  --seed-info <on|off>       whether the BENCHMRK seed analysis is provided
  --name <optional>          override the auto-generated arm name

The arm gets: prompt.txt, seed file (if on), consult transport (if planner),
planner briefing, tool-denied planner subdir (CLI transport), sandbox settings
denying every sibling arena dir (and every sibling gets a deny for the new
arm), and run-config.json recording the exact condition.
"""
import argparse
import datetime
import json
import pathlib
import shutil
import sys

BENCH = pathlib.Path(__file__).resolve().parent
ARENA = BENCH / "arena"
TEMPLATES = BENCH / "templates"

SHORT = {
    "claude-opus-5": "opus5",
    "claude-fable-5": "fable5",
    "claude-sonnet-5": "sonnet5",
    "claude-opus-4-8": "opus48",
    "claude-opus-4-1": "opus41",
    "claude-opus-4-0": "opus40",
    "claude-3-opus-20240229": "opus3",
    "human": "michael",
}

# ---------------------------------------------------------------- player prompt

PLAYER_BASE = """You are playing ONE run of Balatro for a benchmark. Play as well as you possibly can.

## Goal
Reach the highest ante you can, and score as high as you can. This is SOLO Balatro: there are NO lives, so if you ever fail to meet a blind's chip requirement, the run ends immediately. Getting further (higher ante) matters most; your single biggest hand is the tiebreak.

## How you play
You drive the real running game through a local HTTP API. Use this PowerShell helper for EVERY action; it prints either a compact game-state summary or an action result. Run it from your shell like this:

    powershell -NoProfile -ExecutionPolicy Bypass -File "{BENCH}\\bench-rpc.ps1" -Port 12347 -Method <name> -Params "<json>"

Example (start the run):

    powershell -NoProfile -ExecutionPolicy Bypass -File "{BENCH}\\bench-rpc.ps1" -Port 12347 -Method start -Params "{{\\"deck\\":\\"RED\\",\\"stake\\":\\"WHITE\\",\\"seed\\":\\"BENCHMRK\\"}}"

Mind the JSON quoting for your shell. Always call `gamestate` to see the current state before you decide your next move. Do not fire actions blind. Indices are 0-based and refer to the arrays shown in the game state (hand cards, shop cards, packs, etc.); re-read the state before indexing because positions shift after every action.

Start your run with EXACTLY: method start, params {{"deck":"RED","stake":"WHITE","seed":"BENCHMRK"}}.

### Endpoints (method, params, valid state, effect)
- gamestate | {{}} | any | full state: state, ante_num, round_num, money, won, hands (poker-hand levels), jokers, consumables, hand, shop, vouchers, packs, blinds, round (chips scored / hands_left / discards_left).
- start | {{deck,stake,seed}} | MENU | begin the run.
- select | {{}} | BLIND_SELECT | play the blind currently on deck.
- skip | {{}} | BLIND_SELECT | skip a Small or Big blind (never the Boss); you take its tag instead.
- play | {{cards:[indices]}} | SELECTING_HAND | play those hand cards as a poker hand.
- discard | {{cards:[indices]}} | SELECTING_HAND | discard those hand cards and redraw.
- use | {{consumable:i, cards:[targets?]}} | SELECTING_HAND or SHOP | use a tarot/planet/spectral (cards = the hand cards it targets, if any).
- buy | {{card:i}} OR {{voucher:i}} OR {{pack:i}} | SHOP | buy that shop item.
- pack | {{card:i}} OR {{skip:true}}, plus {{cards:[targets]}} when a picked consumable needs targets | opened booster | pick or skip a card from an opened pack.
- sell | {{joker:i}} OR {{consumable:i}} | SELECTING_HAND or SHOP | sell for money.
- rearrange | {{hand:[order]}} OR {{jokers:[order]}} OR {{consumables:[order]}} | play/shop | reorder (joker order matters for some effects).
- reroll | {{}} | SHOP | reroll the shop for its current cost.
- cash_out | {{}} | ROUND_EVAL | collect the round's rewards.
- next_round | {{}} | SHOP | leave the shop and go to the next blind selection.

The flow: start -> BLIND_SELECT -> select (or skip a small/big) -> SELECTING_HAND -> play/discard until the blind's chip goal is met -> ROUND_EVAL -> cash_out -> SHOP -> buy / reroll / use / open packs -> next_round -> repeat. The Boss is the third round of each ante and cannot be skipped; read its effect in the state before selecting it.

## Rules
- Play legitimately only. The endpoints `set`, `add`, and `load` are disabled by the server and will error; do not attempt to work around that.
- These instructions are complete; you may re-read THIS instructions file if needed. Do NOT read, list, or search any OTHER files (no other journals, no game-data files, nothing else) except: your own journal{ALLOWED_EXTRAS}.
{SEED_SECTION}{PLANNING_SECTION}
## Journal
Keep a running journal at:

    {ARM}\\journal.md

Write your build plan, the key decisions and your reasoning, per-ante progress, and your best single hand as you go. For EVERY ante, record a line with the best single hand you scored during that ante (these feed a per-ante graph) (track it by watching round.chips before and after each play). At the end, append a post-mortem: final ante, best single hand, exactly what ended the run, and concrete lessons for a future attempt on this seed.

## Efficiency
A full run is long. Be decisive, keep your internal reasoning tight, and rely on the compact state summary rather than dumping raw state. Make strong plays; do not narrate more than you need to.

## Winning
If you beat ante 8, the game shows a win screen and pauses. STOP COMPLETELY at that point: update your journal, then end your turn and wait. Do not poll, do not fire any further API calls{NO_CONSULT_AT_WIN}, do not try to dismiss the win screen. The operator will take a screenshot, click Endless manually, and tell you to continue.{WIN_RESUME} Consultations continue at every ante boundary in endless.

## Ending
Play until the game reaches GAME_OVER. Then call gamestate one last time, finish your journal, and return a single final line exactly in this format:

    RESULT ante=<number> best_hand=<number> won=<true|false>
"""

SEED_SECTION = """
## Seed intelligence
This is NOT a blind run. You have been given a full analysis of seed BENCHMRK:

    {ARM}\\BENCHMRK_analysis.txt

It lists, for each ante: the boss, the voucher, the tags, the shop item queue, and pack contents. Read it and use it however you like.
"""

PLANNING_COMMON = """
## Planning partnership
{PARTNER_INTRO} You talk to it with this command (your message as ONE quoted argument; ALWAYS give this call a 10-minute timeout, replies can be very slow):

    python "{ARM}\\consult.py" "<your message>"
{TRANSPORT_NOTES}
When you MUST consult:
- At the very start: before calling start, bring the planner your proposed overall strategy for the whole run.
- At the end of every ante: immediately after you cash_out a Boss blind, before you buy anything in the shop, report what happened last ante, the current state (ante, money, jokers, hand levels, deck shape), and your proposed plan for the next ante.

How a consultation works:
- It is a dialogue: keep exchanging messages until you and the planner agree on the strategy. The planner signals endorsement by ending its reply with the line AGREED.
- You are capped at 10 messages per consultation. If there is no agreement by then, note the disagreement in your journal and proceed on your best judgment.
- Do not simply defer: if you believe the planner is wrong, argue your case. Agreement should be real, in both directions.
- Do not consult mid-blind; you play the hands alone.
- The dialogue is logged automatically to planner-dialogue.md in your folder; you may re-read that file at any time.
{RETRY_NOTE}
In your journal, record one line per consultation: whether consensus was reached and the agreed plan.
"""

PARTNER_NEUTRAL = "You are the PLAYER half of a two-member team. A separate PLANNER shares these same instructions{AND_SEED}, keeps its memory across the whole run, and does long-horizon planning and evaluation with you."
PARTNER_INSPIRE = "You are the PLAYER half of a two-model team. A separate PLANNER model has these same instructions{AND_SEED}, and it keeps its memory across the whole run. Its job is to inspire and pressure-test deep long-horizon planning in YOU, and to guard you against myopia. It was trained before Balatro was released, so it may err on specific game mechanics; weigh mechanical claims against your own knowledge{SEED_REF}. Its long-view challenges are the point: engage with them seriously."

RETRY_CLI = "- If the consult command errors or times out, re-run the SAME command with the SAME message (the planner conversation tolerates retries). If it fails three times in a row, note it in the journal and continue playing."
RETRY_API = "- If the consult command errors, retry it once; if it still fails, note it in the journal and continue playing."
NOTES_MAILBOX = """
If it prints that the planner has not replied yet, keep waiting by running (again with a 10-minute timeout, as many times as needed):

    python "{ARM}\\consult.py" --wait

Never skip or abandon a mandatory consultation because the planner is slow, and never send a new message while a reply is still owed; use --wait.
"""

# ---------------------------------------------------------------- planner roles

ROLE_HEADER = """# You are the PLANNER

You are one half of a two-model team playing a single benchmarked run of Balatro (seed BENCHMRK, Red Deck, White Stake, solo, no lives). Your teammate, the PLAYER, is a separate model that drives the actual game through an API. You never touch the game and you have no tools: your entire contribution is this text dialogue. Everything you need is already in this prompt, each part clearly marked with BEGIN/END delimiters below.
"""

ROLE_GENERAL = """
## Your role
Long-horizon planning and evaluation. The PLAYER consults you:
- once at the very start of the run, before its first action, and
- at the end of every ante (right after the Boss blind is beaten, before any shop purchases for the next ante).

Each consultation is a multi-turn dialogue. The PLAYER brings you the current situation and a proposed strategy; you evaluate it against the whole rest of the run, not just the next blind. Reason through alternatives, push back where the plan is weak, and hold the long view. Do not rubber-stamp.
"""

ROLE_PRINCIPLES = """
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
"""

ROLE_INSPIRE = """
## Why you are here
This run is a proof of concept for deep long-horizon agentic planning. The working hypothesis: models playing alone drift into myopia. They optimize the next blind, react to the shop in front of them, and defer the endgame until it arrives. Your presence is the countermeasure. Success here is measured by the depth and consistency of the PLAYER's foresight across the whole run, not by your own knowledge of the game.

## An honest note on your knowledge
Balatro was released in February 2024, after your training data ends. You likely have little or no firsthand knowledge of it. That is expected and is not a handicap for this role: the PLAYER knows the game deeply from training, and the rules explainer plus the seed intelligence (if provided) are in this prompt. Ground every specific claim you make in those sources rather than in memory.

A useful anchor you DO know: Slay the Spire. Balatro is the same genre of roguelike run, and it demands the same dual-horizon judgment: every decision must serve both surviving the next fight and scaling the deck for the endgame. The instincts you have about that tension (greedy short-term picks that starve the late game, engines that must be committed to early to come online in time) transfer directly; only the mechanics are new.

## Your role: inspire the planning, don't replace it
Your job is not to out-know the player about Balatro. It is to draw deep long-horizon planning OUT of the player. The PLAYER consults you:
- once at the very start of the run, before its first action, and
- at the end of every ante (right after the Boss blind is beaten, before any shop purchases for the next ante).

In each consultation:
- Demand a plan that reaches the END of the run, not just the next ante. Ask what the plan is for the largest requirements coming, and how the current build gets from here to there.
- Probe assumptions. When the player proposes something, ask what evidence from the game state or the seed intelligence supports it, and what would have to be true for it to fail.
- Name myopia when you see it: reactive purchases, plans that keep deferring the hard problem, short-term fixes that spend resources the stated long-term plan needs.
- Hold continuity: remind the player of its own earlier commitments and projections. If the plan changes, make the revision explicit and reasoned rather than silent.

## Balatro: a rules explainer (you were trained before this game existed)

Balatro is a poker-themed roguelike deckbuilder. One run works like this:

- **Run structure.** A run is a sequence of antes. Each ante has three blinds in order: Small Blind, Big Blind, Boss Blind. A blind is beaten by scoring at least its chip requirement within a limited number of played hands. Requirements grow steeply from ante to ante (multiplying many-fold over the run). Beating the ante 8 Boss wins the base game; play can then continue into endless mode, where requirements keep exploding. Failing any blind ends the run instantly (no lives in this benchmark).
- **Playing a blind.** The player holds a hand of cards drawn from their deck (standard 52-card deck at the start; the run modifies it). Each play selects 1-5 cards forming a poker hand (high card, pair, two pair, three of a kind, straight, flush, full house, four of a kind, straight flush). A limited number of hands and discards are available per blind; a discard replaces selected cards with new draws. Exact counts are shown in the live game state. Small and Big blinds may be SKIPPED (forfeiting their reward, gaining a "tag" with a stated effect instead); Boss blinds cannot be skipped and each imposes a special named restriction on play.
- **Scoring.** A played hand scores chips x mult. The hand type contributes base chips and base mult; each scoring card adds its chip value (pips at face value, face cards 10, aces 11). Jokers then modify the totals: some add chips, some add mult, some MULTIPLY mult. Effects apply in joker order, left to right. Each poker-hand type has a LEVEL; Planet cards raise a hand type's level, permanently increasing its base chips and mult.
- **Jokers.** Up to 5 joker slots (modifiable). Jokers are the run's engine: bought in shops or from packs, each has a persistent effect (scoring, economy, retriggers, card generation, scaling over time, etc.). Their text is shown in the game state.
- **Consumables.** Up to 2 consumable slots. Tarot cards modify playing cards or give money; Planet cards level hand types; Spectral cards have powerful, often costly effects.
- **Card modifications.** Playing cards can carry an enhancement (examples: Bonus = extra chips; Mult = extra mult; Steel = x1.5 mult while HELD in hand, not played; Glass = x2 mult when played but a chance to shatter; Gold = money if held at round end; Stone = flat chips, no rank or suit; Lucky = chance-based bonuses), an edition (Foil = +chips, Holographic = +mult, Polychrome = x1.5 mult), and a seal (Red = the card retriggers; Blue = creates the played hand's Planet card if held; Gold = money when played; Purple = a Tarot when discarded).
- **Economy.** Money is earned from blind rewards, per-hand bonuses, interest (a bonus per $5 held at round end, capped), jokers, and tags. Money buys shop items and rerolls.
- **The shop.** After every beaten blind: a few purchasable cards (jokers or consumables), one Voucher (a permanent run upgrade), and booster packs (opened immediately; pick from their contents: playing cards, jokers, tarots, planets, or spectrals). The shop can be rerolled for a rising cost.
- **The seed.** A run's content (shop queues, pack contents, bosses, vouchers, tags) derives from its seed.
"""

ROLE_PROTOCOL = """
## Agreement protocol
- Each consultation is a multi-turn dialogue; it continues until you genuinely endorse the plan.
- When you endorse it, end your reply with a line containing exactly: AGREED
- Never write AGREED unless you actually agree. The player is capped at 10 messages per consultation and will proceed without consensus after that; a real disagreement, held honestly, is a legitimate outcome.
- Keep replies concrete: name specific jokers, vouchers, tags, antes, and numbers. No filler.

## Continuity
This one conversation persists for the entire run. Every earlier consultation stays in your context; track how the run is evolving against the plan, notice when reality diverges from your expectations, and update your advice as evidence comes in.

## The player's full instructions (for your reference; your role is the one above)

=== BEGIN PLAYER INSTRUCTIONS ===
{PLAYER_PROMPT}
=== END PLAYER INSTRUCTIONS ===
{SEED_BLOCK}
## Final reminders (read after everything above)
- You are the PLANNER. You never act in the game; the PLAYER does.
- Dialogue until genuine agreement. Endorse only by ending your reply with a line containing exactly: AGREED. Never write it unless you mean it.
"""

SEED_BLOCK = """
## Seed intelligence: the map of this run (the same file the player has)

=== BEGIN SEED INTELLIGENCE (BENCHMRK) ===
{SEED}
=== END SEED INTELLIGENCE (BENCHMRK) ===
"""

ROLES = {"general": ROLE_GENERAL, "principles": ROLE_PRINCIPLES, "inspire": ROLE_INSPIRE}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--player", default="claude-opus-5")
    ap.add_argument("--planner", default="none",
                    help="none | human | model id (claude-3-* routes via API key)")
    ap.add_argument("--planner-prompt", default="general", choices=list(ROLES))
    ap.add_argument("--seed-info", default="on", choices=["on", "off"])
    ap.add_argument("--name", default=None)
    a = ap.parse_args()

    seed_on = a.seed_info == "on"
    planner = None if a.planner == "none" else a.planner
    transport = None
    if planner == "human":
        transport = "mailbox"
    elif planner:
        transport = "api" if planner.startswith("claude-3") else "cli"

    pshort = SHORT.get(a.player, a.player.replace("claude-", "").replace("-", ""))
    plshort = SHORT.get(planner, (planner or "solo").replace("claude-", "").replace("-", ""))
    name = a.name or (
        f"{pshort}"
        + (f"__plan-{plshort}-{a.planner_prompt}" if planner else "__solo")
        + ("__seed" if seed_on else "__noseed")
    )
    arm = ARENA / name
    i, base = 2, name
    while arm.exists():
        name = f"{base}-{i}"; arm = ARENA / name; i += 1
    armstr = str(arm)

    # ---- player prompt
    allowed = []
    if seed_on:
        allowed.append("the seed intelligence file")
    if planner:
        allowed.append("your own planner dialogue log")
    extras = (", " + ", and ".join(allowed)) if allowed else ""
    seed_sec = SEED_SECTION.format(ARM=armstr) if seed_on else ""
    planning_sec = ""
    if planner:
        and_seed = " and the same seed intelligence" if seed_on else ""
        intro_t = PARTNER_INSPIRE if a.planner_prompt == "inspire" else PARTNER_NEUTRAL
        intro = intro_t.format(AND_SEED=and_seed,
                               SEED_REF=" and the seed file" if seed_on else "")
        notes = NOTES_MAILBOX.format(ARM=armstr) if transport == "mailbox" else ""
        retry = RETRY_API if transport == "api" else RETRY_CLI
        if transport == "mailbox":
            retry = "- If the consult command errors, retry it once; if it still fails, note it in the journal and continue playing."
        planning_sec = PLANNING_COMMON.format(
            PARTNER_INTRO=intro, ARM=armstr, TRANSPORT_NOTES=notes, RETRY_NOTE=retry)
    prompt = PLAYER_BASE.format(
        BENCH=str(BENCH), ARM=armstr, SEED_SECTION=seed_sec,
        PLANNING_SECTION=planning_sec, ALLOWED_EXTRAS=extras,
        NO_CONSULT_AT_WIN=", do not consult the planner" if planner else "",
        WIN_RESUME=(" When the operator tells you to continue, do the end-of-ante-8"
                    " consultation first (it is an ante boundary), then resume playing"
                    " into endless." if planner else ""),
    )
    if not planner:
        prompt = prompt.replace(" Consultations continue at every ante boundary in endless.", "")

    # ---- stage files
    arm.mkdir(parents=True)
    (arm / ".claude").mkdir()
    (arm / "prompt.txt").write_text(prompt, encoding="utf-8")
    if seed_on:
        shutil.copy(TEMPLATES / "BENCHMRK_analysis.txt", arm / "BENCHMRK_analysis.txt")

    if planner:
        if transport == "mailbox":
            shutil.copy(TEMPLATES / "consult-mailbox.py", arm / "consult.py")
            shutil.copy(TEMPLATES / "planner-console.py", arm / "planner-console.py")
        elif transport == "api":
            shutil.copy(TEMPLATES / "consult-api.py", arm / "consult.py")
            (arm / "planner-config.json").write_text(
                json.dumps({"model": planner, "max_tokens": 4096 if planner.startswith("claude-3") else 16000}, indent=2),
                encoding="utf-8")
        else:
            shutil.copy(TEMPLATES / "consult-cli.py", arm / "consult.py")
            (arm / "planner-config.json").write_text(
                json.dumps({"model": planner}, indent=2), encoding="utf-8")
            (arm / "planner" / ".claude").mkdir(parents=True)
            shutil.copy(TEMPLATES / "planner-tools-deny.json",
                        arm / "planner" / ".claude" / "settings.local.json")
        seed_block = ""
        if seed_on:
            seed = (arm / "BENCHMRK_analysis.txt").read_text(encoding="utf-8-sig").strip()
            seed_block = SEED_BLOCK.format(SEED=seed)
        briefing = (ROLE_HEADER + ROLES[a.planner_prompt]
                    + ROLE_PROTOCOL.format(PLAYER_PROMPT=prompt.strip(), SEED_BLOCK=seed_block))
        (arm / "planner-briefing.md").write_text(briefing, encoding="utf-8")

    # ---- sandbox: deny every sibling arm + bench records; allow own tools
    def both_styles(rel):
        fwd = f"C:/Users/maaro/OneDrive/Desktop/balatro-bench/{rel}".replace("\\", "/")
        back = ("C:\\Users\\maaro\\OneDrive\\Desktop\\balatro-bench\\" + rel).replace("/", "\\")
        return [f"Read({fwd})", f"Read({back})"]

    deny = []
    for rel in [".secrets/**", "runs/**", "analysis/**", "*.md", "templates/**", "seedtool/**"]:
        deny += both_styles(rel)
    for sib in sorted(p.name for p in ARENA.iterdir() if p.is_dir() and p.name != name):
        deny += both_styles(f"arena/{sib}/**")
    deny += ["Read(C:/Users/maaro/.claude/**)", "Read(C:\\Users\\maaro\\.claude\\**)",
             "Grep", "Glob", "Agent", "Task", "WebSearch", "WebFetch"]
    allow = [f'Bash(powershell -NoProfile -ExecutionPolicy Bypass -File "{BENCH}\\bench-rpc.ps1" *)']
    if planner:
        allow.append(f'Bash(python "{arm}\\consult.py" *)')
    (arm / ".claude" / "settings.local.json").write_text(
        json.dumps({"permissions": {"allow": allow, "deny": deny}}, indent=2),
        encoding="utf-8")

    # ---- add this arm to every sibling's deny list
    for sib in ARENA.iterdir():
        s = sib / ".claude" / "settings.local.json"
        if sib.name == name or not s.exists():
            continue
        data = json.loads(s.read_text(encoding="utf-8-sig"))
        d = data.setdefault("permissions", {}).setdefault("deny", [])
        for entry in both_styles(f"arena/{name}/**"):
            if entry not in d:
                d.append(entry)
        s.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # ---- manifest
    (arm / "run-config.json").write_text(json.dumps({
        "staged": datetime.date.today().isoformat(),
        "player": a.player,
        "planner": planner,
        "planner_prompt": a.planner_prompt if planner else None,
        "planner_transport": transport,
        "seed_info": seed_on,
        "arm": name,
    }, indent=2), encoding="utf-8")

    # ---- launch commands
    print(f"Staged: {arm}")
    print(f"Condition: player={a.player} planner={planner or 'none'}"
          + (f" planner_prompt={a.planner_prompt} transport={transport}" if planner else "")
          + f" seed_info={'on' if seed_on else 'off'}")
    if transport == "mailbox":
        print("\nPlanner console (open FIRST, its own window):")
        print(f'  cd /d "{arm}" && python planner-console.py')
    print("\nPlayer launch (cmd):")
    print(f'  cd /d "{arm}" && powershell -NoProfile -Command'
          f' "claude --model {a.player} --permission-mode auto (Get-Content prompt.txt -Raw)"')


if __name__ == "__main__":
    main()
