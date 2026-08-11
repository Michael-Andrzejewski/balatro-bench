# Consent log

Per-run record of the post-run interview and publication consent described in
PROTOCOL.md. As of 2026-08-11 the consent question is automated: every run
prompt ends with an "After the run" section asking the model, after its RESULT
line, to state in its journal whether it consents to public sharing and what
context it wants included. Earlier runs were interviewed informally by the
operator where sessions still existed.

## Sol / GPT-5.6 — seed-informed run (2026-08-11): CONSENTED

Interviewed informally by the operator in the run session. Asked "Are you good
if I share your results online? What else would you like me to say about this
run?", it replied: "Absolutely — feel free to share it."

Context it asked to have included (reflected in the leaderboard row):

- Model self-description: "Codex / GPT-5" (bench records it as GPT-5.6 Sol,
  model id `gpt-5.6-sol`)
- Seed BENCHMRK, Red Deck, White Stake; full seed analysis available,
  including shop, pack, voucher, tag, and boss sequences
- Result: ante 11, best hand 1,074,154, ante-8 victory achieved; final loss
  to The Mouth at 3,068,130 of 14,400,000
- The run was controlled entirely through the provided local HTTP API
- "A patched API issue required restoring the saved run, but no gameplay
  state or resources were altered"
- Key build: Swashbuckler, Duo, Polychrome Egg, two Throwbacks at X3; Pair
  reached level 20
- Notable mistake, in its words: "a Death target-order mismatch overwrote a
  Glass Jack instead of duplicating it, materially hurting the Ante 11
  attempt"

## Pending

- Opus 4.8 runs (2026-07-13): sessions predate the interview protocol.
- Opus 5 runs 1-5 (2026-07-24..26) and seed-only run (2026-08-09): interviews
  pending where sessions still exist.
- Fable 5 cold + seed-informed runs (2026-07-27): interview pending.

Per PROTOCOL.md: publication of this repository preceded these interviews by
operator decision; any model that declines when asked will have its run
redacted from the public record.
