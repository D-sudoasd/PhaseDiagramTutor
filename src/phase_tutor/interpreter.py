"""UI-free constitution interpreter: field, tie-line, lever rule, phase rule, isopleth."""

from __future__ import annotations

from .diagrams.registry import get_diagram
from .geometry import T_at_x, point_in_polygon, x_at_T
from .models import (
    Diagram,
    Interpretation,
    Invariant,
    IsoplethStep,
    PhaseField,
    TieLine,
)

INVARIANT_ATOL = 0.2  # °C


def _ordered_ends(
    field: PhaseField, T: float
) -> tuple[float, float, str, str] | None:
    if not field.is_two_phase:
        return None
    if field.t_min is not None and T < field.t_min - 1e-6:
        return None
    if field.t_max is not None and T > field.t_max + 1e-6:
        return None
    x_a = x_at_T(field.left_curve, T)
    x_b = x_at_T(field.right_curve, T)
    if x_a is None or x_b is None:
        return None
    p_a = field.left_phase or field.phases[0]
    p_b = field.right_phase or field.phases[-1]
    if x_a <= x_b:
        return x_a, x_b, p_a, p_b
    return x_b, x_a, p_b, p_a


def locate_field(diagram: Diagram, x: float, T: float) -> PhaseField | None:
    """Geometric field only (no invariant snap). Two-phase bands win on their edges."""
    hits: list[tuple[float, PhaseField]] = []
    for field in diagram.fields:
        if not field.is_two_phase:
            continue
        ends = _ordered_ends(field, T)
        if ends is None:
            continue
        xL, xR, _, _ = ends
        if xL - 1e-7 <= x <= xR + 1e-7:
            slack = min(x - xL, xR - x)
            hits.append((slack, field))
    if hits:
        hits.sort(key=lambda item: -item[0])
        return hits[0][1]
    for field in diagram.fields:
        if field.is_two_phase:
            continue
        if point_in_polygon(x, T, field.polygon, include_edge=True):
            return field
    # last resort: nearest single-phase polygon centroid-ish by any containment with looser edge
    return None


def matching_invariant(diagram: Diagram, x: float, T: float) -> Invariant | None:
    for inv in diagram.invariants:
        if abs(T - inv.temperature) <= INVARIANT_ATOL and inv.x_min - 1e-6 <= x <= inv.x_max + 1e-6:
            return inv
    return None


def _invariant_compositions(inv: Invariant) -> dict[str, float]:
    if inv.kind == "eutectic":
        # L at x_star, left solid, right solid
        liquid, left, right = inv.phases
        return {left: inv.x_left, liquid: inv.x_star, right: inv.x_right}
    if inv.kind == "peritectic":
        # formula L + α → β ; phases stored (L, α, β) or similar
        mapping: dict[str, float] = {}
        # α left, β mid/star, L right is the Fe-C / schematic convention
        solids = [p for p in inv.phases if p != "L"]
        if "L" in inv.phases:
            mapping["L"] = inv.x_right
        if len(solids) >= 1:
            mapping[solids[0]] = inv.x_left
        if len(solids) >= 2:
            mapping[solids[1]] = inv.x_mid if inv.x_mid is not None else inv.x_star
        return mapping
    if inv.kind == "eutectoid":
        parent, left, right = inv.phases
        return {left: inv.x_left, parent: inv.x_star, right: inv.x_right}
    return {}


def _fractions(x: float, xL: float, xR: float) -> tuple[float, float, bool]:
    span = xR - xL
    if span <= 1e-12:
        return 1.0, 0.0, True
    if x <= xL + 1e-10:
        return 1.0, 0.0, True
    if x >= xR - 1e-10:
        return 0.0, 1.0, True
    fL = (xR - x) / span
    fR = (x - xL) / span
    on_boundary = fL < 1e-6 or fR < 1e-6
    return fL, fR, on_boundary


def _phase_rule(C: int, P: int) -> tuple[int, str]:
    F = C - P + 1
    if F < 0:
        F = 0
    if P == 1:
        text = (
            f"组元数 C = {C}，相数 P = {P}。凝聚态相律 F = C − P + 1 = {F}。"
            "单相区里温度和总成分都可以独立改，点可以在这块面积里自由移动。"
        )
    elif P == 2:
        text = (
            f"组元数 C = {C}，相数 P = {P}。凝聚态相律 F = C − P + 1 = {F}。"
            "双相区只剩一个自由度：选定温度后，两相各自的成分就被结线钉死，只能改总成分来改质量分数。"
        )
    else:
        text = (
            f"组元数 C = {C}，相数 P = {P}。凝聚态相律 F = C − P + 1 = {F}。"
            "三相共存时温度和三相成分全部固定，冷却停在这条水平线上，直到反应结束。"
        )
    return F, text


