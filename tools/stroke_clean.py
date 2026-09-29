"""Clean Make Me a Hanzi medians into a print-like reference drawing.

The medians are centerlines of a brush (Kai) font: a small entry tick at the
start of a stroke, slight waves, horizontals rising a few degrees. As a
reference to trace and to write from, that looks hand-scratched. Cleaning:

1. Ramer-Douglas-Peucker: keep only the real turns of a stroke.
2. Drop the brush entry tick (a short first segment that turns sharply) and
   the press at the end (an even shorter last segment that turns).
3. Snap segments within SNAP_H_DEG of horizontal / SNAP_V_DEG of vertical.
4. The brush foot of 捺 (a falling-right stroke ending in a short horizontal
   flick, 人, 是) merges into one straight diagonal, as in a print font.

The target is a print (Hei) skeleton, not a tidy brush: the customer asked
for lines "like print" (2026-09-29).

Real hooks (the end of 亅 in 小, 你, 水) stay: they are longer than a tick.
Coordinates are in the app cell 0..100 (y down).
"""
import math

RDP_EPS = 4.0      # cell units: only the real turns of a stroke survive
TICK_LEN = 7.0     # a first segment shorter than this ...
TICK_TURN = 50.0   # ... that turns by more than this (degrees) is a tick
END_TICK_LEN = 5.0  # the brush press at the END of a stroke is shorter still;
                    # a real hook (亅, 乚) is longer and stays
MIN_TRIM_LEN = 20.0  # ticks are trimmed only on strokes longer than this: on a
                     # short stroke (the inner lines of 日, 月) the "tick" is a
                     # real part of it, and trimming made them dots
SNAP_H_DEG = 12.0  # brush horizontals rise ~10°: this close to horizontal -> flat
SNAP_V_DEG = 6.0   # brush verticals are nearly exact; a steeper tolerance turned
                   # the steep 撇 of narrow radicals (女 in 妈) into verticals


def _dist_to_segment(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def rdp(points, eps):
    if len(points) < 3:
        return list(points)
    worst, index = 0.0, 0
    for i in range(1, len(points) - 1):
        d = _dist_to_segment(points[i], points[0], points[-1])
        if d > worst:
            worst, index = d, i
    if worst <= eps:
        return [points[0], points[-1]]
    left = rdp(points[:index + 1], eps)
    right = rdp(points[index:], eps)
    return left[:-1] + right


def _length(points):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1])
               for a, b in zip(points, points[1:]))


def _turn(a, b, c):
    """Angle between segments a->b and b->c, degrees (0 = straight on)."""
    v1 = (b[0] - a[0], b[1] - a[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def clean(points):
    """[(x, y), ...] in the 0..100 cell -> cleaned [(x, y), ...]."""
    pts = rdp(points, RDP_EPS)
    long_enough = _length(pts) > MIN_TRIM_LEN
    if long_enough and len(pts) >= 3:
        a, b, c = pts[0], pts[1], pts[2]
        if math.hypot(b[0] - a[0], b[1] - a[1]) < TICK_LEN and _turn(a, b, c) > TICK_TURN:
            pts = pts[1:]
    if long_enough and len(pts) >= 3:
        a, b, c = pts[-3], pts[-2], pts[-1]
        if math.hypot(c[0] - b[0], c[1] - b[1]) < END_TICK_LEN and _turn(a, b, c) > TICK_TURN:
            pts = pts[:-1]
    snap_h = math.tan(math.radians(SNAP_H_DEG))
    snap_v = math.tan(math.radians(SNAP_V_DEG))
    out = [pts[0]]
    for x, y in pts[1:]:
        px, py = out[-1]
        dx, dy = x - px, y - py
        if dx != 0 and abs(dy) <= abs(dx) * snap_h:
            y = py
        elif dy != 0 and abs(dx) <= abs(dy) * snap_v:
            x = px
        out.append((x, y))
    out = _merge_foot(out)
    return [(round(x, 1), round(y, 1)) for x, y in out]


def _merge_foot(pts):
    """捺 with a brush foot: ... -> down-right diagonal -> short horizontal."""
    if len(pts) < 3:
        return pts
    a, b, c = pts[-3], pts[-2], pts[-1]
    diag = (b[0] - a[0], b[1] - a[1])
    foot = (c[0] - b[0], c[1] - b[1])
    if diag[0] <= 0 or foot[0] <= 0:
        return pts
    diag_deg = math.degrees(math.atan2(diag[1], diag[0]))  # y down: below horizontal
    foot_deg = math.degrees(math.atan2(foot[1], foot[0]))
    falling_right = 20 <= diag_deg <= 70
    # The foot is a flatter flick: at most 25° down and 15° flatter than the
    # diagonal itself.
    flat_right = -15 <= foot_deg <= 25 and diag_deg - foot_deg >= 15
    if falling_right and flat_right and math.hypot(*foot) < math.hypot(*diag):
        return pts[:-2] + [c]
    return pts
