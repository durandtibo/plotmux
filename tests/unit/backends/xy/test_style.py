from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.scene import AxesScene, LegendStyle
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    import xy

    from plotmux.backends.xy.style import LEGEND_LOCATION, MARKERS, apply_style, rgba_to_xy


def _chart() -> Any:
    return xy.chart(xy.line(np.arange(3.0), np.arange(3.0), name="a"))


def _scene(**kwargs: Any) -> AxesScene:
    return AxesScene(primitives=(), **kwargs)


def _axes(chart: Any) -> list[Any]:
    return [c for c in chart.children if type(c).__name__ == "Axis"]


def _legends(chart: Any) -> list[Any]:
    return [c for c in chart.children if type(c).__name__ == "Legend"]


################################
#     Tests for rgba_to_xy     #
################################


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        pytest.param((1.0, 0.0, 0.0, 1.0), "rgba(255, 0, 0, 1.0)", id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), "rgba(0, 0, 0, 0.0)", id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), "rgba(128, 128, 128, 0.5)", id="rounding"),
        pytest.param((1.0, 1.0, 1.0, 1.0), "rgba(255, 255, 255, 1.0)", id="white"),
    ],
)
@xy_available
def test_rgba_to_xy(color: tuple[float, float, float, float], expected: str) -> None:
    assert rgba_to_xy(color) == expected


################################
#     Tests for apply_style    #
################################


@xy_available
def test_apply_style_keeps_the_marks() -> None:
    assert cast("Any", apply_style(_chart(), _scene())).children[0].kind == "line"


@xy_available
def test_apply_style_appends_the_two_axes() -> None:
    assert len(_axes(apply_style(_chart(), _scene()))) == 2


@xy_available
def test_apply_style_does_not_change_the_chart() -> None:
    chart = _chart()
    apply_style(chart, _scene(title="t"))
    assert chart.title is None


@xy_available
def test_apply_style_title() -> None:
    assert apply_style(_chart(), _scene(title="t")).title == "t"


@xy_available
def test_apply_style_no_title() -> None:
    assert apply_style(_chart(), _scene()).title is None


@xy_available
def test_apply_style_labels() -> None:
    x_axis, y_axis = _axes(apply_style(_chart(), _scene(xlabel="x", ylabel="y")))
    assert (x_axis.label, y_axis.label) == ("x", "y")


@xy_available
def test_apply_style_no_labels() -> None:
    x_axis, y_axis = _axes(apply_style(_chart(), _scene()))
    assert (x_axis.label, y_axis.label) == (None, None)


@xy_available
def test_apply_style_scales() -> None:
    x_axis, y_axis = _axes(apply_style(_chart(), _scene(xscale="log", yscale="log")))
    assert (x_axis.type_, y_axis.type_) == ("log", "log")


@xy_available
def test_apply_style_x_domain() -> None:
    x_axis, _ = _axes(apply_style(_chart(), _scene(xlim=(1.0, 2.0))))
    assert x_axis.domain == (1.0, 2.0)


@xy_available
def test_apply_style_y_domain() -> None:
    _, y_axis = _axes(apply_style(_chart(), _scene(ylim=(1.0, 2.0))))
    assert y_axis.domain == (1.0, 2.0)


@xy_available
def test_apply_style_single_x_bound_is_left_to_autoscale() -> None:
    x_axis, _ = _axes(apply_style(_chart(), _scene(xlim=(1.0, None))))
    assert x_axis.domain is None


@xy_available
def test_apply_style_single_y_bound_is_left_to_autoscale() -> None:
    _, y_axis = _axes(apply_style(_chart(), _scene(ylim=(None, 2.0))))
    assert y_axis.domain is None


@xy_available
def test_apply_style_preserves_the_layout() -> None:
    chart = xy.chart(xy.line(np.arange(3.0), np.arange(3.0)), width=500, height=300)
    styled = apply_style(chart, _scene())
    assert (styled.width, styled.height) == (500, 300)


@xy_available
def test_apply_style_background_color() -> None:
    styled = apply_style(_chart(), _scene(background_color=(1.0, 0.0, 0.0, 1.0)))
    assert styled.style == {"backgroundColor": "rgba(255, 0, 0, 1.0)"}


@xy_available
def test_apply_style_no_background_color() -> None:
    assert apply_style(_chart(), _scene()).style in (None, {})


@xy_available
def test_apply_style_no_legend_style_adds_no_legend() -> None:
    assert _legends(apply_style(_chart(), _scene(legend=LegendStyle()))) == []


@xy_available
def test_apply_style_no_legend_in_the_scene_adds_no_legend() -> None:
    assert _legends(apply_style(_chart(), _scene())) == []


@xy_available
def test_apply_style_legend_title() -> None:
    (legend,) = _legends(apply_style(_chart(), _scene(legend=LegendStyle(title="Lines"))))
    assert legend.title == "Lines"


@pytest.mark.parametrize("location", sorted(LEGEND_LOCATION) if is_xy_available() else [])
@xy_available
def test_apply_style_legend_location(location: str) -> None:
    scene = _scene(legend=LegendStyle(location=cast("Any", location)))
    (legend,) = _legends(apply_style(_chart(), scene))
    assert legend.loc == LEGEND_LOCATION[location]


@xy_available
def test_apply_style_legend_horizontal_uses_one_column_per_named_mark() -> None:
    chart = xy.chart(
        xy.line(np.arange(3.0), np.arange(3.0), name="a"),
        xy.line(np.arange(3.0), np.arange(3.0), name="b"),
        xy.line(np.arange(3.0), np.arange(3.0)),
    )
    (legend,) = _legends(apply_style(chart, _scene(legend=LegendStyle(orientation="horizontal"))))
    assert legend.ncols == 2


@xy_available
def test_apply_style_legend_vertical_keeps_one_column() -> None:
    (legend,) = _legends(apply_style(_chart(), _scene(legend=LegendStyle(orientation="vertical"))))
    assert legend.ncols == 1


@xy_available
def test_apply_style_legend_horizontal_without_named_mark_has_one_column() -> None:
    chart = xy.chart(xy.line(np.arange(3.0), np.arange(3.0)))
    (legend,) = _legends(apply_style(chart, _scene(legend=LegendStyle(orientation="horizontal"))))
    assert legend.ncols == 1


@xy_available
def test_legend_locations_whole_table() -> None:
    assert LEGEND_LOCATION == {
        "top_left": "upper left",
        "top_right": "upper right",
        "bottom_left": "lower left",
        "bottom_right": "lower right",
        "top": "upper center",
        "bottom": "lower center",
        "left": "center left",
        "right": "center right",
    }


@xy_available
def test_markers() -> None:
    assert MARKERS == ("circle", "square", "triangle", "diamond", "cross", "x")
