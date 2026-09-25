"""List every file path a relay session touched outside its own arena.

Usage: python audit.py <arena folder> [<log name>]
Reads Claude stream-json or Codex --json logs and prints each tool call that mentions a
path outside the arena (plus its own ~/.claude session data, which is shown but marked).
"""
import json, pathlib, re, sys

PATH = re.compile(r'(?<![A-Za-z])[A-Za-z]:[\\/](?!n[\\\s-]|n$)[A-Za-z0-9_.~-][^\'"\s|;&<>]*|~/[^\'"\s|;&<>]+')
HARMLESS = ('WindowsPowerShell', 'balatro-bench\\bench-rpc.ps1', 'balatro-bench\\relay\\count_tokens.py')


def calls(log):
    for line in log.open(encoding='utf-8', errors='replace'):
        try: e = json.loads(line)
        except ValueError: continue
        if e.get('type') == 'assistant':  # Claude
            for b in e['message'].get('content', []):
                if b.get('type') == 'tool_use': yield b['name'], json.dumps(b['input'])
        it = e.get('item') or {}
        if e.get('type') == 'item.completed' and it.get('type') == 'command_execution':  # Codex
            yield 'shell', it.get('command', '')
        if e.get('type') == 'item.completed' and it.get('type') == 'file_change':
            yield 'file_change', json.dumps(it.get('changes', ''))


def main(arena, log_name=None):
    arena = pathlib.Path(arena)
    logs = [arena / log_name] if log_name else [f for f in arena.glob('*log*.jsonl') if not f.name.startswith('canary')]
    own = str(arena).lower().replace('/', '\\')
    total = flagged = 0
    for log in logs:
        for name, text in calls(log):
            total += 1
            text = text.replace('\\\\', '\\').replace('/', '\\')
            outside = [p for p in PATH.findall(text) if not p.lower().startswith(own) and not any(h.lower() in p.lower() for h in HARMLESS)]
            if outside:
                flagged += 1
                mark = 'OWN SESSION DATA' if all(arena.name.lower() in p.lower() for p in outside) else 'OUTSIDE'
                print(f'[{mark}] {log.name} {name}: {sorted(set(outside))[:4]}')
    print(f'{arena.name}: {total} tool calls, {flagged} touching paths outside the arena')


if __name__ == '__main__':
    main(*sys.argv[1:])
