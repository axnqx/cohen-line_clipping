"""Assignment 05: Cohen-Sutherland Line Clipping (Roll No. 208)

This program:
1. Computes four-bit region codes in TOP, BOTTOM, RIGHT, LEFT order.
2. Implements Cohen-Sutherland clipping without any ready-made clipping routine.
3. Prints a result table for L1-L6.
4. Saves and displays two figures:
   - initial_diagram.png: original dashed lines + surviving solid segments
   - clipped_diagram.png: only the surviving segments inside the window

Run with: python clipping_208.py
Requires: matplotlib
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# ------------------------------------------------------------
# 1. Roll number and clipping-window boundaries
# ------------------------------------------------------------
ROLL_NUMBER = 208

# The second-last digit is a, and the last digit is b.
a = (ROLL_NUMBER // 10) % 10
b = ROLL_NUMBER % 10

X_MIN, Y_MIN = 50, 50
X_MAX, Y_MAX = 200, 150

# Save the generated PNG files in a folder beside this Python file.
OUTPUT_DIR = Path(__file__).resolve().parent / "a05_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Region-code constants
# Bit order required by the assignment: TOP, BOTTOM, RIGHT, LEFT
# ------------------------------------------------------------
INSIDE = 0       # 0000
TOP = 8           # 1000
BOTTOM = 4        # 0100
RIGHT = 2         # 0010
LEFT = 1          # 0001


# ------------------------------------------------------------
# 3. Function to calculate the region code of a point
# ------------------------------------------------------------
def get_region_code(x, y):
    """Return the four-bit region code for point (x, y)."""
    code = INSIDE

    if y > Y_MAX:
        code |= TOP
    elif y < Y_MIN:
        code |= BOTTOM

    if x > X_MAX:
        code |= RIGHT
    elif x < X_MIN:
        code |= LEFT

    return code


def code_to_bits(code):
    """Convert a region-code integer into exactly four binary digits."""
    return format(code, "04b")


# ------------------------------------------------------------
# 4. Cohen-Sutherland line-clipping function
# ------------------------------------------------------------
def cohen_sutherland_clip(point1, point2):
    """Clip a line and return (outcome, intersection_count, clipped_points).

    The count records the number of intersection-calculation passes.
    The final inside/outside test is not counted as an intersection pass.
    """
    x1, y1 = point1
    x2, y2 = point2

    code1 = get_region_code(x1, y1)
    code2 = get_region_code(x2, y2)

    # Trivial acceptance: both endpoints are inside the window.
    if code1 == INSIDE and code2 == INSIDE:
        return "accepted", 0, ((x1, y1), (x2, y2))

    # Trivial rejection: both endpoints share an outside region.
    if (code1 & code2) != 0:
        return "rejected", 0, None

    intersection_count = 0

    # Each loop pass clips one outside endpoint. The loop stops as soon as
    # both endpoint codes become 0000, so the pass count equals the number
    # of boundary intersections calculated.
    while code1 != INSIDE or code2 != INSIDE:
        # A common outside bit means the line is completely outside.
        if (code1 & code2) != 0:
            return "rejected", intersection_count, None

        # Select one endpoint that is outside the clipping window.
        if code1 != INSIDE:
            outside_code = code1
        else:
            outside_code = code2

        dx = x2 - x1
        dy = y2 - y1

        # Calculate the intersection with one boundary.
        # The priority follows the region-code bit order.
        if outside_code & TOP:
            # Intersection with y = Y_MAX (top edge).
            x = x1 + dx * (Y_MAX - y1) / dy
            y = Y_MAX
        elif outside_code & BOTTOM:
            # Intersection with y = Y_MIN (bottom edge).
            x = x1 + dx * (Y_MIN - y1) / dy
            y = Y_MIN
        elif outside_code & RIGHT:
            # Intersection with x = X_MAX (right edge).
            y = y1 + dy * (X_MAX - x1) / dx
            x = X_MAX
        else:
            # Intersection with x = X_MIN (left edge).
            y = y1 + dy * (X_MIN - x1) / dx
            x = X_MIN

        # Replace only the endpoint that was outside.
        if outside_code == code1:
            x1, y1 = x, y
            code1 = get_region_code(x1, y1)
        else:
            x2, y2 = x, y
            code2 = get_region_code(x2, y2)

        intersection_count += 1

    # Both endpoints are now inside the clipping window.
    return "clipped", intersection_count, ((x1, y1), (x2, y2))


# ------------------------------------------------------------
# 5. Define the six input lines
# ------------------------------------------------------------
lines = {
    "L1": ((140, 70), (185, 130)),
    "L2": ((10, 165), (40, 190)),
    "L3": ((20, 125), (250, 125)),
    "L4": ((80, 20), (80, 180)),
    "L5": ((20, 20), (150, 200)),
    "L6": ((40 + a, 20), (190 - b, 180)),
}


# ------------------------------------------------------------
# 6. Run the clipping algorithm and print the result table
# ------------------------------------------------------------
def format_point(point):
    if point is None:
        return "—"
    return f"({point[0]:.3f}, {point[1]:.3f})"


results = {}

print("=" * 108)
print("COHEN-SUTHERLAND LINE CLIPPING — ROLL NUMBER:", ROLL_NUMBER)
print(f"a = {a}, b = {b}")
print(f"L6 = (40 + {a}, 20) to (190 - {b}, 180)")
print(f"Clipping window: LL=({X_MIN}, {Y_MIN}), UR=({X_MAX}, {Y_MAX})")
print("Region-code bit order: TOP, BOTTOM, RIGHT, LEFT")
print("=" * 108)

header = (
    f"{'Line':<5} {'Start point':<22} {'End point':<22} "
    f"{'Start code':<12} {'End code':<10} {'Outcome':<11} "
    f"{'Passes':<7} Clipped endpoints"
)
print(header)
print("-" * 108)

for name, (start, end) in lines.items():
    start_code = get_region_code(*start)
    end_code = get_region_code(*end)

    outcome, passes, clipped_points = cohen_sutherland_clip(start, end)
    results[name] = {
        "start": start,
        "end": end,
        "start_code": start_code,
        "end_code": end_code,
        "outcome": outcome,
        "passes": passes,
        "clipped": clipped_points,
    }

    if clipped_points is None:
        clipped_text = "Rejected"
    else:
        clipped_text = (
            f"{format_point(clipped_points[0])} to "
            f"{format_point(clipped_points[1])}"
        )

    print(
        f"{name:<5} {format_point(start):<22} {format_point(end):<22} "
        f"{code_to_bits(start_code):<12} {code_to_bits(end_code):<10} "
        f"{outcome:<11} {passes:<7} {clipped_text}"
    )

print("-" * 108)
print("Note: Passes count boundary-intersection calculations, not the final acceptance test.")


# ------------------------------------------------------------
# 7. Helper function to draw the clipping window
# ------------------------------------------------------------
def draw_window(ax):
    window = Rectangle(
        (X_MIN, Y_MIN),
        X_MAX - X_MIN,
        Y_MAX - Y_MIN,
        fill=False,
        edgecolor="black",
        linewidth=2.0,
        label="Clipping window",
        zorder=3,
    )
    ax.add_patch(window)
    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.65)
    ax.set_aspect("equal", adjustable="box")


# ------------------------------------------------------------
# 8. Figure 1: all original lines + surviving clipped portions
# ------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(10, 8))
draw_window(ax1)

line_colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
label_positions = {
    "L1": (162, 100),
    "L3": (130, 129),
    "L4": (84, 91),
    "L5": (96, 113),
    "L6": (110, 98),
}

for index, (name, (start, end)) in enumerate(lines.items()):
    line_color = line_colors[index % len(line_colors)]

    # Draw every original input line as a dashed line.
    ax1.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        color=line_color,
        linestyle="--",
        linewidth=1.5,
        alpha=0.75,
        label="Original input lines" if index == 0 else None,
        zorder=1,
    )

    # Draw only the surviving portion as a thick solid line.
    clipped = results[name]["clipped"]
    if clipped is not None:
        p1, p2 = clipped
        ax1.plot(
            [p1[0], p2[0]],
            [p1[1], p2[1]],
            color=line_color,
            linestyle="-",
            linewidth=4.0,
            label="Surviving clipped lines" if name == "L1" else None,
            zorder=2,
        )
        label_x, label_y = label_positions[name]
        ax1.text(
            label_x,
            label_y,
            name,
            fontsize=9,
            weight="bold",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.7, "pad": 1.5},
        )
    else:
        # Label the rejected input line outside the window.
        ax1.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
            f" {name} (rejected)",
            fontsize=8,
        )

ax1.set_title("Figure 1 — Initial Diagram: Input Lines and Surviving Portions")
ax1.set_xlim(0, 270)
ax1.set_ylim(0, 220)
ax1.legend(loc="upper right")
fig1.tight_layout()
fig1.savefig(OUTPUT_DIR / "initial_diagram.png", dpi=300, bbox_inches="tight")


# ------------------------------------------------------------
# 9. Figure 2: only the surviving portions inside the window
# ------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(10, 7))
draw_window(ax2)

for index, (name, result) in enumerate(results.items()):
    clipped = result["clipped"]
    if clipped is None:
        continue

    p1, p2 = clipped
    ax2.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color=line_colors[index % len(line_colors)],
        linestyle="-",
        linewidth=3.5,
        marker="o",
        markersize=4,
        label=name,
        zorder=2,
    )

ax2.set_title("Figure 2 — Clipped Diagram: Surviving Segments Only")
ax2.set_xlim(35, 215)
ax2.set_ylim(35, 165)
ax2.legend(title="Surviving lines", loc="best")
fig2.tight_layout()
fig2.savefig(OUTPUT_DIR / "clipped_diagram.png", dpi=300, bbox_inches="tight")

print("\nFigures saved successfully:")
print(OUTPUT_DIR / "initial_diagram.png")
print(OUTPUT_DIR / "clipped_diagram.png")

# Display both figures. Keep this at the end of the program.
plt.show(block=True)
