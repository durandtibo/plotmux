from __future__ import annotations

import numpy as np

from plotmux.specs import BarSeries, StackedBarSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.models import FactorRange
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.stacked_bar import (
        render_stacked_bar,
        stacked_bar_figure_kwargs,
    )

########################################
#     Tests for render_stacked_bar     #
########################################


@bokeh_available
def test_render_stacked_bar_returns_figure() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    fig = figure()
    out = render_stacked_bar(fig, spec)
    assert out is fig


@bokeh_available
def test_render_stacked_bar_draws_one_renderer_per_series() -> None:
    spec = StackedBarSpec(
        x=np.arange(5), series=(BarSeries(y=np.arange(5)), BarSeries(y=np.arange(5)))
    )
    fig = render_stacked_bar(figure(), spec)
    assert len(fig.renderers) == 2


@bokeh_available
def test_render_stacked_bar_label() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5), label="s1"),))
    fig = render_stacked_bar(figure(), spec)
    assert len(fig.legend) == 1


@bokeh_available
def test_render_stacked_bar_no_label_no_legend() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    fig = render_stacked_bar(figure(), spec)
    assert len(fig.legend) == 0


@bokeh_available
def test_render_stacked_bar_width() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), width=0.3)
    fig = render_stacked_bar(figure(), spec)
    assert fig.renderers[0].glyph.width == 0.3


@bokeh_available
def test_render_stacked_bar_alpha() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), alpha=0.5)
    fig = render_stacked_bar(figure(), spec)
    assert fig.renderers[0].glyph.fill_alpha == 0.5


##########################################
#     Tests for stacked_bar_figure_kwargs #
##########################################


@bokeh_available
def test_stacked_bar_figure_kwargs_categorical() -> None:
    spec = StackedBarSpec(x=np.array(["Apples", "Pears"]), series=(BarSeries(y=np.array([2, 1])),))
    kwargs = stacked_bar_figure_kwargs(spec)
    assert kwargs == {"x_range": ["Apples", "Pears"]}


@bokeh_available
def test_stacked_bar_figure_kwargs_numeric() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    assert stacked_bar_figure_kwargs(spec) == {}


@bokeh_available
def test_render_stacked_bar_categorical_x_range() -> None:
    spec = StackedBarSpec(
        x=np.array(["Apples", "Pears", "Nectarines"]), series=(BarSeries(y=np.array([2, 1, 4])),)
    )
    fig = figure(**stacked_bar_figure_kwargs(spec))
    render_stacked_bar(fig, spec)
    assert isinstance(fig.x_range, FactorRange)
    assert list(fig.x_range.factors) == ["Apples", "Pears", "Nectarines"]
