#!/usr/bin/env python3
"""Production figures 1-9 for the revised manuscript (Cordella & Cappelli,
Artificial Life, resubmission of ARTL-2026-0189). Vector PDF + PNG preview.
Data from data_v4.json (harvest_v4.py), protocol v4."""
import json
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"; GRID = "#e1e0d9"; BASE = "#c3c2b7"
C_CORRECT = "#2a78d6"; C_UNDER = "#c98500"; C_KANG = "#d03b3b"; C_UNRES = "#898781"
C_ORANGE = "#eb6834"; C_PURPLE = "#4a3aa7"; C_GREEN = "#2C7A4B"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": BASE,
    "axes.linewidth": 0.8, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "pdf.fonttype": 42, "savefig.facecolor": "white",
})
DATA = json.load(open("data_v4.json"))

def tint(hex_color, f=0.85):
    r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * f); g = int(g + (255 - g) * f); b = int(b + (255 - b) * f)
    return f"#{r:02x}{g:02x}{b:02x}"

def despine(ax, keep=("left", "bottom")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)

def save(fig, name):
    fig.savefig(f"figs/{name}.pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(f"figs/{name}.png", bbox_inches="tight", pad_inches=0.04, dpi=200)
    plt.close(fig)
    print("saved", name)

def box(ax, x, y, w, h, text, fc, ec, fontsize=8.6, bold=True, tc=INK, lw=1.2, ha="center"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.025",
                       facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3)
    ax.add_patch(p)
    tx = x + w / 2 if ha == "center" else x + 0.12
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fontsize, color=tc,
            zorder=4, fontweight="bold" if bold else "normal", linespacing=1.25)

def arrow(ax, xy_from, xy_to, color=INK2, lw=1.4, style="-|>", rad=0.0, ls="-"):
    a = FancyArrowPatch(xy_from, xy_to, arrowstyle=style, mutation_scale=13,
                        color=color, linewidth=lw, linestyle=ls, zorder=2,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2)
    ax.add_patch(a)

# =====================================================================
# FIGURE 1 — experimental setup (new)
# =====================================================================
def figure1():
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7.0); ax.axis("off")
    # WORLD
    box(ax, 0.25, 5.0, 3.9, 1.7,
        "WORLD\n32 scenes = shape {triangle, circle}\n× colour {red, blue} × motion {fast, still}\n× number {1, 2, 3, 4}",
        "#f5f5f2", MUTED, fontsize=7.0, bold=False)
    # INFORMANT
    box(ax, 5.85, 5.0, 3.9, 1.7,
        "INFORMANT — speaker of L2\nGPT-4o-mini at temperature 0 with lexicon L2\nin its system prompt (Appendix A), or a\nrule-based simulator (SIM) applying Table 1",
        tint(C_ORANGE, 0.88), C_ORANGE, fontsize=6.7, bold=False)
    # LEARNER
    box(ax, 0.25, 0.6, 4.9, 2.9,
        "LEARNER — deterministic script\n"
        "perceives each scene in its own categories\n(L1's attributes + parity): ⟨shape, colour, motion, parity⟩\n"
        "keeps, for every L2 word $w$, a set $H_w$ of candidate referents\n"
        "(conjunctions of ≤ 2 attribute values; |$H_0$| = 32)\n"
        "requests scenes (random, minimal pairs, probes)\n"
        "outputs one entry per word: a referent, a declared\nequivalence class, or “unresolved”",
        tint(C_CORRECT, 0.90), C_CORRECT, fontsize=6.5, bold=False)
    # EXPERIMENTER
    box(ax, 6.25, 0.6, 3.5, 2.9,
        "EXPERIMENTER — script\nholds the ground truth (Table 1):\nthe rule behind every L2 word\n\n"
        "scores every entry:\ncorrect / underdetermined /\nkangaroo / unresolved\n\n"
        "checks the informant’s execution\nfidelity on every logged $u(s)$",
        "#f5f5f2", MUTED, fontsize=6.8, bold=False)
    # attribute vector (dashed, left)
    arrow(ax, (0.7, 5.0), (0.7, 3.5), color=INK2, lw=1.3, ls=(0, (4, 2)))
    ax.text(0.85, 4.25, "attribute vector of $s$\n⟨triangle, red, fast, even⟩", fontsize=6.5,
            color=INK2, ha="left", va="center")
    # request scene (blue, up)
    arrow(ax, (3.4, 3.5), (3.4, 5.0), color=C_CORRECT, lw=1.6)
    ax.text(3.55, 4.25, "1. request scene $s$\n(random / minimal\npair / probe)", fontsize=6.6,
            color=C_CORRECT, ha="left", va="center")
    # description world -> informant
    arrow(ax, (4.15, 5.85), (5.85, 5.85), color=INK2, lw=1.5)
    ax.text(5.0, 6.15, "2. description of $s$", fontsize=6.6, color=INK2, ha="center")
    ax.text(5.0, 5.62, "“2 red triangles\nmoving fast”", fontsize=6.2, color=MUTED, ha="center",
            va="top", style="italic")
    # utterance informant -> learner
    arrow(ax, (6.7, 5.0), (4.85, 3.5), color=C_ORANGE, lw=1.6)
    ax.text(6.3, 4.3, "3. utterance $u(s)$\n“ZUMU TAK”", fontsize=6.8, color=C_ORANGE,
            ha="left", va="center")
    # final dictionary
    arrow(ax, (5.15, 2.05), (6.25, 2.05), color=C_CORRECT, lw=1.6)
    ax.text(5.7, 2.28, "final\ndictionary", fontsize=6.2, color=C_CORRECT, ha="center", va="bottom")
    # fidelity
    arrow(ax, (8.1, 3.5), (8.1, 5.0), color=MUTED, lw=1.2, ls=(0, (4, 2)), style="<|-|>")
    ax.text(8.22, 4.25, "fidelity check\n(every logged $u(s)$\nvs the L2 rule)", fontsize=6.3,
            color=MUTED, ha="left", va="center")
    ax.text(5.0, 0.15, "One exchange = steps 1–3.  A run = ostension → minimal pairs → probes (→ recovery round).  "
            "The learner never sees Table 1.", fontsize=6.8, color=INK2, ha="center", style="italic")
    save(fig, "Figure1")

