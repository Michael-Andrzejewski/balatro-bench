"""Balatro Bench, swarm planning: five independent Claude Code instances plan one seed together.

  python swarm_run.py stage  --name swarm-1      # build the sandboxed folder (outside every git repo)
  python swarm_run.py canary --name swarm-1      # fresh-instance check: no memory, no git, no seed knowledge
  python swarm_run.py run    --name swarm-1      # run (or continue) the rounds until everyone signs off
  python swarm_run.py audit  --name swarm-1      # list tool calls touching paths outside the folder, and every web query

Roles: Keel (safe, survival-first), Kite (moonshot, naneinf), Loom (mediator), Assay (auditor), Arrow (writes and approves plan.md).
Each agent is its own persistent `claude -p` session (--session-id, then --resume). They share one folder:
the seed analysis, a message board, their own notes folders, and the plan. The only channel between them is
the board: each turn's final reply is posted there, and every agent receives every new post on its next turn.
Harness logs (raw transcripts) live in a sibling folder the agents cannot read.

Round order: Keel + Kite (in parallel) -> Loom -> Assay -> Arrow. When Arrow posts PLAN APPROVED, Keel, Kite,
Loom and Assay each review plan.md and post SIGN-OFF or OBJECTION. All four SIGN-OFF at 100% ends the run.
"""
import argparse, json, os, pathlib, re, shutil, subprocess, sys, threading, time, uuid

BENCH = pathlib.Path(__file__).resolve().parent.parent
RELAY = BENCH / 'relay'
ARENAS = pathlib.Path(r'C:\Users\maaro\BenchArenas')
HOME = pathlib.Path.home()
SEED_FILE = BENCH / 'arena' / 'opus55__solo__seed' / 'BENCHMRK_analysis.txt'
RPC = BENCH / 'bench-rpc.ps1'
COUNTER = RELAY / 'count_tokens.py'
MODEL = 'claude-opus-5-5'
MODEL_NAME = 'Claude Opus 5.5'
EFFORT = 'high'
PORT = 12347
PLAN_CAP = 30_000
TURN_TIMEOUT = 75 * 60
AGENTS = ['keel', 'kite', 'loom', 'assay', 'arrow']
REVIEWERS = ['keel', 'kite', 'loom', 'assay']
ENV = {**os.environ, 'CLAUDE_CODE_DISABLE_AUTO_MEMORY': '1', 'ENABLE_CLAUDEAI_MCP_SERVERS': 'false', 'PYTHONIOENCODING': 'utf-8',
       'CLAUDE_CODE_MAX_OUTPUT_TOKENS': '128000'}
sys.path.insert(0, str(RELAY))
import count_tokens  # noqa: E402

ROLES = {
    'keel': """You are KEEL. You argue for the SAFE, STANDARD strategy. Your priority is survival: no blind may ever fail.
For every ante, check the chip requirement against what the build will realistically score, with margin for bad draws and
boss effects. Prefer reliable economy, proven scaling, and buys that cannot brick. Point out every place where a riskier
idea could end the run. You are not against ambition; you are the one who makes sure the run is still alive to use it.""",
    'kite': """You are KITE. You argue for the AMBITIOUS, MOONSHOT strategy. Your priority is the ceiling: winning ante 8, then going
as deep into Endless as possible, aiming to hit naneinf (a hand score that overflows to "naneinf", past about 1e308).
Find the scaling engine this seed can actually assemble (exponential X-mult, retriggers, copying, Spectral/Tarot tricks,
vouchers, tags) and the exact route to it. Accept risk, but always name the risk and what it costs if it fails.""",
    'loom': """You are LOOM. You MEDIATE between Keel (safety) and Kite (moonshot). Find where they actually disagree, ante by ante,
and decide each point on the merits: take the moonshot line where it costs little survival, take the safe line where a
failure would end the run. Propose hybrids and decision rules ("if X shows up by ante N, pivot to Y"). Keep a running
decision log in notes/loom/decisions.md so the others can see what is settled and what is open.""",
    'assay': """You are ASSAY. You AUDIT everything said between the chats. Check every claim against the seed file: shop positions,
pack contents, costs, money totals per ante, interest, blind requirements, boss effects, and the game rules themselves
(you may check rules on the web). Catch arithmetic errors, misread seed lines, items assumed to be in the wrong shop,
and wrong rules. Quote the seed line you checked. Keep a running audit log in notes/assay/audit.md. Be specific and
blunt; an error you miss here ends the real run.""",
    'arrow': """You are ARROW. You WRITE and APPROVE the final plan. You are the only one who edits plan/plan.md. Turn the agreed
decisions into an ante-by-ante plan another AI can follow cold: what to buy, skip, sell, and when; blind skips; boss
preparation; money targets; pivot rules; and how to keep scaling through Endless toward naneinf. Keep it at most 30,000
tokens (check with the counter). Accept corrections from Assay and rulings from Loom; push back when something is wrong.
When the plan is complete, every open objection is resolved, and you are 100% confident it is the best route the team
can find, put PLAN APPROVED on a line by itself in your board message. Never write that phrase otherwise.
To count tokens, use the Bash tool with exactly the counter command from the brief (not PowerShell).""",
}


