from __future__ import annotations

import numpy as np

from plotmux.specs import CdfSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.cdf import render_cdf

################################
#     Tests for render_cdf     #
################################


@plotly_available
def test_render_cdf_returns_figure() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    fig = go.Figure()
    out = render_cdf(fig, spec)
    assert out is fig


@plotly_available
def test_render_cdf_default_nbins() -> None:
    spec = CdfSpec(values=np.arange(101))
    fig = render_cdf(go.Figure(), spec)
    assert len(fig.data) == 1


@plotly_available
def test_render_cdf_pins_yrange() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    fig = render_cdf(go.Figure(), spec)
    assert tuple(fig.layout.yaxis.range) == (0, 1)


@plotly_available
def test_render_cdf_label_shows_legend() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, label="my-label")
    fig = render_cdf(go.Figure(), spec)
    assert fig.data[0].name == "my-label"


@plotly_available
def test_render_cdf_color() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, color="red")
    fig = render_cdf(go.Figure(), spec)
    assert fig.data[0].line.color is not None


@plotly_available
def test_render_cdf_alpha() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, alpha=0.5)
    fig = render_cdf(go.Figure(), spec)
    assert fig.data[0].opacity == 0.5