# =====================================================================
# FIGURE 2 — the anti-kangaroo state machine (former Figure 1, relabelled)
# =====================================================================
def figure2():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.9); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.15, 1.45), 2.7, 3.7,
                                boxstyle="round,pad=0.012,rounding_size=0.03",
                                facecolor="#f5f5f2", edgecolor=BASE, linewidth=1.0, zorder=1))
    ax.text(1.50, 4.82, "EVIDENCE — every exchange\nupdates every anchor (Eq. 2)",
            ha="center", va="center", fontsize=6.6, color=INK2, fontweight="bold")
    box(ax, 0.28, 3.78, 2.45, 0.6, "Ostension\n(6 random scenes)", tint(C_CORRECT, 0.92),
        C_CORRECT, fontsize=6.8, bold=False)
    box(ax, 0.28, 3.0, 2.45, 0.6, "Minimal pairs\n(one attribute varied)",
        tint(C_CORRECT, 0.92), C_CORRECT, fontsize=6.8, bold=False)
    box(ax, 0.28, 2.22, 2.45, 0.6, "Pre-registered probes\n(random or active, Eq. 4)",
        tint(C_CORRECT, 0.92), C_CORRECT, fontsize=6.8, bold=False)
    box(ax, 0.28, 1.58, 2.45, 0.46, "cross-situational elimination",
        "white", INK2, fontsize=6.6, bold=False, tc=INK2, lw=0.9)

    box(ax, 3.6, 3.55, 1.95, 0.78, "PROVISIONAL", tint(C_UNRES, 0.88), MUTED, fontsize=9.5)
    ax.text(4.575, 3.36, "$H_w = H_0$ (32 hypotheses)", ha="center", fontsize=6.8, color=INK2)
    box(ax, 7.7, 3.55, 1.95, 0.78, "PROMOTED", tint(C_CORRECT, 0.85), C_CORRECT, fontsize=9.5)
    ax.text(8.95, 3.36, "entry = $H_w$", ha="center", fontsize=6.8, color=INK2)
    box(ax, 3.6, 0.75, 1.95, 0.78, "UNRESOLVED", tint(C_UNDER, 0.85), C_UNDER, fontsize=9.5)
    ax.text(4.575, 0.56, "no promotion this round", ha="center", fontsize=6.8, color=INK2)
    box(ax, 7.7, 0.75, 1.95, 0.78, "REVOKED", tint(C_KANG, 0.85), C_KANG, fontsize=9.5)
    ax.text(8.675, 0.56, "quarantine", ha="center", fontsize=6.8, color=INK2)

    arrow(ax, (4.575, 5.4), (4.575, 4.40), color=INK2, lw=1.3)
    ax.text(4.7, 5.0, "new word $w$ heard", fontsize=7.2, color=INK2, ha="left")
    arrow(ax, (2.9, 3.2), (3.55, 3.85), color=INK2, lw=1.2)
    arrow(ax, (5.59, 3.94), (7.66, 3.94), color=C_CORRECT, lw=1.7)
    ax.text(6.625, 4.15, "clean probe round (Eq. 5):\n$M$ = 3 correct, 0 failed,\n≥ 1 discriminating pair",
            ha="center", va="bottom", fontsize=6.6, color=C_CORRECT)
    arrow(ax, (4.575, 3.30), (4.575, 1.58), color=C_UNDER, lw=1.5)
    ax.text(4.42, 2.45, "probe failure, or\nno discriminating\npair", fontsize=6.6,
            color="#9d6900", ha="right", va="center")
    arrow(ax, (5.59, 1.14), (8.1, 3.51), color=C_PURPLE, lw=2.0, rad=-0.18)
    ax.text(5.8, 0.68, "recovery round ($r$ = 2):\ntargeted minimal pair if\nneeded, then a clean round\nwith ≥ 1 positive probe",
            fontsize=6.3, color=C_PURPLE, ha="left", va="center")
    arrow(ax, (8.675, 3.51), (8.675, 1.58), color=C_KANG, lw=1.7)
    ax.text(8.8, 2.55, "later probe failure,\nor $H_w$ emptied by\nlater evidence", fontsize=6.5,
            color=C_KANG, ha="left", va="center")
    save(fig, "Figure2")