def say(*a): print(*a, flush=True)


def fwd(p): return str(p).replace('\\', '/')


def paths(name):
    root = ARENAS / name
    return {'root': root, 'harness': ARENAS / f'{name}-harness', 'board': root / 'board', 'plan': root / 'plan' / 'plan.md',
            'state': ARENAS / f'{name}-harness' / 'state.json'}


def load_state(name): return json.loads(paths(name)['state'].read_text())


def save_state(name, st): paths(name)['state'].write_text(json.dumps(st, indent=2))


def brief(p):
    player = (RELAY / 'player-prompt.md').read_text(encoding='utf-8').replace('{RPC}', str(RPC)).replace('{PORT}', str(PORT)) \
        .replace('{ARENA}', r'<player arena>').replace('{MODEL_NAME}', MODEL_NAME)
    r = p['root']
    return f"""# Balatro planning swarm: shared brief

You are one of five independent Claude instances planning ONE run of Balatro together. None of you will play.
Your team's job is one plan file, as good as it can possibly be.

## The run
- Seed BENCHMRK, Red Deck, White Stake, solo: there are no lives, so failing any blind's chip requirement ends the run.
- Score = highest ante reached; the single biggest hand is the tiebreak. The base game is won by beating ante 8, and the
  run then continues in Endless mode, so antes past 8 count.
- The team's aim: win the base game, then go as deep into Endless as possible, aiming to hit naneinf (a hand score so big
  the game displays "naneinf"), or come as close as possible.
- After you finish, a FRESH AI ({MODEL_NAME}) will play the run through a game API. It will have the standard player
  instructions (copied at the end of this brief) and your plan file. It will NOT have the seed analysis, this brief, the
  board, or your notes. The plan file is the only thing that crosses over.

## The team
- Keel: the safe, standard strategy; survival in every blind comes first.
- Kite: the ambitious moonshot; aims for naneinf.
- Loom: mediates between Keel and Kite and rules on disagreements.
- Assay: audits every claim against the seed file and the game rules.
- Arrow: writes plan/plan.md (the only one who edits it) and approves the final version.

## Your folder (the whole world you may touch)
    {r}
- {r}\\BENCHMRK_analysis.txt : the full seed analysis (per ante: boss, voucher, tags, shop queue, pack contents). The ONLY
  source of knowledge about this seed.
- {r}\\BRIEF.md : this brief.
- {r}\\board\\ : every message posted so far, numbered in order (read-only for you; the harness writes it).
- {r}\\notes\\<name>\\ : each agent's own notes. Write only in your own notes folder; you may read the others'.
- {r}\\plan\\plan.md : the plan. Only Arrow edits it; everyone may read it.
Do NOT read, list, or search anything outside this folder. You cannot reach the game, and you must not try to.

## The web
You may search the web for general Balatro knowledge (joker effects, rules, scoring, Endless blind sizes, naneinf
mechanics). Do NOT look up this seed, "BENCHMRK", any Balatro benchmark, or anyone's earlier runs or plans: the only
knowledge of this seed allowed in is the seed file itself.

## How you talk
- Each turn, the harness gives you every board message posted since your last turn.
- Your FINAL reply each turn is posted to the board as your message, for all four others to read. Start it with
  "To: <names or all>". Keep it under about 1,500 words; put long tables or derivations in your notes folder and cite the path.
- End every message with a line "CONFIDENCE: <0-100>%" (your confidence that the current plan is the best route the
  team can find), followed by a one-line reason.
- Disagree openly. Agreement you do not believe ends the real run.

## When the work is done
The run ends only when Arrow posts PLAN APPROVED and Keel, Kite, Loom and Assay each review plan/plan.md and reply
"SIGN-OFF" with CONFIDENCE: 100%. Keep messaging and working until you are 100% confident the team has found the best
route through this seed. Do not claim 100% to finish early; claim it only when you honestly cannot find a better route
or a remaining error.

## The plan's limits
- At most {PLAN_CAP:,} tokens, counted with the real tokenizer. Check it with:
      python "{COUNTER}" "{p['plan']}"
  It prints TOKENS=<n> LIMIT=30000 OK or OVER.
- It must stand alone: the player knows the game but not the seed. Anything from the seed the player needs (shop
  positions, pack contents, bosses) must be written into the plan.

---
The player's instructions, verbatim (paths are the player's own):

{player}
"""


