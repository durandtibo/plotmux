from __future__ import annotations

from plotmux.specs import SlopeSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.models import Slope
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.slope import render_slope

##################################
#     Tests for render_slope     #
##################################


@bokeh_available
def test_render_slope_returns_figure() -> None:
    spec = SlopeSpec(gradient=2, intercept=10)
    fig = figure()
    out = render_slope(fig, spec)
    assert out is fig


@bokeh_available
def test_render_slope_adds_one_layout() -> None:
    spec = SlopeSpec(gradient=2, intercept=10)
    fig = render_slope(figure(), spec)
    slopes = [r for r in fig.renderers + fig.center if isinstance(r, Slope)]
    assert len(slopes) == 1
    assert slopes[0].gradient == 2
    assert slopes[0].y_intercept == 10


@bokeh_available
def test_render_slope_no_color_uses_backend_default() -> None:
    spec = SlopeSpec(gradient=2, intercept=10)
    fig = render_slope(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_slope_color_linewidth_linestyle() -> None:
    spec = SlopeSpec(gradient=2, intercept=10, color="blue", linewidth=4, linestyle="dashed")
    fig = render_slope(figure(), spec)
    slope = next(r for r in fig.center if isinstance(r, Slope))
    assert slope.line_width == 4
    # bokeh normalizes a named dash style (e.g. ``"dashed"``) to its
    # underlying pixel dash-pattern list when read back, rather than
    # keeping the string.
    assert slope.line_dash != []


@bokeh_available
def test_render_slope_alpha() -> None:
    spec = SlopeSpec(gradient=2, intercept=10, alpha=0.5)
    fig = render_slope(figure(), spec)
    slope = next(r for r in fig.center if isinstance(r, Slope))
    assert slope.line_alpha == 0.5


@bokeh_available
def test_render_slope_forwards_kwargs() -> None:
    spec = SlopeSpec(gradient=2, intercept=10)
    fig = render_slope(figure(), spec, line_width=5.0)
    slope = next(r for r in fig.center if isinstance(r, Slope))
    assert slope.line_width == 5.0
