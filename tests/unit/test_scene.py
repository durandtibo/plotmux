from __future__ import annotations

from typing import cast

import numpy as np
import pytest

from plotmux.colors.palette import DEFAULT_PALETTE
from plotmux.primitives import Bars, Line
from plotmux.scene import (
    AxesScene,
    GridScene,
    LegendStyle,
    _assign_colors,
    _build_axes,
    _collect_categories,
    build_scene,
)
from plotmux.specs import (
    BarSeries,
    BarSpec,
    GridSpec,
    HistogramSpec,
    LineSpec,
    PanelSpec,
    ScatterSpec,
    SlopeSpec,
    StackedBarSpec,
)


def _line(label: str | None = None, color: str | None = None) -> LineSpec:
    return LineSpec(x=np.array([0.0, 1.0]), y=np.array([0.0, 1.0]), label=label, color=color)


################################
#     Tests for build_scene    #
################################


def test_build_scene_panel_returns_axes_scene() -> None:
    assert isinstance(build_scene(PanelSpec(marks=(_line(),))), AxesScene)


def test_build_scene_grid_returns_grid_scene() -> None:
    assert isinstance(build_scene(GridSpec(panels=(PanelSpec(marks=(_line(),)),))), GridScene)


def test_build_scene_grid_fields() -> None:
    scene = build_scene(
        GridSpec(
            panels=(PanelSpec(marks=(_line(),)), PanelSpec(marks=(_line(),))), ncols=2, title="t"
        )
    )
    assert (len(scene.panels), scene.ncols, scene.title) == (2, 2, "t")


def test_build_scene_grid_panels_are_scenes_of_the_panels() -> None:
    panel = PanelSpec(marks=(_line(),), title="p")
    assert build_scene(GridSpec(panels=(panel,))).panels == (build_scene(panel),)


def test_build_scene_is_a_pure_function_of_the_spec() -> None:
    spec = PanelSpec(marks=(HistogramSpec(values=np.arange(11.0)), _line()))
    assert build_scene(spec) == build_scene(spec)


def test_build_scene_does_not_change_the_spec() -> None:
    spec = PanelSpec(marks=(_line(),))
    build_scene(spec)
    assert spec == PanelSpec(marks=(_line(),))


def test_build_scene_whole_axes_scene() -> None:
    spec = PanelSpec(
        marks=(_line(label="a"),),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
        xmin=1,
        xmax=2,
        ymin=3,
        ymax=4,
        background_color="#ff0000",
        legend_title="l",
        legend_location="top",
        legend_orientation="horizontal",
    )
    assert build_scene(spec) == AxesScene(
        primitives=(
            Line(
                x=np.array([0.0, 1.0]),
                y=np.array([0.0, 1.0]),
                color=DEFAULT_PALETTE[0],
                label="a",
            ),
        ),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
        xlim=(1, 2),
        ylim=(3, 4),
        background_color=(1.0, 0.0, 0.0, 1.0),
        legend=LegendStyle(title="l", location="top", orientation="horizontal"),
        categories=None,
    )


def test_build_scene_single_mark_gets_a_palette_color() -> None:
    scene = build_scene(PanelSpec(marks=(_line(),)))
    assert scene.primitives[0].color == DEFAULT_PALETTE[0]


def test_build_scene_marks_cycle_the_palette_in_order() -> None:
    scene = build_scene(PanelSpec(marks=(_line(), _line(), _line())))
    assert [p.color for p in scene.primitives] == list(DEFAULT_PALETTE[:3])


def test_build_scene_explicit_color_does_not_consume_a_slot() -> None:
    scene = build_scene(PanelSpec(marks=(_line(color="#ff0000"), _line(), _line())))
    assert [p.color for p in scene.primitives] == [
        (1.0, 0.0, 0.0, 1.0),
        DEFAULT_PALETTE[0],
        DEFAULT_PALETTE[1],
    ]


