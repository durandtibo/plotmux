from __future__ import annotations

import numpy as np

from plotmux.specs import LineSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.line import render_line

#################################
#     Tests for render_line     #
#################################


@bokeh_available
def test_render_line_returns_figure() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    fig = figure()
    out = render_line(fig, spec)
    assert out is fig


@bokeh_available
def test_render_line_label() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    fig = render_line(figure(), spec)
    assert len(fig.legend) == 1


@bokeh_available
def test_render_line_no_label_no_legend() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    fig = render_line(figure(), spec)
    assert len(fig.legend) == 0


@bokeh_available
def test_render_line_no_color_uses_backend_default() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    fig = render_line(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_line_color() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color="red")
    fig = render_line(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_line_forwards_kwargs() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    fig = render_line(figure(), spec, line_width=5.0)
    assert isinstance(fig, figure)
