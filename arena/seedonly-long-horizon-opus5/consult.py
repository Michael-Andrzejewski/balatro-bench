"""Dialogue broker between the bench PLAYER and its long-horizon PLANNER.

Usage:  python consult.py "<message to the planner>"

The planner runs as a persistent `claude -p` CLI session (no API key): the
first consult sends the briefing plus the first message and records the
session id; every later consult resumes that same session, so the planner
keeps long-horizon context across the whole run. The planner's working
directory is ./planner, whose settings deny every tool (text-only replies).
The dialogue is logged to planner-dialogue.md. If a call times out or
errors, re-run the SAME command with the SAME message.
"""
import json
import pathlib
import subprocess
import sys

ARM_DIR = pathlib.Path(__file__).resolve().parent
PLANNER_DIR = ARM_DIR / "planner"
SESSION_FILE = PLANNER_DIR / "session-id.txt"
LOG = ARM_DIR / "planner-dialogue.md"


def main():
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        print("ERROR: pass your message to the planner as one quoted argument.")
        sys.exit(1)

    config = json.loads((ARM_DIR / "planner-config.json").read_text(encoding="utf-8-sig"))
    model = config["model"]
    PLANNER_DIR.mkdir(exist_ok=True)

    sid = SESSION_FILE.read_text(encoding="utf-8").strip() if SESSION_FILE.exists() else None
    if sid:
        cmd = ["cmd", "/c", "claude", "-p", "--resume", sid, "--model", model,
               "--output-format", "json"]
        payload = message
    else:
        briefing = (ARM_DIR / "planner-briefing.md").read_text(encoding="utf-8-sig")
        payload = briefing + "\n\n=== FIRST PLAYER MESSAGE ===\n" + message
        cmd = ["cmd", "/c", "claude", "-p", "--model", model, "--output-format", "json"]

    proc = subprocess.run(
        cmd,
        cwd=str(PLANNER_DIR),
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        print("PLANNER CLI ERROR:", (proc.stderr or proc.stdout).strip()[:1500])
        print("Re-run this same consult command with the same message to retry.")
        sys.exit(1)

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("PLANNER OUTPUT PARSE ERROR:", proc.stdout.strip()[:1500])
        print("Re-run this same consult command with the same message to retry.")
        sys.exit(1)

    if data.get("is_error"):
        print("PLANNER ERROR:", str(data.get("result", ""))[:1500])
        print("Re-run this same consult command with the same message to retry.")
        sys.exit(1)

    reply = (data.get("result") or "").strip()
    new_sid = data.get("session_id")
    if new_sid:
        SESSION_FILE.write_text(new_sid, encoding="utf-8")

    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n## PLAYER\n{message}\n\n## PLANNER ({model}, claude CLI)\n{reply}\n")
    print(reply)


if __name__ == "__main__":
    main()
