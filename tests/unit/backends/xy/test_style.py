from __future__ import annotations

from plotmux.backends.xy.style import rgba_to_xy
from plotmux.testing.fixtures import xy_available


@xy_available
def test_rgba_to_xy_opaque() -> None:
    assert rgba_to_xy((1.0, 0.0, 0.0, 1.0)) == "rgba(255, 0, 0, 1.0)"


@xy_available
def test_rgba_to_xy_transparent() -> None:
    assert rgba_to_xy((0.0, 0.0, 0.0, 0.0)) == "rgba(0, 0, 0, 0.0)"


@xy_available
def test_rgba_to_xy_rounding() -> None:
    assert rgba_to_xy((0.5, 0.5, 0.5, 0.5)) == "rgba(128, 128, 128, 0.5)"
