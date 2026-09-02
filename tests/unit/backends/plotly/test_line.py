from __future__ import annotations

import numpy as np

from plotmux.specs import LineSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.line import render_line

#################################
#     Tests for render_line     #
#################################


@plotly_available
def test_render_line_returns_figure() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    fig = go.Figure()
    out = render_line(fig, spec)
    assert out is fig


@plotly_available
def test_render_line_mode_is_lines() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    fig = render_line(go.Figure(), spec)
    assert fig.data[0].mode == "lines"


@plotly_available
def test_render_line_color_width_style() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color="blue", linewidth=3, linestyle="dotted")
    fig = render_line(go.Figure(), spec)
    trace = fig.data[0]
    assert trace.line.color is not None
    assert trace.line.width == 3
    assert trace.line.dash == "dot"


@plotly_available
def test_render_line_label_shows_legend() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), label="my-line")
    fig = render_line(go.Figure(), spec)
    assert fig.data[0].name == "my-line"
