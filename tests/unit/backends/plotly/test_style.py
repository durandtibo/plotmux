from __future__ import annotations

from typing import Any, cast

import pytest

from plotmux.scene import AxesScene, LegendStyle
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    from plotmux.backends.plotly.style import (
        DASH_STYLE,
        LEGEND_LOCATION,
        MARKER_STYLE,
        apply_legend,
        apply_style,
        axis_range,
        rgba_to_plotly,
    )


def _scene(**kwargs: Any) -> AxesScene:
    return AxesScene(primitives=(), **kwargs)


def _styled(**kwargs: Any) -> Any:
    fig = go.Figure()
    apply_style(fig, _scene(**kwargs))
    return fig


##################################
#     Tests for rgba_to_plotly   #
##################################


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        pytest.param((1.0, 0.0, 0.0, 1.0), "rgba(255, 0, 0, 1.0)", id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), "rgba(0, 0, 0, 0.0)", id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), "rgba(128, 128, 128, 0.5)", id="rounding"),
    ],
)
@plotly_available
def test_rgba_to_plotly(color: tuple[float, ...], expected: str) -> None:
    assert rgba_to_plotly(cast("Any", color)) == expected


#############################
#     Tests for axis_range  #
#############################


@pytest.mark.parametrize(
    ("limits", "scale", "expected"),
    [
        pytest.param((1.0, 2.0), "linear", [1.0, 2.0], id="linear"),
        pytest.param((1.0, 100.0), "log", [0.0, 2.0], id="log-is-in-powers-of-ten"),
        pytest.param((1.0, None), "linear", None, id="lower-only"),
        pytest.param((None, 2.0), "linear", None, id="upper-only"),
        pytest.param((None, None), "linear", None, id="none"),
        pytest.param((1.0, None), "log", None, id="log-lower-only"),
    ],
)
@plotly_available
def test_axis_range(
    limits: tuple[float | None, float | None], scale: str, expected: list[float] | None
) -> None:
    assert axis_range(limits, scale) == expected


################################
#     Tests for apply_style    #
################################


@plotly_available
def test_apply_style_xlabel() -> None:
    assert _styled(xlabel="x").layout.xaxis.title.text == "x"


@plotly_available
def test_apply_style_ylabel() -> None:
    assert _styled(ylabel="y").layout.yaxis.title.text == "y"


@plotly_available
def test_apply_style_no_labels() -> None:
    assert _styled().layout.xaxis.title.text is None


@plotly_available
def test_apply_style_scales() -> None:
    fig = _styled(xscale="log", yscale="log")
    assert (fig.layout.xaxis.type, fig.layout.yaxis.type) == ("log", "log")


@plotly_available
def test_apply_style_default_scales_are_linear() -> None:
    fig = _styled()
    assert (fig.layout.xaxis.type, fig.layout.yaxis.type) == ("linear", "linear")


@plotly_available
def test_apply_style_xlim() -> None:
    assert _styled(xlim=(1.0, 2.0)).layout.xaxis.range == (1.0, 2.0)


@plotly_available
def test_apply_style_ylim() -> None:
    assert _styled(ylim=(1.0, 2.0)).layout.yaxis.range == (1.0, 2.0)


@plotly_available
def test_apply_style_log_limits_are_in_powers_of_ten() -> None:
    assert _styled(xscale="log", xlim=(1.0, 100.0)).layout.xaxis.range == (0.0, 2.0)


@plotly_available
def test_apply_style_single_bound_is_left_to_autoscale() -> None:
    assert _styled(xlim=(1.0, None)).layout.xaxis.range is None


@plotly_available
def test_apply_style_background_color() -> None:
    assert (
        _styled(background_color=(1.0, 0.0, 0.0, 1.0)).layout.plot_bgcolor == "rgba(255, 0, 0, 1.0)"
    )


@plotly_available
def test_apply_style_no_background_color() -> None:
    assert _styled().layout.plot_bgcolor is None


@plotly_available
def test_apply_style_subplot_background_is_a_shape_below_the_traces() -> None:
    fig = make_subplots(rows=1, cols=2)
    apply_style(fig, _scene(background_color=(1.0, 0.0, 0.0, 1.0)), row=1, col=2)
    (shape,) = fig.layout.shapes
    assert (shape.xref, shape.yref, shape.layer) == ("x2 domain", "y2 domain", "below")


@plotly_available
def test_apply_style_subplot_background_does_not_set_the_plot_background() -> None:
    fig = make_subplots(rows=1, cols=2)
    apply_style(fig, _scene(background_color=(1.0, 0.0, 0.0, 1.0)), row=1, col=2)
    assert fig.layout.plot_bgcolor is None


@plotly_available
def test_apply_style_subplot_axes() -> None:
    fig = make_subplots(rows=1, cols=2)
    apply_style(fig, _scene(xlabel="x2"), row=1, col=2)
    assert (fig.layout.xaxis.title.text, fig.layout.xaxis2.title.text) == (None, "x2")


################################
#     Tests for apply_legend   #
################################


def _legend(scene: AxesScene) -> Any:
    fig = go.Figure()
    apply_legend(fig, scene)
    return fig.layout.legend


@plotly_available
def test_apply_legend_without_legend_is_a_noop() -> None:
    assert _legend(_scene()).title.text is None


@plotly_available
def test_apply_legend_title() -> None:
    assert _legend(_scene(legend=LegendStyle(title="Lines"))).title.text == "Lines"


@plotly_available
def test_apply_legend_default_style_changes_nothing() -> None:
    assert _legend(_scene(legend=LegendStyle())).orientation is None


@pytest.mark.parametrize("location", sorted(LEGEND_LOCATION) if is_plotly_available() else [])
@plotly_available
def test_apply_legend_location(location: str) -> None:
    legend = _legend(_scene(legend=LegendStyle(location=cast("Any", location))))
    expected = LEGEND_LOCATION[location]
    assert (legend.x, legend.y, legend.xanchor, legend.yanchor) == (
        expected["x"],
        expected["y"],
        expected["xanchor"],
        expected["yanchor"],
    )


@pytest.mark.parametrize(("orientation", "expected"), [("horizontal", "h"), ("vertical", "v")])
@plotly_available
def test_apply_legend_orientation(orientation: str, expected: str) -> None:
    legend = _legend(_scene(legend=LegendStyle(orientation=cast("Any", orientation))))
    assert legend.orientation == expected


@plotly_available
def test_dash_style_whole_table() -> None:
    assert DASH_STYLE == {"solid": "solid", "dashed": "dash", "dotted": "dot", "dashdot": "dashdot"}


@plotly_available
def test_marker_style_whole_table() -> None:
    assert MARKER_STYLE == {
        "circle": "circle",
        "square": "square",
        "triangle": "triangle-up",
        "diamond": "diamond",
        "cross": "cross",
        "x": "x",
    }