def test_build_scene_palette_cycles_after_its_last_color() -> None:
    marks = tuple(_line() for _ in range(len(DEFAULT_PALETTE) + 1))
    scene = build_scene(PanelSpec(marks=marks))
    assert scene.primitives[-1].color == DEFAULT_PALETTE[0]


def test_build_scene_stacked_series_take_a_color_each() -> None:
    mark = StackedBarSpec(
        x=np.array(["a", "b"]),
        series=(
            BarSeries(y=np.arange(2)),
            BarSeries(y=np.arange(2), color="#ff0000"),
            BarSeries(y=np.arange(2)),
        ),
    )
    scene = build_scene(PanelSpec(marks=(mark,)))
    assert [p.color for p in scene.primitives] == [
        DEFAULT_PALETTE[0],
        (1.0, 0.0, 0.0, 1.0),
        DEFAULT_PALETTE[1],
    ]


def test_build_scene_colors_are_the_same_in_a_panel_and_in_a_grid() -> None:
    panel = PanelSpec(marks=(_line(), _line()))
    assert build_scene(GridSpec(panels=(panel,))).panels[0] == build_scene(panel)


def test_build_scene_slope_uses_the_extent_of_the_siblings() -> None:
    scene = build_scene(PanelSpec(marks=(_line(), SlopeSpec(gradient=2.0, intercept=1.0))))
    assert scene.primitives[1].x.tolist() == [0.0, 1.0]


def test_build_scene_slope_uses_the_limits() -> None:
    scene = build_scene(PanelSpec(marks=(SlopeSpec(gradient=2.0),), xmin=-1, xmax=3))
    assert cast("Line", scene.primitives[0]).y.tolist() == [-2.0, 6.0]


def test_build_scene_slope_in_a_grid() -> None:
    panel = PanelSpec(marks=(SlopeSpec(gradient=1.0),), xmin=0, xmax=1)
    assert build_scene(GridSpec(panels=(panel,))).panels[0].primitives[0].x.tolist() == [0.0, 1.0]


def test_build_scene_stacked_bar_in_a_layer() -> None:
    stacked = StackedBarSpec(x=np.arange(2), series=(BarSeries(y=np.arange(2)),))
    scene = build_scene(PanelSpec(marks=(stacked, _line())))
    assert len(scene.primitives) == 2


def test_build_scene_primitives_follow_the_mark_order() -> None:
    scene = build_scene(PanelSpec(marks=(HistogramSpec(values=np.arange(5.0)), _line())))
    assert [type(p).__name__ for p in scene.primitives] == ["Bars", "Line"]


def test_build_scene_scatter_primitive() -> None:
    scene = build_scene(PanelSpec(marks=(ScatterSpec(x=np.arange(2), y=np.arange(2)),)))
    assert type(scene.primitives[0]).__name__ == "Points"


#############################
#     Tests for the legend  #
#############################


def test_build_scene_no_label_has_no_legend() -> None:
    assert build_scene(PanelSpec(marks=(_line(),), legend_title="l")).legend is None


def test_build_scene_one_label_has_a_legend() -> None:
    assert build_scene(PanelSpec(marks=(_line(), _line(label="a")))).legend == LegendStyle()


def test_build_scene_legend_style_comes_from_the_panel() -> None:
    scene = build_scene(
        PanelSpec(
            marks=(_line(label="a"),),
            legend_title="l",
            legend_location="bottom_left",
            legend_orientation="vertical",
        )
    )
    assert scene.legend == LegendStyle(title="l", location="bottom_left", orientation="vertical")


def test_build_scene_stacked_series_label_makes_a_legend() -> None:
    mark = StackedBarSpec(x=np.arange(2), series=(BarSeries(y=np.arange(2), label="s"),))
    assert build_scene(PanelSpec(marks=(mark,))).legend == LegendStyle()


def test_build_scene_unlabeled_stacked_series_have_no_legend() -> None:
    mark = StackedBarSpec(x=np.arange(2), series=(BarSeries(y=np.arange(2)),))
    assert build_scene(PanelSpec(marks=(mark,))).legend is None


