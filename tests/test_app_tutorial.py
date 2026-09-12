"""AppTest: 导学路径 must move the keyed 选择相图 widget and the constitution point."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from phase_tutor.tutorial import STEPS

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"


def _tutorial_box(at: AppTest):
    for box in at.selectbox:
        if box.label == "导学路径（同一套解释器）":
            return box
    raise AssertionError(f"missing tutorial selectbox; labels={[b.label for b in at.selectbox]}")


def _cool_box(at: AppTest):
    for box in at.selectbox:
        if box.label == "查看冷却线上的这一段":
            return box
    raise AssertionError(f"missing cooling selectbox; labels={[b.label for b in at.selectbox]}")


def test_tutorial_step_4_and_5_move_diagram_and_point():
    at = AppTest.from_file(str(APP), default_timeout=30)
    at.run()
    assert not at.exception, at.exception

    step4 = STEPS[3]
    assert step4.diagram_id == "pb_sn"
    _tutorial_box(at).select(step4.title_zh).run()
    assert not at.exception, at.exception
    assert at.session_state["diagram_id"] == "pb_sn"
    assert at.session_state["x"] == pytest.approx(40.0)
    assert at.session_state["T"] == pytest.approx(220.0)
    assert at.session_state["tutorial_idx"] == 3
    assert "Pb–Sn" in str(at.session_state["diagram_select"]) or "共晶" in str(
        at.session_state["diagram_select"]
    )

    step5 = STEPS[4]
    assert step5.diagram_id == "fe_c"
    _tutorial_box(at).select(step5.title_zh).run()
    assert not at.exception, at.exception
    assert at.session_state["diagram_id"] == "fe_c"
    assert at.session_state["x"] == pytest.approx(0.40)
    assert at.session_state["T"] == pytest.approx(800.0)
    assert at.session_state["tutorial_idx"] == 4


def _field_cooling_label(diagram_id: str, x: float, field_id: str) -> str:
    from phase_tutor.interpreter import walk_isopleth
    from phase_tutor.readout import cooling_step_labels

    steps = walk_isopleth(diagram_id, x)
    labels = cooling_step_labels(steps)
    for lab, step in zip(labels, steps):
        if step.kind == "field" and step.field_id == field_id:
            return lab
    raise AssertionError(f"no field {field_id} on {diagram_id} x={x}: {labels}")


def test_cooling_segment_jump_is_not_the_adjacent_invariant():
    """Selecting α+β / L+γ must land inside that field, not on 共晶 / 包晶."""
    from phase_tutor.interpreter import interpret

    at = AppTest.from_file(str(APP), default_timeout=30)
    at.run()
    assert not at.exception, at.exception

    _tutorial_box(at).select(STEPS[3].title_zh).run()
    assert at.session_state["diagram_id"] == "pb_sn"
    sn_label = _field_cooling_label("pb_sn", 40.0, "alpha_beta")
    _cool_box(at).select(sn_label).run()
    assert not at.exception, at.exception
    sn = interpret("pb_sn", float(at.session_state["x"]), float(at.session_state["T"]))
    assert not sn.on_invariant
    assert set(sn.phases) == {"α", "β"}
    assert sn.field_id == "alpha_beta"

    _tutorial_box(at).select(STEPS[4].title_zh).run()
    assert at.session_state["diagram_id"] == "fe_c"
    fe_label = _field_cooling_label("fe_c", 0.40, "L_gamma")
    _cool_box(at).select(fe_label).run()
    assert not at.exception, at.exception
    steel = interpret("fe_c", float(at.session_state["x"]), float(at.session_state["T"]))
    assert not steel.on_invariant
    assert set(steel.phases) == {"L", "γ"}
    assert steel.field_id == "L_gamma"
