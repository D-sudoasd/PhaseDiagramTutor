from __future__ import annotations

from typing import Sequence

from .models import Point


def x_at_T(points: Sequence[Point], T: float, *, extrapolate: bool = False) -> float | None:
    """Interpolate composition x at temperature T along a polyline of (x, T)."""
    if not points:
        return None
    if len(points) == 1:
        return points[0][0] if abs(points[0][1] - T) < 1e-9 else (points[0][0] if extrapolate else None)

    pts = sorted(points, key=lambda p: (p[1], p[0]))
    tmin, tmax = pts[0][1], pts[-1][1]
    if not extrapolate and (T < tmin - 1e-9 or T > tmax + 1e-9):
        return None
    if T <= tmin:
        return pts[0][0]
    if T >= tmax:
        return pts[-1][0]
    for i in range(len(pts) - 1):
        x0, t0 = pts[i]
        x1, t1 = pts[i + 1]
        if t0 == t1:
            if abs(T - t0) < 1e-9:
                return 0.5 * (x0 + x1)
            continue
        lo, hi = (t0, t1) if t0 < t1 else (t1, t0)
        if lo - 1e-12 <= T <= hi + 1e-12:
            w = (T - t0) / (t1 - t0)
            return x0 + w * (x1 - x0)
    return pts[-1][0]


def T_at_x(points: Sequence[Point], x: float, *, extrapolate: bool = False) -> float | None:
    """Interpolate temperature T at composition x along a polyline of (x, T)."""
    if not points:
        return None
    if len(points) == 1:
        return points[0][1] if abs(points[0][0] - x) < 1e-9 else (points[0][1] if extrapolate else None)

    pts = sorted(points, key=lambda p: (p[0], p[1]))
    xmin, xmax = pts[0][0], pts[-1][0]
    if not extrapolate and (x < xmin - 1e-9 or x > xmax + 1e-9):
        return None
    if x <= xmin:
        return pts[0][1]
    if x >= xmax:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        x0, t0 = pts[i]
        x1, t1 = pts[i + 1]
        if x0 == x1:
            if abs(x - x0) < 1e-9:
                return 0.5 * (t0 + t1)
            continue
        lo, hi = (x0, x1) if x0 < x1 else (x1, x0)
        if lo - 1e-12 <= x <= hi + 1e-12:
            w = (x - x0) / (x1 - x0)
            return t0 + w * (t1 - t0)
    return pts[-1][1]


def resample_by_T(points: Sequence[Point], n: int = 48) -> tuple[Point, ...]:
    if len(points) < 2:
        return tuple(points)
    ts = [p[1] for p in points]
    tmin, tmax = min(ts), max(ts)
    if abs(tmax - tmin) < 1e-12:
        return tuple(points)
    out: list[Point] = []
    for i in range(n):
        T = tmin + (tmax - tmin) * i / (n - 1)
        x = x_at_T(points, T)
        if x is not None:
            out.append((x, T))
    return tuple(out) if out else tuple(points)


def polygon_between(left: Sequence[Point], right: Sequence[Point], n: int = 48) -> tuple[Point, ...]:
    """Closed-enough ring: left curve high→low T, then right curve low→high T."""
    left_s = resample_by_T(left, n)
    right_s = resample_by_T(right, n)
    left_down = tuple(sorted(left_s, key=lambda p: -p[1]))
    right_up = tuple(sorted(right_s, key=lambda p: p[1]))
    return left_down + right_up


def point_on_segment(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
    eps: float = 1e-8,
) -> bool:
    length2 = (bx - ax) ** 2 + (by - ay) ** 2
    if length2 < eps * eps:
        return False
    cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
    scale = max(1.0, abs(bx - ax), abs(by - ay), abs(px), abs(py))
    if abs(cross) > eps * scale:
        return False
    dot = (px - ax) * (bx - ax) + (py - ay) * (by - ay)
    if dot < -eps * scale:
        return False
    if dot - length2 > eps * scale:
        return False
    return True


def point_in_polygon(
    px: float,
    py: float,
    polygon: Sequence[Point],
    *,
    include_edge: bool = True,
) -> bool:
    if len(polygon) < 3:
        return False
    pts = list(polygon)
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    cleaned: list[Point] = []
    for p in pts:
        if not cleaned or p != cleaned[-1]:
            cleaned.append(p)
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and len(cleaned) > 2:
        pts = cleaned
    else:
        pts = cleaned if cleaned else pts
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if point_on_segment(px, py, x1, y1, x2, y2):
            return include_edge
    inside = False
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if (y1 > py) != (y2 > py):
            denom = (y2 - y1) if y2 != y1 else 1e-30
            xinters = (x2 - x1) * (py - y1) / denom + x1
            if px < xinters:
                inside = not inside
    return inside


def polygon_label_point(polygon: Sequence[Point]) -> Point:
    """A point inside the polygon for a short name, near the vertex-average."""
    pts = list(polygon)
    if pts and pts[0] == pts[-1]:
        pts = pts[:-1]
    cleaned: list[Point] = []
    for p in pts:
        if not cleaned or p != cleaned[-1]:
            cleaned.append(p)
    if len(cleaned) < 3:
        return cleaned[0] if cleaned else (0.0, 0.0)
    cx = sum(p[0] for p in cleaned) / len(cleaned)
    cy = sum(p[1] for p in cleaned) / len(cleaned)
    if point_in_polygon(cx, cy, cleaned, include_edge=True):
        return (cx, cy)
    xs = [p[0] for p in cleaned]
    ys = [p[1] for p in cleaned]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    best = cleaned[0]
    best_d = 1e18
    for i in range(9):
        for j in range(9):
            x = xmin + (xmax - xmin) * (i + 0.5) / 9
            y = ymin + (ymax - ymin) * (j + 0.5) / 9
            if not point_in_polygon(x, y, cleaned, include_edge=False):
                continue
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d < best_d:
                best, best_d = (x, y), d
    return best
