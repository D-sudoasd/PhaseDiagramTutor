"""Plotly figure: phase fields, named curves, constitution point, tie-line, isopleth."""

from __future__ import annotations

import json
from typing import Any

import plotly.graph_objects as go

from .geometry import polygon_label_point
from .interpreter import interpret, walk_isopleth
from .models import Diagram, Interpretation, close_ring


HIT_LAYER_NAME = "定位层"
HIT_NX = 81
HIT_NY = 61

CURVE_STYLE = {
    "liquidus": dict(color="#C48A1A", width=2.6, dash="solid"),
    "solidus": dict(color="#3F6B4F", width=2.4, dash="solid"),
    "solvus": dict(color="#5B4B8A", width=2.2, dash="dot"),
    "invariant": dict(color="#8B2E2E", width=2.8, dash="solid"),
    "other": dict(color="#444444", width=1.8, dash="solid"),
}


def _field_xy(polygon) -> tuple[list[float], list[float]]:
    ring = close_ring(polygon)
    return [p[0] for p in ring], [p[1] for p in ring]


def hit_grid(diagram: Diagram, nx: int = HIT_NX, ny: int = HIT_NY) -> tuple[list[float], list[float]]:
    xs = [diagram.x_min + i * (diagram.x_max - diagram.x_min) / (nx - 1) for i in range(nx)]
    ys = [diagram.t_min + j * (diagram.t_max - diagram.t_min) / (ny - 1) for j in range(ny)]
    gx: list[float] = []
    gy: list[float] = []
    for y in ys:
        for x in xs:
            gx.append(x)
            gy.append(y)
    return gx, gy


def nearest_hit_point(
    diagram: Diagram,
    x: float,
    T: float,
    nx: int = HIT_NX,
    ny: int = HIT_NY,
) -> tuple[float, float]:
    """Snap (x, T) onto the click grid (same grid as the 定位层)."""
    gx = diagram.x_min + round((x - diagram.x_min) / (diagram.x_max - diagram.x_min) * (nx - 1)) * (
        (diagram.x_max - diagram.x_min) / (nx - 1)
    )
    gy = diagram.t_min + round((T - diagram.t_min) / (diagram.t_max - diagram.t_min) * (ny - 1)) * (
        (diagram.t_max - diagram.t_min) / (ny - 1)
    )
    gx = min(max(gx, diagram.x_min), diagram.x_max)
    gy = min(max(gy, diagram.t_min), diagram.t_max)
    return gx, gy


def point_from_plotly_select(points: list[Any], fig: go.Figure) -> tuple[float, float] | None:
    """Accept only the hit layer so field-polygon vertices cannot steal the click."""
    for pt in points:
        if isinstance(pt, dict):
            curve = pt.get("curve_number")
            px, py = pt.get("x"), pt.get("y")
        else:
            curve = getattr(pt, "curve_number", None)
            px, py = getattr(pt, "x", None), getattr(pt, "y", None)
        if px is None or py is None or curve is None:
            continue
        try:
            idx = int(curve)
        except (TypeError, ValueError):
            continue
        if 0 <= idx < len(fig.data) and fig.data[idx].name == HIT_LAYER_NAME:
            return float(px), float(py)
    return None


def lever_label_texts(interp: Interpretation) -> tuple[str, str, str] | None:
    """On-plot lever captions: left end, right end, fulcrum. None if no 结线."""
    tl = interp.tie_line
    if tl is None:
        return None
    left = (
        f"{tl.left_phase} {tl.left[0]:.3g}\n"
        f"杠杆 {tl.left_fraction * 100:.1f}%（{tl.left_fraction:.3f}）"
    )
    right = (
        f"{tl.right_phase} {tl.right[0]:.3g}\n"
        f"杠杆 {tl.right_fraction * 100:.1f}%（{tl.right_fraction:.3f}）"
    )
    fulcrum = f"支点 x={interp.x:.3g}"
    return left, right, fulcrum


