from __future__ import annotations

from plotmux.specs import SlopeSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.slope import render_slope

##################################
#     Tests for render_slope     #
##################################


@xy_available
def test_render_slope_returns_chart() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert isinstance(chart, Chart)


@xy_available
def test_render_slope_label() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, label="my-label")
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert isinstance(chart, Chart)


@xy_available
def test_render_slope_no_color_uses_backend_default() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert isinstance(chart, Chart)


@xy_available
def test_render_slope_color() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, color="red")
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert isinstance(chart, Chart)


@xy_available
def test_render_slope_alpha() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, alpha=0.5)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert chart.children[0].props["opacity"] == 0.5


@xy_available
def test_render_slope_linewidth() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, linewidth=3.0)
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert chart.children[0].props["width"] == 3.0


@xy_available
def test_render_slope_linestyle() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0, linestyle="dashed")
    chart = render_slope(spec, xrange=(0.0, 10.0))
    assert chart.children[0].props["dash"] == "dashed"


@xy_available
def test_render_slope_forwards_kwargs() -> None:
    spec = SlopeSpec(gradient=1.0, intercept=0.0)
    chart = render_slope(spec, xrange=(0.0, 10.0), width=5.0)
    assert isinstance(chart, Chart)
