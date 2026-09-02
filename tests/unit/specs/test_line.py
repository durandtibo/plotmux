from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import LineSpec

###############################
#     Tests for LineSpec     #
###############################


def test_line_spec_defaults() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    assert spec.label is None
    assert spec.color is None
    assert spec.alpha is None
    assert spec.linewidth is None
    assert spec.linestyle == "solid"


def test_line_spec_custom() -> None:
    spec = LineSpec(
        x=np.arange(10),
        y=np.arange(10),
        label="my-line",
        color="#ff0000",
        alpha=0.5,
        linewidth=2.0,
        linestyle="dashed",
    )
    assert spec.label == "my-line"
    assert spec.color == (1.0, 0.0, 0.0, 1.0)
    assert spec.alpha == 0.5
    assert spec.linewidth == 2.0
    assert spec.linestyle == "dashed"


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_line_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        LineSpec(x=np.arange(10), y=np.arange(10), alpha=alpha)


def test_line_spec_empty_arrays() -> None:
    spec = LineSpec(x=np.array([]), y=np.array([]))
    assert spec.x.shape == (0,)
    assert spec.y.shape == (0,)


def test_line_spec_single_point() -> None:
    spec = LineSpec(x=np.array([1.0]), y=np.array([2.0]))
    assert spec.x.shape == (1,)


# --- color parsing ---


def test_line_spec_color_named() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_line_spec_color_rgba_tuple() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_line_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        LineSpec(x=np.arange(10), y=np.arange(10), color="not-a-color")


# --- common style ---


def test_line_spec_common_style() -> None:
    spec = LineSpec(
        x=np.arange(10),
        y=np.arange(10),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
    )
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"


# --- frozen / error cases ---


def test_line_spec_is_frozen() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(AttributeError):
        spec.label = "new-label"


@pytest.mark.parametrize(
    ("x", "y"),
    [
        pytest.param(np.arange(10), np.arange(5), id="y_shorter"),
        pytest.param(np.arange(5), np.arange(10), id="x_shorter"),
        pytest.param(np.arange(1), np.array([]), id="y_empty"),
    ],
)
def test_line_spec_mismatched_length(x: np.ndarray, y: np.ndarray) -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        LineSpec(x=x, y=y)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_line_spec_alpha_boundary_values(alpha: float) -> None:
    assert LineSpec(x=np.arange(10), y=np.arange(10), alpha=alpha).alpha == alpha


@pytest.mark.parametrize("linestyle", ["solid", "dashed", "dotted", "dashdot"])
def test_line_spec_linestyle_values(linestyle: str) -> None:
    assert LineSpec(x=np.arange(10), y=np.arange(10), linestyle=linestyle).linestyle == linestyle


def test_line_spec_x_y_coerced_from_lists() -> None:
    spec = LineSpec(x=[1, 2, 3], y=[4, 5, 6])
    assert isinstance(spec.x, np.ndarray)
    assert isinstance(spec.y, np.ndarray)
