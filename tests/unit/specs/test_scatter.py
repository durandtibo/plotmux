from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Points
from plotmux.specs import ScatterSpec

##################################
#     Tests for ScatterSpec     #
##################################


def test_scatter_spec_defaults() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    assert spec.label is None
    assert spec.color is None
    assert spec.size is None
    assert spec.edgecolor is None
    assert spec.alpha is None
    assert spec.marker is None
    assert spec.fill is None


def test_scatter_spec_custom() -> None:
    spec = ScatterSpec(
        x=np.arange(10),
        y=np.arange(10),
        label="my-scatter",
        color="#ff0000",
        size=10.0,
        edgecolor="#000000",
        alpha=0.5,
        marker="square",
        fill=False,
    )
    assert spec.label == "my-scatter"
    assert spec.color == (1.0, 0.0, 0.0, 1.0)
    assert spec.size == 10.0
    assert spec.edgecolor == (0.0, 0.0, 0.0, 1.0)
    assert spec.alpha == 0.5
    assert spec.marker == "square"
    assert spec.fill is False


@pytest.mark.parametrize("fill", [None, True, False])
def test_scatter_spec_fill_values(fill: bool | None) -> None:
    assert ScatterSpec(x=np.arange(10), y=np.arange(10), fill=fill).fill is fill


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_scatter_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), alpha=alpha)


def test_scatter_spec_invalid_edgecolor() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), edgecolor="not-a-color")


def test_scatter_spec_empty_arrays() -> None:
    spec = ScatterSpec(x=np.array([]), y=np.array([]))
    assert spec.x.shape == (0,)


def test_scatter_spec_size_small_positive_boundary() -> None:
    assert ScatterSpec(x=np.arange(10), y=np.arange(10), size=1e-9).size == 1e-9


# --- color parsing ---


def test_scatter_spec_color_named() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_scatter_spec_color_rgba_tuple() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_scatter_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), color="not-a-color")


# --- common style ---


# --- frozen / error cases ---


def test_scatter_spec_is_frozen() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(AttributeError):
        cast("Any", spec).label = "new-label"


def test_scatter_spec_mismatched_length() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        ScatterSpec(x=np.arange(10), y=np.arange(5))


@pytest.mark.parametrize("size", [0, -1, -10.5])
def test_scatter_spec_invalid_size(size: float) -> None:
    with pytest.raises(ValueError, match="size must be a positive number"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), size=size)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_scatter_spec_alpha_boundary_values(alpha: float) -> None:
    assert ScatterSpec(x=np.arange(10), y=np.arange(10), alpha=alpha).alpha == alpha


def test_scatter_spec_edgecolor_defaults_independent_of_color() -> None:
    # edgecolor is not derived from color at the spec level (only at
    # render time), so it stays None even when color is set.
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.edgecolor is None


def test_scatter_spec_edgecolor_rgba_tuple() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), edgecolor=(0.1, 0.2, 0.3, 0.4))
    assert spec.edgecolor == (0.1, 0.2, 0.3, 0.4)


def test_scatter_spec_does_not_alias_the_input_x() -> None:
    x = np.arange(5, dtype=float)
    spec = ScatterSpec(x=x, y=np.arange(5))
    x[0] = 99
    assert spec.x[0] == 0.0


def test_scatter_spec_does_not_alias_the_input_y() -> None:
    y = np.arange(5, dtype=float)
    spec = ScatterSpec(x=np.arange(5), y=y)
    y[0] = 99
    assert spec.y[0] == 0.0


def test_scatter_spec_x_is_read_only() -> None:
    spec = ScatterSpec(x=np.arange(5), y=np.arange(5))
    with pytest.raises(ValueError, match="read-only"):
        spec.x[0] = 1


def test_scatter_spec_y_is_read_only() -> None:
    spec = ScatterSpec(x=np.arange(5), y=np.arange(5))
    with pytest.raises(ValueError, match="read-only"):
        spec.y[0] = 1


