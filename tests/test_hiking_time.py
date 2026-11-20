import pytest

from routes.hiking_time import estimated_duration_min


@pytest.mark.parametrize(
    "distance, elevation_gain_m, expected",
    [
        (12, 600, 240),   # 3 h flat, 2 h ascent -> 3 h + 1 h
        (10, 0, 150),     # 2.5 h flat only
        (4, 900, 210),    # 1 h flat, 3 h ascent -> 3 h + 0.5 h
        (8.5, 650, 195),  # 2.167 h + 1.0625 h = 193.75 min, rounded to 5
    ],
)
def test_estimated_duration(distance, elevation_gain_m, expected):
    assert estimated_duration_min(distance, elevation_gain_m) == expected
