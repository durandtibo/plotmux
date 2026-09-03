from __future__ import annotations

import numpy as np
import pytest

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


def test_stacked_bar_spec_default_colors_are_distinct() -> None:
    spec = StackedBarSpec(
        x=np.arange(3), series=(BarSeries(y=np.arange(3)), BarSeries(y=np.arange(3)))
    )
    assert spec.series[0].color != spec.series[1].color


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
        spec.width = 0.5


def test_stacked_bar_spec_common_style() -> None:
    spec = StackedBarSpec(
        x=np.arange(3),
        series=(BarSeries(y=np.arange(3)),),
        title="t",
        xlabel="x",
        ylabel="y",
    )
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
