from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidColorError, InvalidSpecError
from plotmux.primitives import Bars
from plotmux.specs import BarSeries, StackedBarSpec

######################################
#     Tests for StackedBarSpec     #
######################################


def test_stacked_bar_spec_defaults() -> None:
    spec = StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),))
    assert len(spec.series) == 1
    assert spec.width == 0.8
    assert spec.alpha is None


def test_stacked_bar_spec_categorical_x() -> None:
    spec = StackedBarSpec(
        x=np.array(["Apples", "Pears", "Nectarines"]),
        series=(BarSeries(y=np.array([2, 1, 4])),),
    )
    assert spec.x.tolist() == ["Apples", "Pears", "Nectarines"]


def test_stacked_bar_spec_series_order_preserved() -> None:
    s1 = BarSeries(y=np.arange(3), label="2015")
    s2 = BarSeries(y=np.arange(3), label="2016")
    spec = StackedBarSpec(x=np.arange(3), series=(s1, s2))
    assert spec.series[0].label == "2015"
    assert spec.series[1].label == "2016"


def test_stacked_bar_spec_explicit_color_normalized() -> None:
    spec = StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3), color="red"),))
    assert spec.series[0].color == (1.0, 0.0, 0.0, 1.0)


def test_stacked_bar_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3), color="not-a-color"),))


def test_stacked_bar_spec_empty_series() -> None:
    with pytest.raises(ValueError, match="series must contain at least one BarSeries"):
        StackedBarSpec(x=np.arange(3), series=())


def test_stacked_bar_spec_x_not_1d() -> None:
    with pytest.raises(ValueError, match="x must be 1-dimensional"):
        StackedBarSpec(x=np.ones((3, 2)), series=(BarSeries(y=np.arange(3)),))


def test_stacked_bar_spec_mismatched_series_length() -> None:
    with pytest.raises(ValueError, match="each series' y must have the same length as x"):
        StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(5)),))


def test_stacked_bar_spec_series_y_not_1d() -> None:
    with pytest.raises(ValueError, match="each series' y must have the same length as x"):
        StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.ones((3, 2))),))


@pytest.mark.parametrize("width", [0, -1, -10.5])
def test_stacked_bar_spec_invalid_width(width: float) -> None:
    with pytest.raises(ValueError, match="width must be a positive number"):
        StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),), width=width)


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_stacked_bar_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),), alpha=alpha)


def test_stacked_bar_spec_is_frozen() -> None:
    spec = StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),))
    with pytest.raises(AttributeError):
        cast("Any", spec).width = 0.5


def test_stacked_bar_spec_does_not_alias_the_input_x() -> None:
    x = np.array([0.0, 1.0, 2.0])
    spec = StackedBarSpec(x=x, series=(BarSeries(y=np.arange(3)),))
    x[0] = 99
    assert spec.x[0] == 0.0


def test_stacked_bar_spec_does_not_alias_the_input_series_y() -> None:
    y = np.array([0.0, 1.0, 2.0])
    spec = StackedBarSpec(x=np.arange(3), series=(BarSeries(y=y),))
    y[0] = 99
    assert spec.series[0].y[0] == 0.0


def test_stacked_bar_spec_x_is_read_only() -> None:
    spec = StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),))
    with pytest.raises(ValueError, match="read-only"):
        spec.x[0] = 1


def test_stacked_bar_spec_series_y_is_read_only() -> None:
    spec = StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),))
    with pytest.raises(ValueError, match="read-only"):
        spec.series[0].y[0] = 1


def test_stacked_bar_spec_equal() -> None:
    assert StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3), label="a"),)) == (
        StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3), label="a"),))
    )


def test_stacked_bar_spec_not_equal_with_different_series() -> None:
    assert StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),)) != (
        StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(1, 4)),))
    )


def test_stacked_bar_spec_hash_raises() -> None:
    spec = StackedBarSpec(x=np.arange(3), series=(BarSeries(y=np.arange(3)),))
    with pytest.raises(TypeError, match="unhashable type: 'StackedBarSpec'"):
        hash(spec)


def test_bar_series_equal() -> None:
    assert BarSeries(y=np.arange(3), label="a") == BarSeries(y=np.arange(3), label="a")


def test_bar_series_not_equal_with_different_y() -> None:
    assert BarSeries(y=np.arange(3)) != BarSeries(y=np.arange(1, 4))


##############################################
#     Tests for StackedBarSpec lowering      #
##############################################


def _stacked() -> StackedBarSpec:
    return StackedBarSpec(
        x=np.array(["a", "b"]),
        series=(
            BarSeries(y=np.array([1, 2]), label="s0", color="#ff0000"),
            BarSeries(y=np.array([3, 4]), label="s1"),
            BarSeries(y=np.array([5, 6])),
        ),
        width=0.5,
        alpha=0.5,
    )


def test_stacked_bar_spec_to_primitives() -> None:
    assert _stacked().to_primitives(None) == (
        Bars(
            x=np.array(["a", "b"]),
            height=np.array([1.0, 2.0]),
            base=np.array([0.0, 0.0]),
            width=0.5,
            color=(1.0, 0.0, 0.0, 1.0),
            alpha=0.5,
            label="s0",
        ),
        Bars(
            x=np.array(["a", "b"]),
            height=np.array([3.0, 4.0]),
            base=np.array([1.0, 2.0]),
            width=0.5,
            color=None,
            alpha=0.5,
            label="s1",
        ),
        Bars(
            x=np.array(["a", "b"]),
            height=np.array([5.0, 6.0]),
            base=np.array([4.0, 6.0]),
            width=0.5,
            color=None,
            alpha=0.5,
            label=None,
        ),
    )


def test_stacked_bar_spec_to_primitives_does_not_change_the_series() -> None:
    spec = _stacked()
    spec.to_primitives(None)
    assert spec.series[0].y.tolist() == [1, 2]


def test_stacked_bar_spec_label_raises() -> None:
    with pytest.raises(InvalidSpecError, match="label and color must be set on each BarSeries"):
        StackedBarSpec(x=np.arange(2), series=(BarSeries(y=np.arange(2)),), label="a")


def test_stacked_bar_spec_color_raises() -> None:
    with pytest.raises(InvalidSpecError, match="label and color must be set on each BarSeries"):
        StackedBarSpec(x=np.arange(2), series=(BarSeries(y=np.arange(2)),), color="red")


def test_stacked_bar_spec_x_extent_includes_the_half_width() -> None:
    spec = StackedBarSpec(x=np.array([0.0, 4.0]), series=(BarSeries(y=np.arange(2)),), width=2.0)
    assert spec.x_extent() == (-1.0, 5.0)


def test_stacked_bar_spec_x_extent_categorical() -> None:
    assert _stacked().x_extent() is None


def test_stacked_bar_spec_is_categorical_strings() -> None:
    assert _stacked().is_categorical() is True


def test_stacked_bar_spec_is_categorical_numeric() -> None:
    spec = StackedBarSpec(x=np.arange(2), series=(BarSeries(y=np.arange(2)),))
    assert spec.is_categorical() is False


def test_bar_series_color_is_parsed() -> None:
    assert BarSeries(y=np.arange(2), color="#ff0000").color == (1.0, 0.0, 0.0, 1.0)


def test_bar_series_invalid_color_raises() -> None:
    with pytest.raises(InvalidColorError, match="Invalid color"):
        BarSeries(y=np.arange(2), color="not-a-color")
