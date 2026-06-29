"""
Generate the accuracy bar chart for OpenClaw-Govern from real benchmark output.

Accuracy is computed directly from results/composition_benchmark.csv (the `ok`
column) so the figure can never drift from the measured results. Run the
benchmark first:

    python3 experiments/composition_benchmark.py --csv results/composition_benchmark.csv
    python3 figures/generate_benchmark_plots.py
"""

import csv
from collections import OrderedDict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "results" / "composition_benchmark.csv"

# Display order and short labels.
LABELS = OrderedDict([
    ("none", "None"),
    ("sarc_only", "SARC"),
    ("authz_only", "AuthZ"),
    ("guardrail_only", "Guardrail"),
    ("roma_only", "ROMA"),
    ("async_only", "Async"),
    ("naive_composition", "Naive"),
    ("priority_composition", "Priority"),
    ("openclaw_ordered", "OpenClaw"),
])

# Tally accuracy from the measured CSV.
totals = {k: [0, 0] for k in LABELS}  # strategy -> [correct, total]
with CSV_PATH.open() as handle:
    for row in csv.DictReader(handle):
        strat = row["strategy"]
        if strat not in totals:
            continue
        totals[strat][1] += 1
        if str(row["ok"]).strip().lower() == "true":
            totals[strat][0] += 1

strategies = [LABELS[k] for k in LABELS]
accuracy = [(totals[k][0] / totals[k][1]) if totals[k][1] else 0.0 for k in LABELS]

fig, ax = plt.subplots(figsize=(8, 4.5))

colors = []
for k in LABELS:
    if k == "openclaw_ordered":
        colors.append("#4CAF50")      # our approach
    elif k == "priority_composition":
        colors.append("#fd8d3c")      # strongest baseline
    elif k == "naive_composition":
        colors.append("#ff7f7f")      # weak composition baseline
    else:
        colors.append("#d3d3d3")      # single-module / none

bars = ax.bar(strategies, [a * 100 for a in accuracy],
              color=colors, edgecolor="black", linewidth=1.2)

ax.set_ylabel("Accuracy (%)", fontsize=11)
ax.set_title("Composition Correctness (8 scenarios)", fontsize=12, fontweight="bold")
ax.set_ylim(0, 112)
ax.axhline(y=100, color="green", linestyle="--", linewidth=1.3, alpha=0.7, label="Perfect")
ax.grid(axis="y", alpha=0.3, linestyle="--")

for bar, k in zip(bars, LABELS):
    correct, total = totals[k]
    ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 2,
            f"{correct}/{total}", ha="center", va="bottom", fontsize=9)

ax.legend(loc="upper left")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

png = ROOT / "figures" / "benchmark_accuracy.png"
svg = ROOT / "figures" / "benchmark_accuracy.svg"
plt.savefig(png, dpi=300, bbox_inches="tight")
plt.savefig(svg, format="svg", bbox_inches="tight")
plt.close()

print("Accuracy tallied from", CSV_PATH)
for k in LABELS:
    correct, total = totals[k]
    print(f"  {k:22s} {correct}/{total}")
print("Wrote:", png)
print("Wrote:", svg)
