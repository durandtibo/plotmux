from __future__ import annotations

import numpy as np

from plotmux.specs import BarSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.bar import render_bar

################################
#     Tests for render_bar     #
################################


@xy_available
def test_render_bar_returns_chart() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    chart = render_bar(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_bar_label() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), label="my-label")
    chart = render_bar(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_bar_no_color_uses_backend_default() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    chart = render_bar(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_bar_color() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), color="red")
    chart = render_bar(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_bar_width() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), width=0.3)
    chart = render_bar(spec)
    assert chart.children[0].props["width"] == 0.3


@xy_available
def test_render_bar_explicit_width_kwarg_not_overridden() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), width=0.3)
    # ``width`` passed explicitly as a kwarg takes precedence over
    # ``spec.width`` (``kwargs.setdefault("width", spec.width)`` in
    # ``render_bar``).
    chart = render_bar(spec, width=0.9)
    assert chart.children[0].props["width"] == 0.9
