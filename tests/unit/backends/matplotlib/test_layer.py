from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.layer import render_layer


@matplotlib_available
def test_render_layer_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    out = render_layer(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_layer_draws_each_child() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    render_layer(ax, spec)
    assert len(ax.lines) == 1
    assert len(ax.collections) == 1
    plt.close(fig)


@matplotlib_available
def test_render_layer_combined_legend() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10), label="line"),
            ScatterSpec(x=np.arange(10), y=np.arange(10), label="scatter"),
        )
    )
    render_layer(ax, spec)
    labels = [text.get_text() for text in ax.get_legend().get_texts()]
    assert labels == ["line", "scatter"]
    plt.close(fig)


@matplotlib_available
def test_render_layer_with_histogram() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec(
        layers=(
            HistogramSpec(values=np.arange(101), bins=10),
            LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        )
    )
    render_layer(ax, spec)
    assert len(ax.patches) == 10
    assert len(ax.lines) == 1
    plt.close(fig)


@matplotlib_available
def test_render_layer_unsupported_spec_raises() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec.__new__(LayerSpec)
    object.__setattr__(spec, "layers", (object(),))
    with pytest.raises(NotImplementedError, match="No matplotlib renderer registered"):
        render_layer(ax, spec)
    plt.close(fig)
