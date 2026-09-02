from __future__ import annotations

from plotmux.specs import SlopeSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.slope import render_slope

##################################
#     Tests for render_slope     #
##################################


@altair_available
def test_render_slope_returns_chart() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_slope_label() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, label="my-label")
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_slope_no_color_uses_backend_default() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_slope_color() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, color="red")
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert chart.to_dict()["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_render_slope_alpha() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, alpha=0.5)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert chart.to_dict()["mark"]["opacity"] == 0.5


@altair_available
def test_render_slope_linewidth() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, linewidth=3.0)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert chart.to_dict()["mark"]["strokeWidth"] == 3.0


@altair_available
def test_render_slope_linestyle() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, linestyle="dashed")
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert chart.to_dict()["mark"]["strokeDash"] is not None


@altair_available
def test_render_slope_forwards_kwargs() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0)
    chart = render_slope(spec, xrange=(0.0, 10.0), strokeWidth=5.0)
    assert chart.to_dict()["mark"]["strokeWidth"] == 5.0