# =====================================================================
# FIGURE 3 — outcome composition per condition, 32-scene world (v4)
# =====================================================================
def figure3():
    conds = ["Random", "Random+R2", "Active", "Active+R2"]
    labels = ["Random", "Random + R2", "Active", "Active + R2"]
    cats = [("giuste", "Correct", C_CORRECT), ("canguri", "Kangaroos", C_KANG),
            ("irrisolte", "Unresolved", C_UNRES)]
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    x = range(len(conds)); w = 0.24
    for j, (key, label, color) in enumerate(cats):
        means = [statistics.mean(DATA["four_arm"]["v4/" + c][key]) for c in conds]
        sds = [statistics.stdev(DATA["four_arm"]["v4/" + c][key]) for c in conds]
        xs = [i + (j - 1) * (w + 0.03) for i in x]
        ax.bar(xs, means, width=w, color=color, edgecolor="white", linewidth=0.6,
               label=label, zorder=3)
        ax.errorbar(xs, means, yerr=sds, fmt="none", ecolor=INK2, elinewidth=0.9,
                    capsize=2.4, capthick=0.9, zorder=4)
        for xi, m, sd in zip(xs, means, sds):
            if m == 0:
                ax.text(xi, 0.09, "0", ha="center", va="bottom", fontsize=7.5,
                        color=(C_KANG if key == "canguri" else INK2), fontweight="bold")
            else:
                ax.text(xi, m + sd + 0.13, f"{m:.2f}", ha="center", va="bottom",
                        fontsize=7.2, color=INK2)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels)
    ax.set_ylim(0, 7.0); ax.set_yticks(range(0, 7))
    ax.set_ylabel("L2 words per run (of 6)")
    ax.yaxis.grid(True, color=GRID, linewidth=0.7, zorder=0); ax.set_axisbelow(True)
    despine(ax)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3,
              fontsize=8, handlelength=1.2, handleheight=1.0, columnspacing=1.2)
    fig.text(0.5, -0.06, "Underdetermined promotions: 0 in every condition. Every unresolved word holds the right "
             "referent as its only surviving hypothesis.\nRandom + R2 and Active + R2 use identical exchange "
             "counts (56.0 ± 7.3 per run).", ha="center", va="top", fontsize=6.9, color=INK2)
    save(fig, "Figure3")

