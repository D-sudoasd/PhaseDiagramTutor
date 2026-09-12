"""Chinese readout text for a constitution interpretation."""

from __future__ import annotations

from .interpreter import interpret, walk_isopleth
from .models import Diagram, Interpretation, IsoplethStep


def format_readout_text(interp: Interpretation) -> str:
    lines: list[str] = []
    lines.append("【当前位置】")
    lines.append(f"成分 x = {interp.x:.4g}")
    lines.append(f"温度 T = {interp.T:.2f} °C")
    lines.append(f"相区：{interp.field_name_zh}")
    lines.append("")
    lines.append("【相组成】")
    if interp.on_invariant:
        lines.append("三相共存（不变反应正在进行）。")
        for phase, comp in interp.phase_compositions.items():
            lines.append(f"  {phase} 的固定成分 = {comp:.4g}")
        lines.append("质量分数不能单由总成分唯一确定，取决于反应进行程度。")
    else:
        for phase in interp.phases:
            frac = interp.fractions.get(phase, 0.0)
            comp = interp.phase_compositions.get(phase, interp.x)
            lines.append(f"  {phase}：成分 {comp:.4g}，质量分数 {frac:.4f}（{frac * 100:.1f}%）")
        total = sum(interp.fractions.values())
        lines.append(f"质量分数之和 = {total:.4f}")
    lines.append("")
    lines.append("【结线与杠杆定律】")
    lines.append(interp.lever_explain_zh)
    lines.append("")
    lines.append("【相律】")
    lines.append(interp.phase_rule_zh)
    lines.append("")
    lines.append("【这个点怎么读】")
    lines.append(interp.location_reading_zh)
    lines.append("")
    lines.append("【在材料里怎么用】")
    lines.append(interp.practical_zh)
    return "\n".join(lines)


def format_isopleth_text(steps: list[IsoplethStep], x: float) -> str:
    lines = [f"【冷却线】固定成分 x = {x:.4g}，从高温走到低温："]
    for i, step in enumerate(steps, 1):
        if step.kind == "invariant":
            formula = step.formula_zh or ""
            lines.append(f"{i}. {step.temperature:.1f} °C  穿过{step.name_zh}  {formula}")
            lines.append(f"    {step.meaning_zh}")
        else:
            lines.append(f"{i}. {step.temperature:.1f} °C  进入相区「{step.name_zh}」")
            lines.append(f"    {step.meaning_zh}")
    return "\n".join(lines)


def cooling_step_labels(steps: list[IsoplethStep]) -> list[str]:
    labels: list[str] = []
    for step in steps:
        if step.kind == "invariant":
            labels.append(f"{step.temperature:.0f} °C · {step.name_zh} {step.formula_zh or ''}".strip())
        else:
            labels.append(f"{step.temperature:.0f} °C · {step.name_zh}")
    return labels


def cooling_jump_temperature(steps: list[IsoplethStep], index: int, t_min: float) -> float:
    """Temperature to land on when the user picks a cooling-line segment.

    Field entries from walk_isopleth sit just below an invariant (within
    INVARIANT_ATOL). Jumping to that sample T would snap back to 共晶/包晶.
    Use the midpoint toward the next step, or T − (atol+ε) if the slice is thin.
    Invariant rows keep the invariant temperature.
    """
    from .interpreter import INVARIANT_ATOL

    step = steps[index]
    if step.kind == "invariant":
        return float(step.temperature)
    next_T = float(steps[index + 1].temperature) if index + 1 < len(steps) else float(t_min)
    mid = 0.5 * (float(step.temperature) + next_T)
    margin = INVARIANT_ATOL + 0.05
    if abs(mid - step.temperature) <= INVARIANT_ATOL:
        going_down = next_T <= step.temperature
        mid = float(step.temperature) - margin if going_down else float(step.temperature) + margin
    return float(mid)


def current_cooling_index(steps: list[IsoplethStep], T: float) -> int:
    if not steps:
        return 0
    idx = 0
    for i, step in enumerate(steps):
        if step.temperature + 1e-6 >= T:
            idx = i
        else:
            break
    return idx


def first_screen_answers(
    interp: Interpretation,
    steps: list[IsoplethStep],
    iso_x: float,
) -> dict[str, str]:
    """Three first-screen sentences: phases, 结线/杠杆, cooling path."""
    if interp.on_invariant:
        phases = "三相：" + "、".join(interp.phases)
    else:
        bits = []
        for phase in interp.phases:
            frac = interp.fractions.get(phase, 0.0)
            comp = interp.phase_compositions.get(phase, interp.x)
            bits.append(f"{phase} {frac * 100:.1f}%（成分 {comp:.3g}）")
        phases = "；".join(bits) if bits else interp.field_name_zh

    if interp.tie_line is not None:
        tl = interp.tie_line
        lever = (
            f"结线 {tl.left_phase}={tl.left[0]:.3g}（杠杆 {tl.left_fraction * 100:.1f}%）—"
            f"{tl.right_phase}={tl.right[0]:.3g}（杠杆 {tl.right_fraction * 100:.1f}%）。"
            "离谁远，谁的量就多。"
        )
    elif interp.on_invariant:
        lever = "三相点：质量分数随反应进度变，不能单用总成分定死。"
    else:
        lever = f"单相区没有结线。{interp.phases[0]} 占 100%。"

    labels = cooling_step_labels(steps)
    cooling = f"成分 {iso_x:.3g}：" + ("；".join(labels) if labels else "（无）")
    return {"phases": phases, "lever": lever, "cooling": cooling}


def readout_bundle(diagram: Diagram | str, x: float, T: float, isopleth_x: float | None = None) -> str:
    interp = interpret(diagram, x, T)
    iso_x = x if isopleth_x is None else isopleth_x
    steps = walk_isopleth(diagram, iso_x)
    return format_readout_text(interp) + "\n\n" + format_isopleth_text(steps, iso_x)