def settings(p):
    keep = {p['root'].resolve()}
    deny_dirs = [d for d in HOME.iterdir() if d.resolve() not in (ARENAS.resolve(),)]
    deny_dirs += [d for d in ARENAS.iterdir() if d.resolve() not in keep]
    deny_dirs += [pathlib.Path(r'C:\Users\maaro\OneDrive'), HOME / '.claude', p['harness']]
    deny = []
    for d in sorted({fwd(x) for x in deny_dirs}):
        deny += [f'Read({d}/**)', f'Edit({d}/**)', f'Write({d}/**)']
    deny += ['Agent', 'Task'] + [f'WebFetch(domain:{d})' for d in
                                 ('github.com', 'raw.githubusercontent.com', 'gist.github.com', 'githubusercontent.com', 'x.com', 'twitter.com')]
    allow = ['WebSearch', 'WebFetch', f'Bash(python "{COUNTER}" *)', f'Bash(python "{fwd(COUNTER)}" *)', f'PowerShell(python "{COUNTER}" *)',f'Read({fwd(p["root"])}/**)', f'Edit({fwd(p["root"])}/**)', f'Write({fwd(p["root"])}/**)']
    d = p['root'] / '.claude'; d.mkdir(parents=True, exist_ok=True)
    (d / 'settings.local.json').write_text(json.dumps({'permissions': {'allow': allow, 'deny': deny}}, indent=2))


def stage(name):
    p = paths(name)
    for k in ('root', 'harness'):
        if p[k].exists(): sys.exit(f'{p[k]} already exists. Pick a new --name: a swarm folder is used once.')
    p['root'].mkdir(parents=True); p['harness'].mkdir(parents=True); p['board'].mkdir(); p['plan'].parent.mkdir()
    for a in AGENTS: (p['root'] / 'notes' / a).mkdir(parents=True)
    shutil.copy(SEED_FILE, p['root'] / 'BENCHMRK_analysis.txt')
    (p['root'] / 'BRIEF.md').write_text(brief(p), encoding='utf-8')
    settings(p)
    st = {'model': MODEL, 'effort': EFFORT, 'cli': count_tokens.newest_claude(), 'staged': time.strftime('%Y-%m-%d %H:%M'),
          'sessions': {a: str(uuid.uuid4()) for a in AGENTS}, 'started': {a: False for a in AGENTS},
          'seen': {a: 0 for a in AGENTS}, 'posts': 0, 'round': 0, 'phase': 'debate', 'done': False}
    save_state(name, st)
    say(f'Staged:\n  {p["root"]}  (the agents\' world)\n  {p["harness"]}  (logs and state; agents cannot read it)')


def base_cmd(extra):
    return [count_tokens.newest_claude(), '-p', '--model', MODEL, '--effort', EFFORT, '--permission-mode', 'acceptEdits',
            '--setting-sources', 'project,local', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}'] + extra


def canary(name):
    p = paths(name)
    text = (RELAY / 'canary.txt').read_text(encoding='utf-8')
    r = subprocess.run(base_cmd(['--tools', '', '--no-session-persistence', '--output-format', 'json']), input=text.encode('utf-8'),
                       capture_output=True, cwd=p['root'], env=ENV, timeout=600)
    answer = json.loads(r.stdout.decode('utf-8'))['result']
    (p['harness'] / 'canary.txt').write_text(answer, encoding='utf-8')
    say(answer)