# =====================================================================
# FIGURE 4 — outcome composition under the two injected traps (v4)
# =====================================================================
def figure4():
    order = [("correct", "Correct", C_CORRECT), ("underdet", "Underdetermined (declared class)", C_UNDER),
             ("kangaroo", "Kangaroo", C_KANG), ("unresolved", "Unresolved (abstention)", C_UNRES)]
    names = ["A naive", "B statistical", "C full, weak", "C full, strong"]
    ylabels = ["A  naive ostension", "B  passive elimination", "C  full protocol, weak trap",
               "C  full protocol, strong trap"]
    panels = [("zumu_forma", "Trap T1 — word ZUMU (red ∧ fast), decoy red ∧ triangle; pool 24/32 scenes"),
              ("tin_moto", "Trap T2 — word TIN (odd), decoy motion = still; pool 16/32 scenes")]
    fig, axes = plt.subplots(2, 1, figsize=(6.8, 4.3), sharex=True)
    for ax, (tkey, title) in zip(axes, panels):
        ys = range(len(names))[::-1]
        for yi, arm in zip(ys, names):
            counts = DATA["traps"][tkey][arm]["counts"]; left = 0
            for key, label, color in order:
                v = counts[key]
                if v == 0:
                    continue
                hatch = "///" if key == "kangaroo" else None
                ax.barh(yi, v, left=left, height=0.58, color=color, edgecolor="white",
                        linewidth=1.0, hatch=hatch, zorder=3)
                tc = "white" if key in ("correct", "kangaroo") else INK
                ax.text(left + v / 2, yi, str(v), ha="center", va="center", fontsize=7.5,
                        color=tc, fontweight="bold", zorder=4)
                left += v
        ax.set_yticks(list(ys)); ax.set_yticklabels(ylabels, fontsize=7.6)
        ax.set_xlim(0, 50)
        ax.set_title(title, fontsize=8.0, color=INK, loc="left", pad=4)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7, zorder=0); ax.set_axisbelow(True)
        despine(ax)
    axes[1].set_xlabel("Runs (of 50)")
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor="white",
                             hatch=("///" if k == "kangaroo" else None)) for k, _, c in order]
    fig.legend(handles, [l for _, l, _ in order], frameon=False, ncol=4, loc="upper center",
               bbox_to_anchor=(0.55, 1.04), fontsize=7.4, handlelength=1.2, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    save(fig, "Figure4")

# =====================================================================
# FIGURE 5 — detection times (both traps, condition C-weak)
# =====================================================================
def figure5():
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7), sharey=True)
    for ax, (tkey, title) in zip(axes, [("zumu_forma", "T1 — ZUMU, conjunctive decoy"),
                                        ("tin_moto", "T2 — TIN, atomic decoy")]):
        det = DATA["traps"][tkey]["C full, weak"]["detections"]
        mean = statistics.mean(det)
        bins = list(range(min(det) - 1, max(det) + 3, 2))
        ax.hist(det, bins=bins, color=C_CORRECT, edgecolor="white", linewidth=0.8, zorder=3)
        ax.axvline(mean, color=INK, linestyle=(0, (4, 2)), linewidth=1.1, zorder=4)
        ax.text(mean + 0.4, ax.get_ylim()[1] * 0.80, f"mean = {mean:.1f}", fontsize=7.8,
                color=INK, va="top")
        ax.set_title(title, fontsize=8.0, loc="left", color=INK)
        ax.text(0.98, 0.97, f"decoy eliminated in {len(det)}/50 runs", transform=ax.transAxes,
                ha="right", va="top", fontsize=7.2, color=INK2)
        ax.set_xlabel("Exchange at which the decoy was eliminated")
        ax.yaxis.grid(True, color=GRID, linewidth=0.7, zorder=0); ax.set_axisbelow(True)
        despine(ax)
    axes[0].set_ylabel("Runs")
    fig.tight_layout()
    save(fig, "Figure5")

