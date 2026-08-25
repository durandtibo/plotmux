from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.layer import render_layer

##################################
#     Tests for render_layer     #
##################################


@altair_available
def test_render_layer_returns_layer_chart() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    chart = render_layer(spec)
    assert isinstance(chart, alt.LayerChart)


@altair_available
def test_render_layer_single_child() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    chart = render_layer(spec)
    assert len(chart.layer) == 1


@altair_available
def test_render_layer_combines_marks() -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    chart = render_layer(spec)
    assert len(chart.layer) == 2


@altair_available
def test_render_layer_with_histogram() -> None:
    spec = LayerSpec(
        layers=(
            HistogramSpec(values=np.arange(101), bins=10),
            LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        )
    )
    chart = render_layer(spec)
    assert len(chart.layer) == 2


@altair_available
def test_render_layer_unsupported_spec_raises() -> None:
    spec = LayerSpec.__new__(LayerSpec)
    object.__setattr__(spec, "layers", (object(),))
    with pytest.raises(NotImplementedError, match="No altair renderer registered"):
        render_layer(spec)