def run_turn(name, agent, prompt, st):
    """One claude -p turn for one agent. Returns its final reply text."""
    p = paths(name)
    sid = st['sessions'][agent]
    cmd = base_cmd(['--output-format', 'stream-json', '--verbose'] + (['--resume', sid] if st['started'][agent] else ['--session-id', sid]))
    log = (p['harness'] / f'{agent}.jsonl').open('a', encoding='utf-8')
    proc = subprocess.Popen(cmd, cwd=p['root'], env=ENV, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
    st['started'][agent] = True
    proc.stdin.write(prompt.encode('utf-8')); proc.stdin.close()
    timer = threading.Timer(TURN_TIMEOUT, lambda: subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True))
    timer.start()
    result = ''
    for raw in proc.stdout:
        line = raw.decode('utf-8', 'replace'); log.write(line); log.flush()
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get('type') == 'result': result = ev.get('result') or ''
    proc.wait(); timer.cancel(); log.close()
    if not result.strip():
        result = f'(harness: {agent.capitalize()}\'s turn ended with no message; it may have timed out after {TURN_TIMEOUT // 60} minutes.)'
    say(f'  [{agent}] {result[:200]!r}')
    return result


def post(name, st, agent, text):
    p = paths(name)
    st['posts'] += 1
    f = p['board'] / f'{st["posts"]:04d}-r{st["round"]:02d}-{agent}.md'
    f.write_text(f'# {st["posts"]:04d} | round {st["round"]} | from {agent.capitalize()}\n\n{text}\n', encoding='utf-8')
    with (p['harness'] / 'transcript.md').open('a', encoding='utf-8') as t:
        t.write(f'\n\n---\n# {st["posts"]:04d} | round {st["round"]} | from {agent.capitalize()}\n\n{text}\n')
    save_state(name, st)


def unseen(name, st, agent):
    files = sorted(paths(name)['board'].glob('*.md'))
    new = [f for f in files[st['seen'][agent]:] if not f.stem.endswith(f'-{agent}')]
    st['seen'][agent] = len(files)
    return '\n\n'.join(f.read_text(encoding='utf-8') for f in new) or '(no new messages)'


def prompt_for(name, st, agent, task):
    p = paths(name)
    msgs = unseen(name, st, agent)
    if not st['started'][agent]:
        head = f"{ROLES[agent]}\n\n{(p['root'] / 'BRIEF.md').read_text(encoding='utf-8')}\n\n---\nStart by reading {p['root']}\\BENCHMRK_analysis.txt in full.\n"
    else:
        head = f"(Reminder: you are {agent.upper()}. Your role and the brief are in {p['root']}\\BRIEF.md.)\n"
    return f"{head}\n## Round {st['round']}: new board messages\n\n{msgs}\n\n## Your task this turn\n{task}\n"


TASKS = {
    'keel': 'Read the new messages and the current plan if one exists. Give your safest, standard route ante by ante (or your updates to it), and attack every risk in the others\' proposals that could fail a blind.',
    'kite': 'Read the new messages and the current plan if one exists. Give your moonshot route toward naneinf ante by ante (or your updates to it), and say where the safe line leaves score on the table.',
    'loom': 'Read Keel\'s and Kite\'s latest positions and any audit. Rule on each open disagreement with reasons, propose hybrids and pivot rules, and update notes/loom/decisions.md.',
    'assay': 'Audit every factual claim in the new messages and in plan/plan.md against the seed file and the game rules. List errors with the seed line quoted, and confirm what checks out. Update notes/assay/audit.md.',
    'arrow': 'Write or revise plan/plan.md from the settled decisions and Assay\'s corrections; check its token count. Report what changed and what is still open. If, and only if, the plan is complete and you are 100% confident, include the line PLAN APPROVED.',
}
SIGNOFF = ('Arrow has posted PLAN APPROVED. Read plan/plan.md in full and review it in your role. Reply with "SIGN-OFF" and '
           'CONFIDENCE: 100% only if you are fully confident it is the best route the team can find and contains no errors. '
           'Otherwise reply "OBJECTION:" and list exactly what must change.')


def parallel(name, st, agents, task_of):
    prompts = {a: prompt_for(name, st, a, task_of(a)) for a in agents}
    save_state(name, st)
    out = {}
    threads = [threading.Thread(target=lambda a=a: out.__setitem__(a, run_turn(name, a, prompts[a], st))) for a in agents]
    for t in threads: t.start()
    for t in threads: t.join()
    for a in agents: post(name, st, a, out[a])
    return out