# =====================================================================
# FIGURE 6 — generate-and-test architecture, as a stage diagram with
#            input / output / discarded at each stage
# =====================================================================
def figure6():
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7.4); ax.axis("off")
    ax.axvline(3.3, color=MUTED, linestyle=(0, (5, 3)), linewidth=1.0)
    ax.text(1.65, 7.15, "LLM PROPOSER — untrusted", ha="center", fontsize=8.2,
            color=C_ORANGE, fontweight="bold")
    ax.text(6.65, 7.15, "DETERMINISTIC SCRIPT — judge", ha="center", fontsize=8.2,
            color=C_CORRECT, fontweight="bold")
    box(ax, 3.5, 6.15, 6.1, 0.75,
        "TRIGGER — after ostension (8 episodes × 6 scenes) and probing,\nword $w$ has no surviving hypothesis in $H_0$",
        "#f5f5f2", MUTED, fontsize=6.8, bold=False)
    box(ax, 0.2, 3.2, 2.85, 1.7,
        "reads the observation table of $w$\n(≈ 70 rows: previous scene,\ncurrent scene, word present?)\n\nwrites free text ending with a\nJSON list of ≤ 5 rules in the DSL",
        tint(C_ORANGE, 0.88), C_ORANGE, fontsize=6.7, bold=False)
    arrow(ax, (3.5, 6.2), (1.6, 4.93), color=INK2, lw=1.3, rad=0.25)
    ax.text(1.1, 5.85, "observation\nlog", fontsize=6.6, color=INK2, ha="center", va="center")
    arrow(ax, (3.0, 4.75), (3.5, 5.15), color=C_ORANGE, lw=1.5)
    ax.text(2.55, 5.25, "raw response", fontsize=6.4, color=C_ORANGE, ha="center", va="center")
    ax.text(8.35, 5.72, "discarded at this stage", fontsize=6.6, color=C_KANG, ha="center",
            fontweight="bold")
    stages = [
        (4.75, "1  PARSE — the last JSON list\n    in the response",
         "no parseable list:\nHaiku 28/60, Sonnet 6/60 responses"),
        (3.65, "2  COMPILE + VALIDATE — every\n    atom checked against the DSL",
         "invented operators or attributes:\nHaiku 47/145, Sonnet 23/120 candidates"),
        (2.55, "3  RETROSPECTIVE FILTER —\n    against every logged row",
         "contradicted by a logged row:\nHaiku 87/98, Sonnet 54/97 compiled"),
        (1.45, "4  $M$ = 4 PRE-REGISTERED PROBES\n    on constructed pairs, ≥ 1 positive",
         "failed a probe:\n0 of 120 runs"),
    ]
    for y, text, disc in stages:
        box(ax, 3.5, y, 3.4, 0.8, text, tint(C_CORRECT, 0.90), C_CORRECT, fontsize=6.6,
            bold=False, ha="left")
        ax.text(7.15, y + 0.42, disc, fontsize=6.2, color=C_KANG, va="center", ha="left")
        arrow(ax, (6.92, y + 0.1), (9.8, y + 0.1), color=C_KANG, lw=0.8, style="-", ls=(0, (2, 2)))
    for y1 in (4.75, 3.65, 2.55):
        arrow(ax, (5.2, y1), (5.2, y1 - 0.3), color=C_CORRECT, lw=1.3)
    box(ax, 3.5, 0.35, 3.4, 0.8,
        "PROMOTED — $H_w$ = the candidates that\npassed every stage (scored over all\n33 × 32 scene pairs, Eq. 7)",
        tint(C_CORRECT, 0.80), C_CORRECT, fontsize=6.5, bold=False, ha="left")
    arrow(ax, (5.2, 1.45), (5.2, 1.15), color=C_CORRECT, lw=1.3)
    box(ax, 8.1, 0.35, 1.7, 0.8, "REJECTED\n$w$ stays\nunresolved", tint(C_KANG, 0.88),
        C_KANG, fontsize=6.8, bold=False)
    arrow(ax, (9.8, 4.85), (9.8, 1.15), color=C_KANG, lw=1.0)
    ax.text(5.0, 0.02, "“The LLM proposes; the script disposes.”  A rejected proposal costs coverage, never correctness.",
            ha="center", fontsize=7.0, color=INK2, style="italic")
    save(fig, "Figure6")

