"""Generate a UML class diagram PNG from the final PawPal+ implementation."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# ── Layout constants ──────────────────────────────────────────────────────────
FIG_W, FIG_H = 20, 13
BOX_PAD   = 0.18
HEADER_H  = 0.42
ROW_H     = 0.28
SEP       = 0.08          # gap between attribute and method sections
FONT_MAIN = 8.5
FONT_HDR  = 9.5
BG_HDR    = "#2C3E50"
BG_ATTR   = "#ECF0F1"
BG_METH   = "#D5DBDB"
TXT_HDR   = "white"
TXT_BODY  = "#1A252F"
BORDER    = "#2C3E50"

def draw_class(ax, x, y, name, attrs, methods, width=3.6):
    """Draw one UML class box and return its total height."""
    n_attr = len(attrs)
    n_meth = len(methods)
    box_h  = HEADER_H + n_attr * ROW_H + SEP + n_meth * ROW_H + BOX_PAD

    # Header
    hdr = mpatches.FancyBboxPatch(
        (x, y - HEADER_H), width, HEADER_H,
        boxstyle="square,pad=0", linewidth=1.2,
        edgecolor=BORDER, facecolor=BG_HDR, zorder=3
    )
    ax.add_patch(hdr)
    ax.text(x + width / 2, y - HEADER_H / 2, f"«class»\n{name}",
            ha="center", va="center", fontsize=FONT_HDR,
            fontweight="bold", color=TXT_HDR, zorder=4,
            linespacing=1.3)

    # Attributes section
    attr_h = n_attr * ROW_H + BOX_PAD
    attr_box = mpatches.FancyBboxPatch(
        (x, y - HEADER_H - attr_h), width, attr_h,
        boxstyle="square,pad=0", linewidth=1.2,
        edgecolor=BORDER, facecolor=BG_ATTR, zorder=3
    )
    ax.add_patch(attr_box)
    for i, attr in enumerate(attrs):
        ay = y - HEADER_H - BOX_PAD / 2 - (i + 0.5) * ROW_H
        ax.text(x + 0.12, ay, attr, ha="left", va="center",
                fontsize=FONT_MAIN, color=TXT_BODY, family="monospace", zorder=4)

    # Methods section
    meth_top = y - HEADER_H - attr_h - SEP
    meth_h   = n_meth * ROW_H + BOX_PAD
    meth_box = mpatches.FancyBboxPatch(
        (x, meth_top - meth_h), width, meth_h,
        boxstyle="square,pad=0", linewidth=1.2,
        edgecolor=BORDER, facecolor=BG_METH, zorder=3
    )
    ax.add_patch(meth_box)
    # thin separator line
    ax.plot([x, x + width], [meth_top, meth_top],
            color=BORDER, lw=0.6, zorder=4)
    for i, meth in enumerate(methods):
        my = meth_top - BOX_PAD / 2 - (i + 0.5) * ROW_H
        ax.text(x + 0.12, my, meth, ha="left", va="center",
                fontsize=FONT_MAIN, color="#154360", family="monospace",
                style="italic", zorder=4)

    bottom = meth_top - meth_h
    return box_h, bottom


def arrow(ax, x1, y1, x2, y2, label="", style="solid", color="#2C3E50"):
    ls = "-" if style == "solid" else "--"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=1.2, linestyle=ls),
                zorder=5)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.08, my, label, fontsize=7.5,
                color="#5D6D7E", zorder=6)


# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")
fig.patch.set_facecolor("#FDFEFE")

W = 3.7   # default class box width

# ── Task ─────────────────────────────────────────────────────────────────────
task_x, task_y = 7.8, 12.4
_, task_bot = draw_class(ax, task_x, task_y, "Task",
    attrs=[
        "+ title: str",
        "+ duration_minutes: int",
        "+ priority: str  # high/medium/low",
        "+ reason: str",
        "+ pet: Pet | None",
        "+ completed: bool",
        "+ frequency: str  # once/daily/weekly  [NEW]",
        "+ due_date: date | None              [NEW]",
    ],
    methods=[
        "+ get_priority_score() → int",
        "+ mark_complete() → None",
        "+ next_occurrence() → Task | None  [NEW]",
        "+ __str__() → str",
    ],
    width=W + 0.6,
)

# ── Pet ───────────────────────────────────────────────────────────────────────
pet_x, pet_y = 3.2, 9.8
_, pet_bot = draw_class(ax, pet_x, pet_y, "Pet",
    attrs=[
        "+ name: str",
        "+ species: str",
        "+ tasks: list[Task]",
    ],
    methods=[
        "+ add_task(task) → None",
        "+ pending_tasks() → list[Task]",
        "+ __str__() → str",
    ],
    width=W,
)

# ── Owner ─────────────────────────────────────────────────────────────────────
owner_x, owner_y = 0.3, 9.0
_, owner_bot = draw_class(ax, owner_x, owner_y, "Owner",
    attrs=[
        "+ name: str",
        "+ available_minutes: int",
        "+ pets: list[Pet]",
    ],
    methods=[
        "+ add_pet(pet) → None",
        "+ get_all_tasks() → list[Task]  [NEW]",
        "+ __str__() → str",
    ],
    width=W,
)

# ── ScheduledTask ─────────────────────────────────────────────────────────────
sched_task_x, sched_task_y = 13.2, 9.8
_, st_bot = draw_class(ax, sched_task_x, sched_task_y, "ScheduledTask  [NEW]",
    attrs=[
        "+ task: Task",
        "+ start_minute: int",
        "+ end_minute: int",
        "+ reasoning: str",
    ],
    methods=[
        "+ __str__() → str",
    ],
    width=W + 0.2,
)

# ── Scheduler ─────────────────────────────────────────────────────────────────
sched_x, sched_y = 7.6, 6.5
_, sched_bot = draw_class(ax, sched_x, sched_y, "Scheduler",
    attrs=[
        "+ owner: Owner",
        "+ time_budget: int",
        "+ scheduled_tasks: list[ScheduledTask]",
    ],
    methods=[
        "+ build_plan() → list[ScheduledTask]",
        "+ sort_by_time() → list[ScheduledTask]",
        "+ filter_tasks(...) → list[ScheduledTask]",
        "+ mark_task_complete(task) → Task|None  [NEW]",
        "+ detect_conflicts() → list[tuple]      [NEW]",
        "- _would_conflict(start, end) → bool    [NEW]",
        "+ explain_plan() → str",
    ],
    width=W + 0.9,
)

# ── Relationships ─────────────────────────────────────────────────────────────
# Owner --> Pet  (1 to 0..*)
arrow(ax,
      owner_x + W, owner_y - 0.9,
      pet_x,       pet_y  - 0.9,
      label="1  has  0..*")

# Pet --> Task  (1 to 0..*)
arrow(ax,
      pet_x + W, pet_y - 0.9,
      task_x,    task_y - 2.0,
      label="1  has  0..*")

# Task --> Pet  (back-ref, dashed)
arrow(ax,
      task_x + 0.3,        task_y - 4.5,
      pet_x  + W * 0.6,    pet_y  - 2.2,
      label="task.pet", style="dashed", color="#7F8C8D")

# Scheduler --> Owner
arrow(ax,
      sched_x + 0.5, sched_y,
      owner_x + W / 2, owner_bot,
      label="uses 1")

# Scheduler --> ScheduledTask  (produces)
arrow(ax,
      sched_x + W + 0.9, sched_y - 1.2,
      sched_task_x,      sched_task_y - 1.2,
      label="produces 0..*")

# ScheduledTask --> Task  (wraps)
arrow(ax,
      sched_task_x + (W + 0.2) / 2, sched_task_y,
      task_x + (W + 0.6) * 0.75,    task_bot,
      label="wraps 1")

# ── Legend ────────────────────────────────────────────────────────────────────
legend_x, legend_y = 0.3, 3.2
ax.text(legend_x, legend_y, "Legend", fontsize=9, fontweight="bold", color=BG_HDR)
ax.plot([legend_x, legend_x + 0.5], [legend_y - 0.3] * 2,
        color=BG_HDR, lw=1.2)
ax.text(legend_x + 0.6, legend_y - 0.3, "association / ownership",
        fontsize=8, color=TXT_BODY)
ax.plot([legend_x, legend_x + 0.5], [legend_y - 0.6] * 2,
        color="#7F8C8D", lw=1.2, linestyle="--")
ax.text(legend_x + 0.6, legend_y - 0.6, "back-reference (dashed)",
        fontsize=8, color=TXT_BODY)
ax.text(legend_x, legend_y - 0.9, "[NEW]  =  added during implementation",
        fontsize=8, color="#C0392B")

# Title
ax.text(FIG_W / 2, FIG_H - 0.3,
        "PawPal+ — Updated UML Class Diagram",
        ha="center", fontsize=13, fontweight="bold", color=BG_HDR)

plt.tight_layout(pad=0.5)
out = "uml_diagram.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved → {out}")
