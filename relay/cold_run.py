"""Balatro Bench, mode 1 (cold): one fresh PLAYER, no planner, no seed file, in an arena outside the git repo.

  python cold_run.py stage  --name fable52__solo__noseed --model "claude-fable-5-2[1m]"
  python cold_run.py canary --name fable52__solo__noseed   # fresh-instance check in the arena (no tools, nothing saved)
  python cold_run.py play   --name fable52__solo__noseed   # player session (game must be at MENU)
  python cold_run.py resume --name fable52__solo__noseed --msg "..."   # continue the player (e.g. after Endless)

The prompt is the text stage-run.py builds for --planner none --seed-info off. The arena location,
sandbox settings, environment and launch command are relay_run.py's, plus what the machine needed by
2026-11 so that a fresh instance still sees nothing but its prompt:
  - --safe-mode: no user CLAUDE.md, skills, plugins or hooks. The user-level CLAUDE.md had grown and
    now points every session at a shared memory folder that holds this bench's history.
  - The operator session's own CLAUDE_* and ANTHROPIC_* variables are not passed to the player
    (desktop-app session ids, a messaging socket, a research API key under another name).
  - The helper is allowed under both shell tools (the Windows CLI now has Bash and PowerShell).
  - More Read denies (Documents, Downloads, the game's AppData, the desktop app's session store) and
    denies for the tools that reach other sessions, the cloud or the web.
  - A model the CLI does not know yet (Fable 5.2 on CLI 2.1.317) gets a 200k context window and a 32k
    output cap unless its id carries the [1m] suffix. With the suffix it gets 1M and the 128k cap, the
    same limits the Opus 5.5 entrant had.
"""
import argparse, importlib.util, json, os, pathlib, subprocess, sys, time, uuid

RELAY = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RELAY))
for _s in (sys.stdout, sys.stderr): _s.reconfigure(encoding='utf-8', errors='replace')  # a cp1252 console cannot print every character a player writes
import relay_run as R  # noqa: E402
import count_tokens  # noqa: E402

_spec = importlib.util.spec_from_file_location('stage_run', R.BENCH / 'stage-run.py')
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)

SCRUB_PREFIXES = ('CLAUDE_CODE_', 'CLAUDE_AGENT_SDK_', 'CLAUDE_PREVIEW_', 'ANTHROPIC_')
SCRUB_NAMES = ('CLAUDECODE', 'CLAUDE_PID')
BENCH_VARS = {'CLAUDE_CODE_DISABLE_AUTO_MEMORY': '1', 'ENABLE_CLAUDEAI_MCP_SERVERS': 'false', 'PYTHONIOENCODING': 'utf-8',
              'CLAUDE_CODE_MAX_OUTPUT_TOKENS': '128000', 'CLAUDE_CODE_DISABLE_CLAUDE_MDS': '1'}
EXTRA_FLAGS = ['--safe-mode', '--setting-sources', 'project,local']  # the second flag keeps user-level plugins and settings out too
EXTRA_READ_DENY = ['C:/Users/maaro/Documents', 'C:/Users/maaro/Downloads', 'C:/Users/maaro/AppData/Roaming/Balatro',
                   'C:/Users/maaro/AppData/Roaming/Claude', 'C:/Users/maaro/.codex']
EXTRA_TOOL_DENY = ['Workflow', 'SendMessage', 'ListAgents', 'RemoteTrigger', 'CronCreate', 'CronDelete', 'CronList',
                   'Artifact', 'ArtifactComments', 'ArtifactData', 'DesignSync', 'PushNotification', 'SendToProject', 'SendToProjectContext']


def player_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith(SCRUB_PREFIXES) and k not in SCRUB_NAMES}
    env.update(BENCH_VARS)
    return env


def base_cmd(extra):
    return [count_tokens.newest_claude(), '-p', '--model', R.MODEL, '--effort', R.EFFORT, '--permission-mode', 'auto',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}'] + EXTRA_FLAGS + extra


R.ENV = player_env()
R.base_cmd = base_cmd


def arena_of(name): return R.ARENAS / name


def state_file(name): return R.ARENAS / f'{name}-state.json'


def load_state(name):
    f = state_file(name)
    return json.loads(f.read_text()) if f.exists() else {}


def save_state(name, st): state_file(name).write_text(json.dumps(st, indent=2))


def cold_prompt(arena):
    """Exactly what stage-run.py writes for a solo player with no planner and no seed file."""
    prompt = S.PLAYER_BASE.format(BENCH=str(R.BENCH), ARM=str(arena), SEED_SECTION='', PLANNING_SECTION='',
                                  ALLOWED_EXTRAS='', NO_CONSULT_AT_WIN='', WIN_RESUME='')
    return prompt.replace(' Consultations continue at every ante boundary in endless.', '')