# =====================================================================
# FIGURE 7 — hard-word coverage per proposer instrument (with parser replay)
# =====================================================================
def figure7():
    panels = [
        ("(a) Archived instrument v3 — two worked examples in the prompt are the true rules",
         ["None\n(base space)", "Claude Haiku 4.5\ncopies 18%", "Claude Haiku 4.5\n(lenient parser,\nreplay)",
          "Claude Sonnet 4.6\ncopies 51%", "GPT-4o-mini\ncopies 96%", "Oracle\n(hand-coded)"],
         [0, 10, 15, 28, 28, 30], [0, 1, 1, 15, 24, 30], [None] * 6, 2),
        ("(b) Corrected instrument v4 — neutral worked examples",
         ["None\n(base space)", "Claude Haiku 4.5\ncopies 3%", "Claude Haiku 4.5\n(lenient parser,\nreplay)",
          "Claude Sonnet 4.6\ncopies 1%", "GPT-4o-mini\ncopies 36%", "Oracle\n(hand-coded)"],
         [0, 9, 12, 29, 28, 30], [0, 0, 0, 10, 0, 30], [None] * 6, 2),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 7.6))
    for ax, (title, proposers, nur, gumo, copied, shade) in zip(axes, panels):
        totals = [f"{(n + g) / 60 * 100:.0f}%" for n, g in zip(nur, gumo)]
        x = range(len(proposers)); w = 0.3
        ax.bar([i - w / 2 - 0.02 for i in x], [v / 30 * 100 for v in nur], width=w, color=C_CORRECT,
               edgecolor="white", linewidth=0.6, label="NUR (relational)", zorder=3)
        ax.bar([i + w / 2 + 0.02 for i in x], [v / 30 * 100 for v in gumo], width=w, color=C_ORANGE,
               edgecolor="white", linewidth=0.6, label="GUMO (XOR homonym)", zorder=3)
        for i, (n, g) in enumerate(zip(nur, gumo)):
            ax.text(i - w / 2 - 0.02, n / 30 * 100 + 2, f"{n}/30", ha="center", va="bottom",
                    fontsize=6.6, color=INK2)
            ax.text(i + w / 2 + 0.02, g / 30 * 100 + 2, f"{g}/30", ha="center", va="bottom",
                    fontsize=6.6, color=INK2)
            ax.text(i, 106, totals[i], ha="center", fontsize=8.2, color=INK, fontweight="bold")
        ax.plot(list(x), [0] * len(proposers), color=C_KANG, linewidth=1.2, marker="D",
                markersize=4.2, zorder=4, clip_on=False)
        ax.axvspan(shade - 0.5, shade + 0.5, color="#f5f5f2", zorder=0)
        ax.set_title(title, fontsize=7.8, loc="left", color=INK, pad=26)
        ax.set_xticks(list(x)); ax.set_xticklabels(proposers, fontsize=6.6)
        ax.set_ylim(0, 100); ax.set_yticks(range(0, 101, 25))
        ax.set_ylabel("Correct on hard words\n(%, 30 seeds)", fontsize=7.5)
        ax.yaxis.grid(True, color=GRID, linewidth=0.7, zorder=1); ax.set_axisbelow(True)
        despine(ax)
    axes[0].legend(frameon=False, loc="upper left", fontsize=7.0, handlelength=1.2)
    fig.text(0.5, -0.01, "Bold: hard-word coverage (NUR + GUMO, 60 word-runs). \"copies\": share of a model's compiled candidates that are verbatim copies "
             "of the prompt's worked examples.\nRed diamonds: kangaroos (wrong rule promoted) — 0 for every instrument and model.",
             ha="center", fontsize=6.8, color=INK2)
    fig.tight_layout(h_pad=2.5)
    save(fig, "Figure7")

