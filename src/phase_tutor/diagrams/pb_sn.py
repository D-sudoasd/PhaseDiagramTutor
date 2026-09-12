"""Pb–Sn 简单共晶教学相图。"""

from __future__ import annotations

from ..geometry import polygon_between
from ..models import Curve, Diagram, Invariant, PhaseField, SpecialPoint
from . import palette as C

T_MAX = 360.0
T_MIN = 20.0

LIQUIDUS_L = (
    (0.0, 327.5),
    (10.0, 305.0),
    (20.0, 280.0),
    (30.0, 255.0),
    (40.0, 232.0),
    (50.0, 205.0),
    (61.9, 183.0),
)
LIQUIDUS_R = (
    (61.9, 183.0),
    (70.0, 192.0),
    (80.0, 205.0),
    (90.0, 218.0),
    (100.0, 231.9),
)
SOLIDUS_A = (
    (0.0, 327.5),
    (8.0, 270.0),
    (14.0, 220.0),
    (19.2, 183.0),
)
SOLIDUS_B = (
    (97.5, 183.0),
    (98.5, 205.0),
    (99.4, 220.0),
    (100.0, 231.9),
)
SOLVUS_A = (
    (19.2, 183.0),
    (10.0, 100.0),
    (1.8, 20.0),
)
SOLVUS_B = (
    (97.5, 183.0),
    (98.5, 100.0),
    (99.2, 20.0),
)
EUT_H = (
    (19.2, 183.0),
    (61.9, 183.0),
    (97.5, 183.0),
)


