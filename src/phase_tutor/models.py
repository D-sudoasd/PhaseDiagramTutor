from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence


Point = tuple[float, float]  # (x composition, T)


@dataclass(frozen=True)
class Curve:
    id: str
    kind: Literal["liquidus", "solidus", "solvus", "invariant", "other"]
    name_zh: str
    hover_zh: str
    points: tuple[Point, ...]


@dataclass(frozen=True)
class Invariant:
    id: str
    kind: Literal["eutectic", "peritectic", "eutectoid"]
    name_zh: str
    formula_zh: str
    temperature: float
    x_star: float
    x_left: float
    x_right: float
    x_mid: float | None
    phases: tuple[str, ...]
    hover_zh: str
    cooling_meaning_zh: str

    @property
    def x_min(self) -> float:
        xs = [self.x_left, self.x_right, self.x_star]
        if self.x_mid is not None:
            xs.append(self.x_mid)
        return min(xs)

    @property
    def x_max(self) -> float:
        xs = [self.x_left, self.x_right, self.x_star]
        if self.x_mid is not None:
            xs.append(self.x_mid)
        return max(xs)


@dataclass(frozen=True)
class PhaseField:
    id: str
    name_zh: str
    phases: tuple[str, ...]
    hover_zh: str
    color: str
    polygon: tuple[Point, ...]
    left_curve: tuple[Point, ...] | None = None
    right_curve: tuple[Point, ...] | None = None
    left_phase: str | None = None
    right_phase: str | None = None
    t_min: float | None = None
    t_max: float | None = None

    @property
    def is_two_phase(self) -> bool:
        return len(self.phases) == 2 and self.left_curve is not None and self.right_curve is not None


@dataclass(frozen=True)
class SpecialPoint:
    x: float
    T: float
    label_zh: str
    hover_zh: str


@dataclass(frozen=True)
class Diagram:
    id: str
    title_zh: str
    subtitle_zh: str
    x_label_zh: str
    y_label_zh: str
    x_min: float
    x_max: float
    t_min: float
    t_max: float
    components: tuple[str, str]
    n_components: int
    fields: tuple[PhaseField, ...]
    curves: tuple[Curve, ...]
    invariants: tuple[Invariant, ...]
    special_points: tuple[SpecialPoint, ...]
    source_note_zh: str
    practical_kind: str
    default_x: float
    default_T: float
    extra_notes_zh: str = ""
    colors: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TieLine:
    left: Point
    right: Point
    left_phase: str
    right_phase: str
    left_fraction: float
    right_fraction: float


@dataclass(frozen=True)
class Interpretation:
    diagram_id: str
    x: float
    T: float
    field_id: str
    field_name_zh: str
    phases: tuple[str, ...]
    fractions: dict[str, float]
    phase_compositions: dict[str, float]
    tie_line: TieLine | None
    C: int
    P: int
    F: int
    on_boundary: bool
    on_invariant: bool
    invariant: Invariant | None
    location_reading_zh: str
    lever_explain_zh: str
    phase_rule_zh: str
    practical_zh: str


@dataclass(frozen=True)
class IsoplethStep:
    temperature: float
    kind: Literal["field", "invariant"]
    name_zh: str
    field_id: str | None
    formula_zh: str | None
    meaning_zh: str
    phases: tuple[str, ...]


def close_ring(points: Sequence[Point]) -> tuple[Point, ...]:
    pts = list(points)
    if not pts:
        return ()
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    return tuple(pts)
