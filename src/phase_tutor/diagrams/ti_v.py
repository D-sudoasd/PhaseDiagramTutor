"""Ti–V β 全溶型教学相图（钛合金）。

用来讲 β transus 与 α+β 窗口。不是 Ti-6Al-4V 伪二元截面，也不是 CALPHAD。
纯钛：熔点 1670 °C，β→α 882 °C。V 是 β 稳定元素，把 transus 压低。
"""

from __future__ import annotations

from ..geometry import polygon_between
from ..models import Curve, Diagram, PhaseField, SpecialPoint
from . import palette as C

T_MAX = 1850.0
T_MIN = 25.0
X_MAX = 40.0

LIQUIDUS = (
    (0.0, 1670.0),
    (10.0, 1695.0),
    (20.0, 1725.0),
    (30.0, 1760.0),
    (40.0, 1795.0),
)
SOLIDUS = (
    (0.0, 1670.0),
    (10.0, 1678.0),
    (20.0, 1695.0),
    (30.0, 1720.0),
    (40.0, 1750.0),
)
# 图的右边界 x=40 截断了 β 全溶透镜：高于 1750 °C 时固相端点贴在右轴上。
SOLIDUS_BOUND = SOLIDUS + ((40.0, 1795.0),)
# β transus = α+β / β 边界（右侧）
TRANSUS = (
    (0.0, 882.0),
    (4.0, 780.0),
    (8.0, 660.0),
    (12.0, 520.0),
    (16.0, 360.0),
    (20.0, 180.0),
    (22.5, 25.0),
)
# α solvus = α / α+β 边界（左侧）
ALPHA_SOLVUS = (
    (0.0, 882.0),
    (1.2, 700.0),
    (2.2, 500.0),
    (2.8, 250.0),
    (3.0, 25.0),
)


def build() -> Diagram:
    l_poly = (
        (0.0, T_MAX),
        (X_MAX, T_MAX),
        (X_MAX, 1795.0),
        *tuple(reversed(LIQUIDUS)),
        (0.0, T_MAX),
    )
    beta_poly = (
        *SOLIDUS,
        (X_MAX, T_MIN),
        *tuple(reversed(TRANSUS)),
        (0.0, 1670.0),
    )
    alpha_poly = (
        (0.0, 882.0),
        *ALPHA_SOLVUS,
        (0.0, T_MIN),
        (0.0, 882.0),
    )
    fields = (
        PhaseField(
            id="L",
            name_zh="液相 L",
            phases=("L",),
            hover_zh="相区：钛液。",
            color=C.L,
            polygon=l_poly,
        ),
        PhaseField(
            id="beta",
            name_zh="β（BCC）",
            phases=("β",),
            hover_zh="相区：高温 BCC β。V 是 β 稳定元素，含量越高，β 能稳定到越低的温度。",
            color=C.GAMMA,
            polygon=beta_poly,
        ),
        PhaseField(
            id="alpha",
            name_zh="α（HCP）",
            phases=("α",),
            hover_zh="相区：低温 HCP α。纯钛室温就是 α；溶进少量 V 后仍可保持单相 α。",
            color=C.ALPHA,
            polygon=alpha_poly,
        ),
        PhaseField(
            id="L_beta",
            name_zh="L + β",
            phases=("L", "β"),
            hover_zh="相区：钛液 + β。凝固方式与 Cu–Ni 完全互溶相同：结线连液相线与固相线。",
            color=C.L_GAMMA,
            polygon=polygon_between(LIQUIDUS, SOLIDUS_BOUND),
            left_curve=LIQUIDUS,
            right_curve=SOLIDUS_BOUND,
            left_phase="L",
            right_phase="β",
            t_min=1670.0,
            t_max=1795.0,
        ),
        PhaseField(
            id="alpha_beta",
            name_zh="α + β",
            phases=("α", "β"),
            hover_zh="相区：α+β 窗口。双相钛合金的锻造、固溶、时效，都把温度放在 β transus 以下、这片双相区里。",
            color=C.ALPHA_GAMMA,
            polygon=polygon_between(ALPHA_SOLVUS, TRANSUS),
            left_curve=ALPHA_SOLVUS,
            right_curve=TRANSUS,
            left_phase="α",
            right_phase="β",
            t_min=T_MIN,
            t_max=882.0,
        ),
    )
    curves = (
        Curve("liquidus", "liquidus", "液相线", "液相线：以上全是液体。", LIQUIDUS),
        Curve("solidus", "solidus", "固相线", "固相线：以下全是固体 β（在尚未碰到 transus 之前）。", SOLIDUS),
        Curve(
            "transus",
            "solvus",
            "β transus / 溶解度曲线",
            "β transus：加热时 α 消失、全部变成 β 的温度。钛合金热处理的第一参照线。",
            TRANSUS,
        ),
        Curve(
            "alpha_solvus",
            "solvus",
            "溶解度曲线（α）",
            "溶解度曲线：α 中 V 的固溶极限。越过它就进入 α+β。",
            ALPHA_SOLVUS,
        ),
    )
    return Diagram(
        id="ti_v",
        title_zh="Ti–V 钛合金（β 稳定示意）",
        subtitle_zh="读 β transus 和 α+β 窗口：双相钛合金热处理就站在这张图上",
        x_label_zh="V 含量 / wt%",
        y_label_zh="温度 / °C",
        x_min=0.0,
        x_max=X_MAX,
        t_min=T_MIN,
        t_max=T_MAX,
        components=("Ti", "V"),
        n_components=2,
        fields=fields,
        curves=curves,
        invariants=(),
        special_points=(
            SpecialPoint(0.0, 1670.0, "Ti 熔点 1670 °C", "纯钛熔化。"),
            SpecialPoint(0.0, 882.0, "β transus 882 °C", "纯钛 α ⇄ β。加 V 之后这条温度被压下来。"),
            SpecialPoint(22.5, 25.0, "β 稳定到室温", "V 足够高时，β transus 落到室温以下，成为 β 钛合金。"),
        ),
        source_note_zh="β 全溶型教学示意。纯钛 1670 °C / 882 °C 取教材常用值。曲线拓扑用于讲解 transus 与 α+β 窗口，不是 Ti–V 精确相图，更不是 Ti-6Al-4V。",
        practical_kind="titanium",
        default_x=8.0,
        default_T=600.0,
        extra_notes_zh="α 钛合金靠在左下；α+β 钛合金把热加工放在 transus 以下；β 钛合金把 transus 压到室温附近。",
    )
