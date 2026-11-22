from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidColorError, InvalidSpecError
from plotmux.specs import (
    BarSpec,
    GridSpec,
    HistogramSpec,
    LineSpec,
    PanelSpec,
    SlopeSpec,
)
from plotmux.specs.panel import LEGEND_LOCATIONS, _check_choice, _check_order

LINE = LineSpec(x=np.arange(5), y=np.arange(5))

###############################
#     Tests for PanelSpec     #
###############################


def test_panel_spec_defaults() -> None:
    spec = PanelSpec(marks=(LINE,))
    assert (spec.title, spec.xlabel, spec.ylabel) == (None, None, None)
    assert (spec.xscale, spec.yscale) == ("linear", "linear")
    assert (spec.xmin, spec.xmax, spec.ymin, spec.ymax) == (None, None, None, None)
    assert spec.background_color is None
    assert (spec.legend_title, spec.legend_location, spec.legend_orientation) == (None, None, None)


def test_panel_spec_custom() -> None:
    spec = PanelSpec(
        marks=(LINE,),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
        xmin=1,
        xmax=2,
        ymin=3,
        ymax=4,
        legend_title="l",
        legend_location="top_left",
        legend_orientation="horizontal",
    )
    assert (spec.title, spec.xlabel, spec.ylabel, spec.xscale, spec.yscale) == (
        "t",
        "x",
        "y",
        "log",
        "log",
    )
    assert (spec.xmin, spec.xmax, spec.ymin, spec.ymax) == (1, 2, 3, 4)
    assert (spec.legend_title, spec.legend_location, spec.legend_orientation) == (
        "l",
        "top_left",
        "horizontal",
    )


def test_panel_spec_is_frozen() -> None:
    with pytest.raises(AttributeError):
        cast("Any", PanelSpec(marks=(LINE,))).title = "t"


def test_panel_spec_marks_list_becomes_tuple() -> None:
    assert PanelSpec(marks=cast("Any", [LINE])).marks == (LINE,)


def test_panel_spec_equal() -> None:
    assert PanelSpec(marks=(LINE,), title="a") == PanelSpec(marks=(LINE,), title="a")


def test_panel_spec_not_equal_with_different_title() -> None:
    assert PanelSpec(marks=(LINE,), title="a") != PanelSpec(marks=(LINE,), title="b")


def test_panel_spec_empty_marks_raises() -> None:
    with pytest.raises(InvalidSpecError, match="marks must contain at least one mark"):
        PanelSpec(marks=())


def test_panel_spec_marks_must_be_marks() -> None:
    nested = PanelSpec(marks=(LINE,))
    with pytest.raises(
        InvalidSpecError, match="marks must hold MarkSpec objects, but received PanelSpec"
    ):
        PanelSpec(marks=cast("Any", (nested,)))


def test_panel_spec_grid_is_not_a_mark() -> None:
    grid = GridSpec(panels=(PanelSpec(marks=(LINE,)),))
    with pytest.raises(InvalidSpecError, match="but received GridSpec"):
        PanelSpec(marks=cast("Any", (grid,)))


def test_panel_spec_background_color_is_parsed() -> None:
    assert PanelSpec(marks=(LINE,), background_color="#ff0000").background_color == (
        1.0,
        0.0,
        0.0,
        1.0,
    )


def test_panel_spec_invalid_background_color_raises() -> None:
    with pytest.raises(InvalidColorError, match="Invalid color"):
        PanelSpec(marks=(LINE,), background_color="not-a-color")


@pytest.mark.parametrize("scale", ["linear", "log"])
def test_panel_spec_scales(scale: str) -> None:
    assert PanelSpec(marks=(LINE,), xscale=cast("Any", scale)).xscale == scale


def test_panel_spec_invalid_xscale_raises() -> None:
    with pytest.raises(InvalidSpecError, match="xscale must be one of"):
        PanelSpec(marks=(LINE,), xscale=cast("Any", "symlog"))


def test_panel_spec_invalid_yscale_raises() -> None:
    with pytest.raises(InvalidSpecError, match="yscale must be one of"):
        PanelSpec(marks=(LINE,), yscale=cast("Any", "symlog"))


@pytest.mark.parametrize("location", sorted(LEGEND_LOCATIONS))
def test_panel_spec_legend_locations(location: str) -> None:
    assert (
        PanelSpec(marks=(LINE,), legend_location=cast("Any", location)).legend_location == location
    )


def test_panel_spec_legend_location_best_raises() -> None:
    with pytest.raises(InvalidSpecError, match="legend_location must be one of"):
        PanelSpec(marks=(LINE,), legend_location=cast("Any", "best"))


def test_panel_spec_invalid_legend_orientation_raises() -> None:
    with pytest.raises(InvalidSpecError, match="legend_orientation must be one of"):
        PanelSpec(marks=(LINE,), legend_orientation=cast("Any", "diagonal"))


def test_panel_spec_xmin_greater_than_xmax_raises() -> None:
    with pytest.raises(InvalidSpecError, match="xmin must not be greater than xmax"):
        PanelSpec(marks=(LINE,), xmin=10, xmax=0)


