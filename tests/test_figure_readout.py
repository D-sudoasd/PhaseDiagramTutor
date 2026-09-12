from __future__ import annotations

import json

import pytest

from phase_tutor.diagrams.registry import get_diagram
from phase_tutor.figure import (
    HIT_LAYER_NAME,
    build_figure,
    figure_to_json,
    lever_label_texts,
    nearest_hit_point,
    point_from_plotly_select,
)
from phase_tutor.interpreter import interpret, walk_isopleth
from phase_tutor.readout import first_screen_answers, format_readout_text
from phase_tutor.tutorial import STEPS, get_step, initial_controls


REQUIRED_CN = ("相区", "液相线", "固相线", "结线", "杠杆")


def _flatten(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def test_figure_and_readout_fe_c_and_ti_two_phase():
    cases = {
        "fe_c": (0.40, 800.0),
        "ti_v": (8.0, 600.0),
    }
    for diagram_id, (x, T) in cases.items():
        diagram = get_diagram(diagram_id)
        interp = interpret(diagram, x, T)
        assert interp.tie_line is not None
        fig = build_figure(diagram, x, T, isopleth_x=x, interp=interp)
        payload = figure_to_json(fig)
        blob = _flatten(payload)
        for word in REQUIRED_CN:
            assert word in blob, f"{diagram_id} figure missing {word}"
        names = [t.get("name", "") for t in payload["data"]]
        assert any("结线" in n for n in names)
        assert any(n == "杠杆" for n in names)
        assert any(n and ("相" in n or "+" in n or n.startswith("L") or "α" in n or "β" in n or "γ" in n) for n in names)
        labels = lever_label_texts(interp)
        assert labels is not None
        for caption in labels:
            assert "杠杆" in caption or "支点" in caption
            assert caption.replace("\n", " ") in blob or caption.split("\n")[0] in blob
        for frac in interp.tie_line.left_fraction, interp.tie_line.right_fraction:
            assert f"{frac:.3f}" in blob
            assert f"{frac * 100:.1f}%" in blob
        anns = payload.get("layout", {}).get("annotations") or []
        assert len(anns) >= 3
        xs = [float(a["x"]) for a in anns]
        assert any(abs(v - interp.tie_line.left[0]) < 1e-6 for v in xs)
        assert any(abs(v - interp.tie_line.right[0]) < 1e-6 for v in xs)
        from phase_tutor.geometry import point_in_polygon
        from phase_tutor.figure import HIT_LAYER_NAME

        names = [t.get("name", "") for t in payload["data"]]
        assert HIT_LAYER_NAME in names
        labeled = 0
        for field in diagram.fields:
            hits = [
                a
                for a in anns
                if str(a.get("text", "")) == field.name_zh
                and point_in_polygon(float(a["x"]), float(a["y"]), field.polygon)
            ]
            if hits:
                labeled += 1
        assert labeled >= 3, f"{diagram_id} field labels inside polygons: {labeled}"

        text = format_readout_text(interp)
        assert interp.phases
        for phase in interp.phases:
            assert phase in text
        for frac in interp.fractions.values():
            assert f"{frac:.4f}" in text

        answers = first_screen_answers(interp, walk_isopleth(diagram, x), x)
        assert interp.phases[0] in answers["phases"]
        assert "杠杆" in answers["lever"] or "结线" in answers["lever"]
        assert answers["cooling"]


def test_cooling_jump_temperature_lands_inside_field():
    from phase_tutor.readout import cooling_jump_temperature, cooling_step_labels

    diagram = get_diagram("pb_sn")
    steps = walk_isopleth(diagram, 40.0)
    labels = cooling_step_labels(steps)
    idx = next(
        i
        for i, (lab, step) in enumerate(zip(labels, steps))
        if step.kind == "field" and step.field_id == "alpha_beta"
    )
    T = cooling_jump_temperature(steps, idx, diagram.t_min)
    result = interpret("pb_sn", 40.0, T)
    assert not result.on_invariant
    assert result.field_id == "alpha_beta"

    diagram = get_diagram("fe_c")
    steps = walk_isopleth(diagram, 0.40)
    labels = cooling_step_labels(steps)
    idx = next(
        i
        for i, (lab, step) in enumerate(zip(labels, steps))
        if step.kind == "field" and step.field_id == "L_gamma"
    )
    T = cooling_jump_temperature(steps, idx, diagram.t_min)
    result = interpret("fe_c", 0.40, T)
    assert not result.on_invariant
    assert result.field_id == "L_gamma"


def test_cooling_summary_does_not_glue_reaction_arrows():
    diagram = get_diagram("fe_c")
    interp = interpret(diagram, 0.40, 800.0)
    text = first_screen_answers(interp, walk_isopleth(diagram, 0.40), 0.40)["cooling"]
    assert "；" in text
    assert "L + δ → γ" in text
    assert "γ → α + Fe₃C" in text
    assert "→ 1495" not in text
    assert "→ 727" not in text


def test_tutorial_steps_drive_same_interpreter():
    assert [s.id for s in STEPS] == ["what", "read_point", "lever", "isopleth", "steel", "titanium"]
    for i, step in enumerate(STEPS):
        loaded = get_step(i)
        assert loaded.title_zh == step.title_zh
        result = interpret(step.diagram_id, step.x, step.T)
        assert result.diagram_id == step.diagram_id
        assert result.location_reading_zh
        text = format_readout_text(result)
        assert "【当前位置】" in text


def test_beginner_path_initial_point_is_step_zero_liquid():
    step = STEPS[0]
    boot = initial_controls()
    assert boot["diagram_id"] == step.diagram_id
    assert boot["x"] == step.x
    assert boot["T"] == step.T
    assert boot["iso_x"] == step.isopleth_x
    assert boot["tutorial_idx"] == 0
    result = interpret(step.diagram_id, step.x, step.T)
    assert result.phases == ("L",)
    assert result.fractions["L"] == pytest.approx(1.0)
    assert result.field_id == "L"
    assert result.T == pytest.approx(1400.0)
    assert result.x == pytest.approx(50.0)


def test_steel_and_titanium_are_selectable():
    from phase_tutor.diagrams.registry import list_diagrams

    listed = list_diagrams()
    ids = [row[0] for row in listed]
    titles = " ".join(row[1] for row in listed)
    assert "fe_c" in ids
    assert "ti_v" in ids
    assert "钢铁" in titles or "Fe" in titles
    assert "钛" in titles


def test_hit_layer_does_not_snap_to_field_vertices():
    diagram = get_diagram("fe_c")
    hx, hT = nearest_hit_point(diagram, 0.40, 800.0)
    verts = {(round(p[0], 8), round(p[1], 8)) for f in diagram.fields for p in f.polygon}
    assert (round(hx, 8), round(hT, 8)) not in verts
    result = interpret(diagram, hx, hT)
    assert result.field_id == "alpha_gamma"

    fig = build_figure(diagram, 0.40, 800.0)
    hit_idx = next(i for i, t in enumerate(fig.data) if t.name == HIT_LAYER_NAME)
    fake_vertex = {"curve_number": 0, "x": diagram.fields[0].polygon[0][0], "y": diagram.fields[0].polygon[0][1]}
    assert point_from_plotly_select([fake_vertex], fig) is None
    hit = {"curve_number": hit_idx, "x": hx, "y": hT}
    assert point_from_plotly_select([hit], fig) == pytest.approx((hx, hT))
