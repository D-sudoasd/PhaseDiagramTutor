"""相图导读：中文 Streamlit 入口。解释器与作图都在 phase_tutor 库里。"""

from __future__ import annotations

import sys
from html import escape
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
from phase_tutor.ui_shell import (
    SHELL_CSS,
    cooling_timeline_html,
    coord_hud_html,
    fraction_bar_html,
    freedom_pills_html,
    phase_chips_html,
    phase_table_html,
    statusbar_html,
    titlebar_html,
    tutorial_stepper_html,
)

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
    if "plot_rev" not in st.session_state:
        st.session_state.plot_rev = 0
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


def _bump_view() -> None:
    st.session_state.plot_rev = int(st.session_state.get("plot_rev", 0)) + 1


def _apply_diagram_defaults(diagram_id: str) -> None:
    d = get_diagram(diagram_id)
    st.session_state.diagram_id = diagram_id
    st.session_state.x = d.default_x
    st.session_state.T = d.default_T
    st.session_state.iso_x = d.default_x
    _bump_view()


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
    _bump_view()


def _queue_point(px: float, py: float, x_min: float, x_max: float, t_min: float, t_max: float) -> None:
    st.session_state.pending_point = (
        min(max(float(px), x_min), x_max),
        min(max(float(py), t_min), t_max),
    )
    st.rerun()


_init_state()

diagrams = all_diagrams()
titles = [d.title_zh for d in diagrams]
ids = [d.id for d in diagrams]
step_titles = [s.title_zh for s in STEPS]
tut_idx = int(st.session_state.tutorial_idx)
st.markdown(titlebar_html(get_diagram(st.session_state.diagram_id).title_zh), unsafe_allow_html=True)

