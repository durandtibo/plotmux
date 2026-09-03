from __future__ import annotations

import numpy as np

from plotmux.specs import BarSeries, StackedBarSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.stacked_bar import render_stacked_bar

########################################
#     Tests for render_stacked_bar     #
########################################


@matplotlib_available
def test_render_stacked_bar_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    out = render_stacked_bar(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_draws_one_container_per_series() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(
        x=np.arange(5), series=(BarSeries(y=np.arange(5)), BarSeries(y=np.arange(5)))
    )
    render_stacked_bar(ax, spec)
    assert len(ax.containers) == 2
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_stacks_cumulatively() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(
        x=np.arange(3),
        series=(BarSeries(y=np.array([1.0, 2.0, 3.0])), BarSeries(y=np.array([4.0, 5.0, 6.0]))),
    )
    render_stacked_bar(ax, spec)
    bottoms = [rect.get_y() for rect in ax.containers[1]]
    assert bottoms == [1.0, 2.0, 3.0]
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_label_adds_legend() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5), label="s1"),))
    render_stacked_bar(ax, spec)
    assert ax.get_legend() is not None
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_no_label_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    render_stacked_bar(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_width() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), width=0.3)
    render_stacked_bar(ax, spec)
    assert ax.containers[0][0].get_width() == 0.3
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_distinct_series_colors() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(
        x=np.arange(5), series=(BarSeries(y=np.arange(5)), BarSeries(y=np.arange(5)))
    )
    render_stacked_bar(ax, spec)
    color0 = ax.containers[0][0].get_facecolor()
    color1 = ax.containers[1][0].get_facecolor()
    assert color0 != color1
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_categorical_x() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(
        x=np.array(["Apples", "Pears", "Nectarines"]), series=(BarSeries(y=np.array([2, 1, 4])),)
    )
    render_stacked_bar(ax, spec)
    assert [t.get_text() for t in ax.get_xticklabels()] == ["Apples", "Pears", "Nectarines"]
    plt.close(fig)


@matplotlib_available
def test_render_stacked_bar_forwards_kwargs() -> None:
    fig, ax = plt.subplots()
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    render_stacked_bar(ax, spec, alpha=0.3)
    assert ax.containers[0][0].get_alpha() == 0.3
    plt.close(fig)
