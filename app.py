"""相图导读：中文 Streamlit 入口。解释器与作图都在 phase_tutor 库里。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
src = ROOT / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

import streamlit as st

from phase_tutor.diagrams.registry import all_diagrams, get_diagram
from phase_tutor.figure import build_figure, point_from_plotly_select
from phase_tutor.interpreter import interpret, walk_isopleth
from phase_tutor.readout import (
    cooling_jump_temperature,
    cooling_step_labels,
    current_cooling_index,
    first_screen_answers,
    format_isopleth_text,
    format_readout_text,
)
from phase_tutor.tutorial import STEPS, get_step, initial_controls
from phase_tutor.ui_shell import SHELL_CSS, titlebar_html

st.set_page_config(
    page_title="相图导读",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": "相图导读"},
)
st.markdown(SHELL_CSS, unsafe_allow_html=True)


def _init_state() -> None:
    if "diagram_id" not in st.session_state:
        for key, value in initial_controls().items():
            st.session_state[key] = value
    pending_step = st.session_state.pop("pending_step", None)
    if pending_step is not None:
        _apply_step(int(pending_step))
    if "diagram_select" not in st.session_state:
        st.session_state.diagram_select = get_diagram(st.session_state.diagram_id).title_zh
    if "tutorial_select" not in st.session_state:
        st.session_state.tutorial_select = get_step(int(st.session_state.tutorial_idx)).title_zh
    pending = st.session_state.pop("pending_point", None)
    if pending is not None:
        st.session_state.x = float(pending[0])
        st.session_state.T = float(pending[1])
        if st.session_state.follow:
            st.session_state.iso_x = float(pending[0])
    pending_t = st.session_state.pop("pending_T", None)
    if pending_t is not None:
        st.session_state.T = float(pending_t)


def _apply_diagram_defaults(diagram_id: str) -> None:
    d = get_diagram(diagram_id)
    st.session_state.diagram_id = diagram_id
    st.session_state.x = d.default_x
    st.session_state.T = d.default_T
    st.session_state.iso_x = d.default_x


def _apply_step(idx: int) -> None:
    step = get_step(idx)
    st.session_state.tutorial_idx = idx
    st.session_state.diagram_id = step.diagram_id
    st.session_state.x = step.x
    st.session_state.T = step.T
    st.session_state.iso_x = step.isopleth_x
    st.session_state.follow = True
    st.session_state.diagram_select = get_diagram(step.diagram_id).title_zh
    st.session_state.tutorial_select = step.title_zh


def _fraction_bar(interp) -> str:
    if interp.on_invariant or not interp.fractions:
        return "<div class='pd-note'>三相点没有唯一的杠杆分割。</div>"
    palette = ["#b9d7ee", "#f4c6c6", "#d4c4ec", "#b8e2d4", "#e7c9a4", "#f7e3a8"]
    parts = []
    for i, (phase, frac) in enumerate(interp.fractions.items()):
        pct = max(frac * 100.0, 0.0)
        if pct < 0.3:
            continue
        parts.append(
            f"<div style='width:{pct:.3f}%;background:{palette[i % len(palette)]}'>"
            f"{phase} {pct:.1f}%</div>"
        )
    if not parts:
        return ""
    return "<div class='pd-bar'>" + "".join(parts) + "</div>"


def _cooling_list_html(steps, T: float) -> str:
    labels = cooling_step_labels(steps)
    cur = current_cooling_index(steps, T)
    items = []
    for i, label in enumerate(labels):
        cls = "pd-cool-now" if i == cur else "pd-cool"
        tag = " ← 你在这里" if i == cur else ""
        items.append(f"<div class='{cls}'>{label}{tag}</div>")
    return "".join(items) if items else "<div class='pd-note'>这条冷却线没有穿过相区。</div>"


_init_state()
st.markdown(titlebar_html(), unsafe_allow_html=True)

diagrams = all_diagrams()
titles = [d.title_zh for d in diagrams]
ids = [d.id for d in diagrams]
step_titles = [s.title_zh for s in STEPS]

st.markdown('<div class="pd-toolbar-pad">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.5, 1.7, 1.1])
with c1:
    picked = st.selectbox("选择相图", titles, key="diagram_select")
    new_id = ids[titles.index(picked)]
    if new_id != st.session_state.diagram_id:
        _apply_diagram_defaults(new_id)
        st.rerun()
with c2:
    chosen_step = st.selectbox("导学路径（同一套解释器）", step_titles, key="tutorial_select")
    new_idx = step_titles.index(chosen_step)
    if new_idx != st.session_state.tutorial_idx:
        st.session_state.pending_step = new_idx
        st.rerun()
with c3:
    st.checkbox("冷却线跟随当前成分", key="follow")
    if st.button("回到当前图的默认点", width="stretch"):
        _apply_diagram_defaults(st.session_state.diagram_id)
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

diagram = get_diagram(st.session_state.diagram_id)
if st.session_state.follow:
    st.session_state.iso_x = float(st.session_state.x)
x = float(st.session_state.x)
T = float(st.session_state.T)
iso_x = float(st.session_state.iso_x)
interp = interpret(diagram, x, T)
iso_steps = walk_isopleth(diagram, iso_x)
answers = first_screen_answers(interp, iso_steps, iso_x)
fig = build_figure(diagram, x, T, isopleth_x=iso_x, interp=interp)
step = get_step(st.session_state.tutorial_idx)
cool_labels = cooling_step_labels(iso_steps)
cool_idx = current_cooling_index(iso_steps, T)
if cool_labels:
    cool_idx = min(max(cool_idx, 0), len(cool_labels) - 1)

st.markdown('<div class="pd-workspace">', unsafe_allow_html=True)
plot_col, inspect_col = st.columns([1.72, 1.0], gap="small")
with plot_col:
    st.markdown(
        f'<div class="pd-panel"><p class="pd-panel-h">相图 · {diagram.title_zh}</p><div class="pd-panel-b">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="pd-hint">在相区内部点一下放置当前点（不会吸到相界顶点）。精细移动用图下坐标条。长说明在右侧。</p>',
        unsafe_allow_html=True,
    )
    event = st.plotly_chart(
        fig,
        width="stretch",
        on_select="rerun",
        selection_mode="points",
        key="phase_plot",
        config={
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d", "pan2d", "autoScale2d"],
            "scrollZoom": False,
        },
    )
    try:
        points = event.selection.points if event is not None else []
    except Exception:
        points = []
    picked = point_from_plotly_select(points, fig)
    if picked is not None:
        px, py = picked
        px = min(max(px, diagram.x_min), diagram.x_max)
        py = min(max(py, diagram.t_min), diagram.t_max)
        if abs(px - x) > 1e-6 or abs(py - T) > 1e-6:
            st.session_state.pending_point = (px, py)
            st.rerun()
    st.markdown('<div class="pd-status-pad" style="padding:8px 0 0 0;background:transparent;border:0">', unsafe_allow_html=True)
    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        st.slider(
            "拖动成分",
            min_value=float(diagram.x_min),
            max_value=float(diagram.x_max),
            step=float((diagram.x_max - diagram.x_min) / 400.0),
            key="x",
            help="横轴。与图上当前点是同一套坐标。",
        )
    with ctrl2:
        st.slider(
            "拖动温度",
            min_value=float(diagram.t_min),
            max_value=float(diagram.t_max),
            step=float((diagram.t_max - diagram.t_min) / 400.0),
            key="T",
            help="纵轴。与图上当前点是同一套坐标。",
        )
    with ctrl3:
        if st.session_state.follow:
            st.session_state.iso_x = float(st.session_state.x)
            st.slider(
                "冷却线成分（当前跟随）",
                min_value=float(diagram.x_min),
                max_value=float(diagram.x_max),
                value=float(st.session_state.iso_x),
                step=float((diagram.x_max - diagram.x_min) / 400.0),
                disabled=True,
                help="竖线：成分固定，温度从高到低。",
            )
        else:
            st.slider(
                "拖动冷却线",
                min_value=float(diagram.x_min),
                max_value=float(diagram.x_max),
                step=float((diagram.x_max - diagram.x_min) / 400.0),
                key="iso_x",
                help="竖线：成分固定，温度从高到低。",
            )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pd-note'>{diagram.source_note_zh}</div></div></div>", unsafe_allow_html=True)

with inspect_col:
    st.markdown(
        '<div class="pd-panel"><p class="pd-panel-h">这个点在说什么</p><div class="pd-panel-b">',
        unsafe_allow_html=True,
    )
    st.markdown("<p class='pd-q'>现在有哪些相</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='pd-big'>{interp.field_name_zh}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='pd-ans'>{answers['phases']}</p>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='pd-kv'><span>成分</span><b>{x:.4g}　{diagram.x_label_zh}</b></div>"
        f"<div class='pd-kv'><span>温度</span><b>{T:.1f} °C</b></div>"
        f"<div class='pd-kv'><span>相律</span><b>C={interp.C}　P={interp.P}　F={interp.F}</b></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<p class='pd-q' style='margin-top:12px'>结线与杠杆定律</p>", unsafe_allow_html=True)
    st.markdown(_fraction_bar(interp), unsafe_allow_html=True)
    st.markdown(f"<p class='pd-ans'>{answers['lever']}</p>", unsafe_allow_html=True)
    if interp.practical_zh:
        st.markdown(f"<p class='pd-note'>{interp.practical_zh}</p>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="pd-panel" style="margin-top:8px"><p class="pd-panel-h">沿冷却线往下走</p><div class="pd-panel-b">',
        unsafe_allow_html=True,
    )
    st.markdown("<p class='pd-q'>会穿过哪些相区、会不会碰到共晶/包晶/共析</p>", unsafe_allow_html=True)
    if cool_labels:
        jumped = st.selectbox("查看冷却线上的这一段", cool_labels, index=cool_idx)
        jump_i = cool_labels.index(jumped)
        if jump_i != cool_idx:
            st.session_state.pending_T = cooling_jump_temperature(
                iso_steps, jump_i, diagram.t_min
            )
            st.rerun()
    st.markdown(_cooling_list_html(iso_steps, T), unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    with st.expander("导学说明（可收起，不遮挡相图）", expanded=False):
        st.markdown(f"**{step.title_zh}**  ·  {step.takeaway_zh}")
        st.markdown(step.body_md)
    with st.expander("完整文字读出（便于复制）"):
        st.text(format_readout_text(interp) + "\n\n" + format_isopleth_text(iso_steps, iso_x))

st.markdown(
    "<div class='pd-note' style='padding:0 4px 8px 4px'>这是教学工具：几何拓扑正确，用来建立「点 / 结线 / 竖线」三件套，不是 Thermo-Calc。"
    "三元相图、TTT/CCT、商业牌号精确截面不在本项目范围内。</div></div>",
    unsafe_allow_html=True,
)
