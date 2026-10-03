from manager.growth_kpis import calculate_conversion_rate, normalize_kpi_snapshot


def test_conversion_rate():
    assert calculate_conversion_rate(100, 7) == 7.0
    assert calculate_conversion_rate(0, 3) == 0.0


def test_snapshot_marks_unobserved_values():
    result = normalize_kpi_snapshot({"leads": 10, "customers": 2})

    assert result["leads"]["observed"] is True
    assert result["traffic"]["observed"] is False
    assert result["conversion_rate"]["value"] == 20.0
    assert result["conversion_rate"]["source"] == "derived"