def build_figure(
    diagram: Diagram,
    x: float,
    T: float,
    *,
    isopleth_x: float | None = None,
    interp: Interpretation | None = None,
    show_cooling_marks: bool = True,
) -> go.Figure:
    if interp is None:
        interp = interpret(diagram, x, T)
    iso_x = x if isopleth_x is None else isopleth_x
    fig = go.Figure()
    span_t = diagram.t_max - diagram.t_min

    for field in diagram.fields:
        xs, ys = _field_xy(field.polygon)
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                fill="toself",
                fillcolor=field.color,
                mode="lines",
                line=dict(width=0.4, color="rgba(80,60,40,0.20)"),
                name=field.name_zh,
                hovertemplate=(
                    f"<b>相区</b>：{field.name_zh}<br>"
                    f"{field.hover_zh}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    kind_zh = {
        "liquidus": "液相线",
        "solidus": "固相线",
        "solvus": "溶解度曲线",
        "invariant": "不变反应水平线",
        "other": "相界",
    }
    for curve in diagram.curves:
        style = CURVE_STYLE.get(curve.kind, CURVE_STYLE["other"])
        xs = [p[0] for p in curve.points]
        ys = [p[1] for p in curve.points]
        label = kind_zh.get(curve.kind, "相界")
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                line=style,
                name=curve.name_zh,
                hovertemplate=f"<b>{label}</b>：{curve.name_zh}<br>{curve.hover_zh}<extra></extra>",
                showlegend=False,
            )
        )

    for inv in diagram.invariants:
        fig.add_trace(
            go.Scatter(
                x=[inv.x_left, inv.x_right],
                y=[inv.temperature, inv.temperature],
                mode="lines",
                line=dict(color="#8B2E2E", width=2.4),
                name=f"{inv.name_zh} {inv.formula_zh}",
                hovertemplate=(
                    f"<b>{inv.name_zh}</b> {inv.formula_zh}<br>"
                    f"{inv.temperature:.0f} °C，特征成分 {inv.x_star:g}<br>"
                    f"{inv.hover_zh}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[iso_x, iso_x],
            y=[diagram.t_min, diagram.t_max],
            mode="lines",
            line=dict(color="#1F4E79", width=1.8, dash="dash"),
            name="冷却线（等成分线）",
            hovertemplate=(
                f"<b>冷却线</b>：成分固定为 {iso_x:.3g}<br>"
                "沿这条竖线降温，就是凝固或热处理走过的相区序列"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    if show_cooling_marks:
        steps = walk_isopleth(diagram, iso_x)
        mark_x, mark_y, mark_text = [], [], []
        for step in steps:
            if step.kind == "invariant":
                mark_x.append(iso_x)
                mark_y.append(step.temperature)
                mark_text.append(f"{step.name_zh} {step.formula_zh}")
        if mark_x:
            fig.add_trace(
                go.Scatter(
                    x=mark_x,
                    y=mark_y,
                    mode="markers",
                    marker=dict(size=9, color="#8B2E2E", symbol="x"),
                    name="冷却线穿过的不变反应",
                    hovertemplate="%{text}<extra></extra>",
                    text=mark_text,
                    showlegend=False,
                )
            )

    if interp.tie_line is not None:
        tl = interp.tie_line
        labels = lever_label_texts(interp)
        assert labels is not None
        left_txt, right_txt, fulcrum_txt = labels
        fig.add_trace(
            go.Scatter(
                x=[tl.left[0], tl.right[0]],
                y=[tl.left[1], tl.right[1]],
                mode="lines+markers",
                line=dict(color="#C0392B", width=2.6),
                marker=dict(size=9, color="#C0392B", symbol="line-ns"),
                name="结线",
                hovertemplate=(
                    "<b>结线</b>：等温连接两相成分<br>"
                    f"{tl.left_phase} 端 {tl.left[0]:.3g}（质量分数 {tl.left_fraction:.3f}）<br>"
                    f"{tl.right_phase} 端 {tl.right[0]:.3g}（质量分数 {tl.right_fraction:.3f}）<br>"
                    "杠杆定律：离谁远，谁的量就多"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[tl.left[0], tl.right[0]],
                y=[T, T],
                mode="markers",
                marker=dict(size=1, opacity=0),
                name="杠杆",
                hovertemplate=(
                    "<b>杠杆</b>：结线两端的质量分数<br>"
                    f"{left_txt.replace(chr(10), ' ')}<br>"
                    f"{right_txt.replace(chr(10), ' ')}<br>"
                    f"{fulcrum_txt}<br>"
                    "离谁远，谁的量就多"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )
        # Labels sit just outside the two-phase band (left of left end, right of right end).
        fig.add_annotation(
            x=tl.left[0],
            y=T + 0.04 * span_t,
            text=left_txt.replace("\n", "<br>"),
            showarrow=False,
            xanchor="right",
            bgcolor="rgba(255,255,255,0)",
            font=dict(size=11, color="#7a1f12"),
            xshift=-4,
        )
        fig.add_annotation(
            x=tl.right[0],
            y=T + 0.04 * span_t,
            text=right_txt.replace("\n", "<br>"),
            showarrow=False,
            xanchor="left",
            bgcolor="rgba(255,255,255,0)",
            font=dict(size=11, color="#7a1f12"),
            xshift=4,
        )

    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[T],
            mode="markers",
            marker=dict(size=14, color="#111111", line=dict(width=2, color="white"), symbol="x"),
            name="当前点",
            hovertemplate=(
                f"<b>当前点</b><br>成分 {x:.3g}<br>温度 {T:.1f} °C<br>"
                f"相区：{interp.field_name_zh}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    for field in diagram.fields:
        lx, ly = polygon_label_point(field.polygon)
        fig.add_annotation(
            x=lx,
            y=ly,
            text=field.name_zh,
            showarrow=False,
            font=dict(size=11, color="rgba(27,36,48,0.72)"),
            bgcolor="rgba(255,255,255,0)",
            captureevents=False,
        )

    gx, gy = hit_grid(diagram)
    fig.add_trace(
        go.Scatter(
            x=gx,
            y=gy,
            mode="markers",
            marker=dict(size=14, color="rgba(0,0,0,0)"),
            name=HIT_LAYER_NAME,
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_layout(
        template="plotly_white",
        font=dict(family="Microsoft YaHei, Noto Sans SC, Segoe UI, sans-serif", size=12, color="#1b2430"),
        title=None,
        showlegend=False,
        xaxis=dict(
            title=diagram.x_label_zh,
            range=[diagram.x_min, diagram.x_max],
            ticks="outside",
            showgrid=True,
            gridcolor="rgba(27,36,48,0.08)",
            zeroline=False,
            linecolor="#9aa6b2",
            mirror=True,
        ),
        yaxis=dict(
            title=diagram.y_label_zh,
            range=[diagram.t_min, diagram.t_max],
            ticks="outside",
            showgrid=True,
            gridcolor="rgba(27,36,48,0.08)",
            zeroline=False,
            linecolor="#9aa6b2",
            mirror=True,
        ),
        margin=dict(l=58, r=16, t=10, b=52),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(family="Microsoft YaHei, Noto Sans SC, sans-serif", size=12, color="#1b2430"),
            align="left",
        ),
        plot_bgcolor="#f7f9fb",
        paper_bgcolor="#ffffff",
        uirevision="phase-tutor",
        clickmode="event+select",
        dragmode=False,
        height=640,
    )
    return fig


def figure_to_json(fig: go.Figure) -> dict[str, Any]:
    return json.loads(fig.to_json())


def figure_json_text(fig: go.Figure) -> str:
    return json.dumps(figure_to_json(fig), ensure_ascii=False)
