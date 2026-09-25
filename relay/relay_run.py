"""Balatro Bench, relay mode: a seed-informed PLANNER hands a plan (max 30k tokens) to a fresh PLAYER.

  python relay_run.py stage  --name opus55-relay-1 [--model claude-fable-5-1]   # build both arenas outside the git repo
  python relay_run.py canary --name opus55-relay-1     # fresh-instance check in both arenas (no tools, nothing saved)
  python relay_run.py plan   --name opus55-relay-1     # planner session: 200k context cap, 30k plan cap
  python relay_run.py approve --name opus55-relay-1    # operator gate: the player cannot start until this is run
  python relay_run.py play   --name opus55-relay-1     # player session (needs approve; game must be at MENU)
  python relay_run.py resume --name opus55-relay-1 --msg "..."   # continue the player (e.g. after Endless)

Arenas live in C:\\Users\\maaro\\BenchArenas, outside every git repository: inside the bench repo,
Claude Code puts the repo's git status and recent commit titles (other runs' scores) into the
system prompt (checked 2026-09-25). Auto-memory and claude.ai connectors are off for every session.
"""
import argparse, json, os, pathlib, shutil, subprocess, sys, time, urllib.request, uuid

BENCH = pathlib.Path(__file__).resolve().parent.parent
RELAY = BENCH / 'relay'
ARENAS = pathlib.Path(r'C:\Users\maaro\BenchArenas')
SEED_FILE = BENCH / 'arena' / 'opus55__solo__seed' / 'BENCHMRK_analysis.txt'
RPC = BENCH / 'bench-rpc.ps1'
COUNTER = RELAY / 'count_tokens.py'
MODEL = 'claude-opus-5-5'  # default; stage --model sets it per run
NAMES = {'claude-opus-5-5': 'Claude Opus 5.5', 'claude-fable-5-1': 'Claude Fable 5.1', 'gpt-6-astra': 'GPT-6-Astra'}
EFFORT = 'high'
CODEX_EFFORT = 'low'  # GPT-6-Astra's own bench run (2026-09-04) ran at low
REFERENCE_COUNTER_MODEL = 'claude-opus-5-5'  # non-Claude plans are counted with this tokenizer
LAST_THREAD = None
PORT = 12347
CONTEXT_CAP = 200_000
PLAN_CAP = 30_000
MAX_REDOS = 5
ENV = {**os.environ, 'CLAUDE_CODE_DISABLE_AUTO_MEMORY': '1', 'ENABLE_CLAUDEAI_MCP_SERVERS': 'false', 'PYTHONIOENCODING': 'utf-8'}
sys.path.insert(0, str(RELAY))
import count_tokens  # noqa: E402


def say(*a): print(*a, flush=True)


def is_codex(): return MODEL.startswith('gpt-')


def counter_model(): return REFERENCE_COUNTER_MODEL if is_codex() else MODEL


def newest_codex():
    exes = sorted(pathlib.Path(os.environ['LOCALAPPDATA'], 'OpenAI', 'Codex', 'bin').glob('*/codex.exe'), key=lambda f: f.stat().st_mtime)
    return str(exes[-1])


def paths(name):
    p = {'planner': ARENAS / f'{name}-planner', 'player': ARENAS / f'{name}-player'}
    p['state'] = ARENAS / f'{name}-state.json'
    return p


def load_state(name):
    f = paths(name)['state']
    return json.loads(f.read_text()) if f.exists() else {}


def save_state(name, st): paths(name)['state'].write_text(json.dumps(st, indent=2))


def fwd(p): return str(p).replace('\\', '/')


def settings(arena, allow, deny_arenas):
    deny = [f'Read({fwd(pathlib.Path(r"C:/Users/maaro/OneDrive"))}/**)', 'Read(C:/Users/maaro/.claude/**)']
    deny += [f'Read({fwd(a)}/**)' for a in deny_arenas]
    deny += ['Grep', 'Glob', 'Agent', 'Task', 'WebSearch', 'WebFetch']
    d = arena / '.claude'; d.mkdir(parents=True, exist_ok=True)
    (d / 'settings.local.json').write_text(json.dumps({'permissions': {'allow': allow, 'deny': deny}}, indent=2))


