from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
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
def test_render_layer_unsupported_spec_raises() -> None:
    spec = LayerSpec.__new__(LayerSpec)
    object.__setattr__(spec, "layers", (object(),))
    with pytest.raises(NotImplementedError, match="No bokeh renderer registered"):
        render_layer(figure(), spec)
