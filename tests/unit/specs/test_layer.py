from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LayerSpec, LineSpec


def test_layer_spec_layers() -> None:
    hist_spec = HistogramSpec(values=np.arange(101), bins=10)
    line_spec = LineSpec(x=np.arange(10), y=np.arange(10))
    spec = LayerSpec(layers=(hist_spec, line_spec))
    assert spec.layers == (hist_spec, line_spec)


def test_layer_spec_is_frozen() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    with pytest.raises(AttributeError):
        spec.layers = ()


def test_layer_spec_empty_layers_raises() -> None:
    with pytest.raises(ValueError, match="layers must contain at least one spec"):
        LayerSpec(layers=())


def test_layer_spec_nested_layer_raises() -> None:
    inner = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    with pytest.raises(ValueError, match="layers must not contain a LayerSpec"):
        LayerSpec(layers=(inner,))


def test_layer_spec_common_style() -> None:
    spec = LayerSpec(
        layers=(LineSpec(x=np.arange(10), y=np.arange(10)),),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
    )
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"
