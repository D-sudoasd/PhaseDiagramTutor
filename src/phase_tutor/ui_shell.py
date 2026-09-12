"""App-owned workspace chrome. Tokens + CSS + inspector HTML; no phase-diagram logic."""

from __future__ import annotations

from html import escape

from .models import Diagram, Interpretation, IsoplethStep
from .readout import cooling_step_labels, current_cooling_index

PHASE_COLORS: dict[str, str] = {
    "L": "#d4a017",
    "α": "#3d7ab5",
    "β": "#c45c5c",
    "γ": "#6f57b8",
    "δ": "#2a9a74",
    "Fe₃C": "#b07a3a",
}

SHELL_CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap");

:root {
  --pd-bg: #c5ced6;
  --pd-workspace: #d5dce3;
  --pd-panel: #ffffff;
  --pd-bar: #0c1219;
  --pd-bar-2: #151c27;
  --pd-bar-text: #eef3f8;
  --pd-muted-on-bar: #9aabbd;
  --pd-accent: #d97834;
  --pd-accent-2: #3e7eaf;
  --pd-line: #c5ced8;
  --pd-line-2: #e4e9ee;
  --pd-text: #141a22;
  --pd-muted: #5a6573;
  --pd-ok: #1a7f5a;
  --pd-warn: #9a4b12;
  --pd-shadow: 0 1px 0 rgba(12,18,25,0.04), 0 10px 28px rgba(12,18,25,0.07);
  --pd-focus: 0 0 0 2px #ffffff, 0 0 0 4px rgba(217,120,52,0.55);
  --pd-font: "IBM Plex Sans", "Noto Sans SC", "Segoe UI", "PingFang SC", "Microsoft YaHei UI", sans-serif;
  --pd-mono: "IBM Plex Sans", "Noto Sans SC", ui-monospace, monospace;
}

html, body, [class*="css"], .stApp, .stMarkdown, .stMarkdown p,
button, input, textarea, select {
  font-family: var(--pd-font) !important;
}
.stApp { background: var(--pd-bg) !important; color: var(--pd-text); }
::selection { background: rgba(217,120,52,0.22); }

header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
div[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; height: 0; }
footer { visibility: hidden; height: 0; }
.stDeployButton, button[kind="header"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

.block-container, .stMainBlockContainer, [data-testid="stAppViewContainer"] > .main > div,
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"] {
  padding: 0 !important;
  max-width: 100% !important;
}
.stApp [data-testid="stVerticalBlock"] { gap: 0.42rem !important; }
.stApp [data-testid="stHorizontalBlock"] { gap: 0.55rem !important; align-items: stretch !important; }

