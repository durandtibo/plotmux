from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import (
    CdfSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
    SlopeSpec,
)
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.layer import render_layer

##################################
#     Tests for render_layer     #
##################################


@plotly_available
def test_render_layer_returns_figure() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    fig = go.Figure()
    out = render_layer(fig, spec)
    assert out is fig


@plotly_available
def test_render_layer_combines_marks() -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10), label="line"),
            ScatterSpec(x=np.arange(10), y=np.arange(10), label="scatter"),
        )
    )
    fig = render_layer(go.Figure(), spec)
    assert len(fig.data) == 2
    assert {trace.name for trace in fig.data} == {"line", "scatter"}


@plotly_available
def test_render_layer_with_histogram() -> None:
    spec = LayerSpec(
        layers=(
            HistogramSpec(values=np.arange(101), bins=10),
            LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        )
    )
    fig = render_layer(go.Figure(), spec)
    assert len(fig.data) == 2


@plotly_available
def test_render_layer_supports_cdf_spec() -> None:
    spec = LayerSpec(layers=(CdfSpec(values=np.arange(101), nbins=10),))
    fig = render_layer(go.Figure(), spec)
    assert len(fig.data) == 1


@plotly_available
def test_render_layer_with_slope() -> None:
    spec = LayerSpec(
        layers=(
            ScatterSpec(x=np.arange(10), y=np.arange(10) * 2 + 10, color="yellow"),
            SlopeSpec(gradient=2, intercept=10, color="blue", linewidth=4, linestyle="dashed"),
        )
    )
    fig = render_layer(go.Figure(), spec)
    assert len(fig.data) == 2


@plotly_available
def test_render_layer_slope_without_data_bound_sibling_raises() -> None:
    spec = LayerSpec(
        layers=(
            SlopeSpec(gradient=2, intercept=10),
            SlopeSpec(gradient=-1, intercept=0),
        )
    )
    with pytest.raises(NotImplementedError, match="no data-bound sibling"):
        render_layer(go.Figure(), spec)


@plotly_available
def test_render_layer_unsupported_spec_raises() -> None:
    spec = LayerSpec.__new__(LayerSpec)
    object.__setattr__(spec, "layers", (object(),))
    with pytest.raises(NotImplementedError, match="No plotly renderer registered"):
        render_layer(go.Figure(), spec)