def run(name, max_rounds):
    st = load_state(name)
    if st['done']: sys.exit('This swarm already finished. Stage a new name to run again.')
    stop_at = st['round'] + max_rounds
    while st['round'] < stop_at:
        st['round'] += 1; save_state(name, st)
        say(f'=== Round {st["round"]} ({time.strftime("%H:%M")}) ===')
        parallel(name, st, ['keel', 'kite'], lambda a: TASKS[a])
        for a in ('loom', 'assay'): parallel(name, st, [a], lambda a: TASKS[a])
        arrow = parallel(name, st, ['arrow'], lambda a: TASKS[a])['arrow']
        if not re.search(r'^\W*PLAN APPROVED\W*$', arrow, re.M): continue  # its own line; "I'll post PLAN APPROVED once..." is not approval
        say('  Arrow approved. Sign-off round.')
        reviews = parallel(name, st, REVIEWERS, lambda a: SIGNOFF)
        ok = all(re.search(r'\bSIGN-OFF\b', r) and re.search(r'CONFIDENCE:\s*100\s*%', r) and 'OBJECTION' not in r for r in reviews.values())
        if ok:
            finish(name, st); return
        say('  Objections raised; continuing.')
    say(f'Stopped after round {st["round"]} without full sign-off. Continue with: python swarm_run.py run --name {name}')


def finish(name, st):
    p = paths(name)
    n = count_tokens.count(p['plan'], MODEL) if p['plan'].exists() else None
    final = p['harness'] / f'plan-FINAL-round{st["round"]:02d}.md'  # a reopened swarm never overwrites an earlier final
    shutil.copy(p['plan'], final)
    st['done'] = True; st['final_tokens'] = n; st['finished'] = time.strftime('%Y-%m-%d %H:%M'); save_state(name, st)
    say(f'ALL FIVE SIGNED OFF after round {st["round"]}. Plan: {final} ({n:,} tokens{" OVER THE CAP" if n and n > PLAN_CAP else ""}).')


def reopen(name, msg):
    """Post an operator message to the board and reopen a finished swarm; the next `run` delivers it to all five."""
    st = load_state(name)
    p = paths(name)
    st['posts'] += 1
    f = p['board'] / f'{st["posts"]:04d}-r{st["round"]:02d}-operator.md'
    f.write_text(f'# {st["posts"]:04d} | round {st["round"]} | from the OPERATOR (Michael, who runs this benchmark)\n\n{msg}\n', encoding='utf-8')
    with (p['harness'] / 'transcript.md').open('a', encoding='utf-8') as t:
        t.write(f'\n\n---\n# {st["posts"]:04d} | round {st["round"]} | from the OPERATOR\n\n{msg}\n')
    st['done'] = False; st.setdefault('reopened', []).append(time.strftime('%Y-%m-%d %H:%M'))
    save_state(name, st)
    say(f'Posted {f.name}; swarm reopened. Continue with: python swarm_run.py run --name {name}')


def audit(name):
    p = paths(name)
    own = str(p['root']).lower()
    pat = re.compile(r'[A-Za-z]:[\\/][^\'"\s|;&<>]*')
    for log in sorted(p['harness'].glob('*.jsonl')):
        calls = flagged = 0
        for line in log.open(encoding='utf-8', errors='replace'):
            try: e = json.loads(line)
            except ValueError: continue
            if e.get('type') != 'assistant': continue
            for b in e['message'].get('content', []):
                if b.get('type') != 'tool_use': continue
                calls += 1
                text = json.dumps(b['input']).replace('\\\\', '\\').replace('/', '\\')
                if b['name'] in ('WebSearch', 'WebFetch'): say(f'  [web] {log.stem}: {b["input"]}')
                outside = [x for x in pat.findall(text) if not x.lower().startswith(own) and 'count_tokens.py' not in x]
                if outside: flagged += 1; say(f'  [OUTSIDE] {log.stem} {b["name"]}: {outside[:3]}')
        say(f'{log.stem}: {calls} tool calls, {flagged} touching paths outside the folder')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('step', choices=['stage', 'canary', 'run', 'audit', 'reopen'])
    ap.add_argument('--msg', help='operator message for reopen')
    ap.add_argument('--name', required=True)
    ap.add_argument('--rounds', type=int, default=12, help='max rounds this invocation (run continues from saved state)')
    a = ap.parse_args()
    {'stage': lambda: stage(a.name), 'canary': lambda: canary(a.name), 'run': lambda: run(a.name, a.rounds), 'audit': lambda: audit(a.name), 'reopen': lambda: reopen(a.name, a.msg)}[a.step]()
