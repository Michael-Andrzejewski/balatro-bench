# General decision harnesses for BalatroBench and other benchmarks

Research report, 2026-10-05. Revised the same day after Michael widened the scope: he wants one general planning and decision harness he can point at BalatroBench and at his other decision benchmarks, not a Balatro-only design.

Scope rule followed: no lookup of the benchmark seed, the balatro-bench repo, or prior runs on it. Claims marked "speculative" are my inference, not measured results. Model names and dates are as reported by the sources.

## Short answer

1. **The best ARC-AGI-3 harnesses share one design.** The agent keeps a complete, append-only log of everything it observed. It writes its beliefs about the environment's rules as code. It must check that code against the log ("retrodiction": does my rule explain everything that already happened?) before it spends real actions. It plans by searching inside that checked code, and it attaches a predicted outcome to every action, so any surprise stops the plan at once. Tycho, Retrodict, Schema, Kepler, baseline1, OPINE-World and NOOA all do some version of this. They reach 85 to 100% on the ARC-AGI-3 public set with frontier models.
2. **One capable agent with a file workspace beats role-played teams.** On the same leaderboard, NVIDIA's six-role "DreamTeam" scored 38.1% for $18,000. A single NOOA agent with a 45-line world-modeling skill scored 85.1% for $332. An evolved 9-skill multi-agent system scored 12.3% for $5,300.
3. **The swarm's failure is the failure these harnesses are built to prevent.** It stated rules it had not checked against any evidence (no retrodiction), and its agents argued instead of testing. The research on multi-agent debate says the same thing: copies of one model debating each other mostly reinforce the beliefs they already share.
4. **Caveat:** the near-100% results are all on the 25 public ARC-AGI-3 games, which the authors also used for development. ARC Prize's own neutral harness on the hidden semi-private set gave Claude Opus 5 30.2% and GPT-6 Astra 62.7%. Astra rose to 99.9% when its reasoning state was kept and long conversations were compacted. So the harness matters a great deal, but nobody has shown how much of the public-set gain carries over to unseen environments.

The ranked designs are at the end. Most of them are available as code today.

## 1. ARC-AGI-3: what scored highest and how

