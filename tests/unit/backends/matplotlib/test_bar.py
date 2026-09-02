from __future__ import annotations

import numpy as np

from plotmux.specs import BarSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.bar import render_bar

################################
#     Tests for render_bar     #
################################


@matplotlib_available
def test_render_bar_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    out = render_bar(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_bar_draws_one_container() -> None:
    fig, ax = plt.subplots()
    spec = BarSpec(x=np.arange(5), y=np.arange(5) ** 2)
    render_bar(ax, spec)
    assert len(ax.containers) == 1
    plt.close(fig)


@matplotlib_available
def test_render_bar_label_adds_legend() -> None:
    fig, ax = plt.subplots()
    spec = BarSpec(x=np.arange(5), y=np.arange(5), label="my-label")
    render_bar(ax, spec)
    assert ax.get_legend() is not None
    plt.close(fig)


@matplotlib_available
def test_render_bar_no_label_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    render_bar(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


@matplotlib_available
def test_render_bar_width() -> None:
    fig, ax = plt.subplots()
    spec = BarSpec(x=np.arange(5), y=np.arange(5), width=0.3)
    render_bar(ax, spec)
    assert ax.containers[0][0].get_width() == 0.3
    plt.close(fig)


@matplotlib_available
def test_render_bar_color() -> None:
    fig, ax = plt.subplots()
    spec = BarSpec(x=np.arange(5), y=np.arange(5), color="red")
    render_bar(ax, spec)
    assert ax.containers[0][0].get_facecolor() == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_render_bar_forwards_kwargs() -> None:
    fig, ax = plt.subplots()
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    render_bar(ax, spec, alpha=0.3)
    assert ax.containers[0][0].get_alpha() == 0.3
    plt.close(fig)
