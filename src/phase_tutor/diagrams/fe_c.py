"""亚稳 Fe–Fe₃C 教学相图（钢铁）。

采用一套自洽的教材常用数，避免把不同手册的 0.76–0.80 wt%、723–727 °C 混用：

- 纯铁熔点 1538 °C；A4 1394 °C；A3（纯铁）912 °C
- 包晶 1495 °C：δ 0.09 / γ 0.17 / L 0.53 wt% C
- 共晶 1148 °C：γ 2.11 / L 4.30 / Fe₃C 6.67 wt% C
- 共析 727 °C：α 0.022 / γ 0.76 / Fe₃C 6.67 wt% C
- 渗碳体计量成分 6.67 wt% C；亚稳熔化示意点 D ≈ 1227 °C
"""

from __future__ import annotations

from ..geometry import polygon_between
from ..models import Curve, Diagram, Invariant, PhaseField, SpecialPoint
from . import palette as C

T_MAX = 1600.0
T_MIN = 400.0
X_MAX = 6.67

# Named textbook points
FE_MELT = (0.0, 1538.0)
N = (0.0, 1394.0)  # A4
G = (0.0, 912.0)  # A3
H = (0.09, 1495.0)
J = (0.17, 1495.0)
B = (0.53, 1495.0)
E = (2.11, 1148.0)
Cpt = (4.30, 1148.0)  # eutectic liquid "C"
D = (6.67, 1227.0)
F = (6.67, 1148.0)
P = (0.022, 727.0)
S = (0.76, 727.0)
K = (6.67, 727.0)
Q = (0.008, T_MIN)
CEM_TOP = (6.67, T_MAX)
CEM_BOT = (6.67, T_MIN)

LIQUIDUS_DELTA = (
    FE_MELT,
    (0.25, 1515.0),
    B,
)
LIQUIDUS_GAMMA = (
    B,
    (1.00, 1420.0),
    (1.80, 1330.0),
    (2.60, 1255.0),
    (3.40, 1195.0),
    Cpt,
)
LIQUIDUS_CEM = (
    Cpt,
    (5.50, 1185.0),
    D,
)
SOLIDUS_DELTA = (
    FE_MELT,
    H,
)
SOLIDUS_GAMMA = (
    J,
    (0.40, 1450.0),
    (0.80, 1380.0),
    (1.20, 1300.0),
    (1.60, 1225.0),
    E,
)
A4_DELTA = (N, H)  # δ / (δ+γ)
A4_GAMMA = (N, J)  # γ / (δ+γ)
A3 = (  # GS, γ / (α+γ)
    G,
    (0.10, 890.0),
    (0.20, 860.0),
    (0.35, 820.0),
    (0.50, 780.0),
    (0.65, 748.0),
    S,
)
ACM = (  # ES, γ / (γ+Fe3C)
    E,
    (1.80, 1050.0),
    (1.40, 940.0),
    (1.10, 850.0),
    (0.90, 780.0),
    S,
)
GP = (  # α / (α+γ)
    G,
    P,
)
PQ = (  # α / (α+Fe3C) solvus
    P,
    Q,
)
CEM_HIGH = (D, F)
CEM_MID = (F, K)
CEM_LOW = (K, CEM_BOT)
PERI_H = (H, J, B)
EUT_H = (E, Cpt, F)
EUTD_H = (P, S, K)


