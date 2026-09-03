from __future__ import annotations

import numpy as np

from plotmux.specs import BarSeries, StackedBarSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.stacked_bar import render_stacked_bar

########################################
#     Tests for render_stacked_bar     #
########################################


@plotly_available
def test_render_stacked_bar_returns_figure() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    fig = go.Figure()
    out = render_stacked_bar(fig, spec)
    assert out is fig


@plotly_available
def test_render_stacked_bar_one_trace_per_series() -> None:
    spec = StackedBarSpec(
        x=np.arange(5), series=(BarSeries(y=np.arange(5)), BarSeries(y=np.arange(5)))
    )
    fig = render_stacked_bar(go.Figure(), spec)
    assert len(fig.data) == 2


@plotly_available
def test_render_stacked_bar_sets_barmode_stack() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    fig = render_stacked_bar(go.Figure(), spec)
    assert fig.layout.barmode == "stack"


@plotly_available
def test_render_stacked_bar_width() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), width=0.5)
    fig = render_stacked_bar(go.Figure(), spec)
    assert fig.data[0].width == 0.5


@plotly_available
def test_render_stacked_bar_label_shows_legend() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5), label="s1"),))
    fig = render_stacked_bar(go.Figure(), spec)
    assert fig.data[0].name == "s1"


@plotly_available
def test_render_stacked_bar_alpha() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), alpha=0.5)
    fig = render_stacked_bar(go.Figure(), spec)
    assert fig.data[0].opacity == 0.5


@plotly_available
def test_render_stacked_bar_categorical_x() -> None:
    spec = StackedBarSpec(
        x=np.array(["Apples", "Pears", "Nectarines"]), series=(BarSeries(y=np.array([2, 1, 4])),)
    )
    fig = render_stacked_bar(go.Figure(), spec)
    assert list(fig.data[0].x) == ["Apples", "Pears", "Nectarines"]
