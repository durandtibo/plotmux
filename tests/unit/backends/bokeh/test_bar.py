from __future__ import annotations

import numpy as np

from plotmux.specs import BarSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.models import FactorRange
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.bar import bar_figure_kwargs, render_bar

################################
#     Tests for render_bar     #
################################


@bokeh_available
def test_render_bar_returns_figure() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    fig = figure()
    out = render_bar(fig, spec)
    assert out is fig


@bokeh_available
def test_render_bar_label() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), label="my-label")
    fig = render_bar(figure(), spec)
    assert len(fig.legend) == 1


@bokeh_available
def test_render_bar_no_label_no_legend() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    fig = render_bar(figure(), spec)
    assert len(fig.legend) == 0


@bokeh_available
def test_render_bar_no_color_uses_backend_default() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    fig = render_bar(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_bar_color() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), color="red")
    fig = render_bar(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_bar_width() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), width=0.3)
    fig = render_bar(figure(), spec)
    assert fig.renderers[0].glyph.width == 0.3


@bokeh_available
def test_render_bar_alpha() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), alpha=0.5)
    fig = render_bar(figure(), spec)
    assert fig.renderers[0].glyph.line_alpha == 0.5


##########################################
#     Tests for bar_figure_kwargs        #
##########################################


@bokeh_available
def test_bar_figure_kwargs_categorical() -> None:
    spec = BarSpec(x=np.array(["Apples", "Pears"]), y=np.array([2, 1]))
    assert bar_figure_kwargs(spec) == {"x_range": ["Apples", "Pears"]}


@bokeh_available
def test_bar_figure_kwargs_numeric() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    assert bar_figure_kwargs(spec) == {}


@bokeh_available
def test_render_bar_categorical_x_range() -> None:
    spec = BarSpec(x=np.array(["Apples", "Pears", "Nectarines"]), y=np.array([2, 1, 4]))
    fig = figure(**bar_figure_kwargs(spec))
    render_bar(fig, spec)
    assert isinstance(fig.x_range, FactorRange)
    assert list(fig.x_range.factors) == ["Apples", "Pears", "Nectarines"]
