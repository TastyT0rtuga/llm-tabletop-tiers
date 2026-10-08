#!/usr/bin/env python3
"""Regenerate the figures for the LLM tabletop-tier study from data/*.csv.

Usage:  python make_charts.py
Outputs PNGs into charts/.  Depends only on matplotlib + numpy.
"""
import csv
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "charts")
os.makedirs(OUT, exist_ok=True)

# ---- typography: use Inter if present, else the matplotlib default ----------
# Inter if it is installed anywhere usual (Linux, macOS, Windows); otherwise matplotlib's default sans-serif.
_font_dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"), os.path.expanduser("~/.local/share/fonts"),
              "/Library/Fonts", os.path.expanduser("~/Library/Fonts"), os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")]
for d in _font_dirs:
    for path in glob.glob(os.path.join(d, "**", "Inter*.[ot]tf"), recursive=True):
        try:
            fm.fontManager.addfont(path)
        except Exception:
            pass
if any(f.name == "Inter" for f in fm.fontManager.ttflist):
    plt.rcParams["font.family"] = "Inter"
plt.rcParams["font.size"] = 11.5

# ---- palette ----------------------------------------------------------------
TIERS = ["top", "mixed", "throttled", "floor"]
LABEL = {
    "top": "Top (as played)",
    "mixed": "Mixed (cheap red only)",
    "throttled": "Throttled (cheapest per maker)",
    "floor": "Floor (one small model)",
}
COL = {"top": "#1b6ca8", "mixed": "#2a9d8f", "throttled": "#e0922f", "floor": "#9a4a3c"}
INK = "#1a1a1a"
GRID = "#e6e6e6"
MUTE = "#6b6b6b"


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return list(csv.DictReader(fh))


def style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(length=0, colors=INK)
    ax.set_axisbelow(True)


def header(fig, title, subtitle):
    fig.text(0.06, 0.955, title, fontsize=15, fontweight="bold", color=INK,
             ha="left", va="top")
    if subtitle:
        fig.text(0.06, 0.902, subtitle, fontsize=9.5, color=MUTE,
                 ha="left", va="top")


def caption(fig, text):
    fig.text(0.06, 0.012, text, fontsize=8.5, color=MUTE, ha="left")


