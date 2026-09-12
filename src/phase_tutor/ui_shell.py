"""App-owned workspace chrome. Tokens + CSS only; no phase-diagram logic."""

SHELL_CSS = """
<style>
:root {
  --pd-bg: #d8dee6;
  --pd-panel: #ffffff;
  --pd-bar: #121a26;
  --pd-bar-2: #1b2636;
  --pd-bar-text: #e8eef6;
  --pd-muted-on-bar: #9aa8b8;
  --pd-accent: #c45c26;
  --pd-line: #c3ccd6;
  --pd-text: #1b2430;
  --pd-muted: #5d6a78;
  --pd-ok: #1f6b4a;
  --pd-shadow: 0 1px 0 rgba(18,26,38,0.06), 0 8px 24px rgba(18,26,38,0.06);
}
html, body, [class*="css"], .stApp {
  font-family: "Segoe UI", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  color: var(--pd-text);
}
.stApp { background: var(--pd-bg) !important; }
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
div[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; height: 0; }
footer { visibility: hidden; height: 0; }
.stDeployButton, button[kind="header"] { display: none !important; }
.block-container, .stMainBlockContainer, [data-testid="stAppViewContainer"] > .main > div {
  padding-top: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  padding-bottom: 0 !important;
  max-width: 100% !important;
}
[data-testid="stAppViewBlockContainer"] {
  padding: 0 !important;
  max-width: 100% !important;
}

.pd-titlebar {
  background: linear-gradient(180deg, var(--pd-bar) 0%, var(--pd-bar-2) 100%);
  color: var(--pd-bar-text);
  padding: 10px 18px 8px 18px;
  display: flex;
  align-items: baseline;
  gap: 14px;
  border-bottom: 2px solid var(--pd-accent);
}
.pd-mark {
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0;
}
.pd-sub {
  font-size: 0.78rem;
  color: var(--pd-muted-on-bar);
  margin: 0;
}
.pd-badge {
  margin-left: auto;
  font-size: 0.72rem;
  color: var(--pd-muted-on-bar);
  border: 1px solid #2c3a4d;
  padding: 2px 8px;
  border-radius: 2px;
}

.pd-toolbar-pad { padding: 8px 14px 4px 14px; background: #eef2f6; border-bottom: 1px solid var(--pd-line); }
.pd-status-pad { padding: 2px 14px 8px 14px; background: #eef2f6; border-bottom: 1px solid var(--pd-line); }
.pd-workspace { padding: 10px 12px 12px 12px; }
.pd-panel {
  background: var(--pd-panel);
  border: 1px solid var(--pd-line);
  box-shadow: var(--pd-shadow);
}
.pd-panel-h {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: none;
  color: var(--pd-muted);
  background: #f4f6f8;
  border-bottom: 1px solid var(--pd-line);
  padding: 7px 12px;
  margin: 0;
}
.pd-panel-b { padding: 10px 12px 12px 12px; }
.pd-kv { display: flex; justify-content: space-between; gap: 0.75rem; padding: 0.32rem 0; border-bottom: 1px solid #eef1f4; font-size: 0.88rem; }
.pd-kv span { color: var(--pd-muted); }
.pd-kv b { color: var(--pd-text); font-variant-numeric: tabular-nums; }
.pd-reading { line-height: 1.65; color: var(--pd-text); font-size: 0.86rem; }
.pd-reading p { margin: 0 0 0.55rem 0; }
.pd-bar { display: flex; height: 22px; overflow: hidden; border: 1px solid var(--pd-line); margin: 0.45rem 0 0.7rem 0; }
.pd-bar div { display: flex; align-items: center; justify-content: center; font-size: 0.72rem; color: #1b2430; white-space: nowrap; }
.pd-chip { display: inline-block; padding: 0.08rem 0.45rem; background: #f3e6dc; color: #7a3d16; font-size: 0.72rem; margin-right: 0.3rem; border: 1px solid #e2c4ae; }
.pd-note { font-size: 0.75rem; color: var(--pd-muted); line-height: 1.5; margin-top: 0.45rem; }
.pd-timeline { border-left: 2px solid var(--pd-accent); margin: 0.25rem 0 0 0.2rem; padding-left: 0.75rem; }
.pd-t { font-weight: 650; color: var(--pd-text); font-size: 0.84rem; }
.pd-d { color: var(--pd-muted); font-size: 0.78rem; line-height: 1.4; margin-bottom: 0.55rem; }
.pd-hint { font-size: 0.75rem; color: var(--pd-muted); margin: 0 0 6px 0; }
.pd-q { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; color: var(--pd-accent); margin: 0 0 6px 0; }
.pd-big { font-size: 1.08rem; font-weight: 700; margin: 0 0 8px 0; color: var(--pd-text); }
.pd-ans { font-size: 0.86rem; line-height: 1.55; margin: 0 0 8px 0; color: var(--pd-text); }
.pd-cool { font-size: 0.8rem; padding: 3px 8px; color: var(--pd-muted); }
.pd-cool-now { font-size: 0.84rem; padding: 5px 8px; background: #fff4ea; border-left: 3px solid var(--pd-accent); color: var(--pd-text); font-weight: 650; }

div[data-testid="stSlider"] label, div[data-testid="stSelectbox"] label,
div[data-testid="stCheckbox"] label, .stButton button {
  font-size: 0.82rem !important;
}
.stButton button {
  border-radius: 2px !important;
  background: var(--pd-bar) !important;
  color: #fff !important;
  border: 1px solid #0d141d !important;
}
div[data-testid="stExpander"] {
  background: var(--pd-panel);
  border: 1px solid var(--pd-line);
}
</style>
"""


def titlebar_html() -> str:
    return (
        '<div class="pd-titlebar">'
        '<p class="pd-mark">相图导读</p>'
        '<p class="pd-sub">T–x 相图工作台 · 读点 / 结线 / 冷却线</p>'
        '<span class="pd-badge">教学几何 · 非 CALPHAD</span>'
        "</div>"
    )
