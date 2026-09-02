from __future__ import annotations

from plotmux.specs import SlopeSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.slope import render_slope

##################################
#     Tests for render_slope     #
##################################


@plotly_available
def test_render_slope_returns_figure() -> None:
    spec = SlopeSpec(gradient=2, intercept=10)
    fig = go.Figure()
    out = render_slope(fig, spec, xrange=(0.0, 10.0))
    assert out is fig


@plotly_available
def test_render_slope_adds_one_trace_spanning_xrange() -> None:
    spec = SlopeSpec(gradient=2, intercept=10)
    fig = render_slope(go.Figure(), spec, xrange=(0.0, 10.0))
    assert len(fig.data) == 1
    trace = fig.data[0]
    assert list(trace.x) == [0.0, 10.0]
    assert list(trace.y) == [10.0, 30.0]


@plotly_available
def test_render_slope_no_color_uses_backend_default() -> None:
    spec = SlopeSpec(gradient=2, intercept=10)
    fig = render_slope(go.Figure(), spec, xrange=(0.0, 10.0))
    assert isinstance(fig, go.Figure)


@plotly_available
def test_render_slope_color_linewidth_linestyle() -> None:
    spec = SlopeSpec(gradient=2, intercept=10, color="blue", linewidth=4, linestyle="dashed")
    fig = render_slope(go.Figure(), spec, xrange=(0.0, 10.0))
    trace = fig.data[0]
    assert trace.line.width == 4
    assert trace.line.dash == "dash"


@plotly_available
def test_render_slope_label_shows_legend() -> None:
    spec = SlopeSpec(gradient=2, intercept=10, label="trend")
    fig = render_slope(go.Figure(), spec, xrange=(0.0, 10.0))
    trace = fig.data[0]
    assert trace.name == "trend"
    assert trace.showlegend is True


@plotly_available
def test_render_slope_alpha() -> None:
    spec = SlopeSpec(gradient=2, intercept=10, alpha=0.5)
    fig = render_slope(go.Figure(), spec, xrange=(0.0, 10.0))
    assert fig.data[0].opacity == 0.5
