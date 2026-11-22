from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import pytest

from plotmux.scene import AxesScene, LegendStyle
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if TYPE_CHECKING:
    from matplotlib.axes import Axes

if is_matplotlib_available():
    from matplotlib.figure import Figure

    from plotmux.backends.matplotlib.style import (
        LEGEND_LOCATION,
        MARKER_STYLE,
        _apply_legend,
        apply_style,
    )


def _axes(*, label: str | None = None) -> Axes:
    ax = Figure().subplots()
    ax.plot([0, 1], [0, 1], label=label)
    return ax


def _legend(ax: Axes) -> Any:
    legend = ax.get_legend()
    assert legend is not None
    return legend


def _scene(**kwargs: Any) -> AxesScene:
    return AxesScene(primitives=(), **kwargs)


#################################
#     Tests for apply_style     #
#################################


@matplotlib_available
def test_apply_style_returns_the_axes() -> None:
    ax = _axes()
    assert apply_style(ax, _scene()) is ax


@matplotlib_available
def test_apply_style_title() -> None:
    assert apply_style(_axes(), _scene(title="t")).get_title() == "t"


@matplotlib_available
def test_apply_style_no_title() -> None:
    assert apply_style(_axes(), _scene()).get_title() == ""


@matplotlib_available
def test_apply_style_xlabel() -> None:
    assert apply_style(_axes(), _scene(xlabel="x")).get_xlabel() == "x"


@matplotlib_available
def test_apply_style_ylabel() -> None:
    assert apply_style(_axes(), _scene(ylabel="y")).get_ylabel() == "y"


@matplotlib_available
def test_apply_style_default_scales_are_linear() -> None:
    ax = apply_style(_axes(), _scene())
    assert (ax.get_xscale(), ax.get_yscale()) == ("linear", "linear")


@matplotlib_available
def test_apply_style_xscale() -> None:
    assert apply_style(_axes(), _scene(xscale="log")).get_xscale() == "log"


@matplotlib_available
def test_apply_style_yscale() -> None:
    assert apply_style(_axes(), _scene(yscale="log")).get_yscale() == "log"


@matplotlib_available
def test_apply_style_background_color() -> None:
    ax = apply_style(_axes(), _scene(background_color=(1.0, 0.0, 0.0, 1.0)))
    assert ax.get_facecolor() == (1.0, 0.0, 0.0, 1.0)


@matplotlib_available
def test_apply_style_no_background_color_keeps_the_default() -> None:
    assert apply_style(_axes(), _scene()).get_facecolor() == (1.0, 1.0, 1.0, 1.0)


@matplotlib_available
def test_apply_style_xlim() -> None:
    assert apply_style(_axes(), _scene(xlim=(2.0, 5.0))).get_xlim() == (2.0, 5.0)


@matplotlib_available
def test_apply_style_xlim_lower_bound_only() -> None:
    assert apply_style(_axes(), _scene(xlim=(-3.0, None))).get_xlim()[0] == -3.0


@matplotlib_available
def test_apply_style_xlim_upper_bound_only() -> None:
    assert apply_style(_axes(), _scene(xlim=(None, 7.0))).get_xlim()[1] == 7.0


@matplotlib_available
def test_apply_style_ylim() -> None:
    assert apply_style(_axes(), _scene(ylim=(2.0, 5.0))).get_ylim() == (2.0, 5.0)


@matplotlib_available
def test_apply_style_no_limits_autoscale() -> None:
    assert apply_style(_axes(), _scene()).get_xlim() == pytest.approx((-0.05, 1.05))


@matplotlib_available
def test_apply_style_no_legend_in_the_scene_draws_none() -> None:
    assert apply_style(_axes(label="a"), _scene()).get_legend() is None


@matplotlib_available
def test_apply_style_legend() -> None:
    assert apply_style(_axes(label="a"), _scene(legend=LegendStyle())).get_legend() is not None


########################################
#     Tests for _apply_legend          #
########################################


@matplotlib_available
def test_apply_legend_without_legend_is_a_noop() -> None:
    ax = _axes(label="a")
    _apply_legend(ax, _scene())
    assert ax.get_legend() is None


@matplotlib_available
def test_apply_legend_title() -> None:
    ax = _axes(label="a")
    _apply_legend(ax, _scene(legend=LegendStyle(title="Lines")))
    assert _legend(ax).get_title().get_text() == "Lines"


@matplotlib_available
def test_apply_legend_no_title() -> None:
    ax = _axes(label="a")
    _apply_legend(ax, _scene(legend=LegendStyle()))
    assert _legend(ax).get_title().get_text() == ""


@pytest.mark.parametrize("location", sorted(LEGEND_LOCATION) if is_matplotlib_available() else [])
@matplotlib_available
def test_apply_legend_location(location: str) -> None:
    ax = _axes(label="a")
    _apply_legend(ax, _scene(legend=LegendStyle(location=cast("Any", location))))
    assert (
        _legend(ax)._loc
        == {
            "upper left": 2,
            "upper right": 1,
            "lower left": 3,
            "lower right": 4,
            "upper center": 9,
            "lower center": 8,
            "center left": 6,
            "center right": 7,
        }[LEGEND_LOCATION[location]]
    )


@matplotlib_available
def test_apply_legend_horizontal_orientation_uses_one_row() -> None:
    ax = Figure().subplots()
    ax.plot([0, 1], [0, 1], label="a")
    ax.plot([0, 1], [1, 0], label="b")
    _apply_legend(ax, _scene(legend=LegendStyle(orientation="horizontal")))
    assert _legend(ax)._ncols == 2


@matplotlib_available
def test_apply_legend_vertical_orientation_keeps_one_column() -> None:
    ax = Figure().subplots()
    ax.plot([0, 1], [0, 1], label="a")
    ax.plot([0, 1], [1, 0], label="b")
    _apply_legend(ax, _scene(legend=LegendStyle(orientation="vertical")))
    assert _legend(ax)._ncols == 1


@matplotlib_available
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


@matplotlib_available
def test_marker_style_whole_table() -> None:
    assert MARKER_STYLE == {
        "circle": "o",
        "square": "s",
        "triangle": "^",
        "diamond": "D",
        "cross": "+",
        "x": "x",
    }
