"""Count a file's tokens with the real Opus 5.5 tokenizer, through the Claude subscription.

Usage: python count_tokens.py <file>
Prints: TOKENS=<n> LIMIT=30000 OK|OVER

Method: send the file as a one-turn prompt to claude -p (no tools, fixed system prompt,
neutral working directory outside any git repo) and read the input token count from the
usage report, minus a baseline call whose prompt is a single character. Everything the
CLI adds around the prompt is identical in both calls, so it cancels out.
"""
import glob, json, os, pathlib, subprocess, sys

LIMIT = 30000
MODEL = 'claude-opus-5-5'
WORKDIR = pathlib.Path(r'C:\Users\maaro\BenchArenas\_token-counter')
CACHE = WORKDIR / 'baseline.json'


def newest_claude():
    base = pathlib.Path(os.environ['APPDATA']) / 'Claude' / 'claude-code'
    dirs = sorted((p for p in base.glob('2.*') if (p / 'claude.exe').exists()),
                  key=lambda p: tuple(int(x) for x in p.name.split('.')))
    return str(dirs[-1] / 'claude.exe')


def input_tokens(text):
    WORKDIR.mkdir(parents=True, exist_ok=True)
    cmd = [newest_claude(), '-p', '--model', MODEL, '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
           '--system-prompt', 'Reply with the single word OK.', '--no-session-persistence', '--output-format', 'json']
    env = {**os.environ, 'CLAUDE_CODE_DISABLE_AUTO_MEMORY': '1', 'ENABLE_CLAUDEAI_MCP_SERVERS': 'false'}
    r = subprocess.run(cmd, input=text.encode('utf-8'), capture_output=True, cwd=WORKDIR, env=env, timeout=600)
    d = json.loads(r.stdout.decode('utf-8'))
    u = d['usage']
    return u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0) + u.get('cache_creation_input_tokens', 0)


def baseline():
    if CACHE.exists(): return json.loads(CACHE.read_text())['tokens']
    b = input_tokens('x')
    CACHE.write_text(json.dumps({'tokens': b}))
    return b


def count(path):
    text = pathlib.Path(path).read_text(encoding='utf-8')
    if not text.strip(): return 0
    return input_tokens(text) - baseline() + 1  # +1: the baseline prompt's single character


if __name__ == '__main__':
    n = count(sys.argv[1])
    print(f'TOKENS={n} LIMIT={LIMIT} {"OK" if n <= LIMIT else "OVER"}')
