from __future__ import annotations

import numpy as np

from plotmux.specs import ScatterSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.scatter import render_scatter

####################################
#     Tests for render_scatter     #
####################################


@plotly_available
def test_render_scatter_returns_figure() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    fig = go.Figure()
    out = render_scatter(fig, spec)
    assert out is fig


@plotly_available
def test_render_scatter_mode_is_markers() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].mode == "markers"


@plotly_available
def test_render_scatter_color_size() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", size=12)
    fig = render_scatter(go.Figure(), spec)
    marker = fig.data[0].marker
    assert marker.color is not None
    assert marker.size == 12


@plotly_available
def test_render_scatter_edgecolor_defaults_to_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].marker.line.color == fig.data[0].marker.color


@plotly_available
def test_render_scatter_explicit_edgecolor() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", edgecolor="black")
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].marker.line.color != fig.data[0].marker.color


@plotly_available
def test_render_scatter_label_shows_legend() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), label="my-scatter")
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].name == "my-scatter"


@plotly_available
def test_render_scatter_alpha() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), alpha=0.5)
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].opacity == 0.5


@plotly_available
def test_render_scatter_marker() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), marker="square")
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].marker.symbol == "square"


@plotly_available
def test_render_scatter_no_marker_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].marker.symbol is None


@plotly_available
def test_render_scatter_fill_false_transparent_fill() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", fill=False)
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].marker.color == "rgba(0, 0, 0, 0)"


@plotly_available
def test_render_scatter_fill_false_outline_uses_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", fill=False)
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].marker.line.color is not None
    assert fig.data[0].marker.line.color != "rgba(0, 0, 0, 0)"


@plotly_available
def test_render_scatter_fill_none_or_true_uses_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    fig = render_scatter(go.Figure(), spec)
    assert fig.data[0].marker.color != "rgba(0, 0, 0, 0)"
