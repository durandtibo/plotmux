from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import CdfSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.layer import render_layer

##################################
#     Tests for render_layer     #
##################################


@xy_available
def test_render_layer_returns_chart() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    chart = render_layer(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_layer_single_child() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    chart = render_layer(spec)
    assert len(chart.children) == 1


@xy_available
def test_render_layer_combines_marks() -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    chart = render_layer(spec)
    assert len(chart.children) == 2


@xy_available
def test_render_layer_with_histogram() -> None:
    spec = LayerSpec(
        layers=(
            HistogramSpec(values=np.arange(101), bins=10),
            LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        )
    )
    chart = render_layer(spec)
    assert len(chart.children) == 2


@xy_available
def test_render_layer_supports_cdf_spec() -> None:
    spec = LayerSpec(layers=(CdfSpec(values=np.arange(101), nbins=10),))
    chart = render_layer(spec)
    assert len(chart.children) == 1


@xy_available
def test_render_layer_unsupported_spec_raises() -> None:
    spec = LayerSpec.__new__(LayerSpec)
    object.__setattr__(spec, "layers", (object(),))
    with pytest.raises(NotImplementedError, match="No xy renderer registered"):
        render_layer(spec)
