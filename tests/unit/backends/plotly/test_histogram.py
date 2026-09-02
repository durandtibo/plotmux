from __future__ import annotations

import numpy as np

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    from plotmux.backends.plotly.histogram import render_histogram

######################################
#     Tests for render_histogram     #
######################################


@plotly_available
def test_render_histogram_returns_figure() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = go.Figure()
    out = render_histogram(fig, spec)
    assert out is fig


@plotly_available
def test_render_histogram_single_bin() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=1)
    fig = render_histogram(go.Figure(), spec)
    assert len(fig.data) == 1


@plotly_available
def test_render_histogram_density() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    fig = render_histogram(go.Figure(), spec)
    assert len(fig.data) == 1


@plotly_available
def test_render_histogram_label_shows_legend() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, label="my-label")
    fig = render_histogram(go.Figure(), spec)
    assert fig.data[0].name == "my-label"
    assert fig.data[0].showlegend is True


@plotly_available
def test_render_histogram_no_label() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = render_histogram(go.Figure(), spec)
    assert fig.data[0].name is None


@plotly_available
def test_render_histogram_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, color="red")
    fig = render_histogram(go.Figure(), spec)
    assert fig.data[0].marker.color is not None


@plotly_available
def test_render_histogram_explicit_range() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, xmin=5, xmax=50)
    fig = render_histogram(go.Figure(), spec)
    x = np.asarray(fig.data[0].x)
    assert x.min() >= 5
    assert x.max() <= 50


@plotly_available
def test_render_histogram_row_col() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = render_histogram(make_subplots(rows=1, cols=1), spec, row=1, col=1)
    assert len(fig.data) == 1


@plotly_available
def test_render_histogram_forwards_kwargs() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = render_histogram(go.Figure(), spec, opacity=0.5)
    assert fig.data[0].opacity == 0.5
