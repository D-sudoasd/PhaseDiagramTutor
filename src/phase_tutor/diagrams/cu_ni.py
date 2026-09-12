"""Cu–Ni 完全互溶（isomorphous）教学相图。"""

from __future__ import annotations

from ..geometry import polygon_between
from ..models import Curve, Diagram, PhaseField, SpecialPoint
from . import palette as C

LIQUIDUS = (
    (0.0, 1085.0),
    (10.0, 1118.0),
    (20.0, 1155.0),
    (30.0, 1195.0),
    (40.0, 1238.0),
    (50.0, 1282.0),
    (60.0, 1326.0),
    (70.0, 1368.0),
    (80.0, 1402.0),
    (90.0, 1432.0),
    (100.0, 1455.0),
)
SOLIDUS = (
    (0.0, 1085.0),
    (10.0, 1096.0),
    (20.0, 1112.0),
    (30.0, 1135.0),
    (40.0, 1166.0),
    (50.0, 1204.0),
    (60.0, 1248.0),
    (70.0, 1295.0),
    (80.0, 1346.0),
    (90.0, 1400.0),
    (100.0, 1455.0),
)

T_MAX = 1550.0
T_MIN = 700.0


def build() -> Diagram:
    two_poly = polygon_between(LIQUIDUS, SOLIDUS)
    l_poly = (
        (0.0, T_MAX),
        (100.0, T_MAX),
        (100.0, 1455.0),
        *tuple(reversed(LIQUIDUS)),
        (0.0, T_MAX),
    )
    a_poly = (
        *SOLIDUS,
        (100.0, T_MIN),
        (0.0, T_MIN),
        (0.0, 1085.0),
    )
    fields = (
        PhaseField(
            id="L",
            name_zh="液相 L",
            phases=("L",),
            hover_zh="相区：液相 L。原子已经拆成熔体，没有长程晶体结构。",
            color=C.L,
            polygon=l_poly,
        ),
        PhaseField(
            id="alpha",
            name_zh="固溶体 α",
            phases=("α",),
            hover_zh="相区：单一固溶体 α。Cu 与 Ni 可以任意比例互溶，所以整张图底部都是同一个相。",
            color=C.ALPHA,
            polygon=a_poly,
        ),
        PhaseField(
            id="L_alpha",
            name_zh="L + α",
            phases=("L", "α"),
            hover_zh="相区：液相与固溶体共存。水平结线两端分别落在液相线和固相线上，杠杆定律给出两相质量分数。",
            color=C.L_ALPHA,
            polygon=two_poly,
            left_curve=LIQUIDUS,
            right_curve=SOLIDUS,
            left_phase="L",
            right_phase="α",
            t_min=1085.0,
            t_max=1455.0,
        ),
    )
    curves = (
        Curve(
            id="liquidus",
            kind="liquidus",
            name_zh="液相线",
            hover_zh="液相线：这条线以上全部是液体。冷却时合金第一次析出晶体，就发生在液相线上。",
            points=LIQUIDUS,
        ),
        Curve(
            id="solidus",
            kind="solidus",
            name_zh="固相线",
            hover_zh="固相线：这条线以下全部是固体。冷却时最后一滴液体在固相线上消失。",
            points=SOLIDUS,
        ),
    )
    return Diagram(
        id="cu_ni",
        title_zh="Cu–Ni 完全互溶",
        subtitle_zh="最简单的二元相图：只有液相线、固相线，没有共晶/包晶",
        x_label_zh="Ni 含量 / wt%",
        y_label_zh="温度 / °C",
        x_min=0.0,
        x_max=100.0,
        t_min=T_MIN,
        t_max=T_MAX,
        components=("Cu", "Ni"),
        n_components=2,
        fields=fields,
        curves=curves,
        invariants=(),
        special_points=(
            SpecialPoint(0.0, 1085.0, "Cu 熔点 1085 °C", "纯铜熔化温度。"),
            SpecialPoint(100.0, 1455.0, "Ni 熔点 1455 °C", "纯镍熔化温度。"),
        ),
        source_note_zh="教学示意。Cu、Ni 熔点取 1085 °C 与 1455 °C；液/固相线为光滑示意，拓扑与教材完全互溶图一致，不是 CALPHAD 计算。",
        practical_kind="isomorphous",
        default_x=50.0,
        default_T=1240.0,
        extra_notes_zh="完全互溶意味着固态只有一个相。铸锭里看到的枝晶偏析，正是 L+α 两相区里结线两端成分不同造成的。",
    )