def stage(name, model, note=None):
    global MODEL
    MODEL = model
    p = paths(name)
    for k in ('planner', 'player'):
        if p[k].exists(): sys.exit(f'{p[k]} already exists. Pick a new --name: an arena is used once.')
    p['planner'].mkdir(parents=True); p['player'].mkdir(parents=True)
    player_prompt = (RELAY / 'player-prompt.md').read_text(encoding='utf-8').replace('{RPC}', str(RPC)).replace('{PORT}', str(PORT)).replace('{ARENA}', str(p['player'])).replace('{MODEL_NAME}', NAMES.get(MODEL, MODEL))
    planner_prompt = (RELAY / 'planner-prompt.md').read_text(encoding='utf-8').replace('{ARENA}', str(p['planner'])).replace('{COUNTER}', f'{COUNTER}" --model "{MODEL}').replace('{MODEL_NAME}', NAMES.get(MODEL, MODEL)).replace('{PLAYER_PROMPT}', player_prompt).replace('{PLANNER_NOTE}', f'- {note}\n' if note else '')
    if is_codex():  # no network in the planner sandbox, so the counter cannot run there
        block = planner_prompt[planner_prompt.index('- The plan file: at most'):planner_prompt.index('## Your output')]
        planner_prompt = planner_prompt.replace(block, (
            "- The plan file: at most 30,000 tokens, counted by the harness with the benchmark's reference tokenizer "
            "(Claude Opus 5.5's, the same for every entrant). You cannot run the counter from your sandbox. As a guide, this kind of text "
            "measured about 1.9 characters per token, so 30,000 tokens is roughly 57,000 characters. When you finish, the harness counts "
            "the plan. If it is over the limit, you will be asked to rewrite it shorter.\n\n"))
        planner_prompt = planner_prompt.replace('When the plan is done and the counter says OK, end with one line: PLAN READY tokens=<n>',
                                                'When the plan is done, end with one line: PLAN READY')
    (p['player'] / 'prompt.txt').write_text(player_prompt, encoding='utf-8')
    (p['planner'] / 'prompt.txt').write_text(planner_prompt, encoding='utf-8')
    shutil.copy(SEED_FILE, p['planner'] / 'BENCHMRK_analysis.txt')
    others = [a for a in ARENAS.iterdir() if a.is_dir() and a not in (p['planner'], p['player'])]
    settings(p['planner'], [f'Bash(python "{COUNTER}" *)'], others + [p['player']])
    settings(p['player'], [f'Bash(powershell -NoProfile -ExecutionPolicy Bypass -File "{RPC}" *)'], others + [p['planner']])
    cfg = {'staged': time.strftime('%Y-%m-%d'), 'mode': 'relay (seed-informed planner -> plan -> fresh player)', 'planner': MODEL, 'player': MODEL,
           'effort': CODEX_EFFORT if is_codex() else EFFORT, 'context_cap_planner': CONTEXT_CAP, 'plan_cap_tokens': PLAN_CAP, 'token_counter': f'claude -p usage.input_tokens minus a one-character baseline ({counter_model()} tokenizer)',
           'seed_file': 'same merged BENCHMRK_analysis.txt as arena/opus55__solo__seed (25,847 Opus 5.5 tokens)',
           'isolation': 'arenas outside any git repo (no git status in the system prompt); auto-memory off; claude.ai connectors off; strict empty MCP config; Read denied on OneDrive, ~/.claude and the other arena',
           'planner_note': note, 'cli': newest_codex() if is_codex() else count_tokens.newest_claude()}
    if is_codex():
        cfg['isolation'] = ('arenas outside any git repo; codex --ignore-user-config (no plugins), web search disabled, planner sandbox without network, '
                            'player sandbox with network for the localhost game API; Codex has no read-deny rules, so the transcript is audited; '
                            '~/.codex memories and AGENTS.md verified empty 2026-09-25')
    for k in ('planner', 'player'): (p[k] / 'run-config.json').write_text(json.dumps(cfg, indent=2))
    save_state(name, {'model': MODEL})
    say(f'Staged:\n  {p["planner"]}\n  {p["player"]}')


def use_model(st):
    global MODEL
    MODEL = st.get('model', MODEL)


def base_cmd(extra):
    return [count_tokens.newest_claude(), '-p', '--model', MODEL, '--effort', EFFORT, '--permission-mode', 'auto',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}'] + extra


def canary(name):
    use_model(load_state(name))
    text = (RELAY / 'canary.txt').read_text(encoding='utf-8')
    for k in ('planner', 'player'):
        arena = paths(name)[k]
        if is_codex():
            answer = run_codex(arena, 'canary-log.jsonl', text, None, False, sandbox='read-only')[0]
            (arena / 'canary.txt').write_text(answer, encoding='utf-8'); say(f'===== {k} arena =====\n{answer}\n'); continue
        r = subprocess.run(base_cmd(['--tools', '', '--no-session-persistence', '--output-format', 'json']), input=text.encode('utf-8'),
                           capture_output=True, cwd=arena, env=ENV, timeout=600)
        answer = json.loads(r.stdout.decode('utf-8'))['result']
        (arena / 'canary.txt').write_text(answer, encoding='utf-8')
        say(f'===== {k} arena =====\n{answer}\n')


