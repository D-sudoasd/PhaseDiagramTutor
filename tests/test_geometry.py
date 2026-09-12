from phase_tutor.geometry import point_in_polygon, point_on_segment


def test_degenerate_segment_is_not_on_every_point():
    assert point_on_segment(50.0, 1100.0, 100.0, 1455.0, 100.0, 1455.0) is False


def test_liquid_polygon_does_not_swallow_solid_region():
    # Above liquidus should be inside; well below should be outside.
    liquid = (
        (0.0, 1550.0),
        (100.0, 1550.0),
        (100.0, 1455.0),
        (100.0, 1455.0),  # duplicate vertex, as some builders emit
        (50.0, 1282.0),
        (0.0, 1085.0),
        (0.0, 1550.0),
    )
    assert point_in_polygon(50.0, 1500.0, liquid) is True
    assert point_in_polygon(50.0, 1100.0, liquid) is False