# =====================================================================
# FIGURE 8 — degradation under informant noise (v4)
# =====================================================================
def figure8():
    levels = ["0.0", "0.005", "0.01", "0.02", "0.05", "0.1"]
    lab = ["0%", "0.5%", "1%", "2%", "5%", "10%"]
    xs = list(range(6))
    series = [("giuste", "Correct", C_CORRECT, "o"), ("irrisolte", "Unresolved", C_UNRES, "s"),
              ("canguri", "Kangaroos", C_KANG, "^")]
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for key, label, color, marker in series:
        means = [statistics.mean(DATA["noise"][l][key]) for l in levels]
        sds = [statistics.stdev(DATA["noise"][l][key]) for l in levels]
        ax.fill_between(xs, [m - s for m, s in zip(means, sds)], [m + s for m, s in zip(means, sds)],
                        color=color, alpha=0.13, linewidth=0, zorder=2)
        ax.plot(xs, means, color=color, linewidth=1.8, marker=marker, markersize=5.5,
                markeredgecolor="white", markeredgewidth=0.8, label=label, zorder=3, clip_on=False)
        ax.annotate(label, (xs[-1] + 0.12, means[-1]), fontsize=7.8, color=color, va="center",
                    fontweight="bold", annotation_clip=False)
    for x, l in zip(xs, levels):
        fid = statistics.mean(DATA["noise"][l]["fedelta"])
        ax.annotate(f"fidelity\n{fid:.1f}%", (x, -0.75), fontsize=6.6, color=MUTED, ha="center",
                    va="top", annotation_clip=False)
    ktot = [int(sum(DATA["noise"][l]["canguri"])) for l in levels]
    for x, k in zip(xs, ktot):
        ax.annotate(str(k), (x, 0.16), fontsize=6.8, color=C_KANG, ha="center")
    ax.text(2.5, 0.42, "total kangaroos over 50 runs", fontsize=6.6, color=C_KANG, ha="center")
    ax.set_xlim(-0.2, 5.4); ax.set_xticks(xs); ax.set_xticklabels(lab)
    ax.set_ylim(0, 6.2); ax.set_yticks(range(0, 7))
    ax.set_xlabel("Per-word flip probability $p$ (categorical spacing)", labelpad=24)
    ax.set_ylabel("L2 words per run (of 6)")
    ax.yaxis.grid(True, color=GRID, linewidth=0.7, zorder=1); ax.set_axisbelow(True)
    despine(ax)
    save(fig, "Figure8")

# =====================================================================
# FIGURE 9 — coverage vs exchanges across world sizes (equal-cost view)
# =====================================================================
def figure9():
    worlds = [("W32", "32 scenes · 6 words · |H$_0$| = 32"), ("W162", "162 scenes · 11 words · |H$_0$| = 56"),
              ("W486", "486 scenes · 14 words · |H$_0$| = 92"), ("W2048", "2048 scenes · 22 words · |H$_0$| = 146")]
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.0))
    for ax, (wk, title) in zip(axes.flat, worlds):
        n_words = DATA["worlds_meta"][wk]["parole"]
        for pol, color, rounds, marker in (("Random", C_UNRES, [1, 2, 3, 4, 6], "s"),
                                           ("Active", C_CORRECT, [1, 2], "o")):
            xs, ys = [], []
            for r in rounds:
                d = DATA["sweep"][f"{wk}/{pol}/{r}"]
                xs.append(statistics.mean(d["scambi"])); ys.append(100 * statistics.mean(d["giuste"]) / n_words)
            ax.plot(xs, ys, color=color, linewidth=1.7, marker=marker, markersize=5.5,
                    markeredgecolor="white", markeredgewidth=0.7, label=f"{pol} probes",
                    zorder=3 if pol == "Random" else 4, clip_on=False)
            for x, y, r in zip(xs, ys, rounds):
                if pol == "Random":
                    ax.annotate(f"{r} round{'s' if r > 1 else ''}", (x, y), xytext=(0, -10),
                                textcoords="offset points", fontsize=6.0, color=color, ha="center")
                elif r == 2:
                    ax.annotate("2 rounds", (x, y), xytext=(-4, 5), textcoords="offset points",
                                fontsize=6.0, color=color, ha="right")
        ax.set_title(title, fontsize=7.8, loc="left", color=INK)
        ax.set_ylim(0, 108); ax.set_yticks(range(0, 101, 25))
        ax.yaxis.grid(True, color=GRID, linewidth=0.7, zorder=0); ax.set_axisbelow(True)
        despine(ax)
    for ax in axes[1]:
        ax.set_xlabel("Exchanges per run (mean)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Correct entries (% of lexicon)")
    axes[0][0].legend(frameon=False, loc="lower right", fontsize=7.4, handlelength=1.6)
    fig.text(0.5, -0.01, "Points = mean over 50 seeds; labels = number of probing rounds (1 = no recovery round). "
             "Kangaroos and underdetermined promotions: 0 at every point.",
             ha="center", fontsize=6.8, color=INK2)
    fig.tight_layout()
    save(fig, "Figure9")

if __name__ == "__main__":
    import os
    os.makedirs("figs", exist_ok=True)
    for f in (figure1, figure2, figure3, figure4, figure5, figure6, figure7, figure8, figure9):
        f()
    print("done")
