"""简单包晶示意，用来单独看清 L+α → β。"""

from __future__ import annotations

from ..geometry import polygon_between
from ..models import Curve, Diagram, Invariant, PhaseField, SpecialPoint
from . import palette as C

T_MAX = 1550.0
T_MIN = 400.0

# Generic A–B peritectic schematic (not a commercial alloy).
# A melts 1480 °C, B melts 720 °C.
# Peritectic 1120 °C: α 18% + L 48% → β 28%.
LIQUIDUS_L = (
    (0.0, 1480.0),
    (10.0, 1390.0),
    (18.0, 1280.0),
    (28.0, 1200.0),
    (48.0, 1120.0),
)
LIQUIDUS_R = (
    (48.0, 1120.0),
    (60.0, 1020.0),
    (75.0, 900.0),
    (90.0, 790.0),
    (100.0, 720.0),
)
SOLIDUS_A = (
    (0.0, 1480.0),
    (8.0, 1320.0),
    (14.0, 1200.0),
    (18.0, 1120.0),
)
SOLIDUS_B = (
    (28.0, 1120.0),
    (40.0, 980.0),
    (55.0, 860.0),
    (70.0, 780.0),
    (100.0, 720.0),
)
SOLVUS_A = (
    (18.0, 1120.0),
    (14.0, 800.0),
    (11.0, 400.0),
)
SOLVUS_B = (
    (28.0, 1120.0),
    (24.0, 800.0),
    (21.0, 400.0),
)
PERI_H = (
    (18.0, 1120.0),
    (28.0, 1120.0),
    (48.0, 1120.0),
)


def build() -> Diagram:
    l_poly = (
        (0.0, T_MAX),
        (100.0, T_MAX),
        (100.0, 720.0),
        *tuple(reversed(LIQUIDUS_R)),
        *tuple(reversed(LIQUIDUS_L[:-1])),
        (0.0, T_MAX),
    )
    a_poly = (
        (0.0, 1480.0),
        *SOLIDUS_A,
        *SOLVUS_A[1:],
        (0.0, T_MIN),
        (0.0, 1480.0),
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
            hover_zh="相区：液相。",
            color=C.L,
            polygon=l_poly,
        ),
        PhaseField(
            id="alpha",
            name_zh="α",
            phases=("α",),
            hover_zh="相区：先析出的固溶体 α。包晶反应时它被液体消耗，在表面生成 β。",
            color=C.ALPHA,
            polygon=a_poly,
        ),
        PhaseField(
            id="beta",
            name_zh="β",
            phases=("β",),
            hover_zh="相区：包晶产物 β。理想平衡下 L 与 α 按比例合成 β。",
            color=C.BETA,
            polygon=b_poly,
        ),
        PhaseField(
            id="L_alpha",
            name_zh="L + α",
            phases=("L", "α"),
            hover_zh="相区：液相 + α。包晶反应发生前，先析出的就是这个 α。",
            color=C.L_ALPHA,
            polygon=polygon_between(SOLIDUS_A, LIQUIDUS_L),
            left_curve=SOLIDUS_A,
            right_curve=LIQUIDUS_L,
            left_phase="α",
            right_phase="L",
            t_min=1120.0,
            t_max=1480.0,
        ),
        PhaseField(
            id="L_beta",
            name_zh="L + β",
            phases=("L", "β"),
            hover_zh="相区：液相 + β。包晶点右侧，冷却时直接从液体长出 β。",
            color=C.L_BETA,
            polygon=polygon_between(LIQUIDUS_R, SOLIDUS_B),
            left_curve=LIQUIDUS_R,
            right_curve=SOLIDUS_B,
            left_phase="L",
            right_phase="β",
            t_min=720.0,
            t_max=1120.0,
        ),
        PhaseField(
            id="alpha_beta",
            name_zh="α + β",
            phases=("α", "β"),
            hover_zh="相区：α + β。包晶点左侧冷却到水平线以下，剩余 α 与新生成的 β 共存。",
            color=C.ALPHA_BETA,
            polygon=polygon_between(SOLVUS_A, SOLVUS_B),
            left_curve=SOLVUS_A,
            right_curve=SOLVUS_B,
            left_phase="α",
            right_phase="β",
            t_min=T_MIN,
            t_max=1120.0,
        ),
    )
    curves = (
        Curve("liquidus_l", "liquidus", "液相线（左）", "液相线：α 开始从液体中结晶。", LIQUIDUS_L),
        Curve("liquidus_r", "liquidus", "液相线（右）", "液相线：β 开始从液体中结晶。", LIQUIDUS_R),
        Curve("solidus_a", "solidus", "固相线（α）", "固相线：α 的液固平衡成分。", SOLIDUS_A),
        Curve("solidus_b", "solidus", "固相线（β）", "固相线：β 的液固平衡成分。", SOLIDUS_B),
        Curve("solvus_a", "solvus", "溶解度曲线（α）", "溶解度曲线：α 对 B 组元的固溶极限。", SOLVUS_A),
        Curve("solvus_b", "solvus", "溶解度曲线（β）", "溶解度曲线：β 对 A 组元的固溶极限。", SOLVUS_B),
        Curve("peri_h", "invariant", "包晶水平线", "包晶反应 L+α → β 在恒温下进行。", PERI_H),
    )
    inv = Invariant(
        id="peritectic",
        kind="peritectic",
        name_zh="包晶",
        formula_zh="L + α → β",
        temperature=1120.0,
        x_star=28.0,
        x_left=18.0,
        x_right=48.0,
        x_mid=28.0,
        phases=("L", "α", "β"),
        hover_zh="包晶点：β 成分 28 wt% B，1120 °C。液体与已有的 α 反应，在 α 表面生成 β。",
        cooling_meaning_zh="冷却碰到包晶水平线时，L 与 α 恒温反应生成 β。反应靠固相扩散，实际合金里常残留未反应完的 α，外包一层 β。",
    )
    return Diagram(
        id="peritectic",
        title_zh="简单包晶（示意）",
        subtitle_zh="专门看清 L+α → β：产物长在已有固体表面，所以叫「包」晶",
        x_label_zh="B 含量 / wt%",
        y_label_zh="温度 / °C",
        x_min=0.0,
        x_max=100.0,
        t_min=T_MIN,
        t_max=T_MAX,
        components=("A", "B"),
        n_components=2,
        fields=fields,
        curves=curves,
        invariants=(inv,),
        special_points=(
            SpecialPoint(0.0, 1480.0, "A 熔点", "高熔点组元。"),
            SpecialPoint(100.0, 720.0, "B 熔点", "低熔点组元。"),
            SpecialPoint(18.0, 1120.0, "α 端 18%", "包晶温度下 α 的成分。"),
            SpecialPoint(28.0, 1120.0, "β 28%", "包晶产物成分。"),
            SpecialPoint(48.0, 1120.0, "L 端 48%", "包晶温度下液体成分。"),
        ),
        source_note_zh="抽象教学示意，不是某一张商业相图。用来把钢铁相图里那一小段包晶单独放大看清。",
        practical_kind="peritectic",
        default_x=28.0,
        default_T=1180.0,
        extra_notes_zh="钢在约 0.1–0.5 wt% C 冷却时也会穿过包晶。包晶反应慢，铸坯容易留下包晶偏析。",
    )
