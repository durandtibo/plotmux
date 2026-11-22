from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.primitives import Bars
from plotmux.specs import BarSpec

##############################
#     Tests for BarSpec     #
##############################


def test_bar_spec_defaults() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10))
    assert spec.label is None
    assert spec.color is None
    assert spec.width == 0.8


def test_bar_spec_custom() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10), label="my-bar", color="#ff0000", width=0.5)
    assert spec.label == "my-bar"
    assert spec.color == (1.0, 0.0, 0.0, 1.0)
    assert spec.width == 0.5


def test_bar_spec_empty_arrays() -> None:
    spec = BarSpec(x=np.array([]), y=np.array([]))
    assert spec.x.shape == (0,)


def test_bar_spec_width_small_positive_boundary() -> None:
    assert BarSpec(x=np.arange(10), y=np.arange(10), width=1e-9).width == 1e-9


# --- color parsing ---


def test_bar_spec_color_named() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_bar_spec_color_rgba_tuple() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_bar_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        BarSpec(x=np.arange(10), y=np.arange(10), color="not-a-color")


# --- common style ---


# --- frozen / error cases ---


def test_bar_spec_is_frozen() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(AttributeError):
        cast("Any", spec).label = "new-label"


def test_bar_spec_mismatched_length() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        BarSpec(x=np.arange(10), y=np.arange(5))


@pytest.mark.parametrize("width", [0, -1, -10.5])
def test_bar_spec_invalid_width(width: float) -> None:
    with pytest.raises(ValueError, match="width must be a positive number"):
        BarSpec(x=np.arange(10), y=np.arange(10), width=width)


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_bar_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        BarSpec(x=np.arange(10), y=np.arange(10), alpha=alpha)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_bar_spec_alpha_boundary_values(alpha: float) -> None:
    assert BarSpec(x=np.arange(10), y=np.arange(10), alpha=alpha).alpha == alpha


def test_bar_spec_does_not_alias_the_input_x() -> None:
    x = np.arange(5, dtype=float)
    spec = BarSpec(x=x, y=np.arange(5))
    x[0] = 99
    assert spec.x[0] == 0.0


def test_bar_spec_does_not_alias_the_input_y() -> None:
    y = np.arange(5, dtype=float)
    spec = BarSpec(x=np.arange(5), y=y)
    y[0] = 99
    assert spec.y[0] == 0.0


def test_bar_spec_x_is_read_only() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    with pytest.raises(ValueError, match="read-only"):
        spec.x[0] = 1


def test_bar_spec_y_is_read_only() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    with pytest.raises(ValueError, match="read-only"):
        spec.y[0] = 1


def test_bar_spec_equal() -> None:
    assert BarSpec(x=np.arange(5), y=np.arange(5)) == BarSpec(x=np.arange(5), y=np.arange(5))


def test_bar_spec_not_equal_with_different_y() -> None:
    assert BarSpec(x=np.arange(5), y=np.arange(5)) != BarSpec(x=np.arange(5), y=np.arange(1, 6))


def test_bar_spec_hash_raises() -> None:
    with pytest.raises(TypeError, match="unhashable type: 'BarSpec'"):
        hash(BarSpec(x=np.arange(5), y=np.arange(5)))


######################################
#     Tests for BarSpec lowering     #
######################################


def test_bar_spec_to_primitives() -> None:
    spec = BarSpec(
        x=np.array([0.0, 1.0]), y=np.array([2, 3]), width=0.5, label="a", color="#ff0000", alpha=0.5
    )
    assert spec.to_primitives(None) == (
        Bars(
            x=np.array([0.0, 1.0]),
            height=np.array([2.0, 3.0]),
            base=np.array([0.0, 0.0]),
            width=0.5,
            color=(1.0, 0.0, 0.0, 1.0),
            alpha=0.5,
            label="a",
        ),
    )


def test_bar_spec_to_primitives_categorical() -> None:
    primitive = cast(
        "Bars", BarSpec(x=np.array(["a", "b"]), y=np.array([1, 2])).to_primitives(None)[0]
    )
    assert primitive.x.tolist() == ["a", "b"]


def test_bar_spec_to_primitives_empty() -> None:
    primitive = cast("Bars", BarSpec(x=np.array([]), y=np.array([])).to_primitives(None)[0])
    assert primitive.x.shape == (0,)


def test_bar_spec_x_extent_includes_the_half_width() -> None:
    assert BarSpec(x=np.array([0.0, 4.0]), y=np.arange(2), width=2.0).x_extent() == (-1.0, 5.0)


def test_bar_spec_x_extent_categorical() -> None:
    assert BarSpec(x=np.array(["a", "b"]), y=np.arange(2)).x_extent() is None


def test_bar_spec_is_categorical_numeric() -> None:
    assert BarSpec(x=np.arange(2), y=np.arange(2)).is_categorical() is False


def test_bar_spec_is_categorical_strings() -> None:
    assert BarSpec(x=np.array(["a", "b"]), y=np.arange(2)).is_categorical() is True
