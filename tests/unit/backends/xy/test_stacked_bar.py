from __future__ import annotations

import numpy as np

from plotmux.specs import BarSeries, StackedBarSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.stacked_bar import render_stacked_bar

########################################
#     Tests for render_stacked_bar     #
########################################


@xy_available
def test_render_stacked_bar_returns_chart() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    chart = render_stacked_bar(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_stacked_bar_mode_is_stacked() -> None:
    spec = StackedBarSpec(
        x=np.arange(5), series=(BarSeries(y=np.arange(5)), BarSeries(y=np.arange(5)))
    )
    chart = render_stacked_bar(spec)
    assert chart.children[0].props["mode"] == "stacked"


@xy_available
def test_render_stacked_bar_series_names() -> None:
    spec = StackedBarSpec(
        x=np.arange(5),
        series=(BarSeries(y=np.arange(5), label="s1"), BarSeries(y=np.arange(5), label="s2")),
    )
    chart = render_stacked_bar(spec)
    assert chart.children[0].props["series"] == ["s1", "s2"]


@xy_available
def test_render_stacked_bar_width() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), width=0.3)
    chart = render_stacked_bar(spec)
    assert chart.children[0].props["width"] == 0.3


@xy_available
def test_render_stacked_bar_alpha() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), alpha=0.5)
    chart = render_stacked_bar(spec)
    assert chart.children[0].props["opacity"] == 0.5


@xy_available
def test_render_stacked_bar_categorical_x() -> None:
    spec = StackedBarSpec(
        x=np.array(["Apples", "Pears", "Nectarines"]), series=(BarSeries(y=np.array([2, 1, 4])),)
    )
    chart = render_stacked_bar(spec)
    assert list(chart.children[0].x) == ["Apples", "Pears", "Nectarines"]