def write_settings(arena):
    others = [a for a in R.ARENAS.iterdir() if a.is_dir() and a != arena]
    helper = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{R.RPC}" *'
    R.settings(arena, [f'Bash({helper})', f'PowerShell({helper})'], others)
    f = arena / '.claude' / 'settings.local.json'
    d = json.loads(f.read_text())
    deny = d['permissions']['deny']
    first_tool = next(i for i, x in enumerate(deny) if not x.startswith('Read('))
    deny[first_tool:first_tool] = [f'Read({p}/**)' for p in EXTRA_READ_DENY]
    deny += EXTRA_TOOL_DENY
    f.write_text(json.dumps(d, indent=2))


def stage(name, model):
    arena = arena_of(name)
    if arena.exists(): sys.exit(f'{arena} already exists. Pick a new --name: an arena is used once.')
    arena.mkdir(parents=True)
    R.MODEL = model
    (arena / 'prompt.txt').write_text(cold_prompt(arena), encoding='utf-8')
    write_settings(arena)
    cfg = {'staged': time.strftime('%Y-%m-%d'), 'mode': 'mode 1: solo, cold (no journal, no planner, no seed file)', 'player': model.replace('[1m]', ''),
           'model_flag': model, 'planner': None, 'seed_info': False, 'effort': R.EFFORT, 'arm': name,
           'prompt': 'stage-run.py PLAYER_BASE as built for --planner none --seed-info off',
           'isolation': 'arena outside any git repo; --safe-mode (no user CLAUDE.md, skills, plugins, hooks); auto-memory off; '
                        'claude.ai connectors off; strict empty MCP config; operator-session CLAUDE_*/ANTHROPIC_* variables not passed on; '
                        'Read denied on OneDrive, ~/.claude, Documents, Downloads, the game and desktop-app AppData, and every other arena',
           'cli': count_tokens.newest_claude()}
    (arena / 'run-config.json').write_text(json.dumps(cfg, indent=2))
    save_state(name, {'model': model})
    R.say(f'Staged: {arena}')


def canary(name):
    R.use_model(load_state(name)); arena = arena_of(name)
    text = (RELAY / 'canary.txt').read_text(encoding='utf-8')
    r = subprocess.run(base_cmd(['--tools', '', '--no-session-persistence', '--output-format', 'json']), input=text.encode('utf-8'),
                       capture_output=True, cwd=arena, env=R.ENV, timeout=600)
    out = r.stdout.decode('utf-8', 'replace')
    try: answer = json.loads(out)['result']
    except (ValueError, KeyError): sys.exit(f'Canary failed.\nstdout: {out[-2000:]}\nstderr: {r.stderr.decode("utf-8", "replace")[-2000:]}')
    (arena / 'canary.txt').write_text(answer, encoding='utf-8')
    R.say(f'===== {arena.name} =====\n{answer}\n')


def play(name):
    arena = arena_of(name); st = load_state(name); R.use_model(st)
    if st.get('player_session'): sys.exit('Player already started. Use resume.')
    g = R.gamestate()
    if g.get('state') != 'MENU': sys.exit(f'Game is in state {g.get("state")}, not MENU. Refusing to start.')
    st['player_session'] = str(uuid.uuid4()); st['started'] = time.strftime('%Y-%m-%d %H:%M:%S'); save_state(name, st)
    result, peak, _ = R.run_claude(arena, 'run-log.jsonl', (arena / 'prompt.txt').read_text(encoding='utf-8'), st['player_session'], False)
    st.setdefault('turns', []).append({'step': 'play', 'ended': time.strftime('%Y-%m-%d %H:%M:%S'), 'peak_context': peak}); save_state(name, st)
    R.say('PLAYER RESULT:', result[-1500:])


def resume(name, msg):
    arena = arena_of(name); st = load_state(name); R.use_model(st)
    result, peak, _ = R.run_claude(arena, 'run-log.jsonl', msg, st['player_session'], True)
    st.setdefault('turns', []).append({'step': 'resume', 'message': msg, 'ended': time.strftime('%Y-%m-%d %H:%M:%S'), 'peak_context': peak}); save_state(name, st)
    R.say('PLAYER RESULT:', result[-1500:])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('step', choices=['stage', 'canary', 'play', 'resume'])
    ap.add_argument('--name', required=True)
    ap.add_argument('--model', default='claude-fable-5-2')
    ap.add_argument('--msg')
    a = ap.parse_args()
    {'stage': lambda: stage(a.name, a.model), 'canary': lambda: canary(a.name), 'play': lambda: play(a.name),
     'resume': lambda: resume(a.name, a.msg)}[a.step]()