def _steel_practical(x: float, T: float, field: PhaseField, inv: Invariant | None) -> str:
    if x < 2.11:
        metal = "钢"
        if x < 0.73:
            sub = "亚共析钢"
        elif x <= 0.79:
            sub = "共析钢"
        else:
            sub = "过共析钢"
    else:
        metal = "铸铁"
        if x < 4.22:
            sub = "亚共晶铸铁"
        elif x <= 4.38:
            sub = "共晶铸铁"
        else:
            sub = "过共晶铸铁"
    bits = [f"按本图：{x:.3f} wt% C 属于{metal}（{sub}）。分界在 E 点 2.11 wt% C。"]
    if field.id == "gamma":
        bits.append("当前在奥氏体单相区，对应热处理里的奥氏体化：碳全部溶进 γ，随后才能淬火或控冷。")
    elif field.id == "alpha_gamma":
        bits.append("亚共析钢从 γ 冷却时先沿 A3 析出铁素体，剩下的 γ 成分沿 A3 走向共析点 S，最后变成珠光体。")
    elif field.id == "gamma_cem":
        if x < 2.11:
            bits.append("过共析钢从 γ 冷却时先沿 Acm 析出渗碳体（常呈网状），剩余 γ 走向 S 点再变成珠光体。")
        else:
            bits.append("铸铁共晶之后停在 γ+Fe₃C（莱氏体），继续冷到 727 °C 发生共析，γ 变成珠光体。")
    elif field.id == "alpha_cem":
        bits.append("室温平衡组织是铁素体 + 渗碳体。共析成分下几乎全是珠光体；亚共析还有先共析铁素体，过共析还有先共析渗碳体。")
    elif field.id == "L_cem":
        bits.append("过共晶铸铁：先析出一次渗碳体，液体沿液相线走向共晶点 C（4.30 wt%）。")
    elif field.id == "L_gamma":
        bits.append("凝固先长奥氏体枝晶。液体沿液相线变富碳，固体沿固相线变富碳。")
    if inv is not None:
        bits.append(inv.cooling_meaning_zh)
    return "".join(bits)


def _titanium_practical(diagram: Diagram, x: float, T: float, field: PhaseField) -> str:
    transus = None
    for curve in diagram.curves:
        if curve.id == "transus":
            transus = T_at_x(curve.points, x)
            break
    bits = []
    if transus is not None:
        bits.append(f"本成分的 β transus 约为 {transus:.0f} °C（α 全部消失、进入 β 单相的温度）。")
        if T > transus + 1:
            bits.append("现在在 transus 以上，是 β 单相窗口，对应 β 退火或从 β 区淬火。")
        elif field.id == "alpha_beta":
            bits.append("现在在 transus 以下的 α+β 窗口：双相钛合金的锻造、固溶、时效通常把温度放在这里，用结线读 α/β 各占多少。")
        elif field.id == "alpha":
            bits.append("现在在 α 单相区，更接近 α 钛合金一侧。")
    if x >= 20:
        bits.append("V 已经足够高，transus 接近室温，这是 β 钛合金的读法：室温可以保留 β。")
    elif x <= 3.2:
        bits.append("V 很低，室温以 α 为主，接近 α 钛合金。")
    else:
        bits.append("中等 β 稳定元素含量，按 α+β 钛合金读：组织由 transus 以下的停留温度决定。")
    return "".join(bits)


