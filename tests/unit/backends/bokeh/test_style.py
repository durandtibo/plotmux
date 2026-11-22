from __future__ import annotations

import math
from typing import Any, cast

import pytest

from plotmux.scene import AxesScene, LegendStyle
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.models import Legend
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.style import (
        LEGEND_LOCATIONS,
        MARKERS,
        _apply_legend,
        apply_style,
        rgba_to_bokeh,
    )


def _fig(*, label: str | None = None, **kwargs: Any) -> Any:
    fig = figure(**kwargs)
    fig.line([0, 1], [0, 1], legend_label=label) if label else fig.line([0, 1], [0, 1])
    return fig


def _styled(fig: Any, scene: AxesScene) -> Any:
    return apply_style(fig, scene)


def _scene(**kwargs: Any) -> AxesScene:
    return AxesScene(primitives=(), **kwargs)


##################################
#     Tests for rgba_to_bokeh    #
##################################


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        pytest.param((1.0, 0.0, 0.0, 1.0), (255, 0, 0, 1.0), id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), (0, 0, 0, 0.0), id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), (128, 128, 128, 0.5), id="rounding"),
    ],
)
@bokeh_available
def test_rgba_to_bokeh(color: tuple[float, ...], expected: tuple[float, ...]) -> None:
    assert rgba_to_bokeh(cast("Any", color)) == expected


################################
#     Tests for apply_style    #
################################


@bokeh_available
def test_apply_style_returns_the_figure() -> None:
    fig = _fig()
    assert apply_style(fig, _scene()) is fig


@bokeh_available
def test_apply_style_title() -> None:
    assert _styled(_fig(), _scene(title="t")).title.text == "t"


@bokeh_available
def test_apply_style_no_title() -> None:
    assert _styled(_fig(), _scene()).title.text == ""


@bokeh_available
def test_apply_style_xlabel() -> None:
    assert _styled(_fig(), _scene(xlabel="x")).xaxis.axis_label == "x"


@bokeh_available
def test_apply_style_ylabel() -> None:
    assert _styled(_fig(), _scene(ylabel="y")).yaxis.axis_label == "y"


@bokeh_available
def test_apply_style_no_labels() -> None:
    fig = _styled(_fig(), _scene())
    assert (fig.xaxis.axis_label, fig.yaxis.axis_label) == (None, None)


@bokeh_available
def test_apply_style_background_color() -> None:
    fig = _styled(_fig(), _scene(background_color=(1.0, 0.0, 0.0, 1.0)))
    assert fig.background_fill_color == "rgb(255, 0, 0)"


@bokeh_available
def test_apply_style_no_background_color_keeps_the_default() -> None:
    assert _styled(_fig(), _scene()).background_fill_color == "#ffffff"


@bokeh_available
def test_apply_style_xlim() -> None:
    fig = _styled(_fig(), _scene(xlim=(1.0, 2.0)))
    assert (fig.x_range.start, fig.x_range.end) == (1.0, 2.0)


@bokeh_available
def test_apply_style_xlim_lower_bound_only() -> None:
    fig = _styled(_fig(), _scene(xlim=(1.0, None)))
    assert fig.x_range.start == 1.0


@bokeh_available
def test_apply_style_xlim_upper_bound_only() -> None:
    fig = _styled(_fig(), _scene(xlim=(None, 2.0)))
    assert fig.x_range.end == 2.0


@bokeh_available
def test_apply_style_ylim() -> None:
    fig = _styled(_fig(), _scene(ylim=(1.0, 2.0)))
    assert (fig.y_range.start, fig.y_range.end) == (1.0, 2.0)


@bokeh_available
def test_apply_style_categorical_x_range_is_kept() -> None:
    fig = _styled(_fig(x_range=["a", "b"]), _scene(categories=("a", "b"), xlim=(1.0, 2.0)))
    assert list(fig.x_range.factors) == ["a", "b"]


@bokeh_available
def test_apply_style_no_limits_autoscale() -> None:
    fig = _styled(_fig(), _scene())
    assert math.isnan(fig.x_range.start)


@bokeh_available
def test_apply_style_legend() -> None:
    fig = _styled(_fig(label="a"), _scene(legend=LegendStyle(title="Lines")))
    assert fig.legend[0].title == "Lines"


#################################
#     Tests for _apply_legend   #
#################################


@bokeh_available
def test_apply_legend_without_legend_in_the_scene_is_a_noop() -> None:
    fig = _fig(label="a")
    _apply_legend(fig, _scene())
    assert fig.legend[0].title is None


@bokeh_available
def test_apply_legend_without_labeled_glyph_is_a_noop() -> None:
    _apply_legend(_fig(), _scene(legend=LegendStyle(title="t")))


@bokeh_available
def test_apply_legend_title() -> None:
    fig = _fig(label="a")
    _apply_legend(fig, _scene(legend=LegendStyle(title="Lines")))
    assert fig.legend[0].title == "Lines"


@bokeh_available
def test_apply_legend_no_title_keeps_the_default() -> None:
    fig = _fig(label="a")
    _apply_legend(fig, _scene(legend=LegendStyle()))
    assert fig.legend[0].title is None


@pytest.mark.parametrize("location", LEGEND_LOCATIONS)
@bokeh_available
def test_apply_legend_location(location: str) -> None:
    fig = _fig(label="a")
    _apply_legend(fig, _scene(legend=LegendStyle(location=cast("Any", location))))
    assert fig.legend[0].location == location


@pytest.mark.parametrize("orientation", ["vertical", "horizontal"])
@bokeh_available
def test_apply_legend_orientation(orientation: str) -> None:
    fig = _fig(label="a")
    _apply_legend(fig, _scene(legend=LegendStyle(orientation=cast("Any", orientation))))
    assert fig.legend[0].orientation == orientation


@bokeh_available
def test_apply_legend_is_a_legend_model() -> None:
    assert isinstance(_fig(label="a").legend[0], Legend)


@bokeh_available
def test_markers() -> None:
    assert MARKERS == ("circle", "square", "triangle", "diamond", "cross", "x")