def build() -> Diagram:
    l_poly = (
        (0.0, T_MAX),
        (100.0, T_MAX),
        (100.0, 231.9),
        *tuple(reversed(LIQUIDUS_R)),
        *tuple(reversed(LIQUIDUS_L[:-1])),
        (0.0, T_MAX),
    )
    a_poly = (
        (0.0, 327.5),
        *SOLIDUS_A,
        *SOLVUS_A[1:],
        (0.0, T_MIN),
        (0.0, 327.5),
    )
    b_poly = (
        *SOLIDUS_B,
        (100.0, T_MIN),
        *tuple(reversed(SOLVUS_B)),
    )
    fields = (
        PhaseField(
            id="L",
            name_zh="液相 L",
            phases=("L",),
            hover_zh="相区：液相。焊料熔化后就在这里。",
            color=C.L,
            polygon=l_poly,
        ),
        PhaseField(
            id="alpha",
            name_zh="α（Pb 基固溶体）",
            phases=("α",),
            hover_zh="相区：铅基固溶体 α。锡溶进铅的晶格，但溶解度有限。",
            color=C.ALPHA,
            polygon=a_poly,
        ),
        PhaseField(
            id="beta",
            name_zh="β（Sn 基固溶体）",
            phases=("β",),
            hover_zh="相区：锡基固溶体 β。铅溶进锡的晶格，溶解度更小。",
            color=C.BETA,
            polygon=b_poly,
        ),
        PhaseField(
            id="L_alpha",
            name_zh="L + α",
            phases=("L", "α"),
            hover_zh="相区：液相 + α。亚共晶合金先析出铅基晶体，液体沿液相线变富锡。",
            color=C.L_ALPHA,
            polygon=polygon_between(SOLIDUS_A, LIQUIDUS_L),
            left_curve=SOLIDUS_A,
            right_curve=LIQUIDUS_L,
            left_phase="α",
            right_phase="L",
            t_min=183.0,
            t_max=327.5,
        ),
        PhaseField(
            id="L_beta",
            name_zh="L + β",
            phases=("L", "β"),
            hover_zh="相区：液相 + β。过共晶合金先析出锡基晶体，液体沿液相线变富铅。",
            color=C.L_BETA,
            polygon=polygon_between(LIQUIDUS_R, SOLIDUS_B),
            left_curve=LIQUIDUS_R,
            right_curve=SOLIDUS_B,
            left_phase="L",
            right_phase="β",
            t_min=183.0,
            t_max=231.9,
        ),
        PhaseField(
            id="alpha_beta",
            name_zh="α + β",
            phases=("α", "β"),
            hover_zh="相区：α + β 两固相。共晶凝固结束后，室温焊料就停在这个双相区。",
            color=C.ALPHA_BETA,
            polygon=polygon_between(SOLVUS_A, SOLVUS_B),
            left_curve=SOLVUS_A,
            right_curve=SOLVUS_B,
            left_phase="α",
            right_phase="β",
            t_min=T_MIN,
            t_max=183.0,
        ),
    )
    curves = (
        Curve("liquidus_l", "liquidus", "液相线（左）", "液相线：亚共晶一侧，冷却时 α 开始结晶。", LIQUIDUS_L),
        Curve("liquidus_r", "liquidus", "液相线（右）", "液相线：过共晶一侧，冷却时 β 开始结晶。", LIQUIDUS_R),
        Curve("solidus_a", "solidus", "固相线（α）", "固相线：α 单相区的右边界。液固共存时 α 的成分走这条线。", SOLIDUS_A),
        Curve("solidus_b", "solidus", "固相线（β）", "固相线：β 单相区的左边界。液固共存时 β 的成分走这条线。", SOLIDUS_B),
        Curve("solvus_a", "solvus", "溶解度曲线（α）", "溶解度曲线：温度降低，锡在铅中的溶解度下降，多余的锡以 β 析出。", SOLVUS_A),
        Curve("solvus_b", "solvus", "溶解度曲线（β）", "溶解度曲线：温度降低，铅在锡中的溶解度下降。", SOLVUS_B),
        Curve("eutectic_h", "invariant", "共晶水平线", "共晶反应 L → α+β 在 183 °C 进行。三相成分被这条水平线钉死。", EUT_H),
    )
    inv = Invariant(
        id="eutectic",
        kind="eutectic",
        name_zh="共晶",
        formula_zh="L → α + β",
        temperature=183.0,
        x_star=61.9,
        x_left=19.2,
        x_right=97.5,
        x_mid=None,
        phases=("L", "α", "β"),
        hover_zh="共晶点：61.9 wt% Sn，183 °C。液体在此温度一次性变成 α+β 细密两相混合物。",
        cooling_meaning_zh="冷却穿过共晶水平线时，剩余液体在恒温下全部变成 α+β（共晶组织）。温度在反应结束前不会继续下降。",
    )
    return Diagram(
        id="pb_sn",
        title_zh="Pb–Sn 简单共晶",
        subtitle_zh="焊料相图：先学「共晶水平线 = 液体一次性变成两固相」",
        x_label_zh="Sn 含量 / wt%",
        y_label_zh="温度 / °C",
        x_min=0.0,
        x_max=100.0,
        t_min=T_MIN,
        t_max=T_MAX,
        components=("Pb", "Sn"),
        n_components=2,
        fields=fields,
        curves=curves,
        invariants=(inv,),
        special_points=(
            SpecialPoint(0.0, 327.5, "Pb 327.5 °C", "纯铅熔点。"),
            SpecialPoint(100.0, 231.9, "Sn 231.9 °C", "纯锡熔点。"),
            SpecialPoint(61.9, 183.0, "共晶 61.9 wt% / 183 °C", "共晶成分与温度。"),
            SpecialPoint(19.2, 183.0, "α 端 19.2 wt%", "共晶温度下 α 的饱和成分。"),
            SpecialPoint(97.5, 183.0, "β 端 97.5 wt%", "共晶温度下 β 的饱和成分。"),
        ),
        source_note_zh="教学示意。共晶取 61.9 wt% Sn、183 °C；α/β 端点取 19.2 / 97.5 wt% Sn。曲线为教材拓扑，不是 CALPHAD。",
        practical_kind="eutectic",
        default_x=40.0,
        default_T=220.0,
        extra_notes_zh="共晶成分冷却几乎没有凝固温度区间，所以 Sn–Pb 焊料铺展好、熔点低。亚共晶先出 α，过共晶先出 β。",
    )
