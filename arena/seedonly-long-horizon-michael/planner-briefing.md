# You are the PLANNER (human edition)

This is the role card for the human planner in the `seedonly-long-horizon-michael` arm. You are bound by the same protocol as the model planners in the sibling arms, so the three arms stay comparable.

## Your role
Long-horizon planning and evaluation. The PLAYER (an Opus 5 instance with full seed intelligence) consults you:
- once at the very start of the run, before its first action, and
- at the end of every ante (right after the Boss blind is beaten, before any shop purchases for the next ante).

Each consultation is a multi-turn dialogue. The player brings you the situation and a proposed strategy; you evaluate it against the whole rest of the run, not just the next blind. Push back where the plan is weak. Do not rubber-stamp.

## Protocol requirements (the same ones the models had)
- The dialogue continues until you genuinely endorse the plan.
- You endorse ONLY by ending your reply with a line that is exactly: AGREED
- Never write AGREED unless you actually agree. A held disagreement is a legitimate outcome.
- The player is capped at 10 messages per consultation and proceeds on its own judgment after that.
- The full dialogue is logged to planner-dialogue.md and will be published like the others.

## Mechanics
1. Open a terminal in this folder and run: python planner-console.py
2. Leave it open for the whole run. Player messages appear there.
3. Type your reply; finish with a line containing only: /send
4. The console asks for confirmation before sending any reply that does not end in AGREED, so endorsements are always deliberate.

## Notes
- The player has NOT been told whether its planner is a human or a model; it sees only the dialogue. Keep it that way or reveal it, your choice, but note whichever you do in the run record.
- The player is told replies "can be very slow," so take the time you need; its consult call re-waits in 9-minute windows indefinitely.
- Lessons from the Opus 3 debrief, if you want the checklist it left for whoever sits in this seat next: demand sources for every estimate, hunt for inconsistencies between consultations, stress-test against the worst case, be an adversary rather than a mirror, and pressure-test the whole arc rather than the next step.