/* —— window chrome —— */
.pd-titlebar {
  background: linear-gradient(180deg, var(--pd-bar) 0%, var(--pd-bar-2) 100%);
  color: var(--pd-bar-text);
  padding: 0 16px;
  height: 42px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 2px solid var(--pd-accent);
  position: sticky;
  top: 0;
  z-index: 40;
  box-shadow: 0 8px 18px rgba(12,18,25,0.18);
  user-select: none;
}
.pd-mark {
  font-size: 0.98rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  margin: 0;
}
.pd-sub { font-size: 0.75rem; color: var(--pd-muted-on-bar); margin: 0; }
.pd-title-split {
  width: 1px; height: 16px; background: #2a3544; flex: 0 0 1px;
}
.pd-live {
  font-size: 0.75rem;
  color: #d5e3f0;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
.pd-badge {
  margin-left: auto;
  font-size: 0.68rem;
  color: var(--pd-muted-on-bar);
  border: 1px solid #2c3a4d;
  padding: 3px 9px;
  border-radius: 3px;
  letter-spacing: 0.04em;
  background: rgba(255,255,255,0.03);
}

.pd-toolbar-pad {
  padding: 8px 14px 6px 14px;
  background: linear-gradient(180deg, #eef2f6 0%, #e4eaef 100%);
  border-bottom: 1px solid var(--pd-line);
  box-shadow: inset 0 1px 0 #ffffff;
}
.pd-workspace { padding: 10px 12px 8px 12px; background: var(--pd-workspace); }
.pd-status-pad { padding: 0; background: transparent; border: 0; }

[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--pd-panel) !important;
  border: 1px solid var(--pd-line) !important;
  border-radius: 3px !important;
  box-shadow: var(--pd-shadow) !important;
  overflow: hidden;
}
[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 0 10px 10px 10px !important; }

.pd-panel {
  background: var(--pd-panel);
  border: 1px solid var(--pd-line);
  box-shadow: var(--pd-shadow);
}
.pd-panel-h {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--pd-muted);
  background: linear-gradient(180deg, #f7f9fb 0%, #eef2f6 100%);
  border-bottom: 1px solid var(--pd-line);
  padding: 8px 12px;
  margin: 0 -10px 8px -10px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.pd-panel-h .pd-hud {
  margin-left: auto;
  font-weight: 500;
  letter-spacing: 0;
  color: var(--pd-text);
  font-variant-numeric: tabular-nums;
  font-size: 0.76rem;
}
.pd-panel-b { padding: 0; }
.pd-kv {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.38rem 0;
  border-bottom: 1px solid var(--pd-line-2);
  font-size: 0.86rem;
}
.pd-kv span { color: var(--pd-muted); }
.pd-kv b { color: var(--pd-text); font-variant-numeric: tabular-nums; font-weight: 600; }
.pd-bar {
  display: flex;
  height: 26px;
  overflow: hidden;
  border: 1px solid var(--pd-line);
  border-radius: 3px;
  margin: 0.4rem 0 0.45rem 0;
  background: #f4f6f8;
}
.pd-bar div {
  display: flex; align-items: center; justify-content: center;
  font-size: 0.72rem; color: #1b2430; white-space: nowrap; font-weight: 600;
}
.pd-legend {
  display: flex; flex-wrap: wrap; gap: 8px 12px;
  font-size: 0.72rem; color: var(--pd-muted); margin: 0 0 8px 0;
}
.pd-legend i {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  margin-right: 5px; vertical-align: 0;
}
.pd-chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 0.12rem 0.5rem 0.12rem 0.38rem;
  background: #f6f8fa; color: var(--pd-text);
  font-size: 0.74rem; margin: 0 0.28rem 0.28rem 0;
  border: 1px solid var(--pd-line); border-radius: 999px; font-weight: 600;
}
.pd-chip s {
  width: 8px; height: 8px; border-radius: 50%; display: inline-block;
  text-decoration: none; flex: 0 0 8px;
}
.pd-note { font-size: 0.75rem; color: var(--pd-muted); line-height: 1.5; margin-top: 0.45rem; }
.pd-warn { color: var(--pd-warn); }
.pd-hint { font-size: 0.75rem; color: var(--pd-muted); margin: 0 0 6px 0; line-height: 1.45; }
.pd-q {
  font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
  color: var(--pd-accent); margin: 10px 0 6px 0; text-transform: none;
}
.pd-big { font-size: 1.16rem; font-weight: 700; margin: 0 0 6px 0; color: var(--pd-text); letter-spacing: 0.01em; }
.pd-ans { font-size: 0.86rem; line-height: 1.55; margin: 0 0 8px 0; color: var(--pd-text); }
.pd-cool { font-size: 0.8rem; padding: 4px 8px 4px 0; color: var(--pd-muted); }
.pd-cool-now {
  font-size: 0.84rem; padding: 7px 10px;
  background: linear-gradient(90deg, #fff4ea 0%, #fff8f2 100%);
  border-left: 3px solid var(--pd-accent); color: var(--pd-text); font-weight: 650;
  border-radius: 0 3px 3px 0;
}

.pd-stepper { display: flex; align-items: center; gap: 6px; padding: 2px 2px 6px 2px; }
.pd-dot {
  width: 9px; height: 9px; border-radius: 50%;
  background: #c5ced8; border: 1px solid #b3bcc6;
}
.pd-dot.on { background: var(--pd-accent); border-color: var(--pd-accent); box-shadow: 0 0 0 3px rgba(217,120,52,0.18); }
.pd-dot.done { background: #2a9a74; border-color: #2a9a74; }
.pd-step-lab { font-size: 0.72rem; color: var(--pd-muted); margin-left: 6px; }

.pd-grid { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin: 4px 0 8px 0; }
.pd-grid th {
  text-align: left; font-size: 0.68rem; letter-spacing: 0.06em; color: var(--pd-muted);
  font-weight: 700; padding: 4px 6px; border-bottom: 1px solid var(--pd-line);
}
.pd-grid td {
  padding: 5px 6px; border-bottom: 1px solid var(--pd-line-2);
  font-variant-numeric: tabular-nums;
}
.pd-swatch { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }

.pd-badges { display: flex; gap: 6px; flex-wrap: wrap; margin: 6px 0 4px 0; }
.pd-pill {
  font-size: 0.72rem; font-weight: 650; font-variant-numeric: tabular-nums;
  border: 1px solid var(--pd-line); background: #f6f8fa;
  padding: 3px 8px; border-radius: 3px;
}

.pd-timeline { margin: 4px 0 0 2px; padding: 2px 0 2px 0; }
.pd-tl-item {
  display: grid; grid-template-columns: 14px 1fr; gap: 8px;
  position: relative; padding: 0 0 8px 0;
}
.pd-tl-item:last-child { padding-bottom: 0; }
.pd-tl-rail { position: relative; }
.pd-tl-rail::before {
  content: ""; position: absolute; left: 4px; top: 10px; bottom: -8px;
  width: 2px; background: #d5dde4;
}
.pd-tl-item:last-child .pd-tl-rail::before { display: none; }
.pd-tl-dot {
  width: 10px; height: 10px; border-radius: 50%; background: #c5ced8;
  border: 2px solid #fff; box-shadow: 0 0 0 1px #c5ced8; margin-top: 4px;
}
.pd-tl-item.is-now .pd-tl-dot {
  background: var(--pd-accent); box-shadow: 0 0 0 1px var(--pd-accent), 0 0 0 4px rgba(217,120,52,0.18);
}
.pd-tl-t { font-weight: 650; font-size: 0.82rem; color: var(--pd-text); font-variant-numeric: tabular-nums; }
.pd-tl-d { font-size: 0.74rem; color: var(--pd-muted); line-height: 1.4; margin-top: 1px; }

.pd-statusbar {
  position: sticky; bottom: 0; z-index: 30;
  display: flex; align-items: center; gap: 0;
  background: var(--pd-bar); color: #c9d6e2;
  font-size: 0.72rem; font-variant-numeric: tabular-nums;
  border-top: 1px solid #000; min-height: 26px;
  user-select: none;
}
.pd-sb-item {
  padding: 4px 12px; border-right: 1px solid #2a3544; white-space: nowrap;
}
.pd-sb-item b { color: #eef3f8; font-weight: 600; }
.pd-sb-keys { margin-left: auto; border-right: 0; color: #8a9aab; letter-spacing: 0.02em; }
.pd-sb-keys kbd {
  display: inline-block; border: 1px solid #2a3544; background: #1b2430;
  padding: 0 5px; border-radius: 3px; margin: 0 2px; color: #d5e3f0;
}

/* widgets */
div[data-testid="stSlider"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stCheckbox"] label,
.stButton button, [data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-tertiary"] {
  font-size: 0.8rem !important;
}
div[data-testid="stSelectbox"] > div { min-height: 0; }
[data-baseweb="select"] > div {
  background: #ffffff !important;
  border-color: var(--pd-line) !important;
  min-height: 36px !important;
  border-radius: 3px !important;
}
[data-baseweb="select"]:hover > div { border-color: #9aa8b6 !important; }
[data-baseweb="select"] input { font-size: 0.82rem !important; }

[data-baseweb="slider"] [role="slider"] {
  background: var(--pd-accent) !important;
  border: 2px solid #fff !important;
  box-shadow: 0 0 0 1px rgba(12,18,25,0.25), 0 1px 3px rgba(12,18,25,0.2) !important;
}
[data-baseweb="slider"] [role="slider"]:focus {
  box-shadow: var(--pd-focus) !important;
}
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
  font-variant-numeric: tabular-nums; font-size: 0.7rem; color: var(--pd-muted);
}

.stButton button,
[data-testid="stBaseButton-secondary"],
[data-testid="stDownloadButton"] button {
  border-radius: 3px !important;
  background: #1b2430 !important;
  color: #fff !important;
  border: 1px solid #0d141d !important;
  font-weight: 600 !important;
  transition: background 0.12s ease, transform 0.08s ease, box-shadow 0.12s ease !important;
}
.stButton button:hover,
[data-testid="stBaseButton-secondary"]:hover,
[data-testid="stDownloadButton"] button:hover {
  background: #273140 !important;
  box-shadow: 0 1px 0 rgba(255,255,255,0.08) inset, 0 2px 6px rgba(12,18,25,0.18) !important;
}
.stButton button:focus-visible,
[data-testid="stBaseButton-secondary"]:focus-visible,
[data-testid="stBaseButton-primary"]:focus-visible,
[data-testid="stBaseButton-tertiary"]:focus-visible {
  box-shadow: var(--pd-focus) !important;
}
[data-testid="stBaseButton-primary"] {
  background: var(--pd-accent) !important;
  border-color: #b45e20 !important;
  color: #fff !important;
}
[data-testid="stBaseButton-primary"]:hover { background: #e08942 !important; }
[data-testid="stBaseButton-tertiary"] {
  background: #ffffff !important;
  color: var(--pd-text) !important;
  border: 1px solid var(--pd-line) !important;
}
[data-testid="stBaseButton-tertiary"]:hover {
  background: #f4f7fa !important;
  border-color: #9aa8b6 !important;
}
[data-testid="stBaseButton-tertiary"]:disabled,
.stButton button:disabled {
  opacity: 0.45 !important; cursor: not-allowed !important;
}

div[data-testid="stCheckbox"] label { color: var(--pd-text) !important; }
div[data-testid="stExpander"] {
  background: var(--pd-panel);
  border: 1px solid var(--pd-line) !important;
  border-radius: 3px !important;
  box-shadow: var(--pd-shadow);
}
div[data-testid="stExpander"] details summary {
  font-size: 0.82rem !important; font-weight: 600 !important;
}
div[data-testid="stExpander"] details summary:hover { color: var(--pd-accent) !important; }
div[data-testid="stExpander"] details:focus-within { box-shadow: var(--pd-focus); }

.js-plotly-plot .modebar {
  top: 6px !important; right: 8px !important;
  background: rgba(255,255,255,0.92) !important;
  border: 1px solid var(--pd-line) !important;
  border-radius: 4px !important;
  padding: 1px 2px !important;
}
.js-plotly-plot .hoverlayer .hovertext { filter: none; }

kbd.pd-k {
  font-family: var(--pd-font);
  font-size: 0.68rem; border: 1px solid var(--pd-line); background: #fff;
  padding: 0 4px; border-radius: 3px; color: var(--pd-muted);
}

@media (max-width: 1100px) {
  .pd-sub, .pd-live { display: none; }
  .pd-sb-keys { display: none; }
}
</style>
"""


def _e(text: object) -> str:
    return escape(str(text))


def _phase_color(phase: str) -> str:
    return PHASE_COLORS.get(phase, "#7a8490")


def titlebar_html(diagram_title: str = "") -> str:
    live = f'<span class="pd-title-split"></span><p class="pd-live">{_e(diagram_title)}</p>' if diagram_title else ""
    return (
        '<div class="pd-titlebar">'
        '<p class="pd-mark">相图导读</p>'
        '<p class="pd-sub">T–x 相图工作台 · 读点 / 结线 / 冷却线</p>'
        f"{live}"
        '<span class="pd-badge">教学几何 · 非 CALPHAD</span>'
        "</div>"
    )


def tutorial_stepper_html(idx: int, n: int, title: str) -> str:
    dots = []
    for i in range(n):
        cls = "pd-dot"
        if i < idx:
            cls += " done"
        elif i == idx:
            cls += " on"
        dots.append(f'<span class="{cls}" title="第 {i + 1} 步"></span>')
    return (
        '<div class="pd-stepper">'
        + "".join(dots)
        + f'<span class="pd-step-lab">第 {idx + 1}/{n} 步 · {_e(title)}</span>'
        + "</div>"
    )


def coord_hud_html(x: float, T: float, field_name: str, x_label: str) -> str:
    return (
        f'<span class="pd-hud">{_e(x_label)} {x:.4g}'
        f"　{T:.1f} °C　{_e(field_name)}</span>"
    )


def phase_chips_html(interp: Interpretation) -> str:
    bits = []
    for phase in interp.phases:
        color = _phase_color(phase)
        bits.append(
            f'<span class="pd-chip"><s style="background:{color}"></s>{_e(phase)}</span>'
        )
    return "".join(bits)


def phase_table_html(interp: Interpretation) -> str:
    if interp.on_invariant:
        rows = []
        for phase, comp in interp.phase_compositions.items():
            color = _phase_color(phase)
            rows.append(
                "<tr>"
                f'<td><span class="pd-swatch" style="background:{color}"></span>{_e(phase)}</td>'
                f"<td>{comp:.4g}</td>"
                "<td>—</td>"
                "</tr>"
            )
        body = "".join(rows)
        note = '<p class="pd-note pd-warn">三相点没有唯一的杠杆分割。</p>'
        return (
            '<table class="pd-grid"><thead><tr><th>相</th><th>成分</th><th>质量分数</th></tr></thead>'
            f"<tbody>{body}</tbody></table>{note}"
        )
    rows = []
    for phase in interp.phases:
        frac = interp.fractions.get(phase, 0.0)
        comp = interp.phase_compositions.get(phase, interp.x)
        color = _phase_color(phase)
        rows.append(
            "<tr>"
            f'<td><span class="pd-swatch" style="background:{color}"></span>{_e(phase)}</td>'
            f"<td>{comp:.4g}</td>"
            f"<td>{frac * 100:.1f}%　({frac:.3f})</td>"
            "</tr>"
        )
    if not rows:
        return ""
    return (
        '<table class="pd-grid"><thead><tr><th>相</th><th>成分</th><th>质量分数</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def fraction_bar_html(interp: Interpretation) -> str:
    if interp.on_invariant or not interp.fractions:
        return "<div class='pd-note'>三相点没有唯一的杠杆分割。</div>"
    parts = []
    legend = []
    for phase, frac in interp.fractions.items():
        pct = max(frac * 100.0, 0.0)
        if pct < 0.3:
            continue
        color = _phase_color(phase)
        parts.append(
            f"<div style='width:{pct:.3f}%;background:{color}22;box-shadow:inset 0 0 0 1px {color}55'>"
            f"{_e(phase)} {pct:.1f}%</div>"
        )
        legend.append(
            f'<span><i style="background:{color}"></i>{_e(phase)} {pct:.1f}%</span>'
        )
    if not parts:
        return ""
    return (
        "<div class='pd-bar'>"
        + "".join(parts)
        + "</div><div class='pd-legend'>"
        + "".join(legend)
        + "</div>"
    )


def freedom_pills_html(interp: Interpretation) -> str:
    return (
        '<div class="pd-badges">'
        f'<span class="pd-pill">C = {interp.C}</span>'
        f'<span class="pd-pill">P = {interp.P}</span>'
        f'<span class="pd-pill">F = {interp.F}</span>'
        "</div>"
    )


def cooling_timeline_html(steps: list[IsoplethStep], T: float) -> str:
    labels = cooling_step_labels(steps)
    cur = current_cooling_index(steps, T)
    if not labels:
        return "<div class='pd-note'>这条冷却线没有穿过相区。</div>"
    items = []
    for i, (label, step) in enumerate(zip(labels, steps)):
        now = i == cur
        cls = "pd-tl-item is-now" if now else "pd-tl-item"
        extra = f'<div class="pd-tl-d">{_e(step.meaning_zh)}</div>' if now else ""
        here = '<div class="pd-tl-d">← 你在这里</div>' if now else ""
        items.append(
            f'<div class="{cls}">'
            f'<div class="pd-tl-rail"><div class="pd-tl-dot"></div></div>'
            f'<div><div class="pd-tl-t">{_e(label)}</div>{here}{extra}</div>'
            "</div>"
        )
    return '<div class="pd-timeline">' + "".join(items) + "</div>"


def statusbar_html(
    diagram: Diagram,
    interp: Interpretation,
    x: float,
    T: float,
    iso_x: float,
) -> str:
    phases = "、".join(interp.phases) if interp.phases else interp.field_name_zh
    return (
        '<div class="pd-statusbar">'
        f'<span class="pd-sb-item">{_e(diagram.title_zh)}</span>'
        f'<span class="pd-sb-item">{_e(diagram.x_label_zh)} <b>{x:.4g}</b></span>'
        f'<span class="pd-sb-item">T <b>{T:.1f} °C</b></span>'
        f'<span class="pd-sb-item">相 <b>{_e(phases)}</b></span>'
        f'<span class="pd-sb-item">C={interp.C}　P={interp.P}　F={interp.F}</span>'
        f'<span class="pd-sb-item">冷却线 x={iso_x:.4g}</span>'
        '<span class="pd-sb-item pd-sb-keys">'
        "<kbd>←</kbd><kbd>→</kbd>成分　"
        "<kbd>↑</kbd><kbd>↓</kbd>温度　"
        "<kbd>PgUp</kbd><kbd>PgDn</kbd>导学　"
        "<kbd>Home</kbd>复位"
        "</span>"
        "</div>"
    )
