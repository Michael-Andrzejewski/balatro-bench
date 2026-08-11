"""Generate per-ante progression graphs for Balatro Bench from per-ante-data.json.

Outputs (into analysis/):
  graph-all-runs.png    every run's best hand per ante vs the blind curve
  graph-opus5.png       Opus 5's five attempts
  graph-opus48.png      Opus 4.8's three attempts
  graph-modes.png       final ante reached, grouped by the four bench modes

Usage: python make_graphs.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).parent
DATA = json.loads((HERE / "per-ante-data.json").read_text(encoding="utf-8"))

BLIND_BASE = {int(k): v for k, v in DATA["meta"]["blind_base_by_ante"].items()}
RUNS = DATA["runs"]

MODE_COLORS = {1: "#1f77b4", 2: "#2ca02c", 3: "#ff7f0e", 4: "#d62728", None: "#7f7f7f"}
MODE_LABELS = {
    1: "mode 1: cold",
    2: "mode 2: journal (attempt 2)",
    3: "mode 3: journal (attempt 3)",
    4: "mode 4: seed-informed",
    None: "other / baseline",
}
PLAYER_MARKERS = {"Opus 5": "o", "Opus 4.8": "s", "Fable 5": "^", "Sol (GPT-5.6)": "v", "michael": "D", "rulebot": "P"}


def series(run):
    pts = [(int(a), v) for a, v in run["per_ante"].items() if v is not None]
    pts.sort()
    return [p[0] for p in pts], [p[1] for p in pts]


def boss_curve(max_ante):
    antes = [a for a in sorted(BLIND_BASE) if a <= max_ante]
    return antes, [BLIND_BASE[a] * 2 for a in antes]


def draw_boss_curve(ax, max_ante):
    x, y = boss_curve(max_ante)
    ax.plot(x, y, "k--", linewidth=1.2, alpha=0.6, label="boss blind requirement (2x base)")


def end_marker(ax, run, color):
    """Mark how the run ended: X where it died, star ring at ante 8 if it won."""
    xs, ys = series(run)
    if not xs:
        return
    if run["won_base"] and 8 in xs:
        i = xs.index(8)
        ax.scatter([8], [ys[i]], s=170, facecolors="none", edgecolors="goldenrod",
                   linewidths=1.6, zorder=4)
    last_x, last_y = xs[-1], ys[-1]
    # death happens at final_ante; if we have no value there, sit the X on the boss line
    fx = run["final_ante"]
    fy = last_y if last_x == fx else BLIND_BASE.get(fx, last_y) * 2
    ax.scatter([fx], [fy], marker="x", s=70, color=color, zorder=5)


def style_axes(ax, max_ante, title):
    ax.set_yscale("log")
    ax.set_xlabel("ante")
    ax.set_ylabel("best single hand (chips, log scale)")
    ax.set_xticks(range(1, max_ante + 1))
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.25)
    ax.axvline(8, color="goldenrod", alpha=0.35, linewidth=1)
    ax.text(8.05, ax.get_ylim()[0] * 1.5, "base-game win", color="goldenrod",
            fontsize=8, rotation=90, va="bottom")


def plot_run(ax, run, color, label, linestyle="-"):
    xs, ys = series(run)
    if not xs:
        return
    marker = PLAYER_MARKERS.get(run["player"], "o")
    if run["endpoint_only"]:
        ax.scatter(xs, ys, marker=marker, s=110, color=color, zorder=5, label=label)
    else:
        ax.plot(xs, ys, linestyle=linestyle, marker=marker, markersize=5,
                color=color, linewidth=1.6, label=label)
    end_marker(ax, run, color)


def fig_all_runs():
    fig, ax = plt.subplots(figsize=(11, 7))
    max_ante = 15
    draw_boss_curve(ax, max_ante)
    for run in RUNS:
        color = MODE_COLORS[run["mode"]]
        impure = "IMPURE" in run.get("mode_purity", "")
        label = f'{run["player"]} — {run["condition"]} ({run["date"]}, ante {run["final_ante"]})'
        plot_run(ax, run, color, label, linestyle=":" if impure else "-")
    style_axes(ax, max_ante, "Balatro Bench (seed BENCHMRK): best single hand per ante, all runs")
    ax.legend(fontsize=7.5, loc="upper left", framealpha=0.9)
    note = ("color = mode (blue cold · green journal-2 · orange journal-3 · red seed-informed · gray other)\n"
            "dotted = impure for its mode · X = run ended · gold ring = ante-8 win · lone markers = endpoint-only data")
    fig.text(0.5, 0.005, note, ha="center", fontsize=7.5, color="#444")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(HERE / "graph-all-runs.png", dpi=160)
    plt.close(fig)


def fig_player(player, fname, title):
    fig, ax = plt.subplots(figsize=(10, 6.5))
    runs = [r for r in RUNS if r["player"] == player]
    max_ante = max(r["final_ante"] for r in runs) + 1
    draw_boss_curve(ax, max_ante)
    for run in runs:
        color = MODE_COLORS[run["mode"]]
        impure = "IMPURE" in run.get("mode_purity", "")
        label = f'{run["condition"]} ({run["date"]}, ante {run["final_ante"]})'
        plot_run(ax, run, color, label, linestyle=":" if impure else "-")
    style_axes(ax, max_ante, title)
    ax.legend(fontsize=8, loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(HERE / fname, dpi=160)
    plt.close(fig)


def fig_modes():
    fig, ax = plt.subplots(figsize=(9, 6))
    order = ["Opus 4.8", "Opus 5", "Fable 5", "Sol (GPT-5.6)", "michael", "rulebot"]
    xpos = {1: 1, 2: 2, 3: 3, 4: 4, None: 0}
    offsets = {"Opus 4.8": -0.13, "Opus 5": 0.0, "Fable 5": 0.26, "Sol (GPT-5.6)": -0.26, "michael": 0.13, "rulebot": -0.26}
    for run in RUNS:
        x = xpos[run["mode"]] + offsets.get(run["player"], 0)
        impure = "IMPURE" in run.get("mode_purity", "")
        color = MODE_COLORS[run["mode"]]
        marker = PLAYER_MARKERS.get(run["player"], "o")
        face = "none" if impure else color
        ax.scatter([x], [run["final_ante"]], marker=marker, s=150, facecolors=face,
                   edgecolors=color, linewidths=1.8, zorder=4)
        tag = "W" if run["won_base"] else ""
        ax.annotate(f'a{run["final_ante"]}{tag}', (x, run["final_ante"]),
                    textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8)
    ax.axhline(8, color="goldenrod", alpha=0.4, linewidth=1)
    ax.text(-0.45, 8.1, "base-game win (ante 8)", color="goldenrod", fontsize=8)
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xticklabels(["other /\nbaseline", "1\ncold", "2\njournal\n(attempt 2)",
                        "3\njournal\n(attempt 3)", "4\nseed-\ninformed"], fontsize=9)
    ax.set_ylabel("final ante reached")
    ax.set_yticks(range(0, 17))
    ax.set_ylim(0, 16.5)
    ax.grid(True, axis="y", alpha=0.25)
    ax.set_title("Final ante by bench mode (hollow = run does not purely match its mode)")
    handles = [Line2D([], [], marker=PLAYER_MARKERS[p], linestyle="", color="#444",
                      markersize=9, label=p) for p in order]
    ax.legend(handles=handles, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(HERE / "graph-modes.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    fig_all_runs()
    fig_player("Opus 5", "graph-opus5.png",
               "Opus 5 on BENCHMRK: five attempts, best single hand per ante")
    fig_player("Opus 4.8", "graph-opus48.png",
               "Opus 4.8 on BENCHMRK: three attempts, best single hand per ante")
    fig_modes()
    print("wrote graph-all-runs.png, graph-opus5.png, graph-opus48.png, graph-modes.png")