def test_panel_spec_ymin_greater_than_ymax_raises() -> None:
    with pytest.raises(InvalidSpecError, match="ymin must not be greater than ymax"):
        PanelSpec(marks=(LINE,), ymin=10, ymax=0)


def test_panel_spec_equal_limits_do_not_raise() -> None:
    assert PanelSpec(marks=(LINE,), ymin=5, ymax=5).ymin == 5


def test_panel_spec_mixing_categorical_and_numeric_raises() -> None:
    bar = BarSpec(x=np.array(["a", "b"]), y=np.arange(2))
    with pytest.raises(InvalidSpecError, match="must not mix a categorical x"):
        PanelSpec(marks=(bar, LINE))


def test_panel_spec_categorical_marks_do_not_raise() -> None:
    bar = BarSpec(x=np.array(["a", "b"]), y=np.arange(2))
    assert len(PanelSpec(marks=(bar, bar)).marks) == 2


def test_panel_spec_slope_alone_raises() -> None:
    with pytest.raises(InvalidSpecError, match="needs the x extent of the panel"):
        PanelSpec(marks=(SlopeSpec(gradient=1.0),))


def test_panel_spec_slope_with_one_limit_raises() -> None:
    with pytest.raises(InvalidSpecError, match="needs the x extent of the panel"):
        PanelSpec(marks=(SlopeSpec(gradient=1.0),), xmin=0)


def test_panel_spec_slope_with_limits() -> None:
    assert len(PanelSpec(marks=(SlopeSpec(gradient=1.0),), xmin=0, xmax=1).marks) == 1


def test_panel_spec_slope_with_data_sibling() -> None:
    assert len(PanelSpec(marks=(LINE, SlopeSpec(gradient=1.0))).marks) == 2


def test_panel_spec_slope_with_categorical_sibling_raises() -> None:
    bar = BarSpec(x=np.array(["a", "b"]), y=np.arange(2))
    with pytest.raises(InvalidSpecError, match="needs the x extent of the panel"):
        PanelSpec(marks=(bar, SlopeSpec(gradient=1.0)))


def test_panel_spec_slope_with_one_limit_and_a_sibling() -> None:
    assert len(PanelSpec(marks=(LINE, SlopeSpec(gradient=1.0)), xmin=-1).marks) == 2


#####################################
#     Tests for PanelSpec.x_extent  #
#####################################


def test_panel_spec_x_extent_from_one_mark() -> None:
    assert PanelSpec(marks=(LINE,)).x_extent() == (0.0, 4.0)


def test_panel_spec_x_extent_union_of_marks() -> None:
    other = LineSpec(x=np.array([-2.0, 10.0]), y=np.arange(2))
    assert PanelSpec(marks=(LINE, other)).x_extent() == (-2.0, 10.0)


def test_panel_spec_x_extent_explicit_limits_win() -> None:
    assert PanelSpec(marks=(LINE,), xmin=-1, xmax=10).x_extent() == (-1, 10)


def test_panel_spec_x_extent_one_explicit_limit() -> None:
    assert PanelSpec(marks=(LINE,), xmax=10).x_extent() == (0.0, 10)


def test_panel_spec_x_extent_explicit_limits_without_data() -> None:
    assert PanelSpec(marks=(SlopeSpec(gradient=1.0),), xmin=0, xmax=1).x_extent() == (0, 1)


def test_panel_spec_x_extent_uses_the_range_of_a_histogram() -> None:
    hist = HistogramSpec(values=np.arange(101.0), xmin=10, xmax=20)
    assert PanelSpec(marks=(hist,)).x_extent() == (10.0, 20.0)


def test_panel_spec_x_extent_categorical_is_none() -> None:
    bar = BarSpec(x=np.array(["a", "b"]), y=np.arange(2))
    assert PanelSpec(marks=(bar,)).x_extent() is None


def test_panel_spec_x_extent_includes_the_half_width_of_bars() -> None:
    assert PanelSpec(marks=(BarSpec(x=np.arange(3), y=np.arange(3), width=1.0),)).x_extent() == (
        -0.5,
        2.5,
    )


#################################
#     Tests for _check_choice   #
#################################


def test_check_choice_valid() -> None:
    _check_choice("name", "a", ("a", "b"))


def test_check_choice_invalid_raises() -> None:
    with pytest.raises(
        InvalidSpecError, match=r"name must be one of \['a', 'b'\], but received 'c'"
    ):
        _check_choice("name", "c", ("a", "b"))


#################################
#     Tests for _check_order    #
#################################


@pytest.mark.parametrize(("low", "high"), [(None, None), (1, None), (None, 1), (1, 1), (0, 1)])
def test_check_order_valid(low: float | None, high: float | None) -> None:
    _check_order("lo", low, "hi", high)


def test_check_order_invalid_raises() -> None:
    with pytest.raises(
        InvalidSpecError, match=r"lo must not be greater than hi, but received lo=2 and hi=1"
    ):
        _check_order("lo", 2, "hi", 1)