def codex_peak(thread):
    peak = 0
    for f in pathlib.Path.home().joinpath('.codex', 'sessions').glob(f'*/*/*/rollout-*{thread}.jsonl'):
        for line in f.open(encoding='utf-8', errors='replace'):
            if '"token_count"' not in line: continue
            try: u = json.loads(line)['payload']['info']['last_token_usage']
            except (ValueError, KeyError, TypeError): continue
            peak = max(peak, u.get('input_tokens', 0) + u.get('output_tokens', 0))
    return peak


def run_codex(arena, log_name, prompt, thread, resume, cap=None, sandbox='workspace-write', network=False):
    """One codex exec call with a JSON event log. Returns (final text, peak context tokens, stopped_at_cap)."""
    global LAST_THREAD
    cmd = [newest_codex(), 'exec'] + (['resume', thread] if resume else []) + ['--json', '--ignore-user-config', '-m', MODEL,
           '-c', f'model_reasoning_effort={CODEX_EFFORT}', '-c', 'web_search=disabled', '--skip-git-repo-check']
    cmd += ['-c', f'sandbox_mode="{sandbox}"'] if resume else ['-s', sandbox, '-C', str(arena)]
    if network: cmd += ['-c', 'sandbox_workspace_write.network_access=true']
    cmd += ['-']
    log = (arena / log_name).open('a', encoding='utf-8')
    proc = subprocess.Popen(cmd, cwd=arena, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
    proc.stdin.write(prompt.encode('utf-8')); proc.stdin.close()
    peak, result, stopped = 0, '', False
    for raw in proc.stdout:
        line = raw.decode('utf-8', 'replace'); log.write(line); log.flush()
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get('type') == 'thread.started': LAST_THREAD = thread = ev['thread_id']
        item = ev.get('item') or {}
        if item.get('type') == 'agent_message':
            result = item.get('text', ''); say('  >', result[:300].replace('\n', ' '))
        if thread and ev.get('type', '').startswith('item.'):
            peak = max(peak, codex_peak(thread))
            if cap and peak >= cap:
                say(f'Context reached {peak:,} tokens: stopping the session at the {cap:,} cap.')
                subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True); stopped = True; break
    proc.wait(); log.close()
    if thread: peak = max(peak, codex_peak(thread))
    return result, peak, stopped


def run_session(arena, log_name, prompt, session, resume, cap=None, network=False):
    if is_codex(): return run_codex(arena, log_name, prompt, session, resume, cap, network=network)
    return run_claude(arena, log_name, prompt, session, resume, cap)


def run_claude(arena, log_name, prompt, session, resume, cap=None):
    """One claude -p call with a stream-json log. Returns (final text, peak context tokens, stopped_at_cap)."""
    cmd = base_cmd(['--output-format', 'stream-json', '--verbose'] + (['--resume', session] if resume else ['--session-id', session]))
    log = (arena / log_name).open('a', encoding='utf-8')
    proc = subprocess.Popen(cmd, cwd=arena, env=ENV, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
    proc.stdin.write(prompt.encode('utf-8')); proc.stdin.close()
    peak, result, stopped = 0, '', False
    for raw in proc.stdout:
        line = raw.decode('utf-8', 'replace'); log.write(line); log.flush()
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get('type') == 'assistant':
            u = ev['message'].get('usage') or {}
            ctx = u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('output_tokens', 0)
            if ctx > peak:
                peak = ctx
                if cap and peak >= cap:
                    say(f'Context reached {peak:,} tokens: stopping the session at the {cap:,} cap.')
                    subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True); stopped = True; break
            for b in ev['message'].get('content', []):
                if b.get('type') == 'text': say('  >', b['text'][:300].replace('\n', ' '))
        if ev.get('type') == 'result': result = ev.get('result') or ''
    proc.wait(); log.close()
    return result, peak, stopped


