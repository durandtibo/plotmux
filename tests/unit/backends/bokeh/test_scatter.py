from __future__ import annotations

import numpy as np

from plotmux.specs import ScatterSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.scatter import render_scatter

####################################
#     Tests for render_scatter     #
####################################


@bokeh_available
def test_render_scatter_returns_figure() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    fig = figure()
    out = render_scatter(fig, spec)
    assert out is fig


@bokeh_available
def test_render_scatter_label() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    fig = render_scatter(figure(), spec)
    assert len(fig.legend) == 1


@bokeh_available
def test_render_scatter_no_label_no_legend() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    fig = render_scatter(figure(), spec)
    assert len(fig.legend) == 0


@bokeh_available
def test_render_scatter_no_color_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    fig = render_scatter(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_scatter_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    fig = render_scatter(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_scatter_size() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), size=10.0)
    fig = render_scatter(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_scatter_no_size_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    fig = render_scatter(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_scatter_explicit_size_kwarg_not_overridden() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), size=10.0)
    # ``size`` passed explicitly as a kwarg takes precedence over ``spec.size``
    # (``kwargs.setdefault("size", spec.size)`` in ``render_scatter``).
    fig = render_scatter(figure(), spec, size=99.0)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_scatter_alpha() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), alpha=0.5)
    fig = render_scatter(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_scatter_marker() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), marker="square")
    fig = render_scatter(figure(), spec)
    assert fig.renderers[0].glyph.marker == "square"


@bokeh_available
def test_render_scatter_no_marker_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    fig = render_scatter(figure(), spec)
    assert fig.renderers[0].glyph.marker == "circle"