def build() -> Diagram:
    l_poly = (
        (0.0, T_MAX),
        CEM_TOP,
        D,
        *tuple(reversed(LIQUIDUS_CEM[1:])),
        *tuple(reversed(LIQUIDUS_GAMMA[1:])),
        *tuple(reversed(LIQUIDUS_DELTA)),
        (0.0, T_MAX),
    )
    delta_poly = (FE_MELT, H, N, FE_MELT)
    gamma_poly = (
        J,
        *SOLIDUS_GAMMA[1:],
        *ACM[1:],
        *tuple(reversed(A3[:-1])),
        N,
        J,
    )
    alpha_poly = (
        G,
        P,
        Q,
        (0.0, T_MIN),
        G,
    )
    fields = (
        PhaseField(
            id="L",
            name_zh="液相 L",
            phases=("L",),
            hover_zh="相区：钢液 / 铁液。",
            color=C.L,
            polygon=l_poly,
        ),
        PhaseField(
            id="delta",
            name_zh="δ 铁素体",
            phases=("δ",),
            hover_zh="相区：高温 BCC δ 铁。纯铁在 1394–1538 °C 之间是 δ。",
            color=C.DELTA,
            polygon=delta_poly,
        ),
        PhaseField(
            id="gamma",
            name_zh="奥氏体 γ",
            phases=("γ",),
            hover_zh="相区：FCC 奥氏体。钢的热加工、淬火前的奥氏体化，都是把合金抬进这个单相区。",
            color=C.GAMMA,
            polygon=gamma_poly,
        ),
        PhaseField(
            id="alpha",
            name_zh="铁素体 α",
            phases=("α",),
            hover_zh="相区：低温 BCC 铁素体。碳溶解度极低，所以工业纯铁几乎是单相 α，钢则做不到。",
            color=C.ALPHA,
            polygon=alpha_poly,
        ),
        PhaseField(
            id="L_delta",
            name_zh="L + δ",
            phases=("L", "δ"),
            hover_zh="相区：钢液 + δ 铁。低碳钢凝固开始时常先出 δ。",
            color=C.L_DELTA,
            polygon=polygon_between(SOLIDUS_DELTA, LIQUIDUS_DELTA),
            left_curve=SOLIDUS_DELTA,
            right_curve=LIQUIDUS_DELTA,
            left_phase="δ",
            right_phase="L",
            t_min=1495.0,
            t_max=1538.0,
        ),
        PhaseField(
            id="delta_gamma",
            name_zh="δ + γ",
            phases=("δ", "γ"),
            hover_zh="相区：δ 与奥氏体共存。包晶反应就发生在这个楔形区的顶边。",
            color=C.DELTA_GAMMA,
            polygon=polygon_between(A4_DELTA, A4_GAMMA),
            left_curve=A4_DELTA,
            right_curve=A4_GAMMA,
            left_phase="δ",
            right_phase="γ",
            t_min=1394.0,
            t_max=1495.0,
        ),
        PhaseField(
            id="L_gamma",
            name_zh="L + γ",
            phases=("L", "γ"),
            hover_zh="相区：钢液 + 奥氏体。中、高碳钢凝固时先长奥氏体枝晶。",
            color=C.L_GAMMA,
            polygon=polygon_between(SOLIDUS_GAMMA, LIQUIDUS_GAMMA),
            left_curve=SOLIDUS_GAMMA,
            right_curve=LIQUIDUS_GAMMA,
            left_phase="γ",
            right_phase="L",
            t_min=1148.0,
            t_max=1495.0,
        ),
        PhaseField(
            id="L_cem",
            name_zh="L + Fe₃C",
            phases=("L", "Fe₃C"),
            hover_zh="相区：铁液 + 一次渗碳体。过共晶铸铁先析出 Fe₃C。",
            color=C.L_CEM,
            polygon=polygon_between(LIQUIDUS_CEM, CEM_HIGH),
            left_curve=LIQUIDUS_CEM,
            right_curve=CEM_HIGH,
            left_phase="L",
            right_phase="Fe₃C",
            t_min=1148.0,
            t_max=1227.0,
        ),
        PhaseField(
            id="alpha_gamma",
            name_zh="α + γ",
            phases=("α", "γ"),
            hover_zh="相区：铁素体 + 奥氏体。亚共析钢从奥氏体区冷却，先沿 A3 析出先共析铁素体。",
            color=C.ALPHA_GAMMA,
            polygon=polygon_between(GP, A3),
            left_curve=GP,
            right_curve=A3,
            left_phase="α",
            right_phase="γ",
            t_min=727.0,
            t_max=912.0,
        ),
        PhaseField(
            id="gamma_cem",
            name_zh="γ + Fe₃C",
            phases=("γ", "Fe₃C"),
            hover_zh="相区：奥氏体 + 渗碳体。过共析钢走 Acm 先出网状渗碳体；铸铁在共晶之后也停在这里，直到共析。",
            color=C.GAMMA_CEM,
            polygon=polygon_between(ACM, CEM_MID),
            left_curve=ACM,
            right_curve=CEM_MID,
            left_phase="γ",
            right_phase="Fe₃C",
            t_min=727.0,
            t_max=1148.0,
        ),
        PhaseField(
            id="alpha_cem",
            name_zh="α + Fe₃C",
            phases=("α", "Fe₃C"),
            hover_zh="相区：铁素体 + 渗碳体。室温钢与白口铸铁的平衡组织都在这里。共析成分下它就是珠光体。",
            color=C.ALPHA_CEM,
            polygon=polygon_between(PQ, CEM_LOW),
            left_curve=PQ,
            right_curve=CEM_LOW,
            left_phase="α",
            right_phase="Fe₃C",
            t_min=T_MIN,
            t_max=727.0,
        ),
    )
    curves = (
        Curve("liq_d", "liquidus", "液相线（δ）", "液相线：低碳端，液体开始结晶出 δ。", LIQUIDUS_DELTA),
        Curve("liq_g", "liquidus", "液相线（γ）", "液相线：中高碳端，液体开始结晶出奥氏体。", LIQUIDUS_GAMMA),
        Curve("liq_c", "liquidus", "液相线（渗碳体）", "液相线：过共晶端，液体开始结晶出一次渗碳体。", LIQUIDUS_CEM),
        Curve("sol_d", "solidus", "固相线（δ）", "固相线：δ 与钢液平衡时的 δ 成分。", SOLIDUS_DELTA),
        Curve("sol_g", "solidus", "固相线（γ）", "固相线：奥氏体与钢液平衡时的奥氏体成分，直到 E 点 2.11 wt%。", SOLIDUS_GAMMA),
        Curve("a3", "solvus", "A3 / 溶解度曲线（γ–α）", "溶解度曲线 A3：奥氏体开始析出铁素体的温度。亚共析钢正火、退火都要读这条线。", A3),
        Curve("acm", "solvus", "Acm / 溶解度曲线（γ–Fe₃C）", "溶解度曲线 Acm：过共析钢从奥氏体析出渗碳体的边界。", ACM),
        Curve("gp", "solvus", "溶解度曲线（α–γ）", "溶解度曲线：铁素体中碳的固溶极限（相对奥氏体）。", GP),
        Curve("pq", "solvus", "溶解度曲线（α–Fe₃C）", "溶解度曲线：铁素体中碳的固溶极限（相对渗碳体）。室温下几乎不溶碳。", PQ),
        Curve("peri_h", "invariant", "包晶水平线", "包晶 L+δ → γ，1495 °C。", PERI_H),
        Curve("eut_h", "invariant", "共晶水平线", "共晶 L → γ+Fe₃C（莱氏体），1148 °C。", EUT_H),
        Curve("eutd_h", "invariant", "共析水平线 A1", "共析 γ → α+Fe₃C（珠光体），727 °C。钢的退火、正火、球化都围绕这条线。", EUTD_H),
    )
    invariants = (
        Invariant(
            id="peritectic",
            kind="peritectic",
            name_zh="包晶",
            formula_zh="L + δ → γ",
            temperature=1495.0,
            x_star=0.17,
            x_left=0.09,
            x_right=0.53,
            x_mid=0.17,
            phases=("L", "δ", "γ"),
            hover_zh="包晶：1495 °C，δ 0.09 / γ 0.17 / L 0.53 wt% C。液体与 δ 反应生成奥氏体。",
            cooling_meaning_zh="低碳钢凝固穿过 1495 °C 时，δ 被钢液消耗并改成奥氏体。反应依赖扩散，铸坯里常留下包晶偏析。",
        ),
        Invariant(
            id="eutectic",
            kind="eutectic",
            name_zh="共晶（莱氏体）",
            formula_zh="L → γ + Fe₃C",
            temperature=1148.0,
            x_star=4.30,
            x_left=2.11,
            x_right=6.67,
            x_mid=None,
            phases=("L", "γ", "Fe₃C"),
            hover_zh="共晶：1148 °C，4.30 wt% C。剩余钢液变成奥氏体+渗碳体，即莱氏体。铸铁与钢的分界正在这条水平线的左端 E 点（2.11 wt%）。",
            cooling_meaning_zh="铸铁冷却到 1148 °C，剩余液体恒温变成 γ+Fe₃C。E 点以左（<2.11 wt% C）是钢，以右是铸铁。",
        ),
        Invariant(
            id="eutectoid",
            kind="eutectoid",
            name_zh="共析（珠光体）",
            formula_zh="γ → α + Fe₃C",
            temperature=727.0,
            x_star=0.76,
            x_left=0.022,
            x_right=6.67,
            x_mid=None,
            phases=("γ", "α", "Fe₃C"),
            hover_zh="共析：727 °C，0.76 wt% C。奥氏体变成铁素体+渗碳体片层，即珠光体。A1 线是钢热处理最常用的一条水平线。",
            cooling_meaning_zh="无论钢还是白口铸铁，只要还剩奥氏体，冷却过 727 °C 就会变成珠光体（外加先共析铁素体或渗碳体）。",
        ),
    )
    special = (
        SpecialPoint(0.0, 1538.0, "Fe 1538 °C", "纯铁熔点。"),
        SpecialPoint(0.0, 1394.0, "A4 1394 °C", "纯铁 δ ⇄ γ。"),
        SpecialPoint(0.0, 912.0, "A3 912 °C", "纯铁 γ ⇄ α。"),
        SpecialPoint(0.17, 1495.0, "J 包晶 γ", "包晶产物奥氏体成分 0.17 wt% C。"),
        SpecialPoint(2.11, 1148.0, "E 2.11 wt%", "奥氏体最大溶碳量；钢 / 铸铁分界。"),
        SpecialPoint(4.30, 1148.0, "C 共晶 4.30 wt%", "莱氏体成分。"),
        SpecialPoint(0.76, 727.0, "S 共析 0.76 wt%", "珠光体成分。"),
        SpecialPoint(0.022, 727.0, "P 0.022 wt%", "共析温度下铁素体溶碳上限。"),
        SpecialPoint(6.67, 1148.0, "Fe₃C 6.67 wt%", "渗碳体计量成分。"),
    )
    return Diagram(
        id="fe_c",
        title_zh="Fe–Fe₃C 亚稳相图（钢铁）",
        subtitle_zh="一张图同时有包晶、共晶、共析：钢与铸铁、珠光体、奥氏体化都从这里读",
        x_label_zh="C 含量 / wt%",
        y_label_zh="温度 / °C",
        x_min=0.0,
        x_max=X_MAX,
        t_min=T_MIN,
        t_max=T_MAX,
        components=("Fe", "C"),
        n_components=2,
        fields=fields,
        curves=curves,
        invariants=invariants,
        special_points=special,
        source_note_zh="亚稳 Fe–Fe₃C（不是稳定 Fe–石墨）。本文件采用：共析 0.76 wt% C / 727 °C，共晶 4.30 wt% C / 1148 °C，包晶 1495 °C（δ 0.09、γ 0.17、L 0.53），E 点 2.11 wt%，P 点 0.022 wt%。手册里共析有 0.76–0.80 wt%、723–727 °C 的差别；解释器与本图使用同一套数。曲线为教学拓扑，不是 CALPHAD。",
        practical_kind="steel",
        default_x=0.40,
        default_T=800.0,
        extra_notes_zh="C < 2.11 wt% 按钢读，C > 2.11 wt% 按铸铁读。亚共析 / 共析 / 过共析以 0.76 wt% 为界。",
    )