ARC-AGI-3 is interactive. Each game is a turn-based grid world with no instructions. The agent has to explore, work out the goal and the rules, and finish levels using as few actions as possible. The score is RHAE (relative human action efficiency, 100 = matches or beats humans on every level). Sources: [technical report](https://arxiv.org/html/2603.24621), [community leaderboard](https://arcprize.org/leaderboard/community).

### Leaderboards

**Community leaderboard, public set (25 games, 183 levels)**, from [arcprize.org/leaderboard/community](https://arcprize.org/leaderboard/community):

| System | Score | Cost | Core idea |
|---|---|---|---|
| Tycho (Lehmann, Aioanei, Vahdati) | 100.0% | $2,986 | Actor agent plus a delegated world-model builder; plans by search inside the model |
| Retrodict (Ryan Brown) | 99.9% | $654 | Logs every frame; rule hypotheses must retrodict the log before live actions |
| baseline1 (Sergey Rodionov) | 99.0% | $400 | Coding agent that builds, verifies, and simplifies an executable Python world model |
| NOOA (NVIDIA Labs) | 85.1% | $332 | Single CodeAct agent with a short world-modeling skill and persistent memory |
| OPINE-World (Courtis, Li, Sanner) | 78.4% | $1,040 | Two agents in a counterexample-guided synthesis loop |
| Vision Continual Learning v1 | 63.1% | $4,788 | Multimodal agent whose weights update across games |
| Read-Grep-Bash Agent (Fox et al.) | 50.2% | n/a | General coding agent searching game logs with grep and Python |
| TELL (Dots) | 43.9% | $1,406 | One conversation that builds up confirmed knowledge in a MEMORY.md file |
| DreamTeam (NVIDIA) | 38.1% | $18,000 | Six fixed roles sharing a file workspace |
| Continual Harness (Feng et al.) | 20.5% | $774 | A Refiner that rewrites its own policy |
| Polyphony | 19.8% | $115 | Grows verified per-game heuristics as Python files |
| a-evolve MAS Evolved | 12.3% | $5,300 | Evolved multi-agent orchestrator with 9 learned skills |
| OpenClaw (ARC Prize adaptation) | 5.2% | $2,912 | General open-source harness with memory and code tools |

Also reported: Schema ([site](https://schema-harness.github.io/), [HN](https://news.ycombinator.com/item?id=48935905)) at about 99% with Claude Opus 4.8 plus Fable 5, and 95.35% with GPT-5.6 Sol. Its controlled comparison: **Claude Code alone on the same models scored 42.83%; with Schema, 98.98%.** Kepler ([arXiv 2610.00834](https://arxiv.org/html/2610.00834)) reports 100.00 with Claude Opus 5 for $778 (97% cache reads) and 95.97 with GPT-5.6 Sol. Agno's ARC-AGI-Arcade ([article](https://www.agno.com/articles/arc-agi-arcade)) reports 100% with GPT-5.6.

**Verified on the hidden semi-private set** ([ARC Prize Astra post](https://arcprize.org/blog/astra), [results page](https://arcprize.org/results/openai-gpt-6-astra)): ARC Prize's provider-neutral Standard harness, in which the model chooses which notes to carry forward, scored Claude Opus 5 at 30.2% (July 2026) and GPT-6 Astra at 62.7% ($26K). Astra scored 99.9% ($19K) with a Provider Adapter harness that keeps the model's reasoning state between turns and compacts long conversations. ARC Prize notes that Astra built its own parsers, solvers and state trackers when given a sandbox.

**Offline Kaggle competition** ([Milestone #1 post](https://arcprize.org/blog/arc-prize-2026-milestone-1)): small local models only. First place, Tufa Labs' "Duck" (Qwen 3.6 27B writing Python in a live REPL), scored 1.21% on the private set ([Tufa Labs](https://x.com/tufalabs/status/2072336849465417747)). Tufa found that hand-built tools hurt and letting the model improvise helped. The 2025 preview competition was won by StochasticGoose at 12.58%, a CNN plus RL that predicted which actions change the frame ([preview results](https://arcprize.org/competitions/arc-agi-3-preview-agents)).

### What the top harnesses actually do

**Tycho** ([arXiv 2607.28287](https://arxiv.org/html/2607.28287), [code, Apache-2.0](https://github.com/NIMI-research/Tycho))
- Two agents. Only the **actor** can take actions. A **model-builder** sub-agent writes and repairs a Python world model with four functions (`init_state`, `transition`, `render`, `outcome`), proposes plans, and gives advice.
- **Verification:** the whole interaction record is replayed through the model. A transition counts as matched only if every cell the model claims matches the real next frame. The model may decline to predict cells it is unsure of.
- **Planning:** breadth-first search inside the model until it reaches a state the model classifies as level-complete. The route is replayed and saved with a hash of each frame. The actor treats it as advice and re-checks after every real action. Any mismatch voids the route.
- **Memory:** a workspace on disk per game. Raw evidence is stored apart from notes and models. The conversation is cleared at each level boundary after a summary is written. A library lets the actor query exact past transitions.
- **Ablation** (same model, Opus 4.8): no world model 79.07; actor builds its own model 85.36; **actor asks a separate builder 88.49**; automatic repair whenever verification fails 83.07. The last policy had the best prediction accuracy (88.1% of transitions matched) and the worst score of the model-using policies. Accurate prediction alone does not win; deciding when to model and when to just act matters.
- Results: Opus 5 and GPT-5.6 Sol each cleared 183 of 183 levels. Opus 5 used 6,641 actions for about $2.99K, 61% fewer actions than the human baselines.

**Retrodict** ([code](https://github.com/ryanbbrown/Retrodict))
- GPT-5.6 Sol at max reasoning. Works on text and code only; no images after a short priming step.
- Files: `log.txt` (every frame, ground truth), `playbook.md` (the current model of the game plus working memory; survives context resets), and a scratch folder of game-specific helper code.
- Tools: read, write, edit, search, and a sandboxed Python with numpy, scipy and networkx. No shell.
- Rule: hypotheses are tested by Python that replays them over past frames, which costs nothing. Only questions the log cannot answer earn real actions. **Every action carries an `expect` prediction of exact cells.** A mismatch halts the plan and re-invokes the model with the difference.
- Escalation: after 300 actions stuck on one level, the runner forces "list what the log leaves unexplained, turn checked rules into an executable step simulator, verify it against every frame, search it for a route." After 600 actions it forces work on unexplored states.
- Context resets at 150K tokens; only files survive. Totals: 7,703 actions, 660M tokens, $654.
- Built on [ThinHarness](https://pypi.org/project/thinharness/0.8.0/), a small general-purpose plugin harness by the same author.

**baseline1** (Rodionov; [code](https://github.com/astroseger/arc-3-agents-baseline1), [paper](https://arxiv.org/abs/2605.05138), [ablation paper](https://arxiv.org/html/2607.15439))
- A coding agent with a scripted controller, fixed world-model interfaces, verifier programs and a plan executor. No game-specific logic.
- **The ablation is the most important result in this report for harness design.** With GPT-5.4 and GPT-5.5 at two effort levels:
  - Requiring an executable world model, compared with notes in plain text, was mixed: one setting gained 4.05 points, three lost between 0.62 and 7.69. The authors say an open-ended simulator requirement "diverts effort from direct game solving."
  - Adding simplification (refactoring the model toward simpler rules) helped in 3 of 4 settings (+3.4 to +8.4).
  - **Adding verification ranked first in all four settings** (+0.6 to +8.6 points), and cost 1.8 to 3.3 times more tokens.
  - With GPT-5.6 Sol at max effort, plain-text notes alone completed the public set with 41% fewer actions than humans. "Capability and reasoning effort dominate."

**NOOA** ([paper](https://arxiv.org/html/2607.20709v1), [NVIDIA blog](https://developer.nvidia.com/blog/six-agent-harness-capabilities-for-higher-model-performance/), code at nvidia-nemo/labs-OO-Agents, CC BY 4.0)
- A general framework, not an ARC harness. An agent is a Python object: methods are its actions, fields are its state, docstrings are its prompts. The model acts by writing Python (CodeAct).
- ARC-AGI-3: a single agent with a roughly 45-line world-modeling skill. The skill says to keep an executable model of the game, predict the next state, use retrodiction as the refinement signal, and submit each batch of actions as an experiment with a rationale. 50.2% with GPT-5.5 and 85.1% with GPT-5.6 Sol, at $13 to $20 per game. **Measured effects: the memory system added 11.8 points and the world-modeling skill 8.5.**
- Same harness on other benchmarks: SWE-bench Verified 82.2%, Terminal-Bench 2.0 73.0%, CyberGym L1 86.8% (GPT-5.5). Tested with several model families. **This is the strongest evidence I found of one harness doing well across very different decision benchmarks.**

**OPINE-World** ([arXiv 2607.01531](https://arxiv.org/html/2607.01531v2))
- One agent explores; a separate synthesis agent writes and repairs the world model from a shared replay buffer. When the model fails to predict a transition, the synthesizer **starts fresh instead of the original author defending its hypothesis**. The paper says this is what prevents fixation. A periodic critic hunts for cases the model gets wrong.
- Exploration is steered toward objects whose behavior the current model explains worst (a Bayesian "ontology error" score).
- A program is accepted only if it reproduces every transition in the buffer exactly. 20 of 25 games cleared versus 14 for baseline1 in their comparison. No ablation.

**PRO-LONG and the Read-Grep-Bash agent** ([PRO-LONG paper](https://arxiv.org/html/2607.20064), [code, MIT](https://github.com/alexisfox7/PRO-LONG), [RGB-Agent](https://github.com/alexisfox7/RGB-Agent))
- Memory is just an append-only log of every observation, action and outcome. The agent reads it with grep and code, not summaries.
- Installs as hooks into Claude Code, Codex, OpenCode or pi. No wrapper or server.
- Claude Code with PRO-LONG: 82.1% best-of-2, close to Schema's 84.4%, with 4.2 times fewer tokens. Fable 5 with a bigger budget: 97.4% best-of-2 for $1,750. Only tested on ARC-AGI-3.

**Agno ARC-AGI-Arcade** ([article](https://www.agno.com/articles/arc-agi-arcade), code at agno-agi/arc-agi-arcade)
- Python kernel loaded with the run history, a store of learned mechanics, and per-game manuals ("mechanics, hazards, hypotheses") that the agent corrects when observations prove them wrong.
- **Transfer result:** Gemini 3.7 Flash went from 37.33 to 96.42 when given GPT-5.6's manuals, using 3 times fewer tokens. A strong model's verified notes made a cheap model nearly as good.

**Warnings about the public set**
- [Explore Before You Solve](https://arxiv.org/abs/2605.25931): many public games can be solved with no intelligence at all (10 in a single blind step, 5 after one probing action). The authors call the 55-game private set the real test.
- Kepler's authors say directly that their results "establish neither held-out generalization nor private-set performance," and that the harness's own contribution is unmeasured.
- [DEV Community](https://dev.to/p0rt/the-model-scored-30-the-harness-scored-100-which-one-did-you-benchmark-3mp4) and the Schema HN thread note that the gap between "model in the official harness" and "model in the best harness" is 25 to 70 points on the public set, and none of the 100s are verified on hidden games.

### What carries over to a general harness

Several of these results come from controlled comparisons, not just leaderboard rankings:
- **Verification against recorded history** is the one component that helped in every setting of the only clean ablation (baseline1), and it is in every top system.
- **Memory that survives context resets** (an append-only log plus a curated playbook) added 11.8 points in NOOA, and PRO-LONG matched specialist harnesses with it at a quarter of the tokens.
- **Keeping the model's reasoning state and compacting context** took Astra from 62.7% to 99.9% on hidden games, the largest measured effect.
- **A separate builder or synthesizer for the world model** helped Tycho (85.36 to 88.49) and is OPINE-World's defense against fixation.
- **Actions that carry predictions** (Retrodict, Tycho) turn every step into a test, so wrong beliefs surface quickly.

Weaker or negative findings:
- Requiring a full executable simulator is not automatically good (baseline1 ablation). It pays off when the rules are deterministic and the planning horizon is long.
- Fixed multi-role teams did poorly on cost and score (DreamTeam, a-evolve MAS).
- Hand-built tools hurt a small model (Tufa Labs).
- Model capability and reasoning effort mattered more than any harness component in the baseline1 study.

## 2. Why the swarm failed: verification versus debate

This section applies to any benchmark.

**Models do not reliably check themselves.** Without outside feedback, self-correction often makes answers worse ([Huang et al. 2023](https://arxiv.org/abs/2310.01798)). Self-critique hurt on graph coloring while an outside verifier helped ([Stechly et al. 2023](https://arxiv.org/abs/2310.12397)). The LLM-Modulo approach (the model proposes, outside verifiers critique, repeat) took GPT-4-Turbo on TravelPlanner from a 4.4% baseline to 20.6% ([Kambhampati et al., ICML 2024](https://proceedings.mlr.press/v235/kambhampati24a.html); [case study](https://arxiv.org/abs/2405.20625)). The Gemini Plays Pokemon builder saw the model invent mechanics, for example believing Full Heal restored HP ([blog](https://blog.jcz.dev/the-making-of-gemini-plays-pokemon)). That is the same kind of error as the swarm's Death tarot mistake.

**Debate among copies of one model mostly amplifies what they already believe.**
- [Debate or Vote](https://arxiv.org/abs/2508.17536) (NeurIPS 2025): plain majority voting matched multi-agent debate on 7 benchmarks. The authors prove that debate does not, on average, move agents toward the right answer; the gains come from the vote.
- [Talk Isn't Always Cheap](https://arxiv.org/abs/2509.05396): accuracy can fall over debate rounds, even when stronger models are the majority, because agents switch from right to wrong answers in order to agree.
- [The Cost of Consensus](https://arxiv.org/abs/2605.00914): with identical models, agents adopted the majority answer up to 85.5% of the time. Voting threw away correct answers that some agent had already found (up to a 32.3-point gap between "someone had it" and "the group chose it"). Debate also cost 2.1 to 3.4 times more tokens.
- [Emergence of Biased Consensus](https://arxiv.org/html/2608.02827v1): once conformity passes a threshold, the group locks into a shared bias.
- Older context: [Du et al. 2023](https://arxiv.org/abs/2305.14325) (the original positive debate result), [Should we be going MAD?](https://arxiv.org/abs/2311.17371), [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657).

**Sampling only pays off when something can check the samples.** [Self-consistency](https://arxiv.org/abs/2203.11171) works for short answers that can be compared. [Large Language Monkeys](https://arxiv.org/abs/2407.21787): the chance that at least one sample is right keeps rising as you draw more, but only an automatic verifier can pick it out; voting levels off.

**Search over model proposals needs real feedback and the ability to undo.** [Tree of Thoughts](https://arxiv.org/abs/2305.10601), [RAP](https://arxiv.org/abs/2305.14992), [LATS](https://arxiv.org/abs/2310.04406) (92.7% HumanEval pass@1; depends on environment feedback and returning to earlier states). [PokeChamp](https://arxiv.org/abs/2503.04094): minimax search with the model proposing moves and estimating value, plus an exact damage calculator. It won 76% against the best earlier LLM bot and 84% against the best rule bot. [Cicero](https://www.science.org/doi/10.1126/science.ade9097): a language model paired with a planning engine reached human-level Diplomacy.

**Lessons from earlier attempts.** [Reflexion](https://arxiv.org/abs/2303.11366) carries short written lessons into the next try. [Voyager](https://arxiv.org/abs/2305.16291) uses environment feedback, self-verification against game state, and a library of code skills: 3.3 times more unique items and up to 15.3 times faster tech-tree progress. [FunSearch](https://www.nature.com/articles/s41586-023-06924-6) and [AlphaEvolve](https://arxiv.org/abs/2506.13131) evolve programs against an automatic scorer.

## 3. Other general harnesses with cross-benchmark evidence

| Harness | Domain-general? | Model-agnostic? | Evidence | Code |
|---|---|---|---|---|
| **NOOA** | Yes: one framework across SWE-bench, Terminal-Bench, CyberGym, ARC-AGI-3 | Yes (GPT, Claude, Nemotron) | 82.2% SWE-bench Verified, 73.0% Terminal-Bench 2.0, 85.1% ARC-AGI-3 public | nvidia-nemo/labs-OO-Agents, CC BY 4.0 |
| **PRO-LONG** | The design is general; tested only on ARC-AGI-3 | Yes; hooks into Claude Code, Codex, OpenCode, pi | Matched specialist harnesses at 4 to 6 times fewer tokens | [MIT](https://github.com/alexisfox7/PRO-LONG) |
| **Tycho** | The world-model interface is general for deterministic environments with observable state; the code is ARC-shaped | Claude and GPT tested | 100 public; clean ablation | [Apache-2.0](https://github.com/NIMI-research/Tycho) |
| **Retrodict / ThinHarness** | ThinHarness is general; Retrodict's prompts target ARC | GPT tested | 99.9 public at the lowest cost among the top entries | [repo](https://github.com/ryanbbrown/Retrodict), [PyPI](https://pypi.org/project/thinharness/0.8.0/) |
| **Continual Harness** | General: refines prompts, sub-agents, skills and memory during a run | Gemini, Gemma | Pokemon Red and Emerald (100% of milestones on Emerald at about 40% lower cost); 20.5% ARC-AGI-3 | [arXiv 2605.09998](https://arxiv.org/html/2605.09998), [repo](https://github.com/sethkarten/continual-harness/tree/main) |
| **Gemini Plays Pokemon** | Pokemon-specific, but the lessons are general (text state, sub-agents with clean contexts, goals, summaries) | Gemini | Finished Blue, Yellow Legacy on hard, and Crystal | [blog](https://blog.jcz.dev/the-making-of-gemini-plays-pokemon) |
| **BALROG** | A benchmark suite, not a harness | n/a | Finds that models know a lot but act poorly over long horizons, and that image input often hurts | [arXiv 2411.13543](https://arxiv.org/abs/2411.13543) |
| **OpenClaw** | General | Yes | Only 5.2% on ARC-AGI-3 even with memory and code tools added | leaderboard |

Takeaway: general coding-agent harnesses (Claude Code, Codex, NOOA's CodeAct loop) do transfer, but only after adding three things: a durable log with code-based search, a verification habit, and a world-modeling skill. OpenClaw without the discipline scored 5.2%. Plain Claude Code scored 42.83% on the same task where Schema reached 98.98%.

## 4. Ranked general harness designs

All five keep the model as the decision maker, except where flagged. Each needs the same small **environment adapter** for a new benchmark:
- `observe()`: returns the state as structured text (JSON), never only an image.
- `legal_actions()` and `act(action)`: return the new observation and any reward or terminal flag.
- Optional `snapshot()` and `restore()` if the benchmark allows undo or practice (BalatroBot has `save` and `load`).
- A logger that appends every observation and action to `log.jsonl`.

### Design 1. Claude Code plus an append-only log, with reasoning state kept (cheapest; available today)

- **What:** run the agent as a single long Claude Code or Agent SDK session, not a stateless prompt per step. Install PRO-LONG's hooks (or a 50-line equivalent) so every observation goes to an append-only log the agent searches with grep and Python. Keep a curated `playbook.md` that survives context compaction.
- **Build cost:** a day or two per benchmark, mostly the adapter.
- **Evidence:** PRO-LONG with Claude Code 82.1% on ARC-AGI-3 at 4.2 times fewer tokens. NOOA's memory added 11.8 points. Astra's 62.7% to 99.9% from keeping reasoning state and compacting context. Retrodict and Tycho both rely on files that survive resets.
- **Gap:** no verification discipline. On its own this is the "Claude Code alone, 42.83%" end of Schema's comparison.

### Design 2. Retrodiction-gated actions (add a verification skill; available today)

- **What:** on top of Design 1, a short skill in the style of NOOA's 45 lines or Retrodict's rules:
  - Every claim about how the environment works is written as a small Python predicate or function.
  - It must be replayed against the log before it is used. If the log cannot settle it, design the cheapest experiment that can.
  - Every committed action carries an expected outcome. The runner compares and halts the plan on any mismatch.
  - An escalation rule: after N stuck steps, list what is unexplained and what is unexplored.
  - An **option-coverage rule** for planning benchmarks: every available option gets a written verdict and a reason. This fixes "saw the key joker and ignored it."
- **Build cost:** days. A skill file, a prediction checker in the runner, and an escalation counter.
- **Evidence:** in the baseline1 ablation, verification was the top variant in all four settings. NOOA's world-modeling skill added 8.5 points. Retrodict reached 99.9 for $654. LLM-Modulo took TravelPlanner from 4.4% to 20.6%.
- **Fit:** fully domain-general. This is the single best value for money.

### Design 3. Separate world-model builder plus search planner (Tycho, Schema or OPINE pattern; Tycho code available)

- **What:** an actor agent owns all real actions. A builder sub-agent, started fresh whenever the model is falsified, writes an executable transition model (`init_state`, `transition`, `outcome`) and must reproduce the log exactly. A planner searches inside the accepted model (breadth-first search, beam search, or an expectation over chance outcomes for stochastic games) and hands the actor a route with predicted observations. The actor re-checks after each step.
- **Build cost:** one to three weeks to make Tycho's interface general and add an adapter per benchmark. Stochastic environments need a probabilistic `transition`. That works for Balatro, whose randomness is fixed by the seed.
- **Evidence:** Tycho's ablation (79.07 with no model, 88.49 with a delegated builder). Schema 42.83 to 98.98 over plain Claude Code with Claude models. OPINE-World cleared 6 games baseline1 could not. Caveat: baseline1 found that a forced simulator can hurt when it is not needed, and Tycho found that forced automatic repair hurt.
- **Fit:** best for deterministic or seeded environments where looking far ahead pays: Balatro, puzzles, planning tasks. Overkill for short tasks. The agent writes its own simulator during the run, so the model stays the decision maker.

### Design 4. Cross-run manuals and a self-refining harness (Agno Arcade, Continual Harness; code available)

- **What:** after each run, the strongest model writes or corrects a per-environment manual (mechanics, hazards, confirmed rules, each with its evidence). The next run starts with it. Optionally a Refiner edits prompts and skills between runs.
- **Build cost:** days on top of Design 2.
- **Evidence:** Gemini Flash went from 37 to 96 on ARC-AGI-3 when given GPT-5.6's manuals. Continual Harness recovered most of the gap to expert-built harnesses on Pokemon. Reflexion and Voyager.
- **Rules flag:** for a fixed-seed benchmark, carrying knowledge across runs is a form of practice. It needs an explicit ruling (for example a separate "practiced" track, or manuals allowed only from other seeds or other benchmarks).

### Design 5. Search engine or evolved policy that plays for the model (most ambitious; replaces the model)

- **What:** a human-built or model-evolved program (FunSearch or AlphaEvolve style, or MCTS in a pre-built simulator) makes the in-game decisions; the model only proposes or tunes.
- **Evidence:** PokeChamp, Cicero, AlphaEvolve. The balatro-rl author's conclusion after PPO stalled (see appendix).
- **Flag:** this is outside "the AI plays" for BalatroBench and most decision benchmarks. Put it in a separate "AI-built bot" category next to the rule bot.

### Summary

| Rank | Design | Code today | Build effort | Evidence strength | Model decides? |
|---|---|---|---|---|---|
| 1 | Claude Code session plus append-only log and playbook | Yes (PRO-LONG, MIT) | 1 to 2 days per benchmark | Good | Yes |
| 2 | Plus retrodiction-gated actions and option coverage | Partly (NOOA skill, Retrodict prompts) | Days | Strongest single component | Yes |
| 3 | Plus a fresh-context world-model builder and search planner | Yes (Tycho, Apache-2.0) | 1 to 3 weeks | Good on public set; held-out gains unknown | Yes, the agent writes its own simulator |
| 4 | Plus cross-run manuals and refinement | Yes (Agno Arcade, Continual Harness) | Days | Good | Yes, but needs a practice ruling |
| 5 | Pre-built search or evolved policy | Partly | Weeks to months | Strong in other games | No, separate category |

Speculative: whether the public-set gains carry over to unseen environments, and how much each component adds on Balatro-style planning, where the rules are knowable in advance rather than hidden. My expectation is that Design 2 helps most there, because the swarm's errors were unchecked rule claims, not missing exploration.

## Appendix: plugging BalatroBench into a general harness

**Adapter.** BalatroBot already serves JSON-RPC 2.0 with full game state and has `save`, `load`, `set` and `add` methods ([API](https://coder.github.io/balatrobot/latest/api/)). Wrap it as `observe` / `act` / `snapshot` / `restore` and log every state to `log.jsonl`. The seed-analysis file becomes a read-only document in the workspace.

**Rules grounding (Design 2 for Balatro).** Balatro's rules are knowable: the game's Lua source ships inside Balatro.exe, which is a LOVE archive. Give the agent grep over it. Require each rule claim to cite a source line or a sandbox experiment, built with `add` and `set` and observed in the game. This directly targets the Death tarot and Glass errors.

**Lookahead (Design 3 for Balatro).** Balatro saves its RNG state with the run, so a loaded save replays identically ([Steam thread](https://steamcommunity.com/app/2379780/discussions/0/604151850480996889/), [PSNProfiles](https://forum.psnprofiles.com/topic/180277-save-scumming-and-seed-tracking-helps-with-completionist-and-runs-in-general-including-for-rule-breaker/)). That makes the real game an exact but slow simulator, if a sandbox copy is allowed. Faster options:

| Engine | Status |
|---|---|
| [jackdaw-balatro](https://github.com/TylerFlar/jackdaw-balatro) (Python, MIT) | Claims a bit-exact LuaJIT PRNG, all 150 jokers, and about 250 live-versus-sim diff scenarios. No pass rate or game version published ([validation.md](https://github.com/TylerFlar/jackdaw-balatro/blob/main/docs/validation.md)). The best fast candidate; validate it on this seed first. |
| [balatro-rs](https://github.com/evanofslack/balatro-rs) (Rust) | Byte-accurate RNG, but only 74 of 150 jokers and no skip tags. Fine for hand-level search only. |
| [balatro-rl sim](https://github.com/taggarttufte/balatro-rl) | 496 tests, about 1,535 steps per second. An audit found about 30% of its jokers implemented wrong in earlier versions: hand-written rule models are often wrong. PPO peaked at a 2.35% win rate; the author recommends MCTS with priors. |
| [balatro-gym](https://github.com/cassiusfive/balatro-gym) | No fidelity evidence published. |
| Seed tools: [Immolate](https://github.com/SpectralPack/Immolate), [TheSoul](https://github.com/SpectralPack/TheSoul), [Blueprint](https://miaklwalker.github.io/Blueprint/) | Faithful RNG reimplementations used for seed analysis. Some queues shift with player actions. |
| Scorers: [EFHIII calculator](https://github.com/EFHIII/balatro-calculator), [Balatro-Preview](https://github.com/DivvyCr/Balatro-Preview) | Reimplemented scoring; a few jokers may be wrong. Asking the game itself is safer. |

**Existing Balatro LLM agents for comparison.**
- [Attol8/balatro-ai](https://github.com/Attol8/balatro-ai): the model decides strategy while Python tools give exact scores, legal hands and discard outcomes. It reached ante 13 and a best hand of 1.3e11 on Red/White using public information only, and won two Black/Gold runs. It is evidence for exact tools, though no ablation is published.
- [coder/balatrollm](https://github.com/coder/balatrollm): a plain prompt-and-act loop with the last 10 actions as memory. It powers [balatrobench.com](https://balatrobench.com/), where Gemini 3 Pro won 9 of 15 runs to ante 8.

**Benchmark-spirit flags for BalatroBench.**
- Design 1 and 2 tools only answer factual questions: in spirit.
- A simulator the agent writes itself during the run (Design 3): in spirit by ARC's community convention.
- Save/load branching on a sandbox copy, or manuals carried across runs: practice. This needs a ruling and probably a separate track.
- A pre-built engine choosing moves (Design 5): a different category.
