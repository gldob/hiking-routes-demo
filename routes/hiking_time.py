"""Estimated walking time following DIN 33466.

A hiker covers 4 km per hour on the flat and 300 m of ascent per hour.
The total time is the larger of the two partial times plus half of the
smaller one. The result is rounded to the nearest 5 minutes.
"""

import math

KM_PER_HOUR = 4.0
ASCENT_M_PER_HOUR = 300.0


def estimated_duration_min(distance_km, elevation_gain_m):
    horizontal = distance_km / KM_PER_HOUR
    vertical = elevation_gain_m / ASCENT_M_PER_HOUR
    hours = max(horizontal, vertical) + min(horizontal, vertical) / 2
    return int(math.floor(hours * 60 / 5 + 0.5) * 5)