def test_build_scene_unlabeled_stacked_series_keep_no_label() -> None:
    mark = StackedBarSpec(x=np.arange(2), series=(BarSeries(y=np.arange(2)),))
    assert build_scene(PanelSpec(marks=(mark,))).primitives[0].label is None


###################################
#     Tests for the categories    #
###################################


def test_build_scene_numeric_x_has_no_categories() -> None:
    assert build_scene(PanelSpec(marks=(_line(),))).categories is None


def test_build_scene_categories_in_order_of_first_appearance() -> None:
    bar = BarSpec(x=np.array(["b", "a", "b"]), y=np.arange(3))
    assert build_scene(PanelSpec(marks=(bar,))).categories == ("b", "a")


def test_build_scene_categories_are_shared_by_the_marks() -> None:
    first = BarSpec(x=np.array(["b", "a"]), y=np.arange(2))
    second = BarSpec(x=np.array(["c", "a"]), y=np.arange(2))
    assert build_scene(PanelSpec(marks=(first, second))).categories == ("b", "a", "c")


def test_build_scene_categories_of_a_stacked_bar() -> None:
    mark = StackedBarSpec(x=np.array(["x", "y"]), series=(BarSeries(y=np.arange(2)),))
    assert build_scene(PanelSpec(marks=(mark,))).categories == ("x", "y")


############################
#     Tests for _build_axes#
############################


def test_build_axes_limits_default_to_autoscale() -> None:
    scene = _build_axes(PanelSpec(marks=(_line(),)))
    assert (scene.xlim, scene.ylim) == ((None, None), (None, None))


def test_build_axes_histogram_range_is_not_an_axis_limit() -> None:
    scene = _build_axes(PanelSpec(marks=(HistogramSpec(values=np.arange(11.0), xmin=2, xmax=4),)))
    assert scene.xlim == (None, None)


#################################
#     Tests for _assign_colors  #
#################################


def test_assign_colors_empty() -> None:
    assert _assign_colors(()) == ()


def test_assign_colors_keeps_the_other_fields() -> None:
    line = Line(x=np.arange(2.0), y=np.arange(2.0), linewidth=3.0, label="a")
    (result,) = _assign_colors((line,))
    assert result == Line(
        x=np.arange(2.0), y=np.arange(2.0), color=DEFAULT_PALETTE[0], linewidth=3.0, label="a"
    )


def test_assign_colors_does_not_change_the_input() -> None:
    line = Line(x=np.arange(2.0), y=np.arange(2.0))
    _assign_colors((line,))
    assert line.color is None


########################################
#     Tests for _collect_categories    #
########################################


def _bars(x: list[str] | list[float]) -> Bars:
    return Bars(x=np.array(x), height=np.ones(len(x)), base=np.zeros(len(x)), width=0.8)


def test_collect_categories_numeric_is_none() -> None:
    assert _collect_categories((_bars([1.0, 2.0]),)) is None


def test_collect_categories_no_primitive_is_none() -> None:
    assert _collect_categories(()) is None


def test_collect_categories_removes_duplicates() -> None:
    assert _collect_categories((_bars(["a", "b", "a"]),)) == ("a", "b")


def test_collect_categories_bytes() -> None:
    bars = Bars(x=np.array([b"a", b"b"]), height=np.ones(2), base=np.zeros(2), width=0.8)
    assert _collect_categories((bars,)) == ("a", "b")


def test_collect_categories_of_a_line() -> None:
    line = Line(x=np.array(["a", "b"]), y=np.arange(2.0))
    assert _collect_categories((line,)) == ("a", "b")


###############################
#     Tests for LegendStyle   #
###############################


def test_legend_style_defaults() -> None:
    assert LegendStyle() == LegendStyle(title=None, location=None, orientation=None)


@pytest.mark.parametrize("title", ["a", None])
def test_legend_style_title(title: str | None) -> None:
    assert LegendStyle(title=title).title == title
