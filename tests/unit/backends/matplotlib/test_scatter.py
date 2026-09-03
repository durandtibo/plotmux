from __future__ import annotations

import numpy as np

from plotmux.specs import ScatterSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.scatter import render_scatter

####################################
#     Tests for render_scatter     #
####################################


@matplotlib_available
def test_render_scatter_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    out = render_scatter(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_scatter_draws_one_collection() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    render_scatter(ax, spec)
    assert len(ax.collections) == 1
    plt.close(fig)


@matplotlib_available
def test_render_scatter_label_adds_legend() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    render_scatter(ax, spec)
    assert ax.get_legend() is not None
    plt.close(fig)


@matplotlib_available
def test_render_scatter_no_label_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    render_scatter(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


@matplotlib_available
def test_render_scatter_size() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), size=42.0)
    render_scatter(ax, spec)
    assert (ax.collections[0].get_sizes() == 42.0).all()
    plt.close(fig)


@matplotlib_available
def test_render_scatter_no_size_uses_backend_default() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    render_scatter(ax, spec)
    assert len(ax.collections[0].get_sizes()) > 0
    plt.close(fig)


@matplotlib_available
def test_render_scatter_color() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    render_scatter(ax, spec)
    assert tuple(ax.collections[0].get_facecolor()[0]) == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_render_scatter_forwards_kwargs() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    render_scatter(ax, spec, alpha=0.3)
    assert ax.collections[0].get_alpha() == 0.3
    plt.close(fig)


@matplotlib_available
def test_render_scatter_edgecolor() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), edgecolor="blue")
    render_scatter(ax, spec)
    assert tuple(ax.collections[0].get_edgecolor()[0]) == (0.0, 0.0, 1.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_render_scatter_marker() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), marker="square")
    render_scatter(ax, spec)
    # A square marker's path has 5 vertices (4 corners, closed); a circle
    # (matplotlib's default) has many more.
    assert len(ax.collections[0].get_paths()[0].vertices) == 5
    plt.close(fig)


@matplotlib_available
def test_render_scatter_no_marker_uses_backend_default() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    render_scatter(ax, spec)
    assert len(ax.collections[0].get_paths()[0].vertices) != 5
    plt.close(fig)


@matplotlib_available
def test_render_scatter_fill_false_draws_hollow_marker() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", fill=False)
    render_scatter(ax, spec)
    # ``facecolors="none"`` means no face color at all (an empty array),
    # not a transparent rgba tuple.
    assert len(ax.collections[0].get_facecolor()) == 0
    plt.close(fig)


@matplotlib_available
def test_render_scatter_fill_false_outline_uses_color() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", fill=False)
    render_scatter(ax, spec)
    assert tuple(ax.collections[0].get_edgecolor()[0]) == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_render_scatter_fill_false_outline_prefers_edgecolor() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red", edgecolor="blue", fill=False)
    render_scatter(ax, spec)
    assert tuple(ax.collections[0].get_edgecolor()[0]) == (0.0, 0.0, 1.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_render_scatter_fill_none_or_true_is_filled() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    render_scatter(ax, spec)
    assert tuple(ax.collections[0].get_facecolor()[0]) == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)