def test_scatter_spec_equal() -> None:
    assert ScatterSpec(x=np.arange(5), y=np.arange(5)) == ScatterSpec(
        x=np.arange(5), y=np.arange(5)
    )


def test_scatter_spec_not_equal_with_different_y() -> None:
    assert ScatterSpec(x=np.arange(5), y=np.arange(5)) != ScatterSpec(
        x=np.arange(5), y=np.arange(1, 6)
    )


def test_scatter_spec_hash_raises() -> None:
    with pytest.raises(TypeError, match="unhashable type: 'ScatterSpec'"):
        hash(ScatterSpec(x=np.arange(5), y=np.arange(5)))


######################################
#     Tests for the input policy     #
######################################


def test_scatter_spec_nan_in_y_is_kept() -> None:
    spec = ScatterSpec(x=np.arange(3), y=np.array([1.0, np.nan, 3.0]))
    assert np.array_equal(spec.y, np.array([1.0, np.nan, 3.0]), equal_nan=True)


def test_scatter_spec_nan_in_x_is_kept() -> None:
    spec = ScatterSpec(x=np.array([1.0, np.nan, 3.0]), y=np.arange(3))
    assert np.array_equal(spec.x, np.array([1.0, np.nan, 3.0]), equal_nan=True)


def test_scatter_spec_nan_does_not_warn(recwarn: pytest.WarningsRecorder) -> None:
    ScatterSpec(x=np.arange(3), y=np.array([1.0, np.nan, 3.0]))
    assert len(recwarn) == 0


@pytest.mark.parametrize("value", [np.inf, -np.inf])
def test_scatter_spec_inf_in_y_raises(value: float) -> None:
    with pytest.raises(InvalidSpecError, match=r"ScatterSpec: y must not contain inf"):
        ScatterSpec(x=np.arange(3), y=np.array([1.0, value, 3.0]))


@pytest.mark.parametrize("value", [np.inf, -np.inf])
def test_scatter_spec_inf_in_x_raises(value: float) -> None:
    with pytest.raises(InvalidSpecError, match=r"ScatterSpec: x must not contain inf"):
        ScatterSpec(x=np.array([1.0, value, 3.0]), y=np.arange(3))


##########################################
#     Tests for ScatterSpec lowering     #
##########################################


def test_scatter_spec_to_primitives() -> None:
    spec = ScatterSpec(
        x=np.array([0.0, 1.0]),
        y=np.array([2.0, 3.0]),
        label="a",
        color="#ff0000",
        size=4.0,
        edgecolor="#00ff00",
        alpha=0.5,
        marker="square",
        fill=False,
    )
    assert spec.to_primitives(None) == (
        Points(
            x=np.array([0.0, 1.0]),
            y=np.array([2.0, 3.0]),
            color=(1.0, 0.0, 0.0, 1.0),
            alpha=0.5,
            size=4.0,
            marker="square",
            fill=False,
            edgecolor=(0.0, 1.0, 0.0, 1.0),
            label="a",
        ),
    )


def test_scatter_spec_to_primitives_defaults() -> None:
    primitive = cast("Points", ScatterSpec(x=np.arange(2), y=np.arange(2)).to_primitives(None)[0])
    assert (primitive.color, primitive.size, primitive.marker, primitive.fill) == (
        None,
        None,
        None,
        None,
    )


def test_scatter_spec_x_extent() -> None:
    assert ScatterSpec(x=np.array([3.0, -1.0]), y=np.arange(2)).x_extent() == (-1.0, 3.0)


def test_scatter_spec_x_extent_categorical() -> None:
    assert ScatterSpec(x=np.array(["a", "b"]), y=np.arange(2)).x_extent() is None


def test_scatter_spec_is_categorical_numeric() -> None:
    assert ScatterSpec(x=np.arange(2), y=np.arange(2)).is_categorical() is False


def test_scatter_spec_is_categorical_strings() -> None:
    assert ScatterSpec(x=np.array(["a", "b"]), y=np.arange(2)).is_categorical() is True
