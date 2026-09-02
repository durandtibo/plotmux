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
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.models import Slope
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.layer import render_layer

##################################
#     Tests for render_layer     #
##################################


@bokeh_available
def test_render_layer_returns_figure() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    fig = figure()
    out = render_layer(fig, spec)
    assert out is fig


@bokeh_available
def test_render_layer_combines_marks() -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10), label="line"),
            ScatterSpec(x=np.arange(10), y=np.arange(10), label="scatter"),
        )
    )
    fig = render_layer(figure(), spec)
    assert len(fig.renderers) == 2
    assert len(fig.legend[0].items) == 2


@bokeh_available
def test_render_layer_with_histogram() -> None:
    spec = LayerSpec(
        layers=(
            HistogramSpec(values=np.arange(101), bins=10),
            LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        )
    )
    fig = render_layer(figure(), spec)
    assert len(fig.renderers) == 2


@bokeh_available
def test_render_layer_supports_cdf_spec() -> None:
    spec = LayerSpec(layers=(CdfSpec(values=np.arange(101), nbins=10),))
    fig = render_layer(figure(), spec)
    assert len(fig.renderers) == 1


@bokeh_available
def test_render_layer_with_slope() -> None:
    spec = LayerSpec(
        layers=(
            ScatterSpec(x=np.arange(10), y=np.arange(10) * 2 + 10, color="yellow"),
            SlopeSpec(gradient=2, intercept=10, color="blue", linewidth=4, linestyle="dashed"),
        )
    )
    fig = render_layer(figure(), spec)
    # The scatter is a glyph renderer; the slope is an annotation added via
    # ``add_layout`` (``fig.center``), not another entry in ``fig.renderers``.
    assert len(fig.renderers) == 1
    assert any(isinstance(r, Slope) for r in fig.center)


@bokeh_available
def test_render_layer_unsupported_spec_raises() -> None:
    spec = LayerSpec.__new__(LayerSpec)
    object.__setattr__(spec, "layers", (object(),))
    with pytest.raises(NotImplementedError, match="No bokeh renderer registered"):
        render_layer(figure(), spec)
