from __future__ import annotations

import numpy as np

from plotmux.specs import ScatterSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.scatter import render_scatter

####################################
#     Tests for render_scatter     #
####################################


@xy_available
def test_render_scatter_returns_chart() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_label() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    chart = render_scatter(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_no_color_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    chart = render_scatter(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_size() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), size=10.0)
    chart = render_scatter(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_no_size_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_explicit_size_kwarg_not_overridden() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), size=10.0)
    # ``size`` passed explicitly as a kwarg takes precedence over ``spec.size``
    # (``kwargs.setdefault("size", spec.size)`` in ``render_scatter``).
    chart = render_scatter(spec, size=99.0)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_alpha() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), alpha=0.5)
    chart = render_scatter(spec)
    assert chart.children[0].props["opacity"] == 0.5


@xy_available
def test_render_scatter_edgecolor() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), edgecolor="blue")
    chart = render_scatter(spec)
    assert chart.children[0].props["stroke"] is not None
    assert chart.children[0].props["stroke_width"] == 1.0


@xy_available
def test_render_scatter_no_edgecolor() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_scatter_marker() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), marker="square")
    chart = render_scatter(spec)
    assert chart.children[0].props["symbol"] == "square"


@xy_available
def test_render_scatter_no_marker_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert chart.children[0].props["symbol"] == "circle"


@xy_available
def test_render_scatter_fill_false_transparent_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", fill=False)
    chart = render_scatter(spec)
    assert chart.children[0].props["color"] == "rgba(0, 0, 0, 0)"


@xy_available
def test_render_scatter_fill_false_outline_uses_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", fill=False)
    chart = render_scatter(spec)
    assert chart.children[0].props["stroke"] == "rgba(255, 0, 0, 1.0)"
    assert chart.children[0].props["stroke_width"] == 1.0


@xy_available
def test_render_scatter_fill_false_outline_prefers_edgecolor() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", edgecolor="blue", fill=False)
    chart = render_scatter(spec)
    assert chart.children[0].props["stroke"] == "rgba(0, 0, 255, 1.0)"


@xy_available
def test_render_scatter_fill_none_or_true_keeps_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    chart = render_scatter(spec)
    assert chart.children[0].props["color"] == "rgba(255, 0, 0, 1.0)"
