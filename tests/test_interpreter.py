"""Gating tests: import the shipped interpreter, not a reimplementation."""

from __future__ import annotations

import pytest

from phase_tutor.diagrams.registry import all_diagrams, get_diagram
from phase_tutor.interpreter import interpret, walk_isopleth


def _assert_single_phase(diagram_id: str, x: float, T: float) -> None:
    result = interpret(diagram_id, x, T)
    assert not result.on_invariant
    assert len(result.phases) == 1
    phase = result.phases[0]
    assert result.fractions[phase] == pytest.approx(1.0)
    assert sum(result.fractions.values()) == pytest.approx(1.0)
    assert result.P == 1
    assert result.F == result.C - result.P + 1


def _assert_two_phase(diagram_id: str, x: float, T: float) -> None:
    diagram = get_diagram(diagram_id)
    result = interpret(diagram, x, T)
    assert not result.on_invariant
    assert len(result.phases) == 2
    assert result.tie_line is not None
    tl = result.tie_line
    assert tl.left[1] == pytest.approx(T)
    assert tl.right[1] == pytest.approx(T)
    assert tl.left[0] <= x + 1e-9
    assert tl.right[0] >= x - 1e-9
    assert 0.0 - 1e-9 <= tl.left_fraction <= 1.0 + 1e-9
    assert 0.0 - 1e-9 <= tl.right_fraction <= 1.0 + 1e-9
    assert tl.left_fraction + tl.right_fraction == pytest.approx(1.0, abs=1e-9)
    assert sum(result.fractions.values()) == pytest.approx(1.0, abs=1e-9)
    assert result.P == 2
    assert result.F == 1

    field = next(f for f in diagram.fields if f.id == result.field_id)
    from phase_tutor.geometry import x_at_T

    x_left_curve = x_at_T(field.left_curve, T)
    x_right_curve = x_at_T(field.right_curve, T)
    ends = sorted([x_left_curve, x_right_curve])
    assert tl.left[0] == pytest.approx(ends[0], abs=1e-6)
    assert tl.right[0] == pytest.approx(ends[1], abs=1e-6)

    left = interpret(diagram, tl.left[0], T)
    assert left.tie_line is not None
    assert left.tie_line.left_fraction == pytest.approx(1.0, abs=1e-5)
    assert left.tie_line.right_fraction == pytest.approx(0.0, abs=1e-5)

    right = interpret(diagram, tl.right[0], T)
    assert right.tie_line is not None
    assert right.tie_line.right_fraction == pytest.approx(1.0, abs=1e-5)
    assert right.tie_line.left_fraction == pytest.approx(0.0, abs=1e-5)


def test_every_builtin_system_has_single_and_two_phase_points():
    cases = {
        "cu_ni": {"single": (50.0, 1100.0), "two": (50.0, 1240.0)},
        "pb_sn": {"single": (5.0, 100.0), "two": (40.0, 100.0)},
        "peritectic": {"single": (8.0, 900.0), "two": (18.0, 1250.0)},
        "fe_c": {"single": (0.80, 1000.0), "two": (0.40, 800.0)},
        "ti_v": {"single": (1.0, 400.0), "two": (8.0, 600.0)},
    }
    ids = {d.id for d in all_diagrams()}
    assert set(cases) <= ids
    for diagram_id, pts in cases.items():
        _assert_single_phase(diagram_id, *pts["single"])
        _assert_two_phase(diagram_id, *pts["two"])


def test_fe_c_eutectoid_just_below_is_alpha_cementite_not_liquid():
    result = interpret("fe_c", 0.76, 720.0)
    assert "L" not in result.phases
    assert set(result.phases) == {"α", "Fe₃C"}
    assert result.field_id == "alpha_cem"
    assert not result.on_invariant


def test_fe_c_hypoeutectoid_steel_and_hypereutectic_cast_iron():
    steel = interpret("fe_c", 0.40, 800.0)
    assert set(steel.phases) == {"α", "γ"}
    assert steel.field_id == "alpha_gamma"
    assert "亚共析" in steel.practical_zh

    cast = interpret("fe_c", 5.0, 1000.0)
    assert set(cast.phases) == {"γ", "Fe₃C"}
    assert cast.field_id == "gamma_cem"
    assert "过共晶" in cast.practical_zh
    assert "铸铁" in cast.practical_zh


