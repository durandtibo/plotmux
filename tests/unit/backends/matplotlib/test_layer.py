from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.layer import render_layer

##################################
#     Tests for render_layer     #
##################################


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
def test_render_layer_combined_legend_unlabeled_child_drawn_last() -> None:
    # Regression test: the combined legend must reflect every labeled
    # child regardless of draw order, not just rely on the last-drawn
    # child happening to be the one that calls ``ax.legend()``.
    fig, ax = plt.subplots()
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10), label="line"),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),  # unlabeled, drawn last
        )
    )
    render_layer(ax, spec)
    labels = [text.get_text() for text in ax.get_legend().get_texts()]
    assert labels == ["line"]
    plt.close(fig)


@matplotlib_available
def test_render_layer_no_labeled_child_has_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    render_layer(ax, spec)
    assert ax.get_legend() is None
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
def test_render_layer_single_child() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec(layers=(ScatterSpec(x=np.arange(10), y=np.arange(10)),))
    render_layer(ax, spec)
    assert len(ax.collections) == 1
    plt.close(fig)


@matplotlib_available
def test_render_layer_forwards_kwargs_to_every_child() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            LineSpec(x=np.arange(10), y=np.arange(10) + 1),
        )
    )
    render_layer(ax, spec, linewidth=5)
    assert all(line.get_linewidth() == 5 for line in ax.lines)
    plt.close(fig)


@matplotlib_available
def test_render_layer_unsupported_spec_raises() -> None:
    fig, ax = plt.subplots()
    spec = LayerSpec.__new__(LayerSpec)
    object.__setattr__(spec, "layers", (object(),))
    with pytest.raises(NotImplementedError, match="No matplotlib renderer registered"):
        render_layer(ax, spec)
    plt.close(fig)
