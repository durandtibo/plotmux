from __future__ import annotations

import numpy as np

from plotmux.specs import LineSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.line import render_line


@xy_available
def test_render_line_returns_chart() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_line_label() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    chart = render_line(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_line_color() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color="red")
    chart = render_line(spec)
    assert isinstance(chart, Chart)
