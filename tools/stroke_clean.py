"""Clean Make Me a Hanzi medians into a reference drawing.

The medians are centerlines of a brush (Kai) font: a small entry tick at the
start of a stroke, slight waves, horizontals rising a few degrees. As a
reference to trace and to write from, that looks hand-scratched. Cleaning:

1. Ramer-Douglas-Peucker: keep only the real turns of a stroke.
2. Drop the brush entry tick (a short first segment that turns sharply) and
   the press at the end (an even shorter last segment that turns).
3. Snap segments within SNAP_DEG of horizontal / vertical to exactly that.

Real hooks (the end of 亅 in 小, 你, 水) stay: they are longer than a tick.
Coordinates are in the app cell 0..100 (y down).
"""
import math

RDP_EPS = 1.0      # cell units: waves smaller than this go (2.0 merged the
                   # parallel inner lines of 日, 月 too much: matching got worse)
TICK_LEN = 7.0     # a first segment shorter than this ...
TICK_TURN = 50.0   # ... that turns by more than this (degrees) is a tick
END_TICK_LEN = 5.0  # the brush press at the END of a stroke is shorter still;
                    # a real hook (亅, 乚) is longer and stays
MIN_TRIM_LEN = 20.0  # ticks are trimmed only on strokes longer than this: on a
                     # short stroke (the inner lines of 日, 月) the "tick" is a
                     # real part of it, and trimming made them dots
SNAP_DEG = 8.0     # segments this close to horizontal / vertical are snapped


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
    snap = math.tan(math.radians(SNAP_DEG))
    out = [pts[0]]
    for x, y in pts[1:]:
        px, py = out[-1]
        dx, dy = x - px, y - py
        if dx != 0 and abs(dy) <= abs(dx) * snap:
            y = py
        elif dy != 0 and abs(dx) <= abs(dy) * snap:
            x = px
        out.append((x, y))
    return [(round(x, 1), round(y, 1)) for x, y in out]
