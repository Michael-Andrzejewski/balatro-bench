"""Offline tests for the Inspect port, against the mock game. No LLM, no Balatro.

    python test_harness.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from inspect_ai import eval as inspect_eval  # noqa: E402

from balatro_task import balatro_bench  # noqa: E402
from balatro_tools import ApiError, rpc_sync, summarize  # noqa: E402
from mock_game import serve  # noqa: E402


def test_summary_and_sandbox(port: int) -> None:
    g = rpc_sync(port, "gamestate")
    assert g["state"] == "MENU", g
    assert "state=MENU" in summarize(g)
    for m in ("set", "add", "load"):
        try:
            rpc_sync(port, m, {})
        except ApiError as e:
            assert "disabled" in str(e)
        else:
            raise AssertionError(f"{m} should be refused")
    print("sandbox refusal and summary: ok")


def test_scripted_run(port: int) -> None:
    logs = inspect_eval(
        balatro_bench(ports=str(port), player="scripted"),
        model="mockllm/model",
        log_dir=str(Path(__file__).parent / "logs-test"),
        display="none",
    )
    log = logs[0]
    assert log.status == "success", log.status
    sample = log.samples[0]
    sc = sample.scores["balatro_scorer"]
    md = sc.metadata
    print("score:", sc.value, "|", sc.answer)
    print("metrics:", {k: v.value for k, v in log.results.scores[0].metrics.items()})
    assert md["sandbox_verified"] is True
    assert md["game_over"] is True, md["final_state"]
    assert sc.value == 3, sc.value  # mock dies on the ante-3 boss
    assert md["best_hand"] > 0
    assert md["plays"] > 0
    assert md["journal"] and "scripted" in md["journal"][0]["note"]
    assert "ante=3" in sc.answer
    print("scripted end-to-end run: ok")


if __name__ == "__main__":
    srv = serve(12399, die_at_ante=3)
    try:
        test_summary_and_sandbox(12399)
        # The scripted run consumes the instance (MENU -> GAME_OVER); use a fresh one.
        srv2 = serve(12398, die_at_ante=3)
        test_scripted_run(12398)
        srv2.shutdown()
    finally:
        srv.shutdown()
    print("all tests passed")