def test_isopleth_liquid_to_room_includes_fields_and_invariants():
    fe = walk_isopleth("fe_c", 0.40)
    temps = [s.temperature for s in fe]
    assert temps == sorted(temps, reverse=True)
    field_ids = [s.field_id for s in fe if s.kind == "field"]
    assert field_ids[0] == "L"
    assert "alpha_cem" in field_ids
    names = " ".join(s.name_zh + (s.formula_zh or "") for s in fe)
    assert "包晶" in names
    assert "共析" in names
    assert any(s.kind == "invariant" and s.formula_zh == "L + δ → γ" for s in fe)
    assert any(s.kind == "invariant" and s.formula_zh == "γ → α + Fe₃C" for s in fe)

    cast = walk_isopleth("fe_c", 5.0)
    cast_names = " ".join(s.name_zh + (s.formula_zh or "") for s in cast)
    assert "共晶" in cast_names
    assert "共析" in cast_names
    assert any(s.field_id == "L_cem" for s in cast if s.kind == "field")

    sn = walk_isopleth("pb_sn", 40.0)
    assert any(s.kind == "invariant" and "共晶" in s.name_zh for s in sn)
    assert [s.field_id for s in sn if s.kind == "field"][0] == "L"

    cu = walk_isopleth("cu_ni", 50.0)
    cu_fields = [s.field_id for s in cu if s.kind == "field"]
    assert cu_fields[0] == "L"
    assert "L_alpha" in cu_fields
    assert "alpha" in cu_fields
    assert all(s.kind == "field" for s in cu)

    ti = walk_isopleth("ti_v", 8.0)
    ti_fields = [s.field_id for s in ti if s.kind == "field"]
    assert ti_fields[0] == "L"
    assert "alpha_beta" in ti_fields


def test_phase_rule_and_chinese_reading_present():
    two = interpret("cu_ni", 50.0, 1240.0)
    assert "结线" in two.location_reading_zh or "结线" in two.lever_explain_zh
    assert "杠杆" in two.lever_explain_zh
    assert two.F == 1

    one = interpret("cu_ni", 50.0, 1100.0)
    assert one.F == 2
    assert "100%" in one.location_reading_zh or "单相" in one.location_reading_zh


def test_titanium_transus_language():
    result = interpret("ti_v", 8.0, 600.0)
    assert "β transus" in result.practical_zh or "transus" in result.practical_zh
    assert "α+β" in result.field_name_zh or "α + β" in result.field_name_zh


def test_pb_sn_tin_rich_beta_is_single_phase():
    """Sn-rich β used to sit in a hole of b_poly; interpret must succeed there."""
    for x, T in ((99.5, 100.0), (99.8, 50.0), (99.6, 150.0), (100.0, 100.0)):
        result = interpret("pb_sn", x, T)
        assert result.phases == ("β",), (x, T, result.field_id, result.phases)
        assert result.fractions["β"] == pytest.approx(1.0)
        assert not result.on_invariant


def test_interpret_succeeds_on_coarse_grid_for_every_diagram():
    misses: list[tuple[str, float, float]] = []
    for diagram in all_diagrams():
        nx, nt = 15, 15
        for i in range(nx):
            x = diagram.x_min + (diagram.x_max - diagram.x_min) * i / (nx - 1)
            for j in range(nt):
                T = diagram.t_min + (diagram.t_max - diagram.t_min) * j / (nt - 1)
                try:
                    result = interpret(diagram, x, T)
                except ValueError:
                    misses.append((diagram.id, x, T))
                    continue
                assert result.phases, (diagram.id, x, T)
                if result.on_invariant:
                    continue
                total = sum(result.fractions.values())
                assert total == pytest.approx(1.0, abs=1e-6), (diagram.id, x, T, result.fractions)
    assert misses == [], f"interpret() holes: {misses[:20]} (showing up to 20 of {len(misses)})"
