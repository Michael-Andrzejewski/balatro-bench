You are the PLANNER for ONE run of Balatro in a benchmark. You will not play. Your whole job is to write one plan file, as good as you can make it.

## The setup
- The run: seed BENCHMRK, Red Deck, White Stake, solo (no lives: failing any blind's chip requirement ends the run). The score is the highest ante reached; the single biggest hand is the tiebreak. The base game is won by beating ante 8, and the run then continues in Endless mode, so antes past 8 count.
- After you finish, a FRESH instance of your own model ({MODEL_NAME}) will play the run through a game API. It will have the standard player instructions (copied at the end of this prompt so you know exactly what it sees) and your plan file. It will NOT have the seed analysis, this prompt, or anything else you read or thought. Your plan file is the only thing that crosses over.
{PLANNER_NOTE}
## Your inputs
The full seed analysis of BENCHMRK:

    {ARENA}\BENCHMRK_analysis.txt

For each ante it lists the boss, the voucher, the tags, the shop item queue, and pack contents. Read it and use it however you like. Do NOT read, list, or search any other files. You cannot reach the game, and you must not try to.

## Your limits
- Context: up to 200,000 tokens for this whole session (everything you read, think, and write). The harness stops you when you reach 200,000, so leave room to write the plan.
- The plan file: at most 30,000 tokens, counted with your real tokenizer. Check it any time with:

      python "{COUNTER}" "{ARENA}\plan.md"

  It prints TOKENS=<n> LIMIT=30000 OK or OVER. When you finish, the harness counts it again. If it is over the limit, you will be asked to rewrite it shorter.

## Your output
Write the plan to:

    {ARENA}\plan.md

It can contain anything you think will help the player reach the highest ante: routes, what to buy and skip and when, boss preparation, contingencies, reasoning, excerpts of the seed data. You decide what is worth the space. When the plan is done and the counter says OK, end with one line: PLAN READY tokens=<n>

---
The player's instructions, verbatim (paths are the player's own):

{PLAYER_PROMPT}
