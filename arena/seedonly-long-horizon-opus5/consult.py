"""Dialogue broker between the bench PLAYER and its long-horizon PLANNER.

Usage:  python consult.py "<message to the planner>"

The full planner conversation is persisted in planner-state.json, so the
planner keeps long-horizon context across every consultation of the run.
A human-readable copy of the dialogue is appended to planner-dialogue.md.
The planner model is set in planner-config.json.
"""
import json
import pathlib
import sys

ARM_DIR = pathlib.Path(__file__).resolve().parent
KEY_FILE = pathlib.Path(
    r"C:\Users\maaro\OneDrive\Desktop\balatro-bench\.secrets\anthropic-api-key.txt"
)
STATE = ARM_DIR / "planner-state.json"
LOG = ARM_DIR / "planner-dialogue.md"


def main():
    if len(sys.argv) < 2 or not " ".join(sys.argv[1:]).strip():
        print("ERROR: pass your message to the planner as one quoted argument.")
        sys.exit(1)
    message = " ".join(sys.argv[1:]).strip()

    config = json.loads((ARM_DIR / "planner-config.json").read_text(encoding="utf-8"))
    key = KEY_FILE.read_text(encoding="utf-8").strip() if KEY_FILE.exists() else ""
    if not key or "PASTE-YOUR" in key:
        print(
            "ERROR: the operator has not installed the API key yet."
            " Tell the operator and wait; do not proceed without your planner."
        )
        sys.exit(1)

    briefing = (ARM_DIR / "planner-briefing.md").read_text(encoding="utf-8")
    messages = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else []
    messages.append({"role": "user", "content": message})

    import anthropic

    client = anthropic.Anthropic(api_key=key)
    try:
        resp = client.messages.create(
            model=config["model"],
            max_tokens=config["max_tokens"],
            system=[
                {
                    "type": "text",
                    "text": briefing,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
        )
    except anthropic.APIStatusError as e:
        print(
            f"API ERROR ({e.status_code}): {e.message}."
            " Retry this consult call once; if it fails again, note it in your"
            " journal and proceed on your own judgment."
        )
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("API CONNECTION ERROR: retry this consult call.")
        sys.exit(1)

    if resp.stop_reason == "refusal":
        print(
            "PLANNER UNAVAILABLE (refusal). Note it in your journal and proceed"
            " on your own judgment."
        )
        sys.exit(0)

    reply = "".join(b.text for b in resp.content if b.type == "text").strip()
    # Store the assistant turn as the full content blocks (not just the text)
    # so models that emit thinking blocks get them replayed unchanged.
    messages.append(
        {
            "role": "assistant",
            "content": [b.model_dump(exclude_none=True) for b in resp.content],
        }
    )
    STATE.write_text(json.dumps(messages, indent=1), encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n## PLAYER\n{message}\n\n## PLANNER ({config['model']})\n{reply}\n")
    print(reply)


if __name__ == "__main__":
    main()