def _location_reading(
    diagram: Diagram,
    x: float,
    T: float,
    field: PhaseField,
    tie: TieLine | None,
    inv: Invariant | None,
    on_boundary: bool,
) -> str:
    if inv is not None:
        return (
            f"温度正好落在{inv.name_zh}水平线（{inv.temperature:.0f} °C）上，"
            f"反应式 {inv.formula_zh}。三相成分固定，"
            f"总成分 {x:.3g} 只决定反应还能走多远，不能单独定出三个质量分数。"
            f"{inv.cooling_meaning_zh}"
        )
    if not field.is_two_phase:
        return (
            f"点 ({x:.3g} {diagram.x_label_zh.split('/')[0].strip()}, {T:.1f} °C) 落在单相区「{field.name_zh}」。"
            f"显微镜下（平衡态）只应看到这一个相，质量分数 100%。"
            f"{field.hover_zh}"
        )
    assert tie is not None
    if on_boundary:
        winner = tie.left_phase if tie.left_fraction >= tie.right_fraction else tie.right_phase
        return (
            f"点正好压在相区边界上，结线一端的质量分数为 100%，所以当前是 100% {winner}。"
            f"再往双相区里走一点点，就会开始出现第二相。"
        )
    return (
        f"点落在双相区「{field.name_zh}」。过这个点画一条等温水平线，就是结线："
        f"{tie.left_phase} 端成分 {tie.left[0]:.3g}，{tie.right_phase} 端成分 {tie.right[0]:.3g}。"
        f"杠杆定律把总成分看成支点：离谁远，谁的质量分数就大。"
        f"{tie.left_phase} 占 {tie.left_fraction * 100:.1f}%，"
        f"{tie.right_phase} 占 {tie.right_fraction * 100:.1f}%。"
    )


def _lever_text(tie: TieLine | None, inv: Invariant | None) -> str:
    if inv is not None:
        return "三相点不能用一根结线定出三个质量分数。冷却时反应在恒温下进行，分数随反应进度变，不随温度变。"
    if tie is None:
        return "单相区没有结线，也没有杠杆：只有一个相，质量分数为 1。"
    return (
        f"结线：({tie.left[0]:.4g}, {tie.left[1]:.2f}) — ({tie.right[0]:.4g}, {tie.right[1]:.2f})。"
        f"杠杆定律 w({tie.left_phase}) = (x_右 − x) / (x_右 − x_左) = {tie.left_fraction:.4f}，"
        f"w({tie.right_phase}) = (x − x_左) / (x_右 − x_左) = {tie.right_fraction:.4f}，"
        f"二者之和 {tie.left_fraction + tie.right_fraction:.4f}。"
    )


def _practical(diagram: Diagram, x: float, T: float, field: PhaseField, inv: Invariant | None) -> str:
    if diagram.practical_kind == "steel":
        return _steel_practical(x, T, field, inv)
    if diagram.practical_kind == "titanium":
        return _titanium_practical(diagram, x, T, field)
    if diagram.practical_kind == "isomorphous":
        if field.id == "L_alpha":
            return "凝固区间里固相与液相成分不同，这就是枝晶偏析的来源。均匀化退火，就是在固相线以下把这个浓度差扩散掉。"
        if field.id == "alpha":
            return "已经全部是固溶体。Cu–Ni 之所以能做成任意成分的单相合金，就是因为这张图底部没有双相区。"
        return "还在液相。冷却碰到液相线才开始结晶。"
    if diagram.practical_kind == "eutectic":
        if inv is not None:
            return "焊料选在共晶成分附近，就是为了让熔化/凝固几乎发生在一个温度，铺展好、热损伤小。"
        if field.id == "alpha_beta":
            return "室温焊点是 α+β 两相。共晶成分几乎全是细密共晶组织；偏共晶则会留下先析出的块状相。"
        return "亚共晶先出 α，过共晶先出 β，剩余液体都被赶到共晶点。"
    if diagram.practical_kind == "peritectic":
        return "包晶产物长在已有固体表面，液体必须穿过这层固相才能继续反应，所以实际组织里常看到「芯部残留 α、外包 β」。钢铁里那一小段包晶也是同样的几何。"
    return diagram.extra_notes_zh


