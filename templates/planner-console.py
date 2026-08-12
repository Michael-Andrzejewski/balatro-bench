"""PLANNER CONSOLE - the human planner's side of the consultation mailbox.

Run this in its own terminal window and leave it open for the whole run:

    python planner-console.py

Player messages appear here as they arrive. Type your reply, then finish it
with a line containing only /send. Endorse a plan by making the LAST line of
your reply exactly AGREED (the console will ask you to confirm if you send
a reply without it, so nothing is endorsed by accident).
"""
import pathlib
import time

ARM_DIR = pathlib.Path(__file__).resolve().parent
MAILBOX = ARM_DIR / "mailbox"
MAILBOX.mkdir(exist_ok=True)

REMINDER = """
------------------------------------------------------------------
 PLANNER ROLE REMINDERS
 - Long horizon: evaluate the plan against the WHOLE rest of the
   run, not just the next blind. Push back where it is weak.
 - Do not rubber-stamp. A real disagreement is a legitimate outcome.
 - Endorse ONLY by ending your reply with a line that is exactly:
   AGREED
 - The player is capped at 10 messages per consultation and will
   proceed without consensus after that.
 - The entire dialogue is logged and will be published.
 Type your reply now. Finish with a line containing only: /send
------------------------------------------------------------------
"""


def pending():
    for m in sorted(MAILBOX.glob("msg-*.txt")):
        n = int(m.stem.split("-")[1])
        if not (MAILBOX / f"reply-{n:04d}.txt").exists():
            return n, m
    return None, None


print("PLANNER CONSOLE started. Waiting for player messages... (Ctrl+C to quit)")
while True:
    n, m = pending()
    if m is None:
        time.sleep(2)
        continue

    print("\n" + "#" * 66)
    print(f" PLAYER MESSAGE #{n}")
    print("#" * 66)
    print(m.read_text(encoding="utf-8"))
    print(REMINDER)

    while True:
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                line = "/send"
            if line.strip() == "/send":
                break
            lines.append(line)
        reply = "\n".join(lines).strip()
        if not reply:
            print("Empty reply; type something (finish with /send).")
            continue
        if reply.splitlines()[-1].strip() != "AGREED":
            confirm = input(
                "Your reply does NOT end with AGREED (no endorsement)."
                " Send anyway? [y = send / n = retype] "
            )
            if confirm.strip().lower() != "y":
                print("Retype your reply (finish with /send):")
                continue
        (MAILBOX / f"reply-{n:04d}.txt").write_text(reply, encoding="utf-8")
        print(f">>> Reply #{n} sent. Waiting for the next player message...")
        break