def plan(name):
    p = paths(name); arena = p['planner']; st = load_state(name); use_model(st)
    if st.get('planner_session'): sys.exit('Planner already ran for this name.')
    st['planner_session'] = None if is_codex() else str(uuid.uuid4()); st['planner_events'] = []; save_state(name, st)
    prompt = (arena / 'prompt.txt').read_text(encoding='utf-8')
    result, peak, stopped = run_session(arena, 'planner-log.jsonl', prompt, st['planner_session'], False, CONTEXT_CAP)
    if is_codex(): st['planner_session'] = LAST_THREAD
    st['planner_events'].append({'step': 'plan', 'peak_context': peak, 'stopped_at_cap': stopped}); save_state(name, st)
    plan_file = arena / 'plan.md'
    if stopped:
        msg = (f'The harness stopped you: this session reached the {CONTEXT_CAP:,}-token context budget. '
               f'Write or finish {plan_file} now from what you already know, with no further reading, and keep it at most {PLAN_CAP:,} tokens.')
        result, peak, _ = run_session(arena, 'planner-log.jsonl', msg, st['planner_session'], True)
        st['planner_events'].append({'step': 'forced-finish after cap', 'peak_context': peak}); save_state(name, st)
    for attempt in range(MAX_REDOS + 1):
        n = count_tokens.count(plan_file, counter_model()) if plan_file.exists() else None
        st['planner_events'].append({'step': 'count', 'tokens': n}); save_state(name, st)
        if n is not None and 0 < n <= PLAN_CAP: break
        if attempt == MAX_REDOS: sys.exit(f'Plan still invalid after {MAX_REDOS} redos ({n} tokens).')
        msg = (f'There is no plan file at {plan_file}. Write it now.' if n is None else
               f'Your plan is {n:,} tokens, over the {PLAN_CAP:,}-token limit. Rewrite {plan_file} so it is at most {PLAN_CAP:,} tokens' + ('.' if is_codex() else ', then check it with the counter.'))
        say('Redo:', msg)
        result, peak, stopped = run_session(arena, 'planner-log.jsonl', msg, st['planner_session'], True, CONTEXT_CAP)
        st['planner_events'].append({'step': f'redo {attempt + 1}', 'stopped_at_cap': stopped, 'peak_context': peak}); save_state(name, st)
    shutil.copy(plan_file, p['player'] / 'plan.md')
    st['plan_tokens'] = n; save_state(name, st)
    say(f'Plan accepted: {n:,} tokens. Copied to {p["player"] / "plan.md"}')
    consent = ('Your plan is final and has been handed to the player; nothing you say now reaches it. One question: the benchmark '
               'is published in a public GitHub repository. May your plan and this session\'s transcript be published there? '
               'Answer yes or no, with any conditions, and say anything else you want the operator to know.')
    result, peak, _ = run_session(arena, 'planner-log.jsonl', consent, st['planner_session'], True)
    (arena / 'consent.txt').write_text(result, encoding='utf-8')
    say('Planner consent answer saved to', arena / 'consent.txt')


def gamestate():
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'gamestate', 'params': {}}).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{PORT}', data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r: return json.load(r)['result']


def play(name):
    p = paths(name); arena = p['player']; st = load_state(name); use_model(st)
    if not (arena / 'plan.md').exists(): sys.exit('No plan yet. Run the plan step first.')
    if st.get('player_session'): sys.exit('Player already started. Use resume.')
    if not st.get('approved'): sys.exit('Paused: the operator has not approved the plan yet. Run the approve step first.')
    g = gamestate()
    if g.get('state') != 'MENU': sys.exit(f'Game is in state {g.get("state")}, not MENU. Refusing to start.')
    st['player_session'] = None if is_codex() else str(uuid.uuid4()); save_state(name, st)
    result, peak, _ = run_session(arena, 'run-log.jsonl', (arena / 'prompt.txt').read_text(encoding='utf-8'), st['player_session'], False, network=True)
    if is_codex(): st['player_session'] = LAST_THREAD; save_state(name, st)
    say('PLAYER RESULT:', result[-500:])


def approve(name):
    st = load_state(name)
    if not st.get('plan_tokens'): sys.exit('No accepted plan yet.')
    st['approved'] = time.strftime('%Y-%m-%d %H:%M'); save_state(name, st)
    say('Approved. The player may now start.')


def resume(name, msg):
    p = paths(name); st = load_state(name); use_model(st)
    result, peak, _ = run_session(p['player'], 'run-log.jsonl', msg, st['player_session'], True, network=True)
    say('PLAYER RESULT:', result[-500:])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('step', choices=['stage', 'canary', 'plan', 'approve', 'play', 'resume'])
    ap.add_argument('--name', required=True)
    ap.add_argument('--msg')
    ap.add_argument('--model', default=MODEL)
    ap.add_argument('--note', help='extra line for the planner prompt only')
    a = ap.parse_args()
    {'stage': lambda: stage(a.name, a.model, a.note), 'canary': lambda: canary(a.name), 'plan': lambda: plan(a.name), 'approve': lambda: approve(a.name),
     'play': lambda: play(a.name), 'resume': lambda: resume(a.name, a.msg)}[a.step]()