# ---- 1. headline: mean quality by tier --------------------------------------
def chart_quality():
    rows = {r["metric"]: r for r in load("summary.csv")}
    vals = [float(rows["Mean of six scores"][t]) for t in TIERS]
    lo = [float(rows["Mean of six CI low"][t]) for t in TIERS]
    hi = [float(rows["Mean of six CI high"][t]) for t in TIERS]
    fig, ax = plt.subplots(figsize=(8.4, 4.8), dpi=200)
    x = np.arange(len(TIERS))
    ax.bar(x, vals, width=0.62, color=[COL[t] for t in TIERS])
    ax.errorbar(x, vals, yerr=[np.subtract(vals, lo), np.subtract(hi, vals)], fmt="none", ecolor=INK, elinewidth=1.2, capsize=5)
    for xi, v, h in zip(x, vals, hi):
        ax.text(xi, h + 0.06, f"{v:.2f}", ha="center", va="bottom",
                fontweight="bold", color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels([LABEL[t].replace(" (", "\n(") for t in TIERS], fontsize=10)
    ax.set_ylim(0, 5)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_ylabel("Mean of six quality scores (1–5)")
    style(ax)
    header(fig, "Overall exercise quality by model tier",
           "Blind-graded mean of six scores, 95% bootstrap intervals — top and mixed are indistinguishable")
    fig.subplots_adjust(top=0.83, bottom=0.16, left=0.09, right=0.97)
    caption(fig, "6 scenarios × 3 replicates × 4 tiers · 50 blind gradings by 3 models from 3 makers · Oct 2026")
    fig.savefig(os.path.join(OUT, "01_quality_by_tier.png"), facecolor="white")
    plt.close(fig)


# ---- 2. where throttling hurts: six dimensions ------------------------------
def chart_dimensions():
    rows = load("grades.csv")
    rows.sort(key=lambda r: float(r["top"]) - float(r["throttled"]), reverse=True)
    dims = [r["dimension"] for r in rows]
    y = np.arange(len(dims))[::-1]
    h = 0.2
    fig, ax = plt.subplots(figsize=(8.8, 6.0), dpi=200)
    for i, t in enumerate(TIERS):
        vals = [float(r[t]) for r in rows]
        off = (1.5 - i) * h
        ax.barh(y + off, vals, height=h, color=COL[t], label=LABEL[t])
        for yi, v in zip(y, vals):
            ax.text(v + 0.04, yi + off, f"{v:.2f}", va="center", ha="left",
                    fontsize=8.8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(dims)
    ax.set_xlim(0, 5.4)
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.xaxis.grid(True, color=GRID, linewidth=1)
    ax.set_xlabel("Score (1–5)")
    style(ax)
    header(fig, "Where cutting model cost hurts most",
           "Ordered by the top→throttled drop · referee rigor and grounding fall hardest; cheap red costs almost nothing")
    handles = [plt.Rectangle((0, 0), 1, 1, color=COL[t]) for t in TIERS]
    fig.legend(handles, [LABEL[t] for t in TIERS], loc="upper center",
               bbox_to_anchor=(0.56, 0.875), ncol=4, frameon=False, fontsize=8.8)
    fig.subplots_adjust(top=0.79, bottom=0.11, left=0.27, right=0.98)
    caption(fig, "50 blind gradings over 72 runs (3 replicates per cell)")
    fig.savefig(os.path.join(OUT, "02_dimensions_by_tier.png"), facecolor="white")
    plt.close(fig)


# ---- 3. the tradeoff: cost vs quality ---------------------------------------
def chart_cost_vs_quality():
    cost = {r["metric"]: r for r in load("cost.csv")}
    summ = {r["metric"]: r for r in load("summary.csv")}
    pts = {t: (float(cost["Cost per run (USD)"][t]),
               float(summ["Mean of six scores"][t])) for t in TIERS}
    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=200)
    for t in TIERS:
        xv, yv = pts[t]
        ax.scatter([xv], [yv], s=340, color=COL[t], zorder=3,
                   edgecolor="white", linewidth=1.5)
    # label placement tuned to avoid overlap
    place = {
        "top":       (pts["top"][0],       pts["top"][1] - 0.13,  "center", "top"),
        "mixed":     (pts["mixed"][0],     pts["mixed"][1] + 0.13, "center", "bottom"),
        "throttled": (pts["throttled"][0],  pts["throttled"][1] + 0.13, "center", "bottom"),
        "floor":     (pts["floor"][0],      pts["floor"][1] - 0.13, "center", "top"),
    }
    for t, (lx, ly, ha, va) in place.items():
        xv, yv = pts[t]
        ax.text(lx, ly, f"{LABEL[t]}\n${xv:.2f}/run · {yv:.2f} quality",
                ha=ha, va=va, fontsize=9.2, color=INK, fontweight="bold")
    ax.annotate("Mixed: same quality as top for 79% of the cost",
                xy=pts["mixed"], xytext=(0.125, 4.05),
                fontsize=9, color=MUTE,
                arrowprops=dict(arrowstyle="->", color=MUTE, lw=1))
    ax.set_xlim(0.10, 0.50)
    ax.set_ylim(2.9, 4.7)
    ax.xaxis.grid(True, color=GRID, linewidth=1)
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_xlabel("Cost per run (USD)")
    ax.set_ylabel("Mean quality (1–5)")
    style(ax)
    header(fig, "Cost vs. quality — where the money actually matters",
           "Up and to the left is better value")
    fig.subplots_adjust(top=0.83, bottom=0.12, left=0.09, right=0.97)
    caption(fig, "Cost = mean of 18 runs per tier from each run's own ledger · quality = mean of six, 50 gradings")
    fig.savefig(os.path.join(OUT, "03_cost_vs_quality.png"), facecolor="white")
    plt.close(fig)


# ---- 4. trust failures: invented facts and rule breaks ----------------------
def chart_trust():
    rows = {r["metric"]: r for r in load("summary.csv")}
    metrics = ["Invented facts (count)", "Rule breaks (count)"]
    short = ["Invented facts\nper run", "Rule breaks\nper run"]
    x = np.arange(len(metrics))
    w = 0.2
    fig, ax = plt.subplots(figsize=(8.4, 5.0), dpi=200)
    for i, t in enumerate(TIERS):
        vals = [float(rows[m][t]) for m in metrics]
        off = (i - 1.5) * w
        ax.bar(x + off, vals, width=w, color=COL[t], label=LABEL[t])
        for xi, v in zip(x, vals):
            ax.text(xi + off, v + 0.02, f"{v:.2f}", ha="center", va="bottom",
                    fontsize=8.8, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(short)
    ax.set_ylim(0, 2.6)
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_ylabel("Mean count per run (lower is better)")
    style(ax)
    header(fig, "The failure that matters: false comfort",
           "A cheap referee lets invented facts through; a cheap red does not add any (mixed ≈ top)")
    ax.legend(loc="upper right", frameon=False, fontsize=9.3)
    fig.subplots_adjust(top=0.82, bottom=0.11, left=0.09, right=0.97)
    caption(fig, "Means per run over 50 blind gradings; lower is better")
    fig.savefig(os.path.join(OUT, "04_trust_failures.png"), facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    chart_quality()
    chart_dimensions()
    chart_cost_vs_quality()
    chart_trust()
    print("wrote:", ", ".join(sorted(os.listdir(OUT))))