def interpret(diagram: Diagram | str, x: float, T: float) -> Interpretation:
    if isinstance(diagram, str):
        diagram = get_diagram(diagram)
    inv = matching_invariant(diagram, x, T)
    field = locate_field(diagram, x, T)
    if field is None:
        raise ValueError(f"点 ({x}, {T}) 落在相图 {diagram.id} 覆盖范围外。")

    C = diagram.n_components
    if inv is not None:
        comps = _invariant_compositions(inv)
        P = len(inv.phases)
        F, rule = _phase_rule(C, P)
        reading = _location_reading(diagram, x, T, field, None, inv, False)
        return Interpretation(
            diagram_id=diagram.id,
            x=x,
            T=T,
            field_id=f"invariant:{inv.id}",
            field_name_zh=f"{inv.name_zh}（{inv.formula_zh}）",
            phases=inv.phases,
            fractions={},
            phase_compositions=comps,
            tie_line=None,
            C=C,
            P=P,
            F=F,
            on_boundary=False,
            on_invariant=True,
            invariant=inv,
            location_reading_zh=reading,
            lever_explain_zh=_lever_text(None, inv),
            phase_rule_zh=rule,
            practical_zh=_practical(diagram, x, T, field, inv),
        )

    if field.is_two_phase:
        ends = _ordered_ends(field, T)
        assert ends is not None
        xL, xR, pL, pR = ends
        fL, fR, on_boundary = _fractions(x, xL, xR)
        tie = TieLine(
            left=(xL, T),
            right=(xR, T),
            left_phase=pL,
            right_phase=pR,
            left_fraction=fL,
            right_fraction=fR,
        )
        fractions = {pL: fL, pR: fR}
        comps = {pL: xL, pR: xR}
        P = 2
        F, rule = _phase_rule(C, P)
        return Interpretation(
            diagram_id=diagram.id,
            x=x,
            T=T,
            field_id=field.id,
            field_name_zh=field.name_zh,
            phases=(pL, pR),
            fractions=fractions,
            phase_compositions=comps,
            tie_line=tie,
            C=C,
            P=P,
            F=F,
            on_boundary=on_boundary,
            on_invariant=False,
            invariant=None,
            location_reading_zh=_location_reading(diagram, x, T, field, tie, None, on_boundary),
            lever_explain_zh=_lever_text(tie, None),
            phase_rule_zh=rule,
            practical_zh=_practical(diagram, x, T, field, None),
        )

    phase = field.phases[0]
    P = 1
    F, rule = _phase_rule(C, P)
    return Interpretation(
        diagram_id=diagram.id,
        x=x,
        T=T,
        field_id=field.id,
        field_name_zh=field.name_zh,
        phases=(phase,),
        fractions={phase: 1.0},
        phase_compositions={phase: x},
        tie_line=None,
        C=C,
        P=P,
        F=F,
        on_boundary=False,
        on_invariant=False,
        invariant=None,
        location_reading_zh=_location_reading(diagram, x, T, field, None, None, False),
        lever_explain_zh=_lever_text(None, None),
        phase_rule_zh=rule,
        practical_zh=_practical(diagram, x, T, field, None),
    )


def _field_cooling_meaning(field: PhaseField) -> str:
    return field.hover_zh


def walk_isopleth(
    diagram: Diagram | str,
    x: float,
    t_high: float | None = None,
    t_low: float | None = None,
    n: int = 2500,
) -> list[IsoplethStep]:
    if isinstance(diagram, str):
        diagram = get_diagram(diagram)
    t_high = diagram.t_max if t_high is None else t_high
    t_low = diagram.t_min if t_low is None else t_low
    if n < 2:
        n = 2
    steps: list[IsoplethStep] = []
    prev_id: str | None = None
    crossed: set[str] = set()
    prev_T = t_high
    for i in range(n):
        T = t_high - i * (t_high - t_low) / (n - 1)
        for inv in diagram.invariants:
            if inv.id in crossed:
                continue
            if (prev_T - inv.temperature) * (T - inv.temperature) <= 0:
                if inv.x_min - 1e-6 <= x <= inv.x_max + 1e-6:
                    steps.append(
                        IsoplethStep(
                            temperature=inv.temperature,
                            kind="invariant",
                            name_zh=inv.name_zh,
                            field_id=None,
                            formula_zh=inv.formula_zh,
                            meaning_zh=inv.cooling_meaning_zh,
                            phases=inv.phases,
                        )
                    )
                    crossed.add(inv.id)
        field = locate_field(diagram, x, T)
        if field is None:
            prev_T = T
            continue
        if field.id != prev_id:
            steps.append(
                IsoplethStep(
                    temperature=T,
                    kind="field",
                    name_zh=field.name_zh,
                    field_id=field.id,
                    formula_zh=None,
                    meaning_zh=_field_cooling_meaning(field),
                    phases=field.phases,
                )
            )
            prev_id = field.id
        prev_T = T
    return steps
