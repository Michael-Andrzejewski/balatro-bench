"""Dialogue broker between the bench PLAYER and its (human) long-horizon PLANNER.

Usage:
    python consult.py "<message to the planner>"   send a message, then wait
    python consult.py --wait                        keep waiting for the reply

Transport is a file mailbox in ./mailbox. The planner answers through
planner-console.py. Each invocation waits up to 9 minutes; if the planner
has not replied by then, it says so and you re-run with --wait.
The full dialogue is logged to planner-dialogue.md.
"""
import pathlib
import sys
import time

ARM_DIR = pathlib.Path(__file__).resolve().parent
MAILBOX = ARM_DIR / "mailbox"
LOG = ARM_DIR / "planner-dialogue.md"
POLL_SECONDS = 3
WAIT_SECONDS = 540


def last_index():
    msgs = sorted(MAILBOX.glob("msg-*.txt"))
    return int(msgs[-1].stem.split("-")[1]) if msgs else 0


def delivered(n):
    return (MAILBOX / f"reply-{n:04d}.txt").exists() and (
        MAILBOX / f"logged-{n:04d}.flag"
    ).exists()


def main():
    MAILBOX.mkdir(exist_ok=True)
    args = sys.argv[1:]

    if args and args[0] == "--wait":
        n = last_index()
        if n == 0:
            print("ERROR: no consultation in progress; send a message first.")
            sys.exit(1)
        if delivered(n):
            print(
                "The planner's last reply was already delivered. Send your next"
                " message if the consultation continues."
            )
            sys.exit(0)
    else:
        message = " ".join(args).strip()
        if not message:
            print("ERROR: pass your message to the planner as one quoted argument.")
            sys.exit(1)
        n = last_index()
        if n and not delivered(n):
            print(
                "ERROR: the planner has not answered your previous message yet."
                " Run consult.py --wait until that reply arrives before sending"
                " a new message."
            )
            sys.exit(1)
        n += 1
        (MAILBOX / f"msg-{n:04d}.txt").write_text(message, encoding="utf-8")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"\n## PLAYER\n{message}\n")

    reply_file = MAILBOX / f"reply-{n:04d}.txt"
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        if reply_file.exists():
            time.sleep(1)  # let the console finish writing
            reply = reply_file.read_text(encoding="utf-8-sig").strip()
            flag = MAILBOX / f"logged-{n:04d}.flag"
            if not flag.exists():
                with LOG.open("a", encoding="utf-8") as f:
                    f.write(f"\n## PLANNER (michael, human)\n{reply}\n")
                flag.write_text("delivered", encoding="utf-8")
            print(reply)
            return
        time.sleep(POLL_SECONDS)

    print(
        "PLANNER HAS NOT REPLIED YET. This is normal; the planner can be slow."
        " Keep waiting by running (with a 10-minute timeout):\n"
        '  python "'
        + str(ARM_DIR / "consult.py")
        + '" --wait'
    )


if __name__ == "__main__":
    main()