st.markdown('<div class="pd-toolbar-pad">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.35, 1.85, 1.35], gap="small", vertical_alignment="bottom")
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
    st.checkbox("冷却线跟随当前成分", key="follow", help="竖线始终对准当前点的成分。")
    if st.button(
        "回到当前图的默认点",
        key="reset_point",
        shortcut="Home",
        icon=":material/restart_alt:",
        width="stretch",
        help="复位到该相图的默认点并重置视图（Home）",
    ):
        _apply_diagram_defaults(st.session_state.diagram_id)
        st.rerun()
nav_l, nav_mid, nav_r = st.columns([0.9, 2.4, 0.9], vertical_alignment="center")
with nav_l:
    if st.button(
        "上一步",
        key="tut_prev",
        shortcut="PageUp",
        icon=":material/chevron_left:",
        disabled=tut_idx <= 0,
        width="stretch",
        help="导学路径上一步（PageUp）",
    ):
        st.session_state.pending_step = tut_idx - 1
        st.rerun()
with nav_mid:
    st.markdown(
        tutorial_stepper_html(tut_idx, len(STEPS), get_step(tut_idx).title_zh),
        unsafe_allow_html=True,
    )
with nav_r:
    if st.button(
        "下一步",
        key="tut_next",
        shortcut="PageDown",
        icon=":material/chevron_right:",
        type="primary",
        disabled=tut_idx >= len(STEPS) - 1,
        width="stretch",
        help="导学路径下一步（PageDown）",
    ):
        st.session_state.pending_step = tut_idx + 1
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
fig = build_figure(
    diagram,
    x,
    T,
    isopleth_x=iso_x,
    interp=interp,
    uirevision=str(st.session_state.plot_rev),
)
step = get_step(st.session_state.tutorial_idx)
cool_labels = cooling_step_labels(iso_steps)
cool_idx = current_cooling_index(iso_steps, T)
if cool_labels:
    cool_idx = min(max(cool_idx, 0), len(cool_labels) - 1)

dx = (diagram.x_max - diagram.x_min) / 100.0
dT = (diagram.t_max - diagram.t_min) / 100.0
readout_text = format_readout_text(interp) + "\n\n" + format_isopleth_text(iso_steps, iso_x)

st.markdown('<div class="pd-workspace">', unsafe_allow_html=True)
plot_col, inspect_col = st.columns([1.72, 1.0], gap="small")
with plot_col:
    with st.container(border=True):
        st.markdown(
            f'<div class="pd-panel"><p class="pd-panel-h">相图 · {escape(diagram.title_zh)}'
            f"{coord_hud_html(x, T, interp.field_name_zh, diagram.x_label_zh)}</p><div class='pd-panel-b'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="pd-hint">在相区内部点一下放置当前点（不会吸到相界顶点）。'
            "精细移动用图下坐标条或方向键。长说明在右侧。</p>",
            unsafe_allow_html=True,
        )
        event = st.plotly_chart(
            fig,
            width="stretch",
            on_select="rerun",
            selection_mode="points",
            key="phase_plot",
            theme=None,
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                "displayModeBar": False,
                "scrollZoom": False,
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": f"{diagram.id}-phase-diagram",
                    "scale": 2,
                },
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
        st.markdown('<div class="pd-status-pad">', unsafe_allow_html=True)
        ctrl1, ctrl2, ctrl3 = st.columns(3)
        with ctrl1:
            st.slider(
                "拖动成分",
                min_value=float(diagram.x_min),
                max_value=float(diagram.x_max),
                step=float((diagram.x_max - diagram.x_min) / 400.0),
                key="x",
                format="%.3f",
                help="横轴。与图上当前点是同一套坐标。方向键 ← → 也可微调。",
            )
        with ctrl2:
            st.slider(
                "拖动温度",
                min_value=float(diagram.t_min),
                max_value=float(diagram.t_max),
                step=float((diagram.t_max - diagram.t_min) / 400.0),
                key="T",
                format="%.1f °C",
                help="纵轴。与图上当前点是同一套坐标。方向键 ↑ ↓ 也可微调。",
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
                    format="%.3f",
                    help="竖线：成分固定，温度从高到低。",
                )
            else:
                st.slider(
                    "拖动冷却线",
                    min_value=float(diagram.x_min),
                    max_value=float(diagram.x_max),
                    step=float((diagram.x_max - diagram.x_min) / 400.0),
                    key="iso_x",
                    format="%.3f",
                    help="竖线：成分固定，温度从高到低。",
                )
        n1, n2, n3, n4 = st.columns(4, gap="small")
        with n1:
            if st.button("成分 −", key="nudge_x_minus", shortcut="Left", type="tertiary", width="stretch"):
                _queue_point(x - dx, T, diagram.x_min, diagram.x_max, diagram.t_min, diagram.t_max)
        with n2:
            if st.button("成分 +", key="nudge_x_plus", shortcut="Right", type="tertiary", width="stretch"):
                _queue_point(x + dx, T, diagram.x_min, diagram.x_max, diagram.t_min, diagram.t_max)
        with n3:
            if st.button("温度 −", key="nudge_t_minus", shortcut="Down", type="tertiary", width="stretch"):
                _queue_point(x, T - dT, diagram.x_min, diagram.x_max, diagram.t_min, diagram.t_max)
        with n4:
            if st.button("温度 +", key="nudge_t_plus", shortcut="Up", type="tertiary", width="stretch"):
                _queue_point(x, T + dT, diagram.x_min, diagram.x_max, diagram.t_min, diagram.t_max)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pd-note'>{escape(diagram.source_note_zh)}</div></div></div>", unsafe_allow_html=True)

with inspect_col:
    with st.container(height=780):
        with st.container(border=True):
            st.markdown(
                '<div class="pd-panel"><p class="pd-panel-h">这个点在说什么</p><div class="pd-panel-b">',
                unsafe_allow_html=True,
            )
            st.markdown("<p class='pd-q'>现在有哪些相</p>", unsafe_allow_html=True)
            st.markdown(
                f"<p class='pd-big'>{escape(interp.field_name_zh)}</p>{phase_chips_html(interp)}",
                unsafe_allow_html=True,
            )
            st.markdown(f"<p class='pd-ans'>{escape(answers['phases'])}</p>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='pd-kv'><span>成分</span><b>{x:.4g}　{escape(diagram.x_label_zh)}</b></div>"
                f"<div class='pd-kv'><span>温度</span><b>{T:.1f} °C</b></div>",
                unsafe_allow_html=True,
            )
            st.markdown(freedom_pills_html(interp), unsafe_allow_html=True)
            st.markdown("<p class='pd-q' style='margin-top:12px'>结线与杠杆定律</p>", unsafe_allow_html=True)
            st.markdown(fraction_bar_html(interp), unsafe_allow_html=True)
            st.markdown(phase_table_html(interp), unsafe_allow_html=True)
            st.markdown(f"<p class='pd-ans'>{escape(answers['lever'])}</p>", unsafe_allow_html=True)
            if interp.practical_zh:
                st.markdown(f"<p class='pd-note'>{escape(interp.practical_zh)}</p>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

        with st.container(border=True):
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
            st.markdown(cooling_timeline_html(iso_steps, T), unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
        with st.expander("导学说明（可收起，不遮挡相图）", expanded=False, icon=":material/school:"):
            st.markdown(f"**{step.title_zh}**  ·  {step.takeaway_zh}")
            st.markdown(step.body_md)
        with st.expander("完整文字读出（便于复制）", icon=":material/notes:"):
            st.text(readout_text)
            st.download_button(
                "导出读出",
                data=readout_text.encode("utf-8"),
                file_name=f"{diagram.id}-readout.txt",
                mime="text/plain",
                icon=":material/download:",
                help="把当前点的中文读出存成文本。",
            )

st.markdown(
    "<div class='pd-note' style='padding:0 4px 8px 4px'>这是教学工具：几何拓扑正确，用来建立「点 / 结线 / 竖线」三件套，不是 Thermo-Calc。"
    "三元相图、TTT/CCT、商业牌号精确截面不在本项目范围内。</div></div>",
    unsafe_allow_html=True,
)
st.markdown(statusbar_html(diagram, interp, x, T, iso_x), unsafe_allow_html=True)
