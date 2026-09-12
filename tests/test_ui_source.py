from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
FIGURE = (ROOT / "src" / "phase_tutor" / "figure.py").read_text(encoding="utf-8")
TUTORIAL = (ROOT / "src" / "phase_tutor" / "tutorial.py").read_text(encoding="utf-8")


def test_streamlit_chrome_is_chinese():
    for label in (
        "选择相图",
        "导学路径",
        "拖动成分",
        "拖动温度",
        "冷却线跟随当前成分",
        "这个点在说什么",
        "沿冷却线往下走",
        "现在有哪些相",
        "结线与杠杆定律",
        "会穿过哪些相区、会不会碰到共晶/包晶/共析",
        "查看冷却线上的这一段",
        "相图导读",
        "回到当前图的默认点",
    ):
        assert label in APP, f"missing Chinese chrome: {label}"
    assert "page_title=\"相图导读\"" in APP or "page_title='相图导读'" in APP
    # no English-only primary chrome
    assert "Phase Diagram Tutor" not in APP
    assert "Select a diagram" not in APP
    assert "Temperature" not in APP.split("help=")[0]


def test_hover_covers_regions_and_named_lines():
    for word in ("相区", "液相线", "固相线", "溶解度曲线", "结线", "杠杆"):
        assert word in FIGURE
    assert "hovertemplate" in FIGURE
    assert "冷却线" in FIGURE


def test_tutorial_order_matches_criterion():
    order = [
        "相图是一张地图",
        "一个点怎么读",
        "结线与杠杆定律",
        "竖线就是冷却过程",
        "钢铁相图怎么用",
        "钛合金相图怎么用",
    ]
    positions = [TUTORIAL.index(title) for title in order]
    assert positions == sorted(positions)
    assert "fe_c" in TUTORIAL
    assert "ti_v" in TUTORIAL
    assert "组元" in TUTORIAL
    assert "奥氏体化" in TUTORIAL
    assert "β transus" in TUTORIAL


def test_app_is_the_tutor_not_hello():
    assert "build_figure" in APP
    assert "interpret(" in APP
    assert "walk_isopleth" in APP
    assert "Hello World" not in APP
    assert "st.plotly_chart" in APP
    assert "pd-titlebar" in APP or "pd-titlebar" in (ROOT / "src" / "phase_tutor" / "ui_shell.py").read_text(encoding="utf-8")
    assert "pd-workspace" in APP
    assert "pd-panel" in APP
    assert "stDeployButton" in (ROOT / "src" / "phase_tutor" / "ui_shell.py").read_text(encoding="utf-8")
    assert "stHeader" in (ROOT / "src" / "phase_tutor" / "ui_shell.py").read_text(encoding="utf-8")
    assert "Made with Streamlit" not in APP


def test_app_bootstraps_tutorial_step_zero():
    assert "initial_controls" in APP
    assert "1240.0" not in APP
    assert "get_step(0)" in TUTORIAL or "STEPS[0]" in TUTORIAL


def test_public_readme_and_license():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "CALPHAD" in readme
    assert "streamlit run" in readme
    assert "pytest" in readme
    assert "Fe–Fe₃C" in readme or "Fe-Fe" in readme
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in license_text
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".venv/" in gitignore
    assert "__pycache__/" in gitignore


def test_first_screen_answers_are_not_only_in_expander():
    phases_at = APP.index("现在有哪些相")
    expander_at = APP.index("导学说明（可收起，不遮挡相图）")
    assert phases_at < expander_at
    lever_at = APP.index("结线与杠杆定律")
    cooling_at = APP.index("会穿过哪些相区、会不会碰到共晶/包晶/共析")
    assert lever_at < expander_at
    assert cooling_at < expander_at
    assert "first_screen_answers" in APP
    assert "查看冷却线上的这一段" in APP
