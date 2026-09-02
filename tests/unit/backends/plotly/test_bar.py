from __future__ import annotations

import numpy as np

from plotmux.specs import BarSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.bar import render_bar

################################
#     Tests for render_bar     #
################################


@plotly_available
def test_render_bar_returns_figure() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5) ** 2)
    fig = go.Figure()
    out = render_bar(fig, spec)
    assert out is fig


@plotly_available
def test_render_bar_width() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5) ** 2, width=0.5)
    fig = render_bar(go.Figure(), spec)
    assert fig.data[0].width == 0.5


@plotly_available
def test_render_bar_color() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5) ** 2, color="green")
    fig = render_bar(go.Figure(), spec)
    assert fig.data[0].marker.color is not None


@plotly_available
def test_render_bar_label_shows_legend() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), label="my-bar")
    fig = render_bar(go.Figure(), spec)
    assert fig.data[0].name == "my-bar"


@plotly_available
def test_render_bar_alpha() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), alpha=0.5)
    fig = render_bar(go.Figure(), spec)
    assert fig.data[0].opacity == 0.5
